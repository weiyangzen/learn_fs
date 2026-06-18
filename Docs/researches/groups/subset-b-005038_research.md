# Research: subset-b-005038

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb2.c

## Purpose
This driver exposes the Renesas R-Car Gen3 and related RZ USB2 PHY block as up to four generic PHY instances for combined host, OHCI, EHCI, and HSUSB consumers. It also owns OTG role switching for channels with a valid `dr_mode`, VBUS control through either an external regulator or an internally registered regulator, optional extcon publication, reset/runtime PM handling, and SoC-specific register quirks for RZ/G2L, RZ/G3S, RZ/T2H, and RZ/V2H.

## Important APIs, Types, And Functions
`struct rcar_gen3_chan` is the channel-level state: MMIO base, match data, reset, regulator, extcon, four `struct rcar_gen3_phy` children, OTG flags, `dr_mode`, work item, and a spinlock. `struct rcar_gen3_phy_drv_data` selects PHY ops and variant booleans such as `no_adp_ctrl`, `init_bus`, `utmi_ctrl`, and `vblvl_ctrl`. `rcar_gen3_phy_usb2_xlate()` maps DT phandle args to one of the four PHYs and keeps old zero-argument bindings working. The generic PHY callbacks are `rcar_gen3_phy_usb2_init()`, `exit()`, `power_on()`, and `power_off()`, with `rz_g1c_phy_usb2_ops` omitting power callbacks. OTG role helpers include `rcar_gen3_init_otg()`, `rcar_gen3_device_recognition()`, `role_show()`, `role_store()`, and `rcar_gen3_phy_usb2_irq()`.

## Control Flow
Probe maps registers, detects a unified `dr_mode` across the four PHY phandles, allocates/registers an extcon if OTG role handling is active, deasserts optional shared resets, enables runtime PM, initializes bus settings for variants that need it, creates four PHY instances, optionally selects a mux state, configures VBUS supply behavior, requests an optional shared IRQ, registers the PHY provider, and creates the `role` sysfs attribute for OTG channels. PHY init enables USB host/common interrupts, programs timing registers once per channel, initializes OTG only for PHYs with host interrupt bits, and applies variant-specific SIDDQ/UTMI setup. Power-on enables VBUS when external, toggles PLL reset only for the first powered PHY, and marks the child powered; power-off reverses this when the last child powers down. IRQ handling checks OBINT status under the spinlock, clears the appropriate bits, reruns device recognition, and updates VBUS level control.

## State And Persistence
State is in memory only: initialized/powered flags per PHY, channel OTG mode, extcon host state, and regulator/reset ownership. Hardware state persists in USB2 registers until reset or suspend. The `role` sysfs file is transient and removed in `remove()`. Delayed or asynchronous behavior is limited to a work item used to publish extcon state outside the spinlocked path.

## Dependencies And Integration Points
The driver integrates with generic PHY, DT OF matching, `of_usb_get_dr_mode_by_phy()`, extcon provider APIs, regulator consumer and regulator driver APIs, reset controls, optional mux consumer support, runtime PM, platform IRQs, and USB controller PHY consumers. Compatible strings bind SoC-specific data for `renesas,rcar-gen3-usb2-phy`, several R-Car/RZ part numbers, and `renesas,rzg2l-usb2-phy`.

## Risks And Test Signals
Risk concentrates around OTG pin availability, VBUS ownership, and shared multi-PHY state. Invalid or conflicting `dr_mode` values disable OTG behavior. IRQ status clearing differs for `vblvl_ctrl` variants, so regressions can break cable changes only on specific SoCs. Runtime PM calls inside regulator and IRQ paths require clocks/resets to be active. Test signals include successful probe with four PHYs, correct phandle translation, host/device role changes through extcon and `role`, VBUS enable/disable behavior with both external and internal regulators, suspend/resume reset restoration, and multi-consumer power sequencing where only the first/last PHY toggles PLL reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb3.c

## Purpose
This is a compact generic PHY driver for the R-Car Gen3 USB3 PHY. It initializes clock source selection, optional spread-spectrum clocking, reset sequencing, and VBUS detection for a single USB3 PHY instance.

