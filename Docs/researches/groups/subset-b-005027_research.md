# subset-b-005027 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-torrent.c -->
# sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-torrent.c

## Purpose
This is the Cadence Torrent SD0801 PHY platform driver. It exposes a Generic PHY provider for a multi-lane, multi-protocol SerDes block used as DisplayPort, PCIe, SGMII, QSGMII, USB3, USXGMII, and XAUI. It also registers three output clocks for reference-clock routing: `refclk-driver`, `refclk-der`, and `refclk-rec`. The driver supports Cadence default hardware plus TI J721E and J7200 variants through different register-offset shifts and per-SoC register-value tables.

## Important APIs, types, and functions
The primary state is `struct cdns_torrent_phy`, which owns the MMIO bases, regmaps, reset controls, input clocks, reference-clock rates, lane instances, protocol bitmask, and variant `struct cdns_torrent_data`. Each child link is represented by `struct cdns_torrent_inst`, carrying master lane, protocol, lane count, link reset, and SSC mode. Static table types `cdns_reg_pairs`, `cdns_torrent_vals`, `cdns_torrent_vals_entry`, and `cdns_torrent_vals_table` encode hardware programming by `(refclk0, refclk1, link0, link1, ssc)` key.

The Generic PHY hooks are `cdns_torrent_phy_init()`, `cdns_torrent_dp_configure()`, `cdns_torrent_phy_on()`, and `cdns_torrent_phy_off()`. Probe and removal are handled by `cdns_torrent_phy_probe()` and `cdns_torrent_phy_remove()`. PM state is handled by `cdns_torrent_phy_suspend_noirq()` and `cdns_torrent_phy_resume_noirq()`. Custom regmap callbacks provide 16-bit CDB access and 32-bit DPTX access.

## Control flow
Probe obtains match data, allocates `cdns_torrent_phy`, maps the SD0801 register range, initializes lane/common/PCS/PMA regmaps, allocates regmap fields, registers the clock provider, gets resets and clocks, detects whether hardware is already configured, and enables the reference clocks and APB reset when it needs to program hardware. It then walks available child nodes named `phy`, reads `reg`, `cdns,phy-type`, `cdns,num-lanes`, optional `cdns,ssc-mode`, and DP-only `cdns,max-bit-rate`, creates one Generic PHY per link, and stores the per-link instance as PHY driver data. Multi-link configurations are programmed during probe before provider registration.

Single-link initialization selects register tables for the active protocol, reference clock, and SSC mode, writes link/common, PCS, PMA, TX-lane, and RX-lane values, then dispatches to DisplayPort-specific bring-up for DP. Multi-link initialization resolves one or two protocol classes, special-cases two PCIe links as `TYPE_PCIE_ML` for table selection, writes matching tables for each participating node, chooses the DP PLL when DP is present, deasserts link resets, and finally releases the global PHY reset.

DisplayPort initialization validates supported refclks, chooses PLL0/PLL1, initializes AUX, power state, lane reset, PLL parameters, and initial max-rate configuration, then waits for PMA common readiness and moves lanes through A2 to A0. Runtime DP configuration validates lane count, link rates, voltage swing, and pre-emphasis, then can reconfigure lanes, reprogram PLL rate, or update TX voltage coefficients.

## State and persistence behavior
The driver stores probed child-link topology, selected protocols, detected reference-clock rates, clock handles, and regmap fields in device-managed memory. Hardware state persists in PHY registers across runtime operations; `already_configured` detects preconfigured hardware and suppresses destructive reprogramming. Suspend saves the refclk-driver parent, asserts resets, and disables clocks unless it inherited an already-configured block; resume restores the parent, re-enables clocks and APB, and replays multi-link programming when needed.

## Dependencies and integration points
The driver integrates with platform devices, OF child nodes, reset controllers, common clock framework, Generic PHY, regmap, and Cadence/TI PHY dt-bindings. DP consumers use `phy_configure_opts_dp`; non-DP consumers rely mostly on init and power transitions. Register programming depends on large per-protocol tables selected by `of_device_id` data for `cdns,torrent-phy`, `ti,j721e-serdes-10g`, and `ti,j7200-serdes-10g`.

