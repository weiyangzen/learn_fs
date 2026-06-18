# sources/distributed-fs/ceph-client/net/rfkill/Kconfig

## Purpose
Declares build-time configuration for the RF switch subsystem, optional LED/input integrations, and the generic GPIO rfkill platform driver.

## Important APIs, Types, and Functions
Defines `RFKILL` as tristate, `RFKILL_LEDS` as a dependent bool, `RFKILL_INPUT` as an optional/default input bridge, and `RFKILL_GPIO` as a tristate GPIO driver. It uses dependencies on `LEDS_TRIGGERS`, `INPUT`, `GPIOLIB`, and `COMPILE_TEST`.

## Control Flow
Kconfig selection controls which objects the Makefile builds. Enabling `RFKILL` builds the core. LED trigger support defaults on when compatible. Input support defaults on outside expert mode when input is available. GPIO support remains opt-in and depends on GPIO library or compile testing.

## State and Persistence
No runtime state is present. Configuration choices persist in the kernel build configuration.

## Dependencies and Integration
Connects rfkill to the kernel device model, input layer, LED trigger framework, and GPIO platform driver build.

## Risks and Test Signals
Risks include invalid dependency combinations hiding expected functionality or building optional integration without its provider. Test signals are Kconfig dependency resolution for built-in/module combinations, allmodconfig coverage, and `RFKILL_INPUT`/`RFKILL_LEDS` matching their provider availability.
