# sources/distributed-fs/ceph-client/include/linux/mfd/ti-lmu.h

## Purpose

This 87-line header defines the shared TI LMU device model, chip IDs, maximum-current enum, regulator IDs, notifier event, and parent runtime state.

## Important APIs, Types, and Functions

It exports `LMU_EVENT_MONITOR_DONE`, `enum ti_lmu_id`, `enum ti_lmu_max_current`, `enum lm363x_regulator_id`, and `struct ti_lmu` with device, regmap, optional enable GPIO, and blocking notifier head.

## Control Flow

No local code flow. The MFD parent initializes the shared struct, toggles the hardware enable GPIO as needed, and children use regmap plus notifier callbacks for monitor completion events.

## State and Persistence Behavior

`struct ti_lmu` stores runtime parent state and notifier list. Hardware persists lighting and bias configuration in chip registers.

## Dependencies and Integration Points

It integrates TI LMU MFD core with GPIO, regmap, notifier, backlight/LED, regulator, and monitoring subdrivers.

## Risks and Edge Cases

Notifier use requires careful ordering around monitor completion. Optional enable GPIO lifetime and polarity must match hardware. Regulator IDs span multiple chips, so child support must gate unsupported rails.

## Test Signals

Probe tests per LMU ID, notifier registration/notification tests, enable GPIO tests, regulator ID support tests, and child-driver build coverage.
