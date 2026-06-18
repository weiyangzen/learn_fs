# Research Group: subset-b-005042

This grouped report covers the Tegra XUSB pad controller sources and TI PHY build metadata assigned to `subset-b-005042`. Each file section is delimited for reconciliation into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra124.c -->
# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra124.c` Research

## Purpose

This file implements the NVIDIA Tegra124/Tegra132 XUSB pad controller SoC backend. It supplies the SoC-specific pad, lane, port, PHY, fuse-calibration, PLL, and ELPG register operations consumed by the common Tegra XUSB padctl core in `xusb.c`/`xusb.h`. It covers USB2 UTMI lanes, one ULPI lane, HSIC lanes, PCIe UPHY lanes that may be muxed to USB3 SuperSpeed, and a SATA lane that may also serve USB3.

## Important APIs, Types, and Functions

- `struct tegra124_xusb_fuse_calibration` stores HS current, IREF, termination, and squelch fuse-derived calibration for USB2 pads.
- `struct tegra124_xusb_padctl` embeds the common `struct tegra_xusb_padctl` and the Tegra124 fuse data.
- `tegra124_xusb_padctl_probe()` allocates SoC private state and calls `tegra124_xusb_read_fuse_calibration()`.
- `tegra124_xusb_padctl_enable()` / `tegra124_xusb_padctl_disable()` reference-count and sequence AUX mux LP0 clamp/vcore bits.
- `tegra124_usb3_save_context()` samples USB3 DFE/CTLE tuning from IOPHY misc output registers and stores it in the common USB3 port structure.
- `tegra124_hsic_set_idle()` toggles HSIC pull-down/pull-up state for idle.
- Per-pad probe/remove and `struct phy_ops` sets exist for USB2, ULPI, HSIC, PCIe, and SATA.
- `tegra124_usb3_port_enable()` programs SuperSpeed port mapping, EQ/CDR/DFE tuning, RX eye enable, SATA-specific PLL details when applicable, and ELPG unclamp sequencing.
- `tegra124_xusb_padctl_soc` is the exported SoC descriptor consumed by the common platform driver.

## Control Flow

The common driver matches `"nvidia,tegra124-xusb-padctl"` or Tegra132-compatible data to `tegra124_xusb_padctl_soc`. Probe allocates the private padctl and reads fuses. Common pad setup then creates enabled pads from the SoC pad list, registers lanes as generic PHYs, parses each lane's `nvidia,function`, and programs the mux field at each lane's register offset. Common port setup creates optional USB2/ULPI/HSIC/USB3 ports, maps each port to a lane, parses port properties, and calls each port's enable callback.

PHY users drive the main runtime behavior through `phy_ops`. USB2 and HSIC init/exit take/release the padctl AUX clamp reference. USB2 power-on programs fuse-calibrated bias and OTG pad registers, sets the port capability to host in this older implementation, enables VBUS, and powers up the shared USB2 bias pad under a pad-local reference count. HSIC power-on enables its regulator, writes trim and tuning values from lane state, and clears HSIC power-down bits. PCIe and SATA power-on manually initialize PLLs, poll lock bits with 50 ms timeouts, and clear IDDQ for the lane group. USB3 port enable maps the port to its USB2 companion, configures equalization/tuning, optionally restores saved context, and performs ELPG vcore/clamp deassertion.

## State and Persistence

Persistent hardware-facing state is mostly register state plus fuse-derived calibration cached in memory. The padctl has a shared `enable` reference count guarding AUX LP0 clamp sequencing; USB2 pads have their own `enable` count for the shared bias pad. USB3 context (`tap1`, `amp`, `ctle_g`, `ctle_z`, `context_saved`) is stored in the common USB3 port object after `tegra124_usb3_save_context()`. There is no suspend/resume hook in this file's padctl ops, so durable low-power context restoration is narrower than Tegra210/186.

## Dependencies and Integration Points

The file depends on common Tegra XUSB data structures from `xusb.h`, generic PHY APIs, device tree lane/port child nodes, regulators for VBUS/HSIC supplies, Tegra fuse reads, reset/clock primitives, and low-level MMIO access through `padctl_readl()`/`padctl_writel()`. It integrates with the common driver through pad, lane, port, and padctl ops tables. External USB/XHCI/PCIe/SATA consumers see the result as generic PHYs and exported padctl services through the common layer.

