# sources/distributed-fs/ceph-client/include/linux/regulator/driver.h

## Purpose

`driver.h` declares the regulator provider-side API. It is used by PMIC, fixed, GPIO, and SoC regulator drivers to describe rails, implement operations, register regulators, use common regmap helpers, report hardware errors, and participate in coupling.

## Important APIs, Types, and Functions

Status and severity enums include `enum regulator_status` and `enum regulator_detection_severity`. Voltage helper macros wrap `LINEAR_RANGE`. `struct regulator_ops` is the main operation table: list/map/set/get voltage, current and input current limits, protection thresholds, active discharge, enable/disable/is_enabled, mode, error flags, enable/ramp/settling timing, soft start, status, optimum mode/load, bypass, suspend settings, resume, and pull-down.

`struct regulator_desc` is the static descriptor: names, OF matching/parsing callbacks, IDs, ops, IRQ, type, owner, voltage/current tables and linear ranges, regmap registers/masks for selectors/enables/bypass/discharge/soft-start/pull-down/ramp, enable/off-on timing, polling timing, and OF mode mapping. `struct regulator_config` supplies runtime data: device, init data, private driver data, OF node, regmap, and enable GPIO.

Runtime core structures include `struct regulator_err_state`, `struct regulator_irq_data`, `struct regulator_irq_desc`, `struct coupling_desc`, and the core-owned `struct regulator_dev`. Registration and helper APIs include `regulator_register()`, `devm_regulator_register()`, `regulator_unregister()`, notifier calls, IRQ helpers, `rdev_get_*()`, mapping/listing helpers, regmap-backed get/set/enable/bypass/discharge/current/ramp helpers, `regulator_find_closest_bigger()`, and `regulator_sync_voltage_rdev()`.

## Control Flow

A provider defines descriptors and ops, builds a `regulator_config`, and registers each rail. The core combines descriptor capabilities with board constraints from machine/OF data, creates `regulator_dev`, handles consumer requests, serializes operations through regulator mutexes, and calls provider ops or common regmap helpers. Error IRQ helpers map hardware status to regulator events/errors and may disable/re-enable IRQs, retry reads, or invoke a protection callback/poweroff on repeated fatal failures.

Regmap helper flows use descriptor registers and masks to map selectors, enable bits, bypass bits, discharge bits, ramp delay tables, and current-limit tables into hardware writes. Coupled regulators coordinate voltage changes through `coupling_desc` and coupler callbacks.

## State and Persistence Behavior

`struct regulator_dev` carries core runtime state: exclusive/open/use/bypass counts, global and consumer lists, coupling, notifier chain, ww mutex owner, module owner, device objects, constraints, supply tree link, regmap, delayed disable work, driver data, debugfs, enable GPIO state, last-off timestamp, cached errors, and power budget accounting. Hardware register state may persist through suspend/reset depending on PMIC behavior.

## Dependencies and Integration Points

The header depends on device model, linear ranges, notifier, consumer API, ww mutexes, GPIO descriptors, regmap, debugfs, workqueues, and module ownership. It integrates provider drivers with consumers, OF constraints, machine constraints, regmap, IRQ core, poweroff protection, suspend/resume, and coupling.

## Risks

Descriptor mistakes are high impact: wrong masks/registers, voltage tables, selector ranges, enable polarity, ramp units, or timing can damage hardware or break boot. Provider ops must respect constraints and return negative errno consistently. IRQ helper callbacks must initialize error/notification fields correctly. Direct access to `regulator_dev` outside the core is forbidden except narrowly documented notification injection. Coupling and ww mutex use can deadlock if bypassed.

## Test Signals

Tests should cover provider registration/unregistration, descriptor validation, voltage mapping/listing/set/get, regmap enable/disable/bypass/discharge/ramp/current helpers, suspend states, delayed disable/off-on timing, notifier/event mapping, IRQ retry/fatal behavior, coupling balance, debugfs, and consumer API integration.
