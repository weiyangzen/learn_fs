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
