# Research Report: subset-b-005029

Grouped research for Marvell and MediaTek PHY drivers under `sources/distributed-fs/ceph-client/drivers/phy`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c

Purpose: Implements the Marvell Berlin SATA PHY provider for Berlin2 and Berlin2Q SoCs. It exposes one generic PHY per child DT lane and programs host VSA, MBUS, per-port SCR, and vendor-specific PHY registers for SATA Gen3 operation.

Important APIs and types: `struct phy_berlin_priv` holds the MMIO base, clock, spinlock, child PHY descriptors, and SoC-specific PHY base offset. `struct phy_berlin_desc` stores per-lane generic PHY, power-down bit, and lane index. Main callbacks are `phy_berlin_sata_power_on()`, `phy_berlin_sata_power_off()`, and `phy_berlin_sata_phy_xlate()`.

Control flow: Probe maps the SATA register resource, gets the controller clock, counts child nodes, chooses `BG2_PHY_BASE` or `BG2Q_PHY_BASE`, creates child PHYs, and powers them off. Power-on enables the clock, serializes shared VSA accesses with a spinlock, clears the lane power-down bit, configures MBUS request sizes, sets SATA mode, 25 MHz reference, Gen3 maximum speed, 40-bit width, max PLL rate, and controller Gen3 speed. Power-off reverses only the power-down bit.

State and persistence: Runtime state is per-device `priv` plus per-lane descriptors. Hardware register programming persists until power-off, reset, or another consumer changes the PHY. The driver does not store the active mode because it only supports SATA.

Dependencies and integration points: Depends on generic PHY, OF child nodes with `reg`, platform MMIO, and an unnamed clock. It is consumed by SATA controller DT phandles using the lane index.

Risks: Shared VSA address/data access is protected, but `clk_prepare_enable()` return values are ignored. Invalid child `reg` values abort probe after putting the current node. Register programming assumes 25 MHz reference and Gen3 capabilities. Partial power-off does not undo MBUS or speed settings.

Test signals: Build with Berlin SATA PHY enabled, DT probe with both compatible strings, two-lane xlate, SATA link negotiation at 1.5/3/6 Gbps, suspend/resume or remove/reprobe, and register readback of power-down and SCR speed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c

Purpose: Provides a USB PHY driver for Marvell Berlin2 and Berlin2CD/Q. It programs PLL, analog, RX, and TX tuning registers and registers a single generic PHY for USB controller consumers.

Important APIs and types: `struct phy_berlin_usb_priv` carries the MMIO base, reset control, and compatible-selected PLL divider. `phy_berlin_usb_power_on()` is the only PHY callback. `phy_berlin_pll_dividers[]` supplies different divider values through OF match data.

Control flow: Probe maps the resource, obtains the reset control, loads match-data PLL divider, creates a PHY, and registers `of_phy_simple_xlate`. Power-on resets the PHY block, writes PLL divider and PLL control bits, configures analog VCO/test settings, RX squelch/disconnect/filter parameters, TX voltage/amplitude, impedance calibration settings, and final drive/slew masks.

State and persistence: The driver keeps only immutable tuning choices and the reset line. Register state persists in hardware after `power_on`; there is no explicit power-off callback to undo or reset the block.

Dependencies and integration points: Uses generic PHY, reset framework, platform MMIO, OF match data, and USB controller phandles. Compatible strings distinguish Berlin2 from Berlin2CD/Q divider setup.

Risks: There is no polling for PLL lock or calibration completion, so failed hardware bring-up can surface only later in the USB controller. `device_get_match_data()` is assumed non-NULL. Repeated TX control writes deliberately pulse calibration-related fields, so reordering may break analog setup.

Test signals: Probe on both compatible strings, reset assertion/deassertion traces, USB host/device enumeration, high-speed signal quality, repeated PHY power-on through controller reset, and register dumps confirming divider selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-berlin-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c

Purpose: Implements the minimal Marvell MMP3 HSIC PHY provider. It enables the HSIC block and bypasses its PLL through one control register.

Important APIs and types: `struct mmp3_hsic_data` stores the MMIO base. `mmp3_hsic_phy_init()` is the sole PHY operation and sets `HSIC_ENABLE` and `PLL_BYPASS` in `HSIC_CTRL`.

Control flow: Probe allocates driver data, maps the MMIO resource, creates one generic PHY, associates drvdata, and registers `of_phy_simple_xlate`. Consumer `phy_init()` reads `HSIC_CTRL`, ORs in enable and PLL bypass bits, and writes it back.

State and persistence: There is no software state beyond the mapped base. Hardware state remains enabled after init; no exit or power-off callback clears the bits.

Dependencies and integration points: Uses the generic PHY framework and the `marvell,mmp3-hsic-phy` compatible. It is expected to be driven by the MMP3 USB/HSIC controller through a PHY phandle.

Risks: No clock, reset, calibration, or polling path exists, so it assumes the surrounding SoC code has prepared clocks and power domains. Lack of a disable callback may matter for suspend or module unload if the controller expects full shutdown.

Test signals: DT probe, successful `phy_init()` from the HSIC controller, HSIC device attach, suspend/resume behavior, and readback that `HSIC_ENABLE` and `PLL_BYPASS` are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c

Purpose: Supports the MMP3 USB2 PHY, including revision-specific PLL programming and explicit VCO/TX impedance calibration.

Important APIs and types: `struct mmp3_usb_phy` holds the PHY and register base. Register helpers `u2o_get()`, `u2o_set()`, and `u2o_clear()` wrap read-modify-write with readback. Main callbacks are `mmp3_usb_phy_init()` and `mmp3_usb_phy_calibrate()`.

Control flow: Probe maps registers, creates a PHY, and registers an OF provider. Init chooses A0 or B0 bit layouts using `cpu_is_mmp3_a0()` and `cpu_is_mmp3_b0()`, programs PLL feedback/reference dividers, PLL power/lock bypass/KVCO/ICP, TX impedance threshold, TX amplitude and VDD, slew rate, RX squelch threshold, analog power, and OTG power. Calibrate waits 200 us, starts VCO calibration, waits 400 us, pulses TX RCAL, waits again, then polls `USB2_PLL_READY_MASK_MMP3` for up to 100 ms.

