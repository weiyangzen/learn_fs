# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-dove.c

Purpose: this is the Dove SoC pinctrl driver, including both ordinary MPP nibble muxing and several Dove-specific mux controls spread across PMU, MPP4, global configuration, SSP, TWSI, NAND, and audio registers.

Important APIs, types, and functions: custom get/set helpers include `dove_pmu_mpp_ctrl_get/set()`, `dove_mpp4_ctrl_get/set()`, `dove_nand_ctrl_get/set()`, `dove_audio0_ctrl_get/set()`, `dove_audio1_ctrl_get/set()`, and `dove_twsi_ctrl_get/set()`. `dove_audio1_ctrl_gpio_req()` and `dove_audio1_ctrl_gpio_dir()` implement special GPIO request/direction semantics for MPP52-57. `dove_mpp_controls[]` mixes unnamed per-pin controls with named grouped controls such as `mpp_camera`, `mpp_sdio0`, `mpp_audio1`, `mpp_nand`, `audio0`, and `twsi`.

Control flow: probe gets and enables the PDMA clock, maps the base MPP resource, allocates control data, maps MPP4 and PMU resources or falls back to hardcoded offsets, obtains `marvell,dove-global-config` syscon or creates an MMIO regmap fallback, warns if firmware omitted resources, and calls `mvebu_pinctrl_probe()`. Runtime muxing can set standard MPP nibbles, PMU-backed function values with `CONFIG_PMU`, grouped GPIO/function selector bits, and multi-bit audio/TWSI combinations.

State and persistence behavior: static globals store `mpp4_base`, `pmu_base`, `gconfmap`, and `clk`. Register state persists across the involved MMIO and syscon blocks. There is no remove path disabling the clock and no suspend/resume in this file.

Dependencies and integration points: dependencies include the MVEBU core, clock framework, MMIO resources, optional legacy hardcoded register layout, regmap/syscon, and global config compatible lookup. Integration is broad: camera, SDIO, SPI, UART1, NAND, PMU wake/power pins, audio0/audio1, SSP, TWSI, SATA, LCD, and GPIO ranges 0-71.

Risks and test signals: fallback hardcoded resources preserve old DTBs but can hide firmware bugs. Several `regmap_read()` calls ignore errors. Audio1 GPIO availability depends on the active compound mode and intentionally does not force GPIO on request. Test modern DT resources versus fallback, PMU functions on MPP0-15, grouped selectors for camera/SDIO/SPI/UART/NAND, audio1 GPIO subsets, TWSI option bits, and PDMA clock availability.
