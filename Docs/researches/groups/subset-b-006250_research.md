# Research: subset-b-006250

Grouped research for `subset-b-006250`. Each section preserves the source path in its title and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_core.c

## Purpose
`nf_tables_core.c` is the nftables packet interpreter and core expression/object bootstrap for the Ceph-client Linux source mirror. It executes a packet through a prepared `struct nft_chain` rule blob, dispatches expression evaluators, handles nftables verdicts, emits trace notifications, updates base-chain counters, and registers the built-in expression/object types needed by nftables rules.

## Important APIs, Types, and Functions
The exported hot-path API is `nft_do_chain(struct nft_pktinfo *pkt, void *priv)`. It consumes `struct nft_pktinfo`, `struct nft_chain`, `struct nft_rule_blob`, `struct nft_rule_dp`, `struct nft_expr`, `struct nft_regs`, `struct nft_verdict`, `struct nft_traceinfo`, and the local `struct nft_jumpstack`.

Fast inlined evaluators are `nft_bitwise_fast_eval()`, `nft_cmp_fast_eval()`, `nft_cmp16_fast_eval()`, and `nft_payload_fast_eval()`. Generic expression dispatch goes through `expr_call_ops_eval()`, with retpoline mitigation support via `nf_tables_skip_direct_calls` and known direct-call comparisons for common expression evaluators. Tracing helpers are `nft_trace_packet()`, `nft_trace_copy_nftrace()`, `nft_trace_verdict()`, and `__nft_trace_verdict()`. Counter handling is guarded by `nft_counters_enabled` and implemented in `nft_update_chain_stats()`.

Initialization APIs are `nf_tables_core_module_init()` and `nf_tables_core_module_exit()`, which register and unregister the built-in expression types and stateful object types.

## Control Flow, State, and Persistence
`nft_do_chain()` selects either `chain->blob_gen_0` or `chain->blob_gen_1` using the per-net generation cursor, then walks rule data until the sentinel `is_last` rule. For each rule it resets `regs.verdict.code` to `NFT_CONTINUE`, evaluates expressions in rule order, and stops evaluation when an expression changes the verdict. `NFT_BREAK` means the rule did not match and scanning continues at the next rule; `NFT_CONTINUE` traces the matching rule and continues. Terminal netfilter verdicts return immediately, with `NF_DROP` translated to a drop reason.

`NFT_JUMP` stores the next rule on the bounded jump stack and falls through to `NFT_GOTO`; `NFT_GOTO` switches to the verdict chain and restarts at that chain's selected blob. `NFT_RETURN` or end-of-chain unwinds the jump stack. If no jump remains, the base-chain policy is traced, base-chain stats are optionally updated, and the policy is returned with drop reason wrapping for drop policies.

State is mostly per-packet stack state plus RCU-protected chain blobs. Persistent state includes registered expression/object types, static keys for tracing/counters/retpoline behavior, per-chain percpu stats, and per-net generation-selected rule blobs.

## Dependencies and Integration Points
The interpreter depends on nftables core headers, `nf_tables_trace.c` for `nft_trace_notify()`/`nft_trace_init()`, expression implementations such as payload, cmp, counter, meta, lookup, byteorder, bitwise, dynset, rt, object reference, and conntrack fast get, and the netfilter hook wrappers in the chain type files. Base-chain counter state is updated through `struct nft_base_chain`.

## Risks and Test Signals
Main risks are rule-blob RCU lifetime, expression size iteration, register aliasing, bounded jump-stack overflow, policy/drop reason correctness, and fast-path evaluators staying behaviorally identical to generic ops. Useful tests exercise nested jump/goto/return, `NFT_BREAK` matching, generation switching during rule replacement, trace messages for rule/return/policy paths, counters under load, retpoline direct-call toggling, payload fast failures on fragments or short skbs, and all built-in type registration rollback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_offload.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_offload.c

## Purpose
`nf_tables_offload.c` translates eligible nftables netdev ingress chains and rules into flow classifier offload operations for NIC or indirect block drivers. It constructs `struct nft_flow_rule` objects from nft expression offload callbacks, binds nftables base chains to tc flow blocks, commits or aborts hardware rule changes during nft transactions, collects rule stats, and unbinds offload state when devices disappear.

## Important APIs, Types, and Functions
Public helpers include `nft_flow_rule_create()`, `nft_flow_rule_destroy()`, `nft_flow_rule_set_addr_type()`, `nft_offload_set_dependency()`, `nft_offload_update_dependency()`, `nft_chain_offload_support()`, `nft_flow_rule_stats()`, `nft_flow_rule_offload_commit()`, `nft_offload_init()`, and `nft_offload_exit()`.

Key internal flows use `struct nft_offload_ctx`, `struct nft_flow_rule`, `struct flow_rule`, `struct flow_cls_offload`, `struct flow_block_offload`, and `struct nft_base_chain::flow_block`. Chain binding is implemented by `nft_block_offload_cmd()`, `nft_indr_block_offload_cmd()`, `nft_chain_offload_cmd()`, `nft_flow_block_chain()`, and `nft_flow_offload_chain()`.

## Control Flow, State, and Persistence
`nft_flow_rule_create()` first counts expressions that produce flow actions, allocates a `flow_rule` with that action count, initializes an offload context, and calls every expression's `ops->offload()` callback. Any expression without offload support rejects the whole rule. VLAN dissector normalization in `nft_flow_rule_transfer_vlan()` rewrites basic/vlan/cvlan key placement so tc flower receives the expected protocol layout.

Chain support is intentionally narrow: hardware offload only accepts base chains with priority in the supported range and hook ops for `NFPROTO_NETDEV` ingress on devices that either expose `ndo_setup_tc` or have an indirect flow block provider. Bind/unbind creates a `flow_block_offload`, calls device or indirect setup, splices callbacks into the base chain, and on unbind sends `FLOW_CLS_DESTROY` for existing rules before freeing callback entries.

