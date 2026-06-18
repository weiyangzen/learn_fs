## sources/distributed-fs/ceph-client/include/linux/can/rx-offload.h

**Purpose:** This header defines helper state and APIs for CAN drivers that offload receive handling into NAPI-backed queues.

**Important APIs/types/functions:** `struct can_rx_offload` stores netdev, mailbox-read callback, normal and IRQ SKB queues, max queue length, mailbox range, NAPI object, and direction flag. APIs add timestamp/FIFO/manual offload modes, queue timestamped or tail SKBs, retrieve echo SKBs into queues, finish IRQ/threaded IRQ receive processing, delete, enable, and disable offload.

**Control flow, state, persistence:** Drivers initialize offload, enqueue received SKBs from interrupt context, and finish IRQ handling to schedule NAPI. NAPI drains queues into the network stack. State is transient queue/NAPI state tied to the netdevice.

**Dependencies/integration:** Depends on netdevice, NAPI, CAN SKB helpers, and driver mailbox/timestamp hardware.

**Risks and test signals:** Risks include queue overflow, timestamp ordering mistakes, incorrect mailbox direction, NAPI lifecycle races, and using non-IRQ-safe paths in interrupt context. Test signals include high-rate RX stress, timestamp ordering tests, bus-off/error traffic, NAPI enable/disable during open/close, and echo SKB accounting.
