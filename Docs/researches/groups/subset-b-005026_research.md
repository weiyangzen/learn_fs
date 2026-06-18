# Research Report: subset-b-005026

This grouped report covers the requested Broadcom USB PHY and Cadence PHY driver files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.c

Purpose: Implements Broadcom STB USB PHY chip-specific initialization, shutdown, and workaround sequencing behind the generic `brcm_usb_init_ops` interface. It programs USB controller, USB2 MDIO, USB3 MDIO, xHCI EC, and family-specific bit fields for many Broadcom SoC revisions.

Important APIs and functions: Public entry points are `brcm_usb_dvr_init_4908()`, `brcm_usb_dvr_init_7445()`, and the aliases/prototypes declared for 74110, 7216, and 7211B0 in the header. The common operation table `bcm7445_ops` wires `usb_init_ipp()`, `usb_init_common()`, `usb_init_eohci()`, `usb_init_xhci()`, `usb_uninit_common()`, `usb_uninit_eohci()`, `usb_uninit_xhci()`, `usb_get_dual_select()`, and `usb_set_dual_select()`. Internally, `get_family_type()` chooses the best family map from `family_id`; `usb_reg_bits_map_table` maps logical feature selectors to SoC-specific bit masks.

Control flow: The platform driver calls a chip match initializer, which fills `selected_family`, `family_name`, the bit map, and the ops table. Runtime PHY init first applies IPP/IOC strap overrides, then common power-up clears wake state, exits powerdown/IDDQ, sets 64-bit EHCI and endian settings where supported, runs USB2 LDO and eye fixes, enables memory controller interfaces, applies MEMC and overcurrent workarounds, programs DRD/Type-C port mode, and toggles BDC soft reset. USB2 init releases USB20 host reset and applies bridge/keepalive tuning. USB3 init exits IDDQ, starts the PHY PLL sequence, applies PLL/SSC/sigdet/SKIP/AEQ/OTP workarounds, and deasserts xHCI reset. Uninit reverses power state and reset bits.

State and persistence: The file stores immutable mapping tables but mutates persistent MMIO register state in controller and PHY blocks. `brcm_usb_init_params` carries selected family, polarity options, supported/current port mode, mapped register bases, and wake state across calls. Register writes persist until reset, powerdown, suspend, or another init path rewrites them.

Dependencies and integration points: Depends on `brcmstb_get_family_id()`, `brcmstb_get_product_id()`, relaxed/raw MMIO helpers from the header, Linux delay APIs, and the platform driver in `phy-brcm-usb.c`. The MDIO helpers use `USB_CTRL_MDIO`/`MDIO2` and mode bits for USB2 versus USB3 sideband accesses.

Risks: This is timing- and SoC-revision-sensitive hardware code. Zero entries in `usb_reg_bits_map_table` silently skip logical operations, so adding families requires careful selector coverage. `name_to_value()` callers expect table values to match indices; here that remains true for current maps. MDIO page/register writes have no timeout/error feedback. Wrong IPP/IOC polarity, overcurrent suppression, or MEMC workaround handling can produce board-specific failures that look like probe or hotplug instability.

Test signals: Build coverage for all Broadcom compatibles, boot probe logs showing expected family mapping, USB2 and USB3 enumeration, DRD role switching through sysfs, suspend/resume with and without wake IRQ, big-endian MIPS register access, and register traces around USB3 PLL/SSC/OTP workaround paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.h -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.h

Purpose: Defines the shared Broadcom USB PHY initialization contract between the platform PHY driver and chip-specific initialization library. It provides mode constants, register-bank selectors, helper macros, the ops vtable, the parameter/state carrier, and endian-aware MMIO helpers.