## Risks and Edge Cases

- PLL lock paths rely on fixed 50 ms polling windows and return `-ETIMEDOUT`; marginal hardware or clock setup issues can fail PHY bring-up.
- USB2 power-on unconditionally writes the USB2 port capability as host, which is less role-flexible than newer SoCs.
- The SATA power-off path sets `value |= ~XUSB_PADCTL_IOPHY_MISC_PAD_S0_CTL1_IDDQ_OVRD` and `value |= ~XUSB_PADCTL_IOPHY_MISC_PAD_S0_CTL1_IDDQ`, which appears suspicious because it sets nearly all bits rather than setting/clearing the named bits only.
- USB3 port enable contains a TODO noting that some PCIe/SATA PHY setup may belong in PHY power-on callbacks, so ordering may be hardware-sensitive.
- Error unwinding around regulator enable and pad counts should be tested carefully because shared pad state spans multiple lane users.

## Test Signals

Useful validation signals include `CONFIG_ARCH_TEGRA_124_SOC` builds, device-tree lane mux combinations for USB2/ULPI/HSIC/PCIe/SATA, probe logs for fuse reads and optional pad creation, PHY power-on/off cycles, USB2 VBUS behavior, HSIC idle transitions, USB3 companion mapping, PLL timeout absence, and suspend/resume or controller reset tests that exercise `tegra124_usb3_save_context()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra186.c -->
# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra186.c` Research

## Purpose

This file implements the Tegra186-family XUSB padctl backend, with shared support for Tegra186, Tegra194, and Tegra234 SoC descriptors. Compared with Tegra124/210 it focuses on USB2 UTMI and USB3 SuperSpeed pads and implements AO-register sleepwalk/wake handling for low-power USB wake. It also handles UTMI bias tracking, VBUS/ID override for role switching, fuse calibration, and minimal suspend context save/restore.

## Important APIs, Types, and Functions

- `struct tegra_xusb_fuse_calibration` stores per-USB2 HS current levels plus squelch, termination, and RPD control values.
- `struct tegra186_xusb_padctl_context` stores `vbus_id`, USB2 mux/capability, and SS capability registers across noirq suspend.
- `struct tegra186_xusb_padctl` embeds the common padctl, AO MMIO base, calibration data, USB2 tracking clock, UTMI enabled bitmap, and context.
- `tegra186_utmi_enable_phy_sleepwalk()` / `tegra186_utmi_disable_phy_sleepwalk()` program XUSB AO UTMI sleepwalk phases and wake detection.
- `tegra186_utmi_enable_phy_wake()` / `tegra186_usb3_enable_phy_wake()` set ELPG wake interrupt bits; matching disable and remote-wake-detected helpers clear/check those bits.
- `tegra186_utmi_bias_pad_power_on()` / `_off()` handle shared UTMI bias and tracking clock state.
- `tegra186_utmi_phy_set_mode()` implements OTG host/device/none transitions through ID and VBUS override helpers.
- `tegra186_usb3_phy_power_on()` programs SS port capability, optional Gen1-only speed support, and ELPG unclamp.
- Exported SoC descriptors include `tegra186_xusb_padctl_soc`, `tegra194_xusb_padctl_soc`, and `tegra234_xusb_padctl_soc`.

## Control Flow

The common padctl driver selects the SoC descriptor based on compatible strings. `tegra186_xusb_padctl_probe()` allocates the private structure, maps the `"ao"` MMIO resource, and reads fuse calibration. USB2 pad probe obtains the `trk` clock and registers UTMI PHY ops. USB3 pad probe registers SS PHY ops. Common port setup creates USB2 and USB3 ports according to the selected SoC port counts.

