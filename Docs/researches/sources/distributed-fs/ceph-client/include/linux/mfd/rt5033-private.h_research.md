# sources/distributed-fs/ceph-client/include/linux/mfd/rt5033-private.h

## Purpose

This 276-line private Richtek RT5033 header defines charger, regulator, flash LED, fuel-gauge, IRQ, and voltage/current conversion constants for the RT5033 MFD family.

## Important APIs, Types, and Functions

It exports `enum rt5033_reg`, charger status/control masks, charger mode/timer/current/voltage limit constants, regulator voltage ranges for buck/LDO/safe LDO, `enum rt5033_fuel_reg`, fuel-gauge present bit, PMIC IRQ masks, and charger model/manufacturer strings. There are no function declarations.

## Control Flow

The header is table data for child driver flow. Charger code decodes status registers, programs AICR/MIVR/timer/mode/current/voltage fields, regulator code maps selector values to microvolts, and fuel-gauge code addresses OCV/VBAT/SOC/config registers.

## State and Persistence Behavior

State persists in RT5033 registers: charger state, current/voltage limits, timer enables, OTG/high-impedance/UUG mode bits, regulator enables/vsel fields, fuel-gauge measurements, and IRQ status/mask bits.

## Dependencies and Integration Points

It is consumed by RT5033 MFD, charger, regulator, LED, fuel-gauge/power-supply, and IRQ handling code. It pairs with `rt5033.h` for the public parent-device structure.

## Risks and Edge Cases

Many constants encode hardware units and selector caps; off-by-one conversions can overprogram charge current or voltage. Charger current limiting distinguishes input-current AICR from fast-charge current. Reserved register holes must not be treated as contiguous writable areas.

## Test Signals

Charger property conversion tests, regulator selector-to-voltage tests, regmap reserved-register range checks, IRQ mask tests, and hardware charge/discharge tests for status decoding.
