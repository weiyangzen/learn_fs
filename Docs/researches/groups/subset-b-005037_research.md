# Research Report: subset-b-005037

This grouped report covers Qualcomm, Ralink/MediaTek, Realtek, and Renesas PHY driver files under the Ceph-client Linux source mirror. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usbc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usbc.c

Purpose: Implements the Qualcomm QMP USB-C PHY provider for USB3-only and combined USB3/DisplayPort PHY instances. It binds SoC-specific init tables and register layouts for MSM8998, QCM2290, QCS615, SDM660, and SM6115 class PHYs, and exposes separate generic PHY objects for USB and DP when the hardware supports both.

Important APIs/types/functions: Core types are `struct qmp_phy_cfg`, `struct qmp_usbc_offsets`, and `struct qmp_usbc`. Public integration is through `qmp_usbc_usb_phy_ops`, `qmp_usbc_dp_phy_ops`, `qmp_usbc_probe()`, `qmp_usbc_phy_xlate()`, and the OF match table. Major lifecycle helpers are `qmp_usbc_com_init()`, `qmp_usbc_usb_power_on()`, `qmp_usbc_dp_enable()`, `qmp_usbc_dp_power_on()`, `qmp_usbc_register_clocks()`, and `qmp_usbc_typec_switch_set()`.

Control flow: Probe selects a config from OF, registers regulators, optional Type-C orientation switch, optional TCSR syscon controls, parses either legacy child-node resources or a flat MMIO resource, enables runtime PM, registers pipe and DP clocks, creates USB and optional DP PHYs, and registers an OF PHY provider. USB init gates out concurrent DP use, enables common regulators/resets/clocks, programs USB SerDes/TX/RX/PCS tables, selects Type-C lane orientation, starts PCS/SerDes, and polls `PHYSTATUS`. DP init gates out concurrent USB use, powers common resources, initializes AUX, stores DP configure options, programs link-rate-specific SerDes and TX tables, configures swing/pre-emphasis, and polls C-ready, frequency-done, PLL-lock, TSYNC, and PHY-ready status.

State and persistence: Runtime state is in `struct qmp_usbc`: MMIO bases, clocks, reset/regulator arrays, TCSR registers, Type-C orientation, mode, DP options, AUX calibration index, and `usb_init_count`/`dp_init_count`. Register programming persists in PHY hardware until power-off, reset, runtime suspend, or Type-C repower. `phy_mutex` protects shared USB/DP resources and orientation changes.

Dependencies and integration points: Depends on generic PHY, clock provider, regulator, reset, runtime PM, syscon/regmap, Type-C switch, and QMP register definition headers. It integrates with USB/DWC3 and display consumers through OF PHY phandles and exposes pipe/link/pixel clocks to GCC/DISPCC consumers.

Risks: USB and DP are mutually exclusive in this implementation, so init-count imbalance or missing locking can strand the shared block. DP orientation handling has an explicit FIXME for lane remapping. Register tables are hardware-specific and failures usually surface as PHY-ready or PLL timeout. Runtime suspend disables clocks while autonomous wake detection and optional TCSR clamp state must remain coherent.

Test signals: Build coverage for `qcom-qmp-usbc-phy`, OF probe on all compatible strings, USB SuperSpeed enumeration in both Type-C orientations, DP link training at 1.62/2.7/5.4 Gbps, Type-C orientation switch while USB is active, runtime suspend/resume wake, clock provider lookup, and timeout/error paths for missing regulators, resets, or pipe clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp.h

Purpose: Aggregates Qualcomm QMP QSERDES and PCS register definition headers and defines common bit masks used by multiple QMP PHY drivers.

Important APIs/types/functions: This header exports no functions or structs. It includes versioned COM, TXRX, lane-shared, PLL, and PCS register headers, then defines shared bits such as `SW_RESET`, `SW_PWRDN`, `REFCLK_DRV_DSBL`, `SERDES_START`, `PCS_START`, `PHYSTATUS`, autonomous-mode interrupt bits, `IRQ_CLEAR`, and `CLAMP_EN`.

Control flow: There is no executable control flow. Including drivers use these symbols while building their power, reset, start, status, and low-power register sequences.

State and persistence: The file has no mutable state. The constants become persistent only when a consumer writes them to hardware registers.

Dependencies and integration points: It is a compile-time integration point between QMP driver source files and the register definition headers under `drivers/phy/qualcomm`. Consumers include USB, PCIe, UFS, and USB-C QMP drivers that need common state-machine bits independent of QSERDES generation.

Risks: This is a central include surface. Renaming or changing a bit definition can silently alter hardware sequencing across several PHY drivers. Because included headers cover many hardware generations, include-order conflicts or duplicated register names are a build-time risk.

Test signals: Compile all Qualcomm QMP PHY drivers, boot/probe a representative USB/PCIe/UFS QMP PHY, and verify reset, start, status polling, and autonomous-mode suspend paths still program expected bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qusb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qusb2.c

