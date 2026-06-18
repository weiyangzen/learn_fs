# sources/distributed-fs/ceph-client/drivers/char/agp/alpha-agp.c

## Purpose
This file provides AGP backend support for Alpha platforms whose AGP/GART behavior is supplied by architecture machine-vector operations rather than a normal PCI chipset driver.

## Important APIs, Types, and Functions
Core functions are `alpha_core_agp_setup()`, `alpha_core_agp_vm_fault()`, `alpha_core_agp_fetch_size()`, `alpha_core_agp_configure()`, `alpha_core_agp_cleanup()`, `alpha_core_agp_tlbflush()`, `alpha_core_agp_enable()`, `alpha_core_agp_insert_memory()`, and `alpha_core_agp_remove_memory()`. The bridge driver is `alpha_core_agp_driver`, and VM ops are `alpha_core_agp_vm_ops`.

## Control Flow
Module init checks `agp_off`, obtains `alpha_mv.agp_info()`, runs architecture setup, fills a fixed aperture descriptor, allocates a fake `pci_dev`, allocates an AGP bridge, attaches Alpha-specific ops and VM fault handler, then registers the bridge. Memory insertion/removal delegates to `agp->ops->bind()`/`unbind()` and flushes the Alpha PCI TBI.

## State and Persistence Behavior
State lives in architecture-provided `alpha_agp_info`, a fake PCI device, `alpha_bridge`, and generic bridge fields. VM faults translate aperture bus addresses through `agp->ops->translate()` and pin the backing page.

## Dependencies and Integration Points
It depends on Alpha machine vectors, `alpha_agp_info`, PCI hose data, generic AGP backend, and architecture TLB invalidation via `alpha_mv.mv_pci_tbi()`.

## Risks
The fake PCI device must be sufficient for generic AGP users. VM fault translation returns SIGBUS on missing mappings; wrong architecture translate behavior can expose incorrect physical pages. Cleanup assumes `alpha_bridge` was initialized. The bridge is fixed-size and `cant_use_aperture` is set, reflecting architecture constraints that generic users must respect.

## Test Signals
Boot Alpha systems with AGP machine-vector support, verify bridge registration, AGP enable programming, aperture mmap faults translating to correct pages, bind/unbind operations, TBI flushes, and clean module unload.
