# subset-b-006303 XFRM Core Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_policy.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_policy.c

## Purpose

`xfrm_policy.c` is the core Security Policy Database implementation and route-bundle builder for the XFRM/IPsec stack. It owns policy allocation, insertion, deletion, lookup, expiration, socket policy cloning, outbound transform resolution, inbound/fwd policy verification, per-net XFRM policy initialization, AF-specific policy callbacks, XFRM interface session decoding hooks, audit records, and migration of policy templates.

The file is on both outbound and inbound packet paths. Outbound routing calls `xfrm_lookup()` or `xfrm_lookup_route()` to decide whether a flow is bypassed, blocked, queued for acquisition, or wrapped in an `xfrm_dst` chain. Inbound and forwarding paths call `__xfrm_policy_check()` and `__xfrm_route_forward()` to verify that the secpath and selected policy allow the packet.

## Important APIs, Types, and Functions

Key local types include `struct xfrm_flo` for lookup context, `struct xfrm_flow_keys` for flow dissector output, and the inexact policy accelerator types `struct xfrm_pol_inexact_key`, `struct xfrm_pol_inexact_bin`, `struct xfrm_pol_inexact_node`, and `struct xfrm_pol_inexact_candidates`. Exact policies live in per-net `policy_bydst[]` and `policy_byidx` hlist hash tables; broad-prefix policies are stored in a global rhashtable of bins with per-bin RB trees by destination and source prefix.

Policy lifecycle APIs include `xfrm_policy_alloc()`, `xfrm_policy_destroy()`, `xfrm_policy_insert()`, `xfrm_policy_bysel_ctx()`, `xfrm_policy_byid()`, `xfrm_policy_delete()`, `xfrm_policy_flush()`, `xfrm_dev_policy_flush()`, `xfrm_policy_walk()`, `xfrm_policy_walk_init()`, and `xfrm_policy_walk_done()`. Socket policy APIs include `xfrm_sk_policy_insert()` and `__xfrm_sk_clone_policy()`.

Lookup and bundle APIs include `xfrm_selector_match()`, `xfrm_policy_lookup()`, `xfrm_sk_policy_lookup()`, `xfrm_expand_policies()`, `xfrm_tmpl_resolve()`, `xfrm_bundle_create()`, `xfrm_lookup_with_ifid()`, `xfrm_lookup()`, `xfrm_lookup_route()`, `__xfrm_decode_session()`, `__xfrm_policy_check()`, and `__xfrm_route_forward()`. AF integration is registered through `xfrm_policy_register_afinfo()` and `xfrm_policy_unregister_afinfo()`. XFRM interface integration is registered through `xfrm_if_register_cb()` and `xfrm_if_unregister_cb()`.

Maintenance functions include hash resize/rebuild workers, `xfrm_spd_getinfo()`, `xfrm_policy_hash_rebuild()`, `xfrm_policy_timer()`, `xfrm_policy_queue_process()`, `xfrm_dst_check()`, `xfrm_bundle_ok()`, `xfrm_dst_ifdown()`, and the per-net `xfrm_policy_init()`/`xfrm_policy_fini()` path. Optional code covers audit helpers and `xfrm_migrate()` policy/state endpoint migration.

## Control Flow

Policy insertion sanitizes the mark, chooses either an exact by-selector hash chain or an inexact bin/tree chain, inserts by priority and creation position, links the policy into `policy_all`, assigns or reuses an index, starts the lifetime timer, bumps route generation, and replaces any duplicate policy after moving its queued packets to the new policy. Deletion and flush unlink from hash/list indexes under `xfrm_policy_lock`, then kill the policy outside the critical section by marking it dead, deleting timers, purging held packets, clearing state-cache links, releasing device policy offload state, and dropping references.

