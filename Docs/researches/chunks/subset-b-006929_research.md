# sources/distributed-fs/ceph/src/mon/OSDMonitor.cc lines 8318-16118

## Scope

This chunk covers the back half of Ceph's monitor-side OSD map command and pool-operation implementation. It starts in the tail of pool creation validation and includes pool flag setters, erasure-code optimization helpers, `ceph osd pool set`, pool application metadata, per-pool stretch settings, OSD create/new/destroy/purge flows, the main `MMonCommand` prepare dispatcher, legacy `MPoolOp` snapshot/pool operations, pool deletion/rename helpers, priority conversion, and stretch-mode degradation/recovery transitions.

The source is centered on `OSDMonitor` mutating `pending_inc`, the monitor's pending `OSDMap::Incremental`, and coordinating Paxos callbacks through `wait_for_commit()` or `wait_for_finished_proposal()`. It depends on earlier helpers in the same file for CRUSH validation, pool creation, erasure-code profile normalization, removed-snap lookup, command preprocessing, and monitor service lifecycle.

## Purpose

This section is the authoritative write path for many administrative changes to the OSDMap. It validates user and daemon requests, translates them into pending OSDMap increments, schedules Paxos proposals, and replies only when the relevant epoch is committed or the command is proved to be a no-op.

The covered code owns mutation of pool geometry and options, CRUSH maps, CRUSH classes/rules/weight sets, OSD existence and identity, OSD weights and state flags, blocklists, PG remap overrides, snapshots, cache tiers, pool availability status, force-created PGs, Crimson enablement, and stretch-mode state. It also provides compatibility behavior for older monitor/client schemas and idempotent retries.

## Important APIs, Types, and Functions

`prepare_set_flag()` and `prepare_unset_flag()` modify `pending_inc.new_flags` using existing OSDMap flags as a base and enqueue a command reply after the next committed epoch. They back `osd pause/unpause`, `osd set`, and `osd unset`.

`enable_pool_ec_optimizations()` validates and toggles `pg_pool_t::FLAG_EC_OPTIMIZATIONS` for erasure-coded pools. It requires all OSDs to be at least `tentacle`, obtains an `ErasureCodeInterface`, checks plugin support and 4 KiB stripe-unit alignment, and computes `nonprimary_shards` so optimized EC pools restrict primaries to safe shards. Disabling after enablement is refused. `maybe_enable_pool_split_ops()` then records shard mappings for direct-read-capable EC plugins and, on `umbrella` or later, enables `FLAG_CLIENT_SPLIT_READS` for non-Crimson pools.

`prepare_command_pool_set()` is the large `ceph osd pool set` implementation. It copies current or pending `pg_pool_t` state, parses typed values with SI/IEC/int/float helpers, rejects tier-only settings on non-tiers, and handles size/min_size, `pg_num` and `pgp_num` actual/target fields, autoscaling mode, CRUSH rule changes, pool flags, hit-set/cache-tier settings, EC overwrites/optimizations, OMAP support, quotas and targets, compression/checksum/fingerprint/dedup pool opts, recovery priority, read ratio, and fast-read. It updates `p.last_change` and stores the result in `pending_inc.new_pools`.

`prepare_command_pool_application()`, `preprocess_command_pool_application()`, and `_command_pool_application()` share validation for application metadata enable/disable/set/rm commands. They enforce base-tier-only metadata, maximum application/key/value counts and lengths, idempotent disables/removals, and force confirmation when adding a second application or disabling an application.

`prepare_command_pool_stretch_set()` and `prepare_command_pool_stretch_unset()` mutate per-pool stretch fields: peering bucket count/target/barrier, CRUSH rule, size, and min_size. They validate the pool, bucket type, subtree counts, CRUSH rule type, and user confirmation when requested bucket counts exceed available subtrees.

`_prepare_command_osd_crush_remove()`, `do_osd_crush_remove()`, and `prepare_command_osd_crush_remove()` remove or unlink CRUSH items and encode the changed `CrushWrapper` into `pending_inc.crush`.

