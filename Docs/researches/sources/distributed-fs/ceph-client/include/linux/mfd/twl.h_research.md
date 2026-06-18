# sources/distributed-fs/ceph-client/include/linux/mfd/twl.h

## Purpose
`twl.h` is the central public header for TWL4030/TWL5031/TWL6030/TWL6032-family PM and audio codec devices. It defines module IDs, register offsets that must be shared across subdrivers, I2C accessors, interrupt offsets, power-bus message encoding, board platform data, regulator IDs, and feature flags.

## Important APIs, Types, and Functions
Core enums identify common, TWL4030-only, and TWL6030-only modules. APIs include `twl_rev()`, class helpers, `twl_set_regcache_bypass()`, multi-byte/single-byte `twl_i2c_*` helpers, 16-bit little-endian helpers, type/version/HFCLK queries, TWL6030 interrupt mask/unmask, `twl4030_sih_setup()`, `twl4030_remove_script()`, and `twl4030_power_off()`. Structs define clock, charger, GPIO, MADC, keypad, USB PHY, power scripts, resource configs, codec/vibra/audio data, and regulator driver hooks. Macros encode GPIO, INTBR, keypad, MADC, charger, PM master, power resources, power-bus messages, and regulator IDs.

## Control Flow
Subdrivers address registers as `{module id, offset}` and the TWL core maps that pair to the proper I2C slave and absolute address. Board power scripts are arrays of encoded power-bus messages downloaded or removed by the PM core, and SIH setup creates nested IRQ handling for shared interrupt blocks.

## State and Persistence Behavior
Hardware state spans module register files, interrupt masks, GPIO direction/debounce/pulls, PM master scripts, power-resource states, charger data, keypad rows/cols, USB PHY settings, clocks, and regulators. Software state is platform data and script/resource configuration consumed at probe.

## Dependencies and Integration Points
The header depends on kernel types and matrix keypad data. It integrates with I2C/regmap core, IRQ/SIH handling, GPIO, keypad, MADC, charger, USB PHY, audio, vibra, regulator, clock, and OMAP power-management code.

## Risks and Test Signals
Risks include wrong module ID to slave mapping, broad exported register constants encouraging cross-driver coupling, endian mistakes in 16-bit helpers, power-bus script errors that affect sleep/wake/reset, and class-specific TWL4030/TWL6030 register confusion. Test signals are I2C helper read/write tests, SIH nested IRQ tests, power script encoding tests, regulator ID mapping tests per chip class, keypad matrix tests, USB PHY callbacks, and suspend/resume power-resource validation.
