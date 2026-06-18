# Research: subset-b-005033

This grouped report covers the requested Qualcomm PHY source subset under `sources/distributed-fs/ceph-client/drivers/phy/qualcomm/`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31-eusb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31-eusb2.c

## Purpose
This driver implements a Qualcomm M31 eUSB2 high-speed PHY for the SM8750 binding `qcom,sm8750-m31-eusb2-phy`. It exposes a generic PHY provider, sequences regulators, a reference clock, reset, and MMIO register programming, and also delegates mode/init/exit work to a downstream repeater PHY obtained from the device tree.

## Important APIs, Types, and Functions
The core data model is `struct m31eusb2_phy`, which stores the generic `struct phy`, MMIO base, match data, regulator bulk array, clock, reset, and repeater PHY. `struct m31_eusb2_priv_data` points at three register tables: setup, override, and reset sequences. `m31eusb2_phy_write_readback()` masks and writes an individual register field, then verifies the write by reading it back. `m31eusb2_phy_write_sequence()` applies table entries with left-shifted field values based on `__ffs(mask)`. PHY ops are `m31eusb2_phy_init()`, `m31eusb2_phy_exit()`, and `m31eusb2_phy_set_mode()`.

## Control Flow
Probe allocates driver state, reads match data, maps MMIO resource 0, gets an exclusive reset, a clock, two regulators (`vdd`, `vdda12`), creates the PHY, obtains the repeater via `devm_of_phy_get_by_index()`, then registers `of_phy_simple_xlate`. Init enables regulators, initializes the repeater, enables the ref clock, asserts/deasserts the PHY reset, writes setup registers, programs `FSEL` for 38.4 MHz, applies override tuning, and finally applies the reset-release sequence. Exit disables the clock, regulators, and repeater. Mode changes are cached locally and forwarded to the repeater through `phy_set_mode_ext()`.

## State and Persistence
Runtime state is in the devm-managed `m31eusb2_phy` object and in hardware registers. The only remembered software mode is `phy->mode`, with no persistence across reprobe or suspend. The table-driven register writes define power-on hardware state; shutdown only disables resources and exits the repeater, so register retention depends on platform power/reset behavior.

## Dependencies and Integration Points
The driver depends on the Linux PHY, platform, reset, clock, regulator, MMIO, bitfield, and device-tree match-data APIs. Its integration contract is the DT compatible string, MMIO resource, one unnamed reset, one unnamed clock, `vdd` and `vdda12` supplies, and a child or referenced repeater PHY at index 0. It is part of the Qualcomm PHY driver set but does not reuse the QMP table helper.

## Risks and Edge Cases
`m31eusb2_phy_init()` ignores return values from the three table-write calls and the direct `FSEL` write; write/readback failures therefore do not currently abort init. The error path after `phy_init(repeater)` returns `0` after disabling regulators, masking clock-enable or repeater-init failures in some branches. Register values are tightly coupled to SM8750 M31 eUSB2 hardware and to the 38.4 MHz FSEL assumption. Repeater failures are user-visible because mode changes and init/exit are forwarded.

## Test Signals
Useful test signals are successful probe with all resources present, regulator/clock/reset sequencing visible in boot logs, no write/readback error messages during init, successful repeater init/exit, and working USB high-speed enumeration through the eUSB2 path. Negative tests should cover missing supplies, missing repeater, failed clock enable, and bad register readback if fault injection is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31-eusb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31.c

## Purpose
This is a Qualcomm M31 USB2 high-speed PHY driver for IPQ-family SoCs. It supports `qcom,ipq5018-usb-hsphy` and `qcom,ipq5332-usb-hsphy`, powering and programming a UTMI/HS PHY through table-driven MMIO sequences.

## Important APIs, Types, and Functions
`struct m31_phy_regs` describes a register offset, value, and optional microsecond delay. `struct m31_priv_data` selects the per-compatible sequence and optional ULPI mode. `struct m31usb_phy` stores the generic PHY, mapped base, selected table, regulator, clock, reset, and ULPI flag. The main callbacks are `m31usb_phy_init()` as `.power_on` and `m31usb_phy_shutdown()` as `.power_off`.