`prepare_command_osd_remove()`, `_allocate_osd_id()`, `do_osd_create()`, `validate_osd_create()`, `prepare_command_osd_create()`, and `prepare_command_osd_new()` implement OSD identity lifecycle. They allocate or reuse IDs, validate UUID/id collisions, handle destroyed-OSD recreation, update device classes in CRUSH, set `CEPH_OSD_NEW`, record UUIDs, and coordinate cephx and dm-crypt lockbox secrets through `AuthMonitor` and `KVMonitor`.

`prepare_command()` parses `MMonCommand` JSON, requires a monitor session, and delegates to `prepare_command_impl()`. `parse_reweights()` parses JSON maps for bulk OSD reweighting. `parse_pgid()` validates PG identifiers and existence.

`prepare_command_impl()` is the central command dispatcher. It maps command prefixes to pending OSDMap changes, replies immediately for no-ops/errors, waits for existing proposals when a multi-epoch command must settle, or commits the new increment. Its branches cover CRUSH map replacement, CRUSH classes, buckets, rules, tunables, rule creation/removal/rename, erasure-code profile set/rm, max OSD count, full ratios, min compatible client, OSD flags, require-osd-release, OSD in/out/down/rm/stop, targeted no* flags by OSD/CRUSH node/device class, `pg_temp`, `primary_temp`, `pg_upmap`, `pg_upmap_items`, `pg_upmap_primary`, primary affinity, OSD reweight/lost/destroy/purge/new/create, blocklist operations, pool snapshots, force snapshot removal, pool create/delete/rename/set, tiers, quotas, pool application metadata, pool stretch settings, pool availability output, force-create-pg, stretch-mode forcing, and `set-allow-crimson`.

`enforce_pool_op_caps()`, `preprocess_pool_op()`, `_is_removed_snap()`, `_is_pending_removed_snap()`, `preprocess_pool_op_create()`, `prepare_pool_op()`, `prepare_pool_op_create()`, `prepare_pool_op_delete()`, and `_pool_op_reply()` are the older `MPoolOp` path. They enforce monitor caps or unmanaged-snapshot permissions, reject wrong FSIDs, short-circuit idempotent pool/snapshot operations, create/remove managed and unmanaged snapshots, record removed snapshots, and reply with `MPoolOpReply`.

`_check_remove_pool()`, `_check_become_tier()`, `_check_remove_tier()`, `_prepare_remove_pool()`, and `_prepare_rename_pool()` centralize deletion, tiering, and rename invariants. They protect CephFS pools, tier relationships, config and per-pool delete locks, fake pool deletion, cleanup of PG remaps/primary temps/upmaps/choose args, and removal of unused EC CRUSH rules.

`convert_pool_priorities()` rescales pool recovery priorities into the newer allowed range when existing values exceed `OSD_POOL_PRIORITY_MIN/MAX`.

`try_disable_stretch_mode()`, `try_enable_stretch_mode_pools()`, `try_enable_stretch_mode()`, `check_for_dead_crush_zones()`, `trigger_degraded_stretch_mode()`, `trigger_recovery_stretch_mode()`, `set_degraded_stretch_mode()`, `set_recovery_stretch_mode()`, `set_healthy_stretch_mode()`, `notify_new_pg_digest()`, `try_end_recovery_stretch_mode()`, and `trigger_healthy_stretch_mode()` implement stretch-mode validation and state transitions between healthy, degraded, and recovery modes.

## Control Flow

Most command handling follows a two-phase monitor pattern. The command is first validated against committed `osdmap` state and, when needed, projected pending state. If it needs no persistent change, the monitor replies directly through `reply_no_propose`. If it must mutate the OSDMap, the code writes fields in `pending_inc`, uses `wait_for_commit()` or `wait_for_finished_proposal()` with a command callback, and returns `true` so Paxos proposes the increment. If an earlier pending change must commit before validation can be meaningful, the `wait` label schedules a retry after the current proposal.

Pool setting control flow starts by resolving the pool and copying any pending pool update. Each `var` branch validates the requested value, applies release gates such as Nautilus for PG target fields, Quincy for `pg_num_max`, Tentacle for EC optimizations, and Umbrella for OMAP/client split reads, then writes the projected pool back to `pending_inc.new_pools`. PG changes distinguish actual values from targets: pre-Nautilus maps mutate actual `pg_num`/`pgp_num` directly, while newer maps set targets for manager-driven adjustment. Decreasing PG counts is gated more strictly than increasing, and Crimson pools require explicit merge/split allowances.