Purpose: Provides the Qualcomm QUSB2 high-speed USB2 PHY driver. It supports multiple SoCs through per-compatible init tables, register-layout arrays, PLL readiness masks, clock-scheme behavior, and tuning policy.

Important APIs/types/functions: Key types are `struct qusb2_phy_init_tbl`, `struct qusb2_phy_cfg`, `struct override_param(s)`, and `struct qusb2_phy`. The generic PHY contract is `qusb2_phy_gen_ops` with `qusb2_phy_init()`, `qusb2_phy_exit()`, and `qusb2_phy_set_mode()`. Runtime PM uses `qusb2_phy_runtime_suspend()` and `qusb2_phy_runtime_resume()`. Probe parses optional DT override properties and nvmem trim data.

Control flow: Probe maps MMIO, gets `cfg_ahb`, `ref`, optional `iface`, reset, supplies, optional TCSR syscon, optional nvmem cell, and board tuning overrides, then registers one PHY. Init enables regulators and clocks, resets the PHY, disables power, writes the SoC init table, applies DT overrides, applies fused HS TX trim, enables the PHY, resolves single-ended versus differential clock scheme through TCSR/default config, optionally selects `PLL_TEST`, and checks PLL/core-ready status. Exit powers down and unwinds clocks, reset, and regulators. Runtime suspend programs DP/DM wake triggers based on USB line mode, optionally holds PLL reset, toggles autoresume, and disables clocks.

State and persistence: `struct qusb2_phy` stores current mode, clock-scheme choice, initialization flag, override values, optional nvmem/TCSR handles, and resource handles. PHY tuning and PLL state persist in registers until exit, reset, or reinit.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clocks, reset, regulators, nvmem, TCSR regmap/syscon, runtime PM, and `dt-bindings/phy/phy-qcom-qusb2.h`. It is consumed by USB controllers through OF PHY phandles.

Risks: Register layouts differ by SoC, so a wrong `qusb2_phy_cfg` can write valid values to wrong offsets. Optional efuse and DT override values directly affect signal quality. Runtime suspend wake masks depend on accurate `set_mode()` calls from the USB controller. Missing cleanup on init failure can leave clocks or regulators enabled.

Test signals: Build and probe every compatible configuration, validate HS/FS/LS host and device modes, confirm PLL/core-ready status, verify nvmem trim and DT tuning writes with register dumps, test runtime suspend/resume wake for connected and disconnected states, and exercise init failure paths by removing clocks/resets/supplies in DT tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qusb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-sgmii-eth.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-sgmii-eth.c

Purpose: Implements the Qualcomm DWMAC SGMII PHY driver for SA8775P-style Ethernet SerDes, supporting SGMII/1000BASE-X and 2500BASE-X operating modes.

Important APIs/types/functions: `struct qcom_dwmac_sgmii_phy_data` stores the MMIO regmap, reference clock, and current `phy_interface_t`. `qcom_dwmac_sgmii_phy_init_1g()` and `_init_2p5g()` program full PLL/TX/RX/PCS sequences. `qcom_dwmac_sgmii_phy_calibrate()`, `_power_on()`, `_power_off()`, `_set_mode()`, and `_validate()` implement the generic PHY ops.

Control flow: Probe maps a resource, wraps it in a relaxed 32-bit regmap, creates a PHY, gets `sgmi_ref`, registers an OF PHY provider, and defaults the interface to SGMII. Power-on enables the reference clock and calibrates for the selected interface. Calibration selects either the 1.25 Gbps or 3.125 Gbps table, starts the PCS, and polls C-ready, PCS-ready, SGMII-ready, and PLL-lock bits. `set_mode()` validates Ethernet mode and recalibrates immediately if the PHY is already powered.

State and persistence: State is limited to selected interface mode and reference clock state. Hardware PLL, CDR, TX/RX equalization, and PCS configuration persist until power-off or recalibration.

Dependencies and integration points: Depends on generic PHY, Linux PHY interface mode constants, clocks, platform MMIO, and QMP SGMII/QSERDES register headers. It is intended to be called by a DWMAC Ethernet controller PHY consumer.

Risks: Long register write tables are mode-sensitive and not self-validating. `set_mode()` recalibrates on a powered PHY, so link-mode switches rely on consumers sequencing traffic safely. Poll timeouts are the main observable failure signal for wrong clocks, bad tables, or missing hardware readiness.

Test signals: Probe the `qcom,sa8775p-dwmac-sgmii-phy` compatible, bring links up in SGMII, 1000BASE-X, and 2500BASE-X, verify refclk enable/disable balance, run repeated `set_mode()` while powered, and check timeout diagnostics for each readiness poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-sgmii-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-snps-femto-v2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-snps-femto-v2.c

Purpose: Provides a Qualcomm Synopsys femto USB high-speed PHY v2 driver with clock/reset/regulator control, UTMI register programming, runtime suspend hooks, and optional DT-driven electrical tuning.

