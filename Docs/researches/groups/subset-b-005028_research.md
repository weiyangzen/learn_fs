# subset-b-005028 research

Grouped source research for the PHY driver work item. Each section is delimited for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8mq-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8mq-usb.c

## Purpose
NXP i.MX8MQ/i.MX8MP/i.MX95 USB PHY provider for the Linux generic PHY framework. It initializes USB2/USB3 PHY control registers, powers the PHY with clocks and a `vbus` regulator, applies board-tunable electrical parameters, and optionally registers an i.MX95 Type-C orientation switch for the TCA/XBar block.

## Important APIs, types, and functions
- `struct imx8mq_usb_phy` stores the generic PHY, primary and optional alternate clocks, MMIO base, regulator, optional TCA block, and all parsed tuning values.
- `struct tca_blk` owns Type-C switch state, TCA MMIO base, mutex, and current orientation.
- `imx8mq_usb_phy_init()` is the i.MX8MQ init sequence: assert reset/ATE reset, enable reference SSP, enable TX, then deassert reset.
- `imx8mp_usb_phy_init()` extends init with FSEL/SSC/OTG-disable setup, tuning writes, and optional TCA initialization for i.MX8MP/i.MX95.
- `imx8mq_phy_power_on()` and `imx8mq_phy_power_off()` manage `vbus`, `phy`/`alt` clocks, and RX termination override.
- Tuning helpers translate DT properties such as `fsl,phy-tx-vref-tune-percent`, `fsl,phy-tx-rise-tune-percent`, and `fsl,phy-pcs-tx-swing-full-percent` into packed register fields.

## Control flow
Probe allocates state, gets clocks, maps the primary MMIO resource, selects `phy_ops` from compatible data, creates one generic PHY, gets the `vbus` regulator, optionally maps/registers the TCA switch, parses tuning data, and registers an OF PHY provider. Consumers call `power_on()` before `init()`: power enables the supply and clocks; init programs PHY control fields and deasserts reset. Type-C orientation changes temporarily enable the PHY clock, update TCA mux bits under a mutex, then disable the clock again.

## State and persistence
State is runtime-only in MMIO registers, regulator/clock enable counts, cached tuning fields, and cached Type-C orientation. There is no persistent storage. The TCA mutex protects orientation updates; generic PHY core serialization protects normal PHY ops.

## Dependencies and integration points
Depends on `GENERIC_PHY`, clk, regulator, platform MMIO, OF match data, and `linux/usb/typec_mux.h`. Integrates with USB controller nodes through OF PHY phandles and with Type-C mux users via `typec_switch_register()`. The optional second MMIO resource is i.MX95-specific TCA/XBar control.

## Risks and test signals
Risks include clock/regulator leak on partial `power_on()` failure after regulator enable, SoC-specific tuning conversion mistakes, optional TCA switch registration returning `NULL` instead of an errno on registration failure, and race-prone expectations between Type-C orientation changes and PHY power state. Test by probing all compatibles, exercising suspend/off/on cycles, verifying Type-C normal/reverse/none transitions, checking USB2/USB3 enumeration, and confirming tuning fields with register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8mq-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-hsio.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-hsio.c

## Purpose
Generic PHY provider for i.MX8QM/i.MX8QXP HSIO SerDes lanes. It maps lane phandles to PCIe or SATA PHY modes, selects the correct register windows and clocks per lane/controller, controls reset sequencing, configures refclk pad routing, and polls readiness/PLL lock.

## Important APIs, types, and functions
- `struct imx_hsio_priv` holds shared PHY/CTRL/MISC regmaps, base MMIO, `hsio_cfg`, refclk pad policy, lane array, and `open_cnt`.
- `struct imx_hsio_lane` carries lane index, controller index, offsets, type, selected `phy_mode`, clock bulk data, and its `struct phy`.
- `imx_hsio_init()` resolves lane type from phandle args and fetches/enables five named clocks for the selected PCIe/SATA topology.
- `imx_hsio_power_on()` serializes shared pre-configuration, dispatches to PCIe or SATA power-on, then polls lane PLL lock.
- `imx_hsio_set_mode()` writes HSIO protocol mode and optional PCIe RC/EP device type; `imx_hsio_set_speed()` toggles LTSSM enable.
- `imx_hsio_xlate()` consumes three OF args: lane index, PHY type, and controller index.

## Control flow
Probe maps base plus named `phy`, `ctrl`, and `misc` resources into regmaps, reads `fsl,hsio-cfg` and `fsl,refclk-pad-mode`, creates one PHY per hardware lane, and registers a custom xlate. Init assigns offsets/clocks based on lane topology. First power-on programs shared mux/refclk bits, then per-mode reset paths run: PCIe toggles APB clock and waits for `PM_REQ_CORE_RST` to clear; SATA enables EPCS bits and waits for PMA ready. Both then wait for lane TX PLL lock.

## State and persistence
The driver persists no data outside hardware. Runtime state includes lane mode/type/offsets, enabled clocks, and shared `open_cnt`. The mutex protects shared MISC mux state and `open_cnt`.

## Dependencies and integration points
Uses `dt-bindings/phy/phy.h`, `dt-bindings/phy/phy-imx8-pcie.h`, generic PHY, bulk clk APIs, platform MMIO, and regmap MMIO. Consumers are PCIe and SATA controller nodes that pass HSIO lane parameters via PHY phandles.

## Risks and test signals
Risks include underflowing `open_cnt` if power-off is unbalanced, stale lane configuration if a lane phandle is translated multiple ways, unchecked `devm_platform_ioremap_resource_byname()` error pointers before regmap init, and topology-specific clock-name mistakes. Test by booting all supported HSIO configs, PCIe RC/EP mode setting, SATA link bring-up, repeated bind/unbind/power cycles, and fault-injecting missing named resources/clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-hsio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-lvds-phy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-lvds-phy.c

## Purpose
Mixel LVDS PHY provider for i.MX8QM display links. It exposes two LVDS PHY channels, validates LVDS configuration, sets reference clock rate, coordinates master/slave dual-channel operation, controls channel enable bits, and handles runtime PM power-down/up.