OSD create/new flow validates ID/UUID semantics before touching durable state. `osd new` requires a UUID, optionally parses JSON secrets, validates auth and lockbox idempotency, waits for `AuthMonitor` and `KVMonitor` writability, and then updates those services plus `pending_inc`. Existing UUIDs with matching secrets return success without a new OSDMap proposal. Destroy and purge paths validate that the OSD is down, remove cephx/config-key material, mark `CEPH_OSD_DESTROYED`, optionally remove CRUSH items, then remove the OSD entry.

The CRUSH command branches typically obtain `_get_pending_crush()`, mutate a `CrushWrapper`, validate feature compatibility or rule type where needed, encode into `pending_inc.crush`, and wait for commit. Some commands are explicitly idempotent on replays, such as class/rule rename when the destination already exists, missing rule/class removals, or CRUSH updates that match current state with a prior version.

Pool creation handles replicated and erasure-coded forms, default pool type, implicit EC profile/rule creation, expected object counts, target size options, fast-read, autoscale mode, bulk flag, and Crimson flag. It delegates pool object initialization to `prepare_new_pool()` and may split the operation across epochs if the default EC profile or rule must first be created.

Pool deletion checks both committed and pending pool state. It can fake deletion by renaming when configured, otherwise records `pending_inc.old_pools`, clears per-PG temporary mappings and upmap state for that pool, removes pool choose args, and removes an unused EC CRUSH rule. It refuses deletion for CephFS-attached pools, tier pools, pools with tiers, pools protected by `mon_allow_pool_delete == false`, or `FLAG_NODELETE`.

Legacy `MPoolOp` control flow mirrors command handling but replies with `MPoolOpReply`. Preprocess rejects unauthorized operations and short-circuits idempotent requests. Prepare projects `pg_pool_t`, enforces mutual exclusion between pool snapshots and unmanaged snapshots, updates snap metadata or removed-snap queues, and waits for the finished proposal with a `C_PoolOp` callback.

Stretch mode enablement first validates all pools and CRUSH topology without committing: pools must be replicated and start from default size/min_size unless already on the requested rule, the dividing bucket type must exist, there must be exactly two subtrees, bucket count must be two, and site weights must be within `mon_stretch_max_bucket_weight_delta`. Commit mode then rewrites every pool's CRUSH rule, peering bucket fields, size, and min_size, and records global stretch fields in `pending_inc`. Degradation and recovery triggers are asynchronous monitor-side state transitions driven by dead CRUSH zones and manager PG digests.

## State and Persistence Behavior

The principal persistent output is `pending_inc`, an `OSDMap::Incremental`. This chunk writes `new_flags`, `crush`, `new_pools`, `new_pool_names`, `old_pools`, `new_max_osd`, `new_state`, `new_uuid`, `new_weight`, `new_xinfo`, `new_crush_node_flags`, `new_device_class_flags`, `new_pg_temp`, `new_primary_temp`, `new_pg_upmap`, `old_pg_upmap`, `new_pg_upmap_items`, `old_pg_upmap_items`, `new_pg_upmap_primary`, `old_pg_upmap_primary`, `new_primary_affinity`, `new_lost`, blocklist additions/removals, erasure-code profile additions/removals, removed snaps, release requirements, full ratios, stretch-mode fields, and `allow_crimson`.

Pool state persists through `pg_pool_t` copies in `pending_inc.new_pools`. Mutated fields include size/min_size, PG actual/pending/target counts, autoscale mode, CRUSH rule, flags, hit-set and cache settings, EC profile metadata, stripe width, shard mappings, target sizes, compression/checksum/dedup options, quota fields, tiers/read/write tier, snap state, application metadata, recovery priority, Crimson flags, OMAP support, split-read flags, and stretch peering fields. `last_change` and snap epochs are set to the pending epoch when client-visible behavior changes.

CRUSH changes are persisted by encoding a complete modified `CrushWrapper` into `pending_inc.crush`, not by logging small CRUSH deltas. This includes map replacement, class changes, item insert/move/link/remove, bucket swaps, tunables, rules, choose args, weight changes, and choose-arg cleanup during pool deletion.

