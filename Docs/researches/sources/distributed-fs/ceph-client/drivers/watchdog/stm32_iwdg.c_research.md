# sources/distributed-fs/ceph-client/drivers/watchdog/stm32_iwdg.c

## Purpose
`stm32_iwdg.c` drives STM32 independent watchdog hardware. It computes prescaler/reload values from the LSI clock, optionally uses a peripheral clock and early wakeup interrupt on STM32MP1, supports pretimeout notification, and can take over boot-enabled watchdogs.

## Important APIs, types, and functions
`struct stm32_iwdg_data` describes variant features; `struct stm32_iwdg` stores watchdog, variant data, registers, clocks, and LSI rate. Register helpers are `reg_read()` and `reg_write()`. Watchdog ops are `stm32_iwdg_start()`, `stm32_iwdg_ping()`, `stm32_iwdg_set_timeout()`, and `stm32_iwdg_set_pretimeout()`. Setup helpers include `stm32_iwdg_clk_init()`, `stm32_iwdg_irq_init()`, `stm32_iwdg_isr()`, and `stm32_iwdg_probe()`.

## Control flow
Probe selects variant from DT, maps registers, enables clocks, initializes min timeout and `max_hw_heartbeat_ms`, requests optional early-wakeup IRQ and wakeup-source handling, applies nowayout, reads timeout from DT, and if boot-enabled handling is configured, starts hardware with deterministic values and sets `WDOG_HW_RUNNING`. Start enables write access, chooses a power-of-two prescaler, writes prescaler/reload/early-wakeup values, enables the peripheral, waits for PVU/RVU bits to clear, then reloads.

## State and persistence behavior
There is no stop operation because independent watchdogs generally cannot be stopped after start. Timeout and pretimeout live in core fields; hardware registers retain the last prescaler/reload/window/early-wakeup settings until reset.

## Dependencies and integration points
The driver depends on DT compatibles `st,stm32-iwdg` and `st,stm32mp1-iwdg`, clocks `lsi` and optional `pclk`, optional IRQ and wakeup integration, polling helpers, and watchdog core.

## Risks and test signals
Risks include prescaler/reload rounding errors, no ability to stop after bad configuration, pretimeout defaulting to three quarters of timeout, and rate-dependent min/max constraints. Tests should cover both variants, missing clocks, optional IRQ absent/present, wakeup-source setup, timeout and pretimeout changes while active, boot-enabled takeover, status polling timeout, and reload writes.
