## sources/distributed-fs/ceph-client/include/linux/can/dev.h

**Purpose:** This header defines the common CAN network-device driver interface and `struct can_priv` base private data.

**Important APIs/types/functions:** `enum can_mode` models stop/start/sleep; `enum can_termination_gpio` models termination GPIO states. `struct can_priv` stores netdev pointer, CAN stats, nominal/data/XL bittiming, bitrate constraints, clock, termination data/GPIO, echo SKBs, state, ctrlmode, restart work, and driver callbacks. APIs include CAN netdev allocation/free/open/close, registration, restart/bus-off handling, static ctrlmode setup, timestamping ethtool helpers, state-string helpers, state transitions, and OF transceiver setup.

**Control flow, state, persistence:** Drivers allocate a candev, fill constraints/callbacks, open/close through common helpers, update ctrlmode/state, queue restart work on bus-off, and use `can_dev_dropped_skb()` to reject sends that violate mode/frame constraints. State is runtime netdevice state.

**Dependencies/integration:** Depends on CAN bittiming/error/length/netlink/SKB helpers, ethtool, netdevice, GPIO, delayed work, and optional OF.

**Risks and test signals:** Risks include ctrlmode/MTU mismatch, leaking echo SKBs, wrong bus-off restart timing, accepting FD/XL frames when disabled, and unpaired open/close. Test signals include netlink ctrlmode changes, CAN FD/XL send rejection, bus-off recovery, timestamping queries, echo SKB accounting, and register/unregister tests.