Important APIs and types: `USB_CTLR_MODE_HOST`, `USB_CTLR_MODE_DEVICE`, `USB_CTLR_MODE_DRD`, and `USB_CTLR_MODE_TYPEC_PD` encode controller role support. `enum brcmusb_reg_sel` indexes controller, xHCI EC/global, USB PHY, USB MDIO, and BDC EC register bases. `struct brcm_usb_init_ops` is the callback interface used by the platform driver. `struct brcm_usb_init_params` holds mapped register bases, IOC/IPP polarity, role selection, family/product IDs, selected family metadata, selector bit maps, optional PIARB syscon, and wake state. The header declares the SoC initializer functions and inlines wrappers such as `brcm_usb_init_common()` and `brcm_usb_uninit_xhci()`.

Control flow: The header has no standalone driver flow. Callers allocate/fill `brcm_usb_init_params`, call a `brcm_usb_dvr_init_*()` function to install `ops`, and then use the inline wrappers to conditionally dispatch callbacks if present. Register macros build offsets from symbolic names that are defined in the `.c` file.

State and persistence: `struct brcm_usb_init_params` is the persistent software state passed through all PHY init, exit, sysfs, suspend, and resume operations. The inline MMIO helpers perform read/modify/write operations that persist in hardware. The header itself owns no storage except constants and type definitions.

Dependencies and integration points: Includes `linux/regmap.h`; relies on Linux bit/MMIO APIs available through including translation units. The endian-aware `brcm_usb_readl()` and `brcm_usb_writel()` choose `__raw_*` on big-endian MIPS because that platform reverses bus endianness by strap, and use relaxed little-endian I/O elsewhere. It is included by both `phy-brcm-usb.c` and `phy-brcm-usb-init.c`.

Risks: The macros concatenate register and field names, so the implementation file must define exact `USB_CTRL_*` symbols before use. The ops wrappers hide missing callbacks by doing nothing, which is useful for cross-family support but can mask incomplete family bring-up. Any change to `enum brcmusb_reg_sel` order affects register-base arrays and DT resource mapping.

Test signals: Compile all Broadcom PHY variants, probe with old index-based and new named register resources, exercise init/exit paths on big-endian and little-endian platforms, and verify sysfs role selection updates `port_mode` through the ops wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb.c

Purpose: Provides the Linux generic PHY platform driver for Broadcom STB USB PHY blocks. It binds device-tree compatibles to chip-specific init functions, creates USB2 and/or USB3 PHY instances, exposes DRD role sysfs controls, manages clocks and wake IRQs, and coordinates suspend/resume sequencing.

Important APIs and types: `struct brcm_usb_phy_data` is the driver-private state with `brcm_usb_init_params`, PHY objects, clocks, wake IRQ, init count, PM notifier, and lock. `struct match_chip_info` binds an init function plus required/optional register-bank requirements to each compatible. Key callbacks are `brcm_usb_phy_probe()`, `brcm_usb_phy_init()`, `brcm_usb_phy_exit()`, `brcm_usb_phy_suspend()`, `brcm_usb_phy_resume()`, and `brcm_usb_phy_xlate()`. Sysfs attributes are `dr_mode` and optional `dual_select`.

Control flow: Probe gets family/product IDs, applies match-data initialization, reads `brcm,ipp`, `brcm,ioc`, `dr_mode`, `brcm,has-xhci`, and `brcm,has-eohci`, maps required register banks by name or legacy index, obtains clocks, creates PHY objects, registers a wake IRQ if present, applies initial IPP/IOC setup, creates sysfs files, gets optional PIARB syscon, forces the hardware off, and registers the OF PHY provider. Consumer `.init()` calls share common setup through `init_count`: the first init enables clocks and runs `brcm_usb_init_common()`, then each PHY type runs USB2 or USB3-specific init. `.exit()` performs type-specific uninit and tears common state down when the last active PHY exits.

State and persistence: `init_count` tracks shared hardware ownership across USB2 and USB3 consumers. Per-PHY `inited` bits let system resume restore only PHYs that were active. `pm_active` from a global PM notifier makes consumer init/exit no-ops during suspend transitions. `ini.port_mode`, `ini.supported_port_modes`, and `ini.wake_enabled` persist across sysfs and PM paths.

