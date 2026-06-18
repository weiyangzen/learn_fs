## sources/distributed-fs/ceph-client/include/linux/can/can-ml.h

**Purpose:** This header defines CAN network-layer private state and receive-list containers used by the PF_CAN core.

**Important APIs/types/functions:** Capability bits are `CAN_CAP_CC`, `CAN_CAP_FD`, `CAN_CAP_XL`, and `CAN_CAP_RO`. Receive-list constants size SFF direct arrays and EFF hash arrays. `struct can_dev_rcv_lists` contains generic, SFF, and EFF receive hlist heads plus entry count. `struct can_ml_priv` stores device receive lists, optional J1939 private state, and capability mask. Inline helpers are `can_get_ml_priv()`, `can_set_ml_priv()`, `can_cap_enabled()`, and `can_set_cap()`.

**Control flow, state, persistence:** The header stores per-netdevice receive filter state and capabilities. Inline helpers attach/retrieve this state through netdevice ML private slots.

**Dependencies/integration:** Depends on CAN IDs, hlist/list infrastructure, netdevice ML private data, and optional J1939 integration.

**Risks and test signals:** Risks include uninitialized ML private state, stale receive-list entries on device unregister, capability masks inconsistent with device MTU/ctrlmode, and optional J1939 build coverage. Test signals include PF_CAN receive filter registration/unregistration, SFF/EFF dispatch tests, capability reporting, and netdevice teardown leak checks.
