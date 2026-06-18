<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c

## Purpose

`airoha_thermal.c` implements a thermal-zone driver for the Airoha EN7581 thermal sensor. It reads an ADC-backed diode sensor through SCU/syscon registers, calibrates raw ADC values from efuse data or a live fallback sample, registers with the thermal OF framework, programs hardware trip monitoring, and handles threshold interrupts.

## Important APIs, Types, and Functions

`struct airoha_thermal_priv` stores the PTP thermal MMIO base, SCU regmap, SCU ADC resource, registered thermal zone, and calibration fields (`init_temp`, slope, offset). Conversion macros `TEMP_TO_RAW()` and `RAW_TO_TEMP()` translate between millicelsius-like thermal values and ADC raw codes using slope/init/offset constants.

Sensor helpers are `airoha_get_thermal_ADC()`, `airoha_init_thermal_ADC_mode()`, `airoha_thermal_get_temp()`, `airoha_thermal_set_trips()`, `airoha_thermal_irq()`, `airoha_thermal_setup_adc_val()`, and `airoha_thermal_setup_monitor()`. Probe maps resources, obtains the `airoha,chip-scu` syscon phandle, requests the IRQ, configures monitor/ADC/calibration, registers the thermal zone, and enables high/low offset interrupts.

## Control Flow

Probe maps the thermal monitor registers, locates the chip SCU regmap and resource, requests a threaded IRQ, configures AHB monitor access to the ADC output register, switches the SCU thermal ADC mux to diode1, waits for ADC enable, derives calibration from efuse fields or fallback raw reading, registers an OF thermal zone, then enables high/low interrupts. `get_temp` reads six ADC samples, drops min and max, averages the remaining four, and converts to temperature. `set_trips` clamps requested high/low thresholds, writes raw offset registers, and enables sensor0 monitoring. The IRQ handler reads status, maps high-offset status to `THERMAL_TRIP_VIOLATED` and low-offset status to an unspecified event, clears status, and updates the thermal zone.

## State and Persistence Behavior

Runtime state is device-managed `struct airoha_thermal_priv`, MMIO register programming, SCU mux/protect state during ADC setup, calibration values, and thermal-zone registration. No persistent state is written; efuse calibration is read-only hardware state.

## Dependencies and Integration Points

The driver depends on platform devices, OF resources/phandles, MFD syscon/regmap, MMIO accessors, threaded IRQs, thermal OF zone registration, and EN7581 register layout. It is selected by `CONFIG_AIROHA_THERMAL` in Kconfig and built from the thermal Makefile.

## Risks and Edge Cases

`airoha_thermal_set_trips()` appears to clamp `low` using `high` as the input argument, which likely corrupts low-threshold programming when only a low trip is supplied. `airoha_thermal_setup_monitor()` writes `FIELD_PREP(EN7581_FILT_INTERVAL, 379)` for the sensor interval instead of using `EN7581_SEN_INTERVAL`, so the intended 379 sample interval may not be programmed. Several comments document hardware bit swaps relative to documentation; regressions can be introduced by "correcting" them without hardware validation. `of_address_to_resource()` return value is ignored, so an invalid SCU resource can be used for ADC valid address programming. Missing efuse calibration falls back to current ADC reading, making absolute temperature dependent on boot conditions.

## Test Signals

Tests should cover probe with missing/malformed `airoha,chip-scu`, IRQ request failure, efuse present and absent paths, raw/temp conversion boundaries, six-sample averaging, high and low trip programming separately and together, IRQ status high/low/noise cases, register programming for monitor intervals and ADC addresses, suspend/resume expectations if added later, and hardware validation for documented swapped bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c -->