Dependencies and integration points: Integrates Linux platform, PHY, OF, clock, interrupt, sysfs, syscon, suspend notifier, and Broadcom STB SoC ID APIs. It delegates all register-level hardware policy to `phy-brcm-usb-init.c`. PHY phandle translation accepts legacy args `0`/`1` and standard `PHY_TYPE_USB2`/`PHY_TYPE_USB3`.

Risks: `brcm_usb_phy_attrs` is a global array mutated at probe to hide `dual_select`, which can be unsafe if multiple devices with different mode support are ever instantiated. Clock enable errors after earlier enables are not fully unwound in all probe subpaths. `init_count` assumes balanced consumer init/exit calls. Resource name `"crtl"` appears intentionally matching existing DT but is easy to mistype in bindings.

Test signals: Device-tree probe for all compatibles, named and legacy resource mapping, module remove, USB2-only/USB3-only/dual configurations, concurrent PHY consumers, sysfs `dual_select` role changes, wake IRQ system suspend/resume, and clock/reset state after failed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/Kconfig

Purpose: Defines the Kconfig symbols that expose Cadence PHY drivers to kernel configuration: Torrent, MIPI D-PHY TX, MIPI D-PHY RX, Sierra, and Salvo.

Important APIs and symbols: `PHY_CADENCE_TORRENT` depends on OF, HAS_IOMEM, and COMMON_CLK and selects GENERIC_PHY. `PHY_CADENCE_DPHY` and `PHY_CADENCE_DPHY_RX` depend on HAS_IOMEM and OF, select GENERIC_PHY and GENERIC_PHY_MIPI_DPHY, and build `cdns-dphy` or `cdns-dphy-rx` when modular. `PHY_CADENCE_SIERRA` depends on OF, HAS_IOMEM, RESET_CONTROLLER, and COMMON_CLK and selects GENERIC_PHY. `PHY_CADENCE_SALVO` depends on OF and HAS_IOMEM and selects GENERIC_PHY.

Control flow: Kconfig does not execute at runtime. Its selection controls whether the corresponding object files in the Cadence PHY Makefile are compiled and whether dependent PHY framework support is enabled.

State and persistence: Configuration state persists in the kernel `.config`. Choosing `m` versus `y` determines module availability and autoload behavior through OF module aliases in each driver.

Dependencies and integration points: The dependencies match visible driver requirements: MMIO and OF platform probing across all drivers, common clock support for Torrent/Sierra and D-PHY TX, reset controller support for Sierra, and MIPI D-PHY helper validation for TX/RX D-PHY drivers.

Risks: Missing `select GENERIC_PHY_MIPI_DPHY` would break D-PHY helper usage. Underdeclared reset or clock dependencies can create compile/link failures or unusable runtime configurations. Help text is brief, so board integrators must rely on device-tree bindings for detailed compatible and property requirements.

Test signals: `allmodconfig`, `allyesconfig`, and targeted builds for each symbol, plus module autoload on matching DT compatibles, validate the menu wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/Makefile

Purpose: Maps Cadence PHY Kconfig symbols to their driver objects.

Important APIs and symbols: The file builds `phy-cadence-torrent.o`, `cdns-dphy.o`, `cdns-dphy-rx.o`, `phy-cadence-sierra.o`, and `phy-cadence-salvo.o` behind `CONFIG_PHY_CADENCE_TORRENT`, `CONFIG_PHY_CADENCE_DPHY`, `CONFIG_PHY_CADENCE_DPHY_RX`, `CONFIG_PHY_CADENCE_SIERRA`, and `CONFIG_PHY_CADENCE_SALVO`.

Control flow: There is no runtime control flow. Kbuild includes object files only when their config symbols are built-in or modular.

State and persistence: Build selection persists in generated kernel build artifacts and module outputs. The Makefile itself carries no runtime state.

Dependencies and integration points: Integrated with `drivers/phy/Makefile` and the Cadence `Kconfig`. Object names must match module aliases and source files in this directory.

Risks: A stale object mapping causes selected drivers to disappear from builds or produce unresolved symbols. Since each object is standalone, there are no composite object lists here to hide missing source files.

