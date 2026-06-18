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
