# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.h

## Purpose
Declares the sun4v PCI hypervisor-call wrapper interface used by C code for config space, IOMMU, MSI/MSIQ, message routing, and ATU IOTSB operations.

## Important APIs, Types, and Functions
IOMMU calls are `pci_sun4v_iommu_map()`, `pci_sun4v_iommu_demap()`, and `pci_sun4v_iommu_getmap()`. Config accessors are `pci_sun4v_config_get()` / `pci_sun4v_config_put()`. MSI queue, MSI, and message functions get/set validity, state, queue mapping, heads, and tails. ATU v2 functions configure, bind, map, and demap IOTSB entries.

## Control Flow
C code calls these prototypes; assembly wrappers execute `HV_FAST_TRAP` and write output pointer values from HV return registers. Callers must interpret each function's return convention.

## State and Persistence
No local state. Functions mutate hypervisor-owned PCI/IOMMU/MSI state and caller-provided outputs. No persistence.

## Dependencies and Integration Points
Depends on `u64` and must match assembly symbols in `pci_sun4v_asm.S`. Used by `pci_common.c` and `pci_sun4v.c`.

## Risks and Test Signals
Return conventions differ across calls. Prototype/assembly ABI mismatches cause silent corruption. Test through successful config access, DMA map/demap counts, IOTSB setup, and MSI queue operations.