Transaction commit scans `nft_net->commit_list` for netdev-family offloaded chain/rule operations. New chains bind blocks, deleted chains unbind, appended new rules issue `FLOW_CLS_REPLACE`, and deleted rules issue `FLOW_CLS_DESTROY`; unsupported replace/non-append rule operations fail. On failure, `nft_flow_rule_offload_abort()` walks already-processed transactions in reverse and restores offload state. Persistent state is the base-chain flow block callback list, driver block callbacks, offloaded rule cookies, action device references, and netdevice notifier registration.

## Dependencies and Integration Points
This file integrates nftables transaction state with tc flower (`TC_SETUP_CLSFLOWER`), tc block setup (`TC_SETUP_BLOCK`), `flow_indr_dev_setup_offload()`, netdevice notifier events, and expression offload callbacks from payload/cmp/bitwise/meta/immediate-style expressions. It serializes indirect device cleanup under the nftables per-net `commit_mutex`.

## Risks and Test Signals
Risks include partial bind rollback across multiple hook devices, direct versus indirect block cleanup lifetime, offloaded redirect/mirred device reference release, transaction abort symmetry, VLAN key translation, and unsupported policy/rule replacement semantics. Tests should cover successful and failing multi-device binds, netdev unregister unbind, indirect block cleanup, append-only rule offload enforcement, stats retrieval, expression offload dependency propagation, and rollback when a later transaction in the commit list fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_trace.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_tables_trace.c

## Purpose
`nf_tables_trace.c` emits nftables trace events to userspace over nfnetlink. It packages rule, verdict, packet header, device, mark, conntrack, base-chain policy, and trace-id metadata into `NFT_MSG_TRACE` multicast messages when tracing is enabled and listeners exist.

## Important APIs, Types, and Functions
The file defines and exports `DEFINE_STATIC_KEY_FALSE(nft_trace_enabled)`. The main exported functions are `nft_trace_notify()` and `nft_trace_init()`. Message construction is split across `trace_fill_header()`, `nf_trace_fill_ll_header()`, `nf_trace_fill_dev_info()`, `nf_trace_fill_ct_info()`, `nf_trace_fill_pkt_info()`, `nf_trace_fill_rule_info()`, `nft_trace_have_verdict_chain()`, and `nft_trace_get_chain()`.

It relies on `struct nft_traceinfo`, `struct nft_pktinfo`, `struct nft_verdict`, `struct nft_rule_dp`, `struct nft_chain`, conntrack hooks, and nfnetlink trace attributes.

## Control Flow, State, and Persistence
`nft_trace_init()` is called from the interpreter for packets that may be traced. It records the base chain, copies `skb->nf_trace`, resets the packet-dumped flag, and generates a stable per-packet trace id using a once-random siphash key, skb pointer hash, skb flow hash, and input ifindex.

`nft_trace_notify()` first checks `NFNLGRP_NFTRACE` listeners. It resolves the effective chain from either the current rule's trailing `nft_rule_dp_last` metadata or the base chain, sizes a netlink skb for the worst-case trace payload, and emits table/chain/protocol/type/id fields. For rule and return events it dumps the verdict and optional target chain name; for policy events it dumps the base policy. Packet/device/conntrack details are included only once per `nft_traceinfo` unless the packet was stolen, avoiding repeated large header dumps for the same traced packet.

State is transient per packet except for the trace static key and siphash key. Packet header extraction is bounded: link-layer, network, and transport header samples are capped by fixed trace sizes.

## Dependencies and Integration Points
The interpreter in `nf_tables_core.c` invokes this file. Userspace integration is through `nfnetlink_has_listeners()` and `nfnetlink_send()` on `NFNLGRP_NFTRACE`. Conntrack state is optional through `nf_ct_hook`/`nf_ct_get()`. Header copying depends on skb mac/network/transport offsets, VLAN metadata, and nft packet parsing state.

## Risks and Test Signals
Risks include skb offset assumptions for negative mac offsets, packet-dump suppression after stolen verdicts, rule pointer invalidity on implicit return, conntrack hook races, netlink size underestimation, and exposing inconsistent chain names during concurrent rule replacement. Tests should cover rule, jump/goto, return, stolen, queue, drop, and policy traces; VLAN and non-VLAN link headers; IPv4/IPv6 packets with and without L4 parsing; conntracked, untracked, and invalid packets; no-listener fast return; and malformed/short skb header copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_tables_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink.c

## Purpose
`nfnetlink.c` is the NETLINK_NETFILTER core. It owns the per-net netlink socket, subsystem registry, per-subsystem mutexes, multicast helper APIs, message dispatch, and atomic batch commit/abort machinery used by nftables, conntrack, queue, log, acct, osf, cthelper, cttimeout, and hook listing subsystems.

## Important APIs, Types, and Functions
Subsystem APIs are `nfnetlink_subsys_register()`, `nfnetlink_subsys_unregister()`, `nfnl_lock()`, `nfnl_unlock()`, and `lockdep_nfnl_is_held()`. Send-side APIs are `nfnetlink_has_listeners()`, `nfnetlink_send()`, `nfnetlink_set_err()`, `nfnetlink_unicast()`, and `nfnetlink_broadcast()`.

Receive logic is `nfnetlink_rcv()`, `nfnetlink_rcv_msg()`, `nfnetlink_rcv_skb_batch()`, and `nfnetlink_rcv_batch()`. The registry is `table[NFNL_SUBSYS_COUNT]`, mapping subsystem ids to `struct nfnetlink_subsystem` under RCU and a per-subsystem mutex. Batch error tracking uses `struct nfnl_err`.

## Control Flow, State, and Persistence
Normal receive first validates message framing and `CAP_NET_ADMIN`. `nfnetlink_rcv_msg()` verifies the `nfgenmsg` header, loads a subsystem by module autoload if needed, finds the message callback, parses attributes into a bounded stack array capped by `NFNL_MAX_ATTR_COUNT`, and then dispatches by callback type: RCU callbacks run under `rcu_read_lock()`, mutex callbacks validate that the subsystem/callback did not change after acquiring `nfnl_lock()`.

Batch receive starts at `NFNL_MSG_BATCH_BEGIN`, parses an optional generation id, clones the skb, locks the subsystem long enough to validate it supports `valid_genid`, `commit`, and `abort`, then processes only `NFNL_CB_BATCH` messages for that subsystem. It accumulates ack/error reports without stopping on ordinary per-message failures. Successful batches call subsystem `commit`; malformed or failed batches call `abort` with validation or failure action. `-EAGAIN` can replay the entire batch after module autoload or generation changes.

