# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-regs.h

## Purpose
This header defines shared IPU6 platform register offsets for ISYS/PSYS MMUs, SPC/DMEM regions, ISYS/PSYS interrupts, DMA/CD C thresholds, package directory placement, SPC status/control bits, info segment flags, pixel remapping constants, address-burst groups, and PSYS firmware IRQs.

## Important APIs, Types, And Data
Important definitions include unified offsets, ISYS/PSYS IOMMU offsets and stream-id register offsets, SPC/DMEM offsets, ISYS UNISPART/CSI-related IRQ registers, CDC threshold registers, CSI port counts, SPC status bits for start/run/ready/cache behavior, IPU information flags, pixel remapping no-op constants, address-burst group registers and target enums, NCI access mode enum, and PSYS GPDEV/FW IRQ offsets.

## Control Flow
The file has no executable flow. PCI, MMU, ISYS, PSYS, and firmware setup code use the constants to program hardware blocks and construct platform data.

## State And Persistence
There is no software state. Values describe memory-mapped hardware state.

## Dependencies And Integration Points
It depends on Linux bit helpers. It is one of the main hardware-contract headers used by `ipu6.c`, `ipu6-isys.c`, and `ipu6-mmu.c`.

## Risks And Test Signals
Hardware-generation assumptions are important. Wrong offsets can break firmware boot, MMU page-table programming, interrupts, or DMA routing. Tests should include firmware SPC boot, MMU init on ISYS and PSYS, ISYS CSI interrupts, PSYS firmware IRQs, and DMA capture integrity.