## Risks
The largest risk is table coverage: unsupported or missing key combinations silently skip some table groups because `NULL` table values are allowed, so bring-up depends on exact device-tree protocol/refclk/SSC combinations. Lane bounds are checked only through total lane count and per-DP lane validation; bad master-lane layout could still select unexpected regmap arrays if bindings permit overlapping lanes. DP rate changes rely on tight poll timeouts and PLL-ready bit semantics. Clock and reset cleanup in error paths is complex because child reset handles are manually put and clocks may or may not have been enabled depending on `already_configured`. Refclk mux state is saved only for the driver-owned clock provider.

## Test signals
Useful tests are DT binding coverage for all child-node combinations, boot/probe smoke tests for single and multi-link topologies, DP link training at all supported rates and lane counts, PCIe/USB/SGMII/USXGMII link bring-up on Cadence and TI variants, suspend/resume with and without preconfigured firmware state, and fault injection for missing clocks, resets, invalid max bit rates, unsupported lane counts, and PLL/readiness timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-torrent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/canaan/Kconfig

## Purpose
This Kconfig file introduces the Canaan PHY menu entry `PHY_CANAAN_USB`, a tristate option for the Kendryte K230 USB 2.0 PHY controller.

## Important APIs, types, and functions
The relevant symbol is `CONFIG_PHY_CANAAN_USB`. It depends on `(ARCH_CANAAN || COMPILE_TEST) && OF` and selects `GENERIC_PHY`, which ensures the driver can register a Generic PHY provider.

## Control flow
When enabled as built-in or module, the build system can compile `phy-k230-usb.o` through the sibling Makefile. The option is available on Canaan builds and for compile-test coverage.

## State and persistence behavior
Kconfig has no runtime state. Its persistent effect is the kernel configuration choice that determines whether the K230 USB PHY driver exists in the image.

## Dependencies and integration points
The symbol ties architecture support, device tree availability, and Generic PHY infrastructure to the Canaan platform driver.

## Risks
The option does not depend on `HAS_IOMEM`, even though the driver maps MMIO; most target builds provide it, but compile-test matrix coverage should catch missing include or API assumptions. The help text is specific to K230, so future Canaan USB PHY variants would need a broader symbol or new entry.

## Test signals
Configuration tests should cover built-in, module, disabled, `ARCH_CANAAN`, and `COMPILE_TEST` builds, then verify that `CONFIG_PHY_CANAAN_USB=m/y` causes `phy-k230-usb.o` to be selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/canaan/Makefile

## Purpose
This Makefile connects the Canaan USB PHY Kconfig symbol to the driver object.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_PHY_CANAAN_USB) += phy-k230-usb.o`.

## Control flow
Kbuild expands the rule when `CONFIG_PHY_CANAAN_USB` is `y` or `m`, building the object into the kernel or module.

## State and persistence behavior
There is no runtime state. The persistent artifact is the compiled object selected by the kernel configuration.

## Dependencies and integration points
It integrates with the parent PHY driver build and the `PHY_CANAAN_USB` Kconfig entry.

## Risks
Risk is low. A symbol rename or source filename change would break driver inclusion.

## Test signals
Run kernel build configuration checks to confirm the object is present for `CONFIG_PHY_CANAAN_USB=y` and module output exists for `CONFIG_PHY_CANAAN_USB=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/phy-k230-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/canaan/phy-k230-usb.c

## Purpose
This is the Canaan Kendryte K230 USB 2.0 PHY driver. It exposes two PHY instances backed by offsets inside a shared HiSysConfig system-controller MMIO resource and programs recommended analog tuning and pull-up/pull-down settings during power-on.