Test signals: Run targeted `make M=drivers/phy/cadence` or full kernel builds with each `CONFIG_PHY_CADENCE_*` as `m` and `y`, then confirm expected `.o` and `.ko` outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy-rx.c -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy-rx.c

Purpose: Implements the Cadence MIPI D-PHY receiver driver used for CSI-2 style RX operation. It validates MIPI D-PHY options, programs RX band selection and power island timing, starts/stops the RX state machine, and waits for clock/data lanes to become ready.

Important APIs and types: `struct cdns_dphy_rx` holds MMIO base, device, and PHY handle. `struct cdns_dphy_rx_band` maps Mbps ranges to hardware band indices. `struct cdns_dphy_soc_data` carries SoC quirks; currently J721E SR1.0 marks `has_hw_cmn_rstb`. The PHY ops are `cdns_dphy_rx_power_on()`, `cdns_dphy_rx_power_off()`, `cdns_dphy_rx_configure()`, and `cdns_dphy_rx_validate()`.

Control flow: Probe maps one resource, creates a generic PHY, registers an OF provider, and enables runtime PM. Validation requires `PHY_MODE_MIPI_DPHY`, confirms the lane rate maps to a supported band, then calls `phy_mipi_dphy_config_validate()`. Configure optionally asserts common lane reset through the wrapper unless SoC matching says hardware owns it, checks one to four lanes, converts `hs_clk_rate` to DDR bit rate, writes left/right band controls, writes mandated data/clock power island values, and polls clock plus active data lane ready bits. Power-on writes `DPHY_CMN_SSM` with RX mode, bandgap timer, and state-machine enable; power-off clears it.

State and persistence: The driver has minimal software state. Hardware configuration persists in PCS/PMA/wrapper registers after `.configure()` and while the PHY remains powered. Lane readiness is observed synchronously; no cached configured flag is kept.

Dependencies and integration points: Uses Linux PHY, MIPI D-PHY validation helpers, OF platform probing, `readl_relaxed_poll_timeout()`, runtime PM, and `soc_device_match()` for TI J721E SR1.0 reset behavior. It binds `cdns,dphy-rx`.

Risks: The SoC condition `if (!soc || (soc_data && !soc_data->has_hw_cmn_rstb))` means unknown SoCs take software common reset; regressions are possible if another integration has hardware-managed reset but lacks socinfo. Unsupported rates return `-EOPNOTSUPP`; boundary behavior is strict against `max_rate`. Configure waits up to 100 ms per lane-ready poll, so failures can slow camera pipeline startup.

Test signals: Build with `CONFIG_PHY_CADENCE_DPHY_RX`, validate reject paths for wrong mode/rate/lane counts, CSI-2 capture at every supported lane count and representative rates, J721E SR1.0 reset behavior, lane-ready timeout logging, and suspend/runtime PM interactions from the consuming CSI host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy.c

Purpose: Implements the Cadence MIPI D-PHY transmitter driver. It computes PLL dividers from requested MIPI D-PHY options, configures PSM and PLL registers for reference or TI J721E integrations, selects the TX band, starts the TX state machine, and exposes a generic PHY provider.

Important APIs and types: `struct cdns_dphy_cfg` caches PLL input/output/fb dividers, actual HS clock, and lane count. `struct cdns_dphy_ops` abstracts integration-specific hooks for probe/remove, PSM divider, clock-lane routing, PLL programming, wakeup time, PLL lock, and common-ready polling. `ref_dphy_ops` uses the reference register layout; `j721e_dphy_ops` programs TI WIZ registers. PHY callbacks are `cdns_dphy_configure()`, `cdns_dphy_validate()`, `cdns_dphy_power_on()`, and `cdns_dphy_power_off()`.

