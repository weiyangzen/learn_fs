
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h

## Purpose
Defines the SocketCAN Broadcast Manager protocol ABI. It supports timed transmit jobs, receive filters, change notifications, and multiplexed CAN/CAN FD frame handling through BCM socket messages.

## APIs, Control Flow, and State
Exports include `struct bcm_timeval`, `struct bcm_msg_head`, operation codes such as `TX_SETUP`, `TX_DELETE`, `TX_READ`, `TX_SEND`, `RX_SETUP`, `RX_DELETE`, `RX_READ`, `TX_STATUS`, `TX_EXPIRED`, `RX_STATUS`, `RX_TIMEOUT`, and `RX_CHANGED`, plus flags like `SETTIMER`, `STARTTIMER`, `TX_COUNTEVT`, `TX_ANNOUNCE`, `TX_CP_CAN_ID`, `RX_FILTER_ID`, `RX_CHECK_DLC`, `RX_NO_AUTOTIMER`, `RX_ANNOUNCE_RESUME`, `TX_RESET_MULTI_IDX`, `RX_RTR_FRAME`, and `CAN_FD_FRAME`. User messages carry timers, counters, CAN ID filters, frame count, and a following frame array. Kernel BCM sockets maintain the persistent per-socket job/filter state and timers; the header only defines the message contract.

## Dependencies, Integration, Risks, and Tests
Depends on core `linux/can.h` and fixed-width types. Integration points are PF_CAN BCM sockets, periodic transmission, receive timeout/change detection, and CAN FD frame arrays. Risks include variable-length frame array bounds, timer/counter races, userspace mixing classic and FD frames without `CAN_FD_FRAME`, and 32/64-bit `bcm_timeval` compatibility. Test signals include BCM selftests for setup/read/delete, periodic transmit expiry, RX timeout/change events, RTR behavior, CAN FD jobs, and malformed message length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h -->