## Important APIs, types, and functions
`struct k230_usb_phy_global` owns the mapped base and the two `struct k230_usb_phy_instance` entries. Each instance records test/control offsets and an index. `k230_usb_phy_power_on()` writes `K230_PHY_CTL0_VAL` and `K230_PHY_CTL1_VAL`, then adjusts `TEST_CTL3`; `k230_usb_phy_power_off()` clears DM/DP pull-down bits. `k230_usb_phy_xlate()` uses the first phandle argument to select one of the two PHYs. `k230_usb_phy_probe()` maps registers, creates both PHYs, and registers the OF PHY provider.

## Control flow
Probe allocates global state, maps resource 0, initializes static offset pairs for USB0 and USB1, creates two device-managed PHY objects, attaches instance data, and registers a provider with a custom xlate callback. Consumers pass an index in the PHY phandle. On power-on, the driver writes fixed PLL, threshold, impedance, pre-emphasis, VBUS, and OTG tuning values to the instance control registers, sets ID pull-up, and sets DM/DP pull-down only for instance 1. Power-off clears DM/DP pull-downs but leaves other tuning fields untouched.

## State and persistence behavior
Runtime software state is only the mapped base and per-instance offsets. Hardware state persists in HiSysConfig registers after power-on; power-off partially unwinds pull-down state but does not clear ID pull-up or restore control registers. There is no clock, reset, runtime PM, or suspend/resume handling in this driver.

## Dependencies and integration points
The driver depends on platform MMIO, device tree compatible `canaan,k230-usb-phy`, Generic PHY, and bitfield helpers. It is configured by `CONFIG_PHY_CANAAN_USB`.

## Risks
The xlate path assumes `args->args[0]` is present; malformed bindings with zero arguments could read beyond valid phandle argument data. Fixed tuning values and asymmetric pull-down behavior are hard-coded and have no DT override. Lack of reset/clock handling means integration depends on firmware or another driver to make the system-controller block accessible. Power-off does not fully restore power-on changes.

## Test signals
Test both PHY indexes through DT phandles, invalid index handling, USB host/device enumeration on both ports, repeated power-on/off cycles checking `TEST_CTL3`, and compile-test coverage for 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/canaan/phy-k230-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/eswin/Kconfig

## Purpose
This Kconfig file declares `PHY_EIC7700_SATA`, the ESWIN EIC7700 SATA SerDes/PHY driver option.

## Important APIs, types, and functions
The symbol is tristate, depends on `ARCH_ESWIN || COMPILE_TEST`, depends on `HAS_IOMEM`, and selects `GENERIC_PHY`.

## Control flow
When enabled, Kbuild can compile the EIC7700 SATA PHY object through the sibling Makefile. The help text describes support for one SATA host port at 1.5, 3.0, and 6.0 Gb/s.

## State and persistence behavior
Kconfig has no runtime state. It persistently controls whether the driver is built.

## Dependencies and integration points
The symbol links ESWIN architecture support, compile-test coverage, MMIO availability, and Generic PHY support.

## Risks
The entry does not select or depend on `REGMAP_MMIO`, `RESET_CONTROLLER`, or clock framework symbols directly; those are normally present through common kernel dependencies but should remain covered by build testing.

## Test signals
Exercise `y`, `m`, and disabled builds for ESWIN and compile-test configurations, verifying object selection and dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/eswin/Makefile

## Purpose
This Makefile connects the EIC7700 SATA PHY Kconfig symbol to its driver object.

## Important APIs, types, and functions
The rule is `obj-$(CONFIG_PHY_EIC7700_SATA) += phy-eic7700-sata.o`.

## Control flow
Kbuild includes the object when the symbol is built-in or modular.

## State and persistence behavior
There is no runtime state. The build output is controlled by the persisted kernel configuration.

## Dependencies and integration points
It integrates the ESWIN PHY subdirectory with the kernel PHY build and `PHY_EIC7700_SATA`.

## Risks
Risk is low and limited to symbol or filename drift.