Outbound lookup starts in `xfrm_lookup_with_ifid()`. Socket policies are checked first; otherwise the route is bypassed quickly when no outbound policies exist and no if_id is requested. `xfrm_bundle_lookup()` finds main/sub policies, expands them, and resolves templates to states through `xfrm_tmpl_resolve_one()` and `xfrm_state_find()`. Valid states are assembled into nested `xfrm_dst` entries by `xfrm_bundle_create()`, including path lookup for tunnel-like modes, PMTU/header/trailer accounting, output function selection, route cookies, policy/state generation IDs, and state references. If a required state is missing, lookup either returns a queueing dummy bundle or errors depending on `sysctl_larval_drop` and lookup flags.

When acquisition is pending and queueing is enabled, `xdst_queue_output()` places packets on `policy->polq.hold_queue` and arms an exponential backoff timer. `xfrm_policy_queue_process()` re-runs lookup for queued packets after a key manager may have installed SAs; it either reschedules, purges, or rewrites skb dsts and calls `dst_output()`.

Inbound policy checking decodes the packet into a `flowi`, optionally using an XFRM interface callback to choose `if_id` and netns. It first checks all SAs in the secpath against their selectors, including ICMP inner-flow special cases. Then it finds socket or per-net policies, applies default accept/block behavior, validates policy templates against the secpath in the correct order, records verified secpath count, and calls transform-specific reject hooks on mismatch.

Per-net initialization in `xfrm_net_init()` initializes locks, default policies, statistics, state tables, policy tables, sysctls, and NAT keepalive. Global `xfrm_init()` initializes the flow dissector, registers per-net operations, device/input modules, optional ESP-in-TCP, BPF state kfuncs, and IPv4 NAT keepalive.

## State and Persistence Behavior

Persistent policy state is stored per network namespace in policy hash tables, `policy_all`, per-direction counts, hash threshold settings, default user policies, and inexact bins. Individual policies persist selectors, templates, marks, security contexts, interface IDs, lifetimes, use/add timestamps, priority, insertion position, generation ID, optional offload metadata, and a hold queue for unresolved outbound packets.

Bundle validity is persistence-sensitive. `xfrm_dst` chains cache route cookies, state generation IDs, policy generation IDs, MTU values, and policy/state references. `xfrm_dst_check()` forces validation on every use; `xfrm_bundle_ok()` invalidates bundles when the path route, interface, SA state, state genid, or policy genid changes and recalculates cached MTUs when underlying route metrics change.

Timers persist soft/hard lifetime behavior. Policy timers emit key-manager soft expiry notifications or delete policies on hard expiry. Queue timers hold references while active. `curlft.use_time` is written locklessly on hot paths as an advisory timestamp.

Inexact policy storage is shared across namespaces through keyed rhashtable bins but keyed by `possible_net_t`; node pruning is RCU-delayed. Hash resize/rebuild uses seqcounts so lockless readers can retry around table replacement.

## Dependencies and Integration Points

This file depends on core routing/dst APIs, flow dissector, skb secpath, net namespaces, LSM XFRM hooks, audit, SNMP statistics, netfilter NAT session decoding, device offload policy helpers, XFRM state lookup/acquire APIs, key-manager notifications, XFRM user sysctls, NAT keepalive, optional sub-policy, optional IPv6/MIPv6, optional ESP-in-TCP, and optional BPF state kfunc registration.

External users include PF_KEY and netlink user paths for policy management, socket option policy compilation through key managers, IPv4/IPv6 route output, XFRM input/forwarding paths, XFRM interfaces, device offload drivers, and key managers such as user-space IKE daemons through acquire/expire/migrate notifications.

## Risks and Edge Cases

Policy lookup and insertion depend on priority ordering, creation position, exact-vs-inexact chain choice, RCU lifetime, and hash generation retry logic. Incorrect ordering can silently select the wrong policy. Inexact tree merge/prune code is especially sensitive because it restructures prefix trees while preserving list order.