## Control Flow
Probe maps resource 0, gets reset index 0, gets the unnamed clock, reads match data, creates the PHY, gets the `vdd` regulator, stores driver data, and registers a simple PHY provider. Power-on enables the regulator and clock, pulses reset, optionally clears `USB2PHY_PORT_UTMI_CTRL2` for ULPI mode, powers up the PHY, and writes every entry in the selected register table, honoring per-entry delays. Power-off writes `POWER_DOWN`, disables the clock, and disables the regulator.

## State and Persistence
All persistent configuration is static match data. The driver keeps no dynamic link state and has no runtime PM state. Hardware register state is established on each power-on and may be lost whenever `vdd`, reset, or platform power domains are cycled.

## Dependencies and Integration Points
It integrates with device tree via `of_device_get_match_data()`, uses `devm_platform_ioremap_resource()`, a single reset, a single clock, and a `vdd` regulator. It exports a generic PHY for USB controller consumers. The register tables tune clock selection, POR, suspend, TX enable, slew, impedance, current, and pre-emphasis values for the supported IPQ SoCs.

## Risks and Edge Cases
The table writes are blind `writel()` calls with no readback or timeout; bad register definitions only surface as functional failures. The `of_device_get_match_data()` result is dereferenced without an explicit null check, relying on a successful match. ULPI support is present in the data model but both current match entries set it false. Power-on failure after clock enable correctly disables the regulator only in the clock-failure path; later register-write failures are not represented because writes do not return errors.

## Test Signals
Probe should fail cleanly when reset, clock, or `vdd` is absent. Positive tests are USB2 enumeration on IPQ5018/IPQ5332, visible clock/regulator enable ordering, and no reset-time instability. Hardware validation should include suspend/resume and signal-quality checks because many table values are analog tuning constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-m31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-pcie2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-pcie2.c

## Purpose
This legacy Qualcomm PCIe2 PHY driver provides a generic PHY and fixed-rate pipe clock for controllers using the `qcom,pcie2-phy` binding. It programs PARF/PCS registers for refclock selection, TX amplitude/de-emphasis, RX equalization, reset release, and pipe clock enablement.

## Important APIs, Types, and Functions
`struct qcom_phy` holds the device, MMIO base, two regulators (`vdda-vp`, `vdda-vph`), resets (`phy`, `pipe`), and pipe clock. `qcom_pcie2_phy_init()` deasserts the PHY reset and enables regulators. `qcom_pcie2_phy_power_on()` performs the analog/PCS programming sequence and polls `PCIE20_PARF_PHY_STTS`. `qcom_pcie2_phy_power_off()` asserts software reset and disables the pipe clock/reset. `phy_pipe_clksrc_register()` registers a 250 MHz fixed-rate pipe clock source using `clock-output-names`.

## Control Flow
Probe allocates state, maps resource 0, registers the pipe clock source, gets the two regulators, gets the unnamed pipe clock, gets the named `phy` and `pipe` resets, creates the PHY, and registers a simple provider. Init deasserts `phy_reset`, then enables regulators. Power-on programs refclock control bits, asserts PHY software reset, writes swing/de-emphasis/EQ/termination values, disables loopback, deasserts software reset, deasserts pipe reset, sets and enables the pipe clock at 250 MHz, then polls until the status bit clears. Power-off reverses the pipe side and reasserts software reset; exit disables regulators and asserts `phy_reset`.

## State and Persistence
The driver has no dynamic software state beyond resource handles. Hardware programming happens on every power-on. The fixed clock provider persists for the life of the device and is consumed by GCC/PCIe clock topology.

## Dependencies and Integration Points
It depends on Linux PHY, reset, regulator, platform MMIO, iopoll, and clock-provider APIs. The device tree must provide MMIO, `clock-output-names`, two regulators, an unnamed pipe clock, and named resets. The PCIe controller consumes the PHY and pipe clock through DT.

## Risks and Edge Cases
`readl_poll_timeout(..., 1000, 10)` uses a 10 microsecond timeout with a 1000 microsecond sleep interval, which is unusual and may be too short or misleading. If `clk_prepare_enable(pipe_clk)` fails after pipe reset deassertion, the code returns without reasserting `pipe_reset`. The init error message says "pipe reset" when deasserting `phy_reset`. Register magic values are hard-coded and not SoC-specific beyond the single compatible string.

## Test Signals
Expected signals include pipe clock provider registration, successful regulator/reset sequencing, status polling completion, and PCIe link training. Negative tests should exercise missing `clock-output-names`, missing supplies/resets, pipe clock enable failure, and timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-pcie2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-combo.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-combo.c

