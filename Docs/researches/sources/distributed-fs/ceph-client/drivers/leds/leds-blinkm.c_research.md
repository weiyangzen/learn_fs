# sources/distributed-fs/ceph-client/drivers/leds/leds-blinkm.c

## Purpose
Implements support for BlinkM RGB smart LEDs over a simple nonstandard I2C command protocol. Depending on configuration, it registers either three separate red/green/blue LED class devices or one multicolor LED class device, and it also exposes a legacy `blinkm` sysfs group.

## Important APIs, Types, And Functions
`struct blinkm_data` stores I2C client, mutex, LED objects, current/next RGB and HSB values, command argument buffer, address/version/script fields, and mode flags. `struct blinkm_led` stores the client, union of normal/multicolor classdev, and color ID.

Important functions are `blinkm_write`, `blinkm_read`, `blinkm_transfer_hw`, per-color sysfs show/store, `blinkm_set_mc_brightness`, separate color callbacks, `blinkm_detect`, `register_separate_colors`, `register_multicolor`, `blinkm_probe`, and `blinkm_remove`.

## Control Flow
Probe allocates state, initializes defaults and mutex, creates the `blinkm` sysfs group, registers either separate RGB classdevs or one multicolor classdev, and sends stop-script/go-RGB initialization commands. The transfer helper locks the device, prepares command arguments from cached next values, writes commands and optional arguments as byte writes, performs byte reads for read commands, and updates cached current values.

Separate color classdevs update one next color and issue `BLM_GO_RGB`. Multicolor brightness first calls `led_mc_calc_color_components`, copies subLED brightness into next RGB values, and issues `BLM_GO_RGB`. Detect scans address 0x09 and repeatedly balances command/read sequences to avoid confusing the device.

## State And Persistence
The driver maintains shadow current and next RGB/HSB/script fields. Hardware state is inside the BlinkM firmware and command sequencer. Remove unregisters LEDs, fades/resets colors through several I2C commands, and removes sysfs.

## Dependencies And Integration Points
Depends on I2C SMBus byte operations, LED class, optional multicolor LED class, sysfs, runtime PM headers, and I2C legacy detection using `I2C_CLASS_HWMON`.

## Risks
The BlinkM protocol requires balanced sequences; incomplete write/read pairs can leave the device confused. In multicolor mode, `blinkm_remove` still unregisters three union members as plain classdevs, which is a risk area because only one multicolor classdev is registered. `register_multicolor` returns zero even after a registration error path, which can mask failures. Several advanced commands are explicitly unimplemented.

## Test Signals
Test detection at address 0x09, sysfs RGB show/store, test sequence, separate-color registration, multicolor registration with `multi_intensity`, I2C error handling for command sequences, remove fade/reset behavior, and configuration differences with `CONFIG_LEDS_BLINKM_MULTICOLOR`.
