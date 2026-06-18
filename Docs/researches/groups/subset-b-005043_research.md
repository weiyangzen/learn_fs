# subset-b-005043 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-am654-serdes.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-am654-serdes.c

## Purpose
This driver supports the TI AM654x SERDES block as both a generic PHY provider and a small clock provider. It configures the SERDES for PCIe or USB3 use, owns the lane-function mux selection, exposes PHY reset/init/power operations, and registers three SERDES reference-clock mux outputs. It is platform-device and device-tree driven through the `ti,phy-am654-serdes` compatible.

## Important APIs, Types, And Functions
The core state is `struct serdes_am654`, which stores the MMIO-backed `regmap`, allocated `regmap_field` handles, mux control, current PHY type, a single busy flag, and three output clocks. `struct serdes_am654_clk_mux` wraps a common clock `clk_hw` around the shared syscon clock-select register. `serdes_am654_reg_fields[]` maps named SERDES control/status bits such as `PLL_ENABLE`, `PLL_OK`, `CMU_OK_I_0`, `TX0_ENABLE`, `RX0_ENABLE`, and `POR_EN`. Key PHY operations are `serdes_am654_reset()`, `serdes_am654_init()`, `serdes_am654_power_on()`, `serdes_am654_power_off()`, and `serdes_am654_release()`. Clock integration is implemented by `serdes_am654_clk_mux_get_parent()`, `serdes_am654_clk_mux_set_parent()`, and `serdes_am654_clk_register()`.

## Control Flow
Probe maps the SERDES resource, builds a regmap, obtains a mux-control, allocates all regmap fields, registers three clock muxes from `clock-output-names`, adds an OF clock provider, enables runtime PM, creates one generic PHY, and registers an OF PHY provider using `serdes_am654_xlate()`. Translation first delegates to `of_phy_simple_xlate()`, rejects an already-busy SERDES, selects the requested lane function with the mux framework, and records `args[0]` as the PHY type. PHY initialization dispatches to either `serdes_am654_pcie_init()` or `serdes_am654_usb3_init()`, both of which write hardware programming sequences. Power-on enables PLL, enables TX/RX, then polls `CMU_OK_I_0`; power-off disables TX/RX and PLL.

## State And Persistence
The driver stores only runtime state in memory: selected PHY type, busy ownership, regmap fields, clock objects, and mux state. Hardware state persists in SERDES and syscon registers until reset or power loss. `release()` clears `busy`, resets `type` to `PHY_NONE`, and deselects the mux. There is no suspend/resume callback, so consumers and platform PM must tolerate hardware register loss outside normal probe/init paths.

## Dependencies And Integration Points
The code depends on generic PHY, common clock framework, regmap/regmap-field, platform MMIO resources, device-tree clock-output metadata, `ti,serdes-clk` syscon phandle parsing, mux consumer APIs, and runtime PM. It consumes `dt-bindings/phy/phy.h` type IDs and exports clocks through `of_clk_add_provider()`. Consumers receive the same physical SERDES through an OF PHY phandle with PHY type and lane-function selector cells.

## Risks
The single `busy` flag serializes all consumers and can reject valid multi-lane sharing if future hardware use requires concurrent lanes. USB3 initialization is a large hard-coded register recipe with little per-write error handling because the macro discards return values. `serdes_am654_power_on()` does not roll back PLL if TX/RX enable or CMU polling fails. Clock mux programming relies on the static 16-row table matching all legal hardware combinations; missing rows trigger `WARN()` and `-EINVAL`.

## Test Signals
Useful validation includes successful probe with three registered output clocks, correct clock parent switching, PHY xlate rejection for concurrent users, PCIe and USB3 init on hardware, PLL lock and CMU OK polling success, mux deselection after `phy_put()`, and remove path cleanup of the clock provider and runtime PM. Failure injection around regmap-field allocation, mux select, and clock registration should exercise probe unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-am654-serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c

## Purpose
This driver provides generic PHY instances for TI DaVinci DA8xx USB1.1 and USB2.0 PHYs. It controls CFGCHIP2 syscon bits, per-PHY 48 MHz clocks, OTG mode override, and runtime PM so OHCI and MUSB controllers can power and mode-switch their PHYs.

## Important APIs, Types, And Functions
`struct da8xx_usb_phy` holds the device, two `struct phy` objects, two clocks, a CFGCHIP regmap, and the OF provider. USB1.1 operations are `da8xx_usb11_phy_power_on()` and `da8xx_usb11_phy_power_off()`. USB2.0 operations are `da8xx_usb20_phy_power_on()`, `da8xx_usb20_phy_power_off()`, and `da8xx_usb20_phy_set_mode()`. Runtime PM is handled by `da8xx_runtime_suspend()` and `da8xx_runtime_resume()`. `da8xx_usb_phy_of_xlate()` maps OF cell 0 to USB2 and cell 1 to USB1.1.

## Control Flow
Probe obtains the CFGCHIP regmap from platform data or `ti,da830-cfgchip`, gets `usb1_clk48` and `usb0_clk48`, creates both PHYs, stores shared driver data on each PHY, registers an OF provider or legacy `phy_create_lookup()` aliases, writes `PHY_INIT_BITS`, enables runtime PM, then forbids runtime PM by default. USB1.1 power-on enables its clock, clears suspend by setting `CFGCHIP2_USB1SUSPENDM`, and holds a runtime PM reference because USB1.1 may use the USB2.0 output clock as reference. USB2.0 power-on enables the clock and clears `CFGCHIP2_OTGPWRDN`; mode setting writes `CFGCHIP2_OTGMODE_MASK` for host/device/OTG.

