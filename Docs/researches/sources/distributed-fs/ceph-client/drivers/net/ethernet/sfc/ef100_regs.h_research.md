<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h

## Purpose
Provides EF100/Riverhead hardware architecture constants: MMIO register offsets, register strides/rows, bitfield positions and widths, host-memory descriptor layouts, event encodings, PCI vendor capability table fields, RX prefix fields, TX descriptor formats, design-parameter IDs/defaults, and protocol enumerations.

## Important APIs, Types, And Functions
- Register offsets include `ER_GZ_MC_SFT_STATUS`, MCDI doorbells, event queue prime/timer/credit registers, RX/TX ring doorbells, hardware time, and design-parameter TLV registers.
- Descriptor/event field macros define RX descriptors/prefixes, TX send/segment/TSO/override/mem2mem formats, RX packet events, TX completions, driver events, timestamp events, and EF100 event type enumerators.
- PCI capability macros define Xilinx config BAR VSEC and table entries used by `ef100.c`.
- Design parameter enums/defaults define TLV types consumed by `ef100_nic.c`.

## Control Flow
No code executes here. The macros are consumed by I/O helpers and `EFX_*FIELD*` packing/unpacking macros in EF100 PCI, NIC, RX, and TX code. Control flow in those files depends on these constants matching hardware layout exactly.

## State And Persistence
No software state is stored. The header describes hardware state exposed through MMIO registers and DMA descriptor/event memory. Constants such as `ESE_GZ_FCW_LEN`, `ESE_GZ_RX_PKT_PREFIX_LEN`, and TSO defaults directly influence runtime allocation and parsing decisions.

## Dependencies And Integration Points
Included by EF100 PCI/NIC/netdev/RX/TX files and indirectly by common register access macros. It integrates the driver with EF100 firmware/hardware ABI and MCDI-adjacent layout expectations.

## Risks And Edge Cases
Incorrect bit offsets or widths can corrupt DMA descriptors, misread events, map the wrong BAR window, mishandle RX checksum/classification, or reject valid hardware design parameters. Event phase fields must align between RX and TX completions. PCI table constants must match firmware/FPGA capability structures or probe can fail. There is no runtime validation for most definitions beyond hardware behavior.

## Test Signals
Signals are integration-level: successful PCI capability discovery, MCDI doorbells, EVQ priming, RX/TX doorbells, packet RX prefix parsing, TX offloads including TSO/checksum/VLAN, event dispatch, design-parameter parsing, and absence of hardware warnings/resets during traffic. Build failures also reveal renamed or missing field macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h -->