## Purpose
This large driver implements Qualcomm QMP combo PHY blocks that expose both USB3/USB4-style SuperSpeed and DisplayPort PHYs from shared hardware. It supports many SoCs, including Glymur, SAR2130P, SC7180, SC7280, SC8180X, SC8280XP, SDM845, SM6350, SM8150, SM8250, SM8350, SM8450, SM8550, SM8650, SM8750, and X1E80100. It handles shared common-block power/reset, USB PHY sequencing, DP link-rate and voltage programming, Type-C orientation/mode switching, DP AUX bridge registration, runtime PM, and clock providers.

## Important APIs, Types, and Functions
The central types are `struct qmp_phy_cfg`, `struct qmp_combo_offsets`, and `struct qmp_combo`. `qmp_phy_cfg` binds each compatible to register layouts, init tables, DP link-rate tables, DP swing/pre-emphasis matrices, callbacks, reset names, regulators, and quirks such as `has_pwrdn_delay` and `invert_cc_polarity`. `qmp_combo` stores mapped regions for USB, DP, common, PCS, PCS_USB, PCS_MISC, AON, Type-C state, init counters, generic PHYs, clocks, resets, and regulator handles.

Important control helpers include `qmp_combo_com_init()` and `qmp_combo_com_exit()` for shared resource sequencing, `qmp_combo_usb_init()/exit()` and `qmp_combo_usb_power_on()/off()` for USB, and `qmp_combo_dp_init()/exit()/power_on()/power_off()/configure()/calibrate()` for DP. DP-specific helpers include `qmp_combo_dp_serdes_init()`, `qmp_combo_configure_dp_swing()`, `qmp_combo_configure_dp_mode()`, versioned AUX setup, versioned clock setup, and versioned PHY bring-up. Type-C integration is in `qmp_combo_typec_switch_set()` and `qmp_combo_typec_mux_set()`.

## Control Flow
Probe loads match data, initializes reset/regulator resources, parses either legacy child-node bindings or a newer single-MMIO binding with offset tables, determines default mode/orientation from Type-C switches or OF graph `data-lanes`, registers the DRM AUX bridge, enables runtime PM but forbids it by default, registers USB pipe and DP link/pixel clock providers, creates USB and DP PHYs, and registers the PHY provider.

The shared init path enables regulators, asserts and deasserts resets, enables bulk clocks, powers the common block, overrides hardware reset control, programs Type-C port select and polarity, selects USB3/DP/both mode, releases the relevant soft resets, and powers up the USB PCS. USB init calls the common init, configures USB serdes/TX/RX/PCS tables, enables the pipe clock, starts PCS/SerDes, and polls `PHYSTATUS`. DP init calls the common init and versioned AUX setup. DP power-on configures DP SerDes by link rate, writes DP TX tables on lane 1 and lane 2, applies swing/pre-emphasis, configures link clocks and DP PHY state, polls ready/status bits, and marks DP powered. Type-C mux changes can force common-block reinitialization and USB/DP power resequencing if mode or orientation changes.

## State and Persistence
The driver maintains shared `init_count` plus `usb_init_count`, `dp_init_count`, `dp_powered_on`, current `qmpphy_mode`, `orientation`, USB `phy_mode`, AUX calibration index, and latest `phy_configure_opts_dp`. These are devm-managed runtime state only. Hardware state is derived from static tables and the current Type-C/DP configuration. Runtime suspend enables USB autonomous mode, drops pipe and bulk clocks, and runtime resume restores clocks and disables autonomous mode.

## Dependencies and Integration Points
It depends on the Linux PHY, platform, MMIO, iopoll, clock-provider, reset, regulator, OF graph, Type-C switch/mux, Type-C DP altmode, PM runtime, and DRM AUX bridge APIs. It includes many QMP register header files for PCS, PCS_USB, PCS_MISC, AON, DP COM, DP PHY, and USB43 PCS definitions. Consumers are USB controllers, DisplayPort/display controllers, Type-C mux/switch providers, and clock consumers for USB pipe, DP link, and DP VCO-div clocks.

