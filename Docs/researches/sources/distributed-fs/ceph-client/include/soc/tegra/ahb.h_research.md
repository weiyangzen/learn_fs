# sources/distributed-fs/ceph-client/include/soc/tegra/ahb.h

Purpose: declares the Tegra AHB helper used to enable SMMU translation support through the AHB controller.

Important APIs/types/functions: exports `tegra_ahb_enable_smmu(struct device_node *ahb)`.

Control flow: Tegra SMMU code locates the AHB device node and calls this helper so the AHB driver can configure SMMU-related AHB registers.

State and persistence: the persistent state is AHB controller configuration enabling SMMU behavior. The header owns no state.

Dependencies and integration: implemented by `drivers/amba/tegra-ahb.c` and consumed by `drivers/iommu/tegra-smmu.c`; requires `struct device_node` from Open Firmware headers through includers.

Risks: failure to enable SMMU at the AHB level can leave IOMMU translations ineffective or devices inaccessible. Test signals include Tegra SMMU probe, DMA/IOMMU mapping tests, and boot on Tegra platforms using AHB-mediated SMMU enablement.
