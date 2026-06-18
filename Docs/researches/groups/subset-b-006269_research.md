# subset-b-006269 net/sched classifier and ematch research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_flower.c -->
# sources/distributed-fs/ceph-client/net/sched/cls_flower.c

## Purpose

`cls_flower.c` implements the `flower` traffic-control classifier. It matches packets by structured flow-dissector keys rather than fixed byte offsets, covering Ethernet addresses, VLAN/CVLAN, IPv4/IPv6, transport ports and ranges, ICMP, ARP, MPLS stacks, tunnel metadata and options, conntrack fields, packet hash, PPPoE, L2TPv3, IPsec SPI, CFM, and `tc` metadata such as `l2_miss`. It is a hot-path classifier used by `tc filter ... flower`, software classification, and hardware offload through `TC_SETUP_CLSFLOWER`.

## Important APIs, Types, and Functions

Core state is split among `struct cls_fl_head`, `struct fl_flow_mask`, `struct cls_fl_filter`, `struct fl_flow_key`, and `struct fl_flow_tmplt`. `cls_fl_head` owns the mask rhashtable, mask list, hardware-filter list, and handle IDR. Each mask owns a per-mask rhashtable keyed by the masked key bytes and a flow dissector tailored to only the requested fields. Each filter stores the raw key, masked key, actions/extensions, class result, offload flags, handle, hardware count, deleted bit, and refcount.

The main classifier path is `fl_classify()`. Management enters through `fl_init()`, `fl_change()`, `fl_delete()`, `fl_destroy()`, `fl_get()/fl_put()`, `fl_walk()`, `fl_dump()`, `fl_terse_dump()`, and `fl_delete_empty()` in `cls_fl_ops`. Key parsing is concentrated in `fl_set_key()` and helpers for MPLS, VLAN, PPPoE, flags, IP fields, tunnel options, conntrack, CFM, port ranges, and IPsec SPI. Mask creation and lookup are handled by `fl_mask_update_range()`, `fl_init_dissector()`, `fl_create_new_mask()`, `fl_check_assign_mask()`, `fl_ht_insert_unique()`, and `fl_mask_lookup()`. Offload integration uses `fl_hw_replace_filter()`, `fl_hw_destroy_filter()`, `fl_hw_update_stats()`, `fl_reoffload()`, `fl_hw_add()`, `fl_hw_del()`, and template hooks.

## Control Flow

Initialization allocates `cls_fl_head`, initializes the mask list/lock, hardware list, handle IDR, and rhashtable. Classification iterates the RCU-protected mask list. For each mask it clears only the masked key range, runs metadata, tunnel, conntrack, hash, and packet flow dissection into a stack key, computes a masked lookup key, and checks the per-mask rhashtable. Port-range masks take a slower list-assisted path to verify range bounds before the hash lookup. A hit copies the stored `tcf_result` and executes the filter extensions unless software matching is skipped.

`fl_change()` parses netlink options, allocates a temporary mask and new filter, reserves or reuses a handle, validates actions, binds a class, parses keys and masks, validates template compatibility, enables `tc_skb_ext` when needed, assigns or creates the shared mask, inserts a unique masked-key entry, pushes hardware offload if requested, and then publishes the rule under `tp->lock`. Replacement swaps the IDR entry and list node, removes the old rhashtable entry, marks the old filter deleted, destroys old hardware state, unbinds its class, and drops references. Error unwinding removes IDR entries, hardware state, rhashtable entries, masks, class bindings, and filter references in reverse order.

Deletion marks a filter deleted under `tp->lock`, removes it from the mask table, IDR, and list, possibly drops the now-empty mask, destroys hardware state, unbinds the class, and releases the filter. Destroy walks all masks and filters through the same deletion path, destroys the handle IDR, then queues sleepable rhashtable/head cleanup.

Dumping mirrors the parser: `fl_dump_key()` emits only fields with non-zero masks, including nested MPLS, tunnel options, conntrack, flags, and CFM. Full dumps update hardware stats before emitting extension stats; terse dumps emit only flags and terse extension data. Template operations parse a mask-only rule, create/destroy hardware hints, and reject filters whose masks exceed the template mask.

## State and Persistence Behavior

Filter state persists in the handle IDR, per-mask filter lists, and per-mask rhashtables. Masks are shared and refcounted; they are inserted in a global mask table so rules with identical masks reuse the same dissector and lookup table. Filter references are atomic because `flower` uses `TCF_PROTO_OPS_DOIT_UNLOCKED`; the code can race with concurrent get/delete/change paths and uses `tp->lock`, RCU lists, IDR lookups under RCU, and explicit `deleted` checks.

Hardware state is tracked through per-filter `flags`, `in_hw_count`, and `hw_list`. `fl_hw_add()` and `fl_hw_del()` maintain the offloaded-filter list from driver callbacks. A rule matching `l2_miss` enables the shared `tc_skb_ext` facility and disables it when the filter is finally freed. Masks and filters are freed through `rcu_work`, with action net references deciding whether final destruction must run later.

## Dependencies and Integration Points