## Important APIs, types, and functions
- `struct mixel_lvds_phy_priv` stores the syscon regmap, reference clock, mutex, and two channel objects.
- `struct mixel_lvds_phy` stores per-channel `phy_configure_opts_lvds`, ID, and generic PHY.
- `mixel_lvds_phy_validate()` enforces `PHY_MODE_LVDS`, 7/10 bits per lane, 3/4 lanes, 25-165 MHz differential clock, and matching master/slave configuration.
- `mixel_lvds_phy_configure()` sets the PHY reference clock to the requested differential clock rate.
- `mixel_lvds_phy_power_on()` programs divider mode from link format, enables one or both channels, and polls `LOCK`.
- Runtime PM callbacks set/clear the `PD` bit and restore initialization fields.

## Control flow
Probe gets the parent syscon regmap and ref clock, enables runtime PM, writes the POR value, creates two PHYs, and registers a custom xlate with one channel index argument. Consumers validate and configure before power-on. Slave channels are passive: the master powers on/off both channels when the companion is marked slave. Power-on holds the lock while setting mode/channel bits and polling PLL lock.

## State and persistence
State is cached per-channel LVDS configuration and MMIO register state. The mutex protects shared regmap access and cached configuration. Runtime PM may power the block down between active uses; no persistent storage is used.

## Dependencies and integration points
Uses generic PHY LVDS configure/validate operations, clk, syscon/regmap, platform device, and runtime PM. Integrates with display bridge/encoder consumers that configure LVDS physical parameters through `phy_configure_opts_lvds`.

## Risks and test signals
Risks include relying on master configuration being cached before slave validation, clock disable on lock failure while still holding shared state, and probe error paths requiring runtime PM disable. Test master-only and dual-channel master/slave display modes, invalid LVDS opts, runtime suspend/resume, and PLL-lock timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8qm-lvds-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-lynx-28g.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-lynx-28g.c

## Purpose
NXP Layerscape Lynx 28G SerDes generic PHY driver. It exposes up to eight Ethernet SerDes lanes, discovers boot-time lane protocols and PLL capabilities, supports runtime switching among SGMII/1000Base-X, 10GBase-R, and USXGMII, controls protocol converters, and periodically recovers lanes that lose CDR lock.

## Important APIs, types, and functions
- `struct lynx_28g_priv` stores MMIO base, PLL/lane arrays, `pcc_lock`, and delayed CDR work.
- `struct lynx_28g_pll` caches reset/control registers and a bitmap of supported lane modes derived from PLL rate.
- `struct lynx_28g_lane` tracks `powered_up`, `init`, lane ID, current mode, and generic PHY.
- `lynx_28g_lane_change_proto_conf()` writes large per-protocol TX/RX equalization, PLL, width, and receiver filter settings.
- `lynx_28g_set_mode()` validates Ethernet submode, halts the lane if needed, disables old converter, remaps PLL/protocol, enables new converter, and restores power.
- `lynx_28g_cdr_lock_check()` runs every second and resets RX when a powered initialized lane loses CDR lock.

## Control flow
Probe maps MMIO, reads both PLL configurations to infer supported modes, creates PHYs either for DT child `phy` nodes or all eight lanes, reads each lane's boot protocol from `LNaPSS`/PCCR, registers an xlate provider, and starts delayed CDR monitoring. `init()` marks a lane managed and powers it off because firmware leaves lanes on. `power_on()` requests TX/RX reset and waits for reset-done bits; `power_off()` issues halt requests and waits for halt completion.

## State and persistence
Runtime state is lane mode, powered/init flags, cached PLL register snapshots, and hardware converter/lane registers. There is no disk persistence. Shared protocol converter registers are protected by `pcc_lock`; delayed work uses each PHY mutex before CDR repair.

## Dependencies and integration points
Depends on generic PHY Ethernet mode APIs, OF/platform MMIO, workqueues, and phandle consumers such as DPAA2 Ethernet MACs. It integrates with firmware-initialized SerDes because it reads initial PSS/PCCR state instead of assuming defaults.

## Risks and test signals
Risks include unbounded busy-wait loops if halt/reset bits never change, limited protocol support compared to defined hardware registers, mode mismatch if firmware PSS encoding changes, and recurring CDR reset churn under marginal links. Test lane creation with and without child nodes, supported/unsupported `phy_set_mode_ext()` submodes, link changes between SGMII/10G/USXGMII, PLL-disabled configurations, and CDR-loss recovery under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-lynx-28g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-samsung-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-samsung-hdmi.c

## Purpose
Samsung HDMI 2.0 transmitter PHY driver for NXP i.MX8MP. It registers a clock provider named `hdmi_pclk`; clock rate selection programs the HDMI PHY PLL using a large fractional lookup table or calculated integer PMS values, then waits for PLL lock.

## Important APIs, types, and functions
- `struct fsl_samsung_hdmi_phy` stores device, MMIO registers, APB/ref clocks, clock hardware, and current PLL configuration.
- `phy_pll_cfg[]` is the fixed table of known fractional-divider pixel clock settings.
- `fsl_samsung_hdmi_phy_find_pms()` searches integer P/M/S dividers with VCO constraints.
- `fsl_samsung_hdmi_phy_find_settings()` chooses exact table match, calculated integer match, or closest available setting within 22.25-297 MHz.
- `fsl_samsung_hdmi_phy_configure()` writes common PHY registers, PLL dividers, lock detector parameters, mode-done bit, and polls `REG34_PLL_LOCK`.
- Runtime PM suspend/resume disables/re-enables APB clock and restores `cur_cfg`.

## Control flow
Probe maps registers, enables the APB clock, gets the ref clock, initializes runtime PM active state, registers a common-clock provider, then releases runtime PM. Clock consumers call determine/set rate. `set_rate()` finds settings and invokes the register programming sequence; resume replays that sequence if a configuration was active.