## Risks and Edge Cases
Most behavior is table- and compatible-driven; incorrect offsets, register layout selection, or lane mapping can break either USB or DP. `qmp_combo_dp_power_on()` ignores return values from `qmp_combo_dp_serdes_init()` and `cfg->configure_dp_phy()`, so unsupported link rates or DP bring-up timeouts may not propagate correctly. Type-C mux changes deliberately delay switching away from DP while DP is powered, which avoids disruption but can surprise callers expecting immediate mode changes. Shared `init_count` sequencing is critical because USB and DP use the same common block. Runtime PM assumes the PHY has been initialized and uses autonomous mode bits that differ across PCS/PCS_USB/AON generations. The V8 DP header aliases `AUXLESS_SETUP_CYC` and `AUXLESS_SILENCE_CYC` to the same offset, so V8 timing writes need hardware confirmation.

## Test Signals
Strong signals include probe on both legacy and offset-based DT bindings, correct creation of two PHYs and three clocks, USB SuperSpeed enumeration, DP AUX transactions, DP link training at RBR/HBR/HBR2/HBR3, Type-C normal/reverse orientation tests, USB-only/DP-only/USB+DP mode changes, runtime suspend/resume with wake detection, and timeout/error logging during failed PHY start. Hardware validation should include signal integrity across supported link rates because the swing/pre-emphasis matrices and per-SoC tables are analog tuning data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-combo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-common.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-common.h

## Purpose
This header provides the common register-initialization table format and helper functions used by Qualcomm QMP PHY drivers. It standardizes table-driven MMIO programming and optional per-lane filtering.

## Important APIs, Types, and Functions
`struct qmp_phy_init_tbl` contains a register offset, value, debug name, and lane mask. `QMP_PHY_INIT_CFG()` creates an entry for all lanes, while `QMP_PHY_INIT_CFG_LANE()` restricts an entry to a specific lane mask. `qmp_configure_lane()` writes entries whose `lane_mask` intersects the requested mask. `qmp_configure()` applies a table to all lanes by passing mask `0xff`.

## Control Flow
Drivers define static arrays of `qmp_phy_init_tbl` entries. During init, they pass the target MMIO base and table length to `qmp_configure()` or `qmp_configure_lane()`. The helper skips null tables, emits a debug log per write, and writes the value directly with `writel()`.

## State and Persistence
The header has no state. Persistence is entirely in the caller's static tables and in hardware registers after writes.

## Dependencies and Integration Points
It requires `struct device`, MMIO accessors, and debug logging from the kernel environment. It is included by QMP combo and PCIe drivers and depends on register offsets from other QMP headers.

## Risks and Edge Cases
There is no readback, masking, delay, or error return. Callers must ensure register offsets are valid for the selected hardware revision, table lengths are correct, and lane masks match the target lane numbering. Because values are full-register writes, tables must avoid unintentionally clobbering preserved bits.

## Test Signals
Debug logs can confirm register ordering and lane-mask filtering. Functional tests depend on the parent PHY drivers: successful PLL lock, PCS ready, USB/DP/PCIe link training, and no hardware timeout after applying tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-com-v3.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-com-v3.h

## Purpose
This header defines DP COM block offsets for QMP v3 and v4 combo PHY common-control registers. The combo driver uses these offsets to reset, power, switch Type-C polarity, and choose USB/DP operating modes.

## Important APIs, Types, and Functions
It exports preprocessor constants for `QPHY_V3_DP_COM_PHY_MODE_CTRL`, `SW_RESET`, `POWER_DOWN_CTRL`, `SWI_CTRL`, `TYPEC_CTRL`, `TYPEC_PWRDN_CTRL`, and `RESET_OVRD_CTRL`. There are no functions or data structures.

## Control Flow
The constants are consumed by `phy-qcom-qmp-combo.c`, especially in common init/exit and Type-C switching paths. Writes to these offsets establish software reset overrides, common power state, selected PHY mode, and Type-C lane orientation.

## State and Persistence
The header has no state. It names hardware registers whose values persist according to the PHY common-block power/reset domain.

## Dependencies and Integration Points
It is integrated by inclusion in QMP DP combo code and is specific to QMP v3/v4-style DP COM register layouts. It complements bit definitions local to the combo driver, such as `USB3_MODE`, `DP_MODE`, and reset override bits.

## Risks and Edge Cases
Using these offsets with an incompatible QMP generation can misprogram common reset or Type-C control registers. Since offsets are plain constants, version selection must be enforced by the including driver's compatible-specific config.