Persistent state includes one `struct sock *nfnl` per net namespace, per-subsystem registered callbacks under RCU, per-subsystem lock classes, and optional conntrack-listener bit state for event fast paths.

## Dependencies and Integration Points
This file integrates kernel netlink core, module autoload (`nfnetlink-subsys-%d`), network namespaces, netfilter subsystem ids/message types, and conntrack event listener state. Every assigned nfnetlink module registers a `struct nfnetlink_subsystem` here.

## Risks and Test Signals
Risks include attr-count stack overflow prevention, callback replacement races across RCU/mutex transitions, batch replay correctness, module refcounting during batch processing, error-list memory pressure, generation-id validation, capability enforcement, and listener bitmap accuracy. Tests should cover unknown subsystem autoload, invalid attr counts, mutex versus RCU callbacks, mixed-subsystem batches, batch begin/end malformed cases, commit and abort replay, per-message ack ordering, per-net socket teardown, and group bind/unbind side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_acct.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_acct.c

## Purpose
`nfnetlink_acct.c` implements the nfnetlink accounting subsystem. It lets userspace create named packet/byte counters with optional packet or byte quotas, retrieve and optionally zero counters, delete counters, and receive overquota multicast events. Other netfilter modules can hold references to accounting objects and update them per packet.

## Important APIs, Types, and Functions
The main object is `struct nf_acct`, containing atomic packet/byte counters, flags, name, refcount, RCU list node, and optional quota data. Per-net state is `struct nfnl_acct_net`.

nfnetlink callbacks are `nfnl_acct_new()`, `nfnl_acct_get()`, `nfnl_acct_del()`, dump helpers `nfnl_acct_dump()`, `nfnl_acct_start()`, `nfnl_acct_done()`, and formatter `nfnl_acct_fill_info()`. Exported module APIs are `nfnl_acct_find_get()`, `nfnl_acct_put()`, `nfnl_acct_update()`, and `nfnl_acct_overquota()`.

## Control Flow, State, and Persistence
Creation requires a non-empty `NFACCT_NAME`. Existing names honor `NLM_F_EXCL`; replace resets counters and clears overquota if quota is enabled. New objects validate quota flags so only packet or byte quota is selected, store optional initial counter values, set refcount to one, and append to the per-net RCU list.

Get either starts a dump with optional flag mask/value filtering or sends one named object. `NFNL_MSG_ACCT_GET_CTRZERO` atomically exchanges counters with zero and clears overquota state after reporting old values. Delete without a name attempts to delete every object; named delete removes one object only when `refcount_dec_if_one()` proves no external user holds it.

Runtime users call `nfnl_acct_find_get()` under RCU, which also pins the module, then `nfnl_acct_update()` to increment atomic counters. `nfnl_acct_overquota()` compares the selected counter with the stored quota, sets the overquota bit once, and multicasts an overquota report on `NFNLGRP_ACCT_QUOTA`.

## Dependencies and Integration Points
The subsystem registers under `NFNL_SUBSYS_ACCT`, uses per-net generic storage, RCU lists, atomic64 counters, refcounts, and nfnetlink multicast/unicast helpers. Consumers are nftables/xt accounting integrations that resolve named counters and call the exported update/quota APIs.

## Risks and Test Signals
Risks include quota flag validation, refcount deletion races, counter zeroing memory ordering, RCU traversal during namespace exit, overquota event suppression after the first event, and module refcount balance. Tests should cover create/replace/exclusive behavior, byte and packet quotas, counter dump with filtering, get-and-zero semantics, delete while referenced, namespace teardown with live references, and overquota multicast listener behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cthelper.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cthelper.c

## Purpose
`nfnetlink_cthelper.c` lets userspace define conntrack helpers that queue helper processing to nfqueue instead of doing protocol-specific assistance entirely in kernel space. It creates, updates, dumps, and deletes `NF_CT_HELPER_F_USERSPACE` helpers with tuple selectors, expectation policies, private data length, queue number, and enabled/disabled status.

## Important APIs, Types, and Functions
The wrapper type is `struct nfnl_cthelper`, embedding `struct nf_conntrack_helper`. The helper callback is `nfnl_userspace_cthelper()`, which returns `NF_QUEUE_NR(queue_num) | NF_VERDICT_FLAG_QUEUE_BYPASS` once configured.

Parser/formatter helpers include `nfnl_cthelper_parse_tuple()`, `nfnl_cthelper_parse_expect_policy()`, `nfnl_cthelper_expect_policy()`, `nfnl_cthelper_from_nlattr()`, `nfnl_cthelper_to_nlattr()`, `nfnl_cthelper_dump_tuple()`, `nfnl_cthelper_dump_policy()`, and `nfnl_cthelper_fill_info()`. CRUD callbacks are `nfnl_cthelper_new()`, `nfnl_cthelper_get()`, and `nfnl_cthelper_del()`.

## Control Flow, State, and Persistence
New/update requires `CAP_NET_ADMIN`, name, and tuple. A tuple specifies L3 protocol and L4 protocol. If a matching userspace helper exists, `NLM_F_EXCL` fails and otherwise update paths can change policy timeouts/counts, queue number, and configured status; private data length and policy class count are immutable. If no helper exists, creation parses expectation policy classes, validates private data length against `struct nf_conn_help::data`, initializes helper callbacks and flags, registers with conntrack helper core, and links the wrapper into a global list.

During packet processing, unconfigured userspace helpers accept traffic without queuing; configured helpers queue to the selected nfqueue with bypass so traffic is not blocked if userspace is absent. Per-connection helper private data can be serialized/deserialized through CTA_HELP_INFO when the conntrack netlink hook invokes the helper callbacks.

Delete can filter by name and/or tuple. It only unregisters and frees a helper if `refcount_dec_if_one()` succeeds; otherwise it reports busy. Module exit unregisters the nfnetlink subsystem, unregisters all remaining helpers, frees expectation policies, and frees wrappers.

