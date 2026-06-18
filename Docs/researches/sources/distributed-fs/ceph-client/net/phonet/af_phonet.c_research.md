# sources/distributed-fs/ceph-client/net/phonet/af_phonet.c

## Purpose
`af_phonet.c` implements the PF_PHONET protocol family core. It manages Phonet transport protocol registration, socket creation, Phonet link-layer header operations, outbound Phonet packet construction, inbound packet dispatch/routing/error responses, packet tap registration, and module initialization/exit.

## Important APIs, types, and functions
Protocol registration uses the RCU-protected `proto_tab[]`, `phonet_proto_register()`, `phonet_proto_unregister()`, `phonet_proto_get()`, and `phonet_proto_put()`. Socket family creation is `pn_socket_create()`, which selects default datagram or pipe protocol, autoloads missing protocol modules, checks socket type, allocates a `pn_sock` or `pep_sock`, and installs protocol ops.

Header operations are `pn_header_create()` and `pn_header_parse()`, exported as `phonet_header_ops`. Outbound packet construction uses `pn_skb_send()`, `pn_send()`, and `pn_raw_send()`. Inbound packet handling is `phonet_rcv()`, registered as a `packet_type` for `ETH_P_PHONET`. Error helpers `send_obj_unreachable()` and `send_reset_indications()` generate Common Message responses for undeliverable local objects when `can_respond()` allows it.

## Control flow and state
Socket creation requires `CAP_SYS_ADMIN`, resolves a `struct phonet_protocol`, allocates a PF_PHONET sock with that protocol's `struct proto`, initializes base `pn_sock` fields, calls protocol `init()`, and releases the module reference.

Outbound flow in `pn_skb_send()` chooses a device based on bound device, local-address loopback, resource routing, explicit route, or default Phonet device. It derives a source address with `phonet_address_get()`, fills the Phonet header in `pn_send()`, adds a device header for non-loopback traffic, and queues through `dev_queue_xmit()` or `netif_rx()` for loopback.

Inbound flow in `phonet_rcv()` clones as needed, validates and trims to the Phonet length field, extracts destination sockaddr, delivers broadcasts to broadcast sockets, resolves resource-routed packets by resource table, delivers local packets by object/port lookup, sends object-unreachable/reset indications for missing local endpoints, or routes nonlocal packets via `phonet_route_output()`. Routing re-adds the Phonet header, prevents same-device loops, expands headroom for device headers, and transmits.

Module initialization initializes per-net/device state, socket hashes, PF_PHONET family, packet tap, sysctl, and datagram protocol. Exit reverses this sequence and unregisters the packet tap and devices.

## State and persistence behavior
State includes the transport protocol table, PF_PHONET registration, packet tap registration, and sysctl/device state owned by other files. It is kernel memory only and disappears on module unload. Protocol table entries are protected by `proto_tab_lock` for updates and RCU for readers; module references prevent unloading while a protocol is selected for socket creation.

## Dependencies and integration points
This file integrates with netdevice packet taps (`dev_add_pack`), Phonet device/address/route helpers from `pn_dev.c`, socket lookup/resource helpers from `socket.c`, datagram registration from `datagram.c`, sysctl, and module autoload via `request_module("net-pf-%d-proto-%d", ...)`.

## Risks and edge cases
Risks include malformed Phonet length handling, loopback races after address deletion, route loops, source address selection failures, and error-response amplification. `can_respond()` is important to avoid replying to error messages. `phonet_proto_register()` registers the proto before inserting it in `proto_tab`; if the table slot is busy, the current code returns an error without unregistering the proto, so registration callers and module load paths are sensitive to duplicate protocol attempts.

## Test signals
Tests should cover socket creation permission checks, default protocol selection, module autoload, local datagram delivery, broadcast delivery, resource routing, route forwarding, address deletion race with loopback skb, route loop detection, MTU/length validation, and expected Common Message errors for unreachable local objects.
