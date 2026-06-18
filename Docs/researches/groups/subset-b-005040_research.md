# Research Report: subset-b-005040

This grouped report covers Rockchip USB/USBDP PHY drivers and Samsung PHY build glue, video, PCIe, USB2, USB DRD, SATA, and UFS PHY code in the Ceph-client kernel source mirror. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usb.c

Purpose: Implements the older Rockchip USB 2.0 PHY provider for rk3066a, rk3188, and rk3288 GRF-backed PHY blocks. It exposes each child DT PHY as a generic PHY and, unless the PHY is reserved for the early USB-UART path, also registers a fixed 480 MHz clock sourced from the PHY PLL for USB controller consumers.

Important APIs and functions: The platform entry point is `rockchip_usb_phy_probe()`. Per-child setup lives in `rockchip_usb_phy_init()`, which creates `struct rockchip_usb_phy`, discovers the `reg` offset, optional `phy-reset`, optional `phyclk`, optional `vbus`, synthetic `clk480m`, and `struct phy`. Generic PHY operations are `rockchip_usb_phy_power_on()`, `rockchip_usb_phy_power_off()`, and `rockchip_usb_phy_reset()`. Clock callbacks are `rockchip_usb_phy480m_enable()`, `rockchip_usb_phy480m_disable()`, `rockchip_usb_phy480m_is_enabled()`, and `rockchip_usb_phy480m_recalc_rate()`. Built-in-only USB-UART support is entered by the `rockchip.usb_uart` early param and `rockchip_init_usb_uart()`, with SoC-specific helpers `rk3188_init_usb_uart()` and `rk3288_init_usb_uart()`.

Control flow: Probe obtains match data, resolves the GRF regmap from the parent syscon or `rockchip,grf`, then walks available child nodes. Each child maps its register offset to a PLL clock name from the SoC table, optionally registers a 480 MHz clock provider, creates a generic PHY, and powers the analog block down by setting SIDDQ. On power-on, optional VBUS is enabled first, then the 480 MHz clock is prepared, whose enable callback clears SIDDQ. Power-off disables the clock, disables VBUS in the clock disable callback, and sets SIDDQ. Reset asserts/deasserts the child reset with a 10 us delay. If early USB-UART is enabled for the designated PHY, normal PHY clock-provider registration is skipped and the PHY clock is left prepared instead.

State and persistence: Persistent driver state is held in `struct rockchip_usb_phy_base` and per-child `struct rockchip_usb_phy`. Hardware state is mostly GRF write-mask register state: SIDDQ, DISABLE, COMMON_ON_N, UTMI suspend/opmode/xcvrselect/termsel bits, and SoC-specific bypass bits. The USB-UART path permanently changes the selected PHY from USB to UART bypass for the booted kernel. The synthetic clock state is observable through `clk_prepare_enable()` users.

Dependencies and integration points: Depends on the generic PHY framework, common clock framework, reset framework, optional regulator framework, syscon/regmap GRF access, OF child nodes, Rockchip GRF write-mask encoding via `FIELD_PREP_WM16()`, and early boot parameter handling when built in. It integrates with USB2 controller DT PHY references and clock consumers expecting `sclk_otgphy*_480m`.

Risks: Register offsets and PLL names must match the child `reg` properties exactly. USB-UART mode intentionally makes one PHY unavailable for USB and returns `-EBUSY` for normal power operations. Optional VBUS is disabled from the clock disable path, so mismatched clock/PHY usage can affect supply lifetime. Early USB-UART runs before the platform driver and relies on the same DT/syscon data being available at early init time.

Test signals: Useful signals are successful probe for each compatible, visible 480 MHz clock providers on non-UART PHY nodes, correct SIDDQ transitions on PHY power on/off, reset pulse behavior, optional VBUS enable/disable, USB enumeration through DWC2/EHCI/OHCI users, and boot testing with and without `rockchip.usb_uart`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usbdp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usbdp.c

Purpose: Provides the Rockchip USB3/DisplayPort combo PHY driver for RK3576 and RK3588 Samsung USBDP IP blocks. One hardware PMA can be used as USB3, DP, or DP plus USB depending on DT lane mux data or Type-C orientation/mode notifications, and the driver exposes separate generic PHY handles for `PHY_TYPE_USB3` and `PHY_TYPE_DP`.

Important APIs and functions: `rk_udphy_probe()` maps the PMA region, derives the PHY instance id from the MMIO resource start address, parses syscon/regmap dependencies, creates USB3 and DP PHYs, and optionally registers Type-C orientation and mode switch devices. Shared lifecycle is handled by `rk_udphy_power_on()`, `rk_udphy_power_off()`, `rk_udphy_setup()`, `rk_udphy_init()`, and `rk_udphy_disable()`. DP operations include `rk_udphy_dp_phy_power_on()`, `rk_udphy_dp_phy_configure()`, `rk_udphy_dp_set_voltage()`, and validation helpers for link rate, lane count, voltage swing, and pre-emphasis. USB3 operations are `rk_udphy_usb3_phy_init()` and `rk_udphy_usb3_phy_exit()`. Type-C callbacks are `rk_udphy_orien_sw_set()` and `rk_udphy_typec_mux_set()`.