State and persistence: The active programming persists in PHY registers until reset or power loss. No driver state records calibration result beyond returned errors.

Dependencies and integration points: Depends on MMP CPU revision helpers, generic PHY, platform MMIO, and `marvell,mmp3-usb-phy` DT binding. The USB controller invokes init/calibrate through generic PHY.

Risks: Unsupported silicon revisions fail init. The driver hardcodes analog values and depends on exact A0/B0 bit placements. Calibrate returns timeout but leaves earlier power and calibration bits as programmed.

Test signals: A0 and B0 probe coverage, `phy_init()` plus `phy_calibrate()`, timeout injection for PLL ready, USB enumeration after calibration, and register readback across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c

Purpose: Implements Armada 3700 COMPHY lane control for SATA, USB3 host, PCIe, and Ethernet SGMII/1000Base-X/2500Base-X. It directly programs three multiplexed lanes and their selector registers without firmware mediation.

Important APIs and types: `struct mvebu_a3700_comphy_priv` stores common, lane0/lane1 direct, and lane2 indirect register bases, selector lock, and 40 MHz XTAL state. `struct mvebu_a3700_comphy_lane` stores lane id, requested PHY mode/submode, and polarity inversion. Key callbacks are `mvebu_a3700_comphy_set_mode()`, `mvebu_a3700_comphy_power_on()`, `mvebu_a3700_comphy_power_off()`, and `mvebu_a3700_comphy_xlate()`.

Control flow: Probe maps named resources, detects optional `xtal` clock rate, creates one PHY per child lane, initializes each lane to invalid mode, and powers off all lanes. `set_mode` validates against `mvebu_a3700_comphy_modes[]` and refuses mode changes while powered. Power-on dispatches to mode-specific sequences. SATA selects lane2, clears isolation, sets polarity, 40-bit width, SATA mode, reference clock, max PLL rate, and polls TX PLL ready. USB3 selects lane0 or lane2, programs PIPE, SSC, reference clock, power/PLL bits, idle sync, 20-bit width, speed cap, reset release, and polls PCLK. PCIe is lane1 only and sets PIPE/clock/ref/mode before polling PCLK. Ethernet selects lane0/1, resets sideband pins, chooses 1.25 or 3.125 Gbps, optionally writes the large 40 MHz GBE init table, powers PLL/RX/TX, and polls PLL/RX init.

State and persistence: Mode, submode, and polarity are stored per lane. Selector writes are serialized because the selector register is shared. Hardware COMPHY setup persists until power-off, reset, or a later mode setup.

Dependencies and integration points: Integrates with generic PHY consumers for SATA, PCIe, USB3, and Ethernet; OF child `reg`; two-argument phandle xlate for port and polarity; named MMIO resources; optional XTAL clock; and kernel `enum phy_mode`/Ethernet interface modes.

Risks: Mode/lane combinations are strict, and invalid phandle arguments fail xlate. Lane2 indirect access is shared with SATA/USB3 and relies on address/data ordering. The Ethernet table is hardware-sensitive, especially for 40 MHz references. Power-off is lane-based rather than current-mode-only and may touch inactive alternate functions.

Test signals: DT coverage for all lanes and supported modes, polarity phandle tests, SATA/USB3/PCIe link training, SGMII/1000Base-X/2500Base-X Ethernet on 25 and 40 MHz XTAL boards, PLL timeout paths, and mode-change while powered returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c

Purpose: Provides Armada 3700 UTMI USB2 PHY support for both the USB3/USB2 OTG-connected PHY and the host-only USB2 PHY.

Important APIs and types: `struct mvebu_a3700_utmi_caps` distinguishes OTG/USB3-side versus host-side register layout via `usb32`. `struct mvebu_a3700_utmi` stores PHY registers, USB misc syscon regmap, capabilities, and PHY handle. Main callbacks are `mvebu_a3700_utmi_phy_power_on()` and `mvebu_a3700_utmi_phy_power_off()`.

Control flow: Probe maps UTMI registers, resolves `marvell,usb-misc-reg`, selects match-data caps, creates a PHY, powers it off, and registers an OF provider. Power-on programs PLL reference/feedback divisors for 25 MHz boards, enables misc pull-up and clears suspend, powers OTG and disables charger detection/pull-downs for `usb32`, then polls PLL calibration, impedance calibration, squelch calibration, and PLL ready. Power-off clears pull-up and suspend bits and powers down OTG if applicable.

State and persistence: The only software state is caps and regmap handles. PLL and calibration state persists in UTMI hardware. The driver does not cache calibration completion.

Dependencies and integration points: Uses generic PHY, platform MMIO, syscon regmap, and compatible-specific match data. USB controllers consume it through simple PHY phandles.

Risks: `power_off()` reads `USB2_PHY_CTRL(usb32)` from the UTMI MMIO base even though power-on updates that register through the USB misc regmap, which is suspicious if those address spaces differ. Calibration polling can delay up to one second per stage. The code assumes current boards use 25 MHz despite comments about older 40 MHz defaults.

Test signals: Probe both OTG and host compatibles, syscon lookup, USB2 host and OTG enumeration, charger-detection-disabled behavior, calibration timeout injection, and suspend/resume readback of misc pull-up/suspend bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-utmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c

Purpose: Supports Armada CP110 COMPHY lanes for PCIe, SATA, USB3 host/device, and several Ethernet SerDes modes. It prefers firmware SMC configuration and falls back to in-kernel legacy programming for a subset of Ethernet modes.

Important APIs and types: `struct mvebu_comphy_priv` holds MMIO base, system-controller regmap, clocks, device, and physical base passed to firmware. `struct mvebu_comphy_lane` stores lane id, mode/submode, and selected port. `mvebu_comphy_cp110_modes[]` is the lane/port/mode matrix. Key functions include `mvebu_comphy_smc()`, `mvebu_comphy_get_fw_mode()`, `mvebu_comphy_power_on()`, `mvebu_comphy_power_on_legacy()`, and `mvebu_comphy_set_mode()`.

