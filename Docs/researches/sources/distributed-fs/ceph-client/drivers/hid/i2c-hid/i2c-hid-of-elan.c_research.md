<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c

## Purpose
`i2c-hid-of-elan.c` is a Device Tree I2C driver for ELAN and compatible touchscreens using HID-over-I2C. It contributes board/chip-specific power sequencing and timing to the shared I2C-HID core.

## Important APIs, Types, and Functions
`struct elan_i2c_hid_chip_data` describes reset delays, post-power delay, HID descriptor address, optional main regulator name, and whether power must follow backlight enable. `struct i2c_hid_of_elan` embeds `i2chid_ops` plus regulators, reset GPIO, `no_reset_on_power_off`, and chip data. `elan_i2c_hid_power_up` and `elan_i2c_hid_power_down` implement the core callbacks. `i2c_hid_of_elan_probe` gathers resources and calls `i2c_hid_core_probe`.

## Control Flow
Probe allocates wrapper state, installs power callbacks, requests optional reset GPIO initially asserted, reads `no-reset-on-power-off`, obtains mandatory `vccio`, fetches match data, optionally obtains the configured main supply, derives `HID_QUIRK_POWER_ON_AFTER_BACKLIGHT`, then calls the core with the chip-specific descriptor address. Power-up asserts reset, enables main supply if present, enables IO supply, waits post-power delay, deasserts reset, and waits post-reset-on delay. Power-down usually asserts reset, waits optional reset-off delay, and disables IO and main rails; when `no-reset-on-power-off` is set it leaves reset deasserted to avoid wasting power on shared rails.

## State and Persistence Behavior
State is devm-managed for the lifetime of the I2C device. Regulator and GPIO state persists in hardware across core probe, suspend, resume, remove, and shutdown via the common core. The `power_after_backlight` flag becomes a HID initial quirk that makes the core register as a DRM panel follower, deferring probe/resume until panel prepare or enable.

## Dependencies and Integration Points
The driver depends on GPIO consumer APIs, regulator APIs, OF match data, HID quirks, and `i2c_hid_core_pm/remove/shutdown`. Supported compatibles include ELAN, FocalTech, Ilitek, and Parade parts that share the I2C-HID protocol but need different timings.

## Risks and Edge Cases
The code assumes `device_get_match_data` is present for all bound devices. Regulator enable failure after enabling `vcc33` is unwound, but Good power sequencing depends on accurate DT supply names and delays. Panel-follower mode disables wakeup in the core because the panel, not the HID device, owns power state. Incorrect `no-reset-on-power-off` can leave a controller in an undefined state or waste power.

## Test Signals
Validate each compatible with cold boot, suspend/resume, panel blank/unblank, touch input after resume, regulator/GPIO traces, and absence of probe deferrals. For power-after-backlight devices, verify the touchscreen appears only after panel power and that remove/unfollow powers down cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-elan.c -->