Control flow: Probe initializes clocks, resets, GRF maps, lane mapping, optional SBU GPIOs, maximum-speed handling, and initial hardware status. If no `rockchip,dp-lane-mux` exists, the driver defaults to USB mode and waits for Type-C callbacks to define DP mapping. If DT lane mux exists, it validates two or four DP lanes and derives DP-only or DP+USB mode. Power-on sets up clocks, resets, low-power GRF bits, reference-clock tables for 24 or 26 MHz, lane mux bits, DP/USB resets, and PLL/CDR lock polling. DP power-on powers the shared PHY, enables DP lanes, writes VO GRF lane/AUX routing, and delays for AUX readiness. DP configure programs link bandwidth, SSC, ROPLL lock, per-lane TX clock inversion, and per-rate/per-Type-C drive strength tables. Type-C mode changes update lane mux and HPD state; if the active mode changes, the next power-on path tears down and reinitializes the PMA.

State and persistence: `struct rk_udphy` persists current `mode`, powered `status` bitmask, `mode_change`, `flip`, `hs`, lane mux selections, DP lane selections, AUX polarity, HPD selection/configuration, link rate/bandwidth/lane count, Type-C switch/mux handles, and PMA/GRF mappings. Hardware state persists in PMA registers, GRF write-mask registers for low power, LFPS, BVALID, USB3 port disable, VO HPD/lane routing, reset controls, clocks, and SBU DC GPIOs. Resume replays saved HPD state if software HPD had been selected.

Dependencies and integration points: Depends on generic PHY, Type-C mux/switch APIs, USB Type-C DP altmode definitions, reset/clock/regmap/gpio/property helpers, DT binding `PHY_TYPE_USB3` and `PHY_TYPE_DP`, and Rockchip `u2phy-grf`, `usbdpphy-grf`, `usb-grf`, and `vo-grf` syscons. It integrates with DWC3 USB, DP controllers, Type-C port managers, USB maximum-speed policy, and board-specific lane mux properties.

Risks: This is a shared-resource driver, so ordering and mutex coverage are critical. Wrong lane mapping breaks DP or USB silently, and Type-C orientation changes require reinitialization when PMA state is already active. Unsupported reference clock rates fail setup. PLL/CDR polling can return `-EPROBE_DEFER` after a first LCPLL lock failure because firmware may have left the PHY in a problematic state. HPD replay on resume only covers software-triggered HPD state, not full PMA reinitialization.

Test signals: Validate boot/probe on RK3576/RK3588, both MMIO ids on RK3588, USB3-only, DP-only, and DP+USB modes, Type-C normal/reverse orientations, DP states C/D/E, HPD IRQ pulses, AUX transactions after the post-power delay, 1/2/4 lane DP link training at RBR/HBR/HBR2/HBR3, USB high-speed-only maximum-speed behavior, suspend/resume HPD replay, and failure logs for PLL/CDR/refclk issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-usbdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/Kconfig

Purpose: Defines Kconfig symbols for Samsung-family PHY drivers: Exynos DP video, MIPI video, PCIe, UFS, USB2, USB DRD, and Exynos5250 SATA PHY support. It also gates SoC-specific USB2 implementation objects behind the common Samsung USB2 driver.

Important APIs and functions: The relevant symbols are `PHY_EXYNOS_DP_VIDEO`, `PHY_EXYNOS_MIPI_VIDEO`, `PHY_EXYNOS_PCIE`, `PHY_SAMSUNG_UFS`, `PHY_SAMSUNG_USB2`, `PHY_EXYNOS4210_USB2`, `PHY_EXYNOS4X12_USB2`, `PHY_EXYNOS5250_USB2`, `PHY_S5PV210_USB2`, `PHY_EXYNOS5_USBDRD`, and `PHY_EXYNOS5250_SATA`.

Control flow: Build selection flows from SoC or compile-test symbols into driver compilation. Most user-visible drivers select `GENERIC_PHY`; UFS, USB2, USB DRD, and SATA also select or depend on syscon/I2C facilities as needed. The hidden USB2 SoC symbols default on for matching SoC families and cause extra object files to be included in the common USB2 module.

State and persistence: Kconfig has no runtime state, but it persists build-time policy. Defaults such as `default ARCH_EXYNOS` or `default y if ARCH_S5PV210 || ARCH_EXYNOS` determine whether PHY providers are available in platform kernels without explicit user selection.

Dependencies and integration points: Integrates with architecture symbols (`ARCH_EXYNOS`, `ARCH_S5PV210`, `SOC_EXYNOS*`, `CPU_EXYNOS4210`), USB controller symbols (`USB_EHCI_EXYNOS`, `USB_OHCI_EXYNOS`, `USB_DWC2`, `USB_DWC3_EXYNOS`), `OF`, `HAS_IOMEM`, `TYPEC || !TYPEC`, `MFD_SYSCON`, and I2C support for SATA.

Risks: Incorrect dependencies can produce link errors or nonfunctional platform boots. The USB DRD symbol depends on `USB_DWC3_EXYNOS`, so PHY-only compile coverage is constrained. Hidden USB2 SoC options rely on architecture defaults and can omit needed tables on unusual multiplatform or compile-test builds.

Test signals: Build matrix coverage for Exynos, S5PV210, and `COMPILE_TEST`; checking that selected symbols produce the intended objects; randconfig coverage around optional Type-C and USB controller symbols; and boot-time verification that expected PHY providers appear for enabled DT compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/Makefile

Purpose: Maps Samsung PHY Kconfig symbols to object files and composes common multi-object drivers for Samsung UFS and USB2 PHY support.

Important APIs and functions: Object rules directly build `phy-exynos-dp-video.o`, `phy-exynos-mipi-video.o`, `phy-exynos-pcie.o`, `phy-exynos5-usbdrd.o`, and `phy-exynos5250-sata.o`. The `phy-exynos-ufs` composite includes `phy-samsung-ufs.o` plus GS101, Exynos7, ExynosAuto v9/v920, and FSD UFS data files. The `phy-exynos-usb2` composite includes `phy-samsung-usb2.o` plus selected Exynos4210, Exynos4x12, Exynos5250, and S5PV210 data files.

