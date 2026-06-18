# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctmg110_ts.c

Purpose: `cy8ctmg110_ts.c` is an older Cypress CY8CTMG110 I2C touchscreen driver. It reports single-touch absolute X/Y coordinates and `BTN_TOUCH`, supports an optional reset GPIO, and places the controller in and out of sleep across lifecycle events.

Important APIs, types, and functions: `struct cy8ctmg110` stores the input device, physical path, I2C client, and reset GPIO. `cy8ctmg110_power()` drives reset asserted/deasserted. `cy8ctmg110_write_regs()` and `cy8ctmg110_read_regs()` implement small I2C register transactions. `cy8ctmg110_touch_pos()` reads nine bytes starting at `CY8CTMG110_TOUCH_X1`, uses the ninth byte as finger count, and decodes big-endian X/Y. `cy8ctmg110_set_sleepmode()` writes wake/sleep timing values. IRQ, suspend, resume, and devm shutdown all delegate to these helpers.

Control flow: probe checks adapter support, allocates state and input, configures fixed coordinate ranges 0..759 and 0..465, requests an optional reset GPIO initially asserted, powers on and exits sleep mode, installs a devm shutoff action, requests a oneshot threaded IRQ, registers input, and stores client data. Each IRQ reads the current position and reports either release or one contact.

State and persistence: the driver keeps no persistent calibration or firmware state. Runtime state is the reset GPIO level, controller sleep mode, and input event state. Devm cleanup sleeps and resets the device.

Dependencies and integration points: it integrates with I2C, GPIO descriptors, threaded IRQs, PM sleep callbacks, and the legacy input ABS single-touch API. It has no OF match table in this file, only an I2C ID table named `cy8ctmg110`.

Risks: `cy8ctmg110_read_regs()` treats any nonnegative `i2c_transfer()` result as success, without checking that both messages completed. The functionality check asks for SMBus word reads even though the driver uses raw I2C transfers. Coordinates are fixed in code and not corrected through `touchscreen_parse_properties()`. `BUG_ON(len > 5)` is harsh for a helper that could return `-EINVAL`.

Test signals: exercise reset GPIO polarity, sleep/resume commands, IRQ read error handling, pen-up reporting when finger count is zero, fixed range reporting, and suspend/resume with wakeup disabled.