On UTMI power-on, the code maps the USB2 port to XUSB, sets port capability from `mode`, applies fuse-calibrated HS current/term/RPD values, and powers on the UTMI pad plus shared bias. Host-mode init enables the VBUS regulator; peripheral/OTG init resets VBUS/ID override to floating. Runtime mode changes use `PHY_MODE_USB_OTG` submodes to assert grounded ID for host, assert VBUS override for device, or clear both for none. USB3 power-on looks up its companion USB2 port, mirrors the companion role into SS port capability, optionally limits speed to Gen1 if `maximum-speed = super-speed`, and releases ELPG clamps.

For low-power wake, UTMI sleepwalk is programmed in AO registers: disable master, select low-power config, debounce lines, clear fake/wake state, save current speed, configure phased J/K/high-Z drive behavior, capture pad config, switch electrical control to XUSB_AO, program wake match, then enable line wake. USB3 sleepwalk is simpler and mainly asserts/deasserts ELPG clamps. Wake enable/disable functions manipulate ELPG wake event and interrupt bits.

## State and Persistence

The driver keeps fuse calibration in memory, tracks enabled UTMI pads in a bitmap, and uses a shared tracking clock for bias pad calibration. Noirq suspend saves the VBUS/ID override, USB2 pad mux, USB2 port cap, and SS port cap registers; resume restores them. Remote wake state is represented by sticky ELPG wake event bits combined with interrupt-enable bits. The AO sleepwalk configuration persists in AO registers while the main XUSB domain sleeps.

## Dependencies and Integration Points

Dependencies include device-tree MMIO resources (`"ao"`), generic PHY, regulator, clock, fuse, platform, and common XUSB padctl APIs. The common driver provides lane/port creation and external exported helpers, while this file supplies the SoC-specific lane ops and padctl ops. Tegra194 and Tegra234 reuse the same code with different port counts, supply names, and capability flags (`supports_gen2`, tracking polling, tracking update behavior, and low-power config enable).

## Risks and Edge Cases

- `tegra186_usb3_pad_remove()` casts the USB3 pad with `to_usb2_pad()`, which is likely a copy/paste bug; layout compatibility masks it only while the embedded base is first and no USB2-specific members are touched.
- Sleepwalk programming has many ordered register writes and short delays; missing AO resources or wrong SoC capability flags can break wake from suspend.
- UTMI bias tracking warns but continues on tracking-complete poll failure; systems may still work but signal-quality margin can degrade.
- Role switching mixes regulator state with VBUS/ID override. Failed regulator enable/disable paths can leave override state partially changed.
- HSIC support is disabled behind `#if 0` for Tegra186 in this file, so device trees expecting HSIC on this backend will not get a pad/port.

## Test Signals

Test with `CONFIG_ARCH_TEGRA_186_SOC`, `CONFIG_ARCH_TEGRA_194_SOC`, and `CONFIG_ARCH_TEGRA_234_SOC` compile coverage, DT resources named `"ao"`, USB2/USB3 port role combinations, `maximum-speed` limiting, runtime role switching through usb-role-switch, suspend/resume with remote wake from UTMI and SS devices, UTMI tracking-clock availability, and dmesg warnings for tracking poll or fuse read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra210.c -->
# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra210.c` Research

## Purpose

This file implements the Tegra210 XUSB padctl backend. It is the most feature-rich file in this group: it handles USB2 UTMI, HSIC, PCIe UPHY lanes, SATA UPHY lanes, USB3 SuperSpeed mapping over PCIe/SATA lanes, PLL bring-up, PMC-backed sleepwalk, wake-event programming, role-switch VBUS/ID overrides, fake USB3 companion ports for device/OTG-only USB2 ports, and noirq suspend context save/restore.

## Important APIs, Types, and Functions