## Important APIs, Types, And Functions
`struct rcar_gen3_usb3` stores the MMIO base, created PHY, detected availability of `usb3s_clk` and `usb_extal`, and the optional `renesas,ssc-range` property. `rcar_gen3_phy_usb3_init()` is the only generic PHY callback. `write_clkset1_for_usb_extal()`, `rcar_gen3_phy_usb3_enable_ssc()`, and `rcar_gen3_phy_usb3_select_usb_extal()` implement the USB_EXTAL path, PLL multiplier programming, SSC range selection, PHY reset assertion/deassertion, and clock source writes.

## Control Flow
Probe requires a device tree node, maps one register resource, tries to get and briefly enable `usb3s_clk` and `usb_extal` to determine whether each has a nonzero rate, rejects devices with neither clock source available, enables runtime PM, creates a PHY, reads the optional SSC range, sets driver data, and registers a simple OF PHY provider. During PHY init, if USB3S clock is absent and USB_EXTAL is present, the driver programs the USB_EXTAL clock path and optional SSC setting before enabling VBUS detection unconditionally.

## State And Persistence
The driver keeps only static probe-time state: which clock source was usable and the requested SSC range. Hardware state is programmed on `.init` and persists until reset or later reinitialization. Runtime PM is enabled manually and disabled in remove, but no suspend/resume callbacks are supplied here.

## Dependencies And Integration Points
It depends on generic PHY, platform MMIO resources, optional clock providers named `usb3s_clk` and `usb_extal`, DT property `renesas,ssc-range`, runtime PM, and compatible string `renesas,rcar-gen3-usb3-phy`.

## Risks And Test Signals
Unsupported SSC values log an error and skip SSC setup without failing init, so board validation should confirm actual spread-spectrum requirements. Clock detection depends on prepare/enable and nonzero rates, so clock tree mistakes fail probe only when both paths look absent. Test signals include probe acceptance with either clock source, correct fallback to USB_EXTAL when `usb3s_clk` is unavailable, valid SSC ranges 4980/4492/4003, VBUS detection write, and provider resolution by USB3 controller consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rzg3e-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rzg3e-usb3.c

## Purpose
This driver initializes the Renesas RZ/G3E USB3 PHY test/control register block. It performs both USB2 test PHY setup and USB3 test PHY setup, provides a single generic PHY, and handles noirq system sleep reset sequencing.

## Important APIs, Types, And Functions
`struct rz_usb3` tracks the MMIO base, shared reset control, and `skip_reinit` flag used after resume. `rzg3e_phy_usb2test_phy_init()` programs UTMI control, pre-emphasis, OTG tune, SIDDQ release, and port resets. `rzg3e_phy_usb3test_phy_init()` drives CREG/RST/CLK/LANE registers, waits for SRAM init with `readl_poll_timeout_atomic()`, and releases override state. `rzg3e_phy_usb3_init_helper()` composes both halves. `rzg3e_phy_usb3_init()` is the generic PHY callback.

## Control Flow
Probe maps MMIO, obtains a shared reset already deasserted, enables runtime PM through `devm_pm_runtime_enable()`, creates the PHY, attaches driver data, and registers a simple provider. A normal PHY init runs the helper unless `skip_reinit` is true. System suspend drops runtime PM usage, asserts reset, and clears `skip_reinit`. Resume deasserts reset, resumes runtime PM, executes the full init helper immediately, then sets `skip_reinit` so the next PHY `.init` does not duplicate the hardware sequence.

## State And Persistence
The only persistent software state is `skip_reinit`, which bridges system resume and the generic PHY user's later init call. Register programming is volatile hardware state. Reset assertion on suspend clears the PHY, and resume deliberately restores it before normal users run.

## Dependencies And Integration Points
The driver uses generic PHY, platform MMIO resources, reset controller APIs, runtime PM, delay and polling helpers, and compatible string `renesas,r9a09g047-usb3-phy`. It is consumed by USB controller nodes through a simple OF PHY phandle.