Control flow: Probe resolves syscon, maps the COMPHY resource, tries to enable management and AXI clocks for compatibility, records the physical base, creates lane PHYs, and registers a custom xlate that records the port argument. `set_mode` normalizes 1000Base-X to SGMII, validates the lane/port/mode combination, and treats PCIe submode as width. Power-on builds a firmware parameter encoding mode, port, speed, polarity, and width, then calls `COMPHY_SIP_POWER_ON`. On firmware failure or unsupported call, it falls back to selector programming and legacy Ethernet sequences for SGMII/2500Base-X/RXAUI/10GBASE-R. Legacy paths program muxes, reset lanes, configure PLL/rate/DFE/equalization/training registers, poll PLL and RX init, then assert digital reset. Power-off similarly tries firmware first and clears resets/selectors in legacy fallback.

State and persistence: Lane mode, submode, and port are cached until changed. Hardware configuration is persistent in COMPHY and system-controller registers or firmware-owned state. Clocks are enabled for the device lifetime unless probe fails.

Dependencies and integration points: Integrates with ARM SMCCC firmware services, generic PHY consumers, CP110 syscon, named clocks, OF lane child nodes, and Ethernet/PCIe/SATA/USB controller phandles.

Risks: Firmware support level determines behavior; unsupported SMC calls leave Linux fallback available only for Ethernet modes, not SATA/USB/PCIe. Lane/port matrix errors can silently route PHYs incorrectly. PCIe width uses the `submode` integer. Clock initialization failures except defer are tolerated, which preserves DT compatibility but can hide hardware setup issues.

Test signals: Firmware and legacy paths, all lane/port combinations, SGMII/2500Base-X/RXAUI/5G/10G Ethernet links, PCIe width encoding, USB3 host/device, SATA, SMC error fallback, PLL/RX timeout handling, and suspend/resume after hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-comphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c

Purpose: Implements CP110 UTMI USB2 PHY support for two ports, including host/peripheral muxing, PLL sharing, per-port analog tuning, and optional D+/D- lane swapping.

Important APIs and types: `struct mvebu_cp110_utmi` stores UTMI MMIO, system-controller regmap, device, and ops. `struct mvebu_cp110_utmi_port` stores port id, USB data role, and `swap_dx`. Main helpers are `mvebu_cp110_utmi_port_setup()`, `mvebu_cp110_utmi_phy_power_on()`, and `mvebu_cp110_utmi_phy_power_off()`.

Control flow: Probe resolves `marvell,system-controller`, maps registers, iterates child ports, validates `reg`, derives role via `of_usb_get_dr_mode_by_phy()`, permits only one peripheral port, reads parent `swap-dx-lanes`, creates each PHY, and powers it off. Power-on first powers the port off, configures the device mux if peripheral, sets test suspend/select, waits for power down, programs PLL dividers, impedance threshold, TX amplitude, squelch, charger-detect voltages, and D+/D- swap, powers up the port in syscon, clears test select, then polls impedance calibration, PLL calibration, and PLL ready before enabling the shared PLL bit. Power-off clears the port power bit and powers down the shared PLL only if no port remains active.

State and persistence: Role, port id, and swap setting are per-port software state. Shared PLL state is inferred from syscon port bits at power-off rather than refcounted in software.

Dependencies and integration points: Uses generic PHY, syscon regmap, USB OF role helpers, child DT nodes, and a parent-level `swap-dx-lanes` property. Consumers are USB host/device controllers.

Risks: `regmap_test_bits()` error handling is minimal; negative errors are treated as non-active and may allow PLL shutdown. Role conflicts are downgraded to host mode rather than failing probe. Power-on modifies the global USB device mux, so dual-role board descriptions must be precise.

Test signals: Two-port probe, host/peripheral mux selection, one-device-only fallback, D+/D- swap boards, simultaneous port use with shared PLL retention, calibration timeout paths, and USB2 enumeration after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-cp110-utmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c

Purpose: Provides a simple built-in SATA PHY driver for Marvell MVEBU SoCs. It toggles PLL/IVREF/TX/RX power bits and SATA interface shutdown around a controller clock.

Important APIs and types: `struct priv` stores an unnamed clock and MMIO base. PHY callbacks are `phy_mvebu_sata_power_on()` and `phy_mvebu_sata_power_off()`. Probe creates a single generic PHY and registers `of_phy_simple_xlate`.

Control flow: Power-on enables the clock, sets `MODE_2_FORCE_PU_TX`, `MODE_2_FORCE_PU_RX`, `MODE_2_PU_PLL`, and `MODE_2_PU_IVREF`, clears `CTRL_PHY_SHUTDOWN`, and disables the clock. Power-off enables the clock, clears the same mode bits, sets `CTRL_PHY_SHUTDOWN`, and disables the clock. Probe maps resources, gets the clock, creates/registers the PHY, and turns off possible bootloader state.

State and persistence: Software state is only the clock/base pointer. Hardware power state persists in `SATA_PHY_MODE_2` and `SATA_IF_CTRL`.

Dependencies and integration points: Uses generic PHY, platform MMIO, clock framework, and `marvell,mvebu-sata-phy`. It is built in via `builtin_platform_driver()` for early SATA availability.

Risks: `clk_prepare_enable()` return values are ignored. No PLL-ready polling exists, so link failures surface at the SATA controller. The probe comment contains a typo but behavior intentionally disables bootloader-enabled PHY state.

Test signals: Built-in probe ordering, SATA link after power-on, bootloader-on handoff, controller remove or suspend power-off, and register readback of shutdown and mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c

Purpose: Supports the Marvell/PXA1928 28 nm HSIC PHY with clock-managed PLL setup, HSIC enable, impedance calibration wait, and connect interrupt wait.

Important APIs and types: `struct mv_hsic_phy` holds the PHY, platform device, MMIO base, and clock. `wait_for_reg()` wraps `readl_poll_timeout()`. PHY callbacks are `mv_hsic_phy_init()`, `mv_hsic_phy_power_on()`, `mv_hsic_phy_power_off()`, and `mv_hsic_phy_exit()`.

Control flow: Probe gets the clock, maps registers, creates a PHY, and registers a simple provider. Init enables the clock, programs PLL reference/feedback/LPF fields, powers the PLL, and waits for PLL lock. Power-on clears the SE0-on-resume drive bit, enables HSIC, waits for impedance calibration done, and waits for connect interrupt. Power-off clears HSIC enable. Exit powers down the PLL and disables the clock.

State and persistence: Clock enable spans init to exit. Register bits persist across power-on/off; power-off disables HSIC but not the PLL, which is released by exit.