Important APIs/types/functions: Key structs are `override_param`, `override_param_map`, `phy_override_seq`, and `struct qcom_snps_hsphy`. PHY ops are `qcom_snps_hsphy_init()`, `qcom_snps_hsphy_exit()`, and `qcom_snps_hsphy_set_mode()`. Tuning helpers include `qcom_snps_hsphy_read_override_param_seq()` and `qcom_snps_hsphy_override_param_update_val()`.

Control flow: Probe maps MMIO, initializes optional `cfg_ahb` and required `ref` clocks, gets reset and supplies, enables but forbids runtime PM, creates the PHY, stores driver data, reads optional per-compatible tuning properties, and registers the provider. Init enables supplies and clocks, asserts/deasserts reset, enables UTMI common-control override, pulses POR, programs FSEL/refclk/VBUS override and any collected tuning sequence, bypasses the regulator, takes the PHY out of suspend/SIDDQ/POR, and clears overrides. Runtime suspend toggles auto-resume for host mode.

State and persistence: Driver state tracks `phy_initialized`, current mode, and a nine-entry tuning sequence. Hardware state includes override registers, suspend controls, VBUS-valid forcing, SIDDQ, POR, and regulator bypass until exit/reset.

Dependencies and integration points: Uses generic PHY, clocks, reset, regulators, runtime PM, OF match data, and DT properties such as `qcom,hs-disconnect-bp` or amplitude/impedance tuning keys. It integrates with USB host/device controllers through the generic PHY framework.

Risks: Tuning lookup falls back to the last table entry when a DT value is not matched, so bad DT values can still program hardware. Runtime PM is forbidden by default, so tests must explicitly allow it. Init sequencing is timing-sensitive and has no final PLL-ready poll.

Test signals: Probe all compatibles, check regulator/clock/reset balance, inspect override register writes for SC7280 tuning properties, run host/device HS enumeration, exercise runtime suspend in host mode, and validate behavior when optional `cfg_ahb` or tuning properties are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-snps-femto-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.c

Purpose: Implements Qualcomm UNIPHY PCIe 28LP PHY support for IPQ5018 and IPQ5332 families, including per-lane initialization and fixed pipe clock provider registration.

Important APIs/types/functions: `struct qcom_uniphy_pcie_data` describes lane offset, PHY generation, init sequence, and pipe clock rate. `struct qcom_uniphy_pcie` holds resources and lane count. Generic PHY ops are `qcom_uniphy_pcie_power_on()` and `_power_off()`, with `qcom_uniphy_pcie_init()` applying per-lane register tables.

Control flow: Probe reads match data, requires `num-lanes`, maps MMIO, gets all clocks and reset arrays, creates one PHY, registers a fixed-rate pipe clock named from the PHY id, and registers an OF provider. Power-on asserts/deasserts resets with required delays, enables all clocks, waits again, and writes the configured init sequence to each lane base separated by `lane_offset`. Power-off disables clocks and asserts resets.

State and persistence: Runtime state is resource handles, lane count, SoC data, and MMIO base. Hardware CDR/SSCG/PCS or Gen3 PHY configuration persists while powered.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clock bulk APIs, reset arrays, clock-provider APIs, OF match data, and `num-lanes` DT. PCIe host controller drivers consume the PHY and pipe clock.

Risks: `num-lanes` is trusted and not bounded against the mapped resource size. The code registers one pipe clock provider, so multi-PHY DT clock topology must match expectations. A stale macro `phy_to_dw_phy` references unrelated types and is unused but confusing. Init tables are minimal and SoC-specific.

Test signals: Probe IPQ5018 and IPQ5332 compatibles, verify pipe clock rate is 125 MHz or 250 MHz as configured, power-cycle PCIe links, test one-lane and multi-lane DTs, confirm reset/clock ordering, and inspect lane-offset register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs-28nm.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs-28nm.c

Purpose: Provides the Qualcomm 28 nm Synopsys/femto high-speed USB PHY driver for `qcom,usb-hs-28nm-femtophy`, handling power, retention, POR reset, high-voltage DP/DM wake interrupts, and optional init sequences.

Important APIs/types/functions: Main types are `struct hsphy_init_seq`, `struct hsphy_data`, and `struct hsphy_priv`. PHY ops are `qcom_snps_hsphy_init()`, `_exit()`, `_power_on()`, `_power_off()`, and `_set_mode()`. Helpers manage reset, POR reset, retention, HV interrupt masks, and init-sequence writes.

Control flow: Probe maps MMIO, gets `ref`, `ahb`, and `sleep` clocks, gets `phy` and `por` resets, gets `vdd`, `vdda1p8`, and `vdda3p3` supplies, creates/registers a PHY, and sets 1.8 V/3.3 V regulator loads. Init enables clocks, pulses the PHY reset, writes match-data init sequence entries, and performs POR reset with SIDDQ cleared. Power-on enables regulators, disables wake interrupts, and exits retention. Power-off enters retention, enables DP/DM wake interrupts based on current mode, and disables regulators.

State and persistence: State includes current `phy_mode`, resource handles, and optional init data. Retention and interrupt-mask state persists in PHY registers across low-power periods; regulator load votes persist until driver removal or error cleanup.

