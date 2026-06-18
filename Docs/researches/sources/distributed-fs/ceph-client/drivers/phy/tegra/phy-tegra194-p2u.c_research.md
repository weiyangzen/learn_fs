# sources/distributed-fs/ceph-client/drivers/phy/tegra/phy-tegra194-p2u.c

Purpose: NVIDIA Tegra194/Tegra234 P2U (PIPE to UPHY) generic PHY driver that applies PCIe PIPE-side tuning at power-on and L2 exit rate-change calibration.

Important APIs, types, and functions: `struct tegra_p2u` stores MMIO base, optional skip-size-protection flag, and match data. `struct tegra_p2u_of_data` carries `one_dir_search` for Tegra234. `tegra_p2u_power_on()` programs skip size protection, Gen3/Gen4 preset EQ training, RX debounce timer, and optionally disables Gen4 fine-grain search-twice. `tegra_p2u_calibrate()` enables L2 exit rate change. Probe maps named `ctl` resource, reads `nvidia,skip-sz-protect-en`, creates one PHY, and registers simple xlate.

Control flow: platform probe selects match data, maps registers, records DT boolean, creates PHY. Consumers call power-on before using the link; they may call calibrate to enable L2 exit behavior. There is no power-off path.

State and persistence: only the DT boolean and match data are cached. Hardware tuning bits persist until reset. Tegra194 and Tegra234 differ by `one_dir_search`.

Dependencies and integration points: generic PHY framework, platform MMIO resource named `ctl`, Tegra PCIe controller consumers, compatibles `nvidia,tegra194-p2u` and `nvidia,tegra234-p2u`.

Risks: no explicit reset/clock management, assuming parent/controller handles those resources. No power-off means settings are not reverted. Optional skip-size-protection is board-specific and needed for two-retimer topologies; incorrect DT can affect link training.

Test signals: PCIe Gen3/Gen4 link training, retimer topology tests with skip-size protection, L2 exit behavior after calibrate, Tegra234 directional search register readback, and resource-name DT validation.
