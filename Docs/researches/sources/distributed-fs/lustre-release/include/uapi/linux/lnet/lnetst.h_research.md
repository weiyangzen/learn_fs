# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnetst.h

## Purpose
This UAPI header defines the ioctl and generic-netlink-facing ABI for LNet selftest. It describes sessions, groups, batches, tests, debug/stat requests, test parameters, and wire counters used by the selftest framework.

## Important APIs, Types, And Functions
Important constants include `LST_FEAT_BULK_LEN`, `LST_NAME_SIZE`, the `LSTIO_*` ioctl command values, node state bits, batch/group operation codes, `LST_DEFAULT_BATCH`, `LST_MAX_CONCUR`, and the `LNET_SELFTEST_*` generic netlink identifiers. `struct lst_sid` and `struct lst_bid` identify sessions and batches. The `lstio_*_args` structs are the user/kernel ioctl payloads for session, group, node, batch, test, debug, and stats operations. `struct lstcon_trans_stat` stores RPC/framework counters; inline helpers increment or read fixed slots in those arrays. `struct lst_test_bulk_param`, `struct lst_test_ping_param`, `struct srpc_counters`, and `struct sfw_counters` define test parameters and returned counters.

## Control Flow
Users create a session, add groups and nodes, add batches and tests, start or stop batches, query status, and request stats/debug data through ioctl payloads. Many payloads carry `__user` pointers to variable-length buffers or result list heads. Transaction helpers update different indexes in `trs_rpc_stat` and `trs_fwk_stat` depending on the operation family, so consumers must interpret the same arrays according to context. Bulk and ping test parameters select operation type, size, timing, loop count, validation flags, and concurrency.

## State, Persistence, And Dependencies
The header stores no live state, but its structures are the persistent ABI between selftest user tools and kernel modules. It depends on `lnet-types.h` for process IDs and on Linux time/types. `srpc_counters` and `sfw_counters` are packed because they are sent over the wire.

## Integration Points
Selftest controller code, user utilities, and generic netlink handlers consume these definitions. The test framework also depends on LNet process IDs, list-head compatibility stubs for user builds, and LNet message transport underneath the test RPCs.

## Risks
The ABI uses raw `__user` pointers and list heads, so copy-in/copy-out length validation is critical. Inline statistic helpers assume fixed array indexes; off-by-one or context confusion can report wrong states. Some comments contain legacy spellings and stale wording, which raises documentation risk but not direct runtime risk. Packed wire counters must remain layout-stable.

## Test Signals
Exercise full session lifecycle, group add/update/list/info, batch add/start/query/stop/delete, bulk and ping test creation, debug result lists, and stats queries. ABI tests should verify struct sizes, command values, packed counter layout, feature negotiation, maximum concurrency handling, and invalid pointer/length rejection.
