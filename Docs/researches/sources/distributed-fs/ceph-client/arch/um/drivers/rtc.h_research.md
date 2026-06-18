<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h

Purpose: declares host/timetravel helper functions for the UML RTC driver.

Important APIs/types/functions: prototypes are `uml_rtc_start()`, `uml_rtc_enable_alarm()`, `uml_rtc_disable_alarm()`, `uml_rtc_stop()`, and `uml_rtc_send_timetravel_alarm()`.

Control flow: `rtc_kern.c` calls these helpers to create an interrupt source, program real-time alarms, cancel alarms, and inject time-travel alarm events.

State and persistence: no state is defined here; implementation state is in `rtc_user.c` and `rtc_kern.c`.

Dependencies and integration points: bridges the Linux RTC class driver to host `timerfd`/pipe behavior.

Risks: prototypes rely on `bool`; users must include suitable headers before this file, as the C files do.

Test signals: compile RTC driver and exercise alarm setup in normal and time-travel modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h -->