## Risks And Test Signals
Initialization is timing and poll sensitive; a failure to observe `USB3_TEST_RAMCTRL_SRAM_INIT_DONE` fails PHY init/resume. Resume uses runtime PM and reset in noirq sleep callbacks, so ordering against USB controller resume is important. Test signals include successful SRAM poll, correct reset deassert/assert sequence, no duplicate reinit after resume, failure unwinding that reasserts reset and drops PM, and USB2/USB3 link bring-up after both cold boot and system sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rzg3e-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/r8a779f0-ether-serdes.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/r8a779f0-ether-serdes.c

## Purpose
This driver exposes the Renesas R-Car S4-8/R8A779F0 Ethernet SERDES as three generic PHY channels for Ethernet MAC consumers. It performs a shared black-box hardware initialization sequence, channel-specific SGMII/USXGMII programming, speed programming, and link-up monitoring.

## Important APIs, Types, And Functions
`struct r8a779f0_eth_serdes_drv_data` owns the common MMIO base, reset, three channel records, and an `initialized` flag. `struct r8a779f0_eth_serdes_channel` stores channel MMIO, PHY pointer, selected `phy_interface_t`, speed, and index. Register helpers `r8a779f0_eth_serdes_write32()`, `read32()`, and `reg_wait()` select a bank then access or poll offsets. Generic PHY callbacks are `init`, `exit`, `power_on`, `set_mode`, and `set_speed`. `r8a779f0_eth_serdes_xlate()` maps phandle arg 0 to one of three channels.

## Control Flow
Probe maps the common register area, obtains reset, creates three PHYs with per-channel base offsets, and registers an OF PHY provider. It then enables runtime PM and takes a runtime PM reference for the device lifetime. `.set_mode` accepts only `PHY_MODE_ETHERNET` with GMII, SGMII, or USXGMII submodes, though later channel setting only handles SGMII and USXGMII. `.set_speed` records the requested line speed. `.init` runs the common reset/RAM/combination-mode sequence once and marks the shared block initialized. `.power_on` runs late per-channel programming: channel mode table, speed programming, status toggles, and link-up polling/restarts.

## State And Persistence
Software state is the shared `initialized` boolean plus per-channel interface and speed. Hardware programming persists across PHY users until reset or driver exit; `.exit` clears the shared initialized flag rather than reference counting channel users, so multi-channel sequencing depends on generic PHY consumer ordering.

## Dependencies And Integration Points
The driver uses generic PHY, Linux PHY interface mode constants, platform MMIO, reset controller, runtime PM, polling/delay helpers, and compatible string `renesas,r8a779f0-ether-serdes`. It integrates with Ethernet MAC drivers through PHY phandles, `.set_mode`, `.set_speed`, and `.power_on`.

## Risks And Test Signals
The register sequences are explicitly undocumented "black magic", so small changes carry high hardware risk. GMII is accepted in `.set_mode` but not implemented by channel setup/speed paths, so consumers selecting GMII can reach `-EOPNOTSUPP` later. The shared `initialized` flag is not per-channel reference counted. Test signals include all three phandle indices, reset/common init once, SGMII 100/1000 speed writes, USXGMII setup, timeout diagnostics from `reg_wait()`, link-up retry behavior, and concurrent or repeated channel init/exit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/r8a779f0-ether-serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/Kconfig

## Purpose
This Kconfig fragment declares build options for Rockchip PHY drivers under `drivers/phy/rockchip`. It controls which PHY implementations are compiled and which common kernel facilities are selected for each hardware block.

## Important APIs, Types, And Functions
The file is declarative Kconfig. Important symbols in this subset are `PHY_ROCKCHIP_DP`, `PHY_ROCKCHIP_DPHY_RX0`, `PHY_ROCKCHIP_EMMC`, `PHY_ROCKCHIP_INNO_CSIDPHY`, `PHY_ROCKCHIP_INNO_DSIDPHY`, `PHY_ROCKCHIP_INNO_HDMI`, and `PHY_ROCKCHIP_INNO_USB2`. Other folder symbols include NANENG combo, PCIe, Samsung DCPHY/HDPTX, SNPS PCIe3, TYPEC, legacy USB, and USBDP.

