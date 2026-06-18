# subset-b-004559 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c

## Purpose

`spectrum2_mr_tcam.c` adapts the generic Spectrum ACL TCAM machinery for Spectrum-2 multicast-router route lookup. It creates IPv4 and IPv6 ACL rulesets for multicast route keys, binds those rulesets to hardware multicast-router protocol tables, and exposes create/destroy/update callbacks through `mlxsw_sp2_mr_tcam_ops`.

## Important APIs, Types, And Functions

- `struct mlxsw_sp2_mr_tcam` stores the owning `mlxsw_sp`, a private flow block, and IPv4/IPv6 ACL rulesets.
- `struct mlxsw_sp2_mr_route` stores the TCAM instance pointer needed for later action replacement.
- `mlxsw_sp2_mr_tcam_ipv4_init()` and `mlxsw_sp2_mr_tcam_ipv6_init()` build fixed element usages and call `mlxsw_sp_acl_ruleset_get()` with `MLXSW_SP_ACL_PROFILE_MR`.
- `mlxsw_sp2_mr_tcam_bind_group()` writes `PEMRBT` to bind an ACL group id to IPv4 or IPv6 multicast-router lookup.
- `mlxsw_sp2_mr_tcam_rule_parse4()` and `mlxsw_sp2_mr_tcam_rule_parse6()` encode VRID, source, and group fields into ACL key/mask values.
- `mlxsw_sp2_mr_tcam_route_create()`, `route_destroy()`, and `route_update()` create ACL rules, delete them by cookie, and replace their AFA action block.

## Control Flow

Initialization creates a private flow block, then builds and binds IPv4 and IPv6 MR rulesets. IPv4 rules use VRID plus 32-bit source/group addresses. IPv6 rules split the VRID and 128-bit source/group addresses across Spectrum-2 AFK elements. Route creation selects the ruleset by `key->proto`, creates an ACL rule keyed by the route-private pointer, fills priority and key fields, then installs it through `mlxsw_sp_acl_rule_add()`. Destroy looks up the rule in the selected ruleset and deletes it. Update looks up the rule and calls `mlxsw_sp_acl_rule_action_replace()` with a new action block.

## State And Persistence

State is in memory in the MR TCAM object, route-private objects, ACL flow block, rulesets, and ACL rule hash tables. Hardware state persists in the ACL group binding register and in TCAM entries/actions until rules are deleted or the driver tears down the rulesets. There is no disk persistence.

## Dependencies And Integration Points

The file depends on `spectrum_mr.h` route keys and ops, the ACL ruleset/rule APIs in `spectrum_acl.c`, AFK element encoding, AFA action blocks, flow block lifetime helpers, and register packing for `PEMRBT`. It integrates multicast routing with the same TCAM profile backend used by flower offload, but uses the MR profile so group binding is handled by multicast router initialization rather than by port ACL binding.

## Risks

- Wrong VRID or IPv6 element splitting will silently program routes that never match or match the wrong multicast stream.
- The route cookie is the route-private pointer cast to `unsigned long`; route-private lifetime must outlive lookup/delete/update.
- `WARN_ON(!ruleset)` paths return or bail out, but protocol enum expansion would need explicit handling.
- Group binding must happen before route insertion; bind failure unwinds the ruleset, but later hardware failures can leave multicast routing unavailable.
- Route update only replaces actions, not keys or priority.

## Test Signals

Useful signals are Spectrum-2 IPv4 and IPv6 multicast route offload, route deletion and action update, failure injection on `PEMRBT` writes and ACL rule insertion, VRID values near the 12-bit limit, masked source/group routes, and parity between software multicast forwarding and hardware hit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c

## Purpose