## Test Signals
Signals include successful common-block bring-up, correct Type-C orientation behavior, and successful USB/DP mode selection on v3/v4-based platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-com-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v2.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v2.h

## Purpose
This header defines QMP v2 DisplayPort PHY register offsets for AUX interrupt handling, AUX BIST, VCO division, lane control, spare register, and status.

## Important APIs, Types, and Functions
It exports `QSERDES_V2_DP_PHY_AUX_INTERRUPT_MASK`, `AUX_INTERRUPT_CLEAR`, `AUX_BIST_CFG`, `VCO_DIV`, `TX0_TX1_LANE_CTL`, `TX2_TX3_LANE_CTL`, `SPARE0`, and `STATUS`. There are no functions.

## Control Flow
Including drivers use these constants when programming DP AUX behavior, lane enable/control state, link-rate VCO division, and status polling. This specific subset is only offsets; sequencing lives in the driver.

## State and Persistence
The header has no software state. Hardware state is in the DP PHY registers that these offsets name.

## Dependencies and Integration Points
It is a generation-specific register map companion to QMP DP PHY code. It should be paired only with QMP v2 DP PHY layouts and compatible-specific config that knows how to use these offsets.

## Risks and Edge Cases
The file contains a commented line beginning with `// /*`, which is harmless in C99-style kernel code but stylistically odd. Misapplying v2 offsets to v3+ hardware would affect AUX, VCO, lane, and status registers incorrectly.

## Test Signals
Useful signals are correct AUX interrupt masking/clearing, valid VCO division for supported link rates, lane enable behavior, and expected DP PHY status bits during link bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v3.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v3.h

## Purpose
This header defines QMP v3 DisplayPort PHY register offsets used by the combo driver for AUX interrupts, AUX BIST, VCO division, lane control, spare register, and status polling.

## Important APIs, Types, and Functions
The constants include `QSERDES_V3_DP_PHY_AUX_INTERRUPT_MASK`, `AUX_INTERRUPT_CLEAR`, `AUX_BIST_CFG`, `VCO_DIV`, `TX0_TX1_LANE_CTL`, `TX2_TX3_LANE_CTL`, `SPARE0`, and `STATUS`. There are no executable APIs.

## Control Flow
`phy-qcom-qmp-combo.c` uses these offsets through its v3 register layout and v3 AUX/DP configuration functions. DP initialization writes AUX config and lane control, programs VCO division by link rate, then polls the v3 status register.

## State and Persistence
No software state exists in the header. Hardware state persists in the mapped DP PHY register block until reset or power loss.

## Dependencies and Integration Points
The header is paired with `phy-qcom-qmp-dp-phy.h` for common DP PHY offsets/bits and with QSERDES/PCS generation headers in the combo driver. It is selected indirectly through compatible-specific register layout arrays.

## Risks and Edge Cases
Offsets are generation-specific and must not be reused for v4+ hardware where AUX/status locations moved. The header does not define masks for status interpretation; callers must know which bits to poll.

## Test Signals
Successful v3 DP AUX setup, link clock programming, lane-control writes, and status-bit polling during RBR/HBR/HBR2/HBR3 link training validate use of these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v4.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v4.h

## Purpose
This header defines QMP v4 DisplayPort PHY offsets, reflecting the v4 movement of AUX interrupt and status registers compared with v3.

## Important APIs, Types, and Functions
It exports offsets for v4 AUX interrupt mask/clear/status, `VCO_DIV`, lane-control registers, `SPARE0`, and `STATUS`. There are no functions or types.

## Control Flow
The combo driver's v4/v5/v6-style DP path uses these offsets for AUX initialization, lane control, VCO division, and status polling in `qmp_v456_configure_dp_phy()` and related callbacks when the compatible's register layout points at v4 definitions.

## State and Persistence
The file has no state. The register values are hardware state controlled by the parent PHY driver's init, configure, and power-off paths.

## Dependencies and Integration Points
It integrates with common DP PHY definitions and the QMP combo driver's register layout arrays. The v4 AUX interrupt status offset supports decoding with common AUX error masks from `phy-qcom-qmp-dp-phy.h`.

## Risks and Edge Cases
Because v4 offsets differ from v3, wrong layout selection can break AUX interrupt handling and status polling. The header does not include semantic masks for lane-control values, so correctness depends on the driver's magic constants and hardware documentation.

