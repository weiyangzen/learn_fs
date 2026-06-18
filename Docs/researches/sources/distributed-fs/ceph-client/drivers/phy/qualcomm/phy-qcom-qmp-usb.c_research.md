# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb.c

## Purpose

This file is the current standalone Qualcomm QMP USB3/USB3 UNI PHY platform driver. It supports many QMP generations and SoCs, including IPQ, MSM8996, QDU1000, SA8775P, SC8280XP, SDX55/65/75, SM8150/8250/8350, X1E80100, QCS8300, and Glymur USB3 UNI PHY. It programs SERDES/TX/RX/PCS/PCS_USB tables, registers the pipe clock source, supports runtime PM autonomous wake mode, and exposes a Linux generic PHY.

Compared with `phy-qcom-qmp-usb-legacy.c`, this driver uses shared QMP table helpers from `phy-qcom-qmp-common.h`, handles mostly single-lane USB3 PHYs, uses optional input clock acquisition for flat bindings, and has workarounds for overlapping legacy PCS mappings on selected compatibles.

## Important APIs, types, and data

- `struct qmp_usb_offsets` describes flat single-resource layouts: `serdes`, `pcs`, `pcs_misc`, `pcs_usb`, `tx`, and `rx`.
- `struct qmp_phy_cfg` maps a compatible to init tables, regulator data, register layout, optional power-down delay, and optional `pcs_usb_offset`.
- `struct qmp_usb` contains runtime state: device, cfg, register bases, pipe clock, bulk clocks/resets, regulators, current mode, generic PHY, and fixed-rate pipe clock object.
- Register layout arrays `qmp_v2_usb3phy_regs_layout` through `qmp_v7_usb3phy_regs_layout` abstract generation-specific PCS offsets.
- The table families tune PLL and spread-spectrum settings, TX impedance/drive, RX CDR/equalization, PCS lock detection, receiver detect delays, LFPS, and RXEQ training.
- `glymur_usb3_uniphy_cfg` uses v8-style SERDES/TX/RX/PCS/PCS_USB tables and `qmp_usb_offsets_v8`, but its standalone USB3 tables reference the non-USB43 `QSERDES_V8_*` and `QPHY_V8_*` maps rather than the USB4.3-specific headers.

The generic PHY ops are:

- `.init = qmp_usb_enable`
- `.exit = qmp_usb_disable`
- `.set_mode = qmp_usb_set_mode`

Internally, `.init` calls `qmp_usb_init()` and `qmp_usb_power_on()`, while `.exit` calls `qmp_usb_power_off()` and `qmp_usb_exit()`.

## Control flow

Probe:

1. `qmp_usb_probe()` allocates `struct qmp_usb`, stores it as device driver data, reads OF match data, and gets cfg-specific regulators with `devm_regulator_bulk_get_const()`.
2. If a legacy child node exists, `qmp_usb_parse_dt_legacy()` maps parent resource 0 as SERDES, maps child TX/RX/PCS/PCS_MISC resources, optionally sets `pcs_usb` from `pcs_usb_offset`, obtains the child pipe clock, gets all parent clocks, and initializes legacy reset names (`phy`, `common`). For SDX65 and SM8350 UNI legacy bindings it deliberately allows overlapping PCS mappings via `qmp_usb_iomap(..., exclusive=false)`.
3. If no child exists, `qmp_usb_parse_dt()` maps one resource, derives all sub-block bases from `cfg->offsets`, initializes optional standard clocks (`aux`, `cfg_ahb`, `ref`, `com_aux`), gets the `"pipe"` clock, and initializes flat-binding reset names (`phy_phy`, `phy`).
4. Runtime PM is enabled and then forbidden by default.
5. `phy_pipe_clk_register()` publishes a fixed 125 MHz pipe clock source from `clock-output-names`.
6. The generic PHY is created and registered with `of_phy_simple_xlate`.

Enable and link bring-up:

