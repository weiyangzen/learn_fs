# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sy7802.c

## Purpose
Implements the Silergy SY7802 dual-channel flash LED controller as an I2C/regmap LED flash-class driver. It exposes each described LED output, including a joint two-channel mode, as `struct led_classdev_flash` with torch brightness, flash brightness, strobe, timeout, and fault reporting.

## Important APIs, Types, And Functions
`struct sy7802` stores the regmap, enable GPIO, VIN regulator, shared mutex, active channel bitmaps, and flexible array of `struct sy7802_led`. Each `struct sy7802_led` embeds `struct led_classdev_flash`, a backpointer, and `led_id`.

The LED-class callbacks are `sy7802_torch_brightness_set`, `sy7802_flash_brightness_set`, `sy7802_strobe_set`, `sy7802_strobe_get`, `sy7802_timeout_set`, and `sy7802_fault_get`, collected in `sy7802_flash_ops`. Probe support is split across `sy7802_init_flash_properties`, `sy7802_led_register`, `sy7802_probe_dt`, `sy7802_chip_check`, and power helpers.

## Control Flow
`sy7802_probe` validates there are one or two child LED nodes, allocates a sized `struct sy7802`, obtains `enable` GPIO and `vin` regulator, enables the regulator, initializes mutex and regmap, parses/registers child LEDs, enables the chip GPIO, and verifies `SY7802_REG_DEV_ID`. Child parsing reads `led-sources`, rejects duplicated physical channels, converts two sources into `SY7802_LED_JOINT`, initializes flash settings, and registers through `devm_led_classdev_flash_register_ext`.

Torch writes first reject active strobe use, compute a temporary torch-use bitmap, disable torch mode to apply current, program channel or joint current bits, then update enable/mode bits. Strobe does the symmetric operation while rejecting active torch use. Fault reads map SY7802 status bits into generic `LED_FAULT_*` values.

## State And Persistence
The persistent software state is `fled_strobe_used`, `fled_torch_used`, and `leds_active` under `chip->mutex`; hardware state lives in cached regmap registers and the enable GPIO/regulator. Fault reads are destructive because reading `SY7802_REG_FLAGS` clears status. Devm cleanup disables the chip GPIO and regulator.

## Dependencies And Integration Points
Depends on I2C, regmap with MAPLE cache, GPIO consumer, regulator consumer, OF child nodes, and `led-class-flash`. Device tree compatible is `silergy,sy7802`; child nodes provide naming metadata and `led-sources`.

## Risks
Torch and strobe exclusion relies on shared bitmaps, so missed locking would cause invalid mixed modes. Joint output mode writes both channels and can conflict with duplicate `led-sources` if validation regresses. The probe sequence registers LEDs before enabling and checking the chip ID; failures are devm-cleaned, but a bad bus/device can still exercise registration paths before final ID rejection. Fault reads clear hardware state, so polling `flash_fault` consumes evidence.

## Test Signals
Build with the flash LED class and I2C/regmap enabled. Runtime signals include successful probe on `silergy,sy7802`, correct sysfs files for flash brightness/strobe/timeout/fault, rejection of torch while flash is active and vice versa, correct joint channel behavior, cleanup disabling VIN/GPIO, and expected fault-bit translation after induced timeout or undervoltage events.