## Test Signals
DP link bring-up on v4-based SoCs, AUX interrupt/error reporting, and correct status polling after link enable are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v5.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v5.h

## Purpose
This compact header defines the QMP v5 DisplayPort PHY offsets needed by common combo code: VCO division, AUX interrupt status, and PHY status.

## Important APIs, Types, and Functions
It exports `QSERDES_V5_DP_PHY_VCO_DIV`, `QSERDES_V5_DP_PHY_AUX_INTERRUPT_STATUS`, and `QSERDES_V5_DP_PHY_STATUS`. There are no functions or structures.

## Control Flow
QMP combo configurations using a v5 DP PHY layout refer to these offsets when setting link-rate VCO division and polling DP PHY readiness/status. AUX status can be paired with the common AUX error masks.

## State and Persistence
The header has no state. The named registers are programmed or observed by the parent driver during DP configure, power-on, calibration, and error handling.

## Dependencies and Integration Points
It is generation-specific glue for the QMP combo driver and common DP PHY bit definitions. It assumes other generation headers provide the SerDes and TX register definitions used alongside these offsets.

## Risks and Edge Cases
Only a minimal register subset is defined, so callers needing v5-specific lane-control or AUX mask/clear offsets must use other layouts or avoid unsupported operations. Incorrect generation selection will affect link-rate setup and status polling.

## Test Signals
Expected validation is successful DP link training on v5 hardware, correct pixel/link clock rates, and status/AUX behavior matching hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v6.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v6.h

## Purpose
This header defines the QMP v6 DisplayPort PHY offsets used by combo PHY configurations for VCO division, AUX interrupt status, and PHY status.

## Important APIs, Types, and Functions
It provides `QSERDES_V6_DP_PHY_VCO_DIV`, `QSERDES_V6_DP_PHY_AUX_INTERRUPT_STATUS`, and `QSERDES_V6_DP_PHY_STATUS`. It contains no executable code.

## Control Flow
The combo driver uses these offsets through v6 register layout arrays while configuring DP link rates, checking AUX errors, and polling for PHY readiness during v6-class DP bring-up.

## State and Persistence
No software state exists. Hardware state is controlled by the parent QMP combo driver's power and configure callbacks.

## Dependencies and Integration Points
This file integrates with `phy-qcom-qmp-combo.c`, common DP PHY definitions, and v6 QSERDES/PCS headers. SoC configs such as SM8550/SM8650/SAR2130P use v6-era DP tables and layouts.

## Risks and Edge Cases
The v6 status offsets differ from v5/v4; wrong layout pairing can produce false timeouts or missed AUX error reporting. The header intentionally does not validate link rates or lane counts.

## Test Signals
DP link training at all supported rates, AUX read/write reliability, and absence of configure timeouts are the main signals that these offsets are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v8.h

## Purpose
This header defines QMP v8 DisplayPort PHY offsets, including newer AUX-less timing and lane-drive registers used by v8/n3 combo PHY configurations.

## Important APIs, Types, and Functions
It exports offsets for `VCO_DIV`, `AUX_INTERRUPT_STATUS`, `TSYNC_OVRD`, lane-control registers, AUX-less config/timing registers, LFPS timing, lane drive levels, and `STATUS`. There are no functions.

## Control Flow
`qmp_v8_configure_dp_clocks()` and `qmp_v8_configure_dp_phy()` in the combo driver write the v8 AUX-less timing, LFPS, TSYNC override, lane-control, and lane-drive offsets, then poll the v8 status register during bring-up.

## State and Persistence
The header itself has no state. The values written to these registers are established during DP power-on and reset by the common block or platform power transitions.

## Dependencies and Integration Points
It is used with v8 DP QSERDES COM definitions and v8/n3 USB43DP combo configs. It complements the common DP PHY offsets for base config and power-down control.

## Risks and Edge Cases
`QSERDES_V8_DP_PHY_AUXLESS_SETUP_CYC` and `QSERDES_V8_DP_PHY_AUXLESS_SILENCE_CYC` are both defined as `0x0d8`; if this is not intentional for the hardware, one timing write overwrites the other. V8 offsets are not compatible with earlier QMP DP PHY generations. AUX-less and TSYNC programming are sensitive to hardware revision.