Dependencies and integration points: Uses generic PHY, platform MMIO, an unnamed clock, and `marvell,pxa1928-hsic-phy`. The HSIC USB controller drives lifecycle callbacks.

Risks: Timeout paths in power-on return errors but leave HSIC enable set. Connect interrupt timeout is treated as a warning return path. Init disables the clock only on lock failure, so callback pairing matters.

Test signals: PLL lock and calibration success, HSIC device connection, timeout injection for PLL/calibration/connect, clock enable balance over init/exit, and resume behavior with `S2H_DRV_SE0_4RESUME` cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c

Purpose: Implements the Marvell/PXA1928 28 nm USB2 PHY, including PLL, TX/RX, digital, OTG, calibration polling, VBUS validity override, and analog shutdown.

Important APIs and types: `struct mv_usb2_phy` stores PHY, platform device, base, and clock. `wait_for_reg()` polls hardware status. Main callbacks are `mv_usb2_phy_28nm_init()`, `mv_usb2_phy_28nm_power_on()`, `mv_usb2_phy_28nm_power_off()`, and `mv_usb2_phy_28nm_exit()`.

Control flow: Probe obtains clock and MMIO, creates the PHY, and registers the provider. Init enables the clock, programs PLL divider/ICP/LPF fields, powers PLL by register, powers TX analog, sets TX amplitude, RX squelch, digital sync/filter settings, powers OTG by register, then waits for PLL/impedance calibration, RX squelch calibration, and PLL ready. Power-on sets overwrite and VBUS/AVALID/BVALID bits in `PHY_28NM_CTRL_REG3`. Exit powers down PLL, TX analog, OTG, and disables the clock.

State and persistence: Clock and analog power persist from init until exit. VBUS override state is intended to be controlled by power-on/off.

Dependencies and integration points: Uses generic PHY, an unnamed clock, platform MMIO, and `marvell,pxa1928-usb-phy`. USB controllers use the PHY lifecycle callbacks.

Risks: `mv_usb2_phy_28nm_power_off()` appears to use `readl(...) | ~(mask)` instead of clearing the mask with `& ~mask`, which sets most bits and likely corrupts `CTRL_REG3`. Calibration failures disable the clock but leave already-programmed registers. There is no explicit PLL lock polling after later power-on.

Test signals: Init calibration on real hardware, VBUS override behavior, power-off register readback to catch the mask bug, USB enumeration, timeout injection, and clock enable balance through init failure and exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c

Purpose: Provides a legacy Marvell PXA/MMP2 USB UTMI PHY driver with SoC-version-specific tuning for MMP2, PXA910, and PXA168.

Important APIs and types: `enum pxa_usb_phy_version` selects version behavior. `struct pxa_usb_phy` stores PHY, base, and version. Register helpers `u2o_get/set/clear/write()` provide relaxed MMIO with readback. PHY callbacks are `pxa_usb_phy_init()` and `pxa_usb_phy_exit()`.

Control flow: Probe selects version from OF match data, maps registers, creates a generic PHY, registers a provider, and creates legacy lookup aliases when no DT node exists. Init powers PLL and PHY, applies PXA910 extra reference bits if needed, programs PLL/TX/RX fields, writes a PXA168-specific IVREF workaround, pulses VCO calibration and TX RCAL with delays, polls `PLL_READY` up to 100 ms, and enables PXA168 reserve/OTG addon bits. Exit disables PXA168 OTG addon, clears buffer powerdown/clock/power bits, and powers down PLL/PHY.

State and persistence: Version is the only cached software state. Register programming persists until exit or reset. PLL-ready timeout only warns and init still returns success.

Dependencies and integration points: Uses generic PHY, platform MMIO, DT match data, optional legacy PHY lookup names for `mv-udc`, `pxa-u2oehci`, and `mv-otg`.

Risks: Timeout does not fail init. Hardcoded analog settings differ by board quirks only for PXA168 IVREF. Legacy lookup creation expands integration surface and can affect non-DT users. `dev_info()` in init/exit can be noisy.

Test signals: Probe each compatible, legacy non-DT lookup, USB host/device/OTG enumeration, PXA168 hub workaround validation, calibration timeout observation, and suspend/resume after exit/init cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig

Purpose: Defines Kconfig options for MediaTek PHY drivers in this directory, including PCIe, XFI T-PHY, T-PHY, UFS, XS-PHY, HDMI, MIPI CSI v0.5, MIPI DSI, and DisplayPort PHY support.

Important APIs and types: This file has no C APIs. It declares `CONFIG_PHY_MTK_PCIE`, `CONFIG_PHY_MTK_XFI_TPHY`, `CONFIG_PHY_MTK_TPHY`, `CONFIG_PHY_MTK_UFS`, `CONFIG_PHY_MTK_XSPHY`, `CONFIG_PHY_MTK_HDMI`, `CONFIG_PHY_MTK_MIPI_CSI_0_5`, `CONFIG_PHY_MTK_MIPI_DSI`, and `CONFIG_PHY_MTK_DP`.

Control flow: Kconfig controls compile inclusion. Most entries depend on `ARCH_MEDIATEK || COMPILE_TEST` and OF, select `GENERIC_PHY`, and add further dependencies such as `COMMON_CLK`, `REGULATOR`, `HAS_IOMEM`, or `OF_ADDRESS`.

State and persistence: There is no runtime state. Persistent effect is build configuration and module availability.

Dependencies and integration points: Integrates with the kernel configuration system and the local Makefile. Help text documents module names for CSI and feature scope for multiprotocol PHYs.

Risks: Missing dependencies can cause compile failures when drivers include clock, regulator, nvmem, or IO APIs. Overly broad `COMPILE_TEST` exposure is useful but can surface architecture-neutral warnings.

Test signals: `allmodconfig`/`allyesconfig` compile tests, per-option module builds, dependency resolution in menuconfig, and Makefile object inclusion matching each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile

Purpose: Maps MediaTek PHY Kconfig symbols to compiled objects and aggregate driver modules.

Important APIs and types: Defines Kbuild object assignments for DP, PCIe, T-PHY, UFS, XS-PHY, XFI T-PHY, HDMI, MIPI CSI, and MIPI DSI drivers. Aggregate objects are `phy-mtk-hdmi-drv` and `phy-mtk-mipi-dsi-drv`.