Bundle construction touches route references, state references, dst child chains, PMTU accounting, and output callbacks. A missed reference or generation check can leak dsts/states, keep stale routes alive, or transform traffic with obsolete SAs. Queueing unresolved packets is bounded by `XFRM_MAX_QUEUE_LEN`, but timer/reference handling must stay balanced.

Inbound checks are security-sensitive. Optional transport templates, nested tunnels, verified secpath counts, ICMP inner-flow decoding, packet offload shortcuts, default block policy, and LSM results all affect accept/drop decisions. Small logic changes can allow bypass of required IPsec policy or reject valid nested transforms.

Migration is multi-stage and must restore correctly on partial failure. It clones states, updates policy templates, deletes old states, and notifies key managers; failure ordering can leave duplicate or missing SAs if not handled carefully.

## Test Signals

Useful signals include XFRM/IPsec selftests that add/delete policies, route traffic through transport/tunnel/BEET/IPTFS modes, test socket policies, validate default block policy, and exercise policy migration. Runtime checks include `ip xfrm policy`, `ip xfrm state`, `/proc/net/xfrm_stat`, audit records for SPD add/delete, XFRM MIB counters such as `XfrmOutPolBlock`, `XfrmOutNoStates`, `XfrmInTmplMismatch`, and packet captures showing expected encapsulation or bypass.

Build coverage should include `CONFIG_XFRM_STATISTICS`, `CONFIG_XFRM_SUB_POLICY`, `CONFIG_XFRM_MIGRATE`, `CONFIG_SECURITY_NETWORK_XFRM`, `CONFIG_XFRM_OFFLOAD`, `CONFIG_IPV6`, `CONFIG_IPV6_MIP6`, `CONFIG_XFRM_ESPINTCP`, `CONFIG_BPF`, and namespace teardown tests to cover init/fini and RCU cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_proc.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_proc.c

## Purpose

`xfrm_proc.c` exposes per-network-namespace XFRM statistics through `/proc/net/xfrm_stat` when XFRM statistics are enabled. It is a small reporting bridge from per-CPU Linux MIB counters to the procfs seq-file interface used by administrators, tests, and monitoring tools.

## Important APIs, Types, and Functions

`xfrm_mib_list[]` maps printable counter names to `LINUX_MIB_XFRM*` indexes. It covers inbound errors, replay/sequence errors, state/policy mismatches, outbound bundle/state/policy errors, forwarding header errors, acquire errors, direction errors, IPTFS errors, and outbound queue-space failures.

`xfrm_statistics_seq_show()` refreshes device-offload-backed state counters with `xfrm_state_update_stats(net)`, batches per-CPU SNMP counters through `snmp_get_cpu_field_batch_cnt()`, and prints each name/value pair. `xfrm_proc_init()` creates `xfrm_stat` under `net->proc_net`; `xfrm_proc_fini()` removes it.

## Control Flow

The per-net XFRM policy initialization path calls `xfrm_statistics_init()` in `xfrm_policy.c`, which allocates per-CPU `linux_xfrm_mib` storage and then calls `xfrm_proc_init()`. Reading `/proc/net/xfrm_stat` invokes the single seq-file show callback. Namespace teardown calls `xfrm_proc_fini()` before freeing the per-CPU counters.

## State and Persistence Behavior

This file does not own long-lived protocol state beyond the proc entry. It reads `net->mib.xfrm_statistics`, which is allocated per net namespace elsewhere. Values are snapshots of per-CPU counters at read time, after an explicit state stats update so packet-offload state counters are folded into visible statistics.

## Dependencies and Integration Points

Dependencies are procfs, seq_file, SNMP MIB helpers, and `net/xfrm.h`. It integrates with `xfrm_policy.c` under `CONFIG_XFRM_STATISTICS`; without that config this file is not part of the runtime reporting path.

## Risks and Edge Cases

The printed counter list must stay aligned with the MIB enum definitions. Missing a newly added counter reduces observability; misordering or wrong indexes would make `/proc/net/xfrm_stat` misleading. `xfrm_proc_init()` returns `-ENOMEM` if proc entry creation fails, which causes XFRM per-net initialization to unwind.