Control flow: Probe selects ops by compatible, maps MMIO, obtains `psm` and `pll_ref` clocks, runs optional integration probe, creates the PHY, and registers the OF provider. Validate/configure require MIPI D-PHY mode, run generic option validation, derive PLL divisors from the reference clock and requested HS bit clock, update the requested `hs_clk_rate` to the achievable rate, and set `wakeup` in microseconds. Power-on requires a configured and not already powered PHY, enables clocks, derives a roughly 1 MHz PSM divider, selects the left clock lane to drive left lanes, writes PLL configuration, maps actual HS rate to a TX band, writes band config, enables TX state machine bits, then waits for optional PLL lock and common-ready hooks. Power-off disables clocks, clears state-machine enable, and clears `is_powered`.

State and persistence: `is_configured` and `is_powered` enforce call ordering. `cfg` persists the last accepted configuration. Hardware PLL, PSM, band, PWM, WIZ, and state-machine registers persist until power-off, reset, or reconfiguration.

Dependencies and integration points: Uses common clock APIs, OF platform probing, reset headers, generic PHY, MIPI D-PHY helpers, and Linux polling helpers. Binds `cdns,dphy` and `ti,j721e-dphy`. Display or DSI consumers drive it through standard PHY configure/power calls.

Risks: `clk_prepare_enable()` return values are not checked individually before later setup. Error handling after clocks are enabled unwinds both clocks but does not clear partially written registers. PLL math rejects reference clocks outside 9.6 MHz to below 150 MHz and HS rates outside 80 Mbps to 2.5 Gbps; consumers must handle exact-rate adjustment. The generic clock-lane hook is optional and unimplemented for current ops, so integrations that need lane routing must add it.

Test signals: MIPI DSI/display bring-up, validation of invalid rates and modes, actual `hs_clk_rate` negotiation, PLL lock/common-ready timeout handling on J721E, repeated configure/power cycles, and build tests for both compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-salvo.c -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-salvo.c

Purpose: Implements the Cadence SALVO legacy USB2/USB3 PHY driver for NXP platforms. It applies a fixed Cadence/NXP bring-up register sequence, tunes USB2 analog behavior, exposes power clock control, and handles a USB device-mode B-session-valid workaround.

Important APIs and types: `struct cdns_reg_pairs` represents 16-bit register/value pairs. `struct cdns_salvo_data` describes register stride and the init table. `struct cdns_salvo_phy` stores the PHY object, optional clock, MMIO base, match data, and USB2 disconnect threshold enum. PHY callbacks are `cdns_salvo_phy_init()`, `cdns_salvo_phy_power_on()`, `cdns_salvo_phy_power_off()`, and `cdns_salvo_set_mode()`.

Control flow: Probe gets match data for `nxp,salvo-phy`, obtains optional `salvo_phy_clk`, reads `cdns,usb2-disconnect-threshold-microvolt` with a 575 mV default, maps the MMIO resource, creates the PHY, and registers an OF provider. Init enables the clock, writes every USB3 register pair from the NXP sequence, sets receiver-detect slow clock, programs USB2 TXVALID gate timing, AFE RX register 5, and disconnect threshold, delays 10 us, then disables the clock. Power-on/off only prepare/enable or disable/unprepare the clock. Set-mode writes USB2 battery charger/session-valid register values for device mode versus other modes on NXP data.

State and persistence: The large init table is immutable. `usb2_disconn` persists the DT-selected threshold. Hardware register writes remain programmed after init; clock state is controlled by init and power callbacks.

Dependencies and integration points: Uses Linux PHY, platform, OF, optional clocks, bitfield helpers, and MMIO. It binds only `nxp,salvo-phy`. USB controller consumers invoke standard PHY init/power/mode calls.

Risks: `cdns_salvo_phy_init()` reads `TB_ADDR_TX_RCVDETSC_CTRL` into `value` but writes only `RXDET_IN_P3_32KHZ`, dropping any other bits in that register. USB2 disconnect threshold programming clears the mask and then assigns only `FIELD_PREP(...)`, also dropping unrelated bits from `UTMI_AFE_RX_REG0`; this may be intentional for documented reset values but is risky for future silicon. The fixed sequence has no readiness polling or error feedback beyond clock enable.

