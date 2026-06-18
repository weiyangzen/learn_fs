# subset-b-005025 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-dphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-dphy.c

Purpose: Implements the digital MIPI DSI D-PHY block for Amlogic Meson AXG. It bridges the generic PHY MIPI-DPHY interface to AXG DSI control registers and coordinates with a separate analog PHY instance.

Important APIs and types: `struct phy_meson_axg_mipi_dphy_priv` stores the MMIO regmap, `pclk`, reset, analog PHY, and last `phy_configure_opts_mipi_dphy`. `phy_meson_axg_mipi_dphy_configure()` validates MIPI timing with `phy_mipi_dphy_config_validate()`, forwards the same options to the analog PHY, and caches them. The `phy_ops` implement `.init`, `.exit`, `.configure`, `.power_on`, and `.power_off`.

Control flow: probe maps the DSI PHY register window, creates an 8-bit/32-bit regmap, gets `pclk`, reset `phy`, and named `analog`, then enables the clock and deasserts reset before registering a simple OF PHY provider. Init initializes the analog PHY and resets the digital block. Power-on powers the analog side first, enables DSI clocking, calculates byte-clock timing from `hs_clk_rate`, programs clock/HS/LP/init/wakeup/watchdog timing registers, powers the selected number of data lanes, and syncs `txclkesc`. Power-off powers down all lanes, asserts soft reset, then powers off analog.

State and persistence: The driver persists only runtime configuration in `priv->config`; hardware state lives in DSI registers and the companion analog PHY. There is no suspend/resume or NVM state. Dependencies include `clk`, reset controller, generic PHY, regmap MMIO, and the MIPI-DPHY timing helpers.

Integration points: It is matched by `amlogic,axg-mipi-dphy` and is consumed by DSI/display drivers through the generic PHY framework. The named `analog` PHY links it to the AXG MIPI/PCIe analog provider.

Risks and test signals: Timing conversion depends on a valid nonzero `hs_clk_rate` and integer rounding of picosecond periods. Probe enables `pclk` without a remove-time disable path because it relies on devm lifetime and permanent PHY availability. Test with 1-4 lane DSI modes, invalid MIPI timing, analog PHY probe deferral, power-cycle ordering, and scope-visible LP/HS timing after mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-pcie-analog.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-pcie-analog.c

Purpose: Provides the shared AXG analog PHY controls used by MIPI DSI and PCIe-related analog circuitry through the HHI syscon register block.

Important APIs and types: `struct phy_axg_mipi_pcie_analog_priv` stores the HHI regmap, current MIPI-DPHY configuration, and booleans for configured, enabled, and powered state. Helper routines split bandgap control from DSI lane analog setup: `phy_bandgap_enable()`, `phy_bandgap_disable()`, `phy_dsi_analog_enable()`, and `phy_dsi_analog_disable()`.

Control flow: probe obtains the parent syscon regmap, creates one simple PHY, and registers `of_phy_simple_xlate`. Configure validates and caches MIPI-DPHY options; if the analog block is already powered it disables any active DSI analog setup, waits briefly, and re-enables with the new lane mask. Power-on enables bandgap and, when configured, enables the DSI analog lanes. Power-off disables bandgap and tears down DSI analog state.

State and persistence: The driver keeps only software booleans and a cached config. HHI registers hold the actual analog programming. There is no locking, so callers are expected to serialize generic PHY operations.

Dependencies and integration: It depends on parent-node `syscon`, regmap update/write helpers, and generic PHY MIPI config validation. It integrates with `phy-meson-axg-mipi-dphy.c` as the named `analog` PHY and may also be relevant to PCIe PHY setup on AXG.

Risks and test signals: Lane mask construction assumes validated lane counts from 1 to 4, but invalid cached lane values would disable all lanes. Reconfiguration while powered is explicitly handled, but concurrent configure/power calls would be unsafe. Test DSI lane-count changes, power-on before configure, configure after power-on, syscon probe deferral, and cleanup of HHI_MIPI_CNTL registers on power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-mipi-pcie-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-pcie.c

Purpose: Implements the AXG PCIe PHY wrapper that programs a small digital control register, coordinates reset, and delegates analog power/init to a named analog PHY.

Important APIs and types: `struct phy_axg_pcie_priv` holds the MMIO regmap, reset array, generic PHY object, and companion analog PHY. The exported behavior is through `phy_axg_pcie_ops`: `.init`, `.exit`, `.power_on`, `.power_off`, and `.reset`.

Control flow: probe maps `MESON_PCIE_REG0`, creates a regmap, gets an exclusive reset array and named `analog`, creates the PHY, and registers a simple provider. Init initializes analog, writes the common reference-clock/two-x1 setup value, then resets the digital block. Power-on powers the analog PHY and clears `MESON_PCIE_POWERDOWN`; power-off powers analog down and sets powerdown. Reset first resets analog, then asserts/deasserts the reset line with 500 us delays.

