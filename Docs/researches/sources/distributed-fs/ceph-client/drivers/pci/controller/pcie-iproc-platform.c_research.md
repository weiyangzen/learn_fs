# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-platform.c

## Purpose

`pcie-iproc-platform.c` is the OF platform wrapper for Broadcom iProc PCIe controllers. It maps controller registers, reads DT properties that select outbound/inbound mapping behavior and PHYs, chooses the iProc wrapper type from compatible data, and delegates host setup, remove, and shutdown to the shared iProc core.

## Important APIs, Types, And Functions

- `iproc_pcie_of_match_table` maps `brcm,iproc-pcie`, `brcm,iproc-pcie-paxb-v2`, `brcm,iproc-pcie-paxc`, and `brcm,iproc-pcie-paxc-v2` to `enum iproc_pcie_type`.
- `iproc_pltfm_pcie_probe()` allocates host bridge private state, maps resource 0 with `devm_pci_remap_cfgspace()`, reads optional outbound mapping properties, detects inbound mapping via `dma-ranges`, gets optional PHY, disables legacy IRQ mapping for PAXC types, and calls `iproc_pcie_setup()`.
- `iproc_pltfm_pcie_remove()` and `iproc_pltfm_pcie_shutdown()` delegate to `iproc_pcie_remove()` and `iproc_pcie_shutdown()`.

## Control Flow

Probe selects the controller type from OF match data, converts address resource 0 to a resource, maps it as config/MMIO space, and stores the physical base. If `brcm,pcie-ob` is present, `brcm,pcie-ob-axi-offset` becomes mandatory and `need_ob_cfg` is set. Presence of `dma-ranges` requests inbound mapping setup in the core. Optional PHY acquisition is performed before setup. PAXC controllers clear `map_irq` because they do not support legacy INTx. The common core then performs revision-specific setup, mapping, link checks, MSI handling, and host probing.

## State And Persistence

The wrapper stores all runtime state in `struct iproc_pcie` allocated as host bridge private data. DT-derived flags (`need_ob_cfg`, `need_ib_cfg`, `ob.axi_offset`, `type`, `phy`) persist for the common setup path. No persistent storage is used.

## Dependencies And Integration Points

This file depends on OF address parsing, OF PCI properties, PHY framework, platform resources, `devm_pci_alloc_host_bridge()`, `devm_pci_remap_cfgspace()`, and the exported functions from `pcie-iproc.c`. It relies on `pcie-iproc.h` for the shared state contract.

## Risks And Edge Cases

- `brcm,pcie-ob` without `brcm,pcie-ob-axi-offset` is a hard probe failure.
- The inbound mapping decision is a boolean based on `dma-ranges`; malformed ranges fail later in common mapping.
- `of_match_ptr()` around the match table means non-OF builds need care, though this driver is OF-oriented.
- PAXC disables only legacy IRQ mapping at this wrapper level; MSI steering and PAXC quirks are handled later and must remain consistent with selected type.

## Test Signals

Exercise each compatible string, with and without `brcm,pcie-ob`, missing `brcm,pcie-ob-axi-offset`, valid and invalid `dma-ranges`, optional PHY probe deferral, PAXC legacy IRQ absence, shutdown PERST assertion, and successful downstream enumeration through `iproc_pcie_setup()`.