## Dependencies and Integration Points
This file integrates nfnetlink subsystem `NFNL_SUBSYS_CTHELPER`, conntrack helper registration, expectation policy limits, conntrack netlink serialization, and nfqueue. It depends on `nf_conntrack_helper_register()`, `nf_conntrack_helper_unregister()`, `nfct_help()`, and helper hash dumping.

## Risks and Test Signals
Risks include policy update bugs across multiple classes, helper refcount/lifetime interactions with active conntracks, queue bypass semantics, private data length validation, global-list concurrency under nfnetlink mutex, and status transitions that unexpectedly stop or start queueing. Tests should create/update/delete helpers, dump only userspace helpers, reject malformed tuples/policies, verify queue number and enabled status changes, exercise busy delete with active references, and validate CTA_HELP_INFO round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cthelper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cttimeout.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cttimeout.c

## Purpose
`nfnetlink_cttimeout.c` provides userspace-managed conntrack timeout policies. It supports named timeout objects attached to conntracks, replacement of timeout data for the same protocol kind, deletion with reference checks, dump/get operations, and getting or setting per-net default protocol timeouts through each L4 protocol's timeout serializer.

## Important APIs, Types, and Functions
Named objects are `struct ctnl_timeout`, embedding `struct nf_ct_timeout` after list/refcount/name metadata. Per-net storage is `struct nfct_timeout_pernet`. Parser/formatter functions are `ctnl_timeout_parse_policy()`, `ctnl_timeout_fill_info()`, `cttimeout_default_fill_info()`, and protocol default access in `cttimeout_default_get()`.

nfnetlink callbacks are `cttimeout_new_timeout()`, `cttimeout_get_timeout()`, `cttimeout_del_timeout()`, `cttimeout_default_set()`, and `cttimeout_default_get()`. Integration with conntrack core is via `struct nf_ct_timeout_hooks hooks`, `ctnl_timeout_find_get()`, `ctnl_timeout_put()`, and the global RCU pointer `nf_ct_timeout_hook`.

## Control Flow, State, and Persistence
Creation requires name, L3 protocol, L4 protocol, and nested timeout data. Existing names can be replaced only when L3 and L4 protocol kind match; replacement re-parses into the existing timeout data. New objects find the L4 protocol, allocate storage sized by `l4proto->ctnl_timeout.obj_size`, parse protocol-specific attributes via `nlattr_to_obj`, initialize `nf_ct_timeout`, set refcount, pin the module, and append to the per-net RCU list.

Get supports dumps with RCU cursor continuation or named unicast. Delete without name tries all objects; named delete calls `ctnl_timeout_try_del()`, which only removes unreferenced objects, calls `nf_ct_untimeout()` to detach the policy from conntracks, and frees through RCU. Default set passes `NULL` as the destination object to the L4 parser, relying on protocol code to update per-net defaults. Default get selects protocol-specific per-net timeout arrays for ICMP, TCP, UDP, ICMPv6, SCTP, GRE, and generic protocol 255.

Namespace teardown first moves live objects to a freelist in `pre_exit` before the core synchronize-RCU point, then detaches all conntracks and frees unreferenced objects in `exit`. Module exit unregisters hooks and clears timeout pointers from existing conntracks through `nf_ct_iterate_destroy()`.

## Dependencies and Integration Points
The file depends on conntrack core, L4 protocol timeout descriptors, per-net protocol timeout storage, nfnetlink, RCU, and refcounts. It is consumed by conntrack extensions that resolve named timeout policies through `nf_ct_timeout_hook`.

## Risks and Test Signals
Risks include protocol-specific parser misuse for default updates, L4 protocol support checks, refcount/module refcount balance, namespace exit ordering, stale timeout pointers on module unload, and delete races with conntrack attachment. Tests should cover create/replace kind mismatch, malformed protocol data, named and dump get, busy delete, default get/set for every enabled protocol, namespace teardown with attached policies, and module unload clearing conntrack timeout extensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cttimeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_hook.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_hook.c

## Purpose
`nfnetlink_hook.c` exposes registered netfilter hooks to userspace through an nfnetlink dump-only subsystem. It reports hook function names, module names, hook number, priority, and optional typed descriptions for nftables chains, nft flowtables, and BPF netfilter links.

## Important APIs, Types, and Functions
The subsystem callback is `nfnl_hook_get()`, which only supports `NLM_F_DUMP`. Dump setup, iteration, and cleanup are `nfnl_hook_dump_start()`, `nfnl_hook_dump()`, and `nfnl_hook_dump_stop()`. Hook-array lookup is `nfnl_hook_entries_head()`. Message creation is `nfnl_hook_dump_one()`, with typed nested helpers `nfnl_hook_put_bpf_prog_info()`, `nfnl_hook_put_nft_chain_info()`, and `nfnl_hook_put_nft_ft_info()`.

`struct nfnl_dump_hook_data` stores the target netdev name, initial hook-head pointer value for consistency checks, and hook number.

## Control Flow, State, and Persistence
The user must provide a hook number; `NFPROTO_NETDEV` additionally requires a device name. Start validates hook range and resolves the current hook entries pointer under RCU. The pointer is stored only as a consistency token. Dump re-resolves hook entries each iteration, bumps the netlink dump sequence if the head pointer changed or the cursor is beyond the current entry count, retrieves `nf_hook_ops` pointers, and emits one netlink message per hook operation.

For each hook op, KALLSYMS support formats `%ps` into function and optional module names. `NFPROTO_INET` ingress is reported as netdev ingress for hook-number compatibility. For nftables hooks, only active chains/flowtables are described, including table name, object name, and family. BPF link information includes the BPF program id when configured.

Persistent state is limited to subsystem registration. Dump allocations are temporary and freed in `done`.

## Dependencies and Integration Points
This file reads netfilter hook arrays for IPv4, IPv6, ARP, bridge, and netdev ingress/egress families; nftables active-state helpers; optional BPF netfilter link support; KALLSYMS; and netdevice lookup under RCU. It uses `NFNL_CB_RCU` and a helper that temporarily drops/reacquires RCU around `netlink_dump_start()`.