State and persistence: There is no mutable software state beyond resource pointers. Hardware state is fully reprogrammed by init/power/reset callbacks and reset controller state.

Dependencies and integration: It depends on the generic PHY core, reset arrays, regmap MMIO, and `dt-bindings/phy/phy.h`. Device tree must provide `amlogic,axg-pcie-phy`, reset resources, and an `analog` PHY reference. PCIe host drivers consume it through phandles.

Risks and test signals: Error handling returns immediately on analog failures, so PCIe bring-up should verify probe deferral and rollback through consumer retries. The static `MESON_PCIE_TWO_X1` setup assumes a two x1 topology. Test reset sequencing, analog failure propagation, power-off idempotence, and PCIe enumeration after cold boot and warm reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-axg-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-mipi-dphy-analog.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-mipi-dphy-analog.c

Purpose: Controls the G12A MIPI DSI analog D-PHY registers in the parent HHI syscon block. It supplies analog lane enables and bias/reference programming for a separate digital DSI PHY user.

Important APIs and types: `struct phy_g12a_mipi_dphy_analog_priv` stores the PHY, HHI regmap, and cached `phy_configure_opts_mipi_dphy`. `phy_g12a_mipi_dphy_analog_configure()` validates and stores MIPI options. Power callbacks write three HHI MIPI control registers.

Control flow: probe gets the parent HHI syscon regmap, creates a simple PHY, and registers it as an OF provider for `amlogic,g12a-mipi-dphy-analog`. Power-on writes reference, bandgap, and differential TX constants, then builds the enabled-channel mask from the configured lane count. Power-off clears all three HHI registers.

State and persistence: Only the cached MIPI config persists in software. Hardware state is direct register programming and is not restored by a PM callback.

Dependencies and integration: It uses regmap syscon access, generic PHY, MIPI-DPHY validation, and `dt-bindings/phy/phy.h`. It integrates as an analog provider for G12A-family MIPI DSI display paths.

Risks and test signals: Unlike the AXG analog driver, this file does not track whether configure ran before power-on; an uninitialized lane count would produce only the clock-lane default path. Test with display pipeline configure-before-power ordering, 1-4 lane panels, power-off register clearing, invalid lane counts, and parent syscon probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-mipi-dphy-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb2.c

Purpose: Initializes and tears down the USB2 PHY found on Meson G12A and A1 SoCs, including PLL setup, analog tuning, calibration bypass, and UTMI bus width declaration.

Important APIs and types: `enum meson_soc_id` selects G12A versus A1 tuning. `struct phy_meson_g12a_usb2_priv` stores device, regmap, xtal clock, reset, and SoC id. The `phy_ops` implement `.init` and `.exit`; mode selection is intentionally left to the UTMI bus.

Control flow: probe maps the PHY register block, records match data, creates a regmap, gets `xtal` and reset `phy`, deasserts reset, creates a generic PHY, sets bus width to 8, and registers the provider. Init enables the clock, resets the PHY, programs MPLL registers for 24 MHz to 480 MHz, applies SoC-specific analog and calibration values, tunes VBUS, disconnect threshold, and PMA update signals. Exit resets the PHY and disables the clock when reset succeeds.

State and persistence: The driver persists no dynamic link state; all hardware programming is redone on init. SoC variant data is immutable match state.

Dependencies and integration: It depends on clock/reset/regmap/generic PHY infrastructure and device-tree compatible strings `amlogic,g12a-usb2-phy` and `amlogic,a1-usb2-phy`. USB host/device controller glue consumes the PHY and handles mode externally.

Risks and test signals: PLL and analog constants are hardware-specific and not validated at runtime. A reset failure during exit leaves the clock enabled. Test G12A and A1 match data, clock enable failure rollback, PLL lock behavior on hardware, repeated init/exit, and USB high-speed enumeration with disconnect/attach threshold sensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb3-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb3-pcie.c

Purpose: Drives the G12A combo PHY that can operate as either USB3 or PCIe. It programs top-level combo registers and exposes a secondary CR bus as a regmap for detailed USB3 analog workaround writes.

Important APIs and types: `struct phy_g12a_usb3_pcie_priv` holds top-level and CR regmaps, reference clock, reset array, PHY, and selected mode. `phy_g12a_usb3_pcie_xlate()` selects `PHY_TYPE_USB3` or `PHY_TYPE_PCIE` from the phandle argument. CR bus read/write helpers implement the PHY's acknowledge-based address/data handshake.

Control flow: probe maps the top registers, creates both MMIO and custom CR regmaps, gets `ref_clk` enabled and reset array, creates a PHY, and registers a custom xlate provider. USB3 init resets the PHY, switches the combo to USB3, applies CR-bus workarounds for TX alt bus, RX equalization, TX amplitude/preemphasis, MPLL loop control, and top-level VBOOST/LOS fields. PCIe power-on/off changes the PCIe power-state field, and PCIe reset toggles the reset array with 500 us delays. USB3 exit resets the block.