## State and persistence
Persistent state is only the cached `cur_cfg` pointer used for recalc and resume restore. The calculated config is a static global updated for non-table rates, so concurrent devices would share it. Hardware state lives in PHY registers and APB clock state.

## Dependencies and integration points
Uses common clock framework, platform MMIO, PM runtime, APB/ref clocks, and OF clock provider registration. It integrates with the HDMI display pipeline as a pixel clock source rather than as a generic PHY object.

## Risks and test signals
Risks include global `calculated_phy_pll_cfg` sharing across instances, lookup edge cases around table bounds, integer divider approximation quality, and APB runtime PM sequencing during clock ops. Test exact CEA modes, non-table modes, invalid out-of-range rates, runtime suspend/resume with active mode, and PLL lock timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-samsung-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Kconfig

## Purpose
Kconfig menu entries for HiSilicon PHY drivers covering HI6220/HI3660/HI3670 USB, HI3670 PCIe, STB COMBPHY, INNO USB2, and HIX5HD2 SATA PHY support.

## Important APIs, types, and functions
This file defines build symbols, not C APIs. Symbols are `PHY_HI6220_USB`, `PHY_HI3660_USB`, `PHY_HI3670_USB`, `PHY_HI3670_PCIE`, `PHY_HISTB_COMBPHY`, `PHY_HISI_INNO_USB2`, and `PHY_HIX5HD2_SATA`.

## Control flow
Kconfig selection gates whether corresponding objects are built. Most entries are `tristate`, select `GENERIC_PHY`, and several select `MFD_SYSCON` because drivers use syscon/regmap phandles.

## State and persistence
The selected config symbols persist in the kernel `.config` and control build inclusion. No runtime state exists.

## Dependencies and integration points
Integrates with architecture symbols such as `ARCH_HISI`, `ARM64`, `ARCH_HIX5HD2`, `OF`, `HAS_IOMEM`, and `COMPILE_TEST`. Downstream Makefile maps symbols to object files.

## Risks and test signals
Risks are missing dependencies for drivers using clk/reset/regmap APIs or too-restrictive architecture guards. Test with `allmodconfig`, `COMPILE_TEST`, and target defconfigs to ensure symbol visibility and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Makefile

## Purpose
Build mapping for HiSilicon PHY drivers. It links each Kconfig symbol to its driver object file.

## Important APIs, types, and functions
Uses standard Kbuild `obj-$(CONFIG_...) += file.o` rules for seven PHY objects.

## Control flow
When a config symbol is built-in or module, Kbuild compiles the matching `.c` file into the kernel or module set.

## State and persistence
No runtime state. Build decisions persist only through kernel configuration.

## Dependencies and integration points
Depends on the adjacent Kconfig symbols. Object names match the source files in this work item.

