# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda.h

## Purpose
Defines the common PLDA PCIe host-controller register interface, interrupt event model, state structures, platform hook contracts, exported helper prototypes, and small inline configuration helpers used by PLDA-based host drivers.

## Important APIs, Types, And Functions
Important constants cover bridge configuration registers, local interrupt masks/status, MSI address/status, ATR source/translation fields, and event IDs. Core types are `enum plda_int_event`, `struct plda_event_ops`, `struct plda_pcie_host_ops`, `struct plda_msi`, `struct plda_pcie_rp`, and `struct plda_event`. Inline helpers set default MSI values, enable root-port mode, set PCI class code, enable 64-bit prefetchable windows, disable LTR forwarding, disable functions, and write root-complex BARs.

## Control Flow
No standalone execution occurs here. The header defines the contract by which platform drivers customize common PLDA host flow: set fields in `plda_pcie_rp`, optionally supply `event_ops`, `event_irq_chip`, and `host_ops`, then call common host initialization and teardown.

## State And Persistence
The header describes persistent driver state stored per controller: device pointer, host bridge, irq domains, lock, MSI bitmap, register bases, event bitmap, and IRQ numbers. Inline helpers mutate persistent hardware configuration registers such as `GEN_SETTINGS`, `PCIE_PCI_IDS_DW1`, `PCIE_WINROM`, `PMSG_SUPPORT_RX`, `PCI_MISC`, and root BAR registers.

## Dependencies And Integration Points
It is included by `pcie-plda-host.c`, Microchip, and StarFive controller drivers. It relies on Linux PCI constants, irq domains, bit operations, and MMIO accessors available through including C files.

## Risks
Register bit definitions are shared ABI for multiple SoCs; a mistaken shift or mask affects all platform users. Event numbering bridges hardware bits and Linux irq domains, so changes require updating platform event mapping. Inline helpers assume the caller selected the correct function/register bank.

## Test Signals
Compile coverage across both PLDA platform drivers catches many declaration mismatches. Runtime validation comes from correct root-port class code, disabled unused functions, working MSI/INTx/event delivery, 64-bit prefetchable window behavior, and link enumeration on supported SoCs.
