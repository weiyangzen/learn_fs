# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5523.c

Purpose: LP5523/LP55231 nine-channel LED engine driver built on the LP55xx common framework, adding program-engine initialization, master fader controls, and LED selftest.

Important APIs/types/functions: `lp5523_cfg` defines register map hooks for common code, including engine busy, program memory, PWM/current bases, master fader, and LED control base. `lp5523_post_init_device()` enables chip, configures charge pump/clock, enables all LEDs, and calls `lp5523_init_program_engine()`. `lp5523_init_program_engine()` writes engine start addresses and MUX helper programs. `lp5523_selftest()` measures VDD and channel ADC values.

Control flow: common `lp55xx_probe` handles device/LED setup. Post-init writes configuration and validates engine status after running temporary programs. Engine sysfs attributes expose mode, load, LED mux, master faders, and selftest. `lp5523_run_engine()` stops engines and turns off channels or starts via common code.

State and persistence: common framework holds locks, channel/current state, firmware, and engine index. Hardware stores program pages, LED mux pages, master fader values, PWM/current, and ADC test state.

Dependencies/integration: LP55xx common framework, firmware loading, I2C, platform data/OF, sysfs, ADC LED-test hardware.

Risks: selftest loop uses `led->chan_nr` while iterating platform channels and increments `led`, so channel/config alignment is critical. Engine initialization returns `-1` instead of a conventional errno on status mismatch. Timing sleeps are hardware-sensitive.

Test signals: post-init engine status mask, engine LED mux sysfs, master fader attributes, external clock selftest, ADC short/open detection thresholds, firmware load/run/stop, and remove through common code.
