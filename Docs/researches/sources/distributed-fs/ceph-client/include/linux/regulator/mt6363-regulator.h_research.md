# sources/distributed-fs/ceph-client/include/linux/regulator/mt6363-regulator.h

## Purpose

This header defines MediaTek MT6363 regulator register addresses, bit positions, and masks used by the MT6363 regulator driver.

## Important APIs, Types, and Functions

It includes `linux/bits.h` and defines a large set of register constants. These cover top/trap/key registers, buck enable and low-power control registers, buck voltage selector registers and masks, watchdog/debug VOSEL registers, efuse masks, operation-enable and hardware low-power mode registers, sensor-hub alternate controls, forced PWM/FCCM bits, LDO enable/LP/op-enable registers, LDO voltage selector/calibration registers, and current-sink controls.

No C structs or functions are declared; the API is the macro register map.

## Control Flow

The driver uses these constants with regmap operations to enable/disable bucks and LDOs, set low-power modes, program voltage selectors and calibration fields, unlock protected areas, select debug/watchdog values, and control isink channels.

## State and Persistence Behavior

The header itself has no state. The addressed PMIC registers are hardware state and may persist until PMIC reset or power loss. Some registers are protected or debug-oriented and require careful write sequencing.

## Dependencies and Integration Points

It depends on `GENMASK()` from `linux/bits.h` and integrates tightly with the MT6363 PMIC regmap and regulator descriptor tables.

## Risks

Register-address or mask errors directly affect hardware power rails. Shared registers with multiple bitfields, debug VOSEL paths, protected key registers, and sensor-hub aliases are high risk. Incorrect LP/enable bit selection can leave domains powered incorrectly during suspend.

## Test Signals

Tests should verify every descriptor's enable, mode, and voltage fields against these macros, check regmap read/write traces, validate suspend low-power mode programming, and compare constants against the PMIC datasheet.
