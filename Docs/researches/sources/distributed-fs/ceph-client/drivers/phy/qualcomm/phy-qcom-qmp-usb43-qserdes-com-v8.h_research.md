# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-qserdes-com-v8.h

## Purpose

This header defines the USB4.3 v8 QSERDES COM register map for Qualcomm QMP PHYs. It is a dense list of offsets for PLL, clocking, spread-spectrum clocking, VCO tuning, calibration, adaptive analog controls, status, and debug registers. It has no runtime code and exists so table-driven PHY drivers can use named offsets instead of literals.

The header is included by `phy-qcom-qmp.h` and is referenced by USB4.3/DP combo PHY tables in `phy-qcom-qmp-combo.c`. It is distinct from `phy-qcom-qmp-qserdes-com-v8.h`, which provides non-USB43 v8 `QSERDES_V8_COM_*` names used by the standalone USB3 Glymur tables.

## Important APIs, types, and data

- Include guard: `QCOM_PHY_QMP_USB43_QSERDES_COM_V8_H_`.
- The file exports `QSERDES_V8_USB43_COM_*` macro constants only.
- Major register groups:
  - Mode-specific PLL programming for modes 0, 1, and 2: SSC step sizes, clock endpoint divisors, CP/R/C controls, core clock dividers, lock compare registers, DEC start, fractional dividers, integrator loop gains, VCO tune, IVCO, and HS clock selection.
  - Common clock and PLL control: `BG_TIMER`, SSC period/adjust registers, post dividers, bias and buffer enables, sysclk controls, PLL enable/control, reset state machine controls, lock compare enable/config, VCO tune ranges/timers, clock select, and core clock enable.
  - Common mode and analog controls: `CMN_CONFIG_*`, `CMN_MODE*`, VCO DC level, additional controls/misc, auto-gain adjustment, adaptive analog config, and adaptive PLL controls.
  - Calibration/status/debug: IVCO calibration, early lock compare, VCO/bias wait cycles, PSM calibration, clock-forwarding config, DCC and LDO calibration, mode-operation status, sysclk detect status, reset state, PLL calibration status, debug buses, and `C_READY_STATUS`.

## Control flow

There is no executable control flow. A consuming driver writes these offsets through init tables, typically after selecting an SoC-specific compatible and mapping the QSERDES COM base. The same table infrastructure may write different mode-specific offsets during USB4.3, DisplayPort, or combo PHY setup.

## State and persistence behavior

The header itself has no mutable state. The hardware registers it names hold PHY PLL/calibration/control state while the PHY is powered and may reset according to hardware reset sequencing. Persistence and ordering are entirely controlled by the driver that writes these registers.

## Dependencies and integration points

- Included through `phy-qcom-qmp.h`, making the macros available to QMP PHY drivers.
- Used by USB4.3/DP combo PHY initialization tables, including `QSERDES_V8_USB43_COM_*` references in `phy-qcom-qmp-combo.c`.
- Integrates with `struct qmp_phy_init_tbl` table writes and common QMP helper functions.
- Must remain consistent with adjacent v8 USB4.3 PCS, PCS USB, TX/RX, LALB, and DP PHY headers.

## Risks and edge cases

- This is a large raw register map; transcription errors can be difficult to detect at compile time and may only appear as unstable PLL lock, failed link training, or rate-specific failures.
- Similar non-USB43 v8 names exist with different macro prefixes and a smaller/different map. Using the wrong namespace in a table can silently program the wrong offset if the numeric layout diverges.
- Mode 0/1/2 regions are repetitive. Copy-paste mistakes between mode-specific groups are likely and should be reviewed against hardware documentation.
- Status and debug offsets near the end of the file are read-oriented in many drivers; writing them accidentally through a table would be a table-construction bug, not a header bug.

## Test signals

- Compile all consumers that include `phy-qcom-qmp.h` and use `QSERDES_V8_USB43_COM_*` names.
- Hardware bring-up should confirm PLL lock and `C_READY_STATUS`/PCS-ready behavior across all supported USB4.3/DP modes and rates.
- Regression tests should include rate switching and low-power transitions, because many offsets tune mode-specific PLL, SSC, calibration, and clock-forwarding behavior.