Control flow: Kbuild uses `obj-$(CONFIG_...)` and per-composite `-y` or `-$(CONFIG_...)` lines to decide which files are compiled and linked into each module or built-in object. UFS variant data is always linked when `PHY_SAMSUNG_UFS` is enabled; USB2 variant data is conditional on the hidden SoC support symbols.

State and persistence: The file persists build composition only. It determines which exported `const struct ..._drvdata` or `..._config` symbols are available to common probe code at link time.

Dependencies and integration points: Integrates with the Kconfig symbols in the same directory and with common C files that declare external SoC data structures, especially `phy-samsung-ufs.c`/`.h` and the common Samsung USB2 driver.

Risks: Missing a variant object causes unresolved externs or missing compatible support. Linking all UFS variants into one module increases compile coverage but can include tables for platforms not present at runtime. Conditional USB2 objects must remain synchronized with Kconfig defaults and extern declarations in shared headers.

Test signals: Kernel build for all relevant symbol combinations, `modinfo`/object inspection for module composition, and runtime matching of DT compatibles to data structures included by the selected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-dp-video.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-dp-video.c

Purpose: Provides a small generic PHY provider for Exynos DisplayPort video PHY isolation control. It supports Exynos5250 and Exynos5420 PMU control offsets.

Important APIs and functions: `exynos_dp_video_phy_probe()` resolves the PMU regmap, creates one generic PHY, and registers an OF PHY provider. PHY operations are `exynos_dp_video_phy_power_on()` and `exynos_dp_video_phy_power_off()`, which set or clear `EXYNOS4_PHY_ENABLE` at a compatible-specific PMU offset. Match data is `struct exynos_dp_video_phy_drvdata`.

Control flow: Probe first tries the parent syscon regmap for backward-compatible DT layout, then falls back to `samsung,pmu-syscon`. Power-on disables isolation by writing the enable bit; power-off enables isolation by clearing it.

State and persistence: The only runtime state is `struct exynos_dp_video_phy` containing the PMU regmap and selected offset data. Hardware state persists as the PMU isolation bit until changed by this driver or firmware.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF match data, platform devices, and `exynos-regs-pmu.h`. It is consumed by Exynos DisplayPort controller nodes through standard PHY phandles.

Risks: Parent syscon fallback and phandle lookup must match board DT. A wrong PMU offset can isolate the wrong PHY. There is no clock/reset sequencing here, so it assumes the DP controller or platform firmware handles the rest of the PHY bring-up.

Test signals: Probe success for both compatibles, PMU bit changes during DP enable/disable, DisplayPort link training/display output, suspend/resume display recovery, and no regressions for legacy DTs using parent syscon lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-dp-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-mipi-video.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-mipi-video.c

Purpose: Implements MIPI CSI-2/DSI D-PHY power and reset control for S5PV210 and Exynos variants. It exposes multiple PHY instances from a single platform device and maps each phandle index to a CSIS or DSIM PHY.

Important APIs and functions: Device descriptions use `struct mipi_phy_device_desc` and per-PHY `struct exynos_mipi_phy_desc` to identify enable/reset registers, regmaps, reset bits, and coupled PHY relationships. Probe is `exynos_mipi_video_phy_probe()`. OF translation is `exynos_mipi_video_phy_xlate()`. Power operations are `exynos_mipi_video_phy_power_on()`, `exynos_mipi_video_phy_power_off()`, and shared `__set_phy_state()`.

Control flow: Probe obtains the compatible-specific descriptor, resolves one or more syscon regmaps, initializes a spinlock, creates `num_phys` generic PHY objects, and registers a custom xlate provider. Power-on asserts resetn first and then sets the PMU enable bit. Power-off clears resetn and, for coupled CSIS/DSIM pairs, clears PMU enable only when the companion PHY's `power_count` is zero. Different SoCs route reset control through PMU, display sysreg, camera sysreg, or register zero depending on descriptor data.

State and persistence: Runtime state stores regmaps and per-PHY descriptors. Hardware state persists in PMU/sysreg enable and resetn bits. Coupled PHY power state is inferred from the generic PHY `power_count`, so the driver avoids removing shared analog power while a coupled user remains active.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF phandle arguments, Samsung PMU register definitions, and spinlocks around multi-register updates. It integrates with Exynos/S5PV210 camera and display drivers needing CSIS/DSIM PHYs by index.

Risks: Coupled PHY accounting relies on generic PHY power counts and descriptor correctness. Some descriptors use reset register zero in non-PMU sysregs, so regmap ordering and naming must match DT exactly. The spinlock protects driver-side sequencing, but regmap backends must be safe for this context. Incorrect xlate indices return the wrong PHY or fail at runtime.

Test signals: Power cycling each CSIS/DSIM index, concurrent coupled CSIS/DSIM use, register traces for PMU and sysreg writes, camera capture and DSI display output, invalid phandle index handling, and suspend/resume across active video pipelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-mipi-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-pcie.c

Purpose: Provides the Exynos5433 PCIe PHY provider. It programs PMU and FSYS sysreg bits plus the PCIe PHY MMIO register block to bring up a 24 MHz reference-clock PCIe PHY.