## Risks and Test Signals
Risks include inconsistent dumps while hooks are registered/unregistered, netdev rename/removal races, optional-family build coverage, missing KALLSYMS output, and active-state filtering of nftables objects during transactions. Tests should dump every supported family/hook, require device for netdev family, verify function/module name attributes when KALLSYMS is enabled, inspect nft chain/flowtable descriptors, handle hook-array mutation during dump, and reject unsupported non-dump get requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_hook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_log.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_log.c

## Purpose
`nfnetlink_log.c` implements the NFLOG userspace logging backend. It binds per-net logging instances to netlink port ids and groups, accepts configuration for copy mode/range, buffer size, flush timeout, queue threshold, and metadata flags, then batches logged packet metadata and optional payload into nfnetlink unicast messages.

## Important APIs, Types, and Functions
The central state object is `struct nfulnl_instance`, stored in per-net `struct nfnl_log_net::instance_table`. It tracks peer port/user namespace, current batching skb, queue length, timer, copy mode/range, sequence flags, and group number.

Packet logging is `nfulnl_log_packet()` through `struct nf_logger nfulnl_logger`. Message construction is `__build_packet_message()`, with allocation/sending via `nfulnl_alloc_skb()`, `__nfulnl_send()`, and `__nfulnl_flush()`. Instance lifecycle uses `instance_create()`, `instance_lookup_get()`, `instance_destroy()`, `__instance_destroy()`, `instance_put()`, and timer callback `nfulnl_timer()`. Configuration is `nfulnl_recv_config()`.

## Control Flow, State, and Persistence
Userspace binds an instance for a group with `NFULNL_CFG_CMD_BIND`; the creating port id owns subsequent configuration and receives logs. Per-protocol-family bind/unbind commands register or unregister the NFLOG logger for that family. On log events, `nfulnl_log_packet()` resolves the group instance under RCU, computes the netlink message size for requested metadata, applies per-rule qthreshold overrides, and locks the instance.

Copy mode controls payload inclusion: none/meta omit payload, packet copies up to instance range and optional per-rule copy length. Optional flags add local and global sequence numbers and conntrack metadata. Bridge/netdev packets can include VLAN and L2 headers. Socket credentials are translated into the peer user namespace. If the current batching skb lacks tailroom, the instance flushes before appending. Flush occurs when qthreshold is reached or when the timer fires.

Persistent state is per-net group instances, per-instance timers and batched skbs, global sequence atomic counter, procfs status rows, netlink-notifier cleanup on peer release, and nf_logger registration.

## Dependencies and Integration Points
The file integrates nfnetlink subsystem `NFNL_SUBSYS_ULOG`, nf_log core registration, optional bridge netfilter metadata, optional conntrack netlink building via `nfnl_ct_hook`, procfs per-net diagnostics, netlink notifier release events, timers, RCU, spinlocks, netns references, and user namespace credential munging.

## Risks and Test Signals
Risks include batching skb size underestimation, timer/reference lifetime, owner port enforcement, netlink peer release cleanup, copy-range limits from 16-bit nla length, optional conntrack module autoload atomicity, bridge physical/logical ifindex mapping, and credential namespace conversion. Tests should cover bind/unbind, PF logger bind/unbind, all copy modes, qthreshold and timer flush, sequence flags, conntrack flag with and without hook loaded, bridge/VLAN metadata, procfs output, peer socket close destroying instances, and net namespace exit without leaked instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_osf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_osf.c

## Purpose
`nfnetlink_osf.c` implements passive operating-system fingerprint storage and matching for IPv4 TCP SYN packets. Userspace loads and removes fingerprints through nfnetlink; xtables/nft users can match packets against the RCU-protected fingerprint lists and optionally log detected genres.

## Important APIs, Types, and Functions
The exported global database is `nf_osf_fingers[2]`, indexed by the IPv4 don't-fragment bit. Exported match APIs are `nf_osf_match()` and `nf_osf_find()`. Header parsing is centralized in `nf_osf_hdr_ctx_init()` and per-fingerprint comparison in `nf_osf_match_one()`. nfnetlink callbacks are `nfnl_osf_add_callback()` and `nfnl_osf_remove_callback()`.

Important structures include `struct nf_osf_finger`, `struct nf_osf_user_finger`, `struct nf_osf_info`, `struct nf_osf_data`, and local `struct nf_osf_hdr_ctx`.

## Control Flow, State, and Persistence
Matching first reads IPv4 and TCP headers using `skb_header_pointer()`, accepts only SYN packets, captures total length, DF bit, TCP window, and TCP option bytes. `nf_osf_match_one()` requires packet total length and TTL policy to match, validates fingerprint option size against packet option size, walks expected options in order, extracts MSS when present, and validates window size as plain, MSS multiple, MTU multiple, or modulo.

`nf_osf_match()` filters by requested genre unless logging all matches, logs matches or unknown OS messages through `nf_log_packet()`, and returns true when at least one fingerprint matches. `nf_osf_find()` returns the first matching genre/version pair.

Fingerprint add requires `CAP_NET_ADMIN`, `NLM_F_CREATE`, an exact-size fingerprint attribute, bounded option count/lengths, valid WSS mode, NUL-terminated strings, and duplicate detection. New fingerprints are appended to the DF-indexed RCU list under the nfnetlink mutex. Remove finds an exact fingerprint and deletes it with RCU freeing. Module exit unregisters the subsystem and RCU-frees all fingerprints.

## Dependencies and Integration Points
The file integrates nfnetlink subsystem `NFNL_SUBSYS_OSF`, IPv4/TCP header helpers, netfilter logging, and external match expressions/modules that call the exported OSF APIs under RCU. It is IPv4/TCP-specific and does not parse IPv6 fingerprints.

## Risks and Test Signals
Risks include option parser assumptions, MSS endian handling, duplicate exact-match semantics, RCU deletion during matching, TTL policy edge cases, and logging volume. Tests should add/remove fingerprints, reject malformed option strings and non-terminated genres, match DF/non-DF lists, exercise all WSS modes, verify TTL true/less/nocheck behavior, confirm only SYN packets match, validate unknown logging, and run concurrent match with fingerprint removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_osf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_queue.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_queue.c

