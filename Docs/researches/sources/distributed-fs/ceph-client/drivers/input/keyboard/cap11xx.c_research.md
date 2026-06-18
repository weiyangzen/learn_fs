# sources/distributed-fs/ceph-client/drivers/input/keyboard/cap11xx.c

## Purpose

`cap11xx.c` is an I2C input and optional LED driver for Microchip CAP11xx capacitive touch sensors. It verifies chip identity, configures sensor thresholds/gain/sensitivity/signal guards from device tree, reports touch channels as keys, and exposes supported LED outputs through the LED class.

## Important APIs, Types, and Functions

- Register definitions and `cap11xx_regmap_config` describe the 8-bit regmap, defaults, and volatile registers.
- `struct cap11xx_priv` holds regmap, device/input, hardware model, LED descriptors, configuration arrays, and flexible keycode storage.
- `struct cap11xx_hw_model` captures product ID, channel count, LED count, and feature flags for CAP1106/CAP1126/CAP1188/CAP1203/CAP1206/CAP1293/CAP1298.
- `cap11xx_init_keys()` validates and writes DT configuration and keycodes.
- `cap11xx_thread_func()` clears the interrupt, reads sensor state, reports each key, and syncs input.
- `cap11xx_set_sleep()`, input open/close, and `cap11xx_init_leds()` control power and LED outputs.

## Control Flow

Probe gets match data, allocates per-channel state, initializes I2C regmap, checks product/manufacturer/revision registers, applies DT configuration, allocates input, sets key capabilities and IDs, initializes optional LEDs, puts the chip into deep sleep when no LEDs require it awake, registers input, and requests a threaded IRQ. Input open wakes the sensor; close re-enters deep sleep unless LEDs are present. IRQ handling deasserts interrupt in main control, reads `SENSOR_INPUT`, emits key states, and syncs.

## State and Persistence Behavior

Configuration values are cached in `cap11xx_priv` and written to chip registers during probe. Regmap caching covers nonvolatile register defaults while volatile status/input registers are read live. LED state is held by hardware output control and LED class callbacks. Deep sleep is runtime state tied to input open/close, except disabled when LEDs must remain functional.

## Dependencies and Integration Points

The driver integrates with I2C, regmap, OF matching, input, optional LED class, GPIO consumer include support, bitfield helpers, and device-tree properties such as `linux,keycodes`, `autorepeat`, `microchip,sensor-gain`, `microchip,irq-active-high`, `microchip,sensitivity-delta-sense`, `microchip,input-threshold`, `microchip,calib-sensitivity`, and `microchip,signal-guard`.

## Risks and Edge Cases

DT arrays must match model channel counts and value constraints. `microchip,sensitivity-delta-sense` writes a complemented field-prep value, so this path deserves hardware verification. LED child `reg` values must be within model LED count. If IRQ polarity is wrong or the interrupt is not deasserted before status read, reports may be stale. Deep sleep is skipped when LEDs exist, increasing power consumption.

## Test Signals

Test each supported product ID, invalid manufacturer/product detection, all DT property bounds, default and custom keycodes, autorepeat, IRQ press/release reporting, LED registration and brightness, deep sleep on open/close, LED-present sleep behavior, and regmap error injection.
