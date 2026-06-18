# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.c

Purpose: `usbip_network.c` implements shared usbip TCP connection handling, socket options, common PDU send/receive, and byte-order packing.

Important APIs: global `usbip_port` and `usbip_port_string` default to 3240 and can be changed by `usbip_setup_port_number()`. `usbip_net_pack_uint32_t()`, `usbip_net_pack_uint16_t()`, `usbip_net_pack_usb_device()`, and `usbip_net_pack_usb_interface()` convert wire fields. `usbip_net_recv()` and `usbip_net_send()` loop through `recv(MSG_WAITALL)`/`send()` via `usbip_net_xmit()`. `usbip_net_send_op_common()` and `usbip_net_recv_op_common()` handle the shared header. Socket helpers set reuseaddr, nodelay, keepalive, v6only, and `usbip_net_tcp_connect()` resolves/connects IPv4 or IPv6 addresses.

Control flow and integration: CLI and daemon call these routines before command-specific PDUs. Version and status validation happen in `usbip_net_recv_op_common()`.

State and dependencies: state is global port configuration and socket options. It depends on POSIX sockets, getaddrinfo, TCP, and protocol constants. Risks include send/recv treating any zero/negative as generic failure without preserving detailed errno, `usbip_setup_port_number()` leaving previous valid port after invalid input, returning `EAI_SYSTEM` as a positive pseudo-fd on total connect failure, and no TLS/authentication in the protocol. Test signals are remote list/import success over IPv4/IPv6 and correct rejection on protocol version/status mismatch.