## Test Signals

Check that `/proc/net/xfrm_stat` exists in each eligible namespace, contains all expected `Xfrm*` names, and counters move after replay failures, missing states, policy blocks, queue drops, or IPTFS errors. Namespace creation/destruction tests should show no procfs leaks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_replay.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_replay.c

## Purpose

`xfrm_replay.c` implements anti-replay and outbound sequence-number management for XFRM states. It supports legacy 32-bit replay windows, bitmap replay windows stored in `struct xfrm_replay_state_esn`, Extended Sequence Number mode, asynchronous replay state notifications to key managers, and offload-aware outbound sequence allocation for GSO packets.

## Important APIs, Types, and Functions

Public entry points are `xfrm_replay_seqhi()`, `xfrm_replay_notify()`, `xfrm_replay_advance()`, `xfrm_replay_check()`, `xfrm_replay_recheck()`, `xfrm_replay_overflow()`, and `xfrm_init_replay()`.

Legacy mode uses `x->replay.seq`, `x->replay.oseq`, and `x->replay.bitmap`. BMP and ESN modes use `x->replay_esn`, `x->preplay_esn`, `replay_window`, `bmp_len`, `seq`, `seq_hi`, `oseq`, `oseq_hi`, and a variable-size bitmap. ESN-specific logic derives the high sequence number with `xfrm_replay_seqhi()` and validates `XFRM_SKB_CB(skb)->seq.input.hi` during recheck.

Mode-specific helpers include `xfrm_replay_check_legacy()`, `xfrm_replay_check_bmp()`, `xfrm_replay_check_esn()`, `xfrm_replay_advance_bmp()`, `xfrm_replay_advance_esn()`, `xfrm_replay_notify_bmp()`, `xfrm_replay_notify_esn()`, and overflow helpers for legacy/BMP/ESN plus offload variants under `CONFIG_XFRM_OFFLOAD`.

## Control Flow

Inbound processing first calls `xfrm_replay_check()` to reject zero, stale, or duplicate sequence numbers. The mode switch dispatches to legacy, BMP, or ESN checks. Accepted packets later call `xfrm_replay_advance()` to slide the window, clear skipped bitmap positions, mark the received packet bit, update ESN high bits when wrap is detected, optionally notify devices through `xfrm_dev_state_advance_esn()`, and emit replay update notifications if async events are enabled.

ESN checking divides sequence space into the RFC-style same-subspace and window-spans-two-subspaces cases. `xfrm_replay_seqhi()` predicts the high sequence half for a network-order low sequence. Recheck verifies the saved input high half before performing the normal ESN duplicate/window check.

Outbound processing calls `xfrm_replay_overflow()` to allocate the next outgoing sequence. Legacy and BMP paths reject wrap unless `XFRM_SA_XFLAG_OSEQ_MAY_WRAP` permits it. ESN increments `oseq_hi` on low-half wrap and rejects overflow only when the high half wraps. Offload paths store sequence numbers both in `XFRM_SKB_CB` and `struct xfrm_offload`; for GSO they reserve a range equal to `gso_segs`.

Replay notifications compare current replay state to `preplay` snapshots. Updates are sent when sequence deltas exceed `replay_maxdiff` or when `replay_maxage` timeout fires with changes. Otherwise `XFRM_TIME_DEFER` records deferred notification state. Notifications are delivered as `XFRM_MSG_NEWAE` through `km_state_notify()`.

## State and Persistence Behavior

Replay state persists in each `struct xfrm_state`. Legacy state is embedded in `x->replay`/`x->preplay`; BMP/ESN state is dynamically allocated as `x->replay_esn` and `x->preplay_esn`. Statistics increment `x->stats.replay` and `x->stats.replay_window` on duplicate/window failures. Audit records are emitted for replay failures and outbound overflow.

