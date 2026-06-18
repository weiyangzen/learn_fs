# sources/distributed-fs/ceph-client/arch/mips/pci/pci-ar724x.c

## Purpose
Implements AR724x PCIe host controller support, including local/root config access, endpoint config access, link bring-up, resources, and one-line chained IRQ handling.

## Important APIs, Types, And Functions
Defines `struct ar724x_pci_controller`, `ar724x_pci_ops`, `ar724x_pci_probe`, `ar724x_pci_hw_init`, `ar724x_pci_check_link`, IRQ chip callbacks, and `postcore_initcall(ar724x_pci_init)`.

## Control Flow
Probe maps control, endpoint config, and root-complex config windows, collects I/O and memory resources, optionally performs full PCIe reset/PLL/LTSSM initialization, records link status, installs one IRQ, initializes local command bits, and registers the controller. Config reads/writes allow only root bus slot 0/function 0 and endpoint bus slot 0, returning not found when link is down. Local writes program CRP config space; endpoint accesses use `devcfg_base` with BAR0 workaround handling for AR7240. IRQ mask/unmask uses the controller INT_MASK/STATUS registers.

## State And Persistence
Per-controller state stores mapped bases, resources, irq, irq_base, and `link_up`. Hardware reset/PLL/app-control, interrupt, and config registers persist for the boot session.

## Dependencies And Integration Points
Depends on ATH79 reset and PLL helpers, named platform resources `ctrl_base`, `cfg_base`, `crp_base`, `io_base`, `mem_base`, and PCI/IRQ core APIs.

## Risks And Edge Cases
The driver intentionally supports only one endpoint slot. Link-down handling hides endpoint config. BAR0 workaround and local/endpoint access distinction are hardware-specific. Fixed 100 ms link wait may be marginal on slow boards.

## Test Signals
AR724x PCIe board boot, link-up/link-down probes, endpoint BAR programming, interrupt delivery, and config read/write tests are useful.
