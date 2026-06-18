# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8501.c

Purpose: TI LP8501 nine-channel LED controller glue driver using the LP55xx common framework.

Important APIs/types/functions: `lp8501_cfg` supplies register addresses, max channels, engine busy bit, callbacks, and one program page per engine. `lp8501_post_init_device()` enables the chip, waits for startup, configures clock/charge pump, and applies output power selection. `lp8501_run_engine()` starts common engine execution or stops all engines and clears PWM channels.

Control flow: the I2C driver matches `ti,lp8501` and delegates probe/remove to LP55xx common code. During common initialization, post-init programs LP8501-specific config registers. Runtime LED brightness, current, firmware load, and engine sysfs are handled by shared LP55xx helpers.

State and persistence: state lives in LP55xx common chip/LED objects and LP8501 registers. Program memory is volatile and limited to one page per engine. Platform/DT `pwr-sel`, charge pump, and clock mode determine startup register state.

Dependencies and integration: depends on I2C, LED class, firmware support, OF match data, `leds-lp55xx-common`, and `linux/platform_data/leds-lp55xx.h`.

Risks: wrong `pwr_sel`, charge-pump, or clock-mode data can produce unusable outputs. Engine register shifts default to zero in config, so this relies on LP8501 layout matching common bit macros. Stop uses `lp55xx_stop_all_engine()` rather than selected-engine stop, affecting all engines.

Test signals: probe with DT/platform data, verify current/PWM channels 0-8, firmware load/run/stop, output power selection bits, internal/external clock modes, and behavior when engine busy polling times out.