- `struct tegra210_xusb_fuse_calibration` caches USB2 HS current, termination, and RPD fuse values.
- `struct tegra210_xusb_padctl_context` stores key mux/capability registers across suspend.
- `struct tegra210_xusb_padctl` embeds common padctl state, a PMC `regmap`, fuse calibration, and saved context.
- `tegra210_pex_uphy_enable()` and `tegra210_sata_uphy_enable()` perform PLL/reset/calibration/lock sequencing for PCIe and SATA UPHY groups.
- `tegra210_uphy_init()` and `tegra210_uphy_deinit()` coordinate UPHY group bring-up/down and AUX LP0 clamp state.
- `tegra210_pmc_utmi_enable_phy_sleepwalk()` and `tegra210_pmc_hsic_enable_phy_sleepwalk()` program PMC USB sleepwalk state for UTMI and HSIC.
- `tegra210_usb2_phy_power_on()` / `_off()`, `tegra210_hsic_phy_power_on()` / `_off()`, and `tegra210_usb3_phy_power_on()` / `_off()` are the main PHY power paths.
- `tegra210_usb2_phy_set_mode()` drives OTG role changes through VBUS/ID override and VBUS regulator state.
- `tegra210_utmi_port_reset()` detects battery-charger ZIP/ZIN bits and toggles VBUS override as a port reset signal.
- `tegra210_xusb_padctl_soc` exports the SoC descriptor with USB2, HSIC, and USB3 port ops plus supply names.

## Control Flow

Probe allocates `struct tegra210_xusb_padctl`, reads fuse calibration from `TEGRA_FUSE_SKU_CALIB_0` and `TEGRA_FUSE_USB_CALIB_EXT_0`, and optionally finds the PMC phandle/regmap named `"usb_sleepwalk"`. Common pad setup creates USB2, HSIC, PCIe, and SATA pads; lane mux programming temporarily asserts IDDQ through lane ops for UPHY lanes; common port setup maps USB2/HSIC ports directly and maps USB3 ports through `tegra210_usb3_map`.

PCIe/SATA PHY init calls `tegra210_uphy_init()` under the padctl lock. That enables PCIe and SATA PLLs if present, performs manual PLL calibration and RCAL polling unless hardware sequencing is already enabled, switches PLLs to hardware control, starts hardware sequences, and deasserts AUX LP0 clamps. SuperSpeed PHY power-on then maps the SS port to its USB2 companion, writes UPHY USB3 electrical tuning registers, and releases per-port ELPG clamps.

USB2 init enables host-mode VBUS and assigns the shared USB2 bias pad to XUSB. USB2 power-on handles fake USB3 port unclamping when the common layer assigned one, programs squelch/disconnect levels, role-specific port capability, fuse-calibrated current and RPD/termination, charger VREG settings, and shared bias tracking through the `trk` clock with a pad reference count. Power-off reverses fake-port ELPG state and powers down the shared bias pad when the count reaches zero. OTG mode changes ground ID and enable regulator for host, set VBUS override for device, or clear both for none.

HSIC power-on applies trim/tuning, clears HSIC power-down bits, enables the tracking clock, runs HSIC tracking timers, then disables the clock. PMC sleepwalk for UTMI/HSIC copies active electrical parameters into PMC registers, configures saved line state, staged pull-up/pull-down behavior, wake match values, and line wake enables. ELPG wake helpers program sticky wake event and interrupt-enable bits for UTMI, HSIC, and SuperSpeed lanes.

## State and Persistence

The driver persists fuse-derived calibration in memory, PMC sleepwalk settings in PMC registers, UPHY PLL enable state in `pcie->enable` and `sata->enable`, USB2 shared bias state in `usb2->enable`, and fake USB3 port assignment in common USB2 port state. Noirq suspend deinitializes UPHY, saves USB2 pad mux, USB2 port capability, SS port map, and USB3 pad mux, then resume restores the muxes while temporarily asserting IDDQ on UPHY lanes before reinitializing UPHY. Remote wake detection reads ELPG wake interrupt/event bits.

## Dependencies and Integration Points

Dependencies include generic PHY, clocks, reset controls, regulators, Tegra clock helpers (`tegra210_plle_*`, `tegra210_xusb_pll_*`, `tegra210_sata_pll_*`), Tegra fuse data, PMC regmap via device tree, common XUSB padctl data structures, and device-tree lane/port definitions. It integrates with the common driver through pad/lane/port/padctl ops and with USB role switching through the common USB2 port mode callback.

## Risks and Edge Cases