Dependencies and integration points: Uses generic PHY, platform MMIO, bulk clocks, resets, regulators, OF match data, and USB controller `set_mode()` calls.

Risks: Wake interrupt polarity depends on the last mode reported by the consumer. Probe sets regulator loads but remove-time load cleanup is devm-only for regulators, not explicit for successful probe. Register programming is byte-wide and timing-sensitive around reset/POR.

Test signals: Probe with the femtophy compatible, verify regulator load votes and clock/reset sequencing, enumerate HS/FS/LS devices, suspend with connected and disconnected states, confirm DP/DM wake masks, and test init-sequence register delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs-28nm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs.c

Purpose: Implements a Qualcomm ULPI high-speed USB PHY driver with regulator/clock sequencing, optional vendor init sequence, optional POR reset, and VBUS control through extcon or ULPI interrupts.

Important APIs/types/functions: `struct qcom_usb_hs_phy` holds the ULPI device, generic PHY, clocks, regulators, reset, init sequence, extcon device, and notifier. PHY ops are `qcom_usb_hs_phy_power_on()`, `_power_off()`, and `_set_mode()`. `qcom_usb_hs_phy_vbus_notifier()` mirrors extcon VBUS state into ULPI MISC_A.

Control flow: Probe parses `qcom,init-seq` as address/value pairs, gets `ref` and `sleep` clocks, `v1p8` and `v3p3` regulators, optional `por` reset, optional extcon, creates a PHY, and registers the provider. Power-on enables clocks, sets regulator loads/voltages, enables regulators, writes vendor ULPI init entries, pulses reset, initializes VBUS state, and registers the extcon notifier. `set_mode()` either enables ULPI ID/session-valid interrupts or uses VBUSVLDEXTSEL depending on extcon availability.

State and persistence: Runtime state is mostly resource handles and notifier registration. ULPI vendor init, OTG comparator disable, VBUS valid selection/value, and interrupt masks persist in the PHY until power-off or reset.

Dependencies and integration points: Depends on the ULPI bus, generic PHY, clocks, regulators, reset, extcon, notifier API, and OF properties. USB controller mode changes drive `set_mode()`.

Risks: The init sequence is DT-supplied raw ULPI writes with little validation. Extcon notifier registration happens at power-on and must be balanced at power-off. Regulator load/voltage settings influence signal stability and board power.

Test signals: Probe the ULPI compatible, verify init-seq writes, host/device/OTG mode transitions with and without extcon, VBUS notifier behavior, power-cycle under traffic, and regulator/clock cleanup on injected ULPI write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hsic.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hsic.c

Purpose: Provides a Qualcomm ULPI HSIC PHY driver that enables HSIC calibration, selects pinctrl state, and controls the HSIC clocks.

Important APIs/types/functions: `struct qcom_usb_hsic_phy` stores ULPI, generic PHY, pinctrl, and `phy`, `cal`, and `cal_sleep` clocks. PHY ops are `qcom_usb_hsic_phy_power_on()` and `_power_off()`.

Control flow: Probe gets pinctrl and all clocks, creates a PHY, attaches driver data, and registers an OF provider. Power-on enables clocks in order, writes the periodic IO calibration interval to `ULPI_HSIC_IO_CAL`, enables periodic calibration in `ULPI_HSIC_CFG`, selects the default pinctrl state, sets HSIC mode, and disables ULPI auto-resume. Power-off disables the three clocks.

State and persistence: The driver holds only resource handles. HSIC calibration interval, HSIC enable, pinmux state, and autoresume clearing persist in hardware/pinctrl until power-off or reconfiguration.

Dependencies and integration points: Depends on ULPI, generic PHY, pinctrl, and clocks. It is consumed by USB HSIC host controller wiring through OF PHY phandles.

Risks: Power-on ordering must keep clocks enabled before ULPI writes and pinctrl selection. There is no explicit pinctrl sleep-state restore on power-off. Any ULPI write failure unwinds clocks but leaves earlier register writes until next reset.

Test signals: Probe `qcom,usb-hsic-phy`, verify pinctrl default state selection, clock enable/disable balance, HSIC device enumeration, periodic calibration register values, and failure unwinding for missing clocks or pinctrl state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hsic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-ss.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-ss.c

Purpose: Implements an older Qualcomm SuperSpeed USB PHY driver for `qcom,usb-ss-28nm-phy`, managing regulators, clocks, reset, and basic lane/reference power bits.

Important APIs/types/functions: `struct ssphy_priv` stores MMIO, device, optional reset controls, two regulators, three clocks, and current mode. PHY ops are `qcom_ssphy_power_on()` and `_power_off()`. Resource helpers initialize clock, regulator, and reset arrays.