## Risks and test signals
Risk is symbol/object drift if a file is renamed or a Kconfig symbol changes. Test by enabling each symbol and running a kernel build or `make drivers/phy/hisilicon/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3660-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3660-usb3.c

## Purpose
HiSilicon HI3660 USB3 PHY provider. It programs peripheral CRG, PCTRL, and USB OTG BC syscon registers to bring the USB3/USB2 PHY out of reset, select clocks, fake VBUS valid, and apply an eye diagram parameter.

## Important APIs, types, and functions
- `struct hi3660_priv` stores device, three regmaps, and `eye_diagram_param`.
- `hi3660_phy_init()` disables refclk isolation, enables TCXO, asserts/deasserts resets, enables PHY refs, exits IDDQ, fakes VBUS, and writes `USBOTG3_CTRL4`.
- `hi3660_phy_exit()` asserts PHY POR and disables TCXO.
- Probe obtains `hisilicon,pericrg-syscon`, `hisilicon,pctrl-syscon`, parent `usb3-otg-bc` regmap, optional `hisilicon,eye-diagram-param`, and registers one PHY.

## Control flow
After probe, generic PHY consumers call init/exit. Init is strictly sequential; any regmap failure logs and aborts. Delays are fixed for IDDQ exit, reset deassertion, and VBUS validity.

## State and persistence
Runtime state is only the cached eye parameter and syscon register state. No persistent storage or dynamic power-management state is stored.

## Dependencies and integration points
Uses generic PHY, OF, platform driver, `MFD_SYSCON`, and regmap. Integrates with DT via `hisilicon,hi3660-usb-phy` and syscon phandles.

## Risks and test signals
Risks include parent node assumptions for `syscon_node_to_regmap(dev->parent->of_node)`, incomplete cleanup after partial init failure, and fixed timing margins. Test with missing phandles, default/custom eye parameter, USB enumeration, and repeated init/exit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3660-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-pcie.c

## Purpose
Kirin 970/Hi3670 PCIe PHY provider. It coordinates sysctrl/crgctrl/pmctrl syscons, local PHY MMIO, several clocks, PLL programming, IO/ref gating, controller PERST, eye-parameter programming, and NoC power state for PCIe bring-up.

## Important APIs, types, and functions
- `struct hi3670_pcie_phy` holds regmaps, clocks, MMIO base, device, and five eye parameters.
- `hi3670_pcie_get_resources_from_pcie()` obtains the parent PCIe driver's `kirin_pcie_apb` regmap at PHY init time.
- `kirin_pcie_clk_ctrl()` sequences five clocks with rollback on failure.
- `hi3670_pcie_allclk_ctrl()`, `hi3670_pcie_pll_init()`, and `hi3670_pcie_pll_ctrl()` configure and lock FNPLL.
- `hi3670_pcie_phy_power_on()` runs CMOS power, clock/reset, PLL, PERST, pipe clock, eye tuning, and NoC power release.
- `hi3670_pcie_phy_power_off()` disables OE/allclk and drops CMOS power, but intentionally does not disable all clocks due a documented SError risk.

## Control flow
Probe gets global syscon regmaps by compatible, clocks, MMIO, and eye params, then creates a built-in PHY provider. `init()` is not hardware init; it defers APB regmap discovery until the PCIe controller is probed. `power_on()` performs the actual hardware sequence and polls PLL/pipe/NoC status. Failure after clocks are enabled rolls back only through `kirin_pcie_clk_ctrl(false)`.

## State and persistence
State is cached clock/regmap pointers and eye parameters. Hardware state remains in syscon/MMIO registers. No persistent storage exists. There is an intentional power-off asymmetry for critical clocks.

## Dependencies and integration points
Uses generic PHY, clk, regmap/syscon, platform bus lookup, PCIe controller regmap integration, and built-in platform driver registration. It is tightly coupled to the `pcie-kirin` driver registering `kirin_pcie_apb`.

## Risks and test signals
Risks include deferred APB lookup ordering, the `is_pipe_clk_stable()` loop condition depending on active-low semantics, clock leak by design on power-off, and many register writes without rollback. Test PCIe controller probe ordering, link training, suspend/resume/power-off behavior, NoC idle transitions, and custom eye params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-usb3.c

## Purpose
HiSilicon Kirin970/Hi3670 USB3.1 PHY provider. It configures USB2/USB3 clock sources, TCA Type-C adapter state, USB31 PHY CR bus access, fake VBUS, SSC, reset release, eye diagram, and TX vboost.

## Important APIs, types, and functions
- `struct hi3670_priv` stores peri/pctrl/sctrl/usb31misc regmaps and tuning values.
- CR helpers `hi3670_phy_cr_read()` and `hi3670_phy_cr_write()` bit-bang USB31 PHY control registers through `USB_MISC_CFG54/58` with ACK polling.
- `hi3670_config_phy_clock()` selects ABB or pad reference path based on `SCTRL_SCDEEPSLEEPED`.
- `hi3670_config_tca()` programs TCA interrupt, sync mode, mux, Type-C disable, TCPC valid, and VBUS override.
- `hi3670_phy_init()` performs resets, clock selection, IDDQ/test-powerdown exit, PHY/controller deassertion, stable-power flags, TCA config, SSC, fake VBUS, and tuning.

## Control flow
Probe gets three syscon phandles, parent USB31 misc regmap, optional `hisilicon,eye-diagram-param` and `hisilicon,tx-vboost-lvl`, then creates one PHY. Init runs a long regmap sequence and aborts on first failure. Exit asserts PHY reset and disables whichever reference clock path was selected.

## State and persistence
Only cached tuning values and register state. There is no persisted state. Clock-source decision is recomputed from SCTRL on init/exit.

## Dependencies and integration points
Uses generic PHY, syscon/regmap, platform OF, parent syscon layout, and USB Type-C adapter registers. DT compatible is `hisilicon,hi3670-usb-phy`.

## Risks and test signals
Risks include CR-bus timeouts, parent-node syscon assumptions, no rollback after mid-init failures, and reliance on fake VBUS/Type-C overrides. Test both ABB and pad refclock paths, USB2/USB3 enumeration, CR read/write retries, default/custom tuning, and suspend or repeated exit/init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi6220-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi6220-usb.c

## Purpose
HI6220 USB PHY provider. It controls a peripheral syscon block to reset USB OTG/PICOPHY logic, select host/PHY behavior, fake VBUS, program an eye pattern, and enter SIDDQ on exit.

## Important APIs, types, and functions
- `struct hi6220_priv` stores syscon regmap and device.
- `hi6220_phy_init()` toggles reset enable/disable bits for USBOTG bus, PICOPHY POR, USBOTG, and 32K reset.
- `hi6220_phy_setup()` handles on/off register programming.
- `hi6220_phy_start()` and `hi6220_phy_exit()` wrap setup as PHY ops.

## Control flow
Probe gets `hisilicon,peripheral-syscon`, runs reset initialization once, creates a generic PHY, and registers simple xlate. PHY init enables ACA/res select, fakes VBUS, selects OTG PHY, clears SIDDQ/OGDISABLE, and writes `EYE_PATTERN_PARA`. Exit sets SIDDQ.

## State and persistence
Runtime state is the syscon register values; no persisted data. The driver stores only the regmap pointer.

## Dependencies and integration points
Generic PHY, platform driver, OF, `MFD_SYSCON`, and regmap. Integrated by DT compatible `hisilicon,hi6220-usb-phy`.

## Risks and test signals
Risks include ignoring return values in initial reset helper, sparse rollback, and fixed eye pattern. Test boot probe, init/exit error injection, USB OTG host/device behavior, and register programming against reference manual values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi6220-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hisi-inno-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hisi-inno-usb2.c

## Purpose
HiSilicon INNO USB2 PHY provider for one or two host ports. It enables ref clocks, controls POR and per-port UTMI resets, and writes vendor test-register sequences for PHY clock enable across two hardware register formats.

## Important APIs, types, and functions
- `struct hisi_inno_phy_priv` stores MMIO, ref clock, POR reset, type, and two port states.
- `struct hisi_inno_phy_port` stores per-port UTMI reset and back-pointer.
- `hisi_inno_phy_write_reg()` encodes test data/address/port/write/clock/reset fields differently for `PHY_TYPE_0` and `PHY_TYPE_1`.
- `hisi_inno_phy_init()` enables refclk, deasserts POR, writes setup register, then deasserts UTMI reset.
- Probe iterates child nodes and creates up to two PHYs.

## Control flow
Probe maps MMIO, gets refclk and POR reset, reads compatible data for type, walks child nodes to get per-port reset controls and create PHYs, sets bus width 8, and registers simple xlate. Init/exit are per port but POR/refclk are shared, so consumers must be balanced.

## State and persistence
No persistent state. Runtime state includes reset lines, clock enable count, port array, and MMIO test interface state.

## Dependencies and integration points
Depends on clk, reset controller, MMIO, platform/OF, and generic PHY. Child PHY nodes provide per-port resets.

## Risks and test signals
Risks include shared POR/refclk controlled by independent ports without reference counting, leaked reset controls from `of_reset_control_get_exclusive()` unless devm-managed by core cleanup, and accepting more children than supported with a warning. Test one-port and two-port DTs, simultaneous port users, missing child resets, and both type encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hisi-inno-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-histb-combphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-histb-combphy.c

## Purpose
HiSilicon STB COMBPHY provider that can be fixed-mode or selectable among SATA, PCIe, and USB3. It configures a parent syscon mode selector, deasserts POR, enables reference clock/EP clock, and writes vendor nano-register initialization.

## Important APIs, types, and functions
- `struct histb_combphy_priv` stores MMIO, syscon, reset, refclk, PHY, and mode metadata.
- `struct histb_combphy_mode` stores fixed/selectable mode and selector register fields.
- `histb_combphy_xlate()` validates phandle mode argument and fixed-mode compatibility.
- `histb_combphy_set_mode()` maps `PHY_TYPE_*` values to hardware selector values.
- `nano_register_write()` writes address/data through `COMBPHY_CFG_REG` strobe.

## Control flow
Probe maps MMIO, gets parent syscon, parses either `hisilicon,fixed-mode` or `hisilicon,mode-select-bits`, gets clk/reset, creates one PHY, and registers custom xlate. Xlate records selected mode. Init programs mode, clears bypass, enables clock/reset, enables EP clock, delays, and writes nano registers. Exit disables EP clock, asserts reset, and disables refclk.

## State and persistence
Selected mode is cached in `priv->mode.select`; hardware selector and PHY registers hold runtime state. No persistence.

## Dependencies and integration points
Uses generic PHY, syscon/regmap, reset, clk, `dt-bindings/phy/phy.h`, and platform OF. Consumers provide one mode argument in their PHY phandle.

## Risks and test signals
Risks include shared single PHY with mutable selected mode, fixed-mode/selector DT conflicts, and magic nano-register values. Test each mode, fixed-mode mismatch errors, missing selector bits, and clock/reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-histb-combphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hix5hd2-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hix5hd2-sata.c

## Purpose
HIX5HD2 SATA PHY provider. It optionally powers the PHY through a peripheral syscon bit, resets and configures the SATA PHY analog parameters, and steps speed-mode control so settings take effect.

## Important APIs, types, and functions
- `struct hix5hd2_priv` stores MMIO base and optional peripheral syscon.
- `hix5hd2_sata_phy_init()` reads optional `hisilicon,power-reg`, sets power bit, programs MPLL/ref/reset, amplitude, pre-emphasis, and speed mode registers.
- Probe maps one memory resource, optionally gets `hisilicon,peripheral-syscon`, creates one PHY, and registers simple xlate.

## Control flow
Only `.init` is implemented. Init optionally powers via syscon, asserts/deasserts PHY reset with delays, programs analog tuning, then writes GEN1, GEN3, and final GEN2 speed-mode sequences.

## State and persistence
No driver-managed persistent state. Hardware registers retain analog and power settings.

## Dependencies and integration points
Generic PHY, platform MMIO, optional syscon/regmap, OF property `hisilicon,power-reg`. Used by SATA controller consumers.

## Risks and test signals
Risks include using `devm_ioremap()` instead of resource-managed exclusive mapping, optional syscon failures silently treated as absent, and no power-off path. Test with/without `power-reg`, SATA link at GEN1/2/3, repeated init calls, and missing resource handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hix5hd2-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/ingenic/Kconfig

## Purpose
Kconfig entry for Ingenic SoC USB PHY support.

## Important APIs, types, and functions
Defines `PHY_INGENIC_USB`, a tristate symbol for `phy-ingenic-usb.o`.

## Control flow
The symbol is visible on MIPS or `COMPILE_TEST`, requires `USB_SUPPORT` and `HAS_IOMEM`, and selects `GENERIC_PHY`.

## State and persistence
Only build configuration state in `.config`; no runtime state.

## Dependencies and integration points
Feeds the Ingenic PHY Makefile and kernel config dependency graph.

## Risks and test signals
Risk is dependency drift if the driver gains new required subsystems. Test `COMPILE_TEST`, MIPS defconfigs, and module/built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/ingenic/Makefile

## Purpose
Kbuild mapping for the Ingenic USB PHY driver.

## Important APIs, types, and functions
Maps `CONFIG_PHY_INGENIC_USB` to `phy-ingenic-usb.o`.

## Control flow
Kbuild compiles the object when the config is enabled.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Depends on adjacent Kconfig symbol and source filename.

## Risks and test signals
Risk is object-symbol mismatch. Test with `CONFIG_PHY_INGENIC_USB=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/phy-ingenic-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ingenic/phy-ingenic-usb.c

