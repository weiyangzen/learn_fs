# sources/distributed-fs/ceph-client/drivers/net/gtp.c

### Purpose
`gtp.c` implements the Linux `gtp` virtual network device for GTP-U tunneling as used by GSM/3GPP packet core networks. It supports GTPv0 and GTPv1-U, IPv4 and IPv6 subscriber PDP contexts, optional kernel-created UDP sockets, userspace-supplied sockets, generic-netlink PDP management, echo request/response support for kernel-created sockets, and per-netns device tracking.

### Important APIs, Types, And Functions
`struct gtp_dev` is the netdev private state: UDP sockets for GTP0 and GTP1-U, role, hash tables, per-netns list linkage, restart count, and socket ownership. `struct pdp_ctx` represents one active subscriber tunnel, with version-specific TID/TEI state, MS address, peer address, selected socket, device pointer, and TX sequence. PDP contexts are indexed in two RCU hash tables, one by tunnel ID and one by MS address. `struct gtp_net` tracks devices per namespace.

Runtime datapath functions are `gtp_encap_recv()`, `gtp0_udp_encap_recv()`, `gtp1u_udp_encap_recv()`, `gtp_rx()`, `gtp_dev_xmit()`, `gtp_build_skb_ip4()`, `gtp_build_skb_ip6()`, and the outer builders `gtp_build_skb_outer_ip4()` and `gtp_build_skb_outer_ip6()`. Management functions include `gtp_newlink()`, `gtp_dellink()`, `gtp_encap_enable()`, `gtp_create_sockets()`, `gtp_genl_new_pdp()`, `gtp_genl_del_pdp()`, `gtp_genl_get_pdp()`, `gtp_genl_dump_pdp()`, and `gtp_genl_send_echo_req()`.

### Control Flow
Device creation runs through rtnetlink. `gtp_newlink()` parses role, hash size, restart count, and socket mode. It allocates PDP hash tables, either creates bound UDP sockets or attaches encapsulation callbacks to userspace-provided UDP sockets, adjusts MTU/headroom for IPv6 sockets, registers the netdev, and links it into the netns list.

RX begins in `gtp_encap_recv()`, which uses UDP `encap_type` to dispatch to v0 or v1-U parsing. The v0 path checks flags, handles echo messages when sockets are kernel-created, validates TPDU type, identifies inner IPv4/IPv6, finds a PDP by TID and family, and calls `gtp_rx()`. The v1 path similarly handles echo messages, optional sequence/N-PDU/extension header length, extension-header parsing, TEI lookup, and decapsulation. `gtp_rx()` verifies the inner MS address against the PDP and device role, pulls GTP plus UDP headers, resets packet headers, accounts RX stats, and injects with `__netif_rx()`.

TX from the virtual device checks headroom and inner IP availability, then looks up a PDP by source or destination MS address depending on SGSN/GGSN role. It routes to the PDP peer using the PDP socket family, enforces circular route and PMTU checks, pushes a GTPv0 or GTPv1 header, and sends over UDP tunnel helpers. GTPv0 increments a per-PDP sequence counter and includes flow/TID; GTPv1 uses the outgoing TEI.

Generic-netlink commands manage PDP state. `GTP_CMD_NEWPDP` validates version-specific required attributes, resolves the target link and socket, and calls `gtp_pdp_add()`. That function rejects inconsistent address families, detects duplicate MS or TEID/TID entries, supports limited update semantics without replace, and inserts new contexts into both hash tables under RCU. Delete and get paths resolve by link plus MS address or tunnel ID. Multicast notifications are emitted for new/delete and echo responses.

### State And Persistence Behavior
PDP contexts are dynamic in-memory state only. They persist until generic-netlink deletion, device deletion, socket destruction, or namespace teardown. Each context holds a reference to its UDP socket and is freed with `call_rcu()`. Userspace-supplied sockets are held with `sock_hold()` and released when encapsulation is disabled. Kernel-created sockets are released through `udp_tunnel_sock_release()`. A random jhash seed is initialized at module load.

### Dependencies And Integration Points
The driver depends on UDP tunnel socket callbacks, rtnetlink link kind `gtp`, generic netlink family `gtp`, net namespace generic storage, IPv4/IPv6 routing, ICMP/ICMPv6 PMTU signaling, RCU hlist traversal, and UAPI attributes from `<linux/gtp.h>`. Userspace control planes configure PDP contexts through generic netlink and may either own UDP sockets or ask the kernel to create them.

### Risks
Risk areas include RCU lifetime around PDP deletion and generic-netlink get/delete, update semantics when one of the MS or tunnel-key entries exists but not both, address family mismatches between peer attributes and socket family, IPv6 PDP prefix assumptions that only compare the first 64 bits, extension header parsing bounds, echo behavior differences between kernel-created and userspace-owned sockets, and PMTU handling for nested tunnels. In `gtp_dev_xmit()`, IPv6 outer transmit uses unioned route storage, so regression tests should cover that path carefully.

### Test Signals
Exercise rtnetlink creation with userspace FDs and `IFLA_GTP_CREATE_SOCKETS`, IPv4 and IPv6 local sockets, GGSN and SGSN roles, invalid roles/hash sizes, PDP add/update/delete/get/dump for GTPv0 and GTPv1, duplicate MS and TEI/TID conflicts, IPv6 prefix validation, TPDU RX decapsulation, TX encapsulation for both inner families and outer socket families, PMTU/ICMP behavior, echo request/response multicast notifications, and namespace/device teardown with active PDP contexts.