Important APIs and functions: `exynos_pcie_phy_probe()` maps MMIO, resolves `samsung,pmu-syscon` and `samsung,fsys-sysreg`, creates the generic PHY, and registers an OF PHY provider. PHY operations are `exynos5433_pcie_phy_init()` and `exynos5433_pcie_phy_exit()`. `exynos_pcie_phy_writel()` wraps MMIO writes with register index-to-byte offset conversion.

Control flow: Init enables PMU PHY control, disables L1 exit request and refclk gating, asserts common reset, deasserts MAC reset, selects 24 MHz refclk, clears global reset, writes a fixed tuning sequence into PHY registers, then releases common reset and asserts MAC reset bits. Exit re-enables refclk gating and clears PMU enable.

State and persistence: Driver state is `struct exynos_pcie_phy` with MMIO and two syscon regmaps. Hardware state persists in PMU isolation, FSYS reset/refclk/gating controls, and PHY tuning registers until reset or power loss.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF platform matching, and the Exynos PCIe controller consuming the PHY. The driver is built in with `builtin_platform_driver()`, matching early PCIe availability expectations.

Risks: The tuning sequence is hard-coded and SoC-specific. Missing PMU or FSYS syscon phandles prevent probe. Reset ordering is sensitive; wrong values can leave PCIe link training dead or gate the reference clock under the controller.

Test signals: Exynos5433 PCIe probe, PHY init/exit call tracing, PMU/FSYS register dumps, stable PCIe link training, endpoint enumeration, suspend/resume or controller reset testing, and absence of refclk gating during active links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4210-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4210-usb2.c

Purpose: Supplies Exynos4210-specific configuration and power callbacks for the common Samsung USB2 PHY driver. It covers device, host, HSIC0, and HSIC1 PHYs.

Important APIs and functions: The exported data is `exynos4210_usb2_phy_config`. Helpers include `exynos4210_rate_to_clk()`, `exynos4210_isol()`, `exynos4210_phy_pwr()`, `exynos4210_power_on()`, and `exynos4210_power_off()`. Per-PHY metadata is in `exynos4210_phys`.

Control flow: The common driver calls the rate converter for the reference clock and per-instance power callbacks. Power-on clears power-down/suspend/sleep bits, writes the clock FSEL, toggles the relevant reset bits with required delays, then disables PMU isolation for device or host PHYs. Power-off enables PMU isolation first and then sets the PHY power-down bits. Host and HSIC reset masks differ so each physical block and host link path is reset appropriately.

State and persistence: This file persists no private data. It mutates common-driver instance counters indirectly through callbacks and writes the USB PHY MMIO power/clock/reset registers, PMU isolation bits, host floating-prevention register, and reference clock selector.

Dependencies and integration points: Depends on `phy-samsung-usb2.h`, the common Samsung USB2 framework, MMIO accessors, PMU regmap, and Exynos4210 register layout. It integrates with USB device, host, and HSIC controller users selected by DT phandle index.

Risks: Exynos4210 has separate PMU isolation offsets for device and host only; HSIC paths do not use isolation in this helper. Reset bit masks must match the hardware link topology. Power-on sequence order is explicitly important: hardware power before isolation removal.

Test signals: Device and host USB2 enumeration, HSIC0/HSIC1 attached-device detection, reference clock variants 12/24/48 MHz, reset timing stability, PMU isolation transitions, and repeated power-cycle testing through runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4210-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4x12-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4x12-usb2.c

Purpose: Provides Exynos4x12 and Exynos3250 USB2 PHY data and callbacks for the common Samsung USB2 driver. It supports device, host, HSIC0, and HSIC1 on Exynos4x12 and a reduced single-PHY configuration for Exynos3250.

Important APIs and functions: Exports `exynos3250_usb2_phy_config` and `exynos4x12_usb2_phy_config`. Main helpers are `exynos4x12_rate_to_clk()`, `exynos4x12_setup_clk()`, `exynos4x12_isol()`, `exynos4x12_phy_pwr()`, `exynos4x12_power_on_int()`, `exynos4x12_power_off_int()`, `exynos4x12_power_on()`, and `exynos4x12_power_off()`.

Control flow: External power requests use `ext_cnt`; internal shared dependencies use `int_cnt`. Host power-on switches the mode register to host and powers the device PHY internally. Device power-on switches to device when mode switching is supported. HSIC power-on powers device and host dependencies before the HSIC PHY. Power-off unwinds these relationships and switches device mode back to host when needed. Clock setup writes FSEL and common-on bits, with an Exynos3250-specific refclk select option.

State and persistence: Persistent state is held by the common driver counters. Hardware state includes PHY power bits, reset bits, PMU isolation for OTG/HSIC0/HSIC1, mode switch sysreg bits, and clock selection. The comments note empirically corrected reset bit assignments for Exynos4412-like hardware.

Dependencies and integration points: Depends on the common Samsung USB2 driver, MMIO, PMU and system regmaps, and Exynos4x12/3250 SoC configuration. It integrates with USB OTG, host, and HSIC consumers that share physical resources.

Risks: Shared dependency counters must remain balanced; underflow or missed dependency power-off can leave analog blocks on or off incorrectly. Mode switching affects device/host role selection. The hardware reset bit layout intentionally differs from reference manual ordering, making cleanups risky without hardware validation.

Test signals: Device/host role switching, HSIC dependency behavior, repeated nested power requests, counter balance under runtime PM, Exynos3250 single-PHY boot, all supported reference rates, and register traces showing corrected reset bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos4x12-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5-usbdrd.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5-usbdrd.c

