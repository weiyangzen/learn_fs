
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-gpio.h

## Purpose
This header defines platform data for the GPIO bit-banged I2C adapter driver.

## Important APIs And Types
`struct i2c_gpio_platform_data` contains `udelay`, `timeout`, and bitfields describing SDA/SCL electrical behavior: open-drain, output-only, and no-pullup for each line. The comment states SCL frequency is approximately `500 / udelay` kHz.

## Control Flow, State, And Persistence
The i2c-gpio driver uses this data to choose bit timing, clock-stretch timeout, and whether lines can be released/read for open-drain semantics. Runtime state is adapter transfer sequencing over GPIOs; no persistence is defined.

## Dependencies And Integration Points
It integrates board-specific GPIO wiring with the Linux I2C adapter layer and GPIO API.

## Risks And Test Signals
Risks include configuring push-pull as open-drain or vice versa, missing pull-ups, output-only lines that prevent proper arbitration/readback, and bad timing values. Test signals include I2C bus scan, transfers with clock-stretching slaves, waveform timing, no-pullup behavior, and timeout handling when SCL is held low.
