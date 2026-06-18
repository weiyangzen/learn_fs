## sources/distributed-fs/ceph-client/include/linux/can/core.h

**Purpose:** This header exposes the PF_CAN core interfaces used by CAN protocol modules and drivers.

**Important APIs/types/functions:** `DNAME()` formats device names for optional devices. `struct can_proto` binds socket type/protocol to proto ops and `struct proto`. `CAN_REQUIRED_SIZE()` computes the minimum structure size containing a member. APIs include `can_proto_register()`, `can_proto_unregister()`, `can_rx_register()`, `can_rx_unregister()`, `can_send()`, `can_set_skb_uid()`, and `can_sock_destruct()`.

**Control flow, state, persistence:** Protocol modules register socket protocols; receive callbacks are attached to net namespaces/devices with CAN ID and mask filters; `can_send()` injects frames with optional loopback. Runtime filter tables and protocol lists live in AF_CAN implementation state.

**Dependencies/integration:** Depends on CAN UAPI, skbuffs, netdevices, network namespaces, and sockets. It is the shared integration point for raw, BCM, ISO-TP, J1939, and driver-facing CAN code.

**Risks and test signals:** Risks are filter lifetime races, mismatched register/unregister callback/data pairs, namespace leaks, and sending malformed SKBs. Test signals include PF_CAN protocol load/unload, receive filter matching, loopback behavior, namespace teardown, and socket destructor/refcount tests.