## State And Persistence
No persistent software state beyond pointers is stored. Hardware state lives in CFGCHIP2 mode, suspend, power-down, and PLL bits. Runtime resume clears reset/powerdown and turns on the PHY PLL, then polls `CFGCHIP2_PHYCLKGD`; runtime suspend powers down both PHY and OTG paths.

## Dependencies And Integration Points
Dependencies include `linux/mfd/da8xx-cfgchip.h`, syscon/regmap, generic PHY, clocks, runtime PM, OF, and legacy platform lookup. It integrates with OHCI as `"ohci-da8xx"` and MUSB as `"musb-da8xx"` when not using OF.

## Risks
`pm_runtime_get_sync()` in USB1.1 power-on is not checked for errors. Probe allows legacy lookup creation failures to continue as warnings, which can hide non-OF board integration issues. Runtime PM is enabled but forbidden by default, so power savings require userspace policy. Mode override only validates the generic PHY mode, not controller readiness.

## Test Signals
Test with OF and non-OF enumeration, both PHY phandle IDs, clock enable/disable balancing, host/device/OTG mode writes, runtime resume polling for `PHYCLKGD`, and remove cleanup of legacy lookups. Negative tests should cover missing syscon and missing clock resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-dm816x-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-dm816x-usb.c

## Purpose
This driver supports the DM816x USB2 OTG nanoPHY through syscon control registers, a reference clock, generic PHY registration, and legacy `usb_phy` OTG registration. It programs PHY tuning values from the TI kernel and handles runtime power control for two possible PHY instances.

## Important APIs, Types, And Functions
`struct dm816x_usb_phy` stores the syscon regmap, instance number, refclk, legacy `struct usb_phy`, and offsets for shared `usb_ctrl` and per-instance `usbphy_ctrl`. OTG callbacks `dm816x_usb_phy_set_host()` and `dm816x_usb_phy_set_peripheral()` update `struct usb_otg`. Generic PHY init is `dm816x_usb_phy_init()`. Runtime PM callbacks are `dm816x_usb_phy_runtime_suspend()` and `dm816x_usb_phy_runtime_resume()`.

## Control Flow
Probe reads the MMIO resource only to derive the USBPHY control offset, obtains the `"syscon"` phandle regmap, fixes `usb_ctrl` at `0x20`, identifies instance 1 when the derived USBPHY control offset is `0x2c`, allocates an OTG object, prepares `refclk`, enables runtime PM, creates a generic PHY, registers an OF PHY provider, and calls `usb_add_phy_dev()` for legacy USB PHY users. Init warns on non-24 MHz reference clocks, attempts to set PLL reference and sleep bits in the shared USB control register, logs if the register appears writable, and writes TX rise/reference/preemphasis tuning into USBPHY control.

## State And Persistence
The driver keeps instance ID, offsets, and OTG host/gadget pointers in memory. Hardware state is in shared USB_CTRL bits and per-PHY USBPHY_CTRL tuning bits. Runtime suspend disables the instance bit and refclk; runtime resume enables the refclk and instance bit. Remove unregisters the legacy USB PHY, disables runtime PM, and unprepares the clock.

## Dependencies And Integration Points
It uses syscon/regmap, generic PHY, `usb_add_phy_dev()` legacy USB PHY, `usb_otg`, clock APIs, and runtime PM. The compatible is `ti,dm8168-usb-phy`, with a required `syscon` phandle and `refclk`.

## Risks
The comments document uncertain hardware behavior: at least DM816x rev C may ignore USB_CTRL writes. Runtime suspend computes `val = ~BIT(instance)` for a masked update, which works because the mask limits the write but is easy to misread. `usb_add_phy_dev()` return value is ignored, which can hide legacy registration failure. Probe does not call `pm_runtime_disable()` on all later failures after `pm_runtime_enable()`.

## Test Signals
Validation should include both PHY instances, 24 MHz and nonstandard refclk paths, runtime resume/suspend register writes, legacy USB PHY registration and removal, and hardware observation of tuning writes. Failure testing should cover absent syscon, absent refclk, and generic PHY provider registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-dm816x-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-gmii-sel.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-gmii-sel.c

## Purpose
This driver exposes TI CPSW Ethernet port interface selection as generic PHYs. Each PHY represents a CPSW port and programs SoC control-module bits for MII, RMII, RGMII delay modes, SGMII, QSGMII, and USXGMII where supported.

## Important APIs, Types, And Functions
`struct phy_gmii_sel_priv` is controller-wide state with the regmap, SoC data, port count, register offset, and QSGMII main-port mask. `struct phy_gmii_sel_phy_priv` stores per-port ID, selected interface mode, RMII external clock flag, created PHY, and allocated regmap fields. `struct phy_gmii_sel_soc_data` describes port count, feature bits, regfield tables, extra modes, and QSGMII topology. `phy_gmii_sel_mode()` is the primary PHY `.set_mode` implementation. Probe helpers include `phy_gmii_init_phy()`, `phy_gmii_sel_init_ports()`, and `phy_gmii_sel_of_xlate()`.

## Control Flow
Probe selects SoC data by compatible, reads optional `ti,qsgmii-main-ports`, obtains a parent syscon regmap or maps its own MMIO resource, initializes per-port PHYs and regmap fields, then registers an OF PHY provider. OF translation validates the port ID and, on SoCs with RMII clock selection, records the external-clock argument. `phy_gmii_sel_mode()` requires `PHY_MODE_ETHERNET`, converts the Linux `phy_interface_t` submode to a hardware selector value, validates extra-mode support, applies fixed-delay restrictions, stores the mode for resume, and writes mode, RGMII ID, and RMII clock fields as available.

