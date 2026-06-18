# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v_asm.S

## Purpose
SPARC assembly wrappers around sun4v PCI hypervisor fast traps. They adapt C calling conventions to HV services for PCI config, IOMMU, MSI/MSIQ, message routing, and ATU IOTSB.

## Important APIs, Types, and Functions
Exports `pci_sun4v_iommu_map/demap/getmap`, `pci_sun4v_config_get/put`, `pci_sun4v_msiq_*`, `pci_sun4v_msi_*`, `pci_sun4v_msg_*`, and `pci_sun4v_iotsb_conf/bind/map/demap`. Each sets `%o5` to an `HV_FAST_PCI_*` operation and traps via `ta HV_FAST_TRAP`.

## Control Flow
Arguments arrive in outgoing registers. Some wrappers save output pointers in `%g1` before the trap, then store returned values to memory. Config get returns all ones on HV error; config put normalizes errors to `-1`; IOMMU map returns negative status on failure or mapped count on success.

## State and Persistence
No static state. The wrappers mutate HV-managed state and caller output memory only.

## Dependencies and Integration Points
Depends on `linux/linkage.h` and `asm/hypervisor.h`. Must stay ABI-compatible with `pci_sun4v.h` and `pci_sun4v.c`.

## Risks and Test Signals
Register ordering is the contract, so prototype drift is dangerous. Some wrappers store outputs even on nonzero status. Test via link success, sun4v PCI enumeration, DMA mapping, IOTSB setup, and MSI queue configuration.