## Test signals
Verify object inclusion for `CONFIG_PHY_EIC7700_SATA=y` and module generation for `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/phy-eic7700-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/eswin/phy-eic7700-sata.c

## Purpose
This platform driver exposes the ESWIN EIC7700 SATA PHY as a single Generic PHY. It programs reference clock routing, transmit amplitude/pre-emphasis tuning, loss-of-signal detection, AXI low-power request bits, and MPLL multiplier before releasing reset and waiting for PHY readiness.

## Important APIs, types, and functions
`struct eic7700_sata_phy` stores tuning arrays, reset control, regmap, clock, and PHY handle. `wait_for_phy_ready()` wraps `regmap_read_poll_timeout()`. `eic7700_sata_phy_init()` enables the PHY clock, writes all required control registers, deasserts reset, and polls `SATA_P0_PHY_STAT`. `eic7700_sata_phy_exit()` asserts reset and disables the clock. `eic7700_get_tuning_param()` reads optional DT arrays and falls back to default per-generation values. Probe maps MMIO with `devm_ioremap()` and creates a regmap manually because the resource overlaps a clock/reset region already owned by another driver.

## Control flow
Probe allocates state, obtains the memory resource, maps it without claiming exclusivity, initializes a 32-bit regmap, reads tuning properties `eswin,tx-amplitude-tuning` and `eswin,tx-preemph-tuning`, gets clock `phy`, gets an exclusive reset-control array, creates one PHY, stores driver data, and registers an OF simple PHY provider. Init enables the clock, writes static and DT-driven register values, waits briefly, deasserts reset, and requires `SATA_P0_PHY_READY` to become set. Exit reverses reset and clock state.

## State and persistence behavior
The tuning arrays are persistent driver state loaded once at probe. Hardware register settings persist until reinitialized or reset. Failed readiness after reset disables the clock but does not explicitly reassert reset, leaving reset state dependent on the previous deassert call and reset-controller behavior.

## Dependencies and integration points
The driver depends on Generic PHY, regmap-mmio, clocks, reset controls, platform resources, and compatible `eswin,eic7700-sata-phy`. It intentionally shares an address region with the EIC7700 HSP clock/reset driver.

## Risks
DT tuning arrays are not range-checked against their target bitfield widths, so oversized property values will be truncated by `FIELD_PREP` behavior or trigger build/runtime assertions depending on configuration. The overlapping resource mapping is intentional but fragile if the ownership model changes. The ready timeout is short, so slow hardware or clock sequencing issues can fail init. Error handling after ready failure disables the clock but does not restore all programmed state.

## Test signals
Test default and DT-supplied tuning values, SATA Gen1/Gen2/Gen3 link training, reset/clock failure paths, readiness timeout injection, repeated init/exit cycles, and coexistence with the HSP clock/reset driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/eswin/phy-eic7700-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/Kconfig

## Purpose
This Kconfig file declares Freescale/NXP PHY options for i.MX and Layerscape platforms, including the two drivers in this work item: `PHY_MIXEL_MIPI_DPHY` and `PHY_FSL_IMX8M_PCIE`.

## Important APIs, types, and functions
Inside the `(ARCH_MXC && ARM64) || COMPILE_TEST` block, `PHY_MIXEL_MIPI_DPHY` selects `GENERIC_PHY`, `GENERIC_PHY_MIPI_DPHY`, and `REGMAP_MMIO`; `PHY_FSL_IMX8M_PCIE` selects `GENERIC_PHY` and depends on `OF && HAS_IOMEM`. The file also declares adjacent symbols for i.MX8MQ USB, Mixel LVDS, i.MX8QM HSIO, Samsung HDMI PHY, and Layerscape Lynx 28G.

## Control flow
Enabled symbols are consumed by the Freescale PHY Makefile to include the matching object files. The architecture guard limits most i.MX-specific entries to ARM64 i.MX or compile-test builds.

## State and persistence behavior
There is no runtime state. The file persistently controls which PHY drivers are built and which PHY framework dependencies are selected.

## Dependencies and integration points
It integrates NXP PHY drivers with Generic PHY, MIPI D-PHY helpers, regmap-mmio, device tree, and architecture gating.

## Risks
The Mixel MIPI D-PHY driver uses firmware IPC for combo LVDS mode but the Kconfig entry does not make that dependency obvious; missing firmware support would show as build or probe failures depending on broader config. The architecture guard prevents accidental exposure on non-target builds except compile-test.

## Test signals
Config builds should cover `PHY_MIXEL_MIPI_DPHY` and `PHY_FSL_IMX8M_PCIE` as `y` and `m`, with compile-test enabled, and confirm required framework symbols are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/Makefile

## Purpose
This Makefile maps Freescale/NXP PHY Kconfig symbols to object files.

## Important APIs, types, and functions
The relevant rules for this work item are `obj-$(CONFIG_PHY_MIXEL_MIPI_DPHY) += phy-fsl-imx8-mipi-dphy.o` and `obj-$(CONFIG_PHY_FSL_IMX8M_PCIE) += phy-fsl-imx8m-pcie.o`. Other rules cover i.MX8MQ USB, Mixel LVDS, i.MX8QM HSIO, Layerscape Lynx 28G, and Samsung HDMI PHY.

## Control flow
Kbuild includes each object according to its corresponding Kconfig symbol.

## State and persistence behavior
There is no runtime state; build output follows persisted kernel configuration.

## Dependencies and integration points
It integrates the Freescale PHY source files into the kernel PHY build.

## Risks
Risk is low. Symbol or filename drift would omit the target driver from builds.

## Test signals
Build matrix checks should verify object inclusion for the relevant `y` and `m` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8-mipi-dphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8-mipi-dphy.c

## Purpose
This driver exposes the NXP/Mixel i.MX8 MIPI D-PHY, and for i.MX8QXP combo hardware also supports LVDS mode. It converts Generic PHY MIPI D-PHY and LVDS configuration options into PLL dividers, high-speed timing registers, LVDS syscon bits, and optional SCU firmware controls.

## Important APIs, types, and functions
`struct mixel_dphy_priv` stores current `mixel_dphy_cfg`, DPHY and LVDS regmaps, reference clock, device data, SCU IPC handle, slave flag, and alias id. `mixel_dphy_config_from_opts()` validates MIPI rates and computes `cm`, `cn`, `co`, HS prepare/zero/trail, and settle values. `mixel_dphy_configure_mipi_dphy()` writes MIPI timing and PLL registers. `mixel_dphy_configure_lvds_phy()` configures LVDS pads, MODE8, divider, and reference clock rate. `mixel_dphy_power_on()` enables the ref clock and dispatches to MIPI or LVDS lock sequencing. `mixel_dphy_set_mode()` validates mode against combo versus non-combo hardware and programs SCU mode for combo parts.

## Control flow
Probe matches either `fsl,imx8mq-mipi-dphy` or `fsl,imx8qxp-mipi-dphy`, maps the DPHY register region, creates an 8-bit-address/32-bit-value regmap, obtains `phy_ref`, and for combo hardware also looks up `fsl,syscon`, obtains an alias id, and gets an SCU IPC handle. It then creates one PHY and registers a simple provider. Consumers call `set_mode()`, `validate()`, `configure()`, `init()`, and power operations through Generic PHY. MIPI configure computes and stores timing state, writes calibration/test registers, writes timing fields, and writes PLL parameters. LVDS configure sets LVDS pads, selects slave mode if requested, checks VCO range, writes the CO divider, and sets the reference clock rate.

## State and persistence behavior
`priv->cfg` persists the most recent MIPI PLL/timing calculation and is consumed by later power-on. `priv->is_slave` persists the LVDS slave role and suppresses lock polling for slave LVDS. Hardware power state is controlled by active-low `DPHY_PD_PLL` and `DPHY_PD_DPHY`; exit clears PLL divider registers. Clock enable state is paired in power-on/off, while mode state may also persist in SCU firmware controls for combo hardware.

## Dependencies and integration points
The driver depends on Generic PHY, Generic MIPI D-PHY configure options, LVDS configure options, regmap-mmio, common clock framework, syscon, and i.MX SCU firmware IPC for combo mode. It uses device-tree compatible data to distinguish i.MX8MQ MIPI-only and i.MX8QXP combo behavior.

## Risks
The MIPI ratio calculation uses continued fractions and integer scaling; boundary rates and unusual reference clocks need close testing. `mixel_dphy_config_from_opts()` calls `clk_get_rate()` but does not explicitly reject a zero reference clock before using it as a denominator. Combo mode depends on alias ids and SCU controls; wrong aliases can address the wrong MIPI resource. LVDS `clk_set_rate()` return value is ignored. Power-on requires prior mode/configuration, but the driver mostly trusts Generic PHY consumer ordering.

## Test signals
Test MIPI validation at 80 Mbps and 1.5 Gbps boundaries, common DSI pixel-clock derived rates, PLL lock timeout injection, LVDS 24 to 150 MHz differential clock range, master/slave LVDS mode, SCU IPC failure paths, mode rejection on non-combo hardware, and suspend/resume paths driven by consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8-mipi-dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8m-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8m-pcie.c

## Purpose
This driver exposes the i.MX8M PCIe PHY as a Generic PHY for i.MX8MM and i.MX8MP variants. It configures reference-clock pad direction/source, AUX and power GPR bits, optional TX de-emphasis tuning, resets, and PLL readiness polling.

## Important APIs, types, and functions
`struct imx8_pcie_phy` stores MMIO base, reference clock, PHY handle, IOMUXC GPR regmap, reset controls, DT properties, and variant data. `imx8_pcie_phy_power_on()` sequences resets and register programming, then polls `IMX8MM_PCIE_PHY_CMN_REG075` for `ANA_PLL_DONE`. `imx8_pcie_phy_power_off()` asserts resets. `imx8_pcie_phy_init()` and `imx8_pcie_phy_exit()` enable and disable the reference clock. Probe reads optional DT properties, obtains clocks, GPR syscon, resets, maps MMIO, creates the PHY, and registers an OF provider.

## Control flow
Probe selects variant data from `fsl,imx8mm-pcie-phy` or `fsl,imx8mp-pcie-phy`, reads `fsl,refclk-pad-mode`, optional `fsl,tx-deemph-gen1`, optional `fsl,tx-deemph-gen2`, and `fsl,clkreq-unsupported`, gets clock `ref`, looks up the variant-specific IOMUXC GPR compatible, obtains reset `pciephy`, obtains reset `perst` only for i.MX8MP, maps registers, creates one PHY, and registers a simple provider. Init enables the ref clock. Power-on asserts PHY reset, applies i.MX8MM de-emphasis when present, configures refclk pad input/output/internal PLL, updates GPR AUX/power/SSC/refclk bits, deasserts PERST and PHY reset, asserts common reset through GPR, and polls for PLL done. Power-off asserts PHY reset and PERST.

## State and persistence behavior
DT-derived pad mode, de-emphasis values, and CLKREQ behavior persist in driver state. Hardware state persists in PHY MMIO and IOMUXC GPR registers until power-off or a later power-on rewrites them. Clock state is controlled by init/exit, not power-on/off. On i.MX8MM, `perst` is never acquired but `power_on()` and `power_off()` still call `reset_control_deassert/assert(imx8_phy->perst)`, relying on NULL reset-control behavior.

## Dependencies and integration points
The driver depends on Generic PHY, common clock framework, reset controller, syscon regmap lookup by compatible, i.MX IOMUXC GPR definitions, and dt-bindings for i.MX8 PCIe refclk pad modes.

## Risks
`fsl,refclk-pad-mode` defaults to zero if absent, so binding defaults must match hardware expectations. Return values from several reset-control and MMIO writes are not checked. The PERST reset is mandatory only for i.MX8MP, so NULL handling on i.MX8MM must remain valid. PLL polling compares the full register value with `ANA_PLL_DONE`, which is fragile if other status bits become set. Clock enable is separate from power sequencing, so consumers must call init before power-on.

## Test signals
Test internal, input, output, and unused refclk pad modes; i.MX8MM and i.MX8MP reset paths; optional de-emphasis values; CLKREQ unsupported handling; PLL timeout injection; repeated init/power_on/power_off/exit cycles; and PCIe enumeration after warm reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8m-pcie.c -->