`xfrm_init_replay()` selects `XFRM_REPLAY_MODE_LEGACY`, `XFRM_REPLAY_MODE_BMP`, or `XFRM_REPLAY_MODE_ESN`. It validates that bitmap storage can cover the replay window and requires a nonzero ESN replay window for inbound or directionless SAs.

## Dependencies and Integration Points

This file integrates with `xfrm_state.c` timers, `km_state_notify()`, XFRM audit helpers, async event sysctls through `xfrm_aevent_is_on()`, skb control blocks, optional device offload metadata, and device ESN advance hooks. Protocol-specific input/output code calls these helpers around authentication/decryption/encryption.

## Risks and Edge Cases

Sequence wrap handling is the main security boundary. Off-by-one errors around `bottom`, `top`, bitmap position, or ESN high-half prediction can accept replayed packets or reject valid wraparound packets. Outbound GSO offload must reserve enough sequence numbers; otherwise hardware and software can disagree about ESP sequence assignment.

Notification throttling assumes the caller holds the state lock, as documented in comments. Calling without serialization can corrupt `preplay` snapshots or timer/defer state. Bitmap size validation is essential because subsequent helpers index `bmp[nr]` based on `replay_window`.

## Test Signals

Replay tests should cover zero sequence rejection, duplicate rejection, packets older than the replay window, out-of-order packets inside the window, ESN low-half wrap, outbound low/high overflow, `XFRM_SA_XFLAG_OSEQ_MAY_WRAP`, GSO offload sequence reservation, async event threshold and timeout notifications, and audit/MIB increments for replay failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_state.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_state.c

## Purpose

`xfrm_state.c` is the core Security Association Database implementation. It owns XFRM state allocation, hash indexes, type/mode registration, state lookup, acquire state creation, add/update/delete/flush, lifetime timers, replay timers, migration, SPI allocation, key-manager registration/notifications, AF registration, socket policy compilation dispatch, audit records, and per-net SAD initialization.

## Important APIs, Types, and Functions

The per-net SAD is indexed by destination tuple (`state_bydst`), source tuple (`state_bysrc`), SPI/protocol/destination (`state_byspi`), and acquire sequence (`state_byseq`). `struct xfrm_hash_state_ptrs` snapshots RCU-protected hash table pointers and mask under a seqcount. `XFRM_STATE_INSERT` keeps packet-offload SAs at the head of chains so hardware lookups can short-circuit.

Registration APIs include `xfrm_register_type()`, `xfrm_unregister_type()`, `xfrm_register_type_offload()`, `xfrm_unregister_type_offload()`, `xfrm_set_type_offload()`, `xfrm_register_mode_cbs()`, `xfrm_unregister_mode_cbs()`, `xfrm_state_register_afinfo()`, and `xfrm_state_unregister_afinfo()`.

Lifecycle APIs include `xfrm_state_alloc()`, `xfrm_state_free()`, `__xfrm_state_destroy()`, `__xfrm_state_delete()`, `xfrm_state_delete()`, `xfrm_state_flush()`, `xfrm_dev_state_flush()`, `xfrm_state_insert()`, `xfrm_state_add()`, `xfrm_state_update()`, `xfrm_state_check_expire()`, `xfrm_init_state()`, `__xfrm_init_state()`, `xfrm_state_init()`, and `xfrm_state_fini()`.

Lookup and acquire APIs include `xfrm_input_state_lookup()`, `xfrm_state_find()`, `xfrm_stateonly_find()`, `xfrm_state_lookup_byspi()`, `xfrm_state_lookup()`, `xfrm_state_lookup_byaddr()`, `xfrm_find_acq()`, `xfrm_find_acq_byseq()`, `xfrm_get_acqseq()`, `verify_spi_info()`, and `xfrm_alloc_spi()`.

