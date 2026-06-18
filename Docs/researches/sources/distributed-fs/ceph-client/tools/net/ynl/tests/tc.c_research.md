# sources/distributed-fs/ceph-client/tools/net/ynl/tests/tc.c

Purpose: traffic-control selftest for generated `tc` bindings. It validates qdisc CRUD, flower filter creation, indexed actions, nested options, and fixed-header handling.

Important APIs/functions: printing helpers decode qdisc kind/options, fq_codel stats, VLAN/gact action names, flower attributes, and filter options. `tc_clsact_add()`/`tc_clsact_del()` manage clsact qdisc. `tc_filter_add()` builds a flower filter with VLAN keys and an indexed action array, intentionally leaving index 0 unused to match TC action ordering. `tc_filter_del()` removes it.

Control flow/state: fixture unshares a new network namespace, uses loopback ifindex 1, and opens `ynl_tc_family`. `qdisc` adds `fq_codel`, dumps qdiscs, expects fq_codel data, then deletes it. `flower` adds clsact, creates a flower filter, dumps ingress filters, verifies VLAN id/priority, then deletes filter and qdisc.

Dependencies/integration: requires TC qdisc/classifier/action kernel support from `tests/config`, YNL generated `tc-user.h`, kselftest, and network namespace privileges.

Risks/test signals: complex generated-code coverage includes indexed arrays, binary structs, nested sub-options, endian fields, and action arrays. Cleanup paths matter because qdiscs/filters are namespace-local but can affect subsequent assertions. Unsupported clsact is skipped, while filter add failures are hard failures.