State and persistence: The selected `mode` is stored globally in the provider instance at xlate time, so one hardware block is treated as a single-mode resource. Hardware state is not saved across PM.

Dependencies and integration: It depends on generic PHY, reset, enabled reference clock, regmap custom bus callbacks, and `dt-bindings/phy/phy.h`. Device-tree consumers must pass the desired PHY type.

Risks and test signals: Because `mode` is overwritten by each xlate call, simultaneous USB3 and PCIe consumers would race logically. CR-bus polling timeouts are critical failure signals. Test both phandle modes, invalid xlate args, USB3 SuperSpeed enumeration after workaround programming, PCIe reset/power states, and bootloader-preconfigured PCIe noted by the TODO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb3-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-gxl-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-gxl-usb2.c

Purpose: Provides the Meson GXL/GXM USB2 PHY implementation, including host/device/OTG mode pin control, clock/reset management, and runtime PHY reset.

Important APIs and types: `struct phy_meson_gxl_usb2_priv` tracks regmap, current `enum phy_mode`, enable flag, optional clock, and optional shared reset. `phy_ops` expose init, exit, power on/off, set_mode, and reset.

Control flow: probe maps U2P registers, defaults mode to host, creates the regmap, gets optional resources, creates the PHY, and registers a simple provider. Init resets the optional reset line and enables the optional clock, rearming reset on clock failure. Power-on clears `POWER_ON_RESET`, marks enabled, and reapplies the current mode. `set_mode()` programs DM/DP pulldowns and ID pullup for host/OTG versus device, then triggers a PHY reset if enabled. Power-off sets reset and clears enabled. Exit disables the clock and rearms reset.

State and persistence: The last requested mode persists in `priv->mode` while powered off, allowing `power_on` to apply it. `is_enabled` guards reset side effects. No nonvolatile state exists.

Dependencies and integration: It integrates with USB controller PHY consumers through generic PHY mode APIs and matches `amlogic,meson-gxl-usb2-phy`. It uses regmap MMIO, optional shared reset, and optional `phy` clock.

Risks and test signals: Unsupported modes return `-EINVAL` and power-on rolls back to reset. Test host/device/OTG mode switches before and after power-on, optional clock/reset absence, repeated reset calls, and USB role switching with line-state/pullup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-gxl-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8-hdmi-tx.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8-hdmi-tx.c

Purpose: Controls the Meson8/Meson8b/Meson8m2 HDMI transmitter PHY through HHI syscon registers and a TMDS clock.

Important APIs and types: `struct phy_meson8_hdmi_tx_priv` holds the HHI regmap and TMDS clock. The `phy_ops` provide init/exit for clock enable and power_on/power_off for HDMI PHY register programming.

Control flow: probe verifies a memory resource exists, obtains the parent syscon regmap, gets the TMDS clock, creates the PHY, and registers a simple provider. Init enables the TMDS clock. Power-on selects one of two vendor-derived `HDMI_CTL0` constants based on whether TMDS rate is at least 2.97 GHz, writes CTL0/CTL1, then performs the vendor-style three-cycle soft reset with 1-2 ms sleeps. Power-off writes a low-power CTL0 value.

State and persistence: There is no software state beyond resource pointers. PHY programming depends on the current TMDS clock rate at power-on.

Dependencies and integration: It depends on the parent HHI syscon node, generic PHY, and clock framework. It matches `amlogic,meson8-hdmi-tx-phy` for display/HDMI controller consumers.

Risks and test signals: Magic constants are derived from BSP behavior and have limited documentation. Test low and high TMDS rates, repeated power cycles, clock enable/disable balance, parent syscon failures, and HDMI link stability after the triple-reset sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8-hdmi-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8b-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8b-usb2.c

Purpose: Implements USB2 PHY power sequencing for Meson8, Meson8b, Meson8m2, and GXBB, including USB clocks, optional shared reset, host/device role information, and ACA-based host ID detection for later variants.

Important APIs and types: `struct phy_meson8b_usb2_priv` stores regmap, `usb_dr_mode`, two clocks, optional reset, and match data. `struct phy_meson8b_usb2_match_data` selects whether host mode should enable ACA. The `phy_ops` implement power-on and power-off.

Control flow: probe maps registers, reads match data, gets `usb_general` and `usb` clocks, optional reset, and controller dual-role mode via `of_usb_get_dr_mode_by_phy()`, then creates a simple PHY. Power-on triggers reset, enables both clocks with rollback, selects 32 kHz/ref/FSEL settings, pulses power-on reset, enables SOF toggle, and in host mode clears IDDQ. If ACA is enabled it turns on ACA detection and fails when the ID pin floats. Power-off restores host IDDQ, disables clocks, rearms reset, and asserts power-on reset.

State and persistence: The role and variant are static after probe. Hardware is reinitialized each power-on; no runtime mode mutation is implemented.