`spectrum_acl.c` is the high-level ACL manager for the Spectrum driver. It owns AFK creation, dummy FID lifetime, ACL ruleset/rule hash tables, TC flower and multicast-router rule APIs, action construction helpers, statistics, and periodic rule activity polling. It bridges Linux flow blocks and flow actions to hardware-profile operations implemented below `spectrum_acl_tcam.c`.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl` stores the AFK handle, dummy FID, ruleset hash table, global rule list, delayed activity work, and TCAM state.
- `struct mlxsw_sp_acl_ruleset` is keyed by flow block, chain index, and profile ops; it owns a rule hash table, refcount, priority range, and profile-private storage.
- `struct mlxsw_sp_acl_rule` stores cookie, ruleset pointer, `rulei`, last-used/stats baselines, and profile-private entry storage.
- Ruleset APIs include `mlxsw_sp_acl_ruleset_get()`, `lookup()`, `put()`, `bind()`, `unbind()`, `group_id()`, and priority query.
- Rule-info APIs build match keys and actions: key/mask setters, `commit()`, continue/jump/terminate/drop/trap/fwd/mirror/vlan/priority/mangle/police/count/fid/ignore/sample.
- Rule APIs include `mlxsw_sp_acl_rule_create()`, `add()`, `del()`, `destroy()`, `lookup()`, `action_replace()`, and `get_stats()`.
- `mlxsw_sp_acl_init()` and `mlxsw_sp_acl_fini()` own subsystem lifetime.

## Control Flow

Rulesets are looked up or created by profile. Creation allocates profile-private storage, initializes the per-ruleset rule hash table, calls profile `ruleset_add()`, then inserts into the ACL ruleset hash. The first rule added to chain 0 causes the ruleset to bind to all existing flow-block bindings; nonzero chains are reached by jump actions instead of direct port binding. Rule add calls profile `rule_add()`, inserts the cookie into the ruleset hash, updates the global activity list, and increments flow-block counters and ingress/egress bind blockers. Rule delete reverses these steps and unbinds chain 0 when the ruleset becomes singular again.

Action helpers append operations to an AFA block and record state needed for cleanup or stats. Spectrum-1 only supports QoS mangle fields, while Spectrum-2 also supports L4 port and IP address mangling. IPv6 address mangles must arrive in expected odd/even 32-bit pairs so the helper can emit one hardware action per 64-bit half. Periodic delayed work walks the global rule list under `rules_lock`, asks profile `rule_activity_get()` for each rule, and updates `last_used`. Stats read counters and policer drop counters, return deltas since the previous read, and update the cached baselines.

## State And Persistence

All persistent driver state is memory-resident and refcounted. Hardware state is delegated through profile ops and AFA/KVDL/counter/policer/span helpers. The dummy FID is held while ACL is initialized. The delayed work reschedules itself until finalization cancels it. Rule stats are cumulative in hardware but exposed as deltas by cached last packet/byte/drop values in `struct mlxsw_sp_acl_rule`.

## Dependencies And Integration Points

This file integrates Linux flow block binding, TC actions, AFK flexible keys, AFA flexible actions, flow counters, policers, SPAN/mirror/sampling, port range register allocation, dummy FID handling, and profile ops from the TCAM layer. It is called by TC flower offload, multicast routing, and other Spectrum policy paths that need ACL rule construction.

## Risks

- Ruleset binding is conditional on chain 0 and refcount shape; refcount bugs can bind too early, leave ports unbound, or leak rulesets.
- IPv6 mangle pairing is order-sensitive and rejects unexpected ordering.
- The global activity worker can report and reschedule through transient hardware errors; repeated errors are logged but do not stop the worker.
- Stats are delta-based and mutate cached baselines on read, so callers must not expect idempotent reads.
- Cleanup depends on every rule being deleted before `mlxsw_sp_acl_fini()`, which warns on a non-empty list.

## Test Signals

Test TC flower add/delete across ingress and egress, shared flow blocks, chain jumps, rule replacement rejection for flower, mangle field coverage on Spectrum-1 versus Spectrum-2, mirror/sample single-source validation, policer/count stats deltas, activity timestamps, and failure unwinds for profile rule insertion and binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c

## Purpose

`spectrum_acl_atcam.c` implements the algorithmic TCAM backend used by Spectrum-2 and newer ACL regions. It maps encoded rule keys and ERP masks to `PTCE3` entries, tracks duplicate keys, manages large-key IDs for 12-block regions, and spills entries to the C-TCAM backend when A-TCAM insertion is not possible.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_atcam_region` owns the A-TCAM entry hash/list, C-TCAM fallback region, ERP table, type-specific operations, and backend-private state.
- `struct mlxsw_sp_acl_atcam_entry` stores the hash key, delta metadata, C-TCAM fallback entry, large-key id, and ERP mask.
- Generic region ops use a dummy large-key id; 12KB region ops allocate/refcount real large-key IDs from a bitmap and hash table.
- `mlxsw_sp_acl_atcam_region_associate()` maps ACL region ids to hardware regions using `PERAR`.
- `mlxsw_sp_acl_atcam_region_init()` initializes entry hash/list, type-specific state, ERP state, and C-TCAM fallback.
- `mlxsw_sp_acl_atcam_entry_add()`, `entry_del()`, and `entry_action_replace()` are the exported backend entry operations.
- `mlxsw_sp_acl_atcam_rehash_hints_get()` and `put()` delegate rehash hint handling to ERP.

