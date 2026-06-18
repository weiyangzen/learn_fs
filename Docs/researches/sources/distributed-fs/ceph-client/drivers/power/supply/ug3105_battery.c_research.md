# sources/distributed-fs/ceph-client/drivers/power/supply/ug3105_battery.c

## Purpose
`ug3105_battery.c` is an I2C battery monitor driver for the uPI uG3105. It uses voltage/current ADC readings with `adc-battery-helper` to expose battery properties, but intentionally does not use the coulomb counter because Linux cannot guarantee reads while powered off or suspended.

## Important APIs, Types, And Functions
`struct ug3105_chip` embeds `struct adc_battery_helper` as its first member, stores the I2C client, power supply, and ADC scaling factors. `ug3105_read_word()` wraps SMBus word reads. `ug3105_get_voltage_and_current_now()` reads voltage and signed current registers and converts them to microvolts/microamps. `ug3105_start()` enters run mode and resets the coulomb counter; `ug3105_stop()` enters standby. Probe initializes scale factors and calls `adc_battery_helper_init()`.

## Control Flow
Probe allocates state, starts the chip, reads optional `upisemi,rsns-microohm` with a default 10 mOhm sense resistor, computes voltage/current units, registers `ug3105_battery`, initializes the helper, and stores client data. Suspend calls helper suspend then stops the chip; resume restarts the chip and resumes helper polling. Remove and shutdown stop the chip.

## State, Persistence, And Dependencies
Driver state is scale factors and helper state. Hardware state is the mode register and reset coulomb counter. The coulomb counter is reset at start and not accumulated. Dependencies are I2C SMBus, `adc-battery-helper`, power-supply core, firmware property reading, and PM ops.

## Integration Points
The descriptor delegates property implementation to `adc_battery_helper_get_property()` and external-power handling to `adc_battery_helper_external_power_changed()`. It binds via I2C id `"ug3105"` and has PM hooks.

## Risks
The voltage scaling includes a documented empirical factor of 10; board-specific validation is important. Resetting the coulomb counter on each start loses accumulated charge data by design. `ug3105_start()`/`stop()` ignore SMBus write failures. The module author string is missing a closing angle bracket, a metadata issue rather than runtime behavior.

## Test Signals
Test probe with default and custom sense resistor, signed current conversion, voltage scaling against measured values, helper property polling, suspend/resume stop/start behavior, remove/shutdown standby writes, and I2C read failures propagated through property reads.