## State And Persistence
Per-port `phy_if_mode` and `rmii_clock_external` are in-memory restore state. Hardware mode bits persist in syscon/MMIO registers until reset. `phy_gmii_sel_resume_noirq()` replays selected modes for ports that have a nonzero stored `phy_if_mode`.

## Dependencies And Integration Points
The driver depends on generic PHY, regmap/regmap-field, OF networking PHY interface mode constants, syscon, and platform MMIO fallback. It is consumed by CPSW Ethernet nodes through PHY phandles and `.set_mode(PHY_MODE_ETHERNET, interface)`. It supports multiple compatibles including AM33xx, DRA7, DM814, AM654, J7200 CPSW5G, J721E CPSW9G, and J784S4 CPSW9G.

## Risks
Resume restore skips modes encoded as zero because `phy_if_mode` is tested as truthy; if a valid interface enum has value zero, it will not be restored. The debug message in xlate references `args->args[1]` even when the RMII feature is absent and `args_count` may be 1. Fixed-delay SoCs reject RGMII ID/TXID modes, which is correct but can surprise device-tree users. QSGMII main-port defaults to port 1 if properties are omitted.

## Test Signals
Tests should verify each supported interface mode, unsupported extra modes per SoC, QSGMII main/sub-port selection, RMII external clock argument validation, syscon and MMIO resource paths, and noirq resume replay. Device-tree binding tests should catch missing cells and invalid `ti,qsgmii-main-ports`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-gmii-sel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-j721e-wiz.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-j721e-wiz.c

## Purpose
This is the TI WIZ SERDES wrapper driver for J721E-family, AM64, J7200, J784S4, and J721S2 SoCs. It owns wrapper registers around a Cadence/TI SERDES child, registers WIZ clocks, provides resets for the whole SERDES and individual lanes, configures lane modes, handles Type-C lane swap, and instantiates the child `serdes` platform device.

## Important APIs, Types, And Functions
`struct wiz` is the central state: wrapper and optional SCM regmaps, many regmap fields, input and output clocks, lane types, master lane numbers, reset controller, Type-C GPIO, child SERDES device, and saved mux state. `struct wiz_data` selects variant-specific mux fields and clock tables. Clock wrappers include `struct wiz_clk_mux`, `struct wiz_clk_divider`, and `struct wiz_phy_en_refclk`. Key routines are `wiz_regfield_init()`, `wiz_clock_probe()`, `wiz_clock_register()`, `wiz_clock_init()`, `wiz_init()`, `wiz_mode_select()`, `wiz_p_mac_div_sel()`, and reset ops `wiz_phy_reset_assert()` / `wiz_phy_reset_deassert()`.

## Control Flow
Probe obtains the child `serdes` resource, maps it into a regmap, optionally obtains `ti,scm`, reads `num-lanes`, parses Type-C direction GPIO/debounce, reads lane protocol data from child `phy`/`link` nodes, allocates all fields, enables SCM override where present, registers a reset controller with `num_lanes + 1` resets, enables runtime PM, registers clocks, checks whether lanes are already configured, initializes the wrapper if needed, and creates the child SERDES platform device. Initialization resets WIZ, selects DP/QSGMII/USXGMII standard modes, programs MAC dividers for Ethernet SERDES lanes, and enables raw interface auto-start. Reset deassertion handles Type-C lane swaps before releasing full SERDES reset and configures lane enable/full-rate divider for lane resets.

## State And Persistence
State includes parsed lane PHY types, master lane numbers, clock provider registrations, optional Type-C direction delay, and saved mux select values during noirq suspend. Hardware state resides in wrapper lane control, top control, reset, Type-C, and optional SCM registers. Resume restores mux fields, re-enables SCM override, reinitializes clocks, and reruns WIZ init.

## Dependencies And Integration Points
The driver depends on regmap/regmap-field, common clock, reset-controller, runtime PM, GPIO descriptor, OF platform child creation, syscon SCM, and `dt-bindings/phy/phy-ti.h` output clock IDs. It integrates with a child SERDES node, downstream SERDES PHY drivers, clock consumers, and reset consumers that request reset ID 0 for full SERDES or ID N for lane N-1.

## Risks
`wiz_mode_select()` assigns multiple `ret` values for USXGMII before checking only the final write, so earlier register write failures can be lost. Probe enables runtime PM and calls `pm_runtime_get_sync()` but error unwind paths are subtle around clock registration and child creation. Clock provider cleanup differs by WIZ type, so variant mistakes can leak providers. Type-C lane swap policy depends on GPIO timing or master-lane assumptions and can misroute USB3 if device tree lane metadata is wrong.

## Test Signals
Validation should cover each compatible variant, one- and two-refclk clock topologies, SCM override paths, child SERDES creation/destruction, full and per-lane reset behavior, Type-C GPIO debounce and static lane swap, suspend/resume restoration of mux selections, and lane-type parsing from child nodes. Register-write fault injection should target regfield allocation, clock registration, and USXGMII mode writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-j721e-wiz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-control.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-control.c

## Purpose
This driver represents the OMAP/TI control-module PHY registers that are shared by other PHY drivers. It exports helper APIs to power USB2, PIPE3, PCIe, and OTGHS PHY blocks and to program the PCIe PCS delay count or OTGHS mailbox mode bits.

## Important APIs, Types, And Functions
The exported functions are `omap_control_pcie_pcs()`, `omap_control_phy_power()`, and `omap_control_usb_set_mode()`. The code uses `struct omap_control_phy` from `linux/phy/omap_control_phy.h` to store mapped control registers, clock, and type. Private helpers `omap_control_usb_host_mode()`, `omap_control_usb_device_mode()`, and `omap_control_usb_set_sessionend()` update OTGHS mailbox bits.

