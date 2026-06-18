# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_node_table.h

Purpose: defines the RNI allocation table layout and constants for SCU remote node allocation. It encodes the hardware constraint that STP may require three consecutive remote node contexts.

Important APIs/types: `SCIC_SDS_REMOTE_NODE_SETS_PER_BYTE`, `SCIC_SDS_REMOTE_NODE_SETS_PER_DWORD`, `SCIC_SDS_REMOTE_NODES_PER_BYTE`, and `SCIC_SDS_REMOTE_NODES_PER_DWORD` describe the nibble packing. `SCIC_SDS_REMOTE_NODE_TABLE_FULL_SLOT_VALUE` is `0x07`, meaning all three bits in a group are available; `EMPTY_SLOT_VALUE` is `0`. `SCU_STP_REMOTE_NODE_COUNT`, `SCU_SSP_REMOTE_NODE_COUNT`, and `SCU_SATA_REMOTE_NODE_COUNT` express allocation sizes. `struct sci_remote_node_table` stores `available_nodes_array_size`, `group_array_size`, the packed node bitmap, and three selector bitmaps keyed by one-, two-, and three-entry availability. Public APIs initialize, allocate, and release entries.

Control flow: users initialize with the controller's remote-node capacity. Allocation callers pass the required count and receive a base RNI or invalid index. Release callers must provide the same count used at allocation time.

State and persistence behavior: table contents are volatile controller-lifetime allocation state. The source-tree-level invariant is that selector bitmaps mirror the nibble bitmap: selector 0 means one bit set, selector 1 means two bits set, selector 2 means three bits set. The arrays are sized from `SCI_MAX_REMOTE_DEVICES`, so runtime capacities smaller than the maximum use prefixes of the arrays.

Dependencies/integration: includes `isci.h` for maximum device count and integer types. The table backs remote-device construction, which then programs matching hardware contexts through `remote_node_context.c`.

Risks: callers must not mix STP triple and SSP single release semantics. Any future hardware with a different STP RNC count would require updating packing constants and implementation logic together. Test signals include struct sizing for maximum devices, initialization for odd capacities, selector consistency after operations, and invalid-index handling when no group of requested size exists.