## Purpose
Ingenic JZ/X-series USB PHY driver. It powers a USB PHY regulator, enables the PHY clock, applies SoC-specific USBPCR/USBPCR1/USBRDT initialization, releases POR, and supports host/device/OTG mode switching.

## Important APIs, types, and functions
- `struct ingenic_soc_info` supplies the SoC-specific initialization callback.
- `struct ingenic_usb_phy` stores PHY, MMIO base, clock, regulator, and match data.
- `ingenic_usb_phy_init()/exit()` handle clock and SoC register init/POR release; exit disables clock and regulator.
- `ingenic_usb_phy_power_on/off()` manage `vcc`.
- `ingenic_usb_phy_set_mode()` writes USB host/device/OTG bits.
- SoC callbacks cover `jz4770`, `jz4775`, `jz4780`, `x1000`, `x1830`, and `x2000`.

## Control flow
Probe matches compatible to SoC info, maps registers, gets clock and `vcc` regulator, creates one PHY, and registers simple xlate. Power-on enables regulator; init enables clock, runs callback, waits, clears POR, and waits again. Mode changes update USBPCR bits directly.

## State and persistence
Runtime state is MMIO register contents, clock/regulator enable counts, and match-data pointer. No persistent state.

## Dependencies and integration points
Uses generic PHY, clk, regulator, MMIO, bitfield helpers, and platform OF. Consumers are USB controllers needing mode control.

## Risks and test signals
Risks include `exit()` disabling the regulator even though regulator is also managed by `power_off()`, SoC-specific bit overlap (`USBPCR1_DMPD`/`USB_SEL`), and no rollback if init callback succeeds but later POR sequence fails. Test each compatible, power/init ordering, mode switching, regulator balance, and USB host/device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ingenic/phy-ingenic-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/Kconfig

