## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/arc/gaudi2_arc_common_packets.h

### Purpose
`gaudi2_arc_common_packets.h` defines common Gaudi2 ARC CPU identifiers and ARC address-region identifiers shared by ARC firmware packet/control code and the host driver. It names scheduler ARCs, QMAN ARCs for each engine family, special broadcast/invalid IDs, and 16 ARC memory regions.

### Important APIs, Types, And Functions
The anonymous CPU-ID enum defines scheduler IDs `CPU_ID_SCHED_ARC0` through `CPU_ID_SCHED_ARC5`, TPC QMAN IDs `CPU_ID_TPC_QMAN_ARC0` through `CPU_ID_TPC_QMAN_ARC24`, MME/EDMA/PDMA/ROT/NIC QMAN ARC IDs, `CPU_ID_MAX = 69`, `CPU_ID_SCHED_MAX = 6`, `CPU_ID_ALL = 0xFE`, and `CPU_ID_INVALID = 0xFF`. `enum arc_regions_t` defines regions 0 through 15, including SRAM, CFG, general-purpose windows, HBM0 firmware, HBM1-3 graph compiler data, DCCM, PCIe, and LBU windows.

### Control Flow
The header contains no functions. Runtime code uses CPU IDs to address commands, notifications, or setup to specific ARC processors, and uses region identifiers to program ARC auxiliary address translation windows. Region comments document the ARC-visible high-nibble address windows from `0x10000000` through `0xF0000000`.

### State, Persistence, And Dependencies
CPU IDs and region IDs are firmware ABI values. State lives in ARC firmware, command queues, and AUX region registers. The file is included by Gaudi2 driver code such as `gaudi2.c` and must stay synchronized with ARC firmware packet definitions.

### Integration Points
The IDs integrate with Gaudi2 scheduler and engine-firmware flows. They are conceptually paired with ARC farm auxiliary register maps and masks, because those registers configure the address regions named here. Host driver code can use `CPU_ID_ALL` for broadcast and `CPU_ID_INVALID` as a sentinel.

### Risks
Changing numeric CPU IDs can route firmware commands to the wrong ARC. `CPU_ID_TPC_QMAN_ARC24` is documented as never present, so loops must use topology presence checks rather than blindly treating every ID below `CPU_ID_MAX` as live. Region ID spelling and comments are ABI documentation; incorrect region programming can make ARC firmware access the wrong memory aperture.

### Test Signals
Firmware boot and scheduler tests should verify commands to each scheduler ARC, active TPC/MME/DMA/NIC QMAN ARC routing, broadcast behavior, invalid-ID rejection, and AUX region programming for SRAM, CFG, HBM, DCCM, PCIe, and LBU windows. Topology tests should confirm absent ARC IDs are skipped.
