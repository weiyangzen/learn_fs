# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.h

Declares the public interface and SoC data contract for the Tegra DFLL common driver.

`struct tegra_dfll_soc_data` supplies the OPP-owning device, maximum frequency, CVB table, regulator rail alignment, and optional clock-trimmer callbacks for initialization and voltage ranges. Exported prototypes cover registration/unregistration and runtime/system PM callbacks: `tegra_dfll_register()`, `tegra_dfll_unregister()`, `tegra_dfll_runtime_suspend/resume()`, and `tegra_dfll_suspend/resume()`.

The header owns no state, but its struct fields define the persistent SoC characterization used by `clk-dfll.c`. It depends on platform devices, reset types, and `cvb.h`. SoC-specific DFLL shim drivers include this header and pass initialized `tegra_dfll_soc_data` into the common driver.

Incorrect SoC data can make the common DFLL driver program unsafe voltages or rates. Test signals are compile coverage for all Tegra DFLL SoCs and runtime registration using valid CVB/alignment/trimmer data.
