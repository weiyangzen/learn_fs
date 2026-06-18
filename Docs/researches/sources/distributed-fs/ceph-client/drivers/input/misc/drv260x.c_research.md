<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c

## Purpose
`drv260x.c` is an I2C force-feedback haptics driver for TI DRV2604/2604L/2605/2605L devices. It exposes a memless `FF_RUMBLE` input device and translates rumble magnitude into real-time playback register writes.

## Important APIs, Types, and Functions
`struct drv260x_data` stores the input device, I2C client, regmap, work item, optional enable GPIO, regulator, magnitude, selected mode/library, and actuator voltage settings. `drv260x_init()` applies voltage registers and mode-specific LRA/ERM calibration or LRA no-cal initialization. `drv260x_worker()` enables the GPIO, waits for the data-sheet communication delay, sets real-time playback mode, and writes magnitude. `drv260x_haptics_play()` scales strong or weak rumble magnitude into an 8-bit register value.

## Control Flow
Probe reads required `mode` and `library-sel` properties, validates LRA/ERM library combinations, reads optional voltage properties, obtains and enables `vbat`, installs a devm power-off action, obtains optional enable GPIO, allocates and registers a memless FF input device, initializes I2C regmap, runs chip initialization, then registers input. Calibration modes write calibration register patches and poll `GO` for completion with a five-second timeout; no-cal mode writes init registers and returns without setting `GO`.

## State and Persistence Behavior
The current magnitude is stored in memory until the work item writes it to `DRV260X_RT_PB_IN`. Regmap cache is disabled, so hardware registers are the active state. Suspend, resume, and close coordinate with `input_dev->mutex`: suspend enters standby, disables GPIO and regulator; resume reverses that if the input device is enabled; close cancels work, writes standby, and disables the GPIO.

## Dependencies and Integration Points
The driver integrates with I2C IDs, OF/ACPI match tables, regmap, regulator, optional GPIO, input FF memless callbacks, and PM sleep hooks. Device-tree bindings come from `dt-bindings/input/ti-drv260x.h`.

## Risks and Test Signals
Risks include invalid property combinations, failed auto-calibration, regulator/GPIO sequencing, magnitude writes racing with suspend/close, and no explicit stop register write on zero magnitude beyond writing zero RTP. Tests should cover property validation, voltage conversion, calibration timeout, rumble scaling, work execution after zero and nonzero effects, and suspend/resume while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c -->
