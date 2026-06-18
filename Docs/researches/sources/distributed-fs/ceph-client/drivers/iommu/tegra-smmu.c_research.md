# sources/distributed-fs/ceph-client/drivers/iommu/tegra-smmu.c

Purpose: Implements the NVIDIA Tegra memory-controller SMMU as a Linux IOMMU provider. It owns ASID allocation, page-directory/page-table programming, SWGROUP/client enable bits, device-tree fwspec parsing, IOMMU group creation, debugfs visibility, and registration of `tegra_smmu_ops`.

Important APIs/types/functions: `struct tegra_smmu`, `struct tegra_smmu_as`, `struct tegra_smmu_group`, `tegra_smmu_probe()`, `tegra_smmu_remove()`, `tegra_smmu_attach_dev()`, `tegra_smmu_identity_attach()`, `tegra_smmu_map()`, `tegra_smmu_unmap()`, `tegra_smmu_iova_to_phys()`, `tegra_smmu_probe_device()`, `tegra_smmu_of_xlate()`, and debugfs show handlers. Register helpers wrap `readl`/`writel`; page table helpers allocate second-level tables and flush PTC/TLB state.

Control flow: Probe initializes masks from SoC capabilities, enables PTC/TLB/SMMU hardware, enables the Tegra AHB SMMU path, and registers an `iommu_device`. Device probe walks `iommus` phandles, stores the SMMU in `dev_iommu_priv`, and adds SWGROUP IDs. Attaching a translated domain prepares the address space once, maps the page directory for DMA, allocates an ASID, loads PTB registers, then enables each SWGROUP/client. Identity attach disables old SWGROUPs and decrements the AS use count.

State and persistence: Runtime state is in hardware registers, an ASID bitmap, group list, and per-domain page directory/table arrays. Page-table lifetime is reference-counted per PDE on unmap, but `tegra_smmu_domain_free()` still has a TODO for freeing page directory and page tables, making domain teardown a risk area.

Dependencies/integration: Integrates with `linux/iommu`, `soc/tegra/mc`, `soc/tegra/ahb`, OF, PCI grouping, DMA mapping, `iommu-pages`, sysfs, and optional debugfs. It assumes Tegra MC SoC tables provide SWGROUP/client register metadata.

Risks and test signals: Test attach/detach across multiple SWGROUP IDs, ASID exhaustion, 64-bit DMA address rejection, concurrent map allocation under the spinlock, identity default-domain behavior, debugfs output, and repeated domain allocate/free cycles to expose the unfinished cleanup path.