## Control Flow
Probe selects a type from the OF match data, maps either the `otghs_control` register for OTGHS or the `power` register for other types, obtains `sys_clkin` for PIPE3/PCIe power-frequency programming, maps `pcie_pcs` for PCIe, and stores driver data. `omap_control_phy_power()` validates the device and type, reads the power register, updates type-specific powerdown, VBUS detect, OTG detect, or PIPE3 command/frequency bits, then writes the result back. `omap_control_usb_set_mode()` only acts for OTGHS and writes host/device/disconnect mailbox states.

## State And Persistence
Software state is the control module type, mapped register pointers, and optional system clock. The helper functions directly mutate control-module registers; there is no PM callback or cached restore path here. Register state persists only according to platform reset and retention behavior.

## Dependencies And Integration Points
This code is loaded early with `subsys_initcall()` so dependent PHY drivers can look it up. It integrates with `phy-omap-usb2.c` and `phy-ti-pipe3.c` through exported symbols and `ctrl-module` phandles, and with PCIe users that need the PCS delay helper. It depends on platform named resources, OF match data, and clock APIs.

## Risks
The API is void and logs errors instead of returning failures, so callers cannot directly detect failed or unsupported control writes. Register updates use raw `readl()`/`writel()` without locking; shared control module callers must avoid concurrent conflicting writes. Missing or wrong clock rate for PIPE3/PCIe affects programmed power frequency. Probe returns `-EINVAL` for missing `sys_clkin` rather than preserving `-EPROBE_DEFER`.

## Test Signals
Test each compatible type with required named resources, verify exported helper writes for on/off and OTG modes, check PCIe PCS delay programming, and validate dependent drivers still probe when the control module is registered at subsys init. Fault tests should cover invalid device pointers and mismatched helper/type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c

## Purpose
This driver supports OMAP, DRA7x, AM437x, and AM654 USB2 PHYs as both generic PHYs and legacy `usb_phy` devices. It manages PHY clocks, power control through either syscon or the OMAP control module, optional OTG comparator callbacks, false-disconnect calibration, and an AM65x charger-detect erratum workaround.

## Important APIs, Types, And Functions
`struct omap_usb` stores the legacy `usb_phy`, optional `phy_companion`, mapped PHY base, control device, clocks, flags, syscon power register metadata, and on/off masks. `struct usb_phy_data` provides per-compatible labels, flags, and power bit values. Public integration is `omap_usb2_set_comparator()`. Generic PHY ops are `omap_usb_init()`, `omap_usb_exit()`, `omap_usb_power_on()`, and `omap_usb_power_off()`. OTG callbacks include `omap_usb_set_vbus()`, `omap_usb_start_srp()`, `omap_usb_set_host()`, and `omap_usb_set_peripheral()`.

## Control Flow
Probe reads match data, allocates `omap_usb` and `usb_otg`, maps the PHY resource, initializes errata flags, tries `syscon-phy-power` and otherwise obtains a `ctrl-module` platform device, gets wakeup and optional reference clocks with legacy-name fallbacks, configures OTG callbacks based on flags, enables runtime PM, creates a generic PHY, powers it off initially, registers an OF PHY provider, and registers the legacy USB PHY. Init enables clocks, applies false-disconnect latch calibration when requested, and disables charger detection on affected AM65x SR1.0 devices. Power calls update syscon bits or call `omap_control_phy_power()`.

## State And Persistence
Driver state includes flags, clock handles, comparator pointer, control/syscon references, and power masks. Hardware state includes PHY analog config, charger-detect register, and power-control bits. Clocks are enabled during generic PHY init and disabled in exit. There is no explicit suspend/resume; runtime PM is enabled but the actual PHY power path is controlled by generic PHY operations.

## Dependencies And Integration Points
It depends on generic PHY, legacy USB PHY registration, syscon/regmap, OMAP control PHY exported helpers, clocks, platform resources, OF, runtime PM, and `soc_device_match()` for AM65x SR1.0. MUSB/OTG users can interact through either generic PHY or legacy `usb_phy` APIs.

## Risks
`omap_usb_init()` ignores the return from `omap_usb2_enable_clocks()`, which can lead to register writes with clocks unavailable. If `syscon-phy-power` is missing, the control module phandle is mandatory and probe can fail on legacy or incomplete DTs. Optional clock fallbacks preserve old DT compatibility but increase configuration ambiguity. `usb_add_phy_dev()` return value is ignored.

## Test Signals
Tests should cover every compatible's mask/on/off values, syscon and control-module power paths, clock fallback names, comparator VBUS/SRP callbacks, false-disconnect and charger-detect register writes, AM65x SR1.0 matching, and initial power-off behavior. Build tests should include legacy USB PHY users and generic PHY consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-ti-pipe3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-ti-pipe3.c

## Purpose
This driver supports TI PIPE3 PHYs for USB3 SuperSpeed, SATA, and PCIe. It programs DPLL parameters for supported reference clocks, applies protocol-specific RX calibration settings, coordinates power through syscon or OMAP control-module helpers, and manages protocol clocks and errata workarounds.

## Important APIs, Types, And Functions
`struct ti_pipe3` stores mapped PLL/RX/TX bases, clocks, syscon/control-module references, mode, DPLL map, calibration settings, and SATA refclk state. `struct pipe3_dpll_map` and `struct pipe3_settings` encode rate-dependent PLL values and protocol analog/digital tuning. Generic PHY ops are `ti_pipe3_init()`, `ti_pipe3_exit()`, `ti_pipe3_power_on()`, and `ti_pipe3_power_off()`. Helpers include `ti_pipe3_dpll_program()`, `ti_pipe3_dpll_wait_lock()`, `ti_pipe3_calibrate()`, `ti_pipe3_get_sysctrl()`, and `ti_pipe3_get_clk()`.