- PLL bring-up has multiple timeout loops; failures can leave resets/clocks partially unwound and should be validated on all mux combinations.
- PMC sleepwalk is optional: missing `nvidia,pmc` or missing `"usb_sleepwalk"` regmap leaves sleepwalk ops returning `-EOPNOTSUPP`.
- Fake USB3 port handling is necessary for device/OTG USB2 ports without a companion; bad DT port counts can exhaust fake ports and fail setup in the common layer.
- `tegra210_hsic_phy_power_off()` reads `HSIC_PADX_CTL0` but writes the modified power-down bits to `HSIC_PADX_CTL1`, which looks suspicious and may prevent proper HSIC power-down.
- `tegra210_sata_pad_probe()` stores a reset but never obtains `sata->pll`, while `tegra210_sata_uphy_enable()` calls `clk_prepare_enable(sata->pll)`; this depends on external initialization or is a potential null/invalid clock path.
- Role switching calls `regulator_is_enabled()` and disable without checking all return paths, so regulator providers with strict semantics need runtime coverage.

## Test Signals

Useful signals include Tegra210 builds, DT validation for USB2/HSIC/PCIe/SATA lanes and PMC phandle, UPHY PLL lock and RCAL success without timeout logs, USB3 lane-to-port mapping for PCIe and SATA lanes, fake USB3 port assignment for peripheral/OTG USB2 ports, HSIC bring-up/power-down, runtime usb-role-switch host/device/none transitions, UTMI port reset behavior on ZIP/ZIN, suspend/resume with UTMI/HSIC/SS wake, and absence of ELPG clamp ordering regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.c -->
# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.c` Research

## Purpose

This file is the common NVIDIA Tegra XUSB pad controller platform driver. It abstracts SoC-specific padctl behavior behind ops tables from `xusb.h`, creates pad devices, generic PHY lane providers, and port devices from device tree, wires USB role-switch compatibility, manages regulators/resets, handles suspend/resume dispatch, and exports helper APIs used by Tegra USB/XHCI/PHY consumers.

## Important APIs, Types, and Functions

- `tegra_xusb_padctl_of_match[]` maps compatible strings to SoC descriptors for Tegra124/210/186/194/234.
- `tegra_xusb_lane_parse_dt()` validates each lane's `nvidia,function` against its SoC function list.
- `tegra_xusb_pad_init()`, `tegra_xusb_pad_register()`, and `tegra_xusb_pad_unregister()` create pad devices and lane PHY providers.
- `tegra_xusb_setup_pads()` creates pads and programs lane mux functions.
- `tegra_xusb_find_lane()`, `tegra_xusb_port_find_lane()`, `tegra_xusb_find_port()`, and typed USB2/USB3 find helpers connect ports to lanes.
- `tegra_xusb_setup_usb_role_switch()` registers a USB role switch and a legacy `usb_phy` notifier bridge for OTG/peripheral modes.
- `tegra_xusb_setup_ports()` creates USB2, ULPI, HSIC, and USB3 ports and optionally assigns fake USB3 ports.
- `tegra_xusb_padctl_probe()` / `_remove()` own platform lifecycle.
- Exported functions include padctl get/put, USB3 context save, HSIC idle, sleepwalk/wake enable/disable, remote wake detection, LFPS detect, VBUS override, UTMI reset/pad power, companion lookup, and port-number lookup.

## Control Flow

Platform probe first checks for modern `"pads"` child nodes. If missing, it delegates to legacy probe for old device trees. For modern DTs, it gets the SoC descriptor, asks the SoC-specific probe to allocate padctl state, maps MMIO, gets reset and regulators, deasserts reset, enables supplies, then sets up pads and ports.

Pad setup iterates the SoC pad list, finds each pad's DT node under `pads`, calls the pad's SoC-specific probe, registers enabled lane child nodes as PHYs, parses lane functions, and then writes mux bits for each lane through `tegra_xusb_lane_program()`. Port setup iterates SoC port counts for USB2, ULPI, HSIC, and USB3, creates each enabled port device from the `ports` node, maps it to a lane through SoC port ops, parses port-specific properties, and calls port enable callbacks. For SoCs that require fake USB3 ports, USB2 OTG/peripheral ports without a real companion are assigned an unused USB3 index.

For USB role switching, USB2 port parsing defaults to host when `mode` is absent. Peripheral or OTG modes require `usb-role-switch`; setup registers a `usb_role_switch`, creates a legacy `usb_phy` with OTG callbacks, schedules notifier work on role changes, and populates connector child devices. Removal unwinds ports, role-switch state, pads, supplies, reset, and SoC private state in reverse order.