The file depends on `net/pkt_cls.h`, `net/sch_generic.h`, `flow_dissector`, tunnel metadata helpers for Geneve/VXLAN/ERSPAN/GTP/PFCP, conntrack UAPI bits, `tcf_exts`, `tcf_block` offload callbacks, IDR, rhashtable, RCU, and netlink policy parsing. It integrates with `cls_api` through `struct tcf_proto_ops`, with drivers through `TC_SETUP_CLSFLOWER`, and with chain templates through `tmplt_create/destroy/reoffload/dump`.

## Risks and Edge Cases

The mask-sharing path is concurrency-sensitive: a temporary zero-ref mask is inserted to block duplicate mask creation, and callers must handle `-EAGAIN` when a concurrent delete races. Mask range calculation and masked-key hashing must stay consistent or lookups and dumps diverge. Tunnel option parsing requires key/mask lengths to stay aligned and only one option type per rule. Port-range matching combines a list scan with hash lookup and is easy to break by changing `mkey` updates. Conntrack matching is compile-time-feature gated; accepting unsupported fields would create silently unmatchable rules. Offload failure semantics depend on `skip_sw`/`skip_hw` flags, so changes can unexpectedly install software fallbacks or reject valid hardware-only filters.

This local source also contains apparent corruption markers such as duplicated assignments in `fl_range_port_src_cmp()`. Those are compile/test risks for this snapshot and should be distinguished from upstream logic when validating.

## Test Signals

Useful signals include `tc` flower add/replace/delete/dump tests for each key family, netlink extack checks for invalid flags, conntrack, MPLS, tunnel option, and port range combinations, concurrent add/delete stress, `skip_sw` and `skip_hw` offload tests against a driver or dummy callback, and dump round-trip checks. Kernel selftests under networking/tc and driver offload tests should catch many regressions; compile coverage needs conntrack zones/marks/labels, tunnel options, MPLS, and CFM enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_fw.c -->
# sources/distributed-fs/ceph-client/net/sched/cls_fw.c

## Purpose

`cls_fw.c` implements the legacy `fw` traffic-control classifier. It maps `skb->mark`, optionally masked and input-device constrained, to a class result and action chain. It also preserves the older mode where no classifier table is allocated and the packet mark itself is interpreted as a classid for non-shared blocks.

## Important APIs, Types, and Functions

`struct fw_head` stores the global mark mask and 256 hash buckets. `struct fw_filter` stores a mark id, class result, input ifindex, action extensions, owning proto, and deferred free work. `fw_hash()` folds the 32-bit mark into a bucket. The `tcf_proto_ops` implementation is `fw_classify()`, `fw_init()`, `fw_get()`, `fw_change()`, `fw_delete()`, `fw_destroy()`, `fw_walk()`, `fw_dump()`, and `fw_bind_class()`.

`fw_set_parms()` validates actions/police, resolves `TCA_FW_INDEV`, enforces a single head-wide mask, and binds classid. `__fw_delete_filter()` and `fw_delete_filter_work()` destroy actions and release their net references after RCU/action users are gone.

## Control Flow

`fw_classify()` reads `tp->root` under BH RCU. If a head exists, it masks `skb->mark`, scans the matching bucket, verifies id and input device, executes extensions, and returns the action result. If no head exists, it falls back to the old mark-as-classid method unless the block is shared.

`fw_change()` accepts an empty options block only for the old mode. Otherwise it parses netlink options. Replacing an existing filter allocates a new filter, initializes extensions, copies stable fields, validates parameters, swaps it into the bucket with RCU assignment, unbinds and queues the old filter for destruction, and returns the new pointer. Creating the first explicit filter allocates `fw_head`, records the mask, allocates a filter, validates parameters, and inserts it at the bucket head.

Deletion unlinks the exact filter from its bucket, unbinds its class, takes an extension net reference, queues deferred destruction, and reports whether all buckets are empty. Destroy drains every bucket, unbinds each class, queues or performs final destruction, and RCU-frees the head. Dump emits classid, input device, non-default mask, extensions, and stats.

## State and Persistence Behavior

Persistent state is only in the classifier head and its RCU bucket chains. The mark mask is global to the head; later filters must use the same mask or the update is rejected. Class bindings are maintained through `tcf_bind_filter()` and `tcf_unbind_filter()`. Filter destruction is deferred when actions still need net context. The old fallback mode stores no classifier state.

## Dependencies and Integration Points

The classifier integrates with `cls_api` via `register_tcf_proto_ops()`, with netfilter or other producers of `skb->mark`, with qdisc classes through `tcf_result`, with action extensions through `tcf_exts`, and with block sharing checks through `tcf_block_shared()` and `tcf_block_q()`.

## Risks and Edge Cases

The head-wide mask is an important compatibility constraint; changing it per filter would make hash lookup ambiguous. Old mark-as-classid mode is disabled for shared blocks because there is no single qdisc handle to compare. Replacement must preserve RCU list integrity while old filters can still be read. This snapshot contains a duplicated local declaration in `fw_set_parms()`, which is a compile risk in the local tree.

## Test Signals