Purpose: Implements the Samsung Exynos USB DRD PHY provider for many SoCs, including Exynos5250/5420/5433/7/7870/850/990/2200, GS101, and ExynosAuto v920 variants. It supports UTMI high-speed PHYs, PIPE3/SuperSpeed PHYs, newer USBDP PMA/PCS layouts, external high-speed PHY integration, Type-C orientation callbacks, regulators, clocks, PMU isolation, and SoC-specific tuning tables.

Important APIs and functions: Probe is `exynos5_usbdrd_phy_probe()`, OF translation is `exynos5_usbdrd_phy_xlate()`, clock setup is `exynos5_usbdrd_phy_clk_handle()`, and optional Type-C setup is `exynos5_usbdrd_setup_notifiers()`. Common ops include `exynos5_usbdrd_phy_init()`, `exynos5_usbdrd_phy_exit()`, `exynos5_usbdrd_phy_power_on()`, `exynos5_usbdrd_phy_power_off()`, and `exynos5_usbdrd_phy_calibrate()`. Variant ops include Exynos7870, Exynos850, Exynos2200, GS101, and ExynosAuto v920 init/exit/power functions. Tuning is represented by `struct exynos5_usbdrd_phy_tuning` and applied by `exynos5_usbdrd_apply_phy_tunes()`.

Control flow: Probe allocates `struct exynos5_usbdrd_phy`, maps either a legacy single region or named `phy`/`pcs`/`pma` regions, optionally obtains an external `hs` PHY, initializes clocks and reference clock encoding, resolves the PMU regmap, obtains supplies, registers Type-C orientation switch when present, creates two generic PHY instances, assigns PMU offsets based on channel alias and PIPE3/SS split, and registers the provider. Common init enables register clocks, resets link/PHY registers, programs FLADJ, reference clock fields, UTMI or PIPE3 init, and toggles port reset. Common power-on enables core clocks, regulators, and clears PMU isolation; power-off isolates and disables supplies/clocks. Newer variants often move isolation into init to avoid PMA access faults, then apply SoC-specific UTMI/PMA/PCS sequences.

State and persistence: Driver state persists in `struct exynos5_usbdrd_phy`: mapped register regions, clock arrays, regulator array, drvdata, external HS PHY, mutex, per-instance PMU offsets and configs, encoded `extrefclk`, Type-C switch, and current orientation. Hardware state spans PMU isolation bits, PHY controller registers, PCS/PMA tuning registers, link controller resets, VBUSVALID/BVALID force bits, regulator enables, and clock gates. The mutex serializes orientation callbacks with init/exit on variants that share registers.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clk bulk APIs, regulator bulk APIs, syscon/regmap PMU, Type-C switch APIs when enabled, OF aliases, optional external PHYs, PMU register definitions, and DWC3 Exynos users. It integrates with USB DRD controllers, Type-C orientation providers, and board supplies/clocks.

Risks: This file is high-risk because a single driver covers many incompatible register layouts. `drv_data->phy_cfg[i]` is indexed for two possible PHY ids even when a SoC effectively supports only one path, so match data must be consistent with DT consumers. PMU isolation ordering matters; comments note SError risk when accessing PMA while isolated. Reference clock rates outside the supported table fail probe. Type-C orientation changes affect GS101 lane mux/CDR polling and VBUS force bits. Tuning tables write many magic registers and must be hardware-validated.

Test signals: Build and boot for every compatible, PHY phandle index coverage for UTMI and PIPE3, regulator and clock enable/disable traces, USB2 and USB3 enumeration, Exynos5420 SuperSpeed calibration through CRPORT, Type-C attach/detach/orientation behavior, GS101 PLL/CDR lock logs, ExynosAuto v920 HS/SS combo init and powerdown, suspend/resume/runtime PM, and failure-path logs for missing PMU, clocks, regulators, or unsupported refclk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5-usbdrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-sata.c

Purpose: Implements the Exynos5250 SATA SerDes/PHY provider. It powers PMU isolation, programs SATA PHY registers, sends an I2C tuning command to the external SATA PHY component, and waits for PLL lock.

Important APIs and functions: `exynos_sata_phy_probe()` maps registers, resolves PMU syscon and I2C client phandle, enables the `sata_phyctrl` clock, creates the generic PHY, and registers the provider. PHY operations are `exynos_sata_phy_init()`, `exynos_sata_phy_power_on()`, and `exynos_sata_phy_power_off()`. `wait_for_reg_status()` polls PLL lock using jiffies.

Control flow: Probe holds a reference to the I2C device and enables the PHY control clock for the lifetime of the provider. Power-on/off toggles `EXYNOS5_SATAPHY_PMU_ENABLE`. Init enables PMU power, sequences reset bits, sets high-speed Gen3 mode, marks PHY calibrated, sends `{0x3a, 0x0b}` over I2C, cycles common reset, and waits for `PHSTATM_PLL_LOCKED`.

State and persistence: `struct exynos_sata_phy` stores the generic PHY, clock, MMIO base, PMU regmap, and I2C client. Hardware state persists in PMU enable, SATA reset/mode/control registers, and I2C-programmed SerDes state. The I2C device reference is released only on probe failure in this code path.

Dependencies and integration points: Depends on generic PHY, platform MMIO, PMU syscon/regmap, I2C core, OF phandle lookup, clocks, and Exynos5250 SATA host integration.

Risks: Polling uses a tight jiffies loop without sleep. The fixed I2C payload is hardware-specific and failure aborts init. Probe defers if the I2C client is not ready. Clock lifetime is broad: enabled at probe and disabled only on probe failure through local labels. Wrong PMU or I2C phandles prevent SATA bring-up.