Dependencies and integration: It depends on USB OF role parsing, clock/reset/regmap/generic PHY frameworks, and compatible-specific match data.

Risks and test signals: Missing role configuration is fatal. ACA failure disables clocks and re-arms reset but leaves an error path that should be verified for balanced resources. Test all compatible match data, host/device role behavior, ACA floating-pin detection, clock failure rollback, and USB enumeration after repeated power cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8b-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/apple/Kconfig

Purpose: Adds the Kconfig entry for the Apple Type-C PHY driver.

Important APIs and types: Defines `CONFIG_PHY_APPLE_ATC` as a tristate named "Apple Type-C PHY". It depends on Apple ARM64 platforms or compatible compile-test conditions, and on `TYPEC`. It selects `GENERIC_PHY` and `APPLE_TUNABLE`.

Control flow and integration: Enabling this symbol allows the `phy-apple-atc` module to be built and provides support for Apple Silicon Type-C PHY hardware used for USB2, USB3, USB4, Thunderbolt, and DisplayPort.

State and persistence: Kconfig carries build-time state only. It does not encode runtime policy.

Dependencies: The dependency set captures the driver use of Type-C switch/mux APIs, generic PHY APIs, and firmware-provided Apple tunables. The compile-test clause excludes `GENERIC_ATOMIC64`, matching broader ARM64/atomic constraints in kernel build coverage.

Risks and test signals: Build coverage should include built-in, module, disabled, ARCH_APPLE, and COMPILE_TEST configurations. Because the implementation also registers reset-controller and Type-C mux/switch devices, config tests should verify transitive dependencies are sufficient for both module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/apple/Makefile

Purpose: Connects the Apple PHY Kconfig symbol to its object file.

Important APIs and types: `obj-$(CONFIG_PHY_APPLE_ATC) += phy-apple-atc.o` adds the driver object when selected. `phy-apple-atc-y := atc.o` builds that composite object from `atc.c`.

Control flow and integration: Kernel build recursion in `drivers/phy/apple` uses this Makefile to produce the final built-in or module artifact named by Kconfig help as `phy-apple-atc`.

State and persistence: This file has no runtime state; it only controls build graph membership.

Dependencies: It depends on `CONFIG_PHY_APPLE_ATC` from the sibling Kconfig and the presence of `atc.c`.

Risks and test signals: Build tests should verify module name generation, `M=drivers/phy/apple` partial builds, and that future source splits add to `phy-apple-atc-y` rather than replacing the composite target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/atc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/apple/atc.c

Purpose: Implements the Apple Silicon Type-C PHY used for USB2, USB3, USB4/Thunderbolt, and DisplayPort. It also provides the reset controller for the attached DWC3 controller and Type-C orientation/mux callbacks.

Important APIs and types: `struct apple_atcphy` is the central state object: mapped register windows, tunables, current mode, lane swap flag, DP link rate, pipehandler state, three generic PHYs, reset controller, Type-C switch/mux, and mutex. Mode data is encoded in `atcphy_modes[]`, while `dp_lr_config[]` stores DisplayPort PLL/link-rate programming. Public kernel integration is via generic PHY ops for USB2/USB3/DP, Type-C switch/mux ops, and reset-controller ops.

Control flow: probe maps named resources (`core`, `lpdptx`, `axi2af`, `usb2phy`, `pipehandler`), parses firmware tunables, forces DWC3 reset, powers USB2 and ATCPHY down, initializes the pipehandler to dummy mode, then registers reset, mux, switch, and PHY provider interfaces. Type-C mux selection maps safe/USB/USB4/TBT/DP states to internal modes. `atcphy_configure()` powers up, applies tunables, programs common overrides, optionally enables DP AUX, enables CIO3 clocks, configures lane modes/crossbar, and releases PHY reset. USB3 set-mode brings the pipehandler to USB3 after the mux has selected a compatible mode. DP configure maps link rates 1620/2700/5400/8100 to AUSPLL and lane programming.

State and persistence: `mode`, `swap_lanes`, `dp_link_rate`, and `pipehandler_up` persist in memory and gate idempotence. Hardware calibration/tuning comes from firmware-provided `apple,tunable-*` properties; without those high-speed modes are not expected to work. A mutex serializes PHY, mux, switch, and reset-controller register access.

Dependencies and integration: It depends on Type-C mux/switch/altmode definitions, USB PD/EUDO fields, generic PHY DP/USB modes, Apple tunable parsing, reset-controller framework, and reverse-engineered MMIO sequences. It matches `apple,t8103-atcphy`.

Risks and test signals: High-risk areas are undocumented magic sequences, pipehandler locking/unlocking, USB4 pipehandler fallback to USB2, Type-C orientation changes versus active modes, DP link-rate reconfiguration, and reset interactions with DWC3. Test USB2 host/device mode, USB3 host/device pipehandler setup, safe-state teardown, DP pin assignments C/D/E, DP link rates including unsupported values, Thunderbolt/USB4 mux selection, orientation reversal, missing tunables/resources, and reset assert while USB3 pipehandler is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/apple/atc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/Kconfig