Control flow: Probe maps MMIO, gets `ref`, `ahb`, and `pipe` clocks, optional `com` reset and required `phy` reset when `com` exists, gets `vdd` and `vdda1p8` supplies, creates the PHY, and registers a provider. Power-on enables supplies and clocks, performs either register-based reset or reset-controller toggles, selects PCS clock, powers lane0, enables reference PHY, and clears test power-down. Power-off reverses lane/reference bits, asserts test power-down, and disables clocks and supplies.

State and persistence: State is resource handles plus the hardware control bits in `PHY_CTRL0/1/2/4`. No runtime PM or init-count state is kept.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clock bulk APIs, reset controllers, regulators, and OF simple PHY translation. USB3 controllers consume this PHY.

Risks: Reset behavior changes depending on whether a reset controller exists, so DT binding differences affect the hardware sequence. There is no PHY-ready poll after power-on. The `mode` field is initialized but unused, limiting suspend/wake specialization.

Test signals: Probe with and without external reset controls, verify regulator and clock balance, USB3 enumeration, repeated power cycles, register dumps for lane/ref/test bits, and behavior when pipe clock or regulators defer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/ralink/Kconfig

Purpose: Declares build-time configuration entries for Ralink/MediaTek MT7621 PCIe PHY and Ralink USB PHY drivers.

Important APIs/types/functions: Defines `PHY_MT7621_PCI` and `PHY_RALINK_USB`. Both select `GENERIC_PHY`; the PCI option also selects `REGMAP_MMIO`, and the USB option selects `MFD_SYSCON` and depends on `HAS_IOMEM`.

Control flow: No runtime control flow. Kconfig dependency resolution decides whether the corresponding objects are built as modules, built-in, or omitted.

State and persistence: No runtime state. The selected config values persist in the kernel `.config` and drive Makefile object inclusion.

Dependencies and integration points: Integrates with the top-level PHY Kconfig hierarchy and the ralink Makefile. `PHY_MT7621_PCI` is available for `RALINK && OF` or `COMPILE_TEST`; `PHY_RALINK_USB` is available for `RALINK` or compile testing.

Risks: Missing dependencies can produce compile failures under `COMPILE_TEST`; overly strict dependencies can hide drivers for valid platforms. The MT7621 help text ends with a comma, which is cosmetic but unpolished.

Test signals: Run `make olddefconfig`/`menuconfig`, build each option as `y` and `m` where allowed, and compile-test non-Ralink architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/ralink/Makefile

Purpose: Maps Ralink PHY Kconfig symbols to driver objects.

Important APIs/types/functions: Adds `phy-mt7621-pci.o` for `CONFIG_PHY_MT7621_PCI` and `phy-ralink-usb.o` for `CONFIG_PHY_RALINK_USB`.

Control flow: No runtime logic. Kbuild includes object files according to resolved config values.

State and persistence: No state beyond build artifacts generated by Kbuild.

Dependencies and integration points: Integrates with `drivers/phy/ralink/Kconfig` and the parent PHY Makefile.

Risks: Symbol/object mismatches break builds or silently omit drivers. Built-in versus module behavior follows Kconfig and driver registration macros.

Test signals: Build with each config as module and built-in, confirm the expected `.o` and `.ko` files are produced, and check module aliases for platform autoload where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-mt7621-pci.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-mt7621-pci.c

Purpose: Implements the MediaTek MT7621 PCIe PHY driver, including SSC/PLL setup for 20/25/40 MHz crystals, optional E2 revision pipe-reset bypass, and dual-port handling.

Important APIs/types/functions: `struct mt7621_pci_phy` holds regmap, PHY, system clock, MMIO base, dual-port state, and bypass quirk. Key helpers are `mt7621_phy_rmw()`, `mt7621_bypass_pipe_rst()`, `mt7621_set_phy_for_ssc()`, `mt7621_pci_phy_init()`, and power on/off ops. `mt7621_pcie_phy_of_xlate()` records whether the consumer selected a dual-port mode.

Control flow: Probe detects the MT7621 E2 quirk through `soc_device_match()`, maps MMIO, initializes a 32-bit regmap, creates a PHY, gets the system clock, and registers a custom OF xlate provider. Init optionally bypasses pipe reset, reads the XTAL clock rate, forces XTAL/PHY control fields, disables ports, programs PLL/DDS/SSC fields according to clock rate, and sets PLL current/divider controls. Power-on enables PHY and disables force mode for one or two ports; power-off disables PHY and re-enables force mode.

State and persistence: Driver state includes whether the selected consumer asked for dual-port operation and whether the E2 pipe-reset workaround is needed. PLL and force-mode register writes persist until reinitialized or reset by firmware/hardware.

Dependencies and integration points: Depends on generic PHY, regmap MMIO, system clock, platform OF, SoC revision matching, and `dt-bindings/phy/phy.h`. It is registered with `builtin_platform_driver()`, so it is intended for early built-in availability.

Risks: `has_dual_port` is set during OF xlate, so different consumers can alter shared state. Unsupported clock rates fall through to the 20 MHz setup. `mt7621_phy_rmw()` intentionally avoids `regmap_write_bits()` semantics; replacing it would risk PLL misprogramming.

