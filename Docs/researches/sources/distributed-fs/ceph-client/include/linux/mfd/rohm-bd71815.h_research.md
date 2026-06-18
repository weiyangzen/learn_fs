# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd71815.h

## Purpose
`rohm-bd71815.h` declares the shared register map, regulator IDs, interrupt IDs, and masks for the ROHM BD71815 PMIC. It supports regulator, RTC, charger, battery monitor/fuel gauge, LED/WLED, GPIO/GPO, clock, and interrupt child drivers.

## Important APIs, Types, And Constants
The first enum assigns regulator IDs for five bucks, LDO1-5, LDODVREF, LDOLPSR, WLED, and total count. The register enum maps device/power control, buck/LDO modes and voltages, LED, GPO, 32 kHz output, RTC time/alarms, charger state/configuration, battery and DCIN/VSYS status, ADC/measurement registers, coulomb counter registers, interrupt enable/status/update registers, REX/full counters, and test mode. Bit masks define buck ramp and power-state enables, DVS select/defaults, LDO modes, output clock mode, battery/DCIN status, RTC alarm, power-control restart, GPIO drive type, interrupt enable masks, individual interrupt IDs, interrupt bit masks, coulomb counter control, current direction, REX clear/state, and charge-done LED enable.

## Control Flow And State
The MFD core uses the register map and IRQ masks to configure regmap and regmap-irq. Regulator children use regulator IDs plus buck/LDO mode and voltage registers. RTC children use `BD71815_REG_RTC_START` and alarm start/mask definitions. Charger and battery drivers read charger state, battery status, voltage/current monitor registers, coulomb counter registers, and interrupt sources. LED/GPO/clock children use LED control, GPO, and OUT32K definitions.

## State And Persistence Behavior
Hardware-backed state includes rail modes, voltages, power-state participation, LED current/enables, GPIO output/drive, RTC time/alarms, charger state/configuration, watchdog, battery presence/temperature, voltage/current measurements, coulomb counts, and retained REX/full charge counters. Interrupt enable/status registers are persistent until changed or cleared according to hardware semantics. There is no runtime struct in this header.

## Dependencies And Integration Points
The header depends on regmap and integrates with ROHM MFD core code, regulator, RTC, power-supply/charger/fuel-gauge, LED, GPIO/GPO, clk, and regmap-irq subsystems. Interrupt definitions are organized by hardware status register groups and must match the regmap IRQ table.

## Risks
The register enum has non-contiguous blocks and explicit offsets, so inserting values incorrectly would shift later addresses. Interrupt names and masks are group-specific; reusing a mask against the wrong `INT_STAT_xx` register is a likely bug. Charger/battery monitor fields include signed direction bits, so current interpretation must preserve discharging flags. Some comments reference BD71805 while the file is BD71815, a documentation consistency risk.

## Test Signals
Tests should cover regulator mode/voltage programming, RTC read/alarm, charger state transitions, battery detection and temperature interrupts, coulomb counter enable/reset/current direction, LED and OUT32K control, GPIO drive/output, and regmap-irq mapping for all grouped masks.
