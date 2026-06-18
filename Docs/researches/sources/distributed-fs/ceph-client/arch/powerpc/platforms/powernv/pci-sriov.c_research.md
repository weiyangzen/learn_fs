## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-sriov.c

### Purpose
`pci-sriov.c` adds PowerNV-specific SR-IOV support by reshaping VF BAR resources, allocating one PE per VF, programming M64 windows, shifting VF BARs to match allocated PE numbers, and tearing everything down on disable.

### Important APIs, Types, And Functions
Public hooks are `pnv_pci_ioda_fixup_iov()`, `pnv_pci_iov_resource_alignment()`, `pnv_pcibios_sriov_enable()`, and `pnv_pcibios_sriov_disable()`. Internal helpers include `pnv_pci_ioda_fixup_iov_resources()`, `pnv_pci_vf_assign_m64()`, `pnv_ioda_map_m64_segmented()`, `pnv_ioda_map_m64_single()`, `pnv_pci_vf_resource_shift()`, `pnv_ioda_setup_vf_PE()`, and `pnv_ioda_release_vf_PE()`.

### Control Flow
PF fixup allocates `struct pnv_iov_data`, rejects unsupported non-M64 VF BARs, expands segmented VF BAR resources to `vf_bar_size * total_pe_num`, and records single-window mode for very large VF BARs. Resource alignment returns the expanded size for segmented windows. Enabling SR-IOV verifies IODA2-style PHB support, allocates a contiguous PE range, programs segmented or single M64 windows for each VF BAR, shifts BAR resources by the base PE when needed, configures each VF PE/RID, links VF PDNs, and sets up DMA for each VF PE. Disabling releases VF PEs/DMA, unshifts resources, disables used M64 windows, and removes VF PDNs.

### State, Persistence, And Dependencies
State is stored in `pdev->dev.archdata.iov_data`: number of VFs, contiguous PE array, per-BAR single-mode flags, shift flag, used M64 BAR bitmap, and reserved hole resources. Firmware persists M64 BAR programming and PE/RID mappings. Dependencies include the generic PCI SR-IOV hooks, PowerNV PE allocation/configuration, OPAL M64 MMIO calls, PCI resource management, and IODA2 DMA setup.

### Integration Points
`pci-ioda.c` installs these hooks in `ppc_md` when `CONFIG_PCI_IOV` is enabled. VF `pcibios_device_add()` fixups attach created VF `pci_dev`s back to their preallocated PEs.

### Risks
The order of arguments in the single-mode call site must match `pnv_ioda_map_m64_single(phb, pe_num, window_id, start, size)`; confusing PE and window IDs would map the wrong hardware target. BAR shifting creates reserved holes and must be fully undone. Enable failure paths must free contiguous PE runs and M64 windows. The design only supports M64 VF BARs and IODA2-style OPAL APIs, so 32-bit/non-prefetchable VF BARs disable IOV resources.

### Test Signals
Test PFs with unsupported VF BAR flags, small segmented BARs, large single-mode BARs, M64 window exhaustion, contiguous PE allocation failure, BAR shift bounds and hole reservation, enable failure unwinding at each stage, VF PDN association, DMA setup per VF, disable cleanup, and repeated enable/disable cycles.