Test signals: Probe on `nxp,salvo-phy`, USB2 and USB3 enumeration, host/device role transitions invoking `.set_mode`, disconnect threshold validation across boards, clock enable reference behavior over repeated init/power cycles, and register dumps compared to Cadence/NXP reference values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-salvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-sierra.c -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-sierra.c

Purpose: Implements the Cadence Sierra multi-protocol PHY driver. It supports PCIe, USB3, SGMII, and QSGMII lane configurations; single-link and two-link multilink layouts; Cadence and TI register strides; reset control; PLL mux and derived refclk clock providers; and large protocol/SSC-specific register programming tables.

Important APIs and types: `struct cdns_sierra_phy` is the top-level device state with regmaps, regmap fields, clocks, reset controls, child PHY instances, lane counts, autoconf/already-configured flags, and clock provider data. `struct cdns_sierra_inst` describes each child link with type, lane count, master lane, reset, and SSC mode. `struct cdns_sierra_data` is match data containing macro ID, block/register shifts, and four table families: PCS common, PHY PMA lane, PMA common, and PMA lane. Main callbacks are `cdns_sierra_phy_probe()`, `cdns_sierra_phy_init()`, `cdns_sierra_phy_on()`, `cdns_sierra_phy_off()`, `cdns_sierra_phy_reset()`, and `cdns_sierra_phy_configure_multilink()`.

Control flow: Probe requires child `phy` or `link` nodes, selects match data for `cdns,sierra-phy-t0` or `ti,sierra-phy-t0`, maps the base, builds regmap windows for common, lane, PHY PCS, and PHY PMA blocks across up to 16 lanes, allocates regmap fields, gets optional divided ref clocks, registers PLL mux and derived-refclk outputs, enables PLL clocks, detects already configured hardware through PMA common ready, optionally enables `phy_clk`, obtains resets, deasserts APB, validates macro ID, parses child link properties unless `cdns,autoconf`, creates child PHYs, validates total lanes, optionally preconfigures two-link multilink, enables runtime PM, and registers the PHY provider. Child init writes table sets for single-link non-autoconf cases. Multilink configuration writes first protocol tables, swaps protocol order for the second link, deasserts SGMII/QSGMII link resets early, then deasserts the shared PHY reset. Power-on deasserts shared reset for single-link, deasserts link reset, waits for ISO link ready for PCIe/USB, waits for PMA common ready, then waits for lane PLL lock.

State and persistence: Child instances preserve DT topology in `phys[]`. `already_configured` switches children to noop ops and prevents `phy_clk` disable on remove paths. `autoconf` skips software table programming. Register tables persist in hardware CDB blocks. Clock provider state persists through registered `clk_hw` objects, with PLL mux parent and derived-refclk enable bits stored in PHY common registers.

Dependencies and integration points: Uses Linux platform, OF child parsing, generic PHY, PM runtime, reset controller, common clock framework, regmap/regmap_field, and Cadence PHY dt-bindings constants. Consumers reference child PHY nodes and may consume exported clocks `pll_cmnlc`, `pll_cmnlc1`, and `refclk_der`.

Risks: This is high blast-radius hardware code because table selection depends on the two-dimensional protocol pairing and SSC mode. Unsupported combinations silently become missing table pointers for some blocks, leaving partial configuration. Error paths must balance manually acquired child reset controls and registered clock providers. `remove()` asserts `phy_rst`/`apb_rst` even when hardware was already configured and those resets may not have been acquired, which depends on reset-control NULL tolerance. Multilink only supports exactly two subnodes.

Test signals: Build for Cadence and TI compatibles, probe with single PCIe/USB/SGMII and two-link PCIe+USB, PCIe+SGMII, PCIe+QSGMII DTs, validate macro ID mismatch handling, PLL clock provider parent switching, derived refclk enable/disable, reset sequencing, PMA common ready and lane PLL timeout logs, and protocol traffic tests such as PCIe link training, USB3 enumeration, and Ethernet link stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-sierra.c -->
