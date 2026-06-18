# sources/distributed-fs/ceph-client/drivers/char/hw_random/stm32-rng.c

Purpose: STM32/STM32MP RNG driver with clock limiting, health-test configuration, seed-error recovery, runtime PM, and suspend/resume state restore.

Important APIs, types, and functions: `struct stm32_rng_data`, `struct stm32_rng_config`, `struct stm32_rng_private`, `stm32_rng_read()`, seed concealment helpers, `stm32_rng_init()`, PM callbacks, and `stm32_rng_probe()`.

Control flow: probe maps registers, resets hardware if available, reads DT booleans for clock-error detection and config locking, gets clocks, enables runtime PM, and registers hwrng. Init enables clocks, clears errors, optionally programs entropy/health/noise controls under conditional reset, enables RNG, waits for data-ready, then disables clocks. Reads runtime-resume, recover seed errors, poll/read 32-bit words, handle clock errors, treat zero data as late seed error, and autosuspend.

State and persistence: per-device state includes clock/reset handles, SoC configuration, DT options, and saved PM register config. Suspend stores CR/NSCR/HTCR, resume restores with required conditional-reset sequencing.

Dependencies and integration: platform/OF, reset, bulk clocks, runtime/system PM, MMIO polling, and hwrng.

Risks and test signals: recovery retry logic can return partial data, and configuration locking may prevent later changes. Tests should cover each compatible clock count, clock divisor calculation, seed-error recovery with/without CONDRST, suspend/resume restore, timeout paths, zero-data recovery, and DT property combinations.
