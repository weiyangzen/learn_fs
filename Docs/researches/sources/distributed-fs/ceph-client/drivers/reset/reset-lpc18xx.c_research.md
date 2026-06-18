# sources/distributed-fs/ceph-client/drivers/reset/reset-lpc18xx.c

Purpose: NXP LPC18xx/43xx Reset Generation Unit provider and restart handler.

Important APIs/types/functions: `struct lpc18xx_rgu_data`, `lpc18xx_rgu_restart()`, `lpc18xx_rgu_setclear_reset()`, assert/deassert/reset/status ops, and `lpc18xx_rgu_probe()`.

Control flow: probe maps the RGU, enables `reg` and `delay` clocks, calculates reset delay from clock rates, registers 64 resets, and registers a restart sys-off handler. Set/clear preserves active M0 core reset bits by reading inverted active status before writing control registers. `.reset` asserts, delays, and explicitly deasserts only M0 core reset lines.

State and persistence: hardware status/control registers hold state; clocks remain enabled through devm lifetime; spinlock protects updates.

Dependencies and integration: built-in platform driver, clocks, MMIO, restart API, reset framework.

Risks and test signals: preserving M0 reset state is subtle; incorrect delay calculation can under-reset. Test clock failure/rate-zero paths, M0 resets, restart path, status polarity, and concurrent operations.
