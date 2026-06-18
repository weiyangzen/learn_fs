# sources/distributed-fs/ceph-client/drivers/edac/i3000_edac.c

## Purpose
This PCI EDAC driver supports Intel 3000/3010 memory hub controllers. It maps MCHBAR rank-boundary registers, determines channel interleaving, registers DDR2 DIMM/rank topology with EDAC, polls ECC status, and reports CE/UE events.

## Important APIs and Functions
`deap_pfn()`, `deap_offset()`, and `deap_channel()` decode the hardware DRAM Error Address Pointer registers. `i3000_get_error_info()` reads status, address, and syndrome registers with a second status read to detect CE/UE overwrite races. `i3000_process_error_info()` reports EDAC errors. `i3000_is_interleaved()` compares channel rank attributes/boundaries. `i3000_probe1()`, `i3000_init_one()`, and `i3000_remove_one()` manage device lifecycle.

## Control Flow
Init calls `opstate_init()` and registers a PCI driver, with fallback manual `pci_get_device()` probing when normal registration did not bind. Probe enables the PCI device, maps MCHBAR, reads channel DRA/DRB registers, determines one- versus two-channel EDAC layout, allocates an EDAC memory controller, fills csrow/channel DIMMs from cumulative rank boundaries, clears stale errors, registers EDAC, and creates a generic PCI parity controller. Polling reads error registers, clears status by writing ones, and reports UE or CE with PFN/offset/syndrome/channel.

## State and Persistence
Static state includes `mci_pdev`, `i3000_registered`, and optional `i3000_pci`. Per-controller EDAC state has no private allocation. Hardware state includes error-status bits and rank-boundary configuration.

## Dependencies and Integration
The driver depends on PCI config access, MMIO `ioremap`, EDAC memory-controller APIs, EDAC PCI generic parity support, and Intel PCI IDs.

## Risks
The source notes non-atomic register capture: CE can be overwritten by UE between reads, handled by emitting a synthetic "UE overwrote CE" report. The fallback registration path and static globals assume a narrow device model. `mci_pdev` reference handling must remain balanced across driver-registered and manually probed modes.

## Test Signals
Signals include correct DDR2 csrow/channel sizing from DRB values, interleaved versus asymmetric channel detection, CE/UE reports with decoded DEAP address fields, status clearing, generic PCI parity sysfs creation, and clean unload in both normal and fallback probe paths.
