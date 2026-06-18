# sources/distributed-fs/ceph-client/include/uapi/linux/lockd_netlink.h

Purpose: provides the generated generic-netlink UAPI for lockd server configuration and status.

Important APIs and types: `LOCKD_FAMILY_NAME` is `"lockd"` and version is `LOCKD_FAMILY_VERSION`. Attributes include `LOCKD_A_SERVER_GRACETIME`, `LOCKD_A_SERVER_TCP_PORT`, and `LOCKD_A_SERVER_UDP_PORT`. Commands include `LOCKD_CMD_SERVER_SET` and `LOCKD_CMD_SERVER_GET`.

Control flow: netlink clients issue server get/set commands with grace-time and port attributes. The lockd kernel family applies or reports NFS lock daemon settings according to its generated YNL policy.

State and persistence: runtime lockd server settings and grace-period state live in the kernel lockd/NFS server subsystem. The header stores no data and does not define persistence across service restart.

Dependencies and integration points: generated from `Documentation/netlink/specs/lockd.yaml`; integrates generic netlink/YNL tooling, lockd, and NFS server administration tools.

Risks and test signals: risks include generated header/spec drift, enum renumbering, invalid port validation, and inconsistent get/set behavior. Test YNL schema generation, netlink get/set with valid and invalid attributes, and lockd server behavior after configuration changes.