Test signals: Boot MT7621 with 20/25/40 MHz crystals, probe E2 and non-E2 revisions, use one-port and dual-port PHY phandles, verify PCIe link training, inspect PLL register fields, and build as built-in under Ralink and compile-test configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-mt7621-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-ralink-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-ralink-usb.c

Purpose: Implements the Ralink/MediaTek USB2 PHY driver for RT3352, MT7620, MT7628, and MT7688 style SoCs, controlling syscon clock/reset bits and optional MT7628 PHY register initialization.

Important APIs/types/functions: `struct ralink_usb_phy` stores host/device resets, clock-enable mask, PHY, optional MMIO base, and sysctl regmap. `ralink_usb_phy_power_on()` and `_power_off()` implement the generic PHY ops, while `ralink_usb_phy_init()` writes the MT7628-specific analog/digital sequence.

Control flow: Probe reads the match-data clock mask, looks up `ralink,sysctl`, maps a local PHY resource only for `mediatek,mt7628-usbphy`, gets `host` and `device` resets, creates the PHY, and registers a simple provider. Power-on enables the selected UPHY clocks through syscon, forces USB0 host mode, deasserts resets, waits 10 ms, optionally programs MT7628 registers, and logs wakeup/UTMI width status. Power-off clears clock bits and asserts both resets.

State and persistence: The driver stores resource handles and the SoC-specific clock mask. Syscon clock, host-mode, reset, and MT7628 PHY register state persists until power-off or SoC reset.

Dependencies and integration points: Depends on generic PHY, reset controller, syscon/regmap, platform MMIO, OF match data, and Ralink/MediaTek USB controller consumers.

Risks: Host mode is forced unconditionally, so device/OTG use would need additional handling. Register programming for MT7628 is a fixed vendor sequence with no readiness checks. Power-on logs info every time, which may be noisy across repeated power cycles.

Test signals: Probe all compatibles, verify syscon clock masks, reset sequencing, USB host enumeration, MT7628 register initialization, power cycle behavior, and wakeup/UTMI status logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-ralink-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/realtek/Kconfig

Purpose: Declares Realtek RTD USB2 and USB3 PHY driver configuration entries under an `ARCH_REALTEK || COMPILE_TEST` guard.

Important APIs/types/functions: Defines `PHY_RTK_RTD_USB2PHY` and `PHY_RTK_RTD_USB3PHY`. Both depend on `USB_SUPPORT` and select `GENERIC_PHY`, `USB_PHY`, and `USB_COMMON`.

Control flow: No runtime flow. Kconfig controls whether Realtek USB PHY objects are compiled.

State and persistence: No runtime state. Values persist in kernel configuration and affect Kbuild output.

Dependencies and integration points: Integrates with the Realtek PHY Makefile and the parent PHY Kconfig. The selected USB symbols ensure debug/USB helper APIs are available to the driver sources.

Risks: The outer architecture guard hides options outside Realtek unless compile testing. Missing dependencies for debugfs/nvmem/syscon are handled by source-level includes and broader kernel config, so compile-test coverage matters.

Test signals: Build both options as modules and built-in under `ARCH_REALTEK`, compile-test them on another architecture, and confirm Kconfig selects expected generic PHY and USB helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/realtek/Makefile

Purpose: Connects Realtek USB PHY Kconfig options to their object files.

Important APIs/types/functions: Builds `phy-rtk-usb2.o` for `CONFIG_PHY_RTK_RTD_USB2PHY` and `phy-rtk-usb3.o` for `CONFIG_PHY_RTK_RTD_USB3PHY`.

Control flow: No runtime logic. Kbuild object inclusion follows config selection.

State and persistence: No persistent state except generated build artifacts.

Dependencies and integration points: Integrates with `drivers/phy/realtek/Kconfig` and the parent PHY build.

Risks: Object/config mismatch would omit the driver or break the build. Both drivers use similar names and shared concepts, so incorrect object mapping would be easy to miss in review.

Test signals: Build each config as `m` and `y`, inspect generated modules, and verify platform aliases come from each driver's OF match table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb2.c

Purpose: Implements Realtek RTD USB2 PHY initialization and port connect/disconnect tuning for multiple RTD SoCs. It programs paged vendor PHY registers through the DWC2/DWC3 wrapper access register, applies efuse and DT compensation, and exposes debugfs inspection.

Important APIs/types/functions: Key types are `struct phy_cfg`, `struct phy_parameter`, `struct phy_reg`, and `struct rtk_phy`. PHY ops are `rtk_phy_init()`, `rtk_phy_exit()`, `rtk_phy_connect()`, and `rtk_phy_disconnect()`. Important helpers include `rtk_phy_read()`, `rtk_phy_write()`, `rtk_phy_set_page()`, `update_dc_driving_level()`, `update_dc_disconnect_level()`, `do_rtk_phy_toggle()`, `get_phy_data_by_efuse()`, and `parse_phy_data()`.