## Control Flow

Region initialization classifies the region by number of AFK key blocks: 2KB, 4KB, 8KB, or 12KB. It initializes A-TCAM entry tracking, large-key state if needed, ERP tables, and a C-TCAM region for fallback. Entry add first encodes key and mask with AFK, obtains or creates an ERP mask, computes any ERP delta bits, clears those delta bits from the encoded key, and inserts the entry into the A-TCAM entry hash. Duplicate hash keys or ERP/Bloom failures cause the entry to be removed from the A-TCAM tracking structures and then inserted into C-TCAM. Successful A-TCAM inserts update Bloom before writing `PTCE3`; deletes remove `PTCE3`, Bloom, hash/list entries, and ERP references. Action replacement writes either `PTCE3` update or C-TCAM `PTCE2` update depending on where the entry landed.

## State And Persistence

A-TCAM state is the software entry hash/list, ERP mask references, large-key-id references, and hardware `PTCE3` records. C-TCAM spill entries persist in the fallback `parman` region. ERP and Bloom state are shared with `spectrum_acl_erp.c` and `spectrum_acl_bloom_filter.c`. There is no disk persistence.

## Dependencies And Integration Points

The file depends on AFK key encoding, TCAM region metadata, `PTCE3`/`PERAR` register packers, C-TCAM helpers, ERP mask/delta/Bloom helpers, tracepoints, and core resource queries for large-key ids. It is selected through `mlxsw_sp_acl_tcam_ops` in chip-specific Spectrum code and used by the generic TCAM virtual region allocator.

## Risks

- A-TCAM cannot store identical effective keys; duplicate handling must reliably spill to C-TCAM.
- Bloom must be updated before `PTCE3` insertion and unwound on failure, or lookups can become false-negative-prone.
- Large-key-id reference counts affect the shared-key flag written to hardware; wrong counts can corrupt 12KB-region lookups.
- Delta computation mutates the encoded key by clearing bits; ordering around hash insertion and ERP reference management is fragile.
- Fallback to C-TCAM changes ordering and capacity behavior, so mixed A-TCAM/C-TCAM regions need stress testing.

## Test Signals

Exercise rules with identical keys, many distinct masks, 2/4/8/12-block key sizes, C-TCAM spill, action replacement for both A-TCAM and C-TCAM entries, region rehash, large-key-id exhaustion, and failure injection for ERP mask allocation, Bloom update, and `PTCE3` writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_atcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c

## Purpose

