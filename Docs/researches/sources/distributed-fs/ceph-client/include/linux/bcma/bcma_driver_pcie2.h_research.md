# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pcie2.h

## Purpose
Defines BCMA PCIe Gen2 core registers, interrupt/window/MSI/EQ state, memory/ECC/status registers, private config registers, and simple access macros.

## Important APIs, types, and functions
- Register constants cover clock control, root/endpoint power management, LTR/OBFF, error status, AXI config, MDIO, interrupt lazy/masks/status, MSI and event queues, inbound/outbound address windows, memory ECC, link/reset/strap status, and SPROM.
- `struct bcma_drv_pcie2` stores the core pointer and request size.
- Access and bit helpers wrap `bcma_read/write16/32()`, `bcma_set32()`, and `bcma_mask32()`.

## Control flow and state
PCIe2 setup code configures reset/clock behavior, power states, link/LTR behavior, interrupts/MSI, and inbound/outbound mappings. Runtime code reads link/error/ECC status and manipulates masks or windows through the macros.

## State and persistence behavior
State is live PCIe core hardware state. SPROM window reflects persistent device configuration. `reqsize` is runtime driver state for PCIe request sizing.

## Dependencies and integration points
Included by `bcma.h` and used by BCMA PCIe2 host/endpoint support and drivers that need Gen2-specific register access.

## Risks
Inbound/outbound mapping and MSI/EQ registers are easy to misprogram and can break DMA or interrupts. Reset/clock flags can affect link training and survivability across PERST. LTR settings must match platform power policy.

## Test signals
Validate PCIe link training, config access, DMA windows, MSI delivery, interrupt masks, low-power transitions, ECC/error reporting, and SPROM access on PCIe2 hardware.
