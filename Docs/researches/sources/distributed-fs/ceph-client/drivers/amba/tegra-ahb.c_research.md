# sources/distributed-fs/ceph-client/drivers/amba/tegra-ahb.c

### Purpose
`tegra-ahb.c` programs NVIDIA Tegra AHB arbitration, gizmo, and prefetch registers for performance and SMMU coordination, and saves/restores those registers across suspend.

### Important APIs, Types, And Functions
The platform driver is `tegra_ahb_driver`. Key helpers are `tegra_ahb_gizmo_init()`, `tegra_ahb_probe()`, suspend/resume callbacks, `gizmo_readl()`, `gizmo_writel()`, and, with `CONFIG_TEGRA_IOMMU_SMMU`, exported `tegra_ahb_enable_smmu(struct device_node *dn)`.

### Control Flow
Probe allocates `struct tegra_ahb` with a flexible context array, fetches MMIO resource 0, corrects legacy DT base addresses ending in low byte `0x4`, maps registers, stores drvdata, and initializes arbitration/prefetch state. Suspend copies all listed AHB gizmo registers into `ctx`; resume writes them back. SMMU enable finds the AHB device by OF node and sets `SMMU_INIT_DONE`.

### State, Persistence, And Dependencies
State includes MMIO base, device pointer, and saved register context. Hardware register state controls arbitration priorities, USB/AHBDMA prefetch, immediate modes, write splitting, and SMMU init indication. Dependencies include platform driver core, OF matching, devm resource mapping, PM ops, and optional Tegra SMMU integration.

### Integration Points
The driver binds to `nvidia,tegra30-ahb` and `nvidia,tegra20-ahb`. It coordinates with Tegra USB/AHBDMA traffic behavior and the Tegra SMMU driver through the exported init-done API.

### Risks
The base-address workaround mutates the resource start in place for legacy DTs, which is intentional but broad for affected resources. Incorrect register programming can degrade bus fairness or USB/DMA throughput. Suspend context must cover every register modified by init or platform firmware.

### Test Signals
Test probe on legacy and corrected DT bases, readback of priority/prefetch bits, USB/DMA throughput, SMMU init-done handoff, suspend/resume register restoration, and module alias/platform binding.