`spectrum_acl_bloom_filter.c` maintains the A-TCAM Bloom filter used with ERP banks. It computes hardware-specific Bloom indexes from encoded ACL keys, ERP IDs, and region IDs, refcounts programmed bits per ERP bank, and writes `PEABFE` only on zero-to-one or one-to-zero transitions.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_bf` stores a mutex, per-bank size, and flexible array of refcounts for every ERP-bank/Bloom-index pair.
- Spectrum-2/3 helpers encode padded 23-byte chunks and hash them with CRC-16.
- Spectrum-4 helpers encode 20-byte chunks, shift packed chunks to account for 14-bit IDs, and combine CRC-10 row and CRC-6 column results.
- `mlxsw_sp_acl_bf_entry_add()` and `mlxsw_sp_acl_bf_entry_del()` update refcounts and write `PEABFE` records.
- `mlxsw_sp_acl_bf_init()` sizes the refcount array from `ACL_MAX_BF_LOG` and the ERP-bank count.
- `mlxsw_sp2_acl_bf_ops` and `mlxsw_sp4_acl_bf_ops` select chip-specific index calculation.

## Control Flow

For each A-TCAM entry, the selected `index_get()` implementation encodes only the chunks needed by the region key size. Each chunk combines key blocks, ERP id, and region id. Spectrum-2/3 hash the resulting byte stream with CRC-16. Spectrum-4 uses CRC-10 for row and CRC-6 for column, with chunk shifts for multi-chunk packed keys. Add locks the Bloom object, computes the rule-count index as `erp_bank * bank_size + bf_index`, increments an existing nonzero refcount if present, or writes an enable record to hardware and sets the refcount to one. Delete performs the inverse and writes a disable record only when the refcount reaches zero.

## State And Persistence

State is an in-memory refcount table protected by `bf->lock`, plus hardware Bloom bits in `PEABFE`. Refcounts are authoritative for avoiding premature bit clearing when multiple entries hash to the same index. Hardware state persists until deletion, region teardown, or device reset.

## Dependencies And Integration Points

The file is called from ERP/A-TCAM insertion and removal paths. It depends on region key metadata from AFK, A-TCAM encoded keys, ERP-bank mapping from `spectrum_acl_erp.c`, resource `ACL_MAX_BF_LOG`, and `PEABFE` register packing. Chip-specific ops are selected by the Spectrum family.

## Risks

- Hash/encoding layout is hardware-contract code; byte offsets, shifts, and padding errors cause lookup misses.
- Delete failure to allocate the `PEABFE` payload leaves a hardware bit set while software refcount reaches zero.
- Refcount underflow would corrupt Bloom state; callers must balance add/remove per ERP bank.
- Spectrum-4 chunk shifting writes into adjacent bytes by design, so buffer sizing and chunk-count assumptions matter.

## Test Signals

Validate Bloom index vectors against hardware/reference vectors for Spectrum-2/3/4, add/delete collision refcounting, multi-bank ERP use, all key sizes from one to three chunks, allocation failure on add/delete, and A-TCAM lookups before and after ERP rehash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_bloom_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c

## Purpose

`spectrum_acl_ctcam.c` implements conventional TCAM entry placement for ACL regions. It uses `parman` to maintain priority-ordered entries, resizes/moves hardware regions as needed, writes `PTCE2` entries, and supports action replacement.

## Important APIs, Types, And Functions

- `mlxsw_sp_acl_ctcam_region_init()` and `fini()` create/destroy a `parman` instance for a TCAM region.
- `mlxsw_sp_acl_ctcam_chunk_init()` and `fini()` map logical priority chunks to `parman_prio`.
- `mlxsw_sp_acl_ctcam_entry_add()` and `entry_del()` add/remove `parman_item`s and write/remove hardware entries.
- `mlxsw_sp_acl_ctcam_entry_action_replace()` updates the first action set in-place.
- `mlxsw_sp_acl_ctcam_region_resize()` writes `PTAR` resize operations.
- `mlxsw_sp_acl_ctcam_region_move()` writes `PRCR` moves.

## Control Flow

Region initialization creates a `parman` object with base count 16, resize step 16, LSORT ordering, and callbacks that resize `PTAR` regions or move `PRCR` ranges. Entry add first obtains a priority-ordered index from `parman_item_add()`, encodes key and mask with AFK into a `PTCE2` payload, lets backend ops observe/insert the mask, copies the first AFA action set into the entry, and writes the entry. If the write fails it removes backend state and the parman item. Delete disables the `PTCE2` entry, calls backend remove, and removes the parman item.

## State And Persistence

Software state lives in the `parman` object, priority chunks, and per-entry item indexes. Hardware state lives in resized TCAM region allocation, moved entries, and `PTCE2` records. The file itself does not persist state across driver lifetime.

## Dependencies And Integration Points

The module is used directly as the C-TCAM backend and as the spill/fallback path for A-TCAM. It depends on AFK encoding, AFA first action sets, TCAM region metadata from `spectrum_acl_tcam.h`, `parman`, resource `ACL_MAX_TCAM_RULES`, and `PTAR`/`PRCR`/`PTCE2` register packers.

## Risks

- `parman` and hardware movement must stay synchronized; a failed or ignored `PRCR` write can desynchronize software indexes from hardware entries.
- Region resizing is bounded by `ACL_MAX_TCAM_RULES`, but exhaustion propagates as insertion failures.
- The action replacement helper passes `rulei->priority` directly as hardware priority, unlike initial insertion which may invert/fill priority through `mlxsw_sp_acl_tcam_priority_get()`.
- Backend mask insert/remove callbacks must be balanced on all error paths.

## Test Signals

Exercise insert/delete at many priorities, region growth and movement, maximum TCAM rule capacity, C-TCAM spill from A-TCAM, action replacement, failure of `PTCE2` writes, and mixed chunk priority ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_ctcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c

## Purpose

`spectrum_acl_erp.c` manages eRP masks and eRP tables for A-TCAM regions. It aggregates compatible masks through `objagg`, programs region master masks and eRP table entries, coordinates Bloom filter updates, handles C-TCAM lookup enablement, and provides rehash hints that allow the TCAM layer to rebuild regions with fewer roots.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_erp_core` owns per-region-type entry sizes, a `gen_pool` for eRP table rows, the Bloom filter, ERP-bank count, and device pointer.
- `struct mlxsw_sp_acl_erp_table` owns master mask accounting, ERP id/index bitmaps, A-TCAM ERP list, objagg, counters, and region linkage.
- `mlxsw_sp_acl_erp_mask_get()` / `put()` expose mask references as `struct mlxsw_sp_acl_erp_mask`.
- `mlxsw_sp_acl_erp_delta_*()` exposes delta start/mask/value/clear helpers used by A-TCAM key encoding.
- `mlxsw_sp_acl_erp_bf_insert()` and `remove()` update Bloom bits for table-backed ERP roots.
- `mlxsw_sp_acl_erp_region_init()` and `fini()` create/destroy per-region ERP state.
- `mlxsw_sp_acl_erp_rehash_hints_get()` / `put()` create objagg hints for TCAM rehash.
- `mlxsw_sp_acl_erps_init()` and `fini()` own global ERP resources.