## Purpose
Kconfig entries for Intel Keem Bay and Lightning Mountain PHY drivers: eMMC, USB, combo PHY, and LGM eMMC.

## Important APIs, types, and functions
Defines `PHY_INTEL_KEEMBAY_EMMC`, `PHY_INTEL_KEEMBAY_USB`, `PHY_INTEL_LGM_COMBO`, and `PHY_INTEL_LGM_EMMC`.

## Control flow
The symbols gate object compilation and select required framework symbols such as `GENERIC_PHY`, `REGMAP_MMIO`, `MFD_SYSCON`, and `REGMAP`.

## State and persistence
Only kernel configuration state.

## Dependencies and integration points
Architecture gates are `ARCH_KEEMBAY`, `X86`, and `COMPILE_TEST`, with `HAS_IOMEM`/`OF` as needed. The Makefile consumes these symbols.

## Risks and test signals
Risks are missing dependency selections for code paths using clk/reset/syscon or over-broad bool/tristate mismatch. Test modular and built-in build combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/Makefile

## Purpose
Kbuild object mapping for Intel PHY drivers.

## Important APIs, types, and functions
Maps four config symbols to four object files: Keem Bay eMMC/USB and LGM combo/eMMC.

## Control flow
Kbuild includes objects according to `.config`.

## State and persistence
Build state only; no runtime state.

## Dependencies and integration points
Tied to adjacent Intel Kconfig entries and source filenames.

## Risks and test signals
Risk is stale object mapping. Test all four symbols as enabled/module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-emmc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-emmc.c

## Purpose
Intel Keem Bay eMMC PHY provider. It maps eMMC PHY registers through regmap MMIO, delays clock acquisition until PHY init to avoid circular SDHCI dependency, and powers/calibrates the PHY DLL based on the active eMMC clock rate.

## Important APIs, types, and functions
- `struct keembay_emmc_phy` stores `syscfg` regmap and optional `emmcclk`.
- `keembay_emmc_phy_init()/exit()` get/put optional `emmcclk`.
- `keembay_emmc_phy_power()` powers down first, then for power-on selects frequency range, powers CALIO, polls `CAL_DONE`, enables DLL, and polls `DLL_RDY` unless clock rate is zero.
- `keembay_emmc_phy_power_on()` sets TX delay chain and output tap values before analog power-up.

## Control flow
Probe maps registers, creates regmap, creates one PHY, and registers simple xlate. Init obtains the eMMC clock after the SDHCI clock provider exists. Power-on configures delay fields then calls the common power sequence; power-off clears power/DLL bits.

## State and persistence
Runtime state is the optional clock pointer and PHY register bits. No persistent storage.

## Dependencies and integration points
Uses generic PHY, regmap MMIO, clk, platform MMIO, and OF. Integrates with SDHCI/eMMC via a PHY phandle and late clock lookup.

## Risks and test signals
Risks include optional clock rate zero skipping DLL lock verification, unsupported high rates only warning, and dependency on init being called before power. Test SDHCI probe ordering, 0/low/high clock rates, calibration timeout, DLL timeout, and power cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-emmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-usb.c

## Purpose
Intel Keem Bay USB PHY provider. It maps CPR and slave APB register windows, enables USB subsystem clocks/resets, exits IDDQ, initializes USB PHY SRAM/parallel CR interface, and releases DWC3 core reset.

## Important APIs, types, and functions
- `struct keembay_usb_phy` stores device and CPR/slave regmaps.
- `keembay_usb_clocks_on()` sets clock/reset masks, disables IDDQ, waits, and selects pad ref clock.
- `keembay_usb_phy_init()` sequences core reset, PHY reset release, CR parallel interface selection, SRAM init polling, SRAM load done, and core release.
- Probe maps named resources `cpr-apb-base` and `slv-apb-base`.

## Control flow
Probe creates regmaps and generic PHY, registers provider, then immediately enables subsystem clocks and turns on the DWC3 core for the controller driver. Later PHY init performs PHY-specific SRAM and reset sequencing.

## State and persistence
No persisted state. Runtime state is USB subsystem clocks/resets and regmap register contents.

## Dependencies and integration points
Generic PHY, regmap MMIO, platform named resources, and DWC3 integration through early core reset release.

## Risks and test signals
Risks include no explicit power-off/exit path, core turned on during probe before PHY init, and SRAM init timeout. Test with DWC3 probe, missing named resources, clock/reset register readback, repeated init calls, and SRAM timeout fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-keembay-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-combo.c -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-combo.c

## Purpose
Intel Lightning Mountain ComboPHY provider. It supports two internal PHY lanes, selectable PCIe/XPCS/SATA mode, optional dual-lane aggregation, clock/refclk gating, resets, and XPCS RX adaptation calibration.

## Important APIs, types, and functions
- `struct intel_combo_phy` stores shared clocks, resets, app/core MMIO, syscfg/hsiocfg regmaps, mode, aggregation, init count, and mutex.
- `struct intel_cbphy_iphy` stores per-lane PHY and app reset.
- `intel_cbphy_fwnode_parse()` reads clocks/resets, named resources, `intel,syscfg`, `intel,hsio`, `intel,phy-mode`, and optional `intel,aggregation`.
- `intel_cbphy_init()/exit()` serialize shared power and per-lane enable/disable with `init_cnt`.
- `intel_cbphy_calibrate()` triggers XPCS RX adaptation and polls ACK.

## Control flow
Probe parses resources and creates one or two PHYs depending on aggregation. Init powers the shared core on first user, sets mode, enables the requested lane (and lane 1 too in dual-lane mode), deasserts app reset, and enables PCIe pad refclk if needed. Exit decrements `init_cnt`, disables refclk, powers off lanes, and shuts down shared clocks/resets when count reaches zero.

## State and persistence
State is in `init_cnt`, selected mode/aggregation, MMIO/regmap registers, and reset/clock enable state. No persistence. Mutex protects shared init count and mode programming.