## State and Persistence

The common `struct tegra_xusb_padctl` keeps lists of pads, lanes, and ports, mapped registers, reset, supplies, clock pointer, a mutex, and SoC descriptor. Pad/lane/port objects live as devices or PHY-private data and are freed by release/remove hooks. USB2 port state records mode, internal flag, VBUS regulator, and fake USB3 assignment. USB3 port state records companion USB2 port, internal flag, Gen2 limit, and saved tuning fields. Suspend/resume is delegated to SoC ops; the common layer itself preserves list/device topology but not hardware registers.

## Dependencies and Integration Points

This file depends on Linux platform driver, device tree, generic PHY, regulator, reset, USB role-switch, legacy USB PHY/OTG, workqueue, and Tegra fuse headers. It is the integration point between SoC-specific padctl files and external USB controller drivers. External consumers use the PHY provider under each pad, the exported `tegra_xusb_padctl_*` helpers, and DT phandle `nvidia,xusb-padctl`.

## Risks and Edge Cases

- Modern DT detection is binary: missing `pads` falls into legacy handling, so partial or malformed modern DTs may fail in less obvious ways.
- Peripheral/OTG USB2 modes fail probe without `usb-role-switch`, making DT correctness critical.
- `tegra_xusb_setup_ports()` logs port enable failures but continues after individual enable errors; later PHY consumers may see delayed failures.
- Fake USB3 port assignment depends on disabled/unavailable USB3 DT ports; a fully populated USB3 set leaves no fake port for OTG/peripheral-only USB2.
- Role-switch setup allocates a minimal `device_driver` to satisfy role-switch owner expectations and temporarily assigns driver pointers to PHY devices; changes in USB core assumptions could affect this bridge.
- Exported helpers often return `-ENOSYS`, `-ENOTSUPP`, or `-EOPNOTSUPP` depending on missing SoC ops, so callers must not assume uniform errors.

## Test Signals

Validation should include platform probe/remove on every matched compatible, legacy-DT fallback, pad/lane DT function validation including invalid functions, optional disabled pads/ports, PHY provider lookup, USB2 host/peripheral/OTG mode parsing, role-switch default mode, fake USB3 assignment, suspend/resume dispatch to SoC ops, exported helper behavior when SoC ops are absent, and leak/error-unwind checks around partial pad/port creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.h -->
# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.h` Research

## Purpose

This header defines the internal data model and SoC abstraction for the Tegra XUSB pad controller driver family. It is shared by the common platform driver and SoC-specific backends. The header describes lanes, pads, ports, padctl controller state, ops tables, inline type conversions, register access helpers, and exported SoC descriptors.

## Important APIs, Types, and Functions

- Lane model: `struct tegra_xusb_lane_soc`, `struct tegra_xusb_lane`, typed lane wrappers for USB3/USB2/ULPI/HSIC/PCIe/SATA, and `struct tegra_xusb_lane_ops`.
- Pad model: `struct tegra_xusb_pad_soc`, `struct tegra_xusb_pad`, typed pad wrappers, and `struct tegra_xusb_pad_ops`.
- Port model: `struct tegra_xusb_port`, typed USB2/ULPI/HSIC/USB3 port wrappers, `struct tegra_xusb_lane_map`, and `struct tegra_xusb_port_ops`.
- Controller model: `struct tegra_xusb_padctl_soc`, `struct tegra_xusb_padctl_ops`, and `struct tegra_xusb_padctl`.
- Helpers: `padctl_readl()`, `padctl_writel()`, `padctl_readl_poll()`, `tegra_xusb_find_lane()`, `tegra_xusb_find_port()`, typed find/release/remove helpers, and pad registration functions.
- Conditional externs expose SoC descriptors only when their architecture configs are enabled.

## Control Flow

