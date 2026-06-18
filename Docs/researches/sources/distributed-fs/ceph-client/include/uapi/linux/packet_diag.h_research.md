# sources/distributed-fs/ceph-client/include/uapi/linux/packet_diag.h

Purpose: Defines the netlink socket diagnostic ABI for AF_PACKET sockets.

Important APIs/types/functions: Exports `struct packet_diag_req`, `PACKET_SHOW_*` request bits, `struct packet_diag_msg`, diagnostic attribute enum values, `struct packet_diag_info`, `PDI_*` flags, `struct packet_diag_mclist`, and `struct packet_diag_ring`.

Control flow: Userspace sends a diagnostic request selecting family, protocol, inode/cookie filters, and show bits. The kernel replies with packet socket identity and optional nested attributes for basic info, multicast memberships, RX/TX ring configuration, fanout, UID, memory info, and attached filter.

State and persistence behavior: The header snapshots live socket state: packet socket type/num, inode, cookie, interface index, TPACKET version, reserve/copy thresholds, timestamp mode, flags, multicast memberships, and ring geometry. No state is persisted by the header.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with `sock_diag`, `ss`, packet socket ring setup, fanout, BPF filters, and network namespace introspection.

Risks: Diagnostics can expose packet socket configuration and filter programs. Ring fields must match TPACKET setup, and multicast address buffers are fixed at 32 bytes. Inode/cookie filtering must avoid leaking sockets across namespace or permission boundaries.

Test signals: Query AF_PACKET sockets with each `PACKET_SHOW_*` bit, compare ring config to `PACKET_RX_RING`/`TX_RING` setup, validate multicast list output, test namespace isolation, and check attached filter reporting.
