# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5521.c

Purpose: LP5521 three-channel LED engine driver implemented as a chip-specific configuration for the shared LP55xx common framework.

Important APIs/types/functions: `lp5521_cfg` supplies register addresses, reset/enable values, max channels, brightness/current callbacks, firmware callback, run-engine callback, and sysfs group to `lp55xx_probe()`. `lp5521_post_init_device()` verifies reset state, writes direct-control mode, configures clock/charge pump, clears PWM, and enables run-program state. `lp5521_run_engine()` starts/stops LP55xx engines. `lp5521_selftest()` checks external clock status.

Control flow: I2C probe is delegated to `lp55xx_probe` using match/id `driver_data`. Common code handles LED parsing/registration. Post-init is called by common code after reset. Engine sysfs attributes expose engine mode/load, and firmware loading uses the common callback.

State and persistence: common LP55xx structures own channel state, firmware, lock, and platform data. This file defines chip-specific hardware register state and timing waits. Hardware program memory and PWM registers persist until reset or overwritten.

Dependencies/integration: `leds-lp55xx-common.h`, firmware loader, LP55xx platform data/OF, I2C, sysfs attributes, mutex guard in selftest.

Risks: reset verification depends on reading default R current register. External clock selftest only fails when ext clock was requested. Engine timing waits are required after mode/enable writes.

Test signals: common probe with three channels, post-init default register read, internal/external clock config, engine mode/load sysfs, firmware load/run/stop, and selftest output.