## Control Flow

Global init queries ERP bank resources, creates a best-fit `gen_pool`, initializes Bloom, and stores hardware entry sizes for 2/4/8/12KB region types. Region init creates an objagg table, initializes the hardware master mask to zero with `PERCR`, and disables table lookup with `PERERP`. Mask acquisition asks objagg for a root or delta. The first A-TCAM mask uses only the master mask. A second mask transitions the region to an eRP table: it allocates table rows, writes the existing root to `PERPT`, populates Bloom for existing entries, and enables `PERERP`. Additional masks expand the table by bank-sized rows when needed and program new roots and vectors. C-TCAM masks increment C-TCAM counters, set master mask bits, and enable C-TCAM lookup through `PERERP`.

Deltas are permitted only when two masks differ by up to eight consecutive bits that are set in the child but not the parent. Delta create increments delta counters, updates the master mask, and stores the bit location so A-TCAM can clear those key bits and send the delta field in `PTCE3`. Rehash hints are generated with `OBJAGG_OPT_ALGO_SIMPLE_GREEDY`; if hint root count is lower than current root count, the TCAM layer can rebuild the region using those hints.

## State And Persistence

Software state includes gen-pool allocations, ERP ids, ERP indexes, root/delta objagg objects, master-mask per-bit reference counts, C-TCAM/delta counters, and Bloom references. Hardware state includes `PERCR` master masks, `PERPT` table rows, `PERERP` enable/vector state, and Bloom entries. It is persistent only for the driver/device lifetime.

## Dependencies And Integration Points

ERP is called by A-TCAM region initialization and entry add/delete, C-TCAM spill paths, Bloom filter code, and TCAM rehash. It depends on Linux `objagg`, `genalloc`, bitmaps, `rtnl`-safe driver context, Spectrum resource IDs for ERP/Bloom sizing, and `PERCR`/`PERPT`/`PERERP` register packers.

## Risks

- State transitions between no mask, master-mask-only, two masks, multiple masks, C-TCAM lookup, and deltas are intricate and require exact counter balance.
- Bloom updates during table transition must be ordered before enabling table lookup.
- `gen_pool_alloc()` uses an artificial offset because zero means failure; mistakes around the offset corrupt table indexes.
- Delta compatibility is intentionally narrow; unexpected mask shapes increase root count and can force rehash or spill.
- Error unwinds during table expansion/transition must restore old base indexes and bitmaps correctly.

## Test Signals

Test first/second/many mask insertion, C-TCAM masks, delta-compatible and incompatible masks, ERP table expansion to `MLXSW_SP_ACL_ERP_MAX_PER_REGION`, Bloom updates during transitions, rehash hints and region migration, resource exhaustion, and register write failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_erp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c

## Purpose

`spectrum_acl_flex_actions.c` connects the generic ACL flexible-action engine to Spectrum resources. It supplies `mlxsw_afa_ops` for KVDL action-set storage, forwarding entries, counters, mirroring, policing, and packet sampling, and initializes/destroys `mlxsw_sp->afa`.

## Important APIs, Types, And Functions