Purpose: Defines Broadcom PHY driver build options for USB, PCIe, SATA, and STB platform PHY implementations.

Important APIs and types: The menu includes `PHY_BCM63XX_USBH`, `PHY_CYGNUS_PCIE`, `PHY_BCM_SR_USB`, `BCM_KONA_USB2_PHY`, `PHY_BCM_NS_USB2`, `PHY_BCM_NS_USB3`, `PHY_NS2_PCIE`, `PHY_NS2_USB_DRD`, `PHY_BRCM_SATA`, `PHY_BRCM_USB`, and `PHY_BCM_SR_PCIE`. Most select `GENERIC_PHY`; some additionally depend on `PHYLIB`, `EXTCON`, `MFD_SYSCON`, or `SOC_BRCMSTB`.

Control flow and integration: These symbols control which platform or MDIO drivers are built for Broadcom families such as Cygnus, Kona, Northstar, Northstar2, Stingray, BCM63xx, BRCMSTB, BCMBCA, and iProc.

State and persistence: This file has only build-time state. Defaults are tied to relevant architecture symbols where appropriate.

Dependencies: The dependency expressions encode required bus/framework support: OF, MDIO mux/PHYLIB, HAS_IOMEM, architecture families, and compile-test escape hatches.

Risks and test signals: Build matrices should cover every symbol as module and built-in, compile-test paths, and transitive dependency correctness. `PHY_BRCM_USB` is especially coupled to multiple object files and optional SoC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/Makefile

Purpose: Maps Broadcom PHY Kconfig symbols to their compiled objects.

Important APIs and types: Each `obj-$(CONFIG_...)` line adds a driver object. `CONFIG_PHY_BRCM_USB` builds the composite `phy-brcm-usb-dvr.o` from `phy-brcm-usb.o`, `phy-brcm-usb-init.o`, and `phy-brcm-usb-init-synopsys.o`.

Control flow and integration: The Makefile is the build graph for the Broadcom PHY subtree. It links platform, MDIO, and composite STB USB support into the kernel or modules according to Kconfig.

State and persistence: Build-only; no runtime behavior.

Dependencies: It depends on Kconfig symbols from the sibling file and corresponding C sources. Composite object ordering matters for shared init-operation symbols.

Risks and test signals: Test all Broadcom PHY symbols in module and built-in configurations, especially that `phy-brcm-usb-dvr` resolves helper symbols across the three source files and that removed/renamed sources do not leave stale object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-cygnus-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-cygnus-pcie.c

Purpose: Provides generic PHY power control for up to two Broadcom Cygnus PCIe PHYs sharing one configuration register.

Important APIs and types: `enum cygnus_pcie_phy_id` names PCIe0/PCIe1. `struct cygnus_pcie_phy_core` owns the shared base, mutex, and two child PHY records. `cygnus_pcie_power_config()` toggles per-PHY IDDQ bits and is wrapped by power-on/off `phy_ops`.

Control flow: probe requires child nodes, maps the shared register block, initializes a mutex, iterates available child nodes, reads each `reg` id, rejects invalid or duplicate ids, creates a child PHY, and registers a simple OF provider. Power-on clears the relevant IDDQ bit and waits 50 ms for SerDes stabilization. Power-off sets the bit.

State and persistence: Software state is the child id/core mapping. Hardware state is the IDDQ bit in the shared PCIe config register. The mutex serializes read-modify-write access for both PHYs.

Dependencies and integration: It depends on OF child-node binding, generic PHY, MMIO, and platform driver matching `brcm,cygnus-pcie-phy`. PCIe host nodes consume child PHY phandles.

Risks and test signals: Invalid or duplicated child `reg` properties abort probe. Test both PHY ids, concurrent power operations, missing child nodes, invalid ids, and PCIe link training after the 50 ms analog stabilization delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-cygnus-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-kona-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-kona-usb2.c

Purpose: Implements the Broadcom Kona USB2 PHY with minimal OTG and port-control register sequencing.

Important APIs and types: `struct bcm_kona_usb` stores the mapped register base. `bcm_kona_usb_phy_init()` performs a soft reset through `P1CTL`; power-on/off call `bcm_kona_usb_phy_power()` to set or clear OTG reset bits and line-state fields.

Control flow: probe maps the MMIO resource, creates a generic PHY, sets an 8-bit UTMI bus width, associates driver data, and registers a simple provider. Init toggles `P1CTL_SOFT_RESET` with a 2 ms assertion delay. Power-on clears OTG status/line-state bits and sets PRST/HRESET; power-off clears the reset release bits.

State and persistence: There is no mutable software state beyond the mapped register pointer. The PHY is reinitialized by direct register writes.

