# sources/distributed-fs/ceph-client/drivers/phy/tegra/Makefile

Purpose: builds Tegra XUSB composite objects and the standalone Tegra194 P2U object.

Important APIs, types, and functions: `phy-tegra-xusb.o` includes common `xusb.o` plus SoC-specific `xusb-tegra124.o`, `xusb-tegra210.o`, or `xusb-tegra186.o` based on ARCH symbols; `CONFIG_PHY_TEGRA194_P2U` builds `phy-tegra194-p2u.o`.

Control flow: kernel build composition only.

State and persistence: none.

Dependencies and integration points: ties multiple SoC implementations into one XUSB module and builds P2U separately.

Risks: Tegra186 implementation is reused for Tegra194 and Tegra234, so SoC-specific differences must be handled in that source. Multiple ARCH symbols can add multiple object files to the composite.

Test signals: build matrices for Tegra124/132/210/186/194/234 and standalone P2U module builds.