OSD identity state spans OSDMap, AuthMonitor, KVMonitor, and monitor metadata. `do_osd_create()` records OSD weights, NEW state, UUIDs, and optional CRUSH device class. Destroy/purge paths remove auth/config-key material before marking destroyed or removing the OSD. `prepare_command_osd_remove()` also queues metadata removal via `pending_metadata_rm`.

Snapshot state persists in pool snap maps and monitor removed-snap queues. Managed snapshots use `add_snap()` and `remove_pool_snap()`. Unmanaged snapshots use `add_unmanaged_snap()` and `remove_unmanaged_snap()`, with pre-Octopus compatibility behavior. Forced removal adds ranges to `pending_inc.new_removed_snaps` so OSDs can retrim leaked snapshots.

Stretch mode persists at two levels: global `pending_inc.change_stretch_mode`, `stretch_mode_enabled`, bucket counts, degraded/recovery flags, and bucket type; and per-pool peering bucket fields, mandatory member, CRUSH rule, size/min_size, and forced op resend epochs. `stretch_recovery_triggered` is local monitor timing state used to decide when PG digest health permits leaving recovery.

## Dependencies and Integration Points

`OSDMap`, `pg_pool_t`, `pool_opts_t`, `CrushWrapper`, `CrushTester`, `ErasureCodeInterface`, `HitSet` implementations, `Compressor`, `Checksummer`, `FeatureMap`, `PGMapDigest`, and `PoolAvailability` provide the domain model.

Monitor integration is broad. `mon.reply_command()` and `mon.send_reply()` return results. `wait_for_commit()`, `wait_for_finished_proposal()`, `force_immediate_propose()`, `propose_pending()`, and Paxos plug/unplug control proposal timing. `mon.authmon()` and `mon.kvmon()` validate and persist OSD secrets and lockbox keys. `mon.mdsmon()` blocks unsafe CephFS pool/tier/snapshot operations. `mon.mgrstatmon()` supplies pool stats, availability data, and PG recovery digests. `mon.monmap` and combined feature maps gate release transitions.

Command parsing relies on `cmdmap_t`, `cmd_getval()`, `cmd_getval_or()`, `cmd_getval_compat_cephbool()`, strict numeric parsing helpers, JSON parsing helpers, and `Formatter` output. Several branches preserve compatibility with older command schemas, legacy `blacklist` naming, and pre-Nautilus/pre-Octopus OSDMap formats.

Cluster-feature integration uses `check_cluster_features()`, `validate_crush_against_features()`, `HAVE_FEATURE()`, required monitor features, `require_min_compat_client`, and `require_osd_release`. These checks prevent map features from being introduced while clients, OSDs, monitors, MDSs, or managers may not understand them.

Operational side effects include cluster log messages for marking OSDs out, manager availability clearing, blocklist/range-blocklist updates, `creating_pgs` tracking for force-created PGs, and immediate proposal forcing for OSD new/destroy/purge operations that touch multiple monitor services.

## Risks and Edge Cases

The dispatcher is extremely broad and uses shared `err`, `ss`, `rs`, and `goto` labels. Bugs in branch ordering or missing `goto reply_no_propose/update/wait` paths can accidentally propose partial state, reply before a needed proposal, or lose an error message.

Many operations are intentionally idempotent under retries, but idempotency is uneven. OSD create/new depends on UUID and secret matching; CRUSH class/rule renames infer success from destination existence; pool delete may become a fake rename; missing pool/snap delete often returns success. Callers that need strict "did this change happen" semantics must account for this.

Pending-versus-committed state is subtle. The comment at the start of `prepare_command_impl()` states that no-op checks usually use committed state even if pending conflicting changes exist. Some branches inspect pending state and wait, while others intentionally squash pending pool updates. Concurrent administrative clients can therefore observe operations as ordered by committed epochs, not by arrival at the monitor.

PG geometry changes are high risk. Size increases call `check_pg_num()`, PG decreases require newer OSDMap formats and single-step pending decreases, cache pool splits require force confirmation, Crimson pools disallow or gate split/merge, and pool flags such as `NOPGCHANGE` and `CREATING` block changes. Incorrect validation can strand PGs, break client mapping, or cause large data movement.

