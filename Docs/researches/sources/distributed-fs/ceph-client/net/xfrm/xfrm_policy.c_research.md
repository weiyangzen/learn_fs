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
