# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb-legacy.c

## Purpose

This file is the legacy Qualcomm QMP USB3 plus DP PHY driver. It covers older USB3 PHY bindings that also require DP common-block programming and dual-lane register maps. It exposes one generic PHY to the USB controller, registers the 125 MHz pipe clock source, manages runtime PM autonomous wake mode, and performs SoC-specific register table programming for QMP v3/v4/v5 USB3 PHYs.

The “legacy” distinction matters in three ways: the file keeps its own local `struct qmp_phy_init_tbl` and table writer, it explicitly programs `dp_com` reset/mode registers, and it expects legacy child-node resource layouts with TX/RX/PCS/TX2/RX2/PCS_MISC resources.

## Important APIs, types, and data

- `struct qmp_phy_init_tbl` and `QMP_PHY_INIT_CFG(_LANE)` define offset/value/lane-mask table entries local to this driver.
- `enum qphy_reg_layout` normalizes PCS offsets for software reset, start, status, autonomous mode, LFPS/RXTERM interrupt clear, and power-down control.
- `struct qmp_usb_legacy_offsets` exists for flat mappings, with offsets for `serdes`, `pcs`, `pcs_usb`, `tx`, and `rx`.
- `struct qmp_phy_cfg` binds each compatible to SERDES/TX/RX/PCS/PCS_USB tables, clock names, reset names, regulator names, register layout, and optional `pcs_usb_offset`.
- `struct qmp_usb` stores mapped register bases, `dp_com`, pipe clock, bulk clocks, resets, regulators, current `enum phy_mode`, generic PHY, and the fixed-rate pipe-clock provider.
- `qmp_usb_legacy_of_match_table` supports compatibles including `qcom,sc7180-qmp-usb3-phy`, `qcom,sdm845-qmp-usb3-phy`, `qcom,sm8150-qmp-usb3-phy`, `qcom,sm8250-qmp-usb3-phy`, `qcom,sm8350-qmp-usb3-phy`, and `qcom,sm8450-qmp-usb3-phy`.

The generic PHY ops are intentionally combined:

- `.init = qmp_usb_legacy_enable`, which calls init plus power-on.
- `.exit = qmp_usb_legacy_disable`, which calls power-off plus exit.
- `.set_mode = qmp_usb_legacy_set_mode`.

## Control flow

Probe:

1. `qmp_usb_legacy_probe()` allocates runtime state, stores driver data, fetches the compatible cfg, initializes bulk clocks, resets, and regulator arrays from cfg names.
2. If a child node exists, `qmp_usb_legacy_parse_dt_legacy()` maps parent resources 0 and 1 as SERDES and DP_COM, then maps child resources as TX, RX, PCS, TX2, RX2, optional PCS_MISC, and pipe clock from the child.
3. If no child exists, `qmp_usb_legacy_parse_dt()` maps one base resource, derives block bases from cfg offsets, and gets the `"pipe"` clock.
4. Runtime PM is enabled but forbidden by default, preserving opt-in sysfs behavior.
5. `phy_pipe_clk_register()` registers a 125 MHz fixed-rate pipe clock provider using `clock-output-names`.
6. The driver creates and publishes a generic PHY.

PHY enable:

1. `qmp_usb_legacy_init()` enables supplies, asserts/deasserts resets, enables configured clocks, initializes DP_COM via `qmp_usb_legacy_init_dp_com()`, and sets `SW_PWRDN`.
2. `qmp_usb_legacy_power_on()` writes SERDES tables, enables the pipe clock, writes lane 1 and lane 2 TX/RX tables, writes PCS tables, delays briefly, clears PCS software reset, starts SERDES and PCS, and polls `QPHY_PCS_STATUS` until `PHYSTATUS` clears.
3. If pipe-clock enable or polling fails, the function unwinds the pipe clock and returns an error.

PHY disable:

1. `qmp_usb_legacy_power_off()` disables the pipe clock, asserts PCS software reset, clears start bits, and powers the PHY down.
2. `qmp_usb_legacy_exit()` asserts resets, disables bulk clocks, and disables regulators.

Runtime PM:

- `qmp_usb_legacy_runtime_suspend()` checks `qmp->phy->init_count`, enables autonomous LFPS/RXTERM wake mode, then disables pipe and bulk clocks.
- `qmp_usb_legacy_runtime_resume()` restores clocks and disables autonomous mode.

## State and persistence behavior

The driver keeps volatile state only: current PHY mode, resource handles, mapped register bases, and the pipe-clock provider object. Register writes persist only while the PHY retains power. Runtime suspend intentionally leaves enough PCS autonomous-mode state for wake detection while disabling clocks.

`qmp->mode`, set by `qmp_usb_legacy_set_mode()`, controls which autonomous wake interrupt mask is used. Host/device SuperSpeed modes enable LFPS detection; other modes select receiver-detect behavior.

## Dependencies and integration points

- Linux platform, device tree, PHY, regulator, reset, clock, and runtime PM frameworks.
- QMP register headers for PCS USB v4/v5, PCS misc v3, and DP COM v3.
- USB controller consumers receive the PHY through the OF PHY provider.
- GCC/clock-controller integration depends on the fixed-rate pipe clock provider and a corresponding `"pipe"` clock consumer path.
- DP common-register programming is local to this driver and assumes USB3 plus DP shared reset/mode controls.

## Risks and edge cases

- The legacy child resource order is rigid. Misordered TX/RX/PCS/TX2/RX2 resources can write tuning values into the wrong MMIO region.
- DP_COM programming hard-codes default Type-C orientation to CC1 and enables both USB3 and DP mode bits. Boards with different orientation handling depend on higher-level muxing not represented here.
- The driver always configures `tx2` and `rx2` in power-on. The supported cfgs are dual-lane, but any future single-lane legacy cfg would need careful changes.
- Runtime PM reads `qmp->phy->init_count` directly. That is a common in-tree pattern but is sensitive to PHY core semantics.
- `pcs_usb` falls back to `pcs` for autonomous-mode registers. A bad `pcs_usb_offset` or missing layout entry can break wake signaling.
- Because `.init` includes power-on and `.exit` includes power-off, this driver’s operation ordering differs from newer drivers that separate `.power_on`.

## Test signals

- Build coverage under the relevant Qualcomm QMP USB legacy config, including local table helpers and DP COM register definitions.
- Probe should verify clock/reset/regulator acquisition, DP_COM ioremap for legacy bindings, pipe clock registration, and OF PHY provider publication.
- Runtime logs to watch: `reset assert failed`, `reset deassert failed`, `pipe_clk enable failed`, and `phy initialization timed-out`.
- Hardware tests should cover USB3 enumeration, host/device mode changes, runtime suspend/resume wake detection, pipe clock parenting through GCC, and boards using each listed compatible.