Test signals: SATA host link-up at supported speeds, PLL lock status, I2C transaction success, PMU enable/disable checks, probe defer ordering with I2C adapter/client, and repeated PHY init/power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-usb2.c

Purpose: Provides Exynos5250 and Exynos5420 USB2 PHY configuration for the common Samsung USB2 driver. It covers OTG/device, host, and HSIC PHYs, with a reduced Exynos5420 host/HSIC layout.

Important APIs and functions: Exports `exynos5250_usb2_phy_config` and `exynos5420_usb2_phy_config`. Helpers include `exynos5250_rate_to_clk()`, `exynos5250_isol()`, `exynos5250_power_on()`, and `exynos5250_power_off()`. PHY metadata arrays are `exynos5250_phys` and `exynos5420_phys`.

Control flow: Device power-on switches the sysreg mode to device, configures OTG clock/reset/refclk fields, clears sleep/suspend/SIDDQ, pulses resets, and removes isolation. Host/HSIC power-on configures host PHY clock/reset, also configures OTG registers, initializes both HSIC PHY control registers, enables EHCI burst settings, applies OHCI frame settings, and removes host isolation. Power-off re-enables isolation and sets sleep/suspend/SIDDQ or HSIC low-power bits for the selected PHY.

State and persistence: The file relies on common-driver state and writes MMIO registers for host, HSIC, EHCI, OHCI, and OTG control. PMU isolation offset selection depends on whether the active config is Exynos5250 or Exynos5420 and on the PHY id. Mode switch state persists in a system register.

Dependencies and integration points: Depends on `phy-samsung-usb2.h`, common Samsung USB2 code, MMIO, PMU/sysreg regmaps, and Exynos USB host/device controllers. It integrates with EHCI/OHCI/DWC2-style consumers and HSIC devices.

Risks: Host power-on also touches OTG registers and both HSIC controls, so independent consumers are not fully isolated from each other. Exynos5420 uses a different host isolation offset and fewer exposed PHYs. A duplicated macro name for `EXYNOS_5250_HOSTEHCICTRL_FLADJVAL0_MASK` near the FLADJVAL2 comment is suspicious but not used in the active code path. Mode switching can disrupt active role users if calls are unbalanced.

Test signals: Device mode enumeration, host EHCI/OHCI behavior, HSIC device detection, Exynos5420 host isolation offset validation, reference clock variants, sysreg mode switch checks, and repeated runtime PM power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos5250-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos7-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos7-ufs.c

Purpose: Supplies Exynos7 UFS PHY calibration tables and drvdata for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `exynos7_ufs_phy`. Register programming data is split into `exynos7_pre_init_cfg`, `exynos7_pre_pwr_hs_cfg`, and `exynos7_post_pwr_hs_cfg`, referenced by `exynos7_ufs_phy_cfgs`. Clock list is `tx0_symbol_clk`, `rx0_symbol_clk`, `rx1_symbol_clk`, and `ref_clk`.

Control flow: The common UFS PHY driver applies the pre-init table at PHY power-on, then advances through post-init, pre-HS power mode, and post-HS power mode calibration states as callers invoke `.calibrate`. Exynos7 uses the common `samsung_ufs_phy_wait_for_lock_acq()` as `wait_for_cdr` after post-HS programming.

State and persistence: This file contains static const tables only. Hardware state is written by the common driver to PMA common and transmit/receive blocks, and PMU isolation is controlled through offset `EXYNOS7_EMBEDDED_COMBO_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h` macros and the common Samsung UFS PHY core. It integrates with the `samsung,exynos7-ufs-phy` compatible via common match data.

Risks: Table values are magic SoC tuning values and include order-sensitive comments. Lane offsets and CDR status offset must match Exynos7 hardware. Missing clocks or wrong PMU isolation masks prevent link startup.

Test signals: UFS link startup, HS-G1/G2 series A/B power-mode changes, PLL/CDR lock acquisition, clock enable coverage, and hibernate/resume behavior through the common driver even though this SoC has no hibern8-specific table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos7-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov9-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov9-ufs.c

Purpose: Provides ExynosAuto v9 UFS PHY calibration tables and drvdata for the shared Samsung UFS PHY driver.

Important APIs and functions: Exports `exynosautov9_ufs_phy`. Tables are `exynosautov9_pre_init_cfg` and `exynosautov9_pre_pwr_hs_cfg`, referenced by `exynosautov9_ufs_phy_cfgs`. The file defines an Auto v9 lane offset helper `PHY_TRSV_REG_CFG_AUTOV9()` using a 0x50 transmit/receive channel offset.

Control flow: The common driver applies the pre-init table when powering on in the initial state, later applies the pre-HS power-mode table during calibration, and uses the common lock acquisition helper for CDR status after post-HS state if invoked.

