# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.c

Purpose: platform and host1x client driver for Tegra 3D graphics engines across Tegra20/30/114.

Important APIs/functions: `gr3d_probe()` obtains clocks/resets, initializes power domains, builds the host1x DRM client, registers it, and populates address-register bitmap. `gr3d_init()` obtains a host1x channel and syncpoint, attaches IOMMU, and registers with Tegra DRM. `gr3d_exit()` unregisters and tears resources down. `gr3d_is_addr_reg()` classifies address-bearing 3D registers for firewall use. Power helpers handle legacy powergate sequencing when DT lacks generic power domains and support one or two 3D domains/clocks.

Control flow and state: `struct gr3d` stores a shared channel, SoC-specific clock/reset counts, optional PM domain list, and address-register bitmap. Runtime resume acquires resets, enables clocks, deasserts resets, and enables autosuspend; suspend stops the channel, asserts resets, disables clocks, and releases resets.

Dependencies/integration: uses host1x, Tegra PMC legacy powergate API, PM domains/OPP, reset bulk APIs, runtime PM, IOMMU, and Tegra DRM submit.

Risks: legacy power handling has SoC/DT-dependent branches and needs clock/reset balancing. Address-register coverage is large; omissions affect firewall security. Tegra20 single-clock handling intentionally treats 3D1 specially.

Test signals: probe on each compatible, runtime PM cycles, simple 3D submit, invalid address writes, and DT variants with/without generic power domains.