## Control Flow
Probe selects mode data by compatible, maps PLL if applicable and RX/TX resources, resolves syscon or control-module power paths plus PCIe PCS and SATA PLL reset syscons, obtains clocks, enables runtime PM, keeps SATA refclk enabled for erratum i783, creates a generic PHY, powers it off, and registers an OF PHY provider. Init enables clocks, handles PCIe PCS delay and returns early for PCIe, otherwise wakes the DPLL from idle, skips SATA DPLL reprogramming if already locked, programs DPLL values by system clock rate, and calibrates RX registers. Power-on writes system-clock frequency and TX/RX power commands, sequencing RX after TX for USB/SATA and together for PCIe.

## State And Persistence
Software state includes the selected mode, DPLL table, register offsets, syscon references, and whether SATA refclk was kept on. Hardware state includes DPLL registers, RX calibration registers, power control bits, PCS delay, and SATA soft reset bits. Exit idles the DPLL, waits for LDO and oscillator powerdown, toggles SATA soft reset when available, then disables clocks.

## Dependencies And Integration Points
Dependencies include generic PHY, OMAP control PHY helpers, syscon/regmap, platform named resources, clocks, runtime PM, and OF match data. It is consumed by USB3, SATA, and PCIe controller nodes through generic PHY phandles.

## Risks
PCIe init returns immediately after programming PCS delay and leaves clocks enabled until exit, which is intended but different from USB/SATA DPLL flow. Clock acquisition rules differ per mode and syscon availability, making DT compatibility fragile. SATA erratum handling intentionally keeps refclk enabled and may affect power. Some `regmap_update_bits()` calls in power-on do not check return values.

## Test Signals
Validation should cover all compatibles, each supported system clock in USB/SATA DPLL maps, PLL lock and idle timeouts, PCIe PCS syscon versus control-module paths, SATA pllreset presence/absence, clock enable/disable balancing, and TX-before-RX sequencing for USB/SATA. Hardware tests should inspect link training for USB3, SATA, and PCIe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-ti-pipe3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-tusb1210.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-tusb1210.c

## Purpose
This ULPI driver supports TI TUSB1210/TUSB1211 USB PHYs. It creates a generic ULPI PHY, controls optional reset/chip-select GPIOs, programs vendor eye-diagram and DP/DM swap settings, switches host/device OTG control bits, and optionally exposes TUSB1211 charger detection as a power-supply device.

## Important APIs, Types, And Functions
`struct tusb1210` stores the ULPI device, created PHY, GPIOs, cached OTG control and vendor-specific register values, and charger-detection state when `CONFIG_POWER_SUPPLY` is enabled. Generic PHY ops are `tusb1210_power_on()`, `tusb1210_power_off()`, and `tusb1210_set_mode()`. ULPI helpers `tusb1210_ulpi_read()` and `tusb1210_ulpi_write()` centralize error logging. Charger detection is implemented by `tusb1210_chg_det_work()` and power-supply callbacks/notifier helpers.

## Control Flow
Probe allocates state, obtains optional `reset` and `cs` GPIOs, asserts both, reads `TUSB1210_VENDOR_SPECIFIC2`, applies optional `ihstx`, `zhsdrv`, and `datapolarity` device properties, writes the result back, optionally starts charger detection, creates the ULPI PHY with `ulpi_phy_create()`, and stores driver data. Power-on asserts GPIOs, waits 50 ms, and restores vendor-specific settings. Mode switching reads `ULPI_OTG_CTRL`, applies host or device bit sequences, caches the final value, and writes it back.

## State And Persistence
The driver caches `otg_ctrl` and `vendor_specific2` so register state can be restored after reset or charger-detection side effects. Charger detection keeps a delayed-work state machine with retry count and last USB type. Hardware state is in ULPI standard and vendor registers plus GPIO-controlled reset/chip select.

## Dependencies And Integration Points
Dependencies include the ULPI bus and register definitions, generic PHY ULPI helper, GPIO descriptor API, device properties, workqueues, runtime PM of the ULPI parent during charger detection, and optional power-supply core. The driver matches TI vendor/product IDs for TUSB1210 and TUSB1211.

## Risks
`tusb1210_power_on()` ignores the vendor-specific restore write return value. Charger detection depends on hard-coded charger power-supply names and is only partial DCP/SDP detection. ULPI errors during charger detection trigger resets and retries, but repeated failures eventually continue with unknown or best-effort state. The PHY mutex is used around charger ULPI transactions, so interactions with normal PHY operations need careful locking.

## Test Signals
Test product ID matching, optional GPIO behavior, property bitfield writes, host/device OTG register sequences, power-cycle restoration of vendor settings, charger detection enablement only on TUSB1211, power-supply property reporting, notifier-driven reconnect/disconnect transitions, and cleanup cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-tusb1210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-twl4030-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-twl4030-usb.c

## Purpose
This driver supports the TWL4030/TPS65950 USB transceiver used with OMAP OTG controllers. It manages internal USB LDOs, TWL USB I2C registers, ULPI mode, VBUS/ID detection interrupts, MUSB mailbox notifications, runtime PM autosuspend, and a generic PHY plus legacy `usb_phy` interface.