## Control Flow
There is no runtime control flow. During configuration, each `tristate` controls whether the corresponding object is omitted, built-in, or modular. `depends on` gates choices to Rockchip architectures, device tree, compile-test cases, clock framework, I/O memory, extcon, USB, or TYPE-C support. `select` pulls in generic PHY, MIPI D-PHY helpers, MFD syscon, reset controller, USB common, and rational arithmetic helpers as needed.

## State And Persistence
Configuration state persists in the kernel `.config`. The choices determine module names and whether downstream platform devices can bind at runtime.

## Dependencies And Integration Points
The Kconfig symbols are consumed by the Rockchip Makefile. They integrate with generic PHY subsystem availability and enforce dependencies needed by source files, such as `COMMON_CLK` for HDMI/USB2 clock providers, `EXTCON` and `USB_SUPPORT` for Innosilicon USB2, and `GENERIC_PHY_MIPI_DPHY` for DPHY drivers.

## Risks And Test Signals
Dependency mistakes appear as build failures under randconfig or missing drivers on Rockchip platforms. Compile-test coverage is uneven: some options require `ARCH_ROCKCHIP && OF`, while others allow `COMPILE_TEST`. Test signals include `make olddefconfig` symbol resolution, module names matching help text, and all selected source files building with their declared dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/Makefile

## Purpose
This Makefile maps Rockchip PHY Kconfig symbols to the object files built by Kbuild.

## Important APIs, Types, And Functions
The file uses standard `obj-$(CONFIG_SYMBOL) += object.o` assignments. In this subset, `CONFIG_PHY_ROCKCHIP_DP`, `DPHY_RX0`, `EMMC`, `INNO_CSIDPHY`, `INNO_DSIDPHY`, `INNO_HDMI`, and `INNO_USB2` map directly to their respective `phy-rockchip-*.o` objects.

## Control Flow
There is no runtime control flow. Kbuild expands each `obj-y` or `obj-m` entry according to the resolved configuration. The ordering is mostly folder-local and does not express runtime dependencies.

## State And Persistence
The only persistent effect is build output selection: enabled built-in objects are linked into the kernel image, and modular objects become loadable modules.

## Dependencies And Integration Points
This file integrates the Kconfig choices with Linux Kbuild. It must stay synchronized with filenames and Kconfig symbol names in the same folder.

## Risks And Test Signals
Risks are mechanical: stale object names cause missing builds, and missing rows make Kconfig-visible drivers unbuildable. Test signals are `make drivers/phy/rockchip/` and randconfig builds that enable each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dp.c

## Purpose
This driver provides the RK3288 DisplayPort/eDP PHY as a generic PHY. It controls a 24 MHz PHY clock and GRF bits for reference-clock selection and SIDDQ power state.

## Important APIs, Types, And Functions
`struct rockchip_dp_phy` stores the device, parent GRF regmap, and `phy_24m` clock. `rockchip_set_phy_state()` is the central helper used by `.power_on` and `.power_off`; it writes GRF high-word update masks and enables/disables the 24 MHz clock. `rockchip_dp_phy_probe()` obtains the clock, forces it to 24 MHz, locates the parent syscon GRF, selects the internal eDP reference clock, creates the PHY, and registers a simple OF provider.

## Control Flow
Probe requires both the PHY node and a parent OF node because the parent supplies the GRF syscon. After clock and GRF setup, it creates one PHY. Power-on clears SIDDQ through GRF and prepares/enables `phy_24m`. Power-off disables the clock first and writes SIDDQ off. Consumers reach the driver through `of_phy_simple_xlate()`.

## State And Persistence
There is no complex software state beyond handles. Hardware power state lives in GRF SIDDQ and ref-clock selection bits; clock framework state tracks `phy_24m` prepare/enable count.

## Dependencies And Integration Points
The driver depends on generic PHY, common clock, Rockchip GRF syscon as parent, regmap, and compatible string `rockchip,rk3288-dp-phy`. It is consumed by the Rockchip display pipeline through a PHY phandle.