Use `tc filter add fw handle ... classid ...`, masked mark tests, input-device match tests, replacement and deletion tests, dump round trips, and action execution checks. Shared block tests should verify that explicit marks are required and old mode is rejected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_matchall.c -->
# sources/distributed-fs/ceph-client/net/sched/cls_matchall.c

## Purpose

`cls_matchall.c` implements the `matchall` classifier: a single rule that matches every packet unless software classification is skipped. It is mainly a simple carrier for class binding, action execution, packet hit counters, and hardware offload of catch-all policies.

## Important APIs, Types, and Functions

`struct cls_mall_head` is the entire classifier instance. It stores extensions, result, handle, flags, hardware count, per-CPU hit counters, deferred destroy work, and a `deleting` marker. Key functions are `mall_classify()`, `mall_change()`, `mall_delete()`, `mall_destroy()`, `mall_walk()`, `mall_dump()`, `mall_reoffload()`, `mall_replace_hw_filter()`, `mall_destroy_hw_filter()`, and `mall_stats_hw_filter()`.

## Control Flow

Classification reads the single head under BH RCU, rejects missing head or `skip_sw`, copies the result, increments the current CPU hit counter, and executes extensions. Creation parses one options block, rejects a second rule with `-EEXIST`, validates flags, allocates the head and per-CPU counters, validates actions with offload flags, optionally binds classid, attempts hardware replacement unless `skip_hw`, updates software-use state, and publishes `tp->root`. Delete only marks the rule as deleting and reports `last=true`; final cleanup is done by destroy.

Destroy unbinds the class, destroys hardware state unless skipped, and frees extensions/per-CPU memory either immediately or through queued work. Walk skips missing or deleting heads. Dump refreshes hardware stats when applicable, emits classid, flags, aggregated per-CPU hit count, extensions, and extension stats. Reoffload rebuilds a one-rule `flow_rule` and calls the block callback for replace or destroy.

## State and Persistence Behavior

Only one head can persist per classifier. Runtime hit state lives in `struct tc_matchall_pcnt` per CPU and is aggregated on dump. Offload state is persisted in `flags` and `in_hw_count`. Action net references decide whether destruction can run immediately. The `deleting` flag hides the rule from walks while the proto is being removed.

## Dependencies and Integration Points

It depends on `tcf_exts`, per-CPU allocation, `tc_setup_offload_action()`, `tc_setup_cb_add/destroy/reoffload/call()`, and `TC_SETUP_CLSMATCHALL`. It registers as classifier kind `matchall` and supports class binding.

## Risks and Edge Cases

`skip_sw` means the software path must return no match even though the rule logically matches all packets. Hardware-only rules require at least one successful offload. A single-rule classifier means replacement is not supported by adding another rule; callers must delete first. Counter aggregation is best effort across CPUs.

## Test Signals

Test plain matchall action execution, `skip_sw`/`skip_hw` behavior, hardware stats refresh, delete/walk hiding, class binding, and dump of `TCA_MATCHALL_PCNT`. Offload tests should verify failure behavior for hardware-only rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_matchall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_route.c -->
# sources/distributed-fs/ceph-client/net/sched/cls_route.c

## Purpose

`cls_route.c` implements the `route`/`route4` classifier, which maps route realm/classid metadata (`dst->tclassid`) and incoming interface to traffic-control classes and actions. It is legacy IPv4 routing-realm classification optimized around small tag values.

## Important APIs, Types, and Functions

`struct route4_head` owns 257 top-level buckets and a 16-entry fastmap cache. `struct route4_bucket` contains 33 filter chains: 16 `from` buckets, 16 incoming-interface buckets, and one wildcard bucket. `struct route4_filter` stores id, iif, result, extensions, handle, bucket pointer, proto pointer, and deferred work.

Hash helpers include `route4_hash_to()`, `route4_hash_from()`, `route4_hash_iif()`, `route4_hash_wild()`, `to_hash()`, and `from_hash()`. Core operations are `route4_classify()`, `route4_change()`, `route4_delete()`, `route4_destroy()`, `route4_get()`, `route4_walk()`, `route4_dump()`, and `route4_bind_class()`. `route4_set_parms()` builds canonical handles from `to`, `from`, and `iif`.

## Control Flow

Classification obtains `skb_dst()`, reads `dst->tclassid` and `inet_iif()`, then checks the fastmap under `fastmap_lock`. A cached success returns the class immediately; a cached failure returns no match. On cache miss it searches the `to` bucket, first exact `from`, then `iif`, then wildcard, then repeats with `to ANY` by clearing lower bits and using table index 256. A matching rule executes extensions if present; rules without actions may be cached in fastmap.

Creation requires a non-zero handle and options. `route4_set_parms()` validates actions, rejects simultaneous `from` and `iif`, constructs or verifies the canonical handle, allocates a bucket if needed, fills id/iif/class result, and binds classid. `route4_change()` allocates a new filter for both create and replace, inserts it ordered by handle, keeps destination metadata through `tcf_block_netif_keep_dst()`, removes any old filter, resets fastmap, and queues old destruction. Delete unlinks a filter, resets fastmap, queues destruction, frees an empty bucket, and reports whether the classifier is now empty. Destroy drains all buckets and RCU-frees buckets/head.

## State and Persistence Behavior

