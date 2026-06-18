# sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32-lp.c

Purpose: STM32 low-power timer platform driver providing a high-rated clockevent from the MFD STM32 LPTIM block, with wakeup support.

Important APIs/types/functions: `struct stm32_lp_private` stores regmap, clockevent, period, prescaler, device, clock, and hardware version. `stm32_clkevent_lp_set_timer()` dispatches version-specific ARR/IER programming. `stm32mp25_clkevent_lp_set_evt()` handles newer synchronization flags. Probe uses parent MFD data.

Control flow: probe obtains parent `stm32_lptimer` regmap/clock/version, enables clock, checks rate, gets parent IRQ, optionally enables wake IRQ, requests IRQ, computes prescaler to target less than `32000 * HZ`, initializes and registers clockevent. Event programming writes ARR/IER, starts continuous or single mode. IRQ clears ARRM flag and dispatches. Suspend shuts down timer and disables clock; resume reenables clock and restores prescaler.

State/persistence: devm-allocated private struct lives with platform device. Prescaler and period are cached for resume and periodic mode.

Dependencies/integration: platform compatible `st,stm32-lptimer-timer`, STM32 LPTIM MFD parent, regmap, CCF clock, wakeirq PM helpers, module platform driver.

Risks: parent IRQ lookup uses parent platform device; version-specific polling timeout can fail in atomic context; high rating may select this low-power event broadly; wake-source handling must balance device wake state. Tests include STM32MP25 register-sync path, older path, wakeup-source suspend, prescaler calculation, and IRQ clear.