The header itself has no executable top-level flow, but it defines how flow is dispatched. The common driver owns generic object lifecycle and calls padctl/pad/lane/port ops through these structures. SoC files populate static `tegra_xusb_padctl_soc` descriptors with pad arrays, port counts, supply names, and ops. A pad's lane ops probe/remove lane-private objects and optionally provide IDDQ, sleepwalk, wake, and remote-wake behavior. A port's ops map logical ports to lanes and enable/disable port-specific hardware. Padctl ops provide SoC-level probe/remove, PM, context, VBUS, LFPS, HSIC idle, and UTMI hooks.

## State and Persistence

The defined state is hierarchical. `tegra_xusb_padctl` is the root and owns MMIO registers, reset, regulators, mutex, and lists of pads/lanes/ports. Pads own PHY provider state and arrays of lane PHYs. Lanes keep parsed function index, DT node, lane index, and back-pointer to their pad. Ports retain lane association, role-switch/USB PHY bridge state, index, and typed per-port fields such as VBUS regulator, mode, fake USB3 port, saved USB3 tuning, and companion mapping. SoC-specific files extend this with private containers that embed `struct tegra_xusb_padctl`.

## Dependencies and Integration Points

The header depends on Linux IO, polling, mutex, workqueue, USB chapter 9, OTG, and role-switch definitions, with forward declarations for PHY, platform device, provider, and regulator types. It integrates all Tegra XUSB sources by providing the stable private ABI between `xusb.c` and SoC backends. It also defines the compatible SoC descriptor symbols that the common match table references.

## Risks and Edge Cases

- Because type-specific wrappers rely on `container_of()`, each typed object must embed the base structure exactly as expected.
- Ops are optional in many places; callers must test for null callbacks or return unsupported errors consistently.
- `padctl_readl_poll()` returns the `readl_poll_timeout()` error but is typed as `u32`, which can obscure negative error handling in callers.
- State is protected primarily by `padctl->lock`, but some fields are manipulated by generic PHY callbacks, role-switch work, and PM paths; lock ordering must stay consistent.
- Conditional externs mean build coverage depends on architecture config combinations.

## Test Signals

Header-level validation comes from all Tegra XUSB compile configurations, sparse/build warnings for struct declarations, Coccinelle or compiler checks around container casts, runtime tests for optional ops returning expected unsupported values, lockdep coverage for padctl lock usage, and probe/remove tests that exercise every release callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/Kconfig -->
# `sources/distributed-fs/ceph-client/drivers/phy/ti/Kconfig` Research

## Purpose

This Kconfig file declares build-time configuration symbols for Texas Instruments PHY drivers under `drivers/phy/ti`. It controls which TI USB, SERDES, PIPE3, ULPI, transceiver, and Ethernet PHY-selection drivers can be built, and records their architecture, subsystem, and helper-library dependencies.

## Important APIs, Types, and Functions

The file defines Kconfig symbols rather than C APIs. Important symbols include `PHY_DA8XX_USB`, `PHY_DM816X_USB`, `PHY_AM654_SERDES`, `PHY_J721E_WIZ`, `OMAP_CONTROL_PHY`, `OMAP_USB2`, `TI_PIPE3`, `PHY_TUSB1210`, `TWL4030_USB`, and `PHY_TI_GMII_SEL`. These symbols select or depend on generic PHY, USB PHY, MFD syscon, regmap, mux, MMIO mux, common clock, TWL4030, MUSB, OMAP, K3, and COMPILE_TEST infrastructure.

## Control Flow

Kconfig evaluation happens at kernel configuration time. Each entry exposes a tristate option when its dependencies are satisfiable. `select` statements pull in required helper subsystems, while `depends on` restricts visibility or buildability. Downstream, the TI PHY Makefile maps enabled symbols to object files. For example, enabling `OMAP_USB2` selects `GENERIC_PHY`, `USB_PHY`, and sometimes `OMAP_CONTROL_PHY`, then causes `phy-omap-usb2.o` to be built through the Makefile.

## State and Persistence

The persistent state is the generated kernel `.config`. Chosen tristate values (`y`, `m`, or unset) determine whether corresponding drivers are built-in, modules, or omitted. There is no runtime state in this file, but dependency choices persist across builds and affect module availability, init ordering, and link composition.

## Dependencies and Integration Points

