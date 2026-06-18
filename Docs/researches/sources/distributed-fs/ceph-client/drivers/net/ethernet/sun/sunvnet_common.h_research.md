# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.h

## Purpose
`sunvnet_common.h` defines the shared constants, state structures, inline helpers, and exported function prototypes for Sun LDOM virtual network common code. It is the interface between front-end drivers such as `sunvnet.c` and the shared VIO/LDC packet implementation in `sunvnet_common.c`.

## Important APIs, Types, And Constants
- Packet/ring/offload constants: `VNET_CLEAN_TIMEOUT`, `VNET_MAXPACKET`, `VNET_TX_RING_SIZE`, `VNET_TX_WAKEUP_THRESH()`, `VNET_MINTSO`, `VNET_MAXTSO`, `VNET_MAX_MTU`, `VNET_PACKET_SKIP`, `VNET_MAXCOOKIES`, and `VNET_MAX_TXQS`.
- `struct vnet_tx_entry` stores one outstanding SKB, cookie count, and LDC cookies for a TX descriptor.
- `struct vnet_port_stats` defines fixed-width per-port counters and `NUM_VNET_PORT_STATS`.
- `struct vnet_port` embeds `struct vio_driver_state` and stores peer MAC, role flags, parent vnet/netdev pointers, TX buffer ring, list/hash nodes, flow-control booleans, cleanup timer, negotiated MTU/TSO, NAPI state, event mask, and queue index.
- `to_vnet_port()` maps a VIO state pointer back to `struct vnet_port`.
- `vnet_hashfn()` hashes MAC bytes into a 16-bucket port hash.
- `struct vnet_mcast_entry` tracks multicast addresses, whether they have been sent, and whether they remain present.
- `struct vnet` stores lock, netdev pointer, message level, TX queue usage, port list/hash, multicast list, parent-list node, local MAC, and port count.
- Public prototypes declare common netdev, VIO handshake, NAPI, TX, reset, poll-controller, and queue-allocation functions.

## Control Flow And State Behavior
The header fixes the common runtime model: a `vnet` owns many `vnet_port` instances, each port owns one VIO/LDC channel and a 512-entry TX descriptor ring, and the front-end selects a port per SKB before calling `sunvnet_start_xmit_common()`. `VNET_PACKET_SKIP` is part of the wire-buffer layout and is used by both TX shaping and RX pulling. Queue assignment is bounded by `VNET_MAX_TXQS`, while `q_used[]` spreads ports across netdev TX queues.

## Dependencies And Integration Points
The header includes `<linux/interrupt.h>` and relies on declarations from VIO/LDC, netdev, NAPI, timers, SKB, hlist/list, and Ethernet headers that are included by users. It integrates front-end drivers with common code through the exported function prototypes and the `VNET_PORT_TO_NET_DEVICE()` role distinction for vnet versus virtual-switch ports.

## Risks And Edge Cases
- Structure fields are shared by interrupt, NAPI, timer, and TX contexts; callers must respect the locking rules implemented in the C file.
- `VNET_MAXPACKET` allows jumbo MTUs up to 65535 plus Ethernet/VLAN headers, which drives cookie count and allocation sizes.
- Role flags `switch_port`, `tso`, and `vsw` alter routing, checksum behavior, and netdev selection.
- The multicast list is a manual singly linked list, so update/send code must handle allocation failure and removal carefully.
- `NUM_VNET_PORT_STATS` assumes every field in `struct vnet_port_stats` is `u32`.

## Test Signals
Compile users with vnet and virtual-switch configurations, validate queue index allocation up to and beyond 16 ports, check MAC hash collision behavior, verify per-port stat string counts match `NUM_VNET_PORT_STATS`, and stress reset/timer/NAPI/TX interactions over the fields exposed in `struct vnet_port`.