Control flow: Kbuild includes simple one-file objects when corresponding configs are enabled. HDMI builds common glue plus MT2701, MT8173, and MT8195 implementations into one module. MIPI DSI builds common glue plus MT8173 and MT8183 implementations into one module.

State and persistence: No runtime state. The build graph determines which symbols are linked together and which OF match data is available at runtime.

Dependencies and integration points: Coupled to `Kconfig` symbols and exported configuration structures declared in local headers. The aggregate object names determine module output names.

Risks: Omitting a SoC-specific object from an aggregate driver breaks OF match data or external config symbols at link time. Adding new compatibles requires updating both Kconfig dependencies, if needed, and this Makefile.

Test signals: Module and built-in builds for each config, link checks for HDMI/MIPI aggregate objects, and `modinfo` verifying expected aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c

Purpose: Implements a MediaTek DisplayPort PHY shim that programs lane driving defaults, link rate, spread-spectrum clocking, and a PHY digital reset through a regmap supplied by platform data.

Important APIs and types: `struct mtk_dp_phy` stores the regmap. PHY callbacks are `mtk_dp_phy_init()`, `mtk_dp_phy_configure()`, and `mtk_dp_phy_reset()`.

Control flow: Probe expects `dev->platform_data` to contain a `struct regmap **`, allocates state, creates a PHY, and optionally creates a non-DT lookup. Init bulk-writes the same six driving-parameter words to all four lanes. Configure maps DP link rates 1620, 2700, 5400, and 8100 Mbps to hardware bit-rate values when `opts->dp.set_rate` is set, and toggles SSC through `opts->dp.ssc`. Reset pulses `DP_GLB_SW_RST_PHYD` low then high with a short delay.

State and persistence: The driver stores only the regmap pointer. Hardware state persists in the shared DP PHY register block after init/configure/reset.

Dependencies and integration points: Uses generic PHY, platform driver binding by name rather than OF match, and a regmap supplied by a parent MediaTek DP device. DP controller code passes `phy_configure_opts_dp`.

Risks: Probe fails if platform data is absent, so it is tightly coupled to parent device instantiation. Unknown link rates return `-EINVAL`. Bulk write assumes contiguous driving registers and identical lane tuning.

Test signals: Parent-created platform device with regmap, four-lane driving register writes, rate changes for RBR/HBR/HBR2/HBR3, SSC on/off, reset pulse, and DP link training at each supported rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c

Purpose: Supplies MT2701-specific HDMI PHY clock and TMDS enable operations for the common MediaTek HDMI PHY driver.

Important APIs and types: Exports `mtk_hdmi_phy_2701_conf`. Internal clock ops implement `mtk_hdmi_pll_prepare()`, `mtk_hdmi_pll_unprepare()`, `mtk_hdmi_pll_set_rate()`, `mtk_hdmi_pll_determine_rate()`, and `mtk_hdmi_pll_recalc_rate()`.

Control flow: PLL prepare enables autocalibration, clears RLH, enables position divider, bias, PLL, clock LDO, SLDO, bias LPF, serializer, predriver, and driver with staged delays. Set-rate chooses TX position divider from target rate, programs prediv/posdiv/FBK/BIAS/impedance constants, and configures driver bias. Recalc derives rate from hardware prediv, feedback divider, TX posdiv, and optional /5 divider. TMDS enable/disable mirrors the full analog enable/disable sequence.

State and persistence: Rate is mostly hardware-derived; common `mtk_hdmi_phy` stores driver impedance and ibias values from DT. Register state persists while PLL/TMDS are enabled.

Dependencies and integration points: Uses `phy-mtk-hdmi.h` common structures and `phy-mtk-io.h` field helpers. The common HDMI probe selects this config via `mediatek,mt2701-hdmi-phy`.

Risks: `determine_rate()` accepts any rate without bounding, while set-rate uses coarse fixed feedback values. Prepare and TMDS enable duplicate sequencing, so call layering must avoid unexpected double programming. Analog timing is delay-sensitive.

Test signals: Clock registration through common driver, pixel clock set/recalc at low/mid/high rates, HDMI modes on MT2701, TMDS enable/disable during hotplug, and register readback of divider fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c

Purpose: Provides MT8173 HDMI PHY PLL and TMDS operations for the common MediaTek HDMI PHY driver.

Important APIs and types: Exports `mtk_hdmi_phy_8173_conf`. Clock ops are `mtk_hdmi_pll_prepare()`, `mtk_hdmi_pll_unprepare()`, `mtk_hdmi_pll_determine_rate()`, `mtk_hdmi_pll_set_rate()`, and `mtk_hdmi_pll_recalc_rate()`.

Control flow: Determine-rate stores requested PLL rate and chooses parent rate equal to rate below 74.25 MHz or half-rate above it. Set-rate selects pre-divider and TX divider buckets, programs PLL feedback and analog constants, and changes predriver impedance/bias based on whether the rate is below 165 MHz. Prepare enables PLL autocalibration, bias, PLL, bias LPF, and TX divider. TMDS enable only turns on serializer, predriver, and driver bits; power-off clears those bits.

State and persistence: `hdmi_phy->pll_rate` is cached because recalc returns the requested rate rather than reading register fields. IBIAS and impedance settings persist in hardware until the next rate change or disable.

Dependencies and integration points: Consumed by `phy-mtk-hdmi.c` through `mediatek,mt8173-hdmi-phy`. Uses common field helpers and DT-provided `mediatek,ibias`/`mediatek,ibias_up`.

Risks: Cached recalc can diverge from hardware if registers are changed outside this driver. Rate buckets and analog values are hardcoded and sensitive to HDMI mode boundaries. Parent-rate manipulation must match the display clock tree.

Test signals: HDMI modes around 27 MHz, 74.25 MHz, 165 MHz, and high TMDS rates; clk framework set/recalc behavior; TMDS off/on during display blanking; and IBIAS DT property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c

Purpose: Implements MT8195 HDMI PHY PLL, TMDS/FRL-related analog setup, HDMI 2.0 clock ratio handling, and a fixed 5 V regulator for HDMI power output.

