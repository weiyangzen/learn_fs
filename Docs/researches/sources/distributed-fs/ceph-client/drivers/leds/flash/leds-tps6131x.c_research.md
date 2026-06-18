# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-tps6131x.c

## Purpose
Implements the Texas Instruments TPS61310/TPS61311 I2C flash LED controller. The driver exposes one flash-class LED composed from one to three hardware channels and also registers a V4L2 flash device for camera integration, including external strobe control.

## Important APIs, Types, And Functions
`struct tps6131x` owns device state: regmap, optional reset GPIO, register lock, torch watchdog delayed work, channel enable booleans, parsed current/timeout limits, LED fwnode, `struct led_classdev_flash`, and `struct v4l2_flash`.

Key operations are `tps6131x_brightness_set` for torch current, `tps6131x_strobe_set`, `tps6131x_flash_brightness_set`, `tps6131x_flash_timeout_set`, `tps6131x_strobe_get`, and `tps6131x_flash_fault_get`. `tps6131x_timer_configs` maps supported flash timeouts, while `tps6131x_parse_node` validates `led-sources`, current limits, and timeout properties.

## Control Flow
Probe allocates state, initializes a mutex and torch-refresh delayed work, parses the single child LED node, initializes regmap, obtains optional reset GPIO, resets the chip, writes channel/thermal/current-limit configuration, registers the LED flash class device, and initializes V4L2 flash support.

Torch brightness converts the LED framework brightness units into hardware 25 mA steps, distributes current across enabled channels with special handling for channels 1 and 3 sharing a register, writes register 0, enters torch or shutdown mode, and schedules a refresh before the approximate 13 second watchdog expires. Flash brightness similarly distributes current between channel 2 and channels 1/3, writing registers 1 and 2. Timeout selection chooses the nearest supported table entry and writes STIM/range bits.

## State And Persistence
Mutable state includes parsed current steps, channel booleans, `fled_cdev` setting values, and delayed torch refresh work. Register access to interdependent registers 0-3 is serialized by `lock`. Regmap marks registers 3, 4, and 6 precious because they contain read-to-clear/status fields, and status reads bypass cache. Remove releases V4L2 flash and cancels delayed work.

## Dependencies And Integration Points
Depends on I2C, GPIO, regmap, LED flash class, fwnode properties, and `media/v4l2-flash-led-class.h`. Device tree uses compatible `ti,tps61310`; the child node supplies `led-sources`, `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`.

## Risks
Current distribution is subtle because channel 1 and 3 share controls while channel 2 has higher flash capacity. Bad DT current limits are rejected, but an incorrect board description can still underuse hardware. The torch watchdog depends on delayed work; failure to cancel/refresh can leave the controller shutting down unexpectedly. Fault/status reads bypass cache because normal regmap reads would be unsafe for precious registers.

## Test Signals
Test with LED flash sysfs and V4L2 controls. Probe should reset and initialize without regmap errors, V4L2 flash registration should succeed, torch should remain on past 13 seconds due to refresh work, flash timeouts should snap to supported values, and fault bits should map to timeout, over-temperature, short-circuit, undervoltage, and LED over-temperature. Removal should cancel work without late I2C accesses.
