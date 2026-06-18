# sources/distributed-fs/ceph-client/include/linux/regulator/gpio-regulator.h

## Purpose

This header defines platform data for regulators whose voltage or current is selected by GPIO pin states.

## Important APIs, Types, and Functions

`struct gpio_regulator_state` maps a value in microvolts or microamps to a GPIO bitfield. `struct gpio_regulator_config` includes supply/input names, boot enable state, startup delay, GPIO flags and count, available states, regulator type (`REGULATOR_CURRENT` or `REGULATOR_VOLTAGE`), and init data.

## Control Flow

The GPIO regulator driver uses the state table to map requested voltage/current values to GPIO output patterns. During probe it configures GPIOs with initial flags, applies boot/init constraints, and registers a regulator with the core.

## State and Persistence Behavior

Static state is the value-to-GPIO table. Runtime state is GPIO output levels, regulator core constraints, and hardware rail behavior driven by the GPIO pins.

## Dependencies and Integration Points

It depends on GPIO descriptor flags and regulator machine/type definitions. It integrates with board files and systems where external regulator selection pins are controlled directly by the SoC.

## Risks

Wrong bitfield ordering or GPIO flags can select the wrong voltage/current. Missing states can make valid consumer requests fail. Boot state must match actual pin/hardware state to avoid glitches.

## Test Signals

Tests should verify value-to-GPIO mapping, boot initial state, enable sequencing, voltage/current request failures for unsupported states, and polarity/flag handling.