Important APIs and types: Exports `mtk_hdmi_phy_8195_conf`. Important functions include `mtk_hdmi_pll_calc()`, `mtk_hdmi_pll_set_hw()`, `mtk_hdmi_pll_drv_setting()`, clock ops prepare/unprepare/set_rate/determine_rate/recalc_rate, `mtk_hdmi_phy_configure()`, and regulator ops for `hdmi-pwr5v`.

Control flow: Set-rate calculates PLL parameters for 25 to 594 MHz TMDS clocks. It selects TX position divider, finds a TX predivider that keeps ICO clock between 5 and 12 GHz, computes a 33-bit fractional feedback word, chooses digital divider, then writes hardware fields for prediv, feedback, posdiv stages, TX pre/pos dividers, and digital pixel divider. Prepare enables serializer/driver operation bits, disables FRL lane bits, applies bias/impedance settings based on pixel/TMDS range, powers bandgap/LDOs, powers PLL, clears isolation, and unpowers PLL. Configure sets PLL rate from `opts->dp.link_rate` and toggles HDMI 2.0 clock ratio for TMDS above 340 MHz. Regulator ops set, clear, and read the HDMI 5 V output bit.

State and persistence: `hdmi_phy->pll_rate` and `tmds_over_340M` are cached. Hardware analog/PLL and regulator state persists until unprepare, disable, or regulator operation.

Dependencies and integration points: Integrated by common HDMI driver, uses MT8195 register definitions in `phy-mtk-hdmi-mt8195.h`, field helpers, clk framework, generic PHY configure, and regulator core.

Risks: The configure path uses `phy_configure_opts_dp` for HDMI-specific link rate, which is an unusual API contract. PLL arithmetic has multiple boundary checks and integer divisions; boundary modes need coverage. Regulator state is direct MMIO without external enable tracking.

Test signals: Pixel clocks from 25 to 594 MHz, 340 MHz TMDS ratio transition, regulator enable/disable/is_enabled, HDMI 2.0 modes, invalid rate rejection, clock recalc, and suspend/resume preserving expected off state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h

Purpose: Defines MT8195 HDMI PHY register offsets, bitfields, and PLL constants used by `phy-mtk-hdmi-mt8195.c`.

Important APIs and types: Exposes macros such as `PCW_DECIMAL_WIDTH`, `PLL_PREDIV`, `PLL_FBKDIV_HS3`, HDMI config register offsets, PLL field masks, driver impedance/bias fields, FIFO enable, 5 V output bit, and pixel clock selection fields.

Control flow: No executable logic. The macros feed `mtk_phy_update_field()` and bit operations in the MT8195 implementation.

State and persistence: No software state. The masks define persistent MMIO fields for PLL, analog, TMDS, FRL, and regulator behavior.

Dependencies and integration points: Included only by the MT8195 HDMI PHY implementation. Depends on Linux bitfield macros and types.

Risks: Incorrect masks or offsets directly misprogram analog/PLL hardware and are not validated by the compiler beyond constant expression checks in field helpers. Names encode HDMI TX 2.1/20 hardware details, so reuse for another SoC would be risky.

Test signals: Compile coverage, register writes matching vendor reference values, PLL set-rate across all divider cases, and readback of power/clock/regulator bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c

Purpose: Provides common MediaTek HDMI PHY platform glue. It maps registers, registers the HDMI PLL clock, creates the generic PHY, reads common DT tuning properties, and dispatches to SoC-specific operations.

Important APIs and types: `to_mtk_hdmi_phy()` converts clock hardware to driver state. Common PHY callbacks are `mtk_hdmi_phy_power_on()`, `mtk_hdmi_phy_power_off()`, and `mtk_hdmi_phy_configure()`. Probe uses `struct mtk_hdmi_phy_conf` function pointers and optional regulator descriptor.

Control flow: Probe allocates state, maps registers, gets `pll_ref`, reads `clock-output-names`, loads OF match data, registers the PLL clock, reads `mediatek,ibias` and `mediatek,ibias_up`, installs default impedance values, creates a PHY with ops only when enable/disable callbacks exist, registers a PHY provider, optionally disables TMDS by default, optionally registers a fixed regulator, and registers the clock provider. Power-on enables the PLL clock then calls SoC TMDS enable; power-off disables TMDS then the clock. Configure delegates to SoC callback when present.

State and persistence: Stores MMIO base, device, SoC config, PLL clock, regulator device, PLL rate, impedance, ibias values, and MT8195 TMDS ratio flag. Devm resources handle lifetime.

Dependencies and integration points: Integrates generic PHY, clk provider, OF match data, regulator core, and SoC files for MT2701/MT8173/MT8195.

Risks: `mtk_hdmi_phy_dev_get_ops()` can return NULL if config callbacks are incomplete, making probe fail via `devm_phy_create()`. Required DT properties `mediatek,ibias` and `mediatek,ibias_up` are common even if a SoC might not use both. Clock provider registration is not devm-managed.

Test signals: Probe each compatible, PLL clock consumer set-rate, PHY power cycles, optional MT8195 regulator registration, missing DT property failures, and display hotplug/mode-set sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h

Purpose: Declares the common MediaTek HDMI PHY data structures and SoC configuration symbols shared by common and SoC-specific HDMI PHY files.

Important APIs and types: `struct mtk_hdmi_phy_conf` contains clock flags, default-off behavior, optional regulator descriptor, clock ops, TMDS enable/disable callbacks, and optional configure callback. `struct mtk_hdmi_phy` stores MMIO, device, config, PLL clock/hw, regulator, cached rate, impedance, ibias, and high-TMDS flag. Exports `to_mtk_hdmi_phy()` and three SoC config objects.

Control flow: No runtime logic in the header. It defines the interface by which SoC files provide clock and analog operations to `phy-mtk-hdmi.c`.

State and persistence: The state struct fields are live runtime state owned by the common probe and SoC callbacks. Cached PLL and TMDS state can influence later configure/prepare operations.

Dependencies and integration points: Includes clk, phy, platform, module, syscon, regulator, and type headers. Shared by MT2701, MT8173, MT8195, and common glue.

Risks: Adding fields or callbacks affects all SoC implementations. Optional callback semantics must remain clear, especially configure and regulator support.

Test signals: Compile/link of aggregate HDMI module, all OF match data resolving to declared configs, and callback presence validation in common probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h

Purpose: Provides small MMIO bit manipulation helpers for MediaTek PHY drivers.