1. `qmp_usb_init()` enables regulators, asserts and deasserts reset controls, enables bulk clocks, and sets `SW_PWRDN`.
2. `qmp_usb_power_on()` writes SERDES tables, enables the pipe clock, programs TX/RX lane 1 tables, programs PCS and optional PCS_USB tables, applies a 10-20 microsecond delay when `has_pwrdn_delay` is set, clears PCS software reset, starts SERDES and PCS, and polls until `PHYSTATUS` clears.
3. `qmp_usb_power_off()` disables the pipe clock, asserts PCS software reset, clears start bits, and clears `SW_PWRDN`.
4. `qmp_usb_exit()` asserts resets, disables bulk clocks, and disables regulators.

Runtime PM:

- `qmp_usb_runtime_suspend()` enables autonomous wake mode, disables pipe and bulk clocks, and skips work if the PHY is not initialized.
- `qmp_usb_runtime_resume()` restores clocks and disables autonomous mode.
- Autonomous mode clears pending IRQ state, selects LFPS/RXTERM interrupt masks based on `qmp->mode`, and toggles optional PCS_MISC clamp bits only when the layout provides `QPHY_PCS_MISC_CLAMP_ENABLE`.

## State and persistence behavior

Runtime state is volatile and held in `struct qmp_usb`. The main state variable is `qmp->mode`, which is used only for autonomous wake interrupt policy. Hardware state is maintained by register writes while the PHY is powered or while autonomous mode remains armed during runtime suspend. There is no disk persistence.

Clock and reset counts are runtime-discovered for legacy bindings but fixed to the standard optional clock/reset lists for flat bindings. Devm-managed resources handle cleanup on probe failure or device removal.

## Dependencies and integration points

- Linux PHY framework, OF platform matching, runtime PM, regulator bulk APIs, reset bulk APIs, and clock provider APIs.
- `phy-qcom-qmp-common.h` provides `qmp_configure()` and `qmp_configure_lane()`.
- `phy-qcom-qmp.h` and included register-map headers define QSERDES, PCS, PCS_USB, and PCS_MISC offsets.
- The USB controller consumes the published PHY and `"pipe"` clock. GCC consumes the fixed-rate pipe clock source as a parent for its gated pipe clock.
- Device tree must provide either the legacy child-node resource layout or the newer flat register region with compatible-specific offsets.

## Risks and edge cases

- The file is highly table-driven. Mistakes in a table, offset layout, or compatible-to-cfg mapping can pass compilation but fail as link training, enumeration, or intermittent signal-integrity issues.
- The `glymur_usb3_uniphy_cfg` uses `qmp_v7_usb3phy_regs_layout` with v8 data tables. That may be intentional compatibility, but it is a high-value review point whenever v8 PCS status or control offsets change.
- Overlapping PCS mapping exceptions for SDX65 and SM8350 legacy bindings are explicit FIXME areas. Binding cleanup could break old DTs if not coordinated.
- Runtime PM autonomous mode depends on the current PHY mode. If consumers do not call `.set_mode`, wake-detection policy defaults to the non-host/device branch.
- `qmp_usb_init()` does not program tables; table programming happens in power-on inside the combined `.init` wrapper. Future refactors must preserve this sequencing.
- `has_pwrdn_delay` is per-cfg. Missing it on hardware that needs the delay can create flaky initialization.

## Test signals

- Compile with all referenced QMP headers and compatibles enabled.
- Probe checks should verify regulator acquisition, both legacy and flat resource mapping, optional clock handling, reset names, pipe clock provider creation, and PHY provider registration.
- Runtime failures appear as regulator/clock/reset errors, `pipe_clk enable failed`, and `phy initialization timed-out`.
- Hardware validation should include SuperSpeed enumeration, host/device mode selection, runtime suspend/resume wake, repeated cable attach/detach, pipe clock parenting, and per-compatible smoke tests for both legacy child-node and flat DT bindings.