Control flow: Probe copies the compatible's `phy_cfg`, allocates per-port parameters, maps wrapper/VStatus and PHY access registers through OF, reads optional DT properties for sync-clock inversion, driving level, driving compensation, and disconnect compensation, reads optional `usb-dc-cal` and `usb-dc-dis` nvmem cells, updates cached page data, creates one PHY, registers an OF provider, and creates debugfs files. Init writes configured page0/page1/page2 data for each port unless default parameters are requested, then runs disconnect-side toggle logic. Connect/disconnect callbacks retune sensitivity, driving, and disconnect thresholds per port.

State and persistence: The mutable copied `phy_cfg` caches register data and may be updated by efuse/DT-derived values. Per-port state stores efuse and compensation values plus MMIO pointers. Hardware page registers and sensitivity toggles persist until the next toggle/init or controller reset.

Dependencies and integration points: Depends on generic PHY connect/disconnect callbacks, USB debug root/debugfs, nvmem cells, OF MMIO mapping, sys_soc workaround matching, and Realtek DWC USB wrappers.

Risks: `of_iomap()` mappings are not devm-managed in this file. Port bounds use `index > num_phy`, which allows `index == num_phy` and can address past the allocated array. Shared cached `phy_cfg` data is mutated while iterating ports, so multi-port behavior needs care. Hardware access errors are often logged but do not always abort the full init.

Test signals: Probe every compatible, read debugfs `parameter`, verify nvmem compensation on v1/v2 efuse formats, test one-port and two-port configs, run connect/disconnect callbacks, check out-of-range port handling, inspect page register writes, and enumerate USB2 devices across HS/FS/LS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb3.c

Purpose: Implements Realtek RTD USB3 PHY initialization, calibration toggling, efuse/DT amplitude tuning, optional RX front-end offset correction, and debugfs reporting.

Important APIs/types/functions: Main types are `struct phy_cfg`, `struct phy_parameter`, `struct phy_reg`, and `struct rtk_phy`. PHY ops are `rtk_phy_init()`, `rtk_phy_exit()`, `rtk_phy_connect()`, and `rtk_phy_disconnect()`. Major helpers are `rtk_phy_read()`, `rtk_phy_write()`, `do_rtk_usb3_phy_toggle()`, `do_rtk_phy_init()`, `get_phy_data_by_efuse()`, `update_amplitude_control_value()`, and `parse_phy_data()`.

Control flow: Probe selects and copies the SoC config, fixes `num_phy` to one, maps the MDIO control register, reads DT amplitude controls, reads optional `usb_u3_tx_lfps_swing_trim` nvmem data, updates cached parameter entries, creates the PHY/provider, and registers debugfs. Init writes the parameter table unless default parameters are requested, optionally performs a one-time force-calibration toggle and debug-status check, and may loop through RX offset range adjustments followed by another toggle. Connect/disconnect callbacks rerun the calibration toggle when enabled.

State and persistence: The copied `phy_cfg` is mutable: one-time toggles can clear `do_toggle`, and amplitude/efuse updates alter cached register data. Per-PHY state stores MDIO base and tuning values. MDIO register writes persist in the USB3 PHY until reset or reinit.

Dependencies and integration points: Depends on generic PHY, OF MMIO, nvmem, USB debugfs root, and Realtek DWC USB wrappers. Compatible data covers RTD1295, RTD1319, RTD1319D, RTD1619, and RTD1619B.

Risks: `rtk_phy_read()`/`write()` ignore busy-wait return values after issuing the command, so MDIO timeout failures can be masked. `of_iomap()` is not devm-managed. The port bounds check allows `port == num_phy`. RX offset correction can recurse through `goto do_toggle` and should be verified against hardware convergence.

Test signals: Probe each compatible, verify debugfs output, check efuse and DT amplitude updates at registers 0x20/0x21, run SuperSpeed enumeration and disconnect/reconnect cycles, validate one-time toggle status bit behavior, and force RX offset edge values on RTD1319D.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/Kconfig

Purpose: Declares Renesas PHY driver configuration options for Ethernet SERDES, R-Car Gen2 USB, R-Car Gen3 PCIe/USB2/USB3, and RZ/G3E USB3.

Important APIs/types/functions: Defines `PHY_R8A779F0_ETHERNET_SERDES`, `PHY_RCAR_GEN2`, `PHY_RCAR_GEN3_PCIE`, `PHY_RCAR_GEN3_USB2`, `PHY_RCAR_GEN3_USB3`, and `PHY_RZ_G3E_USB3`. All select `GENERIC_PHY`; USB2 also depends on `EXTCON || !EXTCON`, `USB_SUPPORT`, and `REGULATOR`, and selects `MULTIPLEXER` and `USB_COMMON`.

Control flow: No runtime flow. Kconfig controls object inclusion and dependency visibility.

State and persistence: No runtime state. Kernel configuration choices persist in `.config`.

Dependencies and integration points: Integrates with the Renesas PHY Makefile and architecture guard `ARCH_RENESAS || COMPILE_TEST` for most newer options. `PHY_RCAR_GEN2` and `PHY_RCAR_GEN3_PCIE` depend directly on `ARCH_RENESAS`.

