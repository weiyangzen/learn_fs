# Research: subset-b-005032

Grouped research for PHY framework and platform PHY drivers under `sources/distributed-fs/ceph-client/drivers/phy`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-common-props-test.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-common-props-test.c

This file is a KUnit suite for the PHY common polarity property helpers. It creates synthetic firmware/software nodes with `PROPERTY_ENTRY_U32_ARRAY()` and `PROPERTY_ENTRY_STRING_ARRAY()` and validates the exported API behavior from `phy-common-props.c`, especially `phy_get_manual_rx_polarity()`, `phy_get_manual_tx_polarity()`, and one `phy_get_rx_polarity()` path that permits `PHY_POL_AUTO`.

Control flow is a set of isolated test functions: create a software node, call the helper under test with mode names such as `sgmii`, `2500base-x`, or `usb-ss`, assert return code and decoded value, then remove the node. The suite covers missing properties defaulting to `PHY_POL_NORMAL`, single unnamed values, exact name lookup, fallback to `"default"`, mismatched array lengths, absent names with multiple values, and unsupported values returning `-EOPNOTSUPP`.

State is transient and test-local; the only persistent integration is registration through `kunit_test_suite()`. Dependencies are KUnit, firmware-node property APIs, `dt-bindings/phy/phy.h`, and the common polarity header. Risks are mostly coverage gaps: it does not exercise allocation failure in the helper, NULL mode names, invalid property read failures, or TX helper paths allowing custom defaults. Strong test signal exists for the public polarity contract and expected error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-common-props-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-common-props.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-common-props.c

This file implements reusable firmware-property parsing for differential PHY lane polarity. Its exported APIs are `phy_get_rx_polarity()`, `phy_get_tx_polarity()`, `phy_get_manual_rx_polarity()`, and `phy_get_manual_tx_polarity()`, all exported GPL symbols for PHY drivers that need `rx-polarity`/`tx-polarity` and matching `*-polarity-names` properties.

The core control flow is `fwnode_get_u32_prop_for_name()`: missing firmware node or missing value property returns the caller default, a single unnamed value applies globally, named arrays must match value array length, lookup first tries the requested mode name and then `"default"`, and multi-value arrays without a matching name fail with `-EINVAL`. Multi-value decoding allocates a temporary `u32` array with `kcalloc()`. `phy_get_polarity_for_mode()` then verifies the decoded enum against a caller-supplied supported bitmask.

State is not retained beyond the returned value. Dependencies are Linux fwnode/property APIs, `BIT()`-encoded `PHY_POL_*` constants, printk diagnostics, and slab allocation. Integration points are DT/ACPI-backed PHY drivers that want consistent polarity parsing. Risks include strict count matching rejecting malformed but historically tolerated DTs, log noise from invalid firmware data, and possible unsupported-value failures if bindings allow values not represented in a driver's supported mask. KUnit coverage in `phy-common-props-test.c` is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-common-props.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-core-mipi-dphy.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-core-mipi-dphy.c

This file provides common MIPI D-PHY timing calculation and validation helpers for generic PHY consumers/providers. The important exported APIs are `phy_mipi_dphy_get_default_config()`, `phy_mipi_dphy_get_default_config_for_hsclk()`, and `phy_mipi_dphy_config_validate()`.

Control flow starts in `phy_mipi_dphy_calc_config()`, which derives high-speed clock rate from `pixel_clock * bpp / lanes` unless an explicit HS clock is supplied. It computes unit interval in picoseconds and fills `struct phy_configure_opts_mipi_dphy` with spec-derived minimum timings. The validation helper recomputes UI from `cfg->hs_clk_rate` and checks every timing field against MIPI D-PHY v1.2 limits, returning `-EINVAL` on the first violation.

State is caller-owned through the configuration struct; no persistent driver state exists. Dependencies are `linux/phy/phy-mipi-dphy.h`, `do_div()`, time constants, and exported symbol linkage. Integration is with display/camera PHY drivers that call these helpers before `phy_configure()`. Risks include division by zero if callers pass zero lanes or a config with zero `hs_clk_rate` to validation, narrow support for defaults based only on UI and lane count, and spec drift if newer D-PHY versions adjust limits. Test signals are indirect through users; this file has no local KUnit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-core-mipi-dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-core.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-core.c

