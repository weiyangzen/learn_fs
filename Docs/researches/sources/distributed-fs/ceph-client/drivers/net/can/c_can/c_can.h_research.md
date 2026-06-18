<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h

Purpose: this header is the shared contract for the Bosch C_CAN/D_CAN driver family. It defines abstract register ids, concrete register maps for C_CAN and D_CAN layouts, driver-data descriptors, RAM initialization metadata, TX ring state, private driver state, exported core APIs, and TX ring helpers.

Important APIs, types, and functions: `enum reg` names logical controller registers. `reg_map_c_can[]` and `reg_map_d_can[]` translate those names to offsets. `enum c_can_dev_id` differentiates `BOSCH_C_CAN` and `BOSCH_D_CAN`. `struct c_can_driver_data`, `struct c_can_raminit`, `struct c_can_tx_ring`, and `struct c_can_priv` carry device geometry, RAMINIT strategy, TX queue state, and all core callbacks. Exports declared here include `alloc_c_can_dev()`, `free_c_can_dev()`, `register_c_can_dev()`, `unregister_c_can_dev()`, and PM helpers when enabled.

Control flow: bus wrappers allocate a device with `alloc_c_can_dev()`, fill `struct c_can_priv` fields such as register map, read/write callbacks, clock frequency, base address, type, and RAMINIT hook, then call `register_c_can_dev()`. The core uses inline helpers `c_can_get_tx_head()`, `c_can_get_tx_tail()`, and `c_can_get_tx_free()` to manage TX ring capacity with different behavior for C_CAN prioritized mailboxes versus D_CAN FIFO-like transmission.

State and persistence: `struct c_can_priv` is the main runtime state object. It persists NAPI state, message object counts/ranges, RX mask, interrupt/status flags, TX direction bitmap, last status, TX ring indices, register accessors, MMIO base, type, RAMINIT system, and receive-command behavior.

Dependencies and integration points: the header is included by the core, ethtool file, platform wrapper, and PCI wrapper. It integrates with CAN core `struct can_priv`, NAPI, netdevices, regmap-backed RAMINIT, and architecture-specific MMIO access methods.

Risks: register map offsets and logical enum order must stay synchronized because 32-bit reads combine adjacent logical registers. TX free-space semantics differ by controller type and directly affect queue stopping. `struct can_priv` must remain first in `struct c_can_priv` for netdev private-data assumptions.

Test signals: compile C_CAN and D_CAN wrappers, verify register access paths on 16-bit and 32-bit aligned mappings, test TX ring wrap for both controller types, and use ethtool ring reporting to confirm message object partitioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h -->