## Risks And Test Signals
The main risk is sequencing: power-on writes SIDDQ before clock enable, and error handling returns clock failures after the PHY is already unsuspended in GRF. Test signals include GRF ref-clock selection during probe, 24 MHz clock rate enforcement, successful display link training after PHY power-on, and SIDDQ assertion when the display stack powers down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dphy-rx0.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dphy-rx0.c

## Purpose
This driver controls the RK3399 Synopsys MIPI D-PHY RX0 block used by the ISP camera path. It configures GRF DPHY control/test registers, selects HS frequency range values from the requested MIPI D-PHY configuration, and manages the required clocks.

## Important APIs, Types, And Functions
`struct rk_dphy` holds the device, GRF regmap, bulk clocks, match data, current `phy_configure_opts_mipi_dphy`, and selected HS frequency code. `struct rk_dphy_drv_data` supplies clock names, HS frequency range table, and GRF register descriptions. `rk_dphy_configure()` validates MIPI D-PHY options and selects a range entry. `rk_dphy_enable()` writes the RX0 force/turn/enable bits, resets the test interface, programs lane HS RX control registers, and writes settle timing. Generic PHY callbacks prepare/unprepare clocks in `.init`/`.exit`, enable/disable clocks in power callbacks, and configure MIPI timing.

## Control Flow
Probe locates the parent GRF syscon, loads RK3399 match data, allocates and gets the clock bulk (`dphy-ref`, `dphy-cfg`, `grf`), creates a PHY, and registers a simple provider. A consumer first calls `.configure` with validated lane count and `hs_clk_rate`; the driver maps Mbps to a register code. `.init` prepares clocks, `.power_on` enables clocks and writes the DPHY sequence, and `.power_off` disables lanes and clocks.

## State And Persistence
Software retains the last valid MIPI D-PHY config and `hsfreq` code. Hardware state is GRF and internal test-interface programming. No runtime PM or persistent storage is used.

## Dependencies And Integration Points
The driver uses generic PHY, `GENERIC_PHY_MIPI_DPHY`, regmap/syscon from the parent node, bulk clocks, and compatible string `rockchip,rk3399-mipi-dphy-rx0`. It integrates with camera/ISP receivers through MIPI D-PHY configure and power callbacks.

## Risks And Test Signals
If `.configure` is skipped or chooses no range, power-on may program an invalid zero/default value; consumers should configure before enabling. The range lookup treats an unselected code of zero as invalid, which makes the first table entry with cfg `0x00` unreachable for rates under 89 Mbps. Test signals include config validation failures, lane enable mask for 1-4 lanes, correct clock prepare/enable pairing, CSI capture at representative lane rates, and power-off disabling RX0 lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dphy-rx0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c

## Purpose
This driver controls the RK3399 eMMC PHY through GRF registers. It powers the analog block, calibrates pads, configures DLL frequency range, output tap delay, strobe pulldown, and drive impedance for the eMMC controller.

## Important APIs, Types, And Functions
`struct rockchip_emmc_phy` stores GRF offset/base, optional `emmcclk`, and DT-configured electrical parameters. `rockchip_emmc_phy_power()` performs the shared power-off/power-on sequence, polling CALDONE and DLLRDY. `rockchip_emmc_phy_init()` intentionally gets `emmcclk` late to avoid a circular dependency with the SDHCI clock provider. `rockchip_emmc_phy_power_on()` writes drive impedance, tap delay, and strobe settings before powering the analog block. `convert_drive_impedance_ohm()` maps DT ohm values to hardware codes.

## Control Flow
Probe obtains the parent GRF syscon, reads the child `reg` offset, applies defaults and optional DT properties, creates the PHY, and registers a simple provider. Init obtains the optional eMMC clock. Power-on first programs electrical tuning registers, then forces PDB/ENDLL low, checks the current card clock rate to choose DLL frequency, powers up calibration, polls for CALDONE, enables the DLL, and polls for DLLRDY unless the clock rate is zero. Power-off drives PDB and ENDLL low.

## State And Persistence
Persistent software state is the DT-derived tuning configuration and the late-acquired clock pointer. Hardware state remains in GRF registers until reset or power-off. The clock pointer is released in `.exit`.