This file integrates with the kernel Kconfig system, the TI PHY Makefile in the same directory, architecture symbols such as `ARCH_DAVINCI_DA8XX`, `ARCH_OMAP2PLUS`, and `ARCH_K3`, and subsystem symbols such as `USB_SUPPORT`, `COMMON_CLK`, `OF`, `OF_ADDRESS`, `HAS_IOMEM`, `USB_ULPI_BUS`, and `REGULATOR_TWL4030`. It also links TI PHY drivers with generic PHY and legacy USB PHY frameworks through `select`.

## Risks and Edge Cases

- `select` can force helper symbols on without their full dependency context; any helper with hidden prerequisites must be chosen carefully.
- `TWL4030_USB` has a specific `USB_GADGET || !USB_GADGET` condition to avoid built-in/module mismatch when gadget support is modular.
- `OMAP_USB2` selects `OMAP_CONTROL_PHY` only for OMAP/COMPILE_TEST, so K3 builds must not rely on OMAP control functions being present.
- COMPILE_TEST visibility increases build coverage but may expose missing include or dependency assumptions on non-native architectures.

## Test Signals

Test signals include `allyesconfig`/`allmodconfig` on supported TI architectures, `COMPILE_TEST` builds on non-TI architectures, Kconfig dependency warnings, module/built-in combinations for USB gadget and MUSB, and confirming each enabled symbol produces the matching object from the TI Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/Makefile -->
# `sources/distributed-fs/ceph-client/drivers/phy/ti/Makefile` Research

## Purpose

This Makefile maps TI PHY Kconfig symbols to the object files built under `drivers/phy/ti`. It is the build-system counterpart to `Kconfig`, ensuring each selected driver symbol contributes its implementation object to the kernel build.

## Important APIs, Types, and Functions

There are no C APIs. Each `obj-$(CONFIG_...) += ...` assignment is a build rule:

- `CONFIG_PHY_DA8XX_USB` -> `phy-da8xx-usb.o`
- `CONFIG_PHY_DM816X_USB` -> `phy-dm816x-usb.o`
- `CONFIG_OMAP_CONTROL_PHY` -> `phy-omap-control.o`
- `CONFIG_OMAP_USB2` -> `phy-omap-usb2.o`
- `CONFIG_TI_PIPE3` -> `phy-ti-pipe3.o`
- `CONFIG_PHY_TUSB1210` -> `phy-tusb1210.o`
- `CONFIG_TWL4030_USB` -> `phy-twl4030-usb.o`
- `CONFIG_PHY_AM654_SERDES` -> `phy-am654-serdes.o`
- `CONFIG_PHY_TI_GMII_SEL` -> `phy-gmii-sel.o`
- `CONFIG_PHY_J721E_WIZ` -> `phy-j721e-wiz.o`

## Control Flow

During kbuild evaluation, each `CONFIG_*` value expands to `y`, `m`, or empty. Built-in values add the object to the built-in list, module values add it to module builds, and unset values omit it. The ordering is straightforward and follows the file order; no composite multi-object modules are declared here.

## State and Persistence

The Makefile has no runtime state. Its behavior is determined entirely by the persisted kernel `.config` and the Kbuild object lists generated during the build. The source-to-object mapping is stable and source-tree-aligned with the driver filenames.

## Dependencies and Integration Points

The file integrates with the parent `drivers/phy` build, the TI PHY `Kconfig` symbols, and kbuild's `obj-y`/`obj-m` expansion. It assumes the corresponding `.c` files exist in the same directory and that Kconfig has already constrained dependency combinations.

## Risks and Edge Cases

- A mismatch between Kconfig symbol names and Makefile entries silently omits drivers or builds the wrong object.
- Adding a new TI PHY driver requires updating both Kconfig and this Makefile; doing only one leaves configuration or build coverage incomplete.
- Because every entry is a single object, any future multi-file driver would need composite object rules rather than a simple one-line mapping.

## Test Signals

Useful validation includes enabling each TI PHY config as built-in and module, checking `make drivers/phy/ti/` or full kernel builds, verifying no selected symbol lacks an object, and running `scripts/checkkconfigsymbols.py` or equivalent symbol-reference checks after edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/ti/Makefile -->
