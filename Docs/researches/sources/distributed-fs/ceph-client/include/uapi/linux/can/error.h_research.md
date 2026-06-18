
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h

## Purpose
Defines SocketCAN error-frame class bits and payload byte encodings. It lets drivers and userspace classify arbitration loss, controller errors, protocol violations, transceiver faults, ACK failures, bus-off, bus-error, restart, and error-counter reports.

## APIs, Control Flow, and State
The header exports `CAN_ERR_DLC`, top-level `CAN_ERR_*` mask bits, per-byte detail constants such as `CAN_ERR_LOSTARB_*`, controller state bits, protocol violation bits, protocol-location codes, transceiver status codes, and error-counter byte assignments. There are no functions; drivers populate an error `can_frame` with `CAN_ERR_FLAG` plus these masks, and userspace decodes `data[0]` through `data[7]` according to the constants. Persistent controller error state lives in the CAN driver/netdevice, not in the header.

## Dependencies, Integration, Risks, and Tests
Integrates with CAN drivers, raw sockets subscribed to error masks, netlink state/error counters, and diagnostic tools. Risks include flooding userspace with bus-error frames, drivers setting inconsistent class/detail bytes, ambiguity in unspecified locations/statuses, and userspace forgetting that error frames use classic CAN DLC 8 even for FD-capable devices. Test signals include injected CAN controller error states, raw socket error-mask filtering, bus-off/restart tests, transceiver error mapping checks, and diagnostics comparing error frames with netlink counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h -->