## Purpose
`nfnetlink_queue.c` implements NFQUEUE, the userspace verdict path for netfilter packets. It creates per-net queue instances owned by netlink sockets, serializes queued packet metadata/payload to userspace, receives verdicts and optional packet modifications, reinjects packets into the hook pipeline, and flushes queued packets when devices, hooks, namespaces, or userspace sockets disappear.

## Important APIs, Types, and Functions
The central state is `struct nfqnl_instance`, with a queue list, packet-id sequence, rhashtable mapping ids to `struct nf_queue_entry`, peer port id, max length, copy mode/range, flags, and drop counters. It is stored in per-net `struct nfnl_queue_net`.

Queue integration is through `struct nf_queue_handler nfqh` and `nfqnl_enqueue_packet()`. Message building is `nfqnl_build_packet_message()`. Reinjection uses `nfqnl_reinject()` and `nf_reinject()`. Verdict callbacks are `nfqnl_recv_verdict()` and `nfqnl_recv_verdict_batch()`. Configuration is `nfqnl_recv_config()`. Lifecycle and cleanup use `instance_create()`, `instance_destroy()`, `instance_destroy_work()`, `nfqnl_flush()`, device and netlink notifiers, and per-net procfs sequence operations.

## Control Flow, State, and Persistence
Userspace binds a queue with `NFQNL_CFG_CMD_BIND`, then sets copy mode, copy range, max length, and flags such as fail-open, conntrack, GSO, UID/GID, and secctx. When a rule queues a packet, `nfqnl_enqueue_packet()` finds the queue under RCU, rejects copy-none queues, normalizes skb protocol for IPv4/IPv6, rejects unsafe unconfirmed conntrack sharing, and either enqueues the skb or segments GSO packets unless GSO passthrough is enabled.

`nfqnl_build_packet_message()` sizes and fills an nfnetlink packet message with packet id pointer, hook, ifindexes, mark, priority, hardware header, bridge/VLAN metadata, timestamp, UID/GID, cgroup classid, secctx, conntrack attributes, captured length, checksum/GSO flags, and optional zerocopy payload. `__nfqnl_enqueue_packet()` assigns an id, inserts the entry into the rhashtable before unicast, and handles full queues or unicast failure by dropping or fail-opening.

Verdicts are accepted only from the owning port id. Single verdict lookup dequeues by id, optionally parses conntrack/expectation data, applies bridge VLAN/L2 edits, mangles payload length/content, updates mark/priority, then reinjects. Batch verdict dequeues every queued id up to a max id and applies the same verdict/mark/priority. Reinjection updates conntrack first, re-routes local-output packets if address/mark changed, resumes hook iteration after the original hook, and finally calls `okfn`, queues again, steals, or frees.

Persistent state includes queue instances, queued entries and id map, rcu-work destruction, ordered cleanup workqueue, procfs diagnostics, registered queue handler, netdevice notifier for flushing downed-device packets, netlink notifier for peer close, and per-net instance hash buckets.

## Dependencies and Integration Points
The file integrates nf_queue core, nfnetlink subsystem `NFNL_SUBSYS_QUEUE`, IPv4/IPv6 rerouting, bridge netfilter metadata, GSO segmentation, conntrack update and netlink build/parse hooks, LSM secctx, cgroup classid, netdevice and netlink notifiers, rhashtable, procfs, and per-net namespace lifecycle.

## Risks and Test Signals
Risks include queue id wrap/batch ordering, rhashtable/list consistency, fail-open semantics, userspace port ownership, packet mangle length validation, checksum/GSO handling, unconfirmed conntrack parallelism, reinjection hook index correctness, local-output reroute after modifications, and cleanup ordering with RCU work. Tests should bind/configure/unbind queues, enqueue under every copy mode, hit maxlen and unicast failure with/without fail-open, send single and batch verdicts, modify payload/mark/priority/VLAN/L2 headers, exercise GSO segmentation, conntrack metadata round-trip, device-down flush, peer close destruction, procfs counters, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_bitwise.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_bitwise.c

## Purpose
`nft_bitwise.c` implements the nftables `bitwise` expression. It transforms register data with mask/xor, left shift, right shift, and boolean AND/OR/XOR operations using either immediate data or a second source register. It also provides a compact one-word fast op and limited hardware-offload support for masks.

## Important APIs, Types, and Functions
The full expression state is `struct nft_bitwise`; the fast state is `struct nft_bitwise_fast_expr` from nftables core headers. Evaluation entry points are `nft_bitwise_eval()` and the inlined fast evaluator in `nf_tables_core.c`. Full-op helpers include `nft_bitwise_eval_mask_xor()`, `nft_bitwise_eval_lshift()`, `nft_bitwise_eval_rshift()`, `nft_bitwise_eval_and()`, `nft_bitwise_eval_or()`, and `nft_bitwise_eval_xor()`.

Initialization/dump paths are `nft_bitwise_init()`, `nft_bitwise_init_mask_xor()`, `nft_bitwise_init_shift()`, `nft_bitwise_init_bool()`, `nft_bitwise_dump()`, and fast variants. Operation selection is `nft_bitwise_select_ops()`.

## Control Flow, State, and Persistence
Select ops requires source, destination, and length. A four-byte mask/xor expression selects the fast op; other lengths or non-mask/xor ops use the full op. Initialization parses register load/store constraints and validates per-op attribute combinations: mask/xor requires mask and xor with no data or second source; shifts require immediate u32 shift between 1 and 31; boolean ops require exactly one immediate data operand or second source register.

Evaluation reads from the source register and writes to destination for `len` bytes rounded to u32 words. Shift operations propagate carry across u32 words. Boolean register operations use `sreg2` when provided; otherwise they use parsed immediate data. Offload is supported only for mask-only operations where xor is zero, source and destination are identical, and length matches the tracked offload register.

State persists only in expression private data inside nft rules. Parsed `nft_data` values are dumped back through netlink; mask/xor data are released on partial initialization errors.

## Dependencies and Integration Points
This file depends on nft register parsing, nft data parser/dumper, the core interpreter's inlined fast evaluator, and flow offload context register masks. It is registered as expression type `bitwise` by the nftables core module.