Key-manager and user-policy APIs include `xfrm_register_km()`, `xfrm_unregister_km()`, `km_query()`, `km_state_notify()`, `km_policy_notify()`, `km_state_expired()`, `km_policy_expired()`, `km_new_mapping()`, `km_report()`, optional `km_migrate()`, and `xfrm_user_policy()`. Optional compatibility translator APIs are registered under `CONFIG_XFRM_USER_COMPAT`.

## Control Flow

State initialization begins with `xfrm_state_alloc()`, which sets namespace, reference count, hash/list nodes, timers, default lifetime limits, add time, replay notification thresholds, and locks. User/netlink-created states call `xfrm_init_state()`, which resolves inner/outer modes, loads the protocol type module if needed, calls the type `init_state`, validates NAT keepalive constraints, initializes optional mode callbacks, initializes replay mode, and marks the state valid.

Adding a state through `xfrm_state_add()` checks for existing states by SPI or address, optionally finds and deletes a matching acquire state, bumps generation IDs of related cached users, inserts into all relevant hash tables, starts timers, updates counters, and triggers hash growth if a collision occurs. `xfrm_state_update()` either replaces an acquire state with a valid state or updates mutable fields on an existing valid state while preserving identity constraints.

Outbound policy resolution calls `xfrm_state_find()`. It first consults the policy's state cache, then the by-destination hash, then wildcard-source entries. It chooses the best valid state by selector/security match, per-CPU acquire policy, dying state, and add time. If no state exists and key managers are alive, it creates an acquire state, initializes a temporary selector, optionally configures packet offload acquisition, calls `km_query()`, inserts the acquire into indexes, and starts the acquire timer.

Inbound packet lookup calls `xfrm_input_state_lookup()`, which first checks a per-CPU input cache, then by-SPI hash. Valid hits are moved to the head of the per-CPU cache under the state lock. BPF XDP helpers in another file call the exported `xfrm_state_lookup()`.

Deletion sets `km.state` to DEAD, unlinks the state from all indexes and caches, decrements the namespace count, updates NAT keepalive tracking, deletes device state, releases tunnel dependencies, and drops the allocation reference. Actual memory/freeing is RCU-delayed through `xfrm_state_gc_work`, which cancels timers, frees algorithms, replay ESN storage, encapsulation/coaddr, offload state, security context, mode state, protocol type reference, and the slab object.

Lifetime handling is split between `xfrm_timer_handler()` for soft/hard add/use expirations and byte/packet limit checks in `xfrm_state_check_expire()`. Replay async events use `xfrm_replay_timer_handler()`. Key-manager notification functions fan out over the RCU `xfrm_km_list`.

## State and Persistence Behavior

Each `struct xfrm_state` persists identity (`id.daddr`, SPI, proto), source address, reqid, mode, family, selector, marks, interface ID, security context, algorithms, encapsulation, coaddr, replay state, offload metadata, NAT keepalive fields, lifetime counters, timers, generation ID, optional tunnel relation, and key-manager state. Per-net state persists hash tables, state count, all-state walk list, per-CPU input caches, and hash resize work.

Hash table replacement uses seqcounts and RCU so lockless readers can retry safely. State references are protected with `refcount_inc_not_zero()` in RCU readers. Device offload state has a separate GC list so drivers can free resources after deletion and netdev teardown.

Acquire states are temporary but persisted in the SAD so subsequent packets do not flood key managers. Their hard-add lifetime is taken from `net->xfrm.sysctl_acq_expires`.

## Dependencies and Integration Points

This file depends on protocol type implementations for ESP/AH/IPCOMP/tunnel headers, mode callback modules such as IPTFS, crypto AEAD for MTU calculation, key managers, XFRM policy code, replay code, XFRM device offload, NAT keepalive, LSM hooks, audit, netlink extack, random SPI allocation, RCU/hash helpers, per-net namespaces, and optional user compatibility translation.

Integration points include outbound bundle creation in `xfrm_policy.c`, inbound state lookup in `xfrm_input.c`, user/netlink/PF_KEY state management, BPF XDP state lookup, hardware offload drivers, IKE/key-manager daemons through acquire/expire/migrate callbacks, and proc statistics through `xfrm_state_update_stats()`.

