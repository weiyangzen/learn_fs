<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c

Purpose: provides host-side alarm interrupt sources for UML RTC: a pipe for time-travel mode or `timerfd` for normal real-time mode.

Important APIs/types/functions: static `uml_rtc_irq_fds[2]` stores pipe/timer descriptors. Public functions are `uml_rtc_send_timetravel_alarm()`, `uml_rtc_start()`, `uml_rtc_enable_alarm()`, `uml_rtc_disable_alarm()`, and `uml_rtc_stop()`.

Control flow: in time-travel mode `uml_rtc_start()` creates a nonblocking close-on-exec pipe; simulated alarm callbacks write a counter to the pipe. In normal mode it creates a `CLOCK_REALTIME` timerfd, marks SIGIO broken, and adds the FD to SIGIO monitoring. Enabling an alarm calls `timerfd_settime()` with a relative seconds value. Stop closes the write end for pipes or removes SIGIO for timerfd, then closes the read FD.

State and persistence: only runtime FDs are stored. No alarm state is persisted here.

Dependencies and integration points: depends on `timerfd_create`, `timerfd_settime`, pipe helpers, SIGIO helpers, `os_close_file()`, and `rtc_kern.c`.

Risks: timerfd does not send SIGIO, so the workaround must remain aligned with UML IRQ handling. Time-travel writes ignore short-write errors. `uml_rtc_disable_alarm()` uses zero-time timer programming.

Test signals: normal timerfd alarm firing, time-travel pipe injection, start failure cleanup, repeated enable/disable, and stop in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c -->
