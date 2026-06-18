## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm8350.c

Purpose: Provides RTC support for Wolfson WM8350 PMICs, including time read/write, wildcard-style alarms, update/alarm interrupts, and PM wake behavior.

Important APIs/types/functions: The driver uses WM8350 MFD register helpers directly through `struct wm8350`. RTC callbacks are `wm8350_rtc_readtime`, `wm8350_rtc_settime`, `wm8350_rtc_readalarm`, `wm8350_rtc_setalarm`, and `wm8350_rtc_alarm_irq_enable`. Alarm state transitions use `wm8350_rtc_stop_alarm` and `wm8350_rtc_start_alarm`. IRQ handlers are `wm8350_rtc_alarm_handler` and `wm8350_rtc_update_handler`.

Control flow: Probe rejects unsupported BCD and 12-hour modes, enables the RTC tick in `POWER_MGMT_5` if needed, starts the clock if it is stopped, initializes wakeup, registers the RTC, registers seconds and alarm IRQs, and masks seconds updates by default. Reads use two consecutive four-register block reads and accept the time only when they match, then decode binary fields and calculate yday. Set-time sets `RTC_SET`, waits for stop confirmation, writes four packed registers, and clears `RTC_SET` to run. Alarm read decodes wildcard masks as `-1` fields and reports enabled from `ALMSTS` polarity. Alarm write converts `-1` fields back to masks, stops alarm, writes three registers, and optionally starts it. Alarm IRQ reports AF and makes the alarm one-shot by setting `RTC_ALMSET`.

State and persistence: PMIC registers persist time, alarm masks, tick enable, status, and alarm state. Driver-owned `wm8350->rtc.alarm_enabled` is used on resume to restore alarms. Device/block lifetime is managed by the parent MFD platform data.

Dependencies/integration: Depends on WM8350 MFD core/RTC register definitions, RTC core, platform driver, PM sleep, and MFD IRQ registration/freeing.

Risks: Alarm enable polarity is subtle because `ALMSTS` indicates stopped/disabled state. The retry loops use small retry counts and can fail on slow hardware. Probe must unlock/lock protected registers around tick enable. Wildcard alarms have no direct one-shot date semantics, so handler disables after trigger.

Test signals: Non-BCD 24-hour probe only, time double-read stability, stop/start retry timeouts, wildcard alarm fields, one-shot alarm interrupt behavior, seconds update interrupt masking, and suspend/resume with wake alarms.