## Dependencies And Integration Points
It depends on generic PHY, parent syscon GRF, optional `emmcclk`, platform DT properties `drive-impedance-ohm`, `rockchip,enable-strobe-pulldown`, and `rockchip,output-tapdelay-select`, and compatible `rockchip,rk3399-emmc-phy`. It is used by the MMC/SDHCI controller through a PHY phandle.

## Risks And Test Signals
The late clock lookup is intentional but unusual; failures surface at PHY init rather than probe. DLL lock can take longer than documentation, so polling timeout regressions affect high-speed eMMC modes. Test signals include valid/invalid DT impedance mapping, zero-rate init path, CALDONE and DLLRDY polling, HS200/HS400 tuning stability, and clean clock put on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-csidphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-csidphy.c

## Purpose
This driver controls Rockchip Innosilicon MIPI CSI D-PHY receiver blocks across multiple SoCs. It configures lane enables, THS settle timing, optional calibration, reset controls, pclk/runtime PM, and SoC-specific GRF bits.

## Important APIs, Types, And Functions
`struct rockchip_inno_csidphy` stores MMIO, pclk, GRF regmap, reset bulk, match data, current MIPI D-PHY config, and selected HS frequency code. `struct dphy_drv_data` supplies offsets, HS frequency table, GRF register table, and reset names per SoC. `rockchip_inno_csidphy_configure()` validates MIPI options and chooses HS range. `rockchip_inno_csidphy_power_on()` enables pclk/runtime PM, resets analog/digital logic, enables lanes and optional high-rate calibration, programs THS settle for clock/data lanes, and enables GRF lanes. Power-off disables lanes, powers down PLL/LDO where applicable, and releases PM/clock.

## Control Flow
Probe reads match data, gets `rockchip,grf`, maps PHY registers, gets `pclk`, obtains the variant reset bulk, creates the PHY, registers a provider, and enables runtime PM. Consumers configure MIPI lane/rate values first; power-on then uses that state to program lane masks and timing. Variants cover PX30/RK3326/RK1808/RK3368/RK3568/RK3588 with different pwrctl/calib offsets and reset lists.

## State And Persistence
Software retains the last MIPI config and `hsfreq` code. Runtime PM state is managed per power-on/off, while clocks are prepared in `.init` and enabled in `.power_on`. Hardware state is volatile register programming and GRF lane control.

## Dependencies And Integration Points
The driver uses generic PHY, MIPI D-PHY validation helpers, syscon/regmap via `rockchip,grf`, reset bulk APIs, runtime PM, and platform MMIO. It integrates with CSI receiver/camera pipelines through PHY configure and power callbacks.

## Risks And Test Signals
The range lookup uses zero as the "not found" sentinel, so tables with cfg `0x00` make the lowest range invalid. Lane count must be configured before power-on because masks use `config.lanes`. Optional pwrctl/calib offsets differ by SoC, so missing data can silently skip calibration or power control. Test signals include probe on each compatible, reset count bounds, high-rate calibration above 1500 Mbps, lane masks for 1-4 lanes, runtime PM balance, and camera capture at boundary rates from the HS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-csidphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c

## Purpose
This driver controls Rockchip Innosilicon video combo PHYs used for MIPI DSI D-PHY and LVDS modes. It programs analog, digital, lane, and LVDS register banks, calculates PLL dividers, applies timing tables for several maximum-rate families, and exposes the block through generic PHY mode/configure/power callbacks.

## Important APIs, Types, And Functions
`struct inno_dsidphy` stores clocks, MMIO bases, reset, selected mode, MIPI config, and cached PLL parameters. `struct inno_video_phy_plat_data` selects timing table, max rate, and max lanes. `inno_dsidphy_pll_calc_rate()` searches predivider/feedback divider values from the reference clock. `inno_dsidphy_mipi_mode_enable()` programs PLL, pre-emphasis/VOD, timing counters derived from `phy_configure_opts_mipi_dphy`, and lane enables. `inno_dsidphy_lvds_mode_enable()` programs fixed LVDS PLL and lane state. Generic PHY callbacks are `.set_mode`, `.configure`, `.power_on`, and `.power_off`.