## Risks and Test Signals
Risks include shift carry behavior across partial lengths, endian expectations for u32-word operations, invalid attribute combinations, register overlap, missing data release on errors, and offload accepting only true masks. Tests should cover every op, immediate versus second-register boolean ops, one-byte/unaligned lengths, zero/32-bit shift rejection, fast-op selection and dump equivalence, invalid netlink attributes, and offload mask propagation/rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_bitwise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_byteorder.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_byteorder.c

## Purpose
`nft_byteorder.c` implements the nftables `byteorder` expression, converting register data between network byte order and host byte order for arrays of 16-bit, 32-bit, or 64-bit values.

## Important APIs, Types, and Functions
Private state is `struct nft_byteorder`, containing source/destination registers, operation (`NFT_BYTEORDER_NTOH` or `NFT_BYTEORDER_HTON`), total byte length, and element size. The evaluator is `nft_byteorder_eval()`. Netlink setup and dump are `nft_byteorder_init()` and `nft_byteorder_dump()`. Registration is through `struct nft_expr_type nft_byteorder_type`.

## Control Flow, State, and Persistence
Initialization requires all attributes: source register, destination register, operation, length, and element size. It accepts only NTOH/HTON operations and element sizes of 2, 4, or 8 bytes. Register validation uses `nft_parse_register_load()` and `nft_parse_register_store()` for the full requested length.

Evaluation casts the selected register window to u16/u32/u64 views depending on element size. For 64-bit elements it uses `nft_reg_load64()` and `nft_reg_store64()` so nft register layout is respected. For 32-bit and 16-bit elements it loops over `len / size` elements and applies `ntohl`/`htonl` or `ntohs`/`htons`. There is no offload support in this file.

State is entirely expression-private and immutable after rule creation. Dump emits the original register ids, operation, length, and element size.

## Dependencies and Integration Points
The expression depends on nftables register parsing/dumping and Linux byteorder helpers. It is called from the generic interpreter, including direct retpoline-bypass dispatch in `nf_tables_core.c`.

## Risks and Test Signals
Risks include lengths that are not multiples of element size silently leaving tail bytes untouched, register overlap between source and destination, 64-bit register layout correctness, and invalid netlink attributes. Tests should cover 16/32/64-bit NTOH and HTON arrays, in-place conversion, non-multiple lengths if userspace can create them, invalid size/op rejection, dump round-trip, and mixed endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_byteorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_filter.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_filter.c

## Purpose
`nft_chain_filter.c` registers nftables `filter` chain types for IPv4, IPv6, ARP, inet, bridge, and netdev families. Each hook wrapper prepares `struct nft_pktinfo` for the packet family and then delegates to `nft_do_chain()`. The netdev support also tracks device register/unregister/rename events for chains bound by interface name.

## Important APIs, Types, and Functions
Top-level lifecycle APIs are `nft_chain_filter_init()` and `nft_chain_filter_fini()`. Hook wrappers include `nft_do_chain_ipv4()`, `nft_do_chain_ipv6()`, `nft_do_chain_arp()`, `nft_do_chain_inet()`, `nft_do_chain_inet_ingress()`, `nft_do_chain_bridge()`, and `nft_do_chain_netdev()`.

The registered objects are `struct nft_chain_type` instances for filter chains in each enabled family. Netdev lifecycle helpers are `nft_netdev_event()`, `__nf_tables_netdev_event()`, `nf_tables_netdev_event()`, and the `nf_tables_netdev_notifier`.

## Control Flow, State, and Persistence
Family-specific hook functions initialize packet info from the netfilter hook state, then parse or validate protocol headers. IPv4 and IPv6 use dedicated `nft_set_pktinfo_*` helpers. ARP uses unspecific packet info. Inet regular hooks switch on `state->pf`; inet ingress starts from a netdev ingress state, maps Ethernet protocol to IPv4 or IPv6, rewrites the temporary hook state to `NF_INET_INGRESS`, and accepts non-IP packets. Bridge and netdev hooks inspect the Ethernet protocol and validate IPv4/IPv6 headers when present, otherwise falling back to unspecific packet info.

Initialization registers netdev first, then IPv4, IPv6, ARP, inet, and bridge chain types. Fini unregisters in reverse order. Netdev notifier operations walk nftables tables under `commit_mutex`, find netdev-family chains and inet ingress chains, and create or remove per-device `nf_hook_ops` entries when devices matching stored interface names appear, disappear, or change name. Dormant tables skip hook register/unregister but still maintain the ops list.

Persistent state is chain type registration plus per-base-chain hook ops lists for bound devices and a netdevice notifier.

## Dependencies and Integration Points
This file connects nftables to netfilter hooks for all filter-capable families and depends on packet-info helpers from IPv4/IPv6 nft headers, bridge/netdev hook constants, netdevice notifiers, and nftables per-net table/chain lists. The wrappers call the core interpreter in `nf_tables_core.c`.

## Risks and Test Signals
Risks include ingress family remapping, short/invalid IP header validation, netdev rename matching, ops list lifetime under RCU, dormant table behavior, and registration ordering across optional config blocks. Tests should create filter chains for every enabled family/hook, process IPv4/IPv6/non-IP ingress and bridge packets, bind chains to devices before and after device registration, rename devices, unregister devices, toggle dormant tables, and verify reverse-order cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_nat.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_nat.c

## Purpose
`nft_chain_nat.c` registers nftables `nat` chain types for IPv4, IPv6, and inet families. NAT chain hooks prepare nft packet info and run `nft_do_chain()`, while chain type registration uses NAT-specific hook registration functions so nft NAT chains integrate with conntrack/NAT ordering.

## Important APIs, Types, and Functions
The hook wrapper is `nft_nat_do_chain()`. Chain type descriptors are `nft_chain_nat_ipv4`, `nft_chain_nat_ipv6`, and `nft_chain_nat_inet`, compiled by configuration. Module lifecycle is `nft_chain_nat_init()` and `nft_chain_nat_exit()`. Inet wrappers `nft_nat_inet_reg()` and `nft_nat_inet_unreg()` call `nf_nat_inet_register_fn()` and `nf_nat_inet_unregister_fn()`.