This is the generic PHY framework core. It registers the `phy` class, creates/destroys `struct phy` devices, manages OF/non-OF lookup, provider registration, devres wrappers, runtime PM helpers, regulator handling for optional `phy-supply`, debugfs directories, and exported consumer operations such as `phy_init()`, `phy_power_on()`, `phy_set_mode_ext()`, `phy_configure()`, and `phy_validate()`.

Global state includes `phy_provider_list`, non-DT `phys` lookup entries, `phy_ida`, and `phy_debugfs_root`, protected by `phy_provider_mutex` where needed. Per-PHY state includes a mutex, operation table, `init_count`, `power_count`, optional regulator, device object, debugfs dentry, and current mode attribute. Control flow for consumers obtains a PHY by OF phandle or lookup table, pins the provider module, takes a device reference, and optionally creates a stateless device link. Init/power calls take runtime PM references, serialize through the PHY mutex, and call provider callbacks only on first init/power transition.

Dependencies are device core, OF, modules, IDA, debugfs, PM runtime, regulators, and devres. Risks include underflow if consumers call `phy_exit()`/`phy_power_off()` more times than init/power-on, provider lookup deferral semantics, stale non-DT lookup entries if drivers forget removal, and error unwind around module/device references. Test signals are broad in-tree user coverage rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-google-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-google-usb.c

This platform driver exposes a Google USB2 PHY as a generic PHY provider and registers a Type-C orientation switch. Its state is split between `struct google_usb_phy`, holding shared regmap/MMIO/orientation/mutex/switch data, and one `google_usb_phy_instance` for clocks, resets, and the created `struct phy`.

Probe resolves a syscon regmap plus offset from `google,usb-cfg-csr`, maps `usbdp_top`, creates one USB2 PHY, gets two clocks (`usb2`, `usb2_apb`) and two resets, registers an OF provider with a custom `google_usb_phy_xlate()`, enables runtime PM, and registers a Type-C switch. `google_usb2_phy_init()` programs reference frequency and PLL feedback divider, sets VBUS-valid based on orientation, enables clocks, deasserts resets, and sets `PHY_ENABLE`. Exit reverses enable, asserts resets, and disables clocks. Orientation changes update cached orientation and, if runtime active, set or clear `SYS_VBUSVALID` under `phy_mutex`.

Dependencies are regmap/syscon, platform MMIO, clk/reset bulk APIs, runtime PM, generic PHY, and Type-C mux APIs. Risks include runtime PM only gating orientation writes while init/exit also touch registers, fixed PLL constants, xlate relying on one-cell indices, and no remove-time PHY shutdown beyond managed resources. Test signals are probe-time errors and hardware behavior; there is no local unit test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-google-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-lgm-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-lgm-usb.c

This Intel LGM USB PHY driver uses the legacy `struct usb_phy` API rather than generic PHY. It manages APB/controller resets, PHY resets, a VBUS regulator, TCPC mux register programming, and optional extcon-based Type-C polarity/connect state.

Probe maps one MMIO resource, gets `vbus`, obtains controller resets (`apb`, `ctrl`) and PHY resets (`phy31`, `phy`), asserts both reset groups, deasserts controller resets in-band, waits, initializes work, and registers via `usb_add_phy_dev()`. `phy_init()` deasserts PHY resets, polls `SRAM_INIT_DONE`, sets `SRAM_EXT_LD_DONE`, marks initialized, and either forces connected/no-extcon mode or schedules work. Work reads extcon polarity, detects `EXTCON_USB_HOST`, writes `TCPC_CONN` or `TCPC_DISCONN`, and toggles VBUS. Shutdown flushes work, disables VBUS, writes disconnect, and reasserts PHY resets.

Persistent state is `regulator_enabled`, `phy_initialized`, and `connected`, plus deferred work. Dependencies are reset, regulator, extcon through usb_phy notifiers, MMIO polling, and workqueues. Risks include asynchronous extcon changes racing with shutdown despite `flush_work()`, errors from reset operations often not checked in loops, and the old usb_phy integration path differing from generic PHY consumers. Test signals are hardware initialization and extcon events; no in-tree unit test is present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-lgm-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-lpc18xx-usb-otg.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-lpc18xx-usb-otg.c