Persistent state is the bucket tree plus the fastmap cache. The fastmap is guarded by a global spinlock because the triple of id, iif, and filter pointer must change atomically. Filter memory and buckets are RCU-freed. Action net references can delay final filter free. Class binding persists in each filter result and is unbound during delete/destroy.

## Dependencies and Integration Points

The classifier depends on route metadata (`dst_entry::tclassid`), `inet_iif()`, `skb_dst()`, `tcf_exts`, qdisc class binding, netlink route4 attributes, RTNL-protected updates, and RCU-protected classification. It registers classifier kind `route`.

## Risks and Edge Cases

Fastmap cache invalidation is required on every topology change or stale filter pointers can be returned. The priority order (`to/from`, `to/iif`, wildcard, then `to ANY`) is user-visible. `from` and `iif` are mutually exclusive. Handle construction is subtle: top-level hash, from/iif encoding, and wildcard values must match dump/get/delete expectations. This local source has an apparent extra brace after `__route4_delete_filter()`, which is a compile risk in this snapshot.

## Test Signals

Use route realm classification tests with exact `to/from`, `to/fromif`, wildcard, and `to ANY` rules; replacement and deletion with fastmap invalidation; dump round trips for canonical handles; and action/class binding checks. Build tests should catch the local syntax issue.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_u32.c -->
# sources/distributed-fs/ceph-client/net/sched/cls_u32.c

## Purpose

`cls_u32.c` implements the universal 32-bit key traffic-control classifier. It matches packets using arrays of 32-bit value/mask tests at configurable offsets, supports hierarchical hash tables linked from key nodes, optional mark checks, optional performance counters, class binding, actions, and hardware offload through `TC_SETUP_CLSU32`.

## Important APIs, Types, and Functions

`struct tc_u_knode` is a key node containing a handle, parent/child hnode pointers, selector (`tc_u32_sel` plus flexible keys), action extensions, input device, class result, flags, offload count, optional per-CPU stats and mark state, and deferred work. `struct tc_u_hnode` is a hash table with handle, priority, divisor, IDR of keys, refcount, root marker, flags, and flexible bucket array. `struct tc_u_common` shares hnodes between protos attached to the same block/qdisc key.

Major functions are `u32_classify()`, `u32_init()`, `u32_change()`, `u32_delete()`, `u32_destroy()`, `u32_get()`, `u32_walk()`, `u32_dump()`, and `u32_reoffload()`. Helpers manage handle ID allocation (`gen_new_htid()`, `gen_new_kid()`), shared common lookup, key/hnode destruction, parameter validation, replacement cloning, and offload add/delete for hnodes and knodes.

## Control Flow

Classification starts at the root hnode and selected bucket. For each knode it honors `skip_sw`, optional mark mask/value, then evaluates every selector key by reading four bytes with `skb_header_pointer_careful()`. If all keys match and no child hnode exists, terminal nodes execute input-device checks, update optional counters, execute actions, and return. If a child hnode exists, the current node and offset are pushed on a bounded stack, the child bucket is selected by hashing a packet word with the selector mask/shift, and variable/eat offsets are applied. On child exhaustion the stack pops and terminal handling resumes. Stack overflow returns no match and logs a ratelimited warning.

Initialization allocates a root hnode, finds or creates shared `tc_u_common`, links the root into the common hnode list, and stores common data in `tp->data`. `u32_change()` handles three cases: replacing an existing knode by cloning it and swapping under RCU; creating a new hnode when `TCA_U32_DIVISOR` is present; or creating a new knode in a selected hash table. Knode creation validates selectors, allocates optional stats, initializes actions, handles `TCA_U32_LINK`, classid, input device, mark data, hardware offload, sorted bucket insertion, and common knode accounting.

Deletion removes hardware state, unlinks knodes from their parent hnode, removes IDR entries, unbinds classes, and queues/free keys. Hnode deletion is allowed only when it is not root and its refcount is one. Destroy drops the root and common references and drains any remaining shared hnodes. Dump emits either hnode divisor or knode selector/hash/class/link/flags/mark/counters/input-device/extensions and stats.

## State and Persistence Behavior

State persists in shared `tc_u_common` structures keyed by shared block or qdisc pointer, so multiple protos can reference the same hnode namespace. Hnodes and linked child hnodes are refcounted. Handles are allocated by IDR and encode htid, bucket, and node id. Optional performance counters and mark success counters are per CPU and deliberately shared across replacement clones until old readers are gone. Hardware state is in `flags` and `in_hw_count`.

## Dependencies and Integration Points

The file depends on `tc_u32_sel`, `tc_u32_key`, `tcf_exts`, `tcf_block`, IDR, RCU, per-CPU counters, optional `CONFIG_CLS_U32_PERF` and `CONFIG_CLS_U32_MARK`, and hardware offload callbacks using `TC_SETUP_CLSU32`. It registers classifier kind `u32` and can bind classes.

## Risks and Edge Cases

