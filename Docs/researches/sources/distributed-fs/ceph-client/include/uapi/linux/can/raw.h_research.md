
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h

## Purpose
Defines the SocketCAN RAW protocol socket options. It lets userspace configure classic/FD/XL frame reception, filter lists, error filters, loopback, receive-own-messages behavior, join filters, and CAN XL virtual CAN ID handling.

## APIs, Control Flow, and State
Exports include `SOL_CAN_RAW`, `CAN_RAW_FILTER_MAX`, option enums for `CAN_RAW_FILTER`, `CAN_RAW_ERR_FILTER`, `CAN_RAW_LOOPBACK`, `CAN_RAW_RECV_OWN_MSGS`, `CAN_RAW_FD_FRAMES`, `CAN_RAW_JOIN_FILTERS`, `CAN_RAW_XL_FRAMES`, and `CAN_RAW_XL_VCID_OPTS`, plus `struct can_raw_vcid_options` and VCID option flags for TX set/pass and RX filter. RAW sockets store per-socket filter arrays and mode flags; receive paths match frames against filters and error masks, while transmit paths validate MTU and optional XL VCID behavior. The header itself has no runtime logic.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/can.h`. Integration points are PF_CAN RAW sockets, candump/cansend-style tools, vcan/vxcan tests, CAN FD/XL enablement, and error-frame diagnostics. Risks include large filter-array allocations, inverted/joined filter semantics surprising users, sending FD/XL frames without enabling the corresponding option, VCID masking mistakes, and loopback/own-message confusion in multi-socket tests. Test signals include raw socket filter tests, error-mask subscriptions, FD/XL send/receive, VCID option validation, and loopback/receive-own toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h -->
