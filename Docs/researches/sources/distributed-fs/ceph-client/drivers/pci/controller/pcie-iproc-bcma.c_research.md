# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-bcma.c

## Purpose

`pcie-iproc-bcma.c` is the BCMA bus wrapper for Broadcom iProc PCIe controllers. It adapts a BCMA core into the common `iproc_pcie` host-controller implementation by supplying MMIO base, physical base, a fixed 128 MiB memory window, an IRQ mapping callback, and BCMA driver registration.

## Important APIs, Types, And Functions

- `iproc_bcma_pcie_probe()` allocates the PCI host bridge, initializes `struct iproc_pcie`, creates the bridge memory resource from BCMA address data, requests bus resources, installs `map_irq`, stores driver data, and calls `iproc_pcie_setup()`.
- `iproc_bcma_pcie_map_irq()` maps PCI legacy IRQs to BCMA core IRQ line 5.
- `bcma_pcie2_fixup_class()` is an early PCI fixup for Broadcom device IDs `0x8011` and `0x8012`, forcing the class to normal PCI bridge because hardware reports the wrong class.
- `iproc_bcma_pcie_remove()` delegates teardown to `iproc_pcie_remove()`.

## Control Flow

When a BCMA core matching `BCMA_CORE_NS_PCIEG2` probes, the wrapper allocates host bridge private data, sets type `IPROC_PCIE_PAXB_BCMA`, uses `bdev->io_addr` and `bdev->addr` as controller register mappings, constructs a fixed memory resource from `addr_s[0]`, and calls the common core. From that point the common iProc file controls reset, link check, config access, MSI, and bus scanning.

## State And Persistence

The wrapper only persists the common `struct iproc_pcie` in BCMA driver data and the host bridge resource list. The fixed memory window is runtime kernel state and is released through devm/resource cleanup and common remove.

## Dependencies And Integration Points

It depends on the BCMA bus API, PCI host bridge allocation, `devm_request_pci_bus_resources()`, and the shared `pcie-iproc.h` interface. It has no OF parsing and no platform clocks/resets of its own.

## Risks And Edge Cases

- The memory aperture is hard-coded to 128 MiB from `bdev->addr_s[0]`; boards requiring a different aperture are not represented here.
- If `bdev->io_addr` is missing, probe fails with `-ENOMEM`.
- Legacy IRQ routing assumes BCMA IRQ line 5.
- The class fixup is device-ID-specific; unlisted BCMA variants with similar class bugs would remain misclassified.

## Test Signals

Expected signals are BCMA probe success, requested memory resource coverage, root bridge class fixed for IDs `0x8011/0x8012`, functional legacy INTx via BCMA IRQ 5, downstream enumeration through `iproc_pcie_setup()`, and clean common teardown on BCMA remove.