This driver provides a generic PHY for the internal USB OTG PHY on NXP LPC18xx/43xx. It stores a created PHY, one clock, and a syscon regmap in `struct lpc18xx_usb_otg_phy`.

Probe obtains the parent syscon regmap, gets the unnamed PHY clock, creates a managed PHY with init/exit/power callbacks, stores private data, and registers `of_phy_simple_xlate`. `lpc18xx_usb_otg_phy_init()` sets the PHY clock to 480 MHz and prepares it. `power_on()` enables the clock and clears `LPC18XX_CREG_CREG0_USB0PHY` in `CREG0`, because the bit is active-disable. `power_off()` sets that bit and disables the clock. Exit unprepares the clock.

State persistence is limited to clock preparation/enable state and the syscon bit. Dependencies are clk, syscon/regmap, generic PHY, platform driver, and OF. Integration is a simple one-PHY provider for USB controller phandles. Risks include assuming the parent node is the syscon, fixed 480 MHz rate, and possible clock leak if power-off regmap update fails after enable was active. Test signals are driver probe and USB controller operation; no local unit test exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-lpc18xx-usb-otg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-nxp-ptn3222.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-nxp-ptn3222.c

This I2C driver models the NXP PTN3222 eUSB2 redriver as a generic PHY. Its state is `struct ptn3222`, containing the I2C client, created PHY, optional reset GPIO, and two bulk regulators.

Probe allocates state, requests optional `reset` GPIO initially high, gets constant regulator descriptors for `vdd3v3` and `vdd1v8` with load hints, creates a PHY bound to the device node, stores private data, and registers `of_phy_simple_xlate`. `ptn3222_init()` enables both supplies and deasserts reset by driving the GPIO low. `ptn3222_exit()` asserts reset high and disables regulators.

There is no register access despite the I2C transport; the chip is controlled through supplies and reset only. Dependencies are I2C core, GPIO consumer API, regulators, and generic PHY. Integration is with eUSB2 PHY/controller users that need a redriver brought up in sequence. Risks include no delay between regulator enable and reset release, no cleanup of regulators if reset GPIO operation were to fail, no runtime PM, and a probe error message that prints an uninitialized `ret` when `devm_phy_create()` fails. Test signals are limited to resource acquisition and board-level USB behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-nxp-ptn3222.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-pistachio-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-pistachio-usb.c

This platform driver provides the IMG Pistachio USB2 PHY as a generic PHY. It stores the device, CR_TOP syscon regmap, `usb_phy` clock, and DT-provided `img,refclk` selector.

Probe resolves the `img,cr-top` syscon, gets the `usb_phy` clock, reads the reference-clock selector, creates a PHY, and registers `of_phy_simple_xlate`. `pistachio_usb_phy_power_on()` enables the clock, programs strap refclk selection, validates XO crystal mode requires a 12 MHz clock, maps the clock rate to an FSEL index, writes FSEL, then polls up to 200 ms for both RX PHY and UTMI clock status while also detecting VBUS fault. Power-off disables the clock.

State is held in hardware strap/control/status registers and clock enable state. Dependencies are clk, syscon/regmap, DT binding constants from `phy-pistachio-usb.h`, jiffies timing, and generic PHY. Risks include unsupported clock rates returning `-EINVAL`, polling with manual jiffies loops instead of `read_poll_timeout`, VBUS fault causing bring-up failure, and reliance on board-provided `img,refclk`. Test signals are status bits during power-on; no unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-pistachio-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c

This Synopsys eUSB2 HS PHY driver supports Qualcomm SM8550 and Samsung Exynos2200 variants using `snps_eusb2_phy_drvdata` for clock names and SoC-specific register initialization. It also composes with an optional repeater PHY.

Probe maps MMIO, gets an optional reset, bulk clocks, identifies the `ref` clock, gets `vdd` and `vdda12` regulators, optionally obtains a repeater through `devm_of_phy_optional_get()`, creates a generic PHY, and registers a provider. Init enables regulators, initializes the repeater, enables clocks, asserts/deasserts PHY reset, then dispatches to variant `phy_init`. Exynos setup programs reset bits, repeater mode, reference-clock PLL fields for 19.2/20/24/26/48 MHz, TX tuning, IDDQ, and PHY enable. Qualcomm setup programs override controls, PLL fields for 19.2/38.4 MHz, TX defaults, suspend controls, SIDDQ, POR, and override release. `set_mode` forwards mode to the repeater.