- `mlxsw_sp_act_kvdl_set_add()` allocates non-first action sets from KVDL and writes them with `PEFA`.
- Spectrum-1 and Spectrum-2 wrappers differ in the `ca` flag and activity support.
- `mlxsw_sp_act_kvdl_fwd_entry_add()` allocates PBS KVDL entries and writes `PPBS`.
- Counter helpers allocate/free flow counters.
- Mirror helpers acquire SPAN agents and analyzed-port references.
- Policer helpers allocate/delete single-rate byte policers.
- Spectrum-2 sampler helpers program policy-engine sample trigger params and use SPAN session `MLXSW_SP_SPAN_SESSION_ID_SAMPLING`.
- `mlxsw_sp1_act_afa_ops` and `mlxsw_sp2_act_afa_ops` export chip-specific AFA callbacks.
- `mlxsw_sp_afa_init()` and `mlxsw_sp_afa_fini()` own AFA object lifetime.

## Control Flow

When AFA needs extra action sets, the first set is left in TCAM and later sets are allocated in KVDL and written to `PEFA`. Spectrum-2 queries `PEFA` for activity, while Spectrum-1 reports unsupported. Forward actions allocate PBS entries and write the local port. Mirror and sampler actions acquire shared SPAN/analyzed-port resources before returning a span id to AFA; delete releases in reverse. Sampling is rejected on Spectrum-1 and fully wired on Spectrum-2 by setting sample trigger params before acquiring a SPAN agent.

## State And Persistence

State is mainly owned by referenced subsystems: KVDL allocations for action sets/PBS, flow counters, SPAN agents, analyzed-port references, policer indexes, and sample trigger params. Hardware state persists in `PEFA`, `PPBS`, policer/counter blocks, and SPAN/sample configuration until AFA destruction or action deletion.

## Dependencies And Integration Points

The file integrates `core_acl_flex_actions` with Spectrum KVDL, counters, policers, SPAN, sampling, ports, and core resource `ACL_ACTIONS_PER_SET`. It is initialized during Spectrum ACL setup and used by rule action helper functions in `spectrum_acl.c`.

## Risks

- Add/delete callbacks must be exactly balanced or KVDL, SPAN, policer, or sampling resources leak.
- Sampling uses one policy-engine trigger; multiple users must be compatible with trigger-param lifetime.
- Spectrum-1 sampler delete warns unconditionally and should only be reached after impossible add success.
- `local_port` indexes directly into `mlxsw_sp->ports`; invalid callers can dereference missing ports.

## Test Signals

Validate multi-set ACL actions, activity query on Spectrum-2, mirror add/delete, forward-to-port actions, policer and counter allocation cleanup, Spectrum-1 sampling rejection, Spectrum-2 sampling with truncation/rate parameters, and failure unwind at every allocation/register-write step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h

## Purpose

`spectrum_acl_flex_actions.h` is the public Spectrum ACL flexible-action header. It exposes only the initialization and teardown entry points needed by the Spectrum driver.

## Important APIs, Types, And Functions

- `mlxsw_sp_afa_init(struct mlxsw_sp *mlxsw_sp)` creates `mlxsw_sp->afa` using chip-specific AFA ops.
- `mlxsw_sp_afa_fini(struct mlxsw_sp *mlxsw_sp)` destroys the AFA object.
- The header includes `spectrum.h` so callers have `struct mlxsw_sp`.

## Control Flow

The header has no runtime control flow. It participates in driver initialization ordering by making AFA setup available before ACL rules can create or commit action blocks.

## State And Persistence

The header stores no state. Its declared functions manage the runtime `mlxsw_sp->afa` pointer and action-related hardware resources through the implementation file.

## Dependencies And Integration Points

It is included by ACL setup code and by `spectrum_acl_flex_actions.c`. It ties the Spectrum driver to `core_acl_flex_actions` without exposing implementation details such as KVDL, SPAN, counters, policers, or sampling.

## Risks

- The narrow interface is simple, but incorrect init/fini ordering can leave ACL rule construction without an AFA handle or destroy AFA while rules still reference action blocks.
- Since the header does not expose feature flags, chip differences are hidden in `mlxsw_sp->afa_ops` and must be initialized correctly elsewhere.

## Test Signals

Build coverage, Spectrum probe/remove, ACL rule creation after AFA init, and cleanup with no outstanding action blocks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c

## Purpose

`spectrum_acl_flex_keys.c` defines Spectrum flexible-key layouts for ACL matching. It maps logical AFK elements such as MACs, VLAN, system port, IPv4/IPv6 addresses, protocol, L4 ports, TCP flags, VRID, TTL, DSCP, ECN, and FDB miss into hardware key blocks for Spectrum-1, Spectrum-2/3, and Spectrum-4.

## Important APIs, Types, And Functions

