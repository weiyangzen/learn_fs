# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_sun4v.c

## Purpose
sun4v PCI controller, DMA mapping, IOMMU/ATU, MSI, and bus scanning support. Most hardware operations are mediated by hypervisor calls implemented in `pci_sun4v_asm.S`.

## Important APIs, Types, and Functions
`pci_sun4v_probe()` negotiates PCI/ATU HV APIs, installs `sun4v_dma_ops`, allocates per-CPU IOMMU batch pages and PBM/IOMMU/ATU state, then calls `pci_sun4v_pbm_init()`. DMA ops implement coherent, single, and scatterlist mappings using legacy IOMMU or 64-bit ATU IOTSB. `iommu_batch_*()` batches HV map calls. `pci_sun4v_iommu_init()` initializes legacy IOMMU bitmaps and imports OBP mappings. `pci_sun4v_atu_init()` configures 64-bit IOTSB. MSI functions implement `sparc64_msiq_ops` through HV calls.

## Control Flow
The driver matches `SUNW,sun4v-pci`. First probe negotiates HV groups and installs DMA ops. Probe derives `devhandle` from `reg`, initializes per-CPU page lists once, allocates state, and initializes the PBM. DMA paths choose legacy IOMMU for 32-bit-compatible masks and ATU for wider masks when available. MSI allocates queue memory, registers it with HV, validates config, and dispatches through common MSI code.

## State and Persistence
Runtime state includes negotiated HV API versions, global `dma_ops`, per-CPU batches, PBM root linkage, IOMMU/ATU bitmaps and IOTSB tables, MSI queue memory, and OF-derived ranges. OBP mappings may be imported or demapped. No persistent storage.

## Dependencies and Integration Points
Uses Linux DMA map ops, PCI, MSI, OF/platform, percpu, IRQ, SPARC hypervisor APIs, `pci_common.c`, `pci_msi.c`, and `pci_sun4v.h`.

## Risks and Test Signals
Scatterlist partial failure has an explicit missing-demap concern. ATU failure silently falls back to legacy IOMMU. Per-CPU batch allocation lacks full unwind. MSI queue heads are byte offsets. Test via HV API logs, PBM NUMA/resource logs, DMA with 32/64-bit masks, ATU fallback, and MSI dispatch.