Handle encoding and IDR ownership are subtle and user-visible. Linked hnode refcounts must be balanced during update, error unwind, and delete or child tables can leak or be freed while referenced. Replacement clones share per-CPU stats, so freeing the wrong variant can double-free counters. Offset arithmetic and `TC_U32_EAT`/variable offset handling are packet-safety critical. Hardware-only rules must fail when not actually in hardware. This local source contains apparent duplicate lines around bucket selection and hnode allocation, which are compile/review risks for this snapshot.

## Test Signals

Test root and non-root hnode creation, handle auto-allocation and explicit handles, hash bucket matching, linked table traversal, variable/eat offsets, mark matching, input-device checks, class/action execution, replacement preserving counters, deletion of busy hnodes, dump round trips, and `skip_sw`/`skip_hw` offload behavior. Compile both with and without `CONFIG_CLS_U32_PERF` and `CONFIG_CLS_U32_MARK`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/cls_u32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_canid.c -->
# sources/distributed-fs/ceph-client/net/sched/em_canid.c

## Purpose

`em_canid.c` implements an extended match for CAN frames. It lets ematch-capable classifiers test the CAN identifier in an skb against a list of `struct can_filter` rules, optimized for standard 11-bit CAN identifiers and preserving full rule data for dumps and extended identifiers.

## Important APIs, Types, and Functions

`struct canid_match` stores a bitmap for all SFF IDs, counts for total/SFF/EFF rules, and a flexible raw rule array. `em_canid_change()` validates and compiles the user rule array. `em_canid_match()` reads the CAN id from `struct can_frame` data, uses the bitmap for SFF frames, and linearly scans EFF rules. `em_canid_dump()` emits raw rules. `em_canid_destroy()` frees compiled state. The module registers `TCF_EM_CANID`.

## Control Flow

Change rejects empty, misaligned, or more than 500 rules, allocates state plus raw rule storage, copies EFF rules first for a compact match loop, then copies SFF rules and expands each SFF mask into the bitmap. Match first ensures the skb has a full CAN frame. EFF frames compare against the EFF rule prefix; SFF frames mask to 11 bits and test one bitmap bit. Dump returns the original rule array order as stored in `rules_raw`.

## State and Persistence Behavior

Compiled state is per ematch instance and owned by `m->data`. The SFF bitmap is derived state; raw rules are persisted for EFF matching and netlink dump. There is no global state other than module registration.

## Dependencies and Integration Points

It depends on CAN frame layout from `<linux/can.h>`, ematch core registration, skb pull helpers, and netlink raw ematch payload handling. It is usable only where an ematch tree is attached by another classifier.

## Risks and Edge Cases

The code assumes CAN ID is at `skb->data` after ensuring `CAN_MTU`. SFF expansion can be expensive for broad masks but is bounded by 2048 IDs and 500 rules. Filters matching the same numeric id as SFF and EFF require separate rules due to SFF/EFF separation.

## Test Signals

Use SFF exact, SFF masked, all-SFF, EFF exact/masked, mixed rule, over-limit, misaligned length, dump, and inverted ematch tree tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_canid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_cmp.c -->
# sources/distributed-fs/ceph-client/net/sched/em_cmp.c

## Purpose

`em_cmp.c` implements the basic comparison ematch. It compares an 8-, 16-, or 32-bit value at a configured packet layer and offset against a configured operand using equality, less-than, or greater-than semantics.

## Important APIs, Types, and Functions

The module consumes `struct tcf_em_cmp` as fixed-size ematch data. `em_cmp_match()` obtains a base pointer with `tcf_get_base_ptr()`, validates the offset/width with `tcf_valid_offset()`, reads unaligned big-endian data, optionally transforms endian order when `TCF_EM_CMP_TRANS` is set, applies a mask, and evaluates the operand. `em_cmp_ops` registers `TCF_EM_CMP`.

## Control Flow

There is no custom change callback; the ematch core copies the fixed data after checking `datalen`. Match returns false on missing base pointer, invalid offset, unsupported alignment, or unsupported operand. Valid reads dispatch by alignment and then compare.

## State and Persistence Behavior

All state is the copied `tcf_em_cmp` payload held by the ematch core. The module has no per-net or global runtime state beyond registration.

## Dependencies and Integration Points

It depends on ematch core data handling, packet-layer base helpers, skb bounds checking, and unaligned access helpers. It is used inside ematch trees by classifiers that support `TCA_EMATCH_TREE`.

## Risks and Edge Cases

Endian transformation is opt-in and only meaningful for 16/32-bit reads. Offset validation must remain paired with the chosen alignment or malformed skbs could be read out of bounds. Unsupported alignment/operator values fail closed.

## Test Signals

Test all alignments, EQ/LT/GT operands, masks, transform flag, invalid layer/offset, packet truncation, and inverted/combined ematch-tree behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_ipset.c -->
# sources/distributed-fs/ceph-client/net/sched/em_ipset.c

## Purpose

`em_ipset.c` implements an ematch that tests IPv4 or IPv6 packets against a netfilter ipset. It bridges traffic-control ematch evaluation with `ip_set_test()` using `struct xt_set_info` configuration.

## Important APIs, Types, and Functions

