# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-qcom-flash.c

## Purpose
This platform driver supports Qualcomm SPMI PMIC multi-channel flash LED modules. It handles three- and four-channel hardware variants, multi-channel LEDs, torch and flash current programming, thermal derating, fault reporting, and optional V4L2 flash integration.

## Important APIs, Types, and Functions
`struct qcom_flash_data` stores shared module state, regmap fields, lock, hardware type, total current budget, channel count, revision, and V4L2 handles. `struct qcom_flash_led` stores per-LED flash class device, channel IDs, max currents/timeouts, cached flash settings, current allocation, and enable state. Key helpers are `set_flash_module_en()`, `update_allowed_flash_current()`, `set_flash_current()`, `set_flash_timeout()`, and `set_flash_strobe()`. LED callbacks include `qcom_flash_led_brightness_set()`, `qcom_flash_brightness_set()`, `qcom_flash_timeout_set()`, `qcom_flash_strobe_set()`, `qcom_flash_strobe_get()`, and `qcom_flash_fault_get()`.

## Control Flow
Probe gets the parent regmap and register base, verifies module type/subtype, selects the proper reg-field table, adjusts fields by base address, allocates regmap fields, counts child LEDs, and registers each child. Each child parses 1-based `led-sources`, torch current, optional flash current/timeout, and registers a flash class device. Torch brightness disables current strobe state, derates requested current based on current thermal status and shared current budget, programs current and timeout, enables the module, and enables software strobe. Flash strobe follows a similar sequence with flash current and safety timer.

## State and Persistence
Shared state tracks `chan_en_bits`, total allocated current in mA, per-LED current allocation, and per-LED enabled state. These are runtime-only and protected by `flash_data->lock` for shared budget/module updates. LED class settings cache requested flash current and timeout before strobe.

## Dependencies and Integration Points
The driver depends on a parent SPMI PMIC regmap, firmware `reg` base and child `led-sources`, LED flash class, regmap fields, and optional V4L2 flash. It binds `qcom,spmi-flash-led`.

## Risks and Edge Cases
The V4L2 release loops index `v4l2_flash[leds_count]` before decrementing, which appears off by one after `leds_count` has been incremented; cleanup should be reviewed. Thermal derating temporarily lowers threshold registers and must always restore defaults on errors. Channel IDs in firmware are 1-based, while internal regfield IDs are 0-based. Shared total current limiting can reduce a strobe to zero current when thermal/current budget is exhausted. `FIELD_PREP()` is used with single-bit macros rather than masks in strobe config, which should be verified.

## Test Signals
Test PM8150/Pmi8998 three-channel and four-channel subtype detection, multi-channel current splitting, torch clamp programming, thermal derating status paths, simultaneous LEDs sharing the total current budget, V4L2 external strobe, fault reporting for short/thermal/over-current/input-voltage/timeout, and probe/remove cleanup under partial registration failure.