## Important APIs, Types, And Functions
`struct twl4030_usb` stores legacy USB PHY state, regulator handles, link status, connection atomic, runtime flags, IRQ, delayed ID workaround work, and OTG mode. Register access helpers include `twl4030_usb_write()`, `twl4030_usb_read()`, `twl4030_usb_set_bits()`, `twl4030_usb_clear_bits()`, and verified writes through `twl4030_i2c_write_u8_verify()`. Key flows are `twl4030_usb_runtime_resume()`, `twl4030_usb_runtime_suspend()`, `twl4030_usb_irq()`, `twl4030_usb_linkstat()`, `twl4030_phy_init()`, and `twl4030_usb_ldo_init()`.

## Control Flow
Probe reads `usb_mode` from DT or platform data, allocates OTG and driver state, creates a generic PHY/provider, initializes mutex and delayed work, configures TWL LDO registers and regulator handles, registers the legacy USB PHY, creates a `vbus` sysfs attribute, enables runtime PM autosuspend, requests the threaded IRQ, optionally creates a legacy lookup, and drops the initial runtime PM reference. Runtime resume enables regulators in order, clears a VUSB3V1 remap bit, powers the PHY, enables 32 kHz/clock gating, opens I2C access, sets ULPI mode, closes I2C access, and delays 50 ms. IRQ reads PM master hardware conditions, classifies VBUS/ID status, updates runtime PM reference count and MUSB mailbox state, schedules ID workaround polling, and notifies sysfs.

## State And Persistence
The driver tracks current `linkstat`, whether VBUS is externally supplied, whether a MUSB mailbox update is pending, runtime suspend/resume flags, and connection count. Hardware state is in TWL PM/USB module registers and regulator state. Suspend disables the IRQ and may force runtime suspend when disconnected; resume reenables IRQ, resumes if needed, and immediately rechecks cable state.

## Dependencies And Integration Points
Dependencies include TWL MFD I2C helpers, regulator framework, generic PHY, legacy USB PHY, MUSB mailbox, runtime PM, sysfs, platform IRQ, delayed work, and optional legacy platform lookup. It integrates tightly with OMAP MUSB OTG and TWL PM hardware condition bits.

## Risks
The driver mixes legacy USB PHY, generic PHY, IRQ, runtime PM, and regulator control, so ordering bugs can be hard to diagnose. Several TWL I2C writes in LDO init and resume ignore return values. Probe declares `err` without initializing it before the optional platform-data lookup path; with pure DT and no pdata the later `if (err)` can consume an indeterminate value. Cable detection treats self-driven VBUS specially and depends on register accessibility while clocks may be gated.

## Test Signals
Validation should include DT and platform-data probe, regulator sequencing, runtime autosuspend/resume, IRQ connect/disconnect for VBUS and ID grounded, MUSB mailbox retry behavior, sysfs `vbus` updates, system suspend/resume with cable changes, generic PHY init/power-on scheduling, and remove cleanup of work, sysfs, runtime PM, and OTG power bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/phy-twl4030-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/xilinx/Kconfig

## Purpose
This Kconfig file defines the Xilinx PHY driver menu entries under the kernel PHY subsystem. Its only option in this source snapshot is `PHY_XILINX_ZYNQMP`, which enables support for the ZynqMP High Speed Gigabit Transceiver.

## Important APIs, Types, And Functions
The significant symbol is `CONFIG_PHY_XILINX_ZYNQMP`, a tristate option named "Xilinx ZynqMP PHY driver". It depends on `ARCH_ZYNQMP || COMPILE_TEST` and selects `GENERIC_PHY`, ensuring the generic PHY framework is available when the driver is enabled.

## Control Flow
Kconfig evaluation exposes the option when building for ZynqMP or compile-testing. Selecting the symbol feeds the Makefile rule that builds `phy-zynqmp.o`. There is no runtime control flow in this file, but it controls whether the corresponding platform driver can be built in, built as a module, or omitted.

## State And Persistence
The file contributes build-time configuration state only. The chosen tristate value persists in the kernel `.config` and affects object inclusion.

## Dependencies And Integration Points
It integrates with `drivers/phy/xilinx/Makefile`, the top-level PHY Kconfig inclusion, and the generic PHY subsystem. The dependency on `COMPILE_TEST` broadens build coverage beyond ZynqMP machines.

## Risks
The option selects only `GENERIC_PHY`; other runtime dependencies such as clocks, debugfs, PM, OF, and MMIO are assumed available through broader kernel configuration. Misconfigured builds for non-OF environments may compile but not produce useful runtime hardware support.

## Test Signals
Build tests should verify `n`, `m`, and `y` configurations, both native `ARCH_ZYNQMP` and `COMPILE_TEST`, and that enabling the symbol compiles `phy-zynqmp.o` without missing framework dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/xilinx/Makefile

## Purpose
This Makefile connects the Xilinx PHY Kconfig symbol to the object built by kbuild. It is intentionally minimal and currently builds only the ZynqMP GT PHY driver.

## Important APIs, Types, And Functions
The single rule is `obj-$(CONFIG_PHY_XILINX_ZYNQMP) += phy-zynqmp.o`. It uses standard kbuild conditional object syntax.

## Control Flow
During kernel build, kbuild expands `obj-y` or `obj-m` depending on the resolved value of `CONFIG_PHY_XILINX_ZYNQMP`. If the symbol is disabled, no object is included from this Makefile.

## State And Persistence
There is no runtime state. Build inclusion is derived entirely from `.config`.

## Dependencies And Integration Points
The rule integrates with `drivers/phy/xilinx/Kconfig` and the parent PHY Makefile that descends into the Xilinx directory. The object corresponds to `phy-zynqmp.c`.