## Test Signals
Validation should include v8 DP link training at RBR/HBR/HBR2/HBR3, Type-C orientation changes, AUX/AUX-less behavior, and inspection of timeout-free status polling on Glymur/v8-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy.h

## Purpose
This common DP PHY header defines generation-independent QMP DisplayPort PHY offsets and bit masks for revision IDs, core config, AUX config, power-down control, TX drive/pre-emphasis muxing, and AUX error handling.

## Important APIs, Types, and Functions
It exports `QSERDES_DP_PHY_*` offsets for revision, config, mode, power-down, and AUX config registers. It also defines common bit masks for QSERDES v3 bias/clock buffer enable fields, DP TX driver and pre-emphasis mux/mask fields, `DP_PHY_PD_CTL_*` power-down bits, and AUX interrupt error masks. There are no functions.

## Control Flow
The combo driver uses these definitions in DP AUX initialization, DP mode/orientation selection, DP power-off, swing/pre-emphasis programming, and AUX error-mask writes. Version-specific headers add the VCO, lane-control, status, and AUX interrupt offsets that vary by generation.

## State and Persistence
This header has no state. The constants describe hardware register state owned by the parent PHY driver.

## Dependencies and Integration Points
It is included by QMP combo DP code and sits alongside `phy-qcom-qmp-dp-phy-v*.h` and `phy-qcom-qmp-dp-com-v3.h`. It is central to Type-C/DP lane power selection because `DP_PHY_PD_CTL_*` bits are used to power down or release lanes depending on lane count and orientation.

## Risks and Edge Cases
The bit names encode shared assumptions about DP PHY power-down polarity and TX mux behavior. Wrong use can leave AUX, PLL, or lane groups powered down when link training expects them active. Since the masks are common, callers must still select the correct generation-specific offsets.

## Test Signals
Useful validation includes correct AUX transaction behavior, DP lane power selection for 1/2/4-lane modes, successful voltage swing/pre-emphasis changes from link training, and reliable power-down on DP off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-qserdes-com-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-qserdes-com-v8.h

## Purpose
This header defines QSERDES COM register offsets for QMP v8 DisplayPort PLL/SerDes programming. It supports v8 DP link-rate tables in the combo driver.

## Important APIs, Types, and Functions
The constants cover v8 COM registers for HS clock selection, VCO calibration compare codes, SSC step/per settings, charge pump/R/C controls, core clock division, lock compare, divider fractions, loop gains, VCO tune, bias/clock enables, sysclk controls, resets, lock enable, clock select, common config, clock forwarding, and ready/status registers. There are no functions.

## Control Flow
`phy-qcom-qmp-combo.c` uses these offsets in v8 DP SerDes init tables and link-rate-specific RBR/HBR/HBR2/HBR3 tables. During DP power-on, the driver writes the base v8 SerDes table, applies the selected link-rate table, then polls COM ready/status registers through the configured layout.

## State and Persistence
No software state is stored here. Hardware state is the v8 DP PLL/SerDes programming established by the parent driver's table writes.

## Dependencies and Integration Points
This header is paired with v8 DP PHY offsets and QMP combo configs such as Glymur USB43DP. It is consumed through `QMP_PHY_INIT_CFG()` tables from `phy-qcom-qmp-common.h`.

## Risks and Edge Cases
The offsets are highly hardware-generation-specific and mostly analog PLL tuning registers. Incorrect values or accidental use on non-v8 hardware can prevent PLL lock or create marginal DP signal behavior. Because table writes are not read back, errors usually surface only as link-training or status-poll failures.

## Test Signals
Signals include successful COM ready status, stable PLL lock at all supported DP link rates, correct DP link/pixel clock rates, and no timeout in v8 DP configure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-dp-qserdes-com-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-msm8996.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-msm8996.c

## Purpose
This driver implements the Qualcomm QMP PCIe PHY block for MSM8996 using the `qcom,msm8996-qmp-pcie-phy` binding. It exposes up to three per-lane generic PHYs sharing a common SerDes/common block, regulators, resets, and clocks.

## Important APIs, Types, and Functions
`struct qmp_phy_cfg` describes the number of PHYs, SerDes/TX/RX/PCS init tables, clock/reset/regulator names, and register layout offsets. `struct qmp_phy` represents one lane with TX/RX/PCS MMIO, pipe clock, lane reset, index, and backpointer. `struct qcom_qmp` stores shared clocks, resets, regulators, lane array, mutex, and `init_count`.

