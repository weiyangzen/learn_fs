# sources/distributed-fs/ceph-client/drivers/counter/stm32-lptimer-cnt.c

Purpose: STM32 low-power timer counter/encoder driver, supporting simple external counting and optional quadrature X4 mode through the Generic Counter subsystem.

Important APIs/types/functions: `struct stm32_lptim_cnt` stores device, regmap, clock, ceiling, polarity, quadrature flag, and enabled state. Helpers `stm32_lptim_is_enabled()`, `stm32_lptim_setup()`, and `stm32_lptim_set_enable_state()` configure CFGR/CR/ARR/CMP and clock state. Counter callbacks implement count read, function read/write, enable read/write, ceiling read/write, and action read/write.

Control flow: probe uses the parent STM32 LPTIMER MFD data, allocates a counter, selects one-count metadata with either one signal or encoder two-signal support based on `has_encoder`, and registers. Function/action/ceiling writes reject changes while hardware is enabled. Enabling configures counter or encoder mode, writes ARR/CMP after enabling the LP timer, waits for CMPOK/ARROK, clears flags, and starts continuous mode. Suspend disables only if this child had enabled the timer, records desired enabled state, selects sleep pinctrl, and resume restores pinctrl and re-enables if needed.

State and persistence: driver caches ceiling, polarity, quadrature mode, and whether it enabled the timer. Hardware counter/configuration is volatile and restored on resume only for enabled instances.

Dependencies and integration: depends on STM32 LPTIMER MFD regmap/clock definitions, pinctrl PM helpers, platform/OF compatible `st,stm32-lptimer-counter`, and Generic Counter.

Risks: no explicit mutex protects cached configuration fields against concurrent sysfs writes. `stm32_lptim_is_enabled()` is used as a guard but return values in boolean contexts need care because negative errors are true in C. Only quadrature X4 is accepted for encoder mode; other quadrature combinations are not exposed.

Test signals: probe with `has_encoder` true and false, sysfs signal/count layout differences, enable sequence writes ARR/CMP and waits for flags, busy errors for function/action/ceiling writes while enabled, action behavior for rising/falling/both in simple count mode, suspend/resume preserving enabled operation, and clock enable/disable balance.