Important APIs and types: Inline helpers are `mtk_phy_clear_bits()`, `mtk_phy_set_bits()`, and `mtk_phy_update_bits()`. Macro `mtk_phy_update_field()` validates constant masks and applies `FIELD_PREP()`.

Control flow: Each helper reads a 32-bit register, modifies bits, and writes it back. `mtk_phy_update_field()` uses `BUILD_BUG_ON_MSG()` to reject non-constant masks at compile time.

State and persistence: No software state. It writes persistent hardware register fields in caller-provided MMIO regions.

Dependencies and integration points: Used by MediaTek HDMI, MIPI CSI, MIPI DSI, and PCIe PHY drivers. Depends on Linux IO and bitfield helpers.

Risks: Helpers are not locked and provide no memory barriers beyond MMIO accessors. Read-modify-write is unsafe if hardware or another driver concurrently owns adjacent bits. Constant-mask enforcement is useful but prevents dynamic masks.

Test signals: Compile coverage of field macro use, register readback in callers, and sparse/lockdep review for shared-register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h

Purpose: Defines register offsets and bitfields for MediaTek MIPI CSI CD-PHY/DPHY receiver v0.5.

Important APIs and types: Provides offsets for ANA00, ANA18, ANA1C, ANA20, ANA24, ANA40, WRAPPER80, and ANAA8 blocks, plus masks for CPHY enable, bandgap, DPHY clock mode/select, equalizer tuning, reserve fields, async options, reset mode, and byte-clock inversion.

Control flow: No executable code. Macros are consumed by `phy-mtk-mipi-csi-0-5.c` during power-on/off and mode setup.

State and persistence: No software state. Definitions map to persistent analog receiver configuration bits in CSI PHY instances.

Dependencies and integration points: Included by the CSI v0.5 PHY implementation and relies on `BIT()`/`GENMASK()` being available through included translation units.

Risks: CSI0 and CSI1/CSI2 have similar but not identical field meanings; wrong macro choice can tune the wrong lane. Header comments clarify shared versus per-CSI naming, which is important when extending lane mappings.

Test signals: Compile coverage, CSI DPHY/CDPHY power-on register readback, camera capture on CSI0/1/2, and lane/equalizer tuning validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5-rx-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c

Purpose: Implements MediaTek MIPI CSI receiver CD-PHY v0.5 support, currently operating CD-PHY-capable blocks only in DPHY mode and supporting a fixed 4-data-plus-1-clock lane mapping.

Important APIs and types: `struct mtk_mipi_cdphy_port` stores device, base, PHY, PHY type, selected mode, and lane count. `enum PHY_TYPE` has DPHY, CPHY, and CDPHY. Key functions are `mtk_mipi_phy_power_on()`, `mtk_mipi_phy_power_off()`, and `mtk_mipi_cdphy_xlate()`.

Control flow: Probe maps registers, reads required `num-lanes`, interprets optional `phy-type` as DPHY or defaults to CDPHY, creates one PHY, and registers custom xlate. Xlate validates phandle arguments: CDPHY requires one argument and only DPHY mode with four lanes; DPHY requires no arguments. Power-on disables CPHY mode for CDPHY hardware, programs lane clock-mode/select mapping across CSIXA and CSIXB, inverts byte clocks, applies CDPHY or DPHY equalizer tuning, sets analog reserve and reset mode fields, then powers bandgap core and LPF. Power-off clears bandgap core/LPF on both halves.

State and persistence: Type, selected mode, and lane count are stored in `port`. Register state persists in both CSIXA and CSIXB banks until power-off or reset.

Dependencies and integration points: Uses generic PHY, DT phy arguments, `dt-bindings/phy/phy.h`, local register definitions, and MediaTek IO helpers. Camera/CSI receiver drivers consume this PHY.

Risks: Only 4D1C DPHY mapping is supported; other valid hardware layouts fail. `mode` is set by xlate, so consumers must request the PHY before power-on. Some raw constants such as `0x90` are not named.

Test signals: MT8365 probe, CDPHY phandle with DPHY argument, invalid argument and lane-count failures, camera stream startup/shutdown, CSIXA/B register readback, and multi-camera concurrent use if instantiated per port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c

Purpose: Supplies MT2701/MT8173 MIPI DSI TX PLL and lane signal operations for the common MediaTek MIPI TX driver.

Important APIs and types: Exports `mt2701_mipitx_data` and `mt8173_mipitx_data`. Clock ops implement prepare/unprepare, determine-rate, set-rate via common helper, and recalc via common helper. Signal callbacks enable or disable lane LDO outputs and pad tie-low.

Control flow: PLL prepare chooses TX dividers based on cached `data_rate` from 50 MHz to 1.25 GHz, powers bandgap, programs impedance/bias, enables LDO core/output, powers SDM, clears PLL enable, writes dividers and fractional PCW derived from 26 MHz, enables fractional mode and PLL, disables SSC, and writes the SoC preserve value. Unprepare disables PLL, clears preserve, isolates/powers down SDM, disables HS bias/LDOs/bandgap, and clears dividers. Signal enable sets LDO output on clock and four data lanes and clears pad tie-low; disable reverses it.

State and persistence: `mipi_tx->data_rate` is cached by common set-rate. `mppll_preserve` differs between MT2701 and MT8173. Register state persists until unprepare/power-off.

Dependencies and integration points: Used by `phy-mtk-mipi-dsi.c` aggregate driver through match data. Depends on common nvmem/drive-strength fields only indirectly.

Risks: Unsupported data rates outside 50 MHz to 1.25 GHz fail prepare. PLL math assumes 26 MHz reference. MT2701 and MT8173 share logic but differ preserve value; adding variants needs careful register compatibility review.

Test signals: DSI panel bring-up on MT2701 and MT8173, data-rate buckets at boundaries, PLL PCW readback, lane LDO/pad tie behavior, and display blank/unblank cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c

Purpose: Provides MT8183-specific MIPI DSI TX PLL, calibration-data programming, and lane signal callbacks for the common MediaTek MIPI TX driver.

Important APIs and types: Exports `mt8183_mipitx_data`. Clock ops use `.enable`/`.disable` rather than prepare/unprepare, plus common set/recalc and rate clamping. Important helpers are `mtk_mipi_tx_pll_enable()`, `mtk_mipi_tx_pll_disable()`, `mtk_mipi_tx_config_calibration_data()`, and signal power callbacks.

