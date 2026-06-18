<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h

## Purpose
`xt_repldata.h` is a small compatibility helper header for building replacement-table data used by iptables internals. It centralizes a static initializer pattern for x_tables replacement metadata.

## Important APIs, Types, and Functions
The header defines the `xt_repldata` structure initializer macro used by generated or static replacement-table definitions. It references x_tables concepts such as table name, valid hooks, entry counts, and hook/underflow offsets.

## Control Flow, State, and Persistence
There is no executable control flow. The header contributes compile-time data layout used by callers to initialize replacement structures. Any state belongs to the table replacement consumer.

## Dependencies and Integration Points
It depends on x_tables UAPI/internal structures and is included by table code that needs static replacement data. It is not a loadable module and has no runtime registration.

## Risks and Test Signals
Risks include structure layout drift across x_tables revisions, incorrect hook offset initialization by users, and alignment mismatches. Tests should be compile-focused: include the header in all intended table builds, validate replacement structure sizes and offsets, and run iptables table replacement tests that exercise hook and underflow arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_repldata.h -->