- Static `mlxsw_afk_element_inst` arrays define element placement inside hardware blocks.
- `mlxsw_sp1_afk_blocks`, `mlxsw_sp2_afk_blocks`, and `mlxsw_sp4_afk_blocks` enumerate block IDs and supported elements.
- Spectrum-1 uses 16-byte blocks copied directly by `mlxsw_sp1_afk_encode_block()` and cleared by `mlxsw_sp1_afk_clear_block()`.
- Spectrum-2/4 use 36-bit block packing with `mlxsw_sp2_afk_blocks_layout`, `__mlxsw_sp2_afk_block_value_set()`, `mlxsw_sp2_afk_encode_block()`, and `clear_block()`.
- `mlxsw_sp1_afk_ops`, `mlxsw_sp2_afk_ops`, and `mlxsw_sp4_afk_ops` export the layouts and encoding callbacks.

## Control Flow

There is no dynamic policy control flow. AFK users request element usages; the generic AFK core chooses key blocks from these tables and calls the chip-specific `encode_block`/`clear_block` callbacks to build register payloads. Spectrum-4 reuses the Spectrum-2 packing callback but supplies revised block IDs and element widths, including high-entropy markings for selected blocks.

## State And Persistence

The file stores static layout tables only. Runtime state is produced by AFK key-info objects and encoded key/mask buffers in ACL rule insertion. Hardware persistence occurs when those buffers are written by TCAM backends.

## Dependencies And Integration Points

The layouts feed all ACL match encoding in `spectrum_acl.c`, `spectrum_acl_tcam.c`, A-TCAM/C-TCAM insertion, and multicast routing. The file depends on `core_acl_flex_keys.h`, `item.h` bitfield helpers, and exact Spectrum hardware key block definitions.

## Risks

- Any offset, width, block ID, or packing shift error changes hardware match semantics.
- Spectrum-2/4 36-bit packing is non-byte-aligned and must stay compatible with Bloom filter key offsets and ERP mask length assumptions.
- Spectrum-4 changes some VRID/source-port widths and block IDs; using the wrong ops for a device family causes subtle match failures.
- Static tables do not self-validate against hardware capabilities.

## Test Signals

Validate TC flower matches for every listed element, IPv4/IPv6 multicast route keys, VLAN/PCP/system-port/FDB miss matching, Spectrum-1 versus Spectrum-2/4 behavior, masks with partial fields, and encoded key buffers against known hardware layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c

## Purpose