Common sequencing is in `qmp_pcie_msm8996_com_init()` and `qmp_pcie_msm8996_com_exit()`. `qmp_pcie_msm8996_serdes_init()` writes SerDes tables and polls common PCS ready. `qmp_pcie_msm8996_power_on()` initializes SerDes, releases lane reset, enables pipe clock, writes lane tables, powers up PCS, starts PCS/SerDes, and polls lane status. Creation/probe helpers allocate lanes, map child resources, register fixed 125 MHz pipe clock providers, and register the PHY provider.

## Control Flow
Probe maps the shared SerDes resource, initializes bulk clocks/resets/regulators, counts available child nodes, allocates lane slots, and for each child maps TX/RX/PCS resources, obtains a child pipe clock and lane reset, creates a generic PHY, and registers that child's pipe clock source. The exported `.power_on` callback wraps common init plus lane power-on; `.power_off` powers off the lane and exits the common block.

The common init path is reference-counted by `init_count` under `phy_mutex`. The first lane enables regulators, asserts/deasserts shared resets, enables shared clocks, and powers the common block. The last exit asserts resets, disables clocks, and disables regulators. Lane power-on writes TX/RX/PCS tables and polls `PHYSTATUS` clear.

## State and Persistence
Shared state is `init_count` and the per-lane objects. Hardware state is reprogrammed on power-on and cleared through resets or power-down. Pipe clock providers persist for each child node until device removal.

## Dependencies and Integration Points
The driver depends on QMP common table helpers, QMP register definitions, Linux PHY, platform, OF child-node resource mapping, reset, regulator, clock-provider, and iopoll APIs. Device tree must provide one parent SerDes resource and lane child nodes with TX/RX/PCS resources, lane reset, pipe clock, and `clock-output-names`.

## Risks and Edge Cases
`qmp_pcie_msm8996_power_on()` calls `qmp_pcie_msm8996_serdes_init()` without checking its return value, so common SerDes timeout can be ignored and lane init can proceed. Child count is only rejected when greater than the expected lane count; fewer children are allowed. The common exit sequence sets start/reset/power bits in a way that depends on hardware semantics and should be verified against MSM8996 documentation. The fixed pipe clock is 125 MHz, unlike the separate PCIe2 driver's 250 MHz source.

## Test Signals
Signals include probe with one to three lane child nodes, successful pipe clock provider registration per child, shared init reference counting across simultaneous lanes, PCS ready and PHYSTATUS polling success, and PCIe link training on each lane. Negative tests should cover missing child resources, missing `clock-output-names`, lane reset failures, and SerDes timeout propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-msm8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-qhp.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-qhp.h

## Purpose
This header defines Qualcomm QHP PCIe Gen3 QMP register offsets for COM, lane, and PCS blocks. It supports PCIe Gen3 PHY init tables elsewhere in the Qualcomm QMP PHY drivers.

## Important APIs, Types, and Functions
The constants are grouped into COM PLL/SSC/clock/tuning registers, lane driver/RX equalization/CDR/sigdet/DCC/RSM registers, and PCS TX magnitude/power-state/config registers. There are no functions or structures.

## Control Flow
Drivers include this header to build `qmp_phy_init_tbl` arrays that program Gen3 QHP PCIe COM, lane, and PCS blocks. Runtime sequencing, resets, polling, and clock control are handled by the including driver.

## State and Persistence
The header has no state. It names hardware registers whose state is set by parent driver table writes during PHY initialization and power transitions.

## Dependencies and Integration Points
It is a generation/protocol-specific register map for QMP PCIe drivers and pairs with the common QMP table helpers. The offsets cover analog PLL, TX, RX, equalization, signal detect, and PCS power settings needed for PCIe Gen3.

## Risks and Edge Cases
Because every symbol is a raw offset, incorrect pairing with non-QHP or non-Gen3 hardware can corrupt unrelated registers. Many registers are analog tuning controls, so values using these offsets must be validated through link stability and compliance testing, not just compile coverage.

## Test Signals
Validation comes from successful PCIe Gen3 link training, stable operation under ASPM/power-state transitions, PLL lock, receiver detection/signal-detect behavior, and absence of PHY initialization timeouts in the including driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-qhp.h -->
