# sources/distributed-fs/ceph-client/include/linux/regulator/fixed.h

## Purpose

`fixed.h` declares platform data and helper registration for fixed-voltage regulators, including always-on dummy fixed supplies.

## Important APIs, Types, and Functions

`struct fixed_voltage_config` contains supply name, input supply, output microvolts, startup/off-on delays, boot enable state, and regulator init data. `regulator_register_always_on()` registers an always-on fixed regulator when regulator support is enabled; otherwise it returns `NULL`. `regulator_register_fixed()` is a macro alias using the `"fixed-dummy"` name and zero microvolts.

## Control Flow

Board code can create a platform device for an always-on or fixed dummy supply. The fixed regulator driver consumes the config, registers a regulator with fixed voltage and optional startup timing, and exposes it to consumers.

## State and Persistence Behavior

The header defines static config. Runtime state includes platform device lifetime, regulator core state, optional GPIO/driver state in implementation, and boot-on/always-on constraints.

## Dependencies and Integration Points

It uses `regulator_init_data`, `regulator_consumer_supply`, and platform devices. It integrates with board files and fixed regulator consumers.

## Risks

Using a dummy fixed regulator can mask missing real supply modeling. Wrong microvolt values or boot-on flags can cause consumers to skip required sequencing.

## Test Signals

Tests should verify always-on registration, consumer mapping, fixed voltage reporting, startup/off-on delays, and disabled-regulator stub behavior.