Control flow: PLL enable chooses posdiv from data rates 125 MHz to 2+ GHz, powers SDM, clears PLL enable, de-isolates, computes PCW from 26 MHz, writes PLL control, sets posdiv, and enables PLL. Signal power-on powers bandgap in two stages, disables software control for all lanes, programs drive-strength-derived LDO reference, writes 10 calibration bits for each of five lanes using `rt_code[]`, and enables clock-lane clock mode. Power-off re-enables software control for lanes and powers down bandgap/pad state.

State and persistence: Uses `mipi_tx->data_rate`, `mipitx_drive`, and `rt_code[]` loaded by common code from DT/nvmem. Calibration bits persist in per-lane registers until reset or next power-on.

Dependencies and integration points: Consumed by common MIPI TX probe for `mediatek,mt8183-mipi-tx`. Relies on optional nvmem calibration and `drive-strength-microamp`.

Risks: Calibration bit addressing uses `MIPITX_D2P_RTCODE * (i + 1) + j * 4`, so register layout assumptions are critical. Missing calibration values are forced to default nibble values. Data rates below 125 MHz fail.

Test signals: MT8183 DSI panel modes across rate buckets, nvmem calibration present/missing cases, drive-strength clamping, lane register readback, and power cycle display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c

Purpose: Provides common MediaTek MIPI DSI TX PHY glue: PLL clock registration, generic PHY power operations, drive-strength handling, optional nvmem calibration extraction, and OF dispatch to SoC-specific callbacks.

Important APIs and types: Exports common clock helpers `mtk_mipi_tx_pll_set_rate()` and `mtk_mipi_tx_pll_recalc_rate()`, plus `mtk_mipi_tx_from_clk_hw()`. Common PHY callbacks are `mtk_mipi_tx_power_on()` and `mtk_mipi_tx_power_off()`. Probe uses `struct mtk_mipitx_data` match data.

Control flow: Probe loads SoC data, maps registers, gets the reference clock, reads/clamps `drive-strength-microamp` with default 4600 uA, reads `clock-output-names`, registers the PLL `clk_hw`, creates the PHY, registers the PHY provider, stores `dev`, reads optional `calibration-data` nvmem into five RT codes, and registers the clock provider. Power-on enables the PLL clock then calls SoC signal enable. Power-off disables signals then the PLL clock.

State and persistence: `data_rate`, drive strength, `rt_code[]`, MMIO base, and SoC data are stored in `struct mtk_mipi_tx`. Hardware PLL and lane settings persist while powered.

Dependencies and integration points: Integrates generic PHY, clk provider, nvmem, OF match data, and SoC files for MT2701/MT8173/MT8183. Display DSI host drivers consume both the PHY and PLL clock.

Risks: Function name `mtk_mipi_tx_get_calibration_datal` has a typo but is internal. Optional nvmem failures are informational. Clock registration must happen before consumers request the PLL. Drive-strength range is clamped silently after warning.

Test signals: Probe each compatible, PLL clock set-rate/recalc, nvmem present/absent paths, invalid drive-strength warning and clamp, panel enable/disable, and runtime PM or suspend cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h

Purpose: Declares the shared data structures and symbols for MediaTek MIPI DSI TX common and SoC-specific files.

Important APIs and types: `struct mtk_mipitx_data` provides SoC preserve value, clock ops, and signal callbacks. `struct mtk_mipi_tx` stores device, registers, cached data rate, drive strength, five RT calibration codes, SoC data, and PLL clock hardware. Declares common clock helpers and SoC data objects.

Control flow: No executable logic. The header defines callback boundaries used by common probe and MT2701/MT8173/MT8183 implementations.

State and persistence: The struct fields hold runtime state used across clk and PHY callbacks. `rt_code[]` persists software-side calibration data extracted from nvmem and then written to hardware by SoC code.

Dependencies and integration points: Includes clk, nvmem, platform, PHY, module, delay, and slab headers. Shared by aggregate `phy-mtk-mipi-dsi-drv`.

Risks: Adding fields or changing callback semantics affects all SoC implementations. Clock op style differs between MT8173-style prepare and MT8183-style enable callbacks but shares the same common state.

Test signals: Aggregate module compile/link, all SoC match data references, and panel enable paths invoking both common and SoC callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c

Purpose: Implements MediaTek PCIe PHY initialization for MT8195, focused on software loading of eFuse impedance calibration values into PHY SIF registers.

Important APIs and types: `struct mtk_pcie_lane_efuse` stores per-lane TX PMOS/NMOS and RX data. `struct mtk_pcie_phy_data` describes lane count and eFuse support. `struct mtk_pcie_phy` stores device, PHY, SIF base, SoC data, global eFuse value, and per-lane eFuse array. Main callbacks/helpers are `mtk_pcie_phy_init()`, `mtk_pcie_read_efuse()`, and `mtk_pcie_efuse_set_lane()`.

Control flow: Probe maps the named `sif` resource, creates a PHY, loads match data, optionally attempts to read nvmem eFuse data, and registers a simple provider. eFuse read is optional; non-defer/non-ENOMEM failures are ignored by probe. When enabled, it reads `glb_intr` and three cells per lane (`tx_ln%d_pmos`, `tx_ln%d_nmos`, `rx_ln%d`) and validates nonzero lane data. `phy_init()` writes the global internal resistor selection and each supported lane's TX/RX impedance fields. The comment notes hardware resets these settings during suspend, so consumers should call init again on resume.

State and persistence: eFuse values are cached in memory after probe. Hardware SIF fields persist until reset or suspend-induced loss and are restored by `phy_init()`.

Dependencies and integration points: Uses generic PHY, named platform MMIO, OF match data, nvmem cells, and MediaTek IO field helpers. The PCIe controller is the PHY consumer.

Risks: Optional eFuse failures can silently leave default hardware calibration. Cell names must match lane count exactly. Only MT8195 data is present with two lanes. No power-on/off handling is provided.

Test signals: Probe with and without nvmem cells, defer behavior for missing nvmem provider, lane eFuse write readback, PCIe Gen3 link quality, suspend/resume re-init, and invalid all-zero lane data handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-pcie.c -->