`spectrum_acl_tcam.c` is the generic TCAM virtualization layer for Spectrum ACL profiles. It allocates ACL/TCAM region and group IDs, groups regions by priority, creates virtual regions and chunks based on flexible-key usage, inserts virtual entries through chip-specific backend ops, handles delayed A-TCAM rehash migration, exposes a devlink rehash interval parameter, and registers profile ops for TC flower and multicast-router ACL users.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_tcam` stores used-region/group IDAs, hardware limits, virtual-region list, rehash interval, lock, and backend-private storage.
- `struct mlxsw_sp_acl_tcam_vgroup`, `vregion`, `vchunk`, and `ventry` model profile rulesets, compatible key layouts, priority chunks, and entries.
- `mlxsw_sp_acl_tcam_init()` / `fini()` initialize resources, devlink params, and chip backend ops.
- `mlxsw_sp_acl_tcam_priority_get()` converts Linux priority to hardware priority when requested.
- Region helpers allocate/free IDs, associate/allocate/enable/free hardware regions, and attach/detach them from groups.
- Rehash helpers create a second region, migrate entries with a credit budget, roll back on errors, and destroy the old region when complete.
- Flower profile ops bind groups to ports and support activity reads.
- MR profile ops pre-create a chunk, skip port binding, and allow action replacement for multicast routes.

## Control Flow

Ruleset creation creates a virtual group and hardware group. When the first rule for a priority arrives, the layer finds a compatible virtual region by priority and AFK element usage; if none exists, it chooses a configured pattern, creates key-info, allocates and enables a hardware region, and attaches it to the group. It then creates or reuses a virtual chunk for that priority and asks backend ops to create a concrete entry. Group updates write `PAGT`; port binds write `PPBT`.

For rehash-capable backends, each virtual region has delayed work. Rehash asks the backend for hints, creates a new hardware region with those hints, attaches it next to the old region, then migrates chunks and entries under a credit budget. If migration fails, it swaps back and rolls entries back to the old region. If credits run out, context markers let the next work item resume. On success, the old region is detached/destroyed and hints are released. A devlink runtime parameter can disable rehash or force immediate scheduling after interval changes.

## State And Persistence

State is mostly in memory: IDA allocations, virtual groups/regions/chunks/entries, refcounts, AFK key-info references, and rehash context markers. Hardware state includes `PTAR` regions, `PACL` enables, `PAGT` groups, `PPBT` binds, and backend entries. Rehash temporarily duplicates region state through `region2` and `chunk2`.

## Dependencies And Integration Points

The layer depends on chip-specific `mlxsw_sp_acl_tcam_ops`, AFK key-info APIs, devlink params, tracepoints, resource IDs, the ACL high-level profile API, and backend files `spectrum_acl_atcam.c`/`ctcam.c`/`erp.c`. It is the main integration point between Linux flow rules and hardware TCAM programming.

## Risks

- Region splitting for incompatible key usage inside an existing priority span is explicitly unsupported and returns `-EOPNOTSUPP`.
- Rehash migration is complex: list changes during migration reset markers, but bugs can duplicate, lose, or misorder entries.
- Group region attach/detach writes hardware state while holding group locks; failed group updates must restore lists exactly.
- Hardware resource limits for regions, groups, group size, and priorities can fail late under scale.
- Devlink interval changes cancel/reschedule work while region locks and TCAM locks interact.

## Test Signals

Run TC flower rules with diverse key usages and priorities, chain/group binding to multiple ports, region/group exhaustion, region rehash under load, add/delete during rehash, migration rollback injection, devlink interval changes including zero, MR profile route add/update/delete, and hardware activity polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h

## Purpose

`spectrum_acl_tcam.h` declares the shared TCAM data structures and APIs used by the Spectrum ACL core, TCAM virtualization layer, C-TCAM backend, A-TCAM backend, ERP manager, and Bloom filter. It is the internal contract that lets chip-specific TCAM operations plug into generic ruleset/rule handling.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_tcam` is the top-level TCAM allocator state embedded in `struct mlxsw_sp_acl`.
- `struct mlxsw_sp_acl_profile_ops` defines high-level ruleset/rule callbacks consumed by `spectrum_acl.c`.
- `struct mlxsw_sp_acl_tcam_region` carries hardware region id, key type, region info payload, key-info, group/vregion linkage, and backend-private storage.
- C-TCAM structs and functions expose region/chunk/entry lifecycle, entry add/delete, action replacement, and entry offset.
- A-TCAM structs and functions expose region/chunk/entry lifecycle, entry add/delete/action replacement, rehash hints, and container conversions.
- ERP declarations expose mask references, delta helpers, Bloom insertion/removal, region lifecycle, rehash hints, and global ERP init/fini.
- Bloom declarations expose per-entry add/delete and global Bloom init/fini.

## Control Flow

The header has no runtime control flow, but it defines the call graph. High-level ACL code obtains profile ops from `mlxsw_sp_acl_tcam_profile_ops()`. Profile ops call TCAM virtual entry helpers. The virtual layer calls chip backend ops, which use C-TCAM or A-TCAM structures. A-TCAM calls ERP and Bloom helpers declared here. Inline conversion helpers recover A-TCAM containers from embedded C-TCAM objects.

## State And Persistence

The header defines all main in-memory state carriers for TCAM ACLs and their backend-private flexible arrays. Hardware-persistent state represented by these structs includes ACL region IDs, TCAM region info, group IDs, entries, ERP masks/tables, and Bloom bits. No state is stored by the header itself.

## Dependencies And Integration Points

It depends on Linux list, `parman`, IDR/IDA-related use, Spectrum core headers, register constants, and AFK definitions. It is included by `spectrum_acl.c`, `spectrum_acl_tcam.c`, `spectrum_acl_ctcam.c`, `spectrum_acl_atcam.c`, `spectrum_acl_erp.c`, `spectrum_acl_bloom_filter.c`, and multicast TCAM code.

## Risks

- Flexible-array private storage requires allocation sizes from the matching ops; a mismatch corrupts backend state.
- Shared structs encode ownership assumptions that are not enforced by the type system, especially embedded C-TCAM inside A-TCAM.
- Constants such as mask length, base region count, resize step, and catchall priority are hardware-policy contracts.
- Header changes can ripple across all ACL backends and profiles.

## Test Signals

Compile coverage across all Spectrum variants, backend init/fini, C-TCAM and A-TCAM entry lifecycle tests, ERP/Bloom integration, action replacement, rehash, and static analysis for container/flexible-array usage provide the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h -->