State includes current mode, resources, and hardware register state. Dependencies are clk/reset/regulator, MMIO, generic PHY, and optional repeater integration. Risks include tight 5 us status polling in the repeater partner, unsupported ref clocks, error unwind correctness across repeater/clocks/regulators, and no runtime PM. Test signals are probe/init errors and downstream USB enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-snps-eusb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-xgene.c -->
## sources/distributed-fs/ceph-client/drivers/phy/phy-xgene.c

This AppliedMicro X-Gene multi-purpose PHY driver currently implements SATA-oriented SerDes initialization behind a generic PHY provider. It defines a large indirect register map for SDS, CMU, and lane RXTX registers, plus mode/clock enums and SATA tuning override storage in `struct xgene_phy_ctx`.

The low layer is `sds_wr()`/`sds_rd()` polling indirect command completion, wrapped by CMU and SerDes read/write/set/clear helpers. Probe maps SDS MMIO, optionally gets a clock, reads DT override arrays such as `apm,tx-eye-tuning`, `apm,tx-amplitude`, and `apm,tx-speed`, defaults lanes to Gen3, creates a PHY, and registers custom xlate. `xgene_phy_xlate()` stores the requested mode from phandle args. Init runs `xgene_phy_hw_initialize()` for SATA only, toggles the optional clock, then computes receiver calibration averages for both lanes.

Persistent state includes selected mode, optional clock, MMIO base, module parameter `preA3Chip`, and SATA tuning arrays. Dependencies are generic PHY, clk, platform MMIO, OF properties, delays, and module parameters. Risks are high: many magic register constants, indirect access timeout only logs errors, unsupported modes return `-ENODEV`, PLL calibration failure is logged but allowed to continue, and calibration loops can be expensive. Test signals are hardware PLL/calibration logs and SATA link stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/phy-xgene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Kconfig

This Kconfig file defines build-time feature symbols for Qualcomm and Atheros PHY drivers. It covers small legacy drivers (`PHY_ATH79_USB`, APQ8064/IPQ SATA, IPQ USB), display/eDP (`PHY_QCOM_EDP`), QMP subdrivers under `menuconfig PHY_QCOM_QMP`, USB HS/SS/HSIC/QUSB2/M31/eUSB2 drivers, and Ethernet SGMII.

Control flow is Kconfig dependency resolution: symbols constrain architecture, OF, IOMEM, COMMON_CLK, USB, EXTCON, NVMEM, PCI, TYPEC, and DRM availability, and select `GENERIC_PHY` or other helper subsystems where required. The nested QMP menu uses `default PHY_QCOM_QMP` so enabling the parent can expose specific QMP families. Some entries default on for ATH79 if platform EHCI/OHCI is enabled.