Dependencies and integration: It depends on generic PHY and MMIO platform resources, matching `brcm,kona-usb2-phy`. USB controllers consume the PHY provider and bus-width metadata.

Risks and test signals: The reset sequence uses fixed timing and assumes register semantics from older Kona hardware. Test init/power ordering, UTMI 8-bit consumers, repeated power cycles, missing MMIO resource, and USB high-speed attach after soft reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-kona-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb2.c

Purpose: Programs the Broadcom Northstar USB2 PHY PLL divider based on the reference clock.

Important APIs and types: `struct bcm_ns_usb2` stores device, reference clock, PHY, clkset syscon regmap, and base control register. The only PHY operation is `.init`.

Control flow: probe maps the control register, looks up `brcm,syscon-clkset`, gets `phy-ref-clk`, creates the PHY, and registers a simple provider. Init enables the reference clock, reads its rate, derives PLL NDIV for a 1.92 GHz USB2 PLL target using the existing or default PDIV, unlocks DMU PLL settings with `0x0000ea68`, updates the NDIV field, relocks with zero, and disables the reference clock.

State and persistence: Software does not retain state. Hardware persists the computed PLL divider in the DMU USB2 control register until reprogrammed or reset.

Dependencies and integration: It depends on the clock framework, syscon regmap, BCMA DMU bit definitions, generic PHY, and `brcm,ns-usb2-phy` binding.

Risks and test signals: A zero reference clock rate returns `-EINVAL`. The divider math assumes integer division is acceptable for all supported ref clocks. Test with supported clock rates, clkset syscon failure, clock prepare failure, and USB2 link behavior after PLL relock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb3.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb3.c

Purpose: Initializes Broadcom Northstar USB3 PHYs over MDIO, with separate register sequences for AX and BX families plus a DMP reset register.

Important APIs and types: `enum bcm_ns_family` selects AX or BX. `struct bcm_ns_usb3` stores device, family, DMP reset mapping, MDIO device, and generic PHY. `bcm_ns_usb3_mdio_phy_write()` wraps MDIO writes. PHY `.init` performs reset and family-specific programming.

Control flow: the MDIO probe allocates state, records family match data, maps the `usb3-dmp-syscon` resource, creates a PHY, and registers a provider. Init asserts USB3 system soft reset, then AX or BX sequences select MDIO block pages, program PLL/PIPE/TX PMD values, enable SSC, and deassert DMP reset. BX additionally configures LFPS comparator and deglitch values.

State and persistence: Family is immutable match state; hardware programming persists in MDIO-addressed PHY registers and the DMP reset register.

Dependencies and integration: It is an MDIO driver, not a platform driver. It depends on PHYLIB/MDIO, OF resource parsing, BCMA reset definitions, and generic PHY. Compatible strings distinguish `brcm,ns-ax-usb3-phy` and `brcm,ns-bx-usb3-phy`.

Risks and test signals: MDIO write failures are only checked for the initial block select in family init functions; later writes are fire-and-forget. Test MDIO bus errors, both families, DMP mapping failure, USB3 reset deassertion, SSC behavior, and SuperSpeed enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-pcie.c

Purpose: Provides a small MDIO-backed Northstar2 PCIe PHY initializer for the 100 MHz AFE block.

Important APIs and types: The driver stores the `mdio_device` directly as PHY driver data. `ns2_pci_phy_init()` selects MDIO block `PLL_AFE1_100MHZ_BLK` and writes `PLL_CLK_AMP_2P05V` to the clock amplitude register.

Control flow: MDIO probe creates one generic PHY attached to the MDIO OF node, stores the MDIO device as driver data, and registers a simple provider from the PHY device. Init performs the two MDIO writes and logs the failing return code if either fails.

State and persistence: No software state beyond the MDIO pointer. Hardware retains the selected block/amplitude programming.

Dependencies and integration: It depends on OF MDIO, MDIO device access, generic PHY, and compatible `brcm,ns2-pcie-phy`. PCIe host drivers consume the PHY before link setup.

Risks and test signals: Because block select is global to the MDIO PHY page, other users must not race register-page selection. Test MDIO write errors, provider registration, PCIe link stability at 100 MHz reference, and repeated init calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-usbdrd.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-usbdrd.c

Purpose: Implements Northstar2 USB2 dual-role-device PHY support, including host/device mode register programming, extcon state publication, GPIO-based ID/VBUS detection, and PLL lock polling.

Important APIs and types: `struct ns2_phy_driver` owns mapped control windows, GPIOs, IRQs, extcon device, delayed work, and shared `ns2_phy_data`. `ns2_phy_data` stores the PHY and pending state (`EVT_HOST` or `EVT_DEVICE`). PHY ops implement `.init`, `.power_on`, and `.power_off`.