## Risks
Adding future Xilinx PHY drivers requires updating both Kconfig and this Makefile. A symbol/object mismatch would silently omit or fail the intended driver build.

## Test Signals
The main signal is a successful kernel or module build with `CONFIG_PHY_XILINX_ZYNQMP=y` and `=m`, and absence of `phy-zynqmp.o` when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/phy-zynqmp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/xilinx/phy-zynqmp.c

## Purpose
This driver supports the Xilinx ZynqMP PS-GTR high-speed transceiver block. It exposes four lanes as generic PHYs for USB3, SATA, DisplayPort, PCIe, and SGMII, configures reference clocks and spread-spectrum PLL settings, validates lane/controller mappings, applies protocol-specific initialization, and saves/restores hardware state across runtime PM.

## Important APIs, Types, And Functions
`struct xpsgtr_dev` stores controller resources, four lane objects, four reference clocks, mutex, TX termination workaround flag, saved ICM registers, and saved lane registers. `struct xpsgtr_phy` represents one lane with protocol, instance, lane number, refclk, and `skip_phy_init`. `struct xpsgtr_ssc` maps reference clock rates to PLL/SSC settings. Generic PHY ops are `xpsgtr_phy_init()`, `xpsgtr_phy_exit()`, `xpsgtr_phy_power_on()`, and `xpsgtr_phy_configure()`. Important helpers include `xpsgtr_configure_pll()`, `xpsgtr_lane_set_protocol()`, `xpsgtr_phy_tx_term_fix()`, protocol init routines for DP/SATA/SGMII, and OF translation `xpsgtr_xlate()`.

## Control Flow
Probe maps `serdes` and `siou` resources, gets optional `ref0` through `ref3` clocks, creates four PHYs with debugfs status files, registers the OF PHY provider, enables runtime PM, resumes the device, and allocates saved-register storage. Consumers pass four cells: lane, PHY type, instance, and refclk. Xlate validates cell count, lane, type/instance range, reference clock index, and ICM matrix allowance, then records protocol and refclk in the lane. PHY init enables the selected refclk, skips USB reinit when resume marked it safe, optionally performs TX termination calibration, configures PLL/SSC, writes ICM protocol, and applies DP/SATA/SGMII-specific settings. Power-on waits for PLL lock.

## State And Persistence
Per-lane software state records protocol, instance, selected refclk, and whether init can be skipped after resume. Runtime suspend saves ICM registers and a fixed list of lane registers. Runtime resume restores lane registers, compares current ICM config to saved values, and sets `skip_phy_init` for all lanes if the configuration survived. Clocks are reference-counted through generic PHY init/exit.

## Dependencies And Integration Points
The driver depends on generic PHY, OF phandle translation, clocks, runtime PM, debugfs, MMIO resources, and `dt-bindings/phy/phy.h`. It integrates with USB, SATA, DP, PCIe, and Ethernet controller nodes through PHY phandles. The SIOU resource is used for SATA lane selection.

## Risks
The ICM matrix validation loop checks only whether any controller slot equals the requested instance, not whether the slot corresponds to the requested protocol, so invalid protocol/lane combinations may pass when instance numbers overlap. Probe allocates `saved_regs` after `pm_runtime_resume_and_get()` and does not unwind the runtime PM reference on allocation failure. `clk_prepare_enable()` failure in PHY init jumps out without returning the actual error. DP configuration indexes static `[pre][voltage]` tables without range checks in this driver.

## Test Signals
Test all valid lane/protocol/refclk phandle combinations, invalid cell counts and out-of-range values, PLL setup for each supported refclk rate, DP configure values, SATA SIOU writes, SGMII bus width/scrambler bypass, TX termination workaround on matching silicon, runtime suspend/resume skip behavior, debugfs status contents, and clock enable/disable balancing on init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/xilinx/phy-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/Kconfig

## Purpose
This file defines the main kernel pinctrl subsystem menu and many top-level pin controller driver symbols. It enables core pinctrl capabilities, generic helper libraries, debug support, and platform/PMIC/GPIO-expander pinctrl drivers, then sources vendor subdirectory Kconfig files.

## Important APIs, Types, And Functions
Core symbols include `PINCTRL`, `GENERIC_PINCTRL_GROUPS`, `PINMUX`, `GENERIC_PINMUX_FUNCTIONS`, `PINCONF`, `GENERIC_PINCONF`, `GENERIC_PINCTRL`, and `DEBUG_PINCTRL`. Driver symbols in this file include AMD, Apple, AT91, AXP, DA850, Microchip, Rockchip, SCMI, single-register, TPS6594, Zynq, ZynqMP, BlueField, RP1, and others. Each symbol declares dependencies and selects required subsystems such as `GPIOLIB`, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `REGMAP`, or IRQ helpers.

## Control Flow
When `PINCTRL` is enabled, Kconfig exposes core and driver options. Selected symbols control which objects are compiled by `drivers/pinctrl/Makefile` and which subdirectory Kconfigs are traversed. The bottom of the file sources vendor directories such as `actions`, `qcom`, `ti`, `renesas`, `tegra`, and others.

## State And Persistence
This file defines build-time state only. Values persist in `.config` and determine enabled pinctrl infrastructure and drivers. It does not create runtime state directly.

## Dependencies And Integration Points
The file integrates pinctrl with GPIO, IRQCHIP, OF, ACPI, MFD, firmware, regmap, architecture symbols, and compile-test coverage. Its sourced Kconfig files extend the menu for vendor-specific drivers. The selected generic helpers must match object rules in the pinctrl Makefile.

