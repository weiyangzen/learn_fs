# sources/distributed-fs/lustre-release/lnet/utils/lst.c

## Purpose
`lst.c` implements the `lst` user-space command for Lustre/LNet self-test session administration. It creates and destroys self-test sessions, manages node groups, defines batches and tests, starts/stops/query batches, pings nodes, and samples LNet/RPC self-test counters. It supports a newer generic-netlink/YAML path for session and group discovery while keeping legacy ioctl paths against `IOC_LIBCFS_LNETST`.

## Important APIs, Types, and Functions
- Global session state: `session_key`, `session_features`, `trans_stat`, and `LST_INVALID_SID`.
- `expand_strs()` and `lst_parse_nids()` expand numeric bracket expressions and convert them to `struct lnet_process_id` values.
- `lst_ioctl()` wraps `l_ioctl(LNET_DEV_ID, IOC_LIBCFS_LNETST, ...)` and separates local, RPC, and framework errors.
- `lst_yaml_session()` and `lst_yaml_groups()` use liblnetconfig YAML/netlink helpers before falling back to ioctls.
- `jt_lst_*` handlers implement session, ping, group, stat, error, batch, query, and test subcommands.
- `lst_alloc_rpcent()`, `lst_reset_rpcent()`, and `lst_print_transerr()` manage result lists of `struct lstcon_rpc_ent`.

## Control Flow
`main()` initializes environment-derived session state, initializes the LNet config library, and dispatches through `cfs_parser()`. Commands validate options with `getopt_long()`, enforce `LST_SESSION` for mutating/session-bound operations, discover target node counts, allocate matching RPC result lists, invoke a self-test ioctl or netlink request, and print either aggregate or per-node results. `stat` alternates between two samples and computes deltas; `stop` loops on query until no batch work is running or failed.

## State and Persistence Behavior
Only transient process state is held locally. Durable session/group/batch/test state is maintained by the kernel LNet self-test subsystem and selected by `session_key`. `LST_FEATURES` limits advertised features, and successful netlink session creation updates `session_key` and `session_features`.

## Dependencies and Integration Points
The file depends on libcfs ioctl/parser/list utilities, LNet nid conversion, liblnetconfig YAML generic-netlink helpers, and LNet self-test UAPI structures and operation codes from `linux/lnet/lnetst.h`.

## Risks and Edge Cases
YAML parsing is sensitive to reply shape, wide nid ranges can allocate large arrays, fixed-size string buffers need truncation care, return-code classes are non-obvious, stat deltas assume stable result ordering, and bulk parameter parsing needs boundary tests around size, offsets, suffixes, and `LNET_MTU`.

## Test Signals
Cover command option parsing, bracket expansion, invalid NIDs, netlink success/fallback, ioctl local/RPC/framework failures, group/batch empty targets, batch stop/query transitions, stat deltas and changed groups, and add-test validation for ping/brw parameters.
