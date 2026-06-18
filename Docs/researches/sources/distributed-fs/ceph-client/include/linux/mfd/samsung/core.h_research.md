# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/core.h

## Purpose

This 144-line header is the shared Samsung S2M/S5M PMIC core contract. It defines common voltage/ramp constants, supported device types, parent-device data, platform data, regulator init data, and operation modes.

## Important APIs, Types, and Functions

Exports include minimum voltage and step macros, `enum sec_device_type`, `struct sec_pmic_dev`, `struct sec_platform_data`, `struct sec_regulator_data`, `struct sec_opmode_data`, and `enum sec_opmode`. Platform data includes regulator arrays, GPIO DVS tables, buck voltage tables, ramp settings, shutdown behavior, and WRSTBI disable configuration.

## Control Flow

The header has no executable flow. MFD probe code fills `sec_pmic_dev` and platform data from board files or device tree; regulator drivers consume opmode and DVS data to program each PMIC variant.

## State and Persistence Behavior

Driver runtime state lives in `sec_pmic_dev` and platform data. Hardware state persists in PMIC registers, GPIO DVS pins, buck/LDO operation mode fields, and warm-reset behavior.

## Dependencies and Integration Points

It forward-declares GPIO descriptors and integrates Samsung MFD core, regulator drivers, RTC/IRQ support, I2C regmap access, and platform/device-tree configuration.

## Risks and Edge Cases

Platform data contains variant-sensitive arrays and fixed-size buck GPIO/DVS fields; mismatched counts or indexes can program the wrong rail. Manual poweroff and WRSTBI settings affect shutdown and reset behavior.

## Test Signals

Build tests across supported Samsung PMIC variants, platform-data/device-tree parsing tests, regulator DVS table validation, suspend/reset behavior tests, and probe ordering checks.