## Risks and Edge Cases

Identity and index consistency are critical. A state can be indexed by multiple hash tables plus per-policy/per-CPU caches; deletion must remove all links exactly once and invalidate cached users through generation IDs. RCU readers and hash resize seqcounts must not observe freed tables or states.

Acquire logic deliberately rate-limits key-manager requests. Bugs can either flood acquire messages or fail to request missing SAs, causing traffic drops. Per-CPU acquire policy adds another matching dimension and fallback behavior.

Lifetime timers interact with soft expiry, hard expiry, device stats updates, and audit/key-manager notifications. Changes can produce duplicate expiry messages, stale valid SAs, or premature deletion. Offload state ordering is sensitive because hardware resources and software SAD entries must stay coherent.

State initialization loads modules and validates modes/types/NAT keepalive/replay. Missing validation can admit impossible SAs; over-strict validation can break existing IPsec configurations. SPI allocation must avoid collisions across protocol and state tables while handling signals.

## Test Signals

Useful tests add, update, delete, flush, and walk states for ESP/AH/IPCOMP over IPv4 and IPv6; exercise acquire creation and expiration; allocate SPIs over fixed and random ranges; verify input lookup by SPI and output lookup by template; test packet offload and crypto offload; run namespace teardown; validate soft/hard lifetime notifications; and confirm audit records for SAD add/delete/replay/notfound/ICV failures.

Runtime observability includes `ip xfrm state`, `ip xfrm monitor`, `/proc/net/xfrm_stat`, XFRM audit messages, key-manager acquire/expire events, device offload callbacks, and MIB counters for missing states, expired states, proto/mode/sequence errors, and direction errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_state_bpf.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_state_bpf.c

## Purpose

`xfrm_state_bpf.c` exposes unstable BPF kfuncs that let XDP programs look up an XFRM state by mark, destination address, SPI, protocol, address family, and network namespace, then release the acquired state reference. The file is intentionally marked unstable, so compatibility can change.

## Important APIs, Types, and Functions

`struct bpf_xfrm_state_opts` is the BPF-visible options structure. It contains an `error` out parameter, `netns_id`, mark, destination address, SPI, protocol, and family. `BPF_XFRM_STATE_OPTS_SZ` fixes the expected size.

`bpf_xdp_get_xfrm_state()` validates `opts__sz`, validates `netns_id`, resolves either the current XDP device namespace or a namespace by ID, calls `xfrm_state_lookup()`, drops the namespace reference when needed, sets `opts->error` on failures, and returns a referenced `struct xfrm_state *` or NULL.

`bpf_xdp_xfrm_state_release()` releases a state returned by the lookup helper using `xfrm_state_put()`. The BTF kfunc set marks lookup as `KF_RET_NULL | KF_ACQUIRE` and release as `KF_RELEASE`. `register_xfrm_state_bpf()` registers the kfunc ID set for `BPF_PROG_TYPE_XDP`.

## Control Flow

At XFRM global initialization, `xfrm_init()` calls `register_xfrm_state_bpf()`. Later, verified XDP programs can call `bpf_xdp_get_xfrm_state()`. The helper derives the current netns from `xdp->rxq->dev`, optionally switches to a namespace ID, performs the SAD lookup, and returns with a held state reference. The verifier requires that all acquired references are released by `bpf_xdp_xfrm_state_release()`.

## State and Persistence Behavior

The file does not create persistent XFRM state. Its main state effect is reference ownership: successful lookup increments an XFRM state refcount via `xfrm_state_lookup()`, and release decrements it. Errors are communicated through the caller-provided `opts->error` field.

## Dependencies and Integration Points

Dependencies include BPF kfunc infrastructure, BTF IDs, XDP context internals, net namespace lookup by ID, and the exported `xfrm_state_lookup()` API from `xfrm_state.c`. It is registered from the XFRM init path in `xfrm_policy.c`.