Control flow: probe maps `icfg`, `rst-ctrl`, `crmu-ctrl`, and `usb2-strap`, gets `id` and `vbus` GPIOs, allocates/registers extcon, configures debounce or delayed-work fallback, requests both edge-triggered IRQs, shuts down ports, creates the PHY, registers the provider, and queues initial detection. IRQs schedule `extcon_work()`, which reads GPIOs, updates extcon cable states, sets `new_state`, and calls `connect_change()` to switch mode registers. Power-on uses `new_state` to configure host or device P0CTL, resets, CRMU bits, PLL reset bits, and overcurrent polarity.

State and persistence: Runtime role is persisted in `data->new_state` and extcon state. Hardware role state is in ICFG/CRMU/strap registers. Delayed work is the debounce mechanism.

Dependencies and integration: It depends on GPIO descriptors, extcon, delayed workqueues, generic PHY, MMIO resources, and compatible `brcm,ns2-drd-phy`.

Risks and test signals: Probe uses managed resources but does not explicitly cancel delayed work on remove in this file. GPIO state combinations drive role decisions; disconnected state does not reset `new_state`. Test ID/VBUS transitions, debounce fallback, both IRQ paths, host/device power-on, PLL lock timeout, disconnect behavior, and extcon notifications to USB role consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns2-usbdrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-pcie.c

Purpose: Exposes Stingray PCIe PHY handles and gates host-controller use according to the hardware PIPEMUX strap; also validates the special PAXC PHY power state.

Important APIs and types: `struct sr_pcie_phy_core` stores PCIe SS base, CDRU and MHB syscon regmaps, detected `pipemux`, and nine PHY records. `pipemux_table[]` maps strap settings to root-complex-enabled core bitmaps. Separate `phy_ops` handle regular PAXB cores and the PAXC core.

Control flow: probe maps the PCIe SS block, looks up `brcm,sr-cdru` and `brcm,sr-mhb`, reads PIPEMUX config or hardware strap, validates it, creates nine PHYs, and registers a custom xlate that returns `args[0]`. Regular PHY init returns success only when the core bit is enabled for root complex in the strap table. PAXC init checks MHB power status bits.

State and persistence: The detected PIPEMUX value is immutable after probe. Hardware strap and MHB power state are external platform state; the driver does not change them.

Dependencies and integration: It depends on syscon regmaps, generic PHY, OF phandle args, and platform compatible `brcm,sr-pcie-phy`. PCIe host drivers use PHY init failure to skip unavailable cores.