`em_ipset_change()` validates the fixed `xt_set_info` payload, gets a netns ipset reference by index, and copies the payload. `em_ipset_match()` determines packet family, ensures network headers are present, prepares `ip_set_adt_opt` and `xt_action_param`, temporarily pulls the skb to the network offset, resolves input/output devices under RCU, calls `ip_set_test()`, and restores the skb. `em_ipset_destroy()` releases the ipset reference and frees state.

## Control Flow

Configuration fails if the payload size is wrong or the set index is invalid. Match accepts only IPv4 and IPv6 packets. It fills ipset dimensions and flags from the saved config, uses the skb input interface if available, and returns the ipset test result as the ematch result.

## State and Persistence Behavior

Each ematch instance holds a copied `xt_set_info` and a reference to the netns ipset index. Destruction releases the reference through `ip_set_nfnl_put()`. No other persistent state is kept.

## Dependencies and Integration Points

It depends on netfilter ipset (`xt_set_info`, `ip_set_nfnl_get_byindex()`, `ip_set_test()`), IPv4/IPv6 header helpers, `nf_hook_state`, ematch core, and skb protocol helpers.

## Risks and Edge Cases

The skb pull/push around `network_offset` must be balanced. ipset currently does not use IPv6 transport header offset here, so the code uses a fixed IPv6 header length. Set index lifetime depends on correct get/put. Non-IP packets fail closed.

## Test Signals

Test IPv4 and IPv6 sets, input-interface dependent sets, invalid set index, destroy/reconfigure reference balance, truncated network headers, and non-IP packets.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_ipset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_ipt.c -->
# sources/distributed-fs/ceph-client/net/sched/em_ipt.c

## Purpose

`em_ipt.c` implements an ematch that runs selected x_tables matches from traffic control. This snapshot supports the `policy` and `addrtype` xt matches for IPv4/IPv6, allowing TC filters to reuse netfilter match logic.

## Important APIs, Types, and Functions

`struct em_ipt_match` stores the selected `xt_match`, hook, nfproto, and aligned match data. `em_ipt_change()` parses netlink attributes, validates nfproto and supported match name/revision, loads the xt match with `xt_request_find_match()`, copies match data, and calls `xt_check_match()`. `em_ipt_match()` prepares `nf_hook_state` and `xt_action_param` and calls the xt match callback. `em_ipt_destroy()` calls the xt destroy callback if present, drops the module reference, and frees state. `em_ipt_dump()` serializes the match name, hook, revision, nfproto, and match data.

## Control Flow

Configuration requires hook, match name, match data, and nfproto. `get_xt_match()` whitelists match names and invokes match-specific validators: policy revision 0 only and only on `NF_INET_PRE_ROUTING`, addrtype revision 1 only. Runtime match accepts IPv4 or IPv6 packets, ensures the relevant network header is present, resolves the incoming device under RCU, initializes hook state, and returns the xt match result.

## State and Persistence Behavior

Each ematch instance owns one `em_ipt_match` allocation and a module reference on the xt match. Match-specific internal resources are owned by x_tables and released through the match destroy callback. There is no global state beyond ematch registration.

## Dependencies and Integration Points

It depends on x_tables, IPv4/IPv6 netfilter headers, `xt_check_match()`, `xt_request_find_match()`, `nf_hook_state_init()`, ematch core, and skb protocol/header helpers. It exposes ematch kind `TCF_EM_IPT`.

## Risks and Edge Cases

Only whitelisted xt matches are supported; blindly allowing arbitrary xt modules would need stronger validation. Hook and nfproto must match what the xt module expects. Module references and match destroy callbacks must be balanced. `match_data` is aligned with `XT_ALIGN()` and dump uses `usersize` where available, so size mismatches can break round trips.

## Test Signals

Test policy and addrtype valid configs, unsupported names/revisions, wrong hook for policy, IPv4/IPv6 packets, truncated headers, dump round trips, and module unload/reload reference behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_ipt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_meta.c -->
# sources/distributed-fs/ceph-client/net/sched/em_meta.c

## Purpose

`em_meta.c` implements the metadata ematch. It compares two metadata values, each either collected from the skb/kernel/socket/device state or supplied by userspace, using integer or variable-length string semantics. It lets ematch-capable classifiers express predicates over packet length, priority, mark, route classid, device name/index, socket fields, load average, random values, VLAN tag, and hash.

## Important APIs, Types, and Functions

`struct meta_value` stores a `tcf_meta_val` header plus optional static value data. `struct meta_match` stores left and right values. Collector functions are generated by `META_COLLECTOR()` and assigned in `__meta_ops[type][id]`. Type operations live in `__meta_type_ops` and provide compare/change/apply/dump/destroy behavior for `TCF_META_TYPE_VAR` and `TCF_META_TYPE_INT`.

Core functions are `meta_get()`, `em_meta_match()`, `em_meta_change()`, `em_meta_destroy()`, and `em_meta_dump()`. Integer collectors read skb fields, route metadata, socket fields, load averages, random bytes, VLAN tags, and RX hash. Variable collectors read device names and bound interface names.

## Control Flow

