<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c

## Purpose
`i2c-hid-of-goodix.c` is a Device Tree wrapper for Goodix touchscreens that speak HID-over-I2C. It handles Goodix-specific regulator and reset timing before delegating protocol handling to the shared core.

## Important APIs, Types, and Functions
`struct goodix_i2c_hid_timing_data` stores post-power and post-reset delays. `struct i2c_hid_of_goodix` embeds `i2chid_ops`, `vdd`, `vddio`, optional reset GPIO, `goodix,no-reset-during-suspend`, and timing match data. `goodix_i2c_hid_power_up`, `goodix_i2c_hid_power_down`, and `i2c_hid_of_goodix_probe` form the driver’s behavior.

## Control Flow
Probe allocates state, installs power callbacks, requests reset GPIO asserted, obtains `vdd` and `mainboard-vddio`, reads the `goodix,no-reset-during-suspend` property, stores match timing data, then calls `i2c_hid_core_probe` with HID descriptor address `0x0001`. Power-up optionally asserts reset when no-reset-during-suspend is active, enables `vdd`, enables `vddio`, waits post-power delay, deasserts reset, then waits post-reset delay. Power-down asserts reset unless the no-reset property says suspend should preserve reset state, then disables `vddio` and `vdd`.

## State and Persistence Behavior
All software state is devm-managed and lives as long as the I2C client. Hardware state persists in regulators and reset GPIO across the core’s probe, PM, remove, and shutdown calls. The wrapper supplies no private shutdown or restore callbacks, so all higher-level HID and power transitions are controlled by `i2c-hid-core.c`.

## Dependencies and Integration Points
The file depends on regulator, GPIO, OF match, I2C, PM, and the common I2C-HID core. It currently binds `goodix,gt7375p` with a 10 ms post-power delay and 180 ms reset-deassert delay.

## Risks and Edge Cases
If enabling `vddio` fails after `vdd` succeeds, the current code returns without disabling `vdd`, which is a power-leak risk on probe/resume failure. The no-reset-during-suspend behavior is board-sensitive: preserving reset may be required for wake/resume but may also leave stale controller state. The hard-coded descriptor address assumes all bound Goodix devices use the same register.

## Test Signals
Check cold boot and resume input events, regulator unwind on induced failures, reset GPIO polarity, descriptor fetch at `0x0001`, and long suspend/resume cycles on boards with and without `goodix,no-reset-during-suspend`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of-goodix.c -->
