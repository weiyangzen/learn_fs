# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7870.c

## Purpose

`clk-exynos7870.c` provides Common Clock Framework support for the Samsung Exynos7870 SoC. It is a data-driven platform driver that describes the Exynos7870 CMU blocks and registers the matching `struct samsung_cmu_info` for each device-tree compatible. Compared with older `CLK_OF_DECLARE()`-only Samsung clock drivers, this file uses a single platform driver and an OF match table for most CMUs.

The covered CMUs are `MIF`, `DISPAUD`, `FSYS`, `G3D`, `ISP`, `MFCMSCL`, and `PERI`. `MIF` is the central source and distributor for memory/bus, media, display/audio, file-system, ISP, MFC/MSCL, and peripheral clocks. Other CMUs consume MIF outputs through user muxes and expose local PLLs, dividers, and gates for display/audio, USB/MMC/storage, GPU, camera/ISP, media codec/scaler, and low-speed peripherals.

## Important APIs, Types, and Tables

The file uses the Samsung ARM64 clock helper declared in `clk-exynos-arm64.h`. The key registration API is `exynos_arm64_register_cmu(dev, dev->of_node, info)`, called from `exynos7870_cmu_probe()`. `of_device_get_match_data(dev)` selects the correct `struct samsung_cmu_info` from `exynos7870_cmu_of_match`.

Each CMU is represented by a `struct samsung_cmu_info`: `mif_cmu_info`, `dispaud_cmu_info`, `fsys_cmu_info`, `g3d_cmu_info`, `isp_cmu_info`, `mfcmscl_cmu_info`, and `peri_cmu_info`. These descriptors collect register-offset arrays and the relevant `PLL`, `MUX`, `DIV`, `GATE`, `FRATE`, and `FFACTOR` tables. Clock IDs come from `<dt-bindings/clock/samsung,exynos7870-cmu.h>`.

Notable hardware descriptions include three MIF PLLs (`fout_mif_mem_pll`, `fout_mif_media_pll`, `fout_mif_bus_pll`), local PLLs for display/audio, USB FSYS, G3D, and ISP, fixed-rate MIPI/USB/audio clocks, and a large set of MIF output gates. Many gates use the `gout_...` naming style, matching the Exynos7870 clock binding and downstream consumer expectations.

## Control Flow

`core_initcall(exynos7870_cmu_init)` registers `exynos7870_cmu_driver` early. When a platform device with a compatible such as `samsung,exynos7870-cmu-mif` or `samsung,exynos7870-cmu-peri` probes, `exynos7870_cmu_probe()` retrieves the matched CMU descriptor and hands it to `exynos_arm64_register_cmu()`. The Samsung ARM64 helper maps the node's register range, registers PLL/mux/divider/gate/fixed clocks, and installs the OF clock provider.

At runtime, the CCF controls individual clocks through Samsung-provided clock operations. Muxes select parents using the declared parent-name arrays, dividers program rate divisors, and gates toggle bits in the declared CMU registers. Rate changes propagate through `CLK_SET_RATE_PARENT` where enabled. The platform driver has no remove path; these CMUs are expected to be permanent boot-time providers.

## State and Persistence Behavior

Driver state is almost entirely static and hardware-backed. The CMU descriptors and register lists are `__initconst`; after init, the shared Samsung registration code owns the clock hardware state. The only mutable state is in hardware CMU registers and the CCF structures created during registration. There is no file persistence, firmware state store, or dynamically updated private data in this source file.

The `..._clk_regs` arrays are important for state retention across suspend/resume and for safe registration of register-backed clocks. Many Exynos7870 gates are marked `CLK_IS_CRITICAL`, especially MIF mux/gate chains, PPMU, HSI2C, ADC, display, G3D, ISP, and MFCMSCL paths. Those flags prevent the common unused-clock cleanup from disabling clocks required for bus fabric, register access, or always-on hardware.

## Dependencies and Integration Points

The source depends on the platform bus, OF match data, Linux CCF, Samsung `clk.h`, Samsung ARM64 CMU helper code, and the Exynos7870 DT binding. Its compatible strings are:

- `samsung,exynos7870-cmu-mif`
- `samsung,exynos7870-cmu-dispaud`
- `samsung,exynos7870-cmu-fsys`
- `samsung,exynos7870-cmu-g3d`
- `samsung,exynos7870-cmu-isp`
- `samsung,exynos7870-cmu-mfcmscl`
- `samsung,exynos7870-cmu-peri`

The integration pattern is hierarchical. MIF exports clocks such as `gout_mif_cmu_fsys_bus`, `gout_mif_cmu_peri_spi0`, and `gout_mif_cmu_isp_cam`; FSYS, PERI, ISP, DISPAUD, MFCMSCL, and G3D consume those as user-mux parents. This means DT node presence and probe timing must make upstream providers available before dependent consumer clocks are resolved.

## Risks and Edge Cases

The most important risk is parent-chain correctness. A local CMU often depends on a MIF gate, a user mux, and sometimes a local PLL gate before reaching a leaf clock. Any wrong parent string, ID, bit offset, or critical flag can break a whole peripheral domain. The file also has repeated register offsets with distinct semantic names, such as mux and gate aliases sharing the same address; that is intentional for this hardware but increases maintenance risk.

Another risk is broad use of `CLK_IS_CRITICAL`. Some clocks clearly guard bus access, but critical flags can also hide missing runtime PM integration or keep power domains active. Removing or changing those flags requires hardware boot, idle, and suspend testing. Conversely, dropping one incorrectly can cause hard hangs during unused-clock cleanup.

PLL rate tables are sparse or absent for most PLLs. That is acceptable when firmware or bootloader leaves stable rates and the kernel only gates/divides, but it limits safe dynamic rate programming. Fixed-rate clocks for MIPI, USB, and audio assume specific board/PHY frequencies. Binding drift is also a risk because clock IDs and `gout_...` names must match DTS consumers.

## Test Signals

Build tests should cover the Exynos7870 binding header and the platform-driver path. Boot tests should verify that all seven compatible nodes probe, no missing-parent warnings appear, and clock providers are available before dependent devices. `clk_summary` should show MIF roots feeding DISPAUD, FSYS, G3D, ISP, MFCMSCL, and PERI user muxes.

Peripheral validation should include display/audio clocking, MMC and USB operation, GPU/G3D access if enabled, ISP/camera sensor clock paths, MFC/MSCL media paths, UART/SPI/I2C/PWM/MCT/WDT/TMU clocks, and ADC/HSI2C paths marked critical. Suspend/resume and idle tests are especially valuable because this file enumerates large register-save lists and many always-on gates.