## Risks and Edge Cases

The ABI is size-sensitive. The helper permits only the exact options size after confirming that the `error` field is writable; mismatched sizes return `-EINVAL`. Namespace ID handling must drop references on all paths after `get_net_ns_by_id()`. Because the returned pointer is a live kernel object, verifier acquire/release annotations are essential to prevent leaks.

Lookup semantics mirror SAD lookup and do not check policy authorization by themselves. XDP programs using this helper must treat a found SA as state information, not as a complete policy decision.

## Test Signals

BPF selftests should load XDP programs that call lookup and release on existing and missing SAs, pass current netns and explicit netns IDs, test invalid `opts__sz` and `netns_id`, and verify the verifier rejects paths that leak acquired state references. Runtime signals include expected `opts->error` values `-EINVAL`, `-ENONET`, and `-ENOENT`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_state_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_sysctl.c -->
# sources/distributed-fs/ceph-client/net/xfrm/xfrm_sysctl.c

## Purpose

`xfrm_sysctl.c` initializes and optionally exposes per-network-namespace XFRM sysctls under `net/core`. These knobs control async event notification thresholds, larval/acquire packet handling, and acquire-state lifetime.

## Important APIs, Types, and Functions

`__xfrm_sysctl_init()` sets defaults: `sysctl_aevent_etime = XFRM_AE_ETIME`, `sysctl_aevent_rseqth = XFRM_AE_SEQT_SIZE`, `sysctl_larval_drop = 1`, and `sysctl_acq_expires = 30`.

Under `CONFIG_SYSCTL`, `xfrm_table[]` defines `xfrm_aevent_etime`, `xfrm_aevent_rseqth`, `xfrm_larval_drop`, and `xfrm_acq_expires`. `xfrm_sysctl_init()` duplicates the table per namespace, wires each entry to the namespace's `net->xfrm` fields, hides entries from non-init user namespaces by registering a zero-sized table, and stores the registration header. `xfrm_sysctl_fini()` unregisters and frees the duplicated table. Without `CONFIG_SYSCTL`, init only applies defaults.

## Control Flow

Per-net initialization calls `xfrm_sysctl_init()` after policy/state/statistics setup. The function always initializes defaults first, then registers writable sysctls when configured. Per-net exit calls `xfrm_sysctl_fini()` in the sysctl-enabled build.

## State and Persistence Behavior

The actual persistent values are fields in `net->xfrm`, scoped to the network namespace. The sysctl table is per-namespace heap state so each table entry can point at the correct namespace fields. `sysctl_acq_expires` controls acquire state hard-add lifetime; `sysctl_larval_drop` controls whether missing-SA outbound traffic is dropped or queued; the async event knobs control replay notification behavior.

## Dependencies and Integration Points

Dependencies are sysctl infrastructure, slab allocation, net namespaces, user namespace checks, and XFRM definitions. Integration points include `xfrm_policy.c` queue/dummy bundle behavior, `xfrm_state.c` acquire timer setup, and `xfrm_replay.c` async event notification thresholds.

## Risks and Edge Cases

The sysctl table must be duplicated before assigning `.data`; sharing the static table would point all namespaces at the same fields. The unprivileged-user-namespace path registers no visible entries but still keeps defaults active. `xfrm_sysctl_fini()` assumes `net->xfrm.sysctl_hdr` is valid in the `CONFIG_SYSCTL` path, matching successful init ordering.

## Test Signals

Tests should read and write the four sysctls in the initial user namespace, verify defaults in a fresh net namespace, verify sysctls are hidden for unprivileged user namespaces, and confirm behavior changes: `xfrm_larval_drop` affects missing-SA queue/drop behavior, `xfrm_acq_expires` changes acquire expiry, and async event settings affect replay notification cadence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/xfrm/xfrm_sysctl.c -->