## Dependencies and integration points
Uses generic PHY, common clock, reset controls, regmap/syscon references via fwnode, OF xlate, and `dt-bindings/phy/phy.h`. Consumers pass lane ID in the PHY phandle.

## Risks and test signals
Risks include `init_cnt--` underflow if exit is unbalanced, error path disabling shared clock even when another lane is active, unsupported dual-lane SATA, and calibration only meaningful for XPCS. Test PCIe/XPCS/SATA modes, single/dual lane phandles, concurrent lane users, calibration success/timeout, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-combo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-emmc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-emmc.c

## Purpose
Intel Lightning Mountain eMMC PHY provider. It uses a syscon regmap to configure drive impedance, output tap delay, PHY power, frequency selection, calibration, and DLL lock based on eMMC clock rate.

## Important APIs, types, and functions
- `struct intel_emmc_phy` stores syscfg regmap and optional eMMC clock.
- `intel_emmc_phy_init()/exit()` get/put optional `emmcclk` at PHY init time to avoid SDHCI clock-provider cycles.
- `intel_emmc_phy_power()` powers down, computes frequency select from clock rate, powers up, polls `CALDONE`, enables DLL, and polls `DLLRDY`.
- `intel_emmc_phy_power_on()` sets 50-ohm drive and tap delay before power.

## Control flow
Probe gets `intel,syscon`, creates one PHY, and registers simple xlate. Init obtains clock. Power-on writes impedance/delay and analog power sequence. Power-off powers analog blocks down.

## State and persistence
Runtime state is regmap bits and cached clock pointer. No persistent state.

## Dependencies and integration points
Generic PHY, syscon/regmap, clk, OF platform. Used by eMMC/SDHCI consumers.

## Risks and test signals
Risks include high-rate only warning/clamping, dependence on init-before-power ordering, and lack of zero-rate special-case compared with Keem Bay. Test clock rates across FRQSEL ranges, calibration/DLL timeout, SDHCI probe ordering, and power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-emmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/lantiq/Kconfig

## Purpose
Kconfig entries for Lantiq/Intel XWAY USB2 RCU PHY and VRX200/ARX300 PCIe PHY.

## Important APIs, types, and functions
Defines `PHY_LANTIQ_VRX200_PCIE` and `PHY_LANTIQ_RCU_USB2`.

## Control flow
Symbols gate object compilation. PCIe requires OF, IOMEM, and selects generic PHY plus regmap MMIO. USB2 requires OF and selects generic PHY.

## State and persistence
Build configuration only.

## Dependencies and integration points
Consumed by the Lantiq Makefile; architecture gate is `SOC_TYPE_XWAY` or `COMPILE_TEST`.

## Risks and test signals
Risk is missing dependency if drivers evolve. Test `COMPILE_TEST` and XWAY target configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/lantiq/Makefile

## Purpose
Kbuild mapping for Lantiq PHY drivers.

## Important APIs, types, and functions
Maps `CONFIG_PHY_LANTIQ_RCU_USB2` to `phy-lantiq-rcu-usb2.o` and `CONFIG_PHY_LANTIQ_VRX200_PCIE` to `phy-lantiq-vrx200-pcie.o`.

## Control flow
Kbuild compiles objects according to config symbols.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Tied to adjacent Kconfig and source filenames.

## Risks and test signals
Risk is stale mapping. Test both symbols enabled as modules/built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-rcu-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-rcu-usb2.c

## Purpose
Lantiq XWAY RCU-based USB 1.1/2.0 PHY provider. It configures host mode, DMA endianness, optional analog tuning, and controls PHY/core resets and the PHY gate clock.

## Important APIs, types, and functions
- `struct ltq_rcu_usb2_bits` describes SoC-specific bit positions and analog-config presence.
- `struct ltq_rcu_usb2_priv` stores parent RCU regmap offsets, clocks, resets, device, and PHY.
- `ltq_rcu_usb2_of_parse()` gets match data, parent syscon, `reg` offsets, `phy` clock, `ctrl` reset, and optional `phy` reset.
- `ltq_rcu_usb2_phy_init()` writes analog cfg where available, host mode, and endianness.
- Power ops deassert/assert PHY reset and enable/disable clock.

## Control flow
Probe parses resources, deasserts shared USB core reset, asserts PHY reset, creates one PHY, and registers simple xlate. Init writes RCU bits. Power-on deasserts PHY reset, enables clock, and waits 100-200 us; power-off reverses.

## State and persistence
No persistent state. Runtime state is RCU register bits, reset lines, and clock enable.

## Dependencies and integration points
Uses generic PHY, clk, reset, syscon/regmap, OF address parsing, and SoC-specific compatible data. Consumed by USB controller nodes.

## Risks and test signals
Risks include ignoring regmap update errors in init, optional reset handling, and fixed big-endian host DMA assumption. Test all compatible bit layouts, analog-config variants, reset/clock failures, and USB host enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-rcu-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-vrx200-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-vrx200-pcie.c

## Purpose
PCIe PHY provider for Lantiq VRX200/ARX300 SoCs. It programs 16-bit PHY registers for 36 MHz reference mode, controls endian configuration, resets PCIe/PHY, enables PDI/PHY clocks, waits for PLL status, and applies modulation workarounds.

## Important APIs, types, and functions
- `struct ltq_vrx200_pcie_phy_priv` stores PHY/regmap/RCU regmap, clocks, resets, endian property data, and selected mode.
- `ltq_vrx200_pcie_phy_xlate()` accepts one mode argument but only implements `LANTIQ_PCIE_PHY_MODE_36MHZ`.
- `ltq_vrx200_pcie_phy_common_setup()` and `pcie_phy_36mhz_mode_setup()` write PLL/TX/RX tuning.
- `ltq_vrx200_pcie_phy_wait_for_pll()` polls PLL status.
- `ltq_vrx200_pcie_phy_apply_workarounds()` toggles load-enable slices and repeated TX modulation sequences.