## Risks
Because many drivers select common infrastructure, dependency mistakes can create unexpected large builds or missing symbols. Compile-test options broaden coverage but may expose drivers on architectures without meaningful runtime hardware. The menu is a central integration point; ordering and source path mistakes can hide entire vendor families.

## Test Signals
Useful signals include `olddefconfig`/`allyesconfig`/`allmodconfig` coverage, targeted builds for key symbols, dependency cycle checks, menu visibility for architectures and `COMPILE_TEST`, and consistency between each Kconfig symbol and Makefile object rule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/Makefile

## Purpose
This Makefile builds the pinctrl core, optional generic infrastructure, top-level pinctrl drivers, and vendor subdirectories. It is the kbuild counterpart to `drivers/pinctrl/Kconfig`.

## Important APIs, Types, And Functions
Core object rules include always-built `core.o` and `pinctrl-utils.o`, plus conditional `pinmux.o`, `pinconf.o`, `pinconf-generic.o`, `pinctrl-generic.o`, and `devicetree.o`. `subdir-ccflags-$(CONFIG_DEBUG_PINCTRL) += -DDEBUG` turns on debug instrumentation. Many driver rules map `CONFIG_PINCTRL_*` symbols to objects, and subdirectory rules include vendor directories such as `actions/`, `bcm/`, `qcom/`, `ti/`, and `tegra/`.

## Control Flow
kbuild always enters the pinctrl directory when selected by the parent build. It compiles unconditional core objects, expands conditional objects based on `.config`, and descends into subdirectories according to unconditional `obj-y` or architecture/config-gated rules. Modules versus built-ins are inherited from symbol tristate values.

## State And Persistence
There is no runtime state. Build state is the set of object files and subdirectories selected from `.config`.

## Dependencies And Integration Points
It integrates with top-level kernel kbuild, `drivers/pinctrl/Kconfig`, generic pinctrl source files, and vendor driver directories. The OF rule ties `CONFIG_OF` to pinctrl devicetree parsing support.

## Risks
The file has many one-to-one symbol/object mappings; stale rules can build removed files or omit enabled drivers. Some subdirectories are always traversed (`obj-y`) even though their internal Makefiles may select no objects, so subdirectory build hygiene matters. Debug flags apply across the subdirectory and can change diagnostics globally.

## Test Signals
Build `PINCTRL` with minimal core, with `PINMUX`, with `PINCONF`, with `CONFIG_OF`, and with representative driver symbols as built-in and module. `allmodconfig` is a strong signal that Kconfig and Makefile mappings are synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Kconfig

## Purpose
This file defines Kconfig options for Actions Semi OWL pinctrl support and SoC-specific S500, S700, and S900 variants.

## Important APIs, Types, And Functions
`PINCTRL_OWL` is the common boolean driver option. It depends on `(ARCH_ACTIONS || COMPILE_TEST) && OF` and selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `GPIOLIB`, and `GPIOLIB_IRQCHIP`. `PINCTRL_S500`, `PINCTRL_S700`, and `PINCTRL_S900` are SoC-specific booleans depending on the common OWL driver plus ARM or ARM64/compile-test constraints.

## Control Flow
When the parent pinctrl Kconfig sources this file, users can enable the common OWL pinctrl core and then the desired SoC data driver. The selected symbols feed `drivers/pinctrl/actions/Makefile`, which builds `pinctrl-owl.o` and the selected variant object.

## State And Persistence
The file defines build-time configuration only. Enabled symbols persist in `.config` and determine which Actions pinctrl objects are compiled.

## Dependencies And Integration Points
It integrates with the pinctrl, pinmux, pinconf, GPIO, and IRQ-capable GPIO frameworks. The OF dependency reflects device-tree based probing for Actions SoCs. The architecture dependencies keep SoC-specific drivers visible primarily on expected CPU families while allowing compile testing.

## Risks
The SoC symbols depend on `PINCTRL_OWL`; selecting a variant without the common driver is not possible, which is intentional. Because all symbols are bool, they cannot be built as modules even if the rest of pinctrl is modular. Missing defaults mean platform configs must explicitly select the relevant variant.

## Test Signals
Build tests should cover `PINCTRL_OWL` alone and each S500/S700/S900 variant, including `COMPILE_TEST`. Dependency checks should confirm variant options disappear when the common driver is disabled and appear on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Makefile

## Purpose
This Makefile maps Actions Semi OWL pinctrl Kconfig symbols to their kbuild objects.

## Important APIs, Types, And Functions
The rules are `obj-$(CONFIG_PINCTRL_OWL) += pinctrl-owl.o`, `obj-$(CONFIG_PINCTRL_S500) += pinctrl-s500.o`, `obj-$(CONFIG_PINCTRL_S700) += pinctrl-s700.o`, and `obj-$(CONFIG_PINCTRL_S900) += pinctrl-s900.o`.

## Control Flow
kbuild evaluates each object rule according to the corresponding Kconfig boolean. Since the symbols are bool, selected objects build into the kernel image rather than modules.

## State And Persistence
There is no runtime state. The build result is derived from `.config`.

## Dependencies And Integration Points
The file integrates with `drivers/pinctrl/actions/Kconfig` and the parent pinctrl Makefile's `obj-y += actions/` traversal. The common `pinctrl-owl.o` object is expected to provide shared support for variant objects.

## Risks
If a SoC-specific object is selected without matching shared APIs in `pinctrl-owl.o`, build failures occur; the Kconfig dependency is intended to prevent that. Whitespace inconsistencies are harmless but can obscure style checks.

## Test Signals
Build each Actions variant with `PINCTRL_OWL=y`, verify no Actions objects are built when all symbols are disabled, and run compile-test configurations across ARM and ARM64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Makefile -->