## Control Flow
Probe maps the PHY registers, gets `ref` and `pclk`, obtains the APB reset, creates one PHY, registers a provider, and enables runtime PM. Consumers call `.set_mode` for MIPI D-PHY or LVDS. MIPI consumers must call `.configure`, which validates and stores D-PHY timings. Power-on enables pclk/ref clocks, gets runtime PM, powers bandgap/work logic, and dispatches to MIPI or LVDS setup. Power-off disables analog lanes, PLL/LDO, LVDS drivers, drops runtime PM, and disables clocks.

## State And Persistence
The current mode and MIPI timing config remain in memory between callbacks. PLL divider choices are recalculated and cached on MIPI power-on. Hardware state is register-only and cleared by power-off or reset.

## Dependencies And Integration Points
The driver uses generic PHY, MIPI D-PHY helper validation, clock framework, runtime PM, reset controls, platform MMIO, and compatible data for PX30, RK3128, RK3368, RK3506, RK3568, and RV1126 DSI DPHYs. It integrates with DRM bridge/DSI/LVDS consumers via generic PHY mode, configure, and power calls.

## Risks And Test Signals
MIPI power-on assumes a valid prior `.configure`; LVDS uses fixed dividers and does not validate display mode. The PLL calculation caps output above 1 GHz in its search, while max-rate data changes subsequent programming behavior, so high-rate modes need hardware validation. Error handling in power-on does not unwind clocks/PM if an unsupported mode is selected after enabling them. Test signals include mode rejection for unsupported modes, MIPI timing table boundaries, LVDS bring-up, runtime PM balance, lane count behavior for 2-lane and 4-lane variants, and display link stability across pixel rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-hdmi.c

## Purpose
This driver controls RK3228/RK3328 Innosilicon HDMI PHYs and also registers the PHY pre-PLL as a clock provider for the HDMI pixel clock. It owns PLL rate tables, TMDS configuration tables, post-PLL programming, optional RK3328 ESD interrupt handling, and generic PHY power callbacks.

## Important APIs, Types, And Functions
`struct inno_hdmi_phy` stores MMIO regmap, clocks, PHY, registered `clk_hw`, current pixel/TMDS clocks, chip version, IRQ, and platform ops. `pre_pll_config`, `post_pll_config`, and `phy_config` tables encode supported rates and analog settings. Clock ops for RK3228/RK3328 implement prepare/unprepare, recalc, determine_rate, and set_rate. Generic PHY callbacks use `inno_hdmi_phy_power_on()` and `power_off()`. Variant ops initialize bypass/internal control and program post-PLL/driver settings. RK3328 IRQ handlers detect ESD/AGND events and repower the PHY.

## Control Flow
Probe maps MMIO through regmap, gets and enables `sysclk` and `refpclk`, gets `refoclk`, requests an optional IRQ, creates the PHY, sets bus width 8, runs variant init, registers `pin_hd20_pclk` or `clock-output-names` as a clock provider, and registers the PHY provider. HDMI clock consumers set the pixel clock through the registered clk; the driver selects exact pre-PLL table entries and waits for lock. PHY power-on derives TMDS clock from bus width, looks up post-PLL and analog config, ensures pre-PLL rate is set/enabled, enables `phyclk`, calls variant power-on, and waits for post-PLL lock. Power-off calls variant power-off and disables the PHY clock.

## State And Persistence
The driver caches `pixclock`, `tmdsclock`, and `chip_version`. Hardware state includes pre/post PLL registers, TMDS drive settings, interrupt masks, and clock provider state. `of_clk_del_provider()` runs on remove; sysclk/refpclk are disabled by a devm action.

## Dependencies And Integration Points
It depends on generic PHY, common clock provider APIs, regmap MMIO, optional nvmem cell `cpu-version`, platform IRQs, and clocks `sysclk`, `refpclk`, and `refoclk`. It integrates with DRM HDMI components as both a PHY and a pixel clock provider. Compatible strings are `rockchip,rk3228-hdmi-phy` and `rockchip,rk3328-hdmi-phy`.

