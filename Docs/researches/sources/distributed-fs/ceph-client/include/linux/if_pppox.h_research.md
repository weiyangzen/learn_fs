# `sources/distributed-fs/ceph-client/include/linux/if_pppox.h`

Purpose: generic PPP-over-X kernel socket support for PPPoE/PPTP style transports, including socket private state and protocol registration hooks.

Important APIs/types/functions: `pppoe_hdr`, `struct pppoe_opt`, `struct pptp_opt`, `struct pppox_sock`, `pppox_sk`, `struct pppox_proto`, registration functions, `pppox_unbind_sock`, `pppox_ioctl`, compat ioctl, and socket state enum values.

Control flow and state: PPPoX socket state persists in `struct pppox_sock`, embedding `struct sock` first, a PPP channel, RCU hash linkage, transport-specific union, protocol number, sequence/ack state for PPTP, and PADT work for PPPoE.

Dependencies/integration: depends on netdevice, PPP channel core, workqueues, sockets, and UAPI PPPoX definitions. PPPoE and PPTP modules register `pppox_proto` handlers.

Risks: `struct sock` must remain first for container casting; RCU hash linkage and workqueue teardown must be synchronized; ioctl compatibility matters; PPP channel unbind must avoid use-after-free during disconnect.

Test signals: PPPoE connect/disconnect/PADT handling, PPTP sequence/ack updates, proto register/unregister, ioctl and compat ioctl paths, and socket lifetime under module unload.