State and persistence: Static tables and drvdata are the only software state. Runtime hardware state is PMA register contents and PMU isolation at offset `0x728`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h`, common UFS PHY probe/match handling, a single `ref_clk`, and the `samsung,exynosautov9-ufs-phy` compatible.

Risks: The custom transceiver channel offset differs from the default, so using default macros would program the wrong lane. The tables cover no explicit post-HS entries, so link stability relies on pre-init/pre-HS values plus common CDR wait.

Test signals: Probe with one `ref_clk`, UFS link startup, HS-G3 series B power mode, PMU isolation toggle, CDR lock status at `0x5e`, and lane programming on single- and multi-lane configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov9-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov920-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov920-ufs.c

Purpose: Supplies ExynosAuto v920 UFS PHY tables and a custom CDR lock recovery callback for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `exynosautov920_ufs_phy` and `exynosautov920_ufs_phy_wait_cdr_lock()`. Tables include a large `exynosautov920_pre_init_cfg`, small `exynosautov920_pre_pwr_hs_cfg`, empty post-HS table, and `exynosautov920_ufs_phy_cfgs`. The transceiver lane offset is 0x200.

Control flow: The common driver writes the pre-init table during initial power-on and pre-HS table before HS mode. On post-HS CDR wait, the custom callback polls a per-lane CDR lock register at `EXYNOSAUTOV920_CDR_LOCK_OFFSET` plus lane offset. If lock is absent, it repeatedly disables/enables CDR through register `0x222`; on lock it writes a final register `0x246` value and returns success.

State and persistence: Static drvdata controls PMU isolation offset `0x708`, single `ref_clk`, and CDR status offset. The custom wait mutates PMA transceiver registers during recovery loops.

Dependencies and integration points: Depends on common Samsung UFS code and `phy-samsung-ufs.h`. It binds through `samsung,exynosautov920-ufs-phy`.

Risks: The wait loop uses fixed 40 us delays and 100 retries, so marginal hardware may time out. CDR recovery writes are lane-specific and must match the 0x200 lane layout. The large pre-init table is highly hardware-specific, with little semantic validation possible in software.

Test signals: UFS link startup on ExynosAuto v920, two-lane CDR lock behavior, timeout logging, HS mode transitions, PMU isolation state, and regression testing after hibernate/power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov920-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-fsd-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-fsd-ufs.c

Purpose: Provides FSD SoC UFS PHY drvdata and a small set of calibration tables for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `fsd_ufs_phy`. Tables are `fsd_pre_init_cfg`, empty `fsd_pre_pwr_hs_cfg`, empty `fsd_post_pwr_hs_cfg`, and `fsd_ufs_phy_cfgs`. It uses the common `samsung_ufs_phy_wait_for_lock_acq()` callback.

Control flow: Common UFS PHY code applies the pre-init table in the initial calibration stage and sees sentinel-only tables for HS pre/post stages. CDR lock polling uses status offset `0x6e`.

State and persistence: Only static tables and drvdata are defined here. Hardware state is PMA register programming and PMU isolation at offset `FSD_EMBEDDED_COMBO_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h` and the common driver. It binds to `tesla,fsd-ufs-phy`.

Risks: Minimal HS-stage tuning means stability depends on defaults and pre-init programming. The CDR status offset differs from Exynos7, so drvdata correctness is important. The compatible is vendor-specific and may have limited compile/runtime coverage.

Test signals: FSD UFS enumeration, PLL/CDR lock polling at `0x6e`, PMU isolation toggles, single `ref_clk` availability, and power-mode transitions despite empty HS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-fsd-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-gs101-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-gs101-ufs.c

Purpose: Provides Google Tensor GS101 UFS PHY calibration, hibern8 transition tables, and custom calibration/CDR wait callbacks for the shared Samsung UFS PHY core.

Important APIs and functions: Exports `tensor_gs101_ufs_phy`. Tables include `tensor_gs101_pre_init_cfg`, `tensor_gs101_pre_pwr_hs_config`, `tensor_gs101_post_pwr_hs_config`, `tensor_gs101_post_h8_enter`, and `tensor_gs101_pre_h8_exit`. Custom callbacks are `gs101_phy_wait_for_calibration()` and `gs101_phy_wait_for_cdr_lock()`.

Control flow: The common core applies pre-init data then waits for RX calibration done at transceiver register `0x338` per lane. Later HS calibration applies pre/post power tables. Hibern8 enter/exit notifications program the dedicated hibern8 tables; on hibern8 exit the common core invokes the GS101 CDR wait callback, which polls register `0x339` and toggles CDR enable bits in register `0x222` until lock.

State and persistence: This file is static drvdata plus hardware-programming tables. Runtime hardware state includes PMA common/transceiver registers, hibern8-specific overrides, CDR enable toggles, and PMU isolation at `TENSOR_GS101_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h`, the common Samsung UFS PHY driver, one `ref_clk`, and the `google,gs101-ufs-phy` compatible. It integrates with UFS controller hibern8 notifications through `notify_phystate`.

Risks: The pre-HS config array lacks an explicit `END_UFS_PHY_CFG` sentinel in the visible table, so the following static object layout is important to inspect if changing it. Calibration and CDR waits use per-lane offsets and fixed retry timing. Hibern8 tables directly affect low-power entry/exit stability.

Test signals: GS101 UFS boot, RX calibration done polling, CDR recovery after HS mode and hibern8 exit, hibern8 enter/exit cycles, two-lane operation, PMU isolation, and timeout/error logs under marginal link conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-gs101-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-s5pv210-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-s5pv210-usb2.c

Purpose: Supplies S5PV210 USB2 PHY data and callbacks for the common Samsung USB2 driver. It supports device and host PHY instances.

Important APIs and functions: Exports `s5pv210_usb2_phy_config`. Helpers are `s5pv210_rate_to_clk()`, `s5pv210_isol()`, `s5pv210_phy_pwr()`, `s5pv210_power_on()`, and `s5pv210_power_off()`. Per-instance metadata is `s5pv210_phys`.

Control flow: The common driver calls the rate converter for 12/24/48 MHz reference clocks. Power-on clears PMU isolation and powers/resets the selected PHY. Power-off sets power-down bits and then re-enables PMU isolation. Device and host choose different power and reset masks.

State and persistence: No private runtime state is defined here. Hardware state persists in USB PHY power/clock/reset registers and PMU isolation bits at `S5PV210_USB_ISOL_OFFSET`.

Dependencies and integration points: Depends on the common Samsung USB2 driver, MMIO accessors, PMU regmap, and S5PV210 USB device/host consumers.

Risks: Only three reference rates are supported. Clock writing uses `drv->ref_reg_val` directly to `S5PV210_UPHYCLK`, so common-driver conversion must already encode the correct bits. Power/isolation ordering differs from some Exynos variants and should not be mechanically refactored without hardware testing.

Test signals: S5PV210 device and host USB enumeration, 12/24/48 MHz reference clocks, PMU isolation bit changes, reset timing, and repeated power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-s5pv210-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.c

Purpose: Implements the common Samsung UFS PHY framework. It binds compatible-specific drvdata, maps PMA registers, controls PMU isolation, manages clocks, applies staged calibration tables, handles UFS hibern8 notifications, and exposes one generic PHY to UFS host drivers.

Important APIs and functions: Public helper exports within the driver family are `samsung_ufs_phy_config()` and `samsung_ufs_phy_wait_for_lock_acq()`. Generic PHY operations are `samsung_ufs_phy_init()`, `samsung_ufs_phy_exit()`, `samsung_ufs_phy_power_on()`, `samsung_ufs_phy_power_off()`, `samsung_ufs_phy_calibrate()`, `samsung_ufs_phy_set_mode()`, and `samsung_ufs_phy_notify_state()`. Probe is `samsung_ufs_phy_probe()`.

Control flow: Probe matches compatible data, maps `phy-pma`, resolves `samsung,pmu-syscon`, creates the generic PHY, copies isolation config, optionally overrides the PMU offset from the phandle argument, initializes clocks, and registers the PHY provider. Init records bus width as lane count and starts the calibration state machine at `CFG_PRE_INIT`. Power-on disables isolation, enables clocks, and performs pre-init calibration. Later calibrate calls apply the current stage table and advance through pre-init, post-init, pre-HS, post-HS, then wrap to pre-init. Notify-state applies hibern8 enter/exit tables and waits for CDR on exit if supported.

State and persistence: `struct samsung_ufs_phy` tracks PMA base, PMU regmap, clocks, drvdata, current config tables, isolation bits, lane count, calibration state, and current generic PHY mode. Hardware state persists in PMA common/transceiver registers, PMU isolation, and enabled clocks. Calibration state is volatile software state and resets on `.init`.

Dependencies and integration points: Depends on generic PHY, clk bulk, syscon/regmap, platform MMIO, OF match data, UFS PHY notify states, and SoC-specific drvdata from sibling files. It integrates with UFS host controller link startup, power-mode changes, and hibern8 transitions.

Risks: Calibration state advances even if a table is missing, so host call ordering must match expectations. `samsung_ufs_phy_config()` writes lane 1 only for transceiver-block entries and silently ignores common entries on lane 1. `samsung_ufs_phy_ctrl_isol()` writes inverted enable semantics (`isol ? 0 : en`), so PMU bit polarity must match all variants. Missing hibern8 tables are treated as no-op.

Test signals: Probe for all compatibles, lane count from `phy->attrs.bus_width`, staged calibration call sequence during UFS link startup and power-mode changes, clock and PMU isolation traces, PLL/CDR timeout logs, hibern8 enter/exit cycles, and two-lane register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.h -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.h

Purpose: Defines the shared data model, register-table macros, power-mode descriptors, state ids, structures, inline helpers, and extern drvdata declarations used by the Samsung UFS PHY common driver and SoC-specific table files.

Important APIs and functions: Key macros are `PHY_COMN_REG_CFG()`, `PHY_TRSV_REG_CFG_OFFSET()`, `PHY_TRSV_REG_CFG()`, `END_UFS_PHY_CFG`, `PHY_APB_ADDR()`, `PWR_MODE*` helpers, `PHY_PLL_LOCK_BIT`, and `PHY_CDR_LOCK_BIT`. Structures include `samsung_ufs_phy_cfg`, `samsung_ufs_phy_pmu_isol`, `samsung_ufs_phy_drvdata`, and `samsung_ufs_phy`. Inline helpers are `get_samsung_ufs_phy()` and `samsung_ufs_phy_ctrl_isol()`. Function declarations expose lock wait and register programming helpers to variant files.

Control flow: Variant files build sentinel-terminated arrays of `samsung_ufs_phy_cfg` with common or transceiver block ids and power-mode descriptors. The common driver walks these arrays by `id`, writes lane-specific offsets, and uses drvdata callbacks for calibration and CDR waits. PMU isolation is controlled through the inline helper from common power paths.

State and persistence: Header-defined state fields persist the mapped PMA base, PMU regmap, clock bulk array, drvdata pointers, lane count, calibration state, and selected PHY mode. The macros encode APB byte offsets and second-lane transceiver offsets into static tables.

Dependencies and integration points: Depends on Linux generic PHY and regmap types. It couples the common UFS driver with Exynos7, ExynosAuto v9/v920, FSD, and GS101 drvdata definitions.

Risks: The sentinel convention requires every table to end with an entry whose `id` is zero. Power-mode descriptors are stored but the current common writer does not filter by `mode`, so table ordering and host call stage are the real selectors. `samsung_ufs_phy_ctrl_isol()` assumes PMU isolation polarity shared by all variants.

Test signals: Compile coverage for all extern drvdata providers, static inspection of table sentinels, two-lane offset checks, PMU isolation bit behavior, and staged calibration tests that confirm the common driver consumes table structures as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.h -->
