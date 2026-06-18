<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c

Purpose: watchdog-core driver for NXP S32G SWT watchdog hardware, including optional early enable and time-left reporting.

Important APIs, types, and functions: `struct s32g_wdt_device` stores counter clock rate, MMIO base, and watchdog. Key functions are `s32g_wdt_ping()`, `s32g_wdt_start()`, `s32g_wdt_stop()`, `s32g_wdt_set_timeout()`, `s32g_wdt_get_timeleft()`, `s32g_wdt_init()`, and probe.

Control flow: probe maps the SWT registers, gets the `counter` clock, initializes watchdog limits from a 32-bit timeout register and clock rate, applies module/DT timeout, nowayout, stop-on-unregister, initializes control register policy, optionally starts hardware under `early_enable`, registers, and logs configuration. Ping writes the fixed service sequence. Set-timeout writes timeout counts then pings. Get-timeleft temporarily stops running hardware because the counter-output register is readable only while disabled.

State and persistence behavior: state is the SWT control register, timeout register, counter output, selected timeout, clock rate, and `WDOG_HW_RUNNING` when early enabled.

Dependencies and integration points: depends on platform MMIO, `counter` clock, module parameters, watchdog core, and debug/suspend mode semantics in the SWT control register.

Risks and edge cases: get-timeleft briefly disables the watchdog, which is observable hardware state. Minimum timeout is zero because hardware clamps small counter values. Clock-rate changes after probe invalidate conversions. `watchdog_info.options` includes ioctl command constants, not only option flags.

Test signals: service sequence writes, early_enable, timeout count conversion, get-timeleft while active, nowayout stop rejection through core, and clock-rate boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/s32g_wdt.c -->
