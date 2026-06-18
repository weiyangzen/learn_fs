# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71828.h

## Purpose
`rohm-bd71828.h` provides the shared register and interrupt definitions for the ROHM BD71828 PMIC. It is used by child drivers for regulators, GPIO, 32 kHz clock, RTC, charger, battery/fuel gauge, LEDs, and interrupt handling.

## Important APIs, Types, And Constants
The regulator enum covers BUCK1-7, LDO1-6, LDO_SNVS, and total count. Voltage-count constants and masks describe selector ranges, including fixed 1.8 V LDO6. Register macros define mode control, run-level/DVS controls, buck/LDO enable/mode/voltage registers, GPIO control and IO status, OUT32K, RTC time and three alarm blocks, charger/battery status and ADC values, coulomb-counter/current/voltage measurement registers, LED control, interrupt mask/status/update registers, and maximum register. Main IRQ bit IDs aggregate BUCK, DCIN, VSYS, CHG, BAT, BAT_MON, TEMP, and RTC groups. The interrupt enum and per-interrupt masks define detailed events such as buck OCP, DCIN insertion/removal, button pushes, watchdog/reset, VSYS transitions, charger state, battery/thermal events, coulomb counter thresholds, overcurrent, temperature, and RTC alarms.

## Control Flow And State
The MFD core configures regmap/regmap-irq using the register and mask definitions. Regulator children use enable/mode/voltage registers and DVS/run-level masks. GPIO and clock children manipulate GPIO control and OUT32K registers. RTC uses contiguous time and alarm registers. Charger and fuel-gauge children read DCIN, battery, voltage/current, coulomb counter, and measurement-clear registers. Interrupt handling fans out from `BD71828_REG_INT_MAIN` to the group status registers.

## State And Persistence Behavior
Hardware-backed state includes regulator enable and low-power modes, DVS source, run levels, GPIO drive/output, RTC time/alarms, charger enable/state, DCIN/battery presence, voltage/current/coulomb measurements, LED state, and interrupt masks/status. Coulomb counter clear bits and measurement clear registers are stateful operations with side effects. This header has no runtime struct; state ownership lives in MFD core and child drivers.

## Dependencies And Integration Points
The header depends on `linux/bits.h`, `linux/mfd/rohm-generic.h`, and `linux/mfd/rohm-shared.h`. It integrates with ROHM common MFD support, regulator, RTC, GPIO, clk, LED, power-supply/fuel-gauge, and regmap-irq subsystems. The main/group IRQ split is a key integration contract.

## Risks
The register map is broad and includes repeated macro definitions such as `BD71828_REG_CHG_STATE`, so maintainers must avoid accidental redefinition drift. Interrupt masks are raw hex values grouped by register; using them outside the correct group will mis-handle events. Coulomb counter and battery-current direction masks require careful signed conversion. DVS/run-level control can alter CPU/SoC rail behavior if programmed incorrectly.

## Test Signals
Tests should verify regulator selector ranges and fixed LDO6 handling, DVS/run-level mode changes, GPIO output and drive modes, RTC alarms, charger enable and DCIN detection, battery presence/temperature, coulomb counter clear/read paths, LED masks, and regmap-irq main-to-group fan-out.
