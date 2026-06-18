
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h

## Purpose
Defines the SocketCAN ISO 15765-2 transport protocol socket options. It exposes addressing, padding, flow-control, link-layer, timing, broadcast, and CAN FD support configuration for ISO-TP sockets.

## APIs, Control Flow, and State
Exports include `SOL_CAN_ISOTP`, socket option names `CAN_ISOTP_OPTS`, `CAN_ISOTP_RECV_FC`, `CAN_ISOTP_TX_STMIN`, `CAN_ISOTP_RX_STMIN`, and `CAN_ISOTP_LL_OPTS`; structures `can_isotp_options`, `can_isotp_fc_options`, and `can_isotp_ll_options`; flags such as listen mode, extended/RX extended addressing, TX/RX padding and pad checks, half-duplex, forced STmin, wait-for-TX-done, single-frame and consecutive-frame broadcast, and dynamic flow-control parameters; defaults for flags, padding, frame tx time, block size, STmin, WFTmax, MTU, tx data length, and tx flags; and `CAN_ISOTP_FRAME_TXTIME_ZERO`. Kernel ISO-TP sockets use these options to drive segmentation, flow-control exchange, timers, padding validation, and CAN/CAN FD frame generation. Per-socket protocol state persists in the kernel.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/can.h` and fixed-width types. Integration points are PF_CAN ISO-TP sockets, automotive diagnostics, UDS tools, CAN FD transport, and vcan tests. Risks include invalid extended-address combinations, padding-check incompatibility with peers, STmin unit/override confusion, broadcast modes bypassing normal flow control, invalid link-layer MTU/tx_dl pairs, and timing races around half-duplex or wait-for-TX-done. Test signals include ISO-TP selftests for multi-frame transfer, flow-control limits, padding validation, CAN FD payload sizes, broadcast modes, timeout paths, and setsockopt/getsockopt round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h -->