Configuration parses `TCA_EM_META_HDR`, verifies both sides have the same type and valid ids, allocates a `meta_match`, copies headers, checks collector support, and applies optional static left/right value attributes through the type-specific `change()` function. Match resolves each side with `meta_get()`: static values are copied directly, dynamic ids call the collector, and type-specific extras such as shift and mask are applied. The comparison result is interpreted by EQ/LT/GT. Dump rebuilds the header and emits static payloads through type-specific dump hooks.

## State and Persistence Behavior

Each ematch instance stores a `meta_match`. Static variable values allocate memory and are freed by `meta_var_destroy()`. Static integer values are stored inline in `unsigned long`. Dynamic values are read at match time and are not cached. Socket and device fields are best-effort snapshots; some use RCU or `READ_ONCE()`.

## Dependencies and Integration Points

The file depends on skb internals, netdevice, route/dst metadata, socket fields, VLAN helpers, load average state, random bytes, ematch core, and `linux/tc_ematch/tc_em_meta.h`. It is consumed through ematch trees attached to classifiers.

## Risks and Edge Cases

Many collectors fail closed when required context is absent, such as no skb dst or no associated full socket. Variable comparisons are length-sensitive and use raw byte compare after optional shift. Integer masks are encoded in the static `val` field and applied as extras, which can be non-obvious. Collector table bounds and unsupported ids must be enforced or NULL function calls are possible. This local source includes apparent duplicated text/code near `META_COLLECTOR(int_rtiif)` and the meta-ops comment, which is a compile/review risk.

## Test Signals

Test integer EQ/LT/GT, variable device-name comparisons, static left/right values, shifts and masks, socket-dependent collectors with local and forwarded packets, absent route/socket/device contexts, VLAN tag collection, dump round trips, and unsupported type/id rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_meta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_nbyte.c -->
# sources/distributed-fs/ceph-client/net/sched/em_nbyte.c

## Purpose

`em_nbyte.c` implements an ematch that compares an arbitrary byte pattern at a configured layer and offset inside the skb. It is a simple fixed-pattern matcher for short packet fields that are not necessarily 32-bit aligned.

## Important APIs, Types, and Functions

`struct nbyte_data` wraps `struct tcf_em_nbyte` and a flexible pattern. `em_nbyte_change()` validates payload size and copies the header plus pattern. `em_nbyte_match()` resolves the configured base layer with `tcf_get_base_ptr()`, adds the offset, validates the requested length with `tcf_valid_offset()`, and compares bytes with `memcmp()`. `em_nbyte_ops` registers `TCF_EM_NBYTE`.

## Control Flow

Configuration rejects payloads shorter than the header or shorter than header plus declared pattern length. Matching fails closed on missing layer base or out-of-bounds range; otherwise exact byte equality returns true.

## State and Persistence Behavior

All state is copied into `m->data` and freed by the ematch core because this module has no custom destroy callback. No global state is kept besides registration.

## Dependencies and Integration Points

It depends on ematch core default data management, packet base helpers, skb bounds checking, and netlink payload layout from `tc_em_nbyte.h`.

## Risks and Edge Cases

The declared length controls both allocation and match bounds. Large lengths are bounded only by the netlink attribute size and memory allocation. Matching is exact; masks or partial wildcards require other ematches.

## Test Signals

Test valid pattern matches at network/transport layers, truncated packets, invalid layer, zero-length or malformed config, dump through ematch core, and inversion/boolean composition in ematch trees.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_nbyte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_text.c -->
# sources/distributed-fs/ceph-client/net/sched/em_text.c

## Purpose

`em_text.c` implements a textsearch-backed ematch. It scans a configured skb byte range for a pattern using a named Linux textsearch algorithm, enabling TC ematch users to match embedded byte strings without writing a full classifier.

## Important APIs, Types, and Functions

`struct text_match` stores from/to layer and offset boundaries plus a `struct ts_config`. `em_text_change()` validates range config, prepares or autoloads the textsearch algorithm, and stores compiled state. `em_text_match()` resolves the start/end layer pointers and calls `skb_find_text()`. `em_text_destroy()` destroys the textsearch config and frees state. `em_text_dump()` emits algorithm name, offsets, layers, pattern length, and pattern bytes.

## Control Flow

Configuration validates that the payload includes the pattern, that from-layer is not after to-layer, and that offsets are ordered within the same layer. It first tries `textsearch_prepare()` without autoload; on `-ENOENT` it drops RTNL, retries with `TS_AUTOLOAD`, then returns `-EAGAIN` after successful autoload so the caller can replay under normal locking. Runtime match converts layer-relative boundaries to skb-data offsets and returns true when `skb_find_text()` finds the pattern.

## State and Persistence Behavior

Compiled textsearch state is per ematch instance and owned by `m->data`. The textsearch algorithm module/config is held by `ts_config` and released on destroy. No match results are cached.

## Dependencies and Integration Points

It depends on the kernel textsearch API, ematch core, skb range helpers, RTNL behavior around module autoload, and `tc_em_text.h` payload format.

## Risks and Edge Cases

The autoload path deliberately returns `-EAGAIN` after loading so callers must retry. Range calculations depend on valid layer base pointers and can fail closed when a header is unavailable. Textsearch cost depends on selected algorithm and scan window.

## Test Signals

