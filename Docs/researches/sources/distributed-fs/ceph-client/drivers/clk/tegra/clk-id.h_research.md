# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-id.h

Defines a shared `enum clk_id` for Tegra clocks used across multiple SoC clock initialization files.

The enum lists root clocks, PLLs, PLL outputs, bus clocks, peripheral clocks, audio sync clocks, display/XUSB/SATA clocks, and newer Tegra210-era IDs, ending with `tegra_clk_max`. It has no functions; its ordering is the API.

There is no runtime state. The enum values are compile-time indexes into Tegra clock arrays and registration tables. It is included by Tegra clock setup code that stores `struct clk *` or `clk_hw` by ID. The values must remain consistent across files that share clock arrays.

Changing enum order can break clock registration silently by indexing the wrong slot. Additions should appear before `tegra_clk_max` and be coordinated with all SoC tables. Test signals are build coverage and boot-time clock lookup for every ID referenced by SoC code.
