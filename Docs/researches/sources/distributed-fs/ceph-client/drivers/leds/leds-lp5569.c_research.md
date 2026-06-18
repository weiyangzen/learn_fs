# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c

Purpose: TI LP5569 nine-channel programmable LED engine driver built on the shared LP55xx common layer. It supplies LP5569-specific register layout, startup programming, master fader attributes, mux handling, and open/short self-test behavior.

Important APIs/types/functions: `lp5569_cfg` is the `struct lp55xx_device_config` consumed by `lp55xx_probe`; `lp5569_post_init_device()` programs MISC, clock, charge pump, enable, and initial engine state; `lp5569_init_program_engine()` loads fixed per-engine mux setup programs; `lp5569_run_engine()` delegates start/stop to common helpers; `lp5569_selftest()`, `lp5569_led_open_test()`, and `lp5569_led_short_test()` expose diagnostics through sysfs. Attribute macros from `leds-lp55xx-common.h` create engine load/mode/leds and master-fader files.

Control flow: module registration binds an I2C driver to `lp55xx_probe`; the common probe allocates chip/LED state, calls LP5569 post-init, registers LEDs, then installs this driver's device attributes. Post-init writes default power/charge-pump settings, selects internal clock output when requested, waits for startup busy to clear, writes engine program start addresses, loads mux helper bytecode for engines 1-3, starts it briefly, checks engine interrupt status, then stops all engines. Brightness/current writes are handled by common LP55xx callbacks.

State and persistence: runtime state lives in `struct lp55xx_chip`, per-engine mode/mux fields, per-LED brightness/current fields, and hardware registers. Firmware patterns are loaded from sysfs or firmware request into volatile program memory. Self-test temporarily changes charge pump, PWM, current, and test bits, then restores LED current and brightness from cached LED state.

Dependencies and integration: depends on I2C SMBus, firmware loader, DT/platform data from `linux/platform_data/leds-lp55xx.h`, LED class and multicolor support, bitfield helpers, and LP55xx common exports. Device match is `ti,lp5569`; user integration is via standard LED class nodes plus engine and selftest sysfs files.

Risks: self-test and mux setup rely on exact register semantics and timing; errors during cleanup writes are ignored. The short-test enable call passes the open-test bit as mask while writing short-test value, which is a suspicious bit-mask interaction worth regression testing against hardware. Engine status validation assumes all three engine interrupt bits assert after the bootstrap program. Firmware/program memory parsing inherits common LP55xx ASCII-hex limitations.

Test signals: probe on real LP5569 with DT children, verify LED brightness/current sysfs, engine load/mode/leds programming, master fader mappings, firmware pattern execution, and `selftest` output with known good/open/shorted LED loads. I2C fault injection should cover post-init failures and cleanup paths.
