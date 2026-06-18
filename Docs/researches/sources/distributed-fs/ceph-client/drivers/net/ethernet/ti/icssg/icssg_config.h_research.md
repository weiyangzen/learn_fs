<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h

## Purpose

`icssg_config.h` defines the shared firmware configuration contract consumed by ICSSG configuration, main driver, SR1 support, switchdev, and statistics code. It describes packet descriptor sizing, MSMC buffer-pool sizing, management command formats, port-state command IDs, SR1 config layout, FDB/VLAN table formats, and firmware queue IDs.

## Important APIs, Types, and Functions

Important types include `struct icssg_buffer_pool_cfg`, `struct icssg_flow_cfg`, `struct icssg_rxq_ctx`, `struct icssg_r30_cmd`, `struct icssg_sr1_config`, `struct icssg_setclock_desc`, `struct mgmt_cmd`, `struct mgmt_cmd_rsp`, `struct prueth_vlan_tbl`, and `struct prueth_fdb_slot`. Key enums/macros define `enum icssg_port_state_cmd`, `ICSSG_FW_MGMT_*`, SR1 RX/management flow constants, hardware queue IDs, FDB membership bits, buffer pool totals for EMAC and switch mode, and IETF preemption verification states.

## Control Flow

The header has no executable flow. Its definitions shape `icssg_config.c` buffer setup and R30 command paths, `icssg_prueth_sr1.c` SR1 load-time config and management commands, `icssg_prueth.c` timestamp setclock descriptors, and switchdev/FDB code that passes membership flags to firmware.

## State and Persistence Behavior

Most structures are `__packed` and map directly to PRUSS DRAM/shared RAM or DMA-visible firmware command buffers. Any field layout change is an ABI change with ICSSG firmware. Buffer-size macros determine the SRAM allocation size in probe and the per-slice pool offsets written during interface start.

## Dependencies and Integration Points

The header relies on Linux endian/types helpers and on `SIZE_OF_FDB`/`NUMBER_OF_FDB_BUCKET_ENTRIES` from `icssg_switch_map.h` through include ordering in `icssg_prueth.h`. It is included by `icssg_prueth.h`, which makes these constants part of the broader driver internal API.

## Risks and Edge Cases

The file encodes firmware assumptions that are easy to break silently: SR1 command bitfields, queue IDs, FDB valid/membership bits, packed command response layout, and MSMC pool sizes. Comments note firmware-specific limitations such as only 4 real QoS levels and SR1 management queues. The `PRUETH_SWITCH_FDB_MASK` computation must stay consistent with firmware FDB bucket sizing and ageing logic.

## Test Signals

Build coverage across SR1 and non-SR1 platform drivers is the main compile-time signal. Runtime validation should exercise all modes that use the packed layouts: SR1 command responses, SR2 FDB management commands, VLAN table updates, PVID programming, and SRAM allocation sizing on banked and non-banked MSMC platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_config.h -->
