# sources/distributed-fs/ceph-client/net/smc/smc_diag.c

## Purpose
`smc_diag.c` implements SOCK_DIAG support for AF_SMC sockets. It lets user space dump SMC socket state, fallback reason, connection cursors, SMC-R link details, and SMC-D DMB details through the standard netlink socket diagnostics path.

## Important APIs, Types, and Functions
The local cursor type is `struct smc_diag_dump_ctx`, stored in `netlink_callback->ctx`. `smc_diag_msg_common_fill()` copies common address and cookie information from the SMC socket and its CLC TCP socket. `__smc_diag_dump()` emits one `struct smc_diag_msg` plus optional attributes. `smc_diag_dump_proto()` walks one SMC protocol hash table, and `smc_diag_dump()` dumps IPv4 then IPv6 SMC sockets. Module init/exit register and unregister `smc_diag_handler` for `AF_SMC`.

## Control Flow
A `SOCK_DIAG_BY_FAMILY` dump request enters `smc_diag_handler_dump()`, which starts a netlink dump with `smc_diag_dump()`. The dump scans `smc_proto` and, if IPv6 is enabled, `smc_proto6`, applying net namespace filtering and using per-protocol position cursors. For each socket, `__smc_diag_dump()` creates a netlink message, selects diagnostic mode as fallback TCP, SMC-D, or SMC-R, fills common attrs, then conditionally appends `SMC_DIAG_CONNINFO`, `SMC_DIAG_LGRINFO`, or `SMC_DIAG_DMBINFO` based on requested extensions and connection validity.

## State and Persistence
The file persists no state beyond module registration. Dump progress is held in callback context positions. It reads live socket and link-group state, so output is a snapshot under protocol hash lock plus checks such as `smc_conn_lgr_valid()` and `list_empty()`.

## Dependencies and Integration Points
It depends on Linux sock_diag/inet_diag/netlink APIs, `smc_proto`, `smc_proto6`, socket helpers from `smc.h`, core link-group helpers from `smc_core.h`, and ISM GID conversion from `smc_ism.h`. It exposes module aliases for NETLINK_SOCK_DIAG AF_SMC and the SMC-R generic netlink family name.

## Risks
Diagnostic dumps read a large amount of live state with minimal stabilization beyond hash locking and validity checks. Races with close, fallback, or link-group teardown could produce partial data, so every optional block must tolerate missing descriptors and removed groups. Message-size failures must cancel the current netlink message correctly. IPv6 paths are compiled conditionally and need coverage when enabled.

## Test Signals
Use `ss`, `sock_diag`, or SMC-specific diagnostic tools to dump AF_SMC sockets in fallback, SMC-R, and SMC-D modes. Validate extension masks for connection, link-group, and DMB info. Exercise sockets while closing or during link-group teardown and confirm no kernel warnings, malformed netlink messages, or stale namespace leakage.