Risks and test signals: Strap-table correctness defines which controllers enumerate. `WARN_ON` catches out-of-range xlate args. Test all valid strap values, invalid strap rejection, PAXC powered/unpowered cases, xlate index bounds, and PCIe host behavior when init returns `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-usb.c

Purpose: Initializes Broadcom Stingray USB high-speed and SuperSpeed PHYs, including combo PHY instances with separate HS and SS generic PHY handles.

Important APIs and types: `enum bcm_usb_phy_version` distinguishes combo versus HS-only hardware. `struct bcm_usb_phy_cfg` stores type, version, MMIO base, PHY pointer, and register offset table. `bcm_usb_phy_create()` builds either two PHYs for combo hardware or one HS PHY.

Control flow: probe maps the register block, reads compatible match data, creates PHY objects, stores the config as driver data, and registers a custom xlate. SS init programs PHY PCTL, clears suspend, starts PLL sequencing, releases PLL reset, waits 30 ms, then polls PLL lock. HS init toggles PLL reset and polls lock. Reset toggles CORERDY for HS PHYs.

State and persistence: Version/type/offset tables are static after probe. Hardware PLL and PHY control bits persist until reset or power management elsewhere.

Dependencies and integration: It depends on generic PHY, OF phandle args, MMIO, and polling helpers. Compatible strings are `brcm,sr-usb-combo-phy` and `brcm,sr-usb-hs-phy`.

Risks and test signals: Combo xlate supports only indexes 0 and 1. PLL lock polling is the main runtime failure. Test HS-only and combo bindings, invalid xlate index, HS reset, SS PLL lock timeout, and USB host enumeration for both PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm63xx-usbh.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm63xx-usbh.c

Purpose: Implements BCM63xx USBH PHY control across several SoC variants with differing register maps, PLL bits, endian swap settings, and device-mode selectors.

Important APIs and types: `struct bcm63xx_usbh_phy_variant` describes per-SoC register offsets and bit masks. `struct bcm63xx_usbh_phy` stores mapped base, optional clocks, reset, selected variant, and a `device_mode` flag set by phandle translation. PHY ops implement init, exit, power_on, and power_off.

Control flow: probe selects variant match data, maps MMIO, gets exclusive reset and optional `usbh`/`usb_ref` clocks, creates one PHY, and registers a custom xlate. Xlate stores whether the consumer requested device mode. Init enables clocks, resets the block, configures native CPU endian swap bits, setup polarity bits, USB simulation control, optional magic test-port value, and UTMI device-mode bits. Power-on/off set or clear per-variant PLL control masks. Exit disables both clocks.

State and persistence: `device_mode` persists from the most recent xlate call, so the single PHY provider is configured according to its consumer argument. Variant data is static. Hardware register programming is re-applied during init.

Dependencies and integration: It depends on optional clocks, reset controller, generic PHY, raw MMIO access, and compatibles for BCM6318/6328/6358/6362/6368/63268.

Risks and test signals: There is a likely typo in the `USBH_PLLC_CLKSEL_MASK` definition using its own mask in the shift expression, though that field is not used in this file. Single stored `device_mode` would be unsafe for multiple consumers with conflicting args. Test each variant register map, host/device xlate args, optional clock absence, reset/clock rollback, PLL power bits, and endian behavior on MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm63xx-usbh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-sata.c

Purpose: Provides Broadcom SATA PHY initialization for STB 16/28/40 nm, iProc NS2/NSP/Stingray, and DSL 28 nm variants, with optional spread-spectrum clocking, receive equalization, and TX amplitude tuning.

Important APIs and types: `struct brcm_sata_phy` owns common MMIO bases, version, and up to two `brcm_sata_port` entries. Each port stores `ssc_en`, `rxaeq_mode`, `rxaeq_val`, and `tx_amplitude_val` from child DT properties. Register helpers select PCB banks and account for 28 nm versus 40 nm per-port spacing.

Control flow: probe requires child port nodes, maps the `phy` resource and optionally `phy-ctrl` for NS2, selects version from compatible, creates one PHY per child `reg`, reads port tuning properties, and registers a simple provider. Init dispatches by version: STB variants set SSC/TX frequency and RX AEQ, 16 nm applies detailed CDR/PPM/TX amplitude settings, NS2/NSP/SR/DSL program OOB/PLL registers and poll PLL lock. Calibrate is supported only on STB 28/40 nm and enables RX frequency monitor correction.

State and persistence: Per-port DT tuning persists in memory. Hardware state is banked PHY register programming and optional NS2 PHY-control reset pulses.

Dependencies and integration: It depends on generic PHY, platform resources named `phy` and sometimes `phy-ctrl`, OF child nodes, and compatible-specific variant selection. AHCI/SATA controllers consume child PHYs.

Risks and test signals: Many values are characterized magic constants; PLL lock timeout is the main hard failure. Manual RX AEQ validates only the value range. Test each compatible, both port ids, duplicate/invalid child regs, SSC on/off, manual/auto/off RX AEQ, TX amplitude values 400/500/600/800/default, PLL timeout paths, and calibrate support returning `-EOPNOTSUPP` on unsupported variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-sata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init-synopsys.c -->
# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init-synopsys.c

Purpose: Supplies Broadcom STB Synopsys USB initialization callbacks for newer controllers such as BCM7216, BCM7211 B0, and BCM74110. It is part of the composite `phy-brcm-usb-dvr` driver and fills `brcm_usb_init_ops`.

Important APIs and types: It consumes `struct brcm_usb_init_params` and installs one of `bcm74110_ops`, `bcm7216_ops`, or `bcm7211b0_ops` through `brcm_usb_dvr_init_74110()`, `brcm_usb_dvr_init_7216()`, and `brcm_usb_dvr_init_7211b0()`. Helpers cover IPP/IOC polarity, common init/uninit, XHCI soft reset, dual-select get/set, 7211b0 MDIO writes, and wake-enable programming.

Control flow: `usb_init_ipp()` optionally overrides strap-selected power polarity and waits when polarity changes. Common init programs port mode, BDC reset behavior, and chip-specific PHY power/PLL details. 7211b0 powers up USB PHY LDO/bandgap, waits up to 200 ms for PLL lock, sets PHY mode, adjusts BDC read transaction size, disables the power-up FSM, and applies a USB2 eye fix through MDIO. 7216 toggles USB power, disables suspend clock switching, optionally forces COMMONONN, and disables wake. 74110 extends 7216 with S2 clock changes and USB2 tune values. Uninit either enables wake/PME paths or powers down/reset PHY and XHCI depending on `wake_enabled`.

State and persistence: The file mutates only hardware registers and fields inside the caller-owned init params (`family_name`, `ops`). Wake behavior depends on `params->wake_enabled`, and selected port mode is stored in controller registers.

Dependencies and integration: It depends on `phy-brcm-usb-init.h` register helpers, BRCMSTB SoC definitions, optional `syscon_piarbctl`, and mapped register slots for CTRL, XHCI global, USB PHY, USB MDIO, and BDC EC blocks.

Risks and test signals: MDIO helper loops busy-wait without timeout on GMDIO busy. 7211b0 PLL lock timeout is polled but common init continues after the loop without returning status. Test init/uninit with and without wake, host/device/DRD port modes, IPP/IOC polarity changes, 7211b0 PLL and MDIO behavior, 7216/74110 suspend-clock settings, XHCI reset sequencing, and dual-select sysfs or role-control users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init-synopsys.c -->