## Control flow
Probe maps PHY MMIO as an 8-bit-register/16-bit-value regmap, gets RCU syscon and endian properties, clocks and resets, creates one PHY, and registers custom xlate. Init sets AHB endian, resets PHY and PCIe. Power-on enables PDI clock, writes setup, enables PHY clock, waits for PLL, and applies workarounds. Power-off disables clocks; exit asserts resets.

## State and persistence
Selected mode is cached but only 36 MHz is supported. Hardware registers store all runtime state. No persistent storage.

## Dependencies and integration points
Generic PHY, regmap MMIO, syscon/regmap, clk, reset, device properties, and Lantiq PHY dt-binding constants. Consumed by PCIe controller.

## Risks and test signals
Risks include unsupported DT modes returning errors, many setup writes without error checking, PLL timeout, and endian property misconfiguration. Test 36 MHz mode, unsupported mode rejection, big/little-endian DT, PLL timeout, and PCIe link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-vrx200-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/Kconfig

## Purpose
Kconfig menu entries for Marvell PHY drivers, including the Armada375 USB cluster and Armada38x COMPHY files in this work item plus other Marvell PHYs in the same directory.

## Important APIs, types, and functions
Relevant symbols here are `ARMADA375_USBCLUSTER_PHY` and `PHY_MVEBU_A38X_COMPHY`; the file also defines Berlin, A3700, CP110, SATA, PXA, and MMP3 PHY options.

## Control flow
Symbols gate object builds and select `GENERIC_PHY`. Some defaults are SoC-dependent, such as `ARMADA375_USBCLUSTER_PHY` defaulting y for `MACH_ARMADA_375`.

## State and persistence
Only build configuration state.

## Dependencies and integration points
Consumed by the Marvell Makefile and architecture/config dependency graph (`ARCH_MVEBU`, `OF`, `HAS_IOMEM`, `HAVE_ARM_SMCCC`, etc.).

## Risks and test signals
Risks are dependency mismatches and default-y behavior unexpectedly including built-in code. Test Marvell defconfigs, `COMPILE_TEST`, and selected module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/Makefile

## Purpose
Kbuild object mapping for Marvell PHY drivers.

## Important APIs, types, and functions
Relevant mappings are `CONFIG_ARMADA375_USBCLUSTER_PHY += phy-armada375-usb2.o` and `CONFIG_PHY_MVEBU_A38X_COMPHY += phy-armada38x-comphy.o`, alongside other Marvell PHY objects.

## Control flow
Kbuild includes each object according to config state.

## State and persistence
No runtime state; build state only.

## Dependencies and integration points
Relies on adjacent Marvell Kconfig symbols and source filenames.

## Risks and test signals
Risk is symbol/object drift. Test enabled builds for Armada375 and Armada38x symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada375-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada375-usb2.c

## Purpose
Armada 375 USB cluster PHY selector. It controls a shared cluster bit that routes the common USB2 PHY resources between USB2 and USB3 users and enforces a single-consumer mode.

## Important APIs, types, and functions
- `struct armada375_cluster_phy` stores the PHY, control register, selected USB3 flag, and already-provided PHY type.
- `armada375_usb_phy_xlate()` validates the phandle argument, rejects conflicting second consumers, and records USB2 vs USB3 mode.
- `armada375_usb_phy_init()` sets or clears `USB2_PHY_CONFIG_DISABLE` based on `use_usb3`.
- Probe maps one MMIO resource, creates one PHY, and registers custom xlate.

## Control flow
Consumers request the PHY with `PHY_TYPE_USB2` or `PHY_TYPE_USB3`. Xlate decides whether the request is allowed and records mode. Init then writes the cluster control bit accordingly.

## State and persistence
State is runtime-only in `phy_provided`, `use_usb3`, and one MMIO register. No persistence.

## Dependencies and integration points
Generic PHY, OF address/platform MMIO, built-in platform driver, and `dt-bindings/phy/phy.h`. Integrates with Armada USB2/USB3 controllers sharing a cluster.

## Risks and test signals
Risks include no locking around `phy_provided`, confusing USB2 vs USB3 optional-get error semantics, and only init-time register programming. Test conflicting consumers, USB2-only/USB3-only DTs, invalid phandle mode, and controller enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada375-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada38x-comphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada38x-comphy.c

## Purpose
Armada 38x COMPHY driver focused on Ethernet SerDes speed switching for lanes configured as GBE. It exposes child lanes as PHYs, validates port/lane muxing, sets SGMII/1000Base-X/2500Base-X speed fields, and waits for TX/RX PLL ready.

## Important APIs, types, and functions
- `struct a38x_comphy` stores shared base, optional `conf` resource, device, and lane array.
- `struct a38x_comphy_lane` stores lane MMIO base, lane number, selected port, and parent.
- `gbe_mux[][]` maps lane/GBE port to expected selector values.
- `a38x_comphy_xlate()` validates port arg, prevents lane reuse, checks hardware selector, and returns the lane PHY.
- `a38x_comphy_set_mode()` supports `PHY_MODE_ETHERNET` with SGMII/1000BASEX/2500BASEX and polls PLL ready.

## Control flow
Probe maps base and optional `conf`, iterates child nodes with `reg`, creates PHYs, and registers custom xlate. Xlate binds a lane to a port only if the current selector matches GBE mux table. `set_mode()` disables optional config, writes speed generation, polls PLL status, and re-enables config on success.

## State and persistence
Per-lane selected `port` is cached in memory; hardware selector/speed/conf registers carry runtime state. No persistent storage.

## Dependencies and integration points
Generic PHY, platform MMIO, OF child nodes, Ethernet PHY interface mode constants. Consumers are Ethernet MAC/PCS drivers using generic PHY set_mode.

## Risks and test signals
Risks include port assignment not being reset after failed xlate, limited support to GBE despite broader COMPHY hardware, optional `conf` behavior changing link enable timing, and polling timeout. Test valid/invalid mux tables, all supported Ethernet submodes, duplicate lane requests, and 2500Base-X link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada38x-comphy.c -->
