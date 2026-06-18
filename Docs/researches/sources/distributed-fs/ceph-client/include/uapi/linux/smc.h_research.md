<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/smc.h

Purpose: defines UAPI constants and socket options for the SMC protocol family, including SMC-R/SMC-D selection, diagnostics, and connection metadata.

Important APIs, types, and functions: the header exports SMC protocol/socket constants, option names for enabling/disabling SMC variants and retrieving info, and structures used to describe SMC connection, link, device, peer, or fallback state for userspace.

Control flow: applications create AF_SMC sockets or query SMC state through socket options. The kernel negotiates SMC-R over RDMA or SMC-D over ISM when possible, otherwise falls back to TCP, and reports negotiated/fallback state through the defined ABI.

State and persistence behavior: SMC connection, link group, RDMA/ISM device, token, buffer, and fallback state lives in kernel socket and device state for the connection lifetime. The header defines query/control layouts only.

Dependencies and integration points: integrates with AF_SMC sockets, TCP fallback, RDMA/InfiniBand, ISM devices, net namespaces, and diagnostic tooling.

Risks and edge cases: fallback reasons and link metadata must be stable for tooling. Protocol selection must handle systems lacking RDMA/ISM. Socket option structs need version/length compatibility as SMC features grow.

Test signals: AF_SMC connection setup with SMC-R, SMC-D, and TCP fallback, socket-option get/set behavior, metadata dumps, unsupported-device cases, and connection teardown under device loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc.h -->
