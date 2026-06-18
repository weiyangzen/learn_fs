<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c`

Purpose: legacy ISA-style MixCOM/FlashCOM watchdog miscdevice driver that probes fixed I/O ports and uses an internal timer because the hardware cannot be shut down normally.

Important APIs, types, and functions: `mixcomwd_io_info[]` lists candidate ports and card IDs. `checkcard()` reserves a port and validates ID. `mixcomwd_ping()` writes magic value 55. `mixcomwd_timerfun()` pings every five seconds. File ops implement single-open, magic close, status ioctl, and keepalive.

Control flow: init scans the fixed port list until a card responds, registers `/dev/watchdog`, and leaves the port reserved. Open pings and, if not nowayout, cancels any internal keepalive timer from a prior close. Writes optionally scan for `V` and ping. Release with magic close starts the internal ping timer instead of disabling hardware; unexpected release logs that the watchdog will not stop. Exit warns and deletes internal timer, deregisters misc device, and releases the port.

State and persistence: driver state includes `mixcomwd_opened`, `watchdog_port`, `mixcomwd_timer_alive`, `expect_close`, and a kernel timer. Hardware keeps running once activated; "close" transfers responsibility to kernel timer.

Dependencies and integration points: depends on fixed legacy I/O port probing, misc watchdog ABI, timer API, module nowayout, and port reservation.

Risks and test signals: risks include false-positive fixed-port probing, timer cleanup causing reset, no timeout setting, and confusing close semantics. Test card detection on all supported ports, status bit reporting, magic close timer behavior, unexpected close, module exit warning, and nowayout module pinning.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mixcomwd.c -->