EC optimization and overwrite flags are effectively irreversible and version-sensitive. They depend on plugin-reported capabilities, shard mappings, stripe-unit alignment, BlueStore-only placement for overwrites, and conversion of existing `pg_temp` order when optimizations are first enabled.

CRUSH mutations can cause large remaps or invalid placement. The code uses feature validation, optional smoke tests, rule type checks, force flags for dangerous bucket/class/hash changes, and refuses removal of rules/classes still in use or referenced by EC profiles. Still, many branches modify a full CRUSH map in memory and encode it wholesale, so accidental stale pending state can be costly.

OSD destroy/purge/new flows span OSDMap, auth, config-key, CRUSH, and metadata. Partial failure is mitigated by validation ordering, Paxos plug/unplug, and idempotency checks, but the code comments explicitly require later steps in purge to be guaranteed after auth/config-key side effects are applied.

Pool deletion and tier changes are blocked for CephFS and tier invariants, but cache tier transitions depend on manager pool statistics for dirty object counts. Missing or stale stats can affect whether a dangerous transition is refused.

Snapshot operations must avoid mixing pool-managed and unmanaged modes, must block CephFS-attached pools, and must handle already purged or pending-removed snap IDs. Force-remove-snap can deliberately cause OSD retrimming and must not exceed the pool's snap sequence.

Stretch mode is explicitly limited to two sites. It asserts or errors on other topologies, halves pool min_size in degraded mode, forces mandatory bucket membership, and uses manager digest health plus a wait timer to exit recovery. Incorrect dead-zone detection or stale PG digest data could prematurely change pool peering rules.

## Test Signals

Command-dispatch tests should cover every `prepare_command_impl()` prefix family with success, validation failure, idempotent retry, pending-change wait, and formatter/plain output variants. Assertions should verify `pending_inc` fields and returned proposal behavior, not only command text.

Pool setting tests should exercise `size`, `min_size`, `pg_num` and `pgp_num` actual/target changes, autoscale bounds, `pg_num_min/max`, Crimson split/merge gates, EC overwrite and optimization gates, OMAP support restrictions, pool option parsing with SI/IEC units, dedup tier lookup, and irreversible flag disable attempts.

CRUSH tests should cover full map replacement with `prior_version`, smoke-test failure, class create/rm/rename, device class set/rm, bucket add/move/link/unlink/swap, weight-set create/reweight/remove, tunables, replicated and erasure rule creation, rule removal while in use, and cleanup of choose args/rules on pool deletion.

OSD lifecycle tests should cover legacy `osd create`, `osd new` with and without secrets, idempotent UUID reuse, mismatched secrets, destroyed-ID recreation, OSD remove while up, destroy/purge with auth or KVMonitor not writeable, purge-new restrictions, device-class creation, and metadata removal queuing.

Pool lifecycle and snapshot tests should cover pool create with replicated and EC defaults, implicit EC profile/rule creation across two epochs, dot-prefixed internal names, fake and real pool delete, rename idempotency, managed snapshots, unmanaged snapshots, removed-snap idempotency, force-remove dry runs, and CephFS pool rejection.

Tier/cache tests should cover adding/removing tiers, overlays, cache modes and invalid transitions with dirty objects, `add-cache` default hit-set configuration, tier pool non-empty rejection, CephFS restrictions, Crimson tier rejection, and force-nonempty snapshot hazards.

Placement override tests should cover `pg_temp`, `primary_temp`, `pg repeer`, pg-upmap, pg-upmap-items, pg-upmap-primary, release/feature gates, pending update waits, duplicate entries, invalid OSD IDs, illegal acting sets, and pool-pending-removal behavior.

Stretch tests should cover enable validation for non-replicated pools, non-default size/min_size, invalid bucket type, more or fewer than two zones, weight imbalance, per-pool stretch set/unset, dead-zone detection, degraded mode pool rewrites, recovery mode triggering, PG digest based exit, and forced healthy/recovery commands.

Security and capability tests should cover `MMonCommand` without session, `MPoolOp` write caps, unmanaged-snapshot special permissions, blocklist/range-blocklist feature gates, `set-allow-crimson` requiring both experimental feature and confirmation, and release-gate commands with connected old clients or missing monitor/OSD features.
