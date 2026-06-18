# sources/distributed-fs/ceph-client/drivers/power/supply/adc-battery-helper.h

## Purpose
`adc-battery-helper.h` declares the public interface and state structure for the ADC battery helper. It lets simple battery drivers embed the helper, expose the standard helper-backed property list, and reuse common get-property, external-power, and PM callbacks.

## Important APIs, Types, And Functions
- `ADC_BAT_HELPER_MOV_AVG_WINDOW_SIZE` fixes OCV and internal-resistance moving-average windows at eight samples.
- `adc_battery_helper_get_func` is the required combined voltage/current callback. The combined callback is intentional so clients can sample voltage and current close together.
- `struct adc_battery_helper` contains the power-supply pointer, optional charge-finished GPIO, delayed work, mutex, callback, OCV/resistance sample arrays, poll counters/indexes, last voltage/current, capacity, status, and supplied flag.
- `adc_battery_helper_properties[]` and `ADC_HELPER_NUM_PROPERTIES` describe the exported property list contract.
- `adc_battery_helper_init()`, `adc_battery_helper_get_property()`, `adc_battery_helper_external_power_changed()`, `adc_battery_helper_suspend()`, and `adc_battery_helper_resume()` are the exported helper functions.

## Control Flow
Client drivers embed `struct adc_battery_helper`, register their power supply, call `adc_battery_helper_init()`, and either use the helper callbacks directly or delegate selected properties to them. The PM and property helpers assume they can retrieve the helper from driver data.

## State And Persistence
The header defines only in-memory state. Persistence is left to the client device and battery-info firmware data. The moving average arrays and counters are reset by helper initialization/resume logic in the C file.

## Dependencies And Integration Points
The header forward-declares `struct power_supply` and `struct gpio_desc`, includes mutex and workqueue types, and relies on power-supply property enums through users including power-supply headers before or through the C implementation. It is intended for local power-supply drivers in the same subsystem.

## Risks
- The comment states the helper must be the first member of client data for direct callback use. This is an ABI-like layout contract not enforced by the compiler.
- `ADC_HELPER_NUM_PROPERTIES` must stay synchronized with `adc_battery_helper_properties[]`; the C file uses `static_assert()` to catch mismatches.
- The callback signature uses plain `int *volt` and `int *curr`; clients must honor microvolt and microampere units expected by the implementation.

## Test Signals
- Build coverage catches property-count mismatches through the C file static assertion.
- Client-driver tests should verify driver data layout, unit conventions, and direct callback use for get-property and suspend/resume.