Risks: Narrow dependencies reduce compile-test coverage for older Gen2/Gen3 PCIe drivers. The file notes alphabetical sorting; adding entries out of order increases maintenance churn.

Test signals: Build all Renesas PHY configs under `ARCH_RENESAS`, compile-test the options that allow it, and verify selected helper symbols for USB2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/Makefile

Purpose: Maps Renesas PHY Kconfig symbols to driver object files.

Important APIs/types/functions: Builds `r8a779f0-ether-serdes.o`, `phy-rcar-gen2.o`, `phy-rcar-gen3-pcie.o`, `phy-rcar-gen3-usb2.o`, `phy-rcar-gen3-usb3.o`, and `phy-rzg3e-usb3.o` according to their respective config symbols.

Control flow: No runtime logic. Kbuild includes objects based on config values.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Integrates with `drivers/phy/renesas/Kconfig` and parent PHY build rules.

Risks: A config/object typo breaks builds or silently omits platform support. This file includes objects not otherwise researched in this subset, so changes should account for the whole Renesas PHY directory.

Test signals: Enable each config as module or built-in where supported and verify expected object/module generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen2.c

Purpose: Implements the Renesas R-Car Gen2/RZ-G1C USB PHY mux and power driver. It exposes two PHY choices per channel and programs `UGCTRL2` selection fields so PCI/USBHS/USB20/USB3 users get exclusive access to the shared hardware path.

Important APIs/types/functions: Core types are `struct rcar_gen2_phy`, `struct rcar_gen2_channel`, `struct rcar_gen2_phy_driver`, and `struct rcar_gen2_phy_data`. PHY ops are `rcar_gen2_phy_init()`, `_exit()`, `_power_on()`, `_power_off()` plus RZ/G1C-specific power ops. `rcar_gen2_phy_xlate()` maps child-node phandles and argument indexes to the correct PHY.

Control flow: Probe requires DT, gets the `usbhs` clock, maps MMIO, selects match data, allocates channel objects for child nodes, reads each child `reg`, derives the selection mask and two select values, creates two PHYs per channel, registers a provider, and stores driver data. Init uses `cmpxchg()` to reserve a channel exclusively, enables the clock, and writes the selected mux field under a spinlock. Power-on only performs PLL/connect sequencing for USBHS selections; RZ/G1C uses a different delay and USB20 suspend behavior. Exit disables the clock and releases the selected PHY.

State and persistence: `selected_phy` is per-channel exclusivity state, initialized to `-1`. `UGCTRL2`, `UGCTRL`, and `LPSTS` hardware fields persist until another PHY selection or power transition. A spinlock serializes shared register updates.

Dependencies and integration points: Depends on generic PHY, OF child nodes, clocks, platform MMIO, atomics, and spinlocks. Consumers are PCI/USB controller nodes that reference child PHYs.

Risks: `cmpxchg()` exclusivity assumes balanced `phy_exit()` calls. Child `reg` values index sparse arrays; invalid values fail probe. Only USBHS paths get PLL lock polling, so other selections rely on downstream controllers for validation.

Test signals: Probe all compatibles, validate phandle translation for each child/argument, attempt concurrent users on one channel and expect `-EBUSY`, verify UGCTRL2 mux bits, test USBHS PLL lock timeout behavior, and power-cycle PCI/USBHS/USB20 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-pcie.c

Purpose: Provides a small Renesas R-Car Gen3 PCIe PHY driver for R8A77980, controlling the PHY power-down bit in the PCIe PHY control register.

Important APIs/types/functions: `struct rcar_gen3_phy` stores the generic PHY, spinlock, and MMIO base. `rcar_gen3_phy_pcie_modify_reg()` serializes read-modify-write updates. PHY ops are `r8a77980_phy_pcie_power_on()` and `_power_off()`.

Control flow: Probe requires DT, maps MMIO, allocates state, initializes the spinlock, enables runtime PM, creates the PHY, registers a simple OF provider, and leaves power control to consumers. Power-on clears `PHY_CTRL_PHY_PWDN`; power-off sets it. Remove disables runtime PM.

State and persistence: Runtime state is only the MMIO base and lock. The power-down bit persists in hardware until the next power op or reset. Runtime PM is enabled for phy-core management, but there are no custom PM callbacks.

Dependencies and integration points: Depends on generic PHY, platform MMIO, OF, spinlocks, and runtime PM. PCIe controller nodes consume this PHY through OF.

Risks: The driver supports only the R8A77980 register layout. Any new compatible with a different offset or bit would need match data rather than reusing this file blindly. Error paths correctly disable runtime PM, so future resource additions should preserve that balance.

Test signals: Probe `renesas,r8a77980-pcie-phy`, verify provider registration, power-cycle through the PCIe host, inspect `PHY_CTRL_PHY_PWDN` transitions, and remove/unbind to confirm runtime PM disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rcar-gen3-pcie.c -->