## Risks And Test Signals
Supported rates are table-driven; unsupported pixel clocks fail `determine_rate` or pre/post-PLL lookup. RK3228 rejects fractional pre-PLL entries in determine_rate while RK3328 accepts them. IRQ repower assumes cached clocks/config are valid. Test signals include clock rate negotiation for CEA/VESA modes, pre/post PLL lock polling, RK3328 nvmem version handling including defer, ESD IRQ recovery, 10-bit bus-width TMDS scaling, and provider cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-usb2.c

## Purpose
This is the main Rockchip Innosilicon USB2 PHY driver. It supports OTG and host ports across many SoCs, exports a 480 MHz PHY clock, manages extcon cable state, charger detection, linestate/ID/VBUS/host-disconnect interrupts, delayed OTG and host state machines, resets, optional USBGRF register space, and variant-specific tuning/register maps.

## Important APIs, Types, And Functions
`struct rockchip_usb2phy` owns device state, GRF/USBGRF regmaps, input clocks, 480 MHz output clock, reset, extcon, mux IRQ, charger state/type, and per-port state. `struct rockchip_usb2phy_port` stores a PHY, port id, suspend/VBUS/host-disconnect state, IRQs, mutex, delayed works, DT mode, and register config. `struct rockchip_usb2phy_cfg` and nested register tables describe each SoC instance. Register helpers `property_enable()` and `property_enabled()` implement high-word write-mask register access. PHY callbacks handle init, exit, power_on, and power_off. State machines are `rockchip_usb2phy_otg_sm_work()`, `rockchip_chg_detect_work()`, and `rockchip_usb2phy_sm_work()`.

## Control Flow
Probe gets the GRF syscon, optional USBGRF, clocks, reset, match-data config array, extcon, selects the config row matching the node `reg`, enables input clocks with devm cleanup, registers the 480 MHz clock, resets/tunes the PHY, iterates child `host-port` and `otg-port` nodes to create per-port PHYs and IRQ/work state, registers a PHY provider, and optionally requests a combined top-level IRQ. OTG init enables BVALID and ID interrupts and schedules the OTG work unless the port is host-only. Host init enables linestate and optional disconnect IRQs and schedules host work. Power-on enables the 480 MHz clock, clears PHY suspend, resets the PHY, and waits for UTMI stability; power-off sets suspend and disables the clock. Charger detection follows DCD, primary, and secondary phases and reports SDP/CDP/DCP/SLOW through extcon.

## State And Persistence
Software state includes port suspend flags, OTG state, VBUS attachment, charger state/type, DCD retries, host disconnect state, extcon cable states, and delayed work scheduling. Hardware state is spread across GRF/USBGRF registers for suspend, detection enables/status/clear bits, charger comparators, clock output, and SoC tuning. State is not persistent across reset; probe and power callbacks reconstruct it.

## Dependencies And Integration Points
The driver uses generic PHY, common clock provider APIs, extcon provider/notifier APIs, power_supply charger type enums, reset controls, syscon/regmap, platform IRQs, delayed work, USB OF mode parsing, and optional child-node IRQ naming. It binds many compatible strings from `rockchip,px30-usb2phy` through `rockchip,rk3588-usb2phy` and `rockchip,rv1108-usb2phy`, and is consumed by USB host/device controllers plus clock consumers of `clk_usbphy_480m`.

## Risks And Test Signals
This file has the highest integration risk in the subset. Register tables are SoC-specific and selected by `reg`, so DT mismatches can bind the wrong offsets. Workqueues, extcon notifications, and IRQ clear/enable order can race cable changes. Charger detection depends on comparator semantics that differ on RK3576/RK3588. Power-on always resets the PHY after unsuspend, which can affect active consumers if reference counting is wrong. Test signals include probe for every compatible/config row, child port creation, combined and per-port IRQ modes, host autosuspend/resume on linestate, OTG ID/VBUS transitions, charger type classification, 480 MHz clock provider behavior, rk3128/rk3576/rk3588 tuning writes, and cleanup of delayed work on PHY exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-usb2.c -->