State is persisted in kernel `.config`, not runtime code. Integration points are the top-level PHY build, Makefile object selection, module availability, and DT binding compatibility. Risks include dependency mismatches causing unavailable drivers for compile-test, built-in/module conflicts noted around EXTCON, and legacy QMP USB compatibility choices. Test signals are `allyesconfig`, `allmodconfig`, architecture defconfigs, and object inclusion matching `Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Makefile -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Makefile

This Makefile maps Qualcomm/Atheros PHY Kconfig symbols to object files. It is the build integration layer for the directory and directly controls which C drivers are compiled into built-in objects or modules.

Each `obj-$(CONFIG_...) += ...` line ties a Kconfig symbol to one or more object files. Simple mappings include `PHY_ATH79_USB` to `phy-ath79-usb.o`, `PHY_QCOM_APQ8064_SATA` to `phy-qcom-apq8064-sata.o`, `PHY_QCOM_EDP` to `phy-qcom-edp.o`, `PHY_QCOM_EUSB2_REPEATER` to `phy-qcom-eusb2-repeater.o`, and IPQ-specific USB/SATA objects. QMP combo deliberately builds both `phy-qcom-qmp-combo.o` and `phy-qcom-qmp-usbc.o`.

State is build-system state only. Dependencies are the Linux kbuild convention and Kconfig symbols defined nearby. Integration risks are missing object entries for new Kconfig symbols, stale entries after file renames, or multi-object symbols omitting companion objects. Test signals are compile coverage from enabled configs and link failures if symbols or objects drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-ath79-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-ath79-usb.c

This Atheros AR71XX/9XXX USB PHY driver is a minimal generic PHY provider around reset controls. `struct ath79_usb_phy` stores the mandatory `phy` reset and optional inverted `usb-suspend-override` reset.

Probe allocates state, gets reset controls, creates a generic PHY with power callbacks, stores private data, and registers `of_phy_simple_xlate` for `qca,ar7100-usb-phy`. `power_on()` asserts `no_suspend_override` if present because the logic is inverted, then deasserts the PHY reset; if deassert fails it unwinds the override. `power_off()` asserts the PHY reset, then deasserts the override, unwinding the PHY reset if that fails.

State is entirely in reset lines. Dependencies are reset controller, generic PHY, OF matching, and platform driver infrastructure. Risks are reset polarity confusion, optional override availability differences across SoCs, and no explicit delays around reset transitions. Test signals are resource acquisition and USB controller link behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-ath79-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-apq8064-sata.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-apq8064-sata.c

This Qualcomm APQ8064 SATA PHY driver programs a UNIPHY/SATA SerDes register block through direct MMIO. `struct qcom_apq8064_sata_phy` keeps the MMIO base, always-enabled `cfg` clock, and device pointer.

Probe maps the register resource, creates a generic PHY, gets and enables the `cfg` clock, registers `of_phy_simple_xlate`, and disables the clock on remove. Init writes a fixed sequence: power down/up transitions, RX/TX impedance calibration setup, UNIPHY PLL reference, calibration, SDM, SSC, lock-detect registers, global PLL power-up, and polls PLL lock plus TX/RX calibration status with `readl_relaxed_poll_timeout()`. After calibration it writes functional-mode CDR, data, alignment, OOB, equalization, and drive controls. Exit powers down SATA PHY and PLL blocks.

State is MMIO register programming and the enabled config clock. Dependencies are clk, generic PHY, MMIO polling, and OF. Risks include fixed magic tuning values, 10 second timeout constant despite comment saying 1 second, no runtime PM, and limited recovery after calibration failure. Test signals are poll timeouts and SATA link bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-apq8064-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-edp.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-edp.c

This Qualcomm eDP/DP QMP PHY driver exposes a generic DP PHY plus two clock outputs for link and VCO-divided pixel clocks. `struct qcom_edp` holds MMIO regions for eDP, TX0, TX1, PLL, bulk clocks, two regulators, DP configuration, clock hardware, and version-specific config.

Probe selects `qcom_edp_phy_cfg` by compatible, maps four resources, obtains all clocks, gets `vdda-phy` and `vdda-pll`, sets regulator loads, registers clock providers, creates the PHY, and registers `of_phy_simple_xlate`. Init enables supplies/clocks, programs AUX configuration, bias, power-down states, and interrupt masks. Configure stores `phy_configure_opts_dp` and optionally applies voltage swing/pre-emphasis tables. Power-on dispatches version ops for v4/v6/v8 PLL and SSC programming based on link rate, configures lanes, sets VCO divisor and derived clock rates, runs reset-state-machine control, and polls `DP_PHY_STATUS`. Power-off writes power-down; exit disables clocks and regulators; set-mode accepts only `PHY_MODE_DP` and tracks eDP submode.

Dependencies are QMP register headers, clk provider API, regulators, MMIO polling, generic PHY DP opts, and OF match data. Risks include dense per-version magic tables, invalid link-rate/lane combinations, no unwind in several init early returns after clocks are enabled, and clock rate assumptions. Test signals are DP/eDP link training, clock consumers, and poll failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-edp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c

This driver controls Qualcomm PMIC eUSB2 repeaters through the parent device regmap. Per-compatible `eusb2_repeater_cfg` tables provide default tuning registers and regulator names for PM8550B, PMIV0104, SMB2360, and SMB2370.

Probe gets match data, obtains the parent regmap, reads the `reg` base offset, initializes bulk regulators, creates a PHY, and registers a provider. Init enables regulators, sets `EUSB2_RPTR_EN`, writes PMIC-specific tuning defaults, applies DT overrides such as `qcom,tune-usb2-preem`, `qcom,tune-usb2-disc-thres`, amplitude, FSDIF, and squelch detector breakpoint mapping, then polls `RPTR_OK`. `set_mode()` applies a host-mode workaround forcing 19.2 MHz clock bits and clears it for device mode. Exit disables regulators; remove calls exit defensively.

State includes base offset, regulators, mode-sensitive force registers, and tuning registers. Dependencies are regmap, regulators, generic PHY, OF properties, and PMIC parent devices. Risks include a very small poll timeout, repeated exit on remove after managed PHY users may already have exited, silent ignore of unsupported squelch DT values, and shared-regulator host/device mode persistence. Test signals are init timeout logs and USB role-switch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-eusb2-repeater.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq4019-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq4019-usb.c

This Qualcomm IPQ4019 USB PHY driver provides separate HS and SS generic PHY behavior selected by OF compatible data. State is `struct ipq4019_usb_phy`, containing MMIO base, POR reset, optional SRIF reset, device, and created PHY.

Probe maps the register resource, obtains `por_rst` and optional `srif_rst`, creates a PHY using the matched ops table, stores private data, and registers `of_phy_simple_xlate`. SS power-on first calls SS power-off, then deasserts POR. SS power-off asserts POR and waits. HS power-off asserts POR, waits, asserts SRIF, waits. HS power-on performs power-off, deasserts SRIF, waits, then deasserts POR.

State is almost entirely reset-line state; the mapped base is not used by current callbacks. Dependencies are reset controls, generic PHY, OF match data, platform MMIO, and delays. Risks include no error checking on reset assert/deassert callbacks, optional SRIF reset use in HS paths without NULL concerns delegated to reset API semantics, fixed 10 ms delays, and unused MMIO suggesting either future expansion or unnecessary resource requirement. Test signals are reset behavior and USB enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq4019-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-sata.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-sata.c

This Qualcomm IPQ806x SATA PHY driver programs one MMIO register block and keeps a config clock enabled while the provider is registered. `struct qcom_ipq806x_sata_phy` holds MMIO, `cfg_clk`, and device.

Probe maps the resource, creates a generic PHY, gets and enables `cfg`, registers `of_phy_simple_xlate`, and disables the clock on remove. Init enables spread-spectrum clocking, programs Gen1/2/3 TX pre-emphasis and amplitude fields, sets RX equalization, asserts PHY reset and reference SSP enable, waits for writes to complete and 20-70 us for settling, then clears reset. Exit asserts PHY reset again.

State is the MMIO parameter registers and enabled config clock. Dependencies are clk, generic PHY, platform MMIO, and OF. Integration is with IPQ806x SATA controllers using a single PHY phandle. Risks include hard-coded tuning values, no polling for lock or ready status, no runtime PM, and no cleanup path if provider registration fails beyond disabling the clock. Test signals are SATA link stability rather than explicit status checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-usb.c

This Qualcomm IPQ806x DWC3 USB PHY driver supports HS and SS variants selected by OF match data. It uses `struct usb_phy` for local state: MMIO base, ref/xo clocks, and SS tuning values (`rx_eq`, `tx_deamp_3_5db`, `mpll`). `struct phy_drvdata` embeds the operation table and reference clock rate.

Probe maps the resource, gets the `ref` clock and sets it to 60 MHz for HS or 125 MHz for SS, optionally gets `xo`, reads tuning properties with defaults, creates a generic PHY, and registers a provider. HS init enables clocks, writes QSCRATCH HS control bits for UTMI clock, clamps, VBUS valid, common-on, and optional core-clock use, waits, then bypasses VBUS/ID filters. SS init enables clocks, resets the SS PHY, selects pad/core reference, waits for stable ref clock, enables SS PHY and lane power, then uses CR protocol helpers to read/write internal SSPHY registers for suspend workaround, RX EQ, TX preemphasis/amplitude, MPLL, and QSCRATCH param control. Exit paths disable clocks and, for SS, request low-power state.

Dependencies are clk, MMIO, generic PHY, device properties, and latch polling. Risks include optional `xo_clk` handling after `devm_clk_get()` failure, CR-protocol timeout sensitivity, write-readback only logging mismatch, and many SoC tuning defaults. Test signals are latch timeouts, writeback errors, and USB HS/SS enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-ipq806x-usb.c -->