Test multiple textsearch algorithms, module autoload retry, same-layer and cross-layer ranges, invalid ordering, truncated skb ranges, dump round trips, and negative matches.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_u32.c -->
# sources/distributed-fs/ceph-client/net/sched/em_u32.c

## Purpose

`em_u32.c` implements a small ematch based on the `cls_u32` 32-bit key format. It tests one `struct tc_u32_key` against packet data, using the skb network header or an ematch packet-info pointer as the base.

## Important APIs, Types, and Functions

`em_u32_match()` is the only runtime function. It computes the pointer from `skb_network_header()` or `info->ptr`, adds `(info->nexthdr & key->offmask)` when packet info is supplied, then adds `key->off`, validates four bytes, and applies the classic `((word ^ val) & mask) == 0` predicate. `em_u32_ops` declares fixed `datalen = sizeof(struct tc_u32_key)` and registers `TCF_EM_U32`.

## Control Flow

There is no custom change callback; the ematch core validates and copies fixed-size key data. Runtime matching fails closed on invalid offset and returns the mask comparison result otherwise.

## State and Persistence Behavior

All persistent state is the copied `tc_u32_key` in `m->data`. The module has no dynamic per-instance allocations and no global state besides registration.

## Dependencies and Integration Points

It depends on the ematch core, `tc_u32_key` layout from packet classifier headers, skb network-header helpers, optional `tcf_pkt_info`, and skb offset validation.

## Risks and Edge Cases

The code dereferences a `__be32 *` directly after validation, so alignment assumptions follow architecture/network-header behavior. `info->nexthdr & offmask` makes behavior dependent on callers that populate packet info. Endianness follows the u32 key values supplied by userspace.

## Test Signals

Test network-header base matches, packet-info base matches, offmask behavior, truncated skbs, exact and masked values, and ematch inversion/boolean composition.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/em_u32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/ematch.c -->
# sources/distributed-fs/ceph-client/net/sched/ematch.c

## Purpose

`ematch.c` is the core extended-match framework for traffic-control classifiers. It registers ematch kinds, validates netlink ematch trees, owns module references and per-match private data, dumps trees, destroys trees, and evaluates boolean ematch expressions with AND/OR/END/inversion/container semantics.

## Important APIs, Types, and Functions

Global state is `ematch_ops`, protected by `ematch_mod_lock`. Public exports are `tcf_em_register()`, `tcf_em_unregister()`, `tcf_em_tree_validate()`, `tcf_em_tree_destroy()`, `tcf_em_tree_dump()`, and `__tcf_em_tree_match()`. `tcf_em_validate()` validates one match attribute, loads modules when needed, handles container references, invokes kind-specific `change()`, or copies simple/raw data. `tcf_em_match()` applies inversion around a kind-specific match result.

## Control Flow

Registration inserts a unique kind with a required `match()` callback. Validation parses tree header/list attributes, allocates an array sized by `nmatches`, requires match attributes to be numbered sequentially, validates each match, and verifies the actual count equals the header. Container matches store a forward-only reference to another sequence; backward/self references are rejected to avoid loops. Unknown kinds may trigger module autoload by temporarily dropping RTNL and then returning `-EAGAIN` so the request can be replayed.

Destroy walks each match, calls kind-specific destroy or default `kfree()` for non-simple copied data, releases the module reference, and frees the match array. Dump emits the tree header and each match as a nested, sequential netlink attribute, delegating kind-specific payloads when available. Matching interprets the flat match array as a stack-based expression: containers push the current index and jump to a referenced sequence, markers/operators decide early end, and stack pop restores the caller sequence. Stack overflow fails closed with a ratelimited warning.

## State and Persistence Behavior

The registry persists for loaded ematch modules. Each validated tree owns a match array, module references for concrete kinds, copied or kind-managed data, and its header. Trees are immutable while in use; callers are expected to validate into a temporary tree and then publish safely in their classifier private state.

## Dependencies and Integration Points

It depends on RTNL, module loading, netlink attribute parsing/dumping, `tcf_ematch_ops` supplied by individual ematch modules, `struct tcf_proto` for net namespace access, and `CONFIG_NET_EMATCH_STACK` for expression evaluation depth. Classifiers such as basic/cgroup users can attach ematch trees through `tcf_em_tree_validate()` and evaluate them through the wrapper around `__tcf_em_tree_match()`.

## Risks and Edge Cases

Module reference ownership is delicate: after `tcf_em_lookup()` succeeds, validation must not drop the reference except through destroy. Container references must remain forward-only or expressions can loop. Attribute numbering and `nmatches` mismatch are rejected because evaluation trusts array indexes. Stack depth is bounded by `CONFIG_NET_EMATCH_STACK`; too much nesting returns `-1`. This local source contains an apparent duplicated `if (data_len < sizeof(u32))` line in simple-data validation, which is a compile/review risk.

## Test Signals

Test registration duplicate rejection, unknown-kind autoload/retry, malformed tree headers/lists, sequential attribute numbering, forward and invalid container references, simple and non-simple data ownership, dump round trips, inversion, AND/OR/END expression behavior, and stack-overflow handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/ematch.c -->