## Control Flow, State, and Persistence
`nft_nat_do_chain()` initializes generic packet info, switches on `state->pf`, and applies IPv4 or IPv6 packet-info parsing before invoking the nftables interpreter. IPv4 and IPv6 chain types support prerouting, postrouting, local-out, and local-in hooks. Inet NAT supports the same logical hooks for dual-stack tables and delegates registration to inet NAT helpers.

Module initialization registers enabled chain types; exit unregisters them. State is limited to registered chain type metadata and any hooks created by nftables core when users create NAT base chains.

## Dependencies and Integration Points
The file depends on nftables core, IPv4/IPv6 packet-info helpers, and NAT registration helpers from `nf_nat`. It is loaded through nft chain aliases for family-specific `nat` chain creation.

## Risks and Test Signals
Risks include hook-mask mismatch with NAT core expectations, IPv4/IPv6 packet-info setup before NAT expressions, inet registration symmetry, and optional-family build coverage. Tests should create NAT chains in IPv4, IPv6, and inet tables; exercise all supported hooks; verify module autoload aliases; confirm cleanup unregisters types; and test NAT rule execution on packets requiring conntrack/NAT state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_route.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_route.c

## Purpose
`nft_chain_route.c` registers nftables `route` chain types for IPv4, IPv6, and inet local-output hooks. Route chains run nftables rules and then force route recalculation if rules changed routing-relevant packet fields such as addresses, mark, TOS/flow label, or hop limit.

## Important APIs, Types, and Functions
Hook wrappers are `nf_route_table_hook4()`, `nf_route_table_hook6()`, and `nf_route_table_inet()`. Chain type descriptors are `nft_chain_route_ipv4`, `nft_chain_route_ipv6`, and `nft_chain_route_inet`. Lifecycle APIs are `nft_chain_route_init()` and `nft_chain_route_fini()`.

## Control Flow, State, and Persistence
IPv4 local-output hook setup records source address, destination address, skb mark, and TOS before running `nft_do_chain()`. If the verdict is `NF_ACCEPT` and any of those fields changed, it calls `ip_route_me_harder()` and converts route failure into `NF_DROP_ERR(err)`.

IPv6 records source and destination addresses, mark, hop limit, and the first header word containing version, traffic class, and flow label. After accepted rule evaluation, it calls `nf_ip6_route_me_harder()` if any saved field differs. The inet route hook dispatches to the IPv4 or IPv6 hook based on `state->pf`; unknown families simply run the chain with generic packet info.

Persistent state is only registered chain type metadata. Route recalculation side effects occur per packet.

## Dependencies and Integration Points
The file integrates nftables local-output route chains with IPv4/IPv6 routing helpers, nft packet-info setup, and netfilter local-out hook semantics. It relies on rule expressions that may modify packet headers or skb mark.

## Risks and Test Signals
Risks include missing a field that should trigger reroute, rerouting after packet modifications that changed header pointers, IPv6 first-word unaligned access assumptions, inet dispatch for optional family builds, and correct drop-error propagation. Tests should modify each watched field separately, leave fields unchanged, trigger route helper failure, run IPv4 and IPv6 inet route chains, and verify non-accept verdicts do not reroute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_chain_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_cmp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_cmp.c

## Purpose
`nft_cmp.c` implements the nftables `cmp` expression. It compares register data with immediate nft data using equality, inequality, and lexicographic ordering operations. It selects specialized fast expression layouts for common equality/inequality cases and provides hardware-offload translation into flow dissector key/mask matches.

## Important APIs, Types, and Functions
Full expression state is `struct nft_cmp_expr`; fast states are `struct nft_cmp_fast_expr` and `struct nft_cmp16_fast_expr`. Evaluation entry point is `nft_cmp_eval()`, while fast evaluators are inlined by `nf_tables_core.c`. Initialization/dump functions are `nft_cmp_init()`, `nft_cmp_fast_init()`, `nft_cmp16_fast_init()`, `nft_cmp_dump()`, `nft_cmp_fast_dump()`, and `nft_cmp16_fast_dump()`.

Offload helpers are `nft_payload_n2h()`, `__nft_cmp_offload()`, `nft_cmp_offload()`, `nft_cmp_fast_offload()`, and `nft_cmp16_fast_offload()`. Op selection is `nft_cmp_select_ops()`.

## Control Flow, State, and Persistence
Selection requires source register, operation, and data. It validates operation codes, parses the data once to discover length, and chooses the fast one-word op for EQ/NEQ up to u32, the 16-byte fast op for aligned eligible registers up to `struct nft_data`, or the generic op for ordering and other cases.

Generic evaluation uses `memcmp()` over `len` bytes and maps comparison result to nft semantics. Mismatches set `regs->verdict.code = NFT_BREAK`, causing the interpreter to skip the current rule. Fast initialization builds little-endian masks for partial u32 or 16-byte comparisons and records an inversion flag for NEQ. Dumps reconstruct the original netlink operation and immediate data.

Offload supports equality matches only. It locates the tracked offload register, optionally converts payload data and masks from network to host order, copies key/mask bytes into the flow rule at the recorded offset, marks the flow dissector key as used, rejects non-Ethernet ingress-iftype metadata, and updates dependency state for later payload/protocol checks.

Expression state persists in immutable rule private data. No dynamic resources are held after initialization.

## Dependencies and Integration Points
The expression depends on nft data parsing/dumping, register validation, core interpreter fast-op inlining, flow offload context register tracking, Linux flow dissector key layout, and payload/meta expressions that establish offload register offsets and masks.

## Risks and Test Signals
Risks include memcmp lexicographic ordering semantics, endian handling for partial masks, fast-op selection for aligned registers, offload accepting only equality, dependency propagation, and metadata iftype restrictions. Tests should cover all comparison operators, EQ/NEQ fast and generic paths, partial-length masks on big and little endian, 16-byte comparisons, dump round-trips, offload success after payload extraction, offload rejection for NEQ/range/unsupported metadata, and interpreter `NFT_BREAK` behavior on mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_cmp.c -->
