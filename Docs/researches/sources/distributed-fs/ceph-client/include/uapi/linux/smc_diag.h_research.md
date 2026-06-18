<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h

Purpose: defines netlink sock_diag request, response, attribute, and payload layouts for inspecting SMC sockets and SMC-R/SMC-D internals.

Important APIs, types, and functions: `struct smc_diag_req` and message/extension enums select SMC diagnostics. Payload structs include `smc_diag_msg`, `smc_diag_cursor`, `smc_diag_conninfo`, `smc_diag_linkinfo`, `smc_diag_lgrinfo`, `smc_diag_fallback`, and `smcd_diag_dmbinfo`.

Control flow: diagnostic tools send a sock_diag request for SMC sockets. The kernel dumps socket records with optional connection info, link group/link info, fallback data, and SMC-D DMB information encoded as netlink attributes.

State and persistence behavior: responses are snapshots of live socket, cursor, send/receive buffer, link, token, GID, and fallback state. The header owns no persistent state.

Dependencies and integration points: depends on inet diagnostics, socket diagnostics, and InfiniBand device-name limits. It integrates with `ss`, sock_diag netlink, AF_SMC internals, RDMA, and ISM.

Risks and edge cases: live sockets can change while being dumped, so cursors and counters are snapshots. Optional extensions must be length-checked. GID/token fields differ between SMC-R and SMC-D, and tooling must tolerate absent attributes.

Test signals: sock_diag dumps for idle and active SMC-R/SMC-D sockets, fallback connections, extension filtering, namespace isolation, socket destruction during dump, and attribute length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h -->
