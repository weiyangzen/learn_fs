<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c

Purpose: simple legacy watchdog miscdevice for Winsystems EPX-C3 boards using fixed control and pet I/O ports.

Important APIs, types, and functions: global `epx_c3_alive` tracks open state. Important functions are `epx_c3_start()`, `epx_c3_stop()`, `epx_c3_pet()`, file operations, ioctl handler, reboot notifier, init, and exit.

Control flow: init reserves two I/O ports, registers reboot notifier, and registers `/dev/watchdog`. Open rejects concurrent users, pins the module when nowayout, enables hardware, pets it, and marks alive. Write pets. Ioctl supports support/status, enable/disable, keepalive, and fixed get-timeout. Release disables only when nowayout is false. Reboot notifier disables on halt/down.

State and persistence behavior: state is only `epx_c3_alive`, nowayout, and hardware port values. Timeout is fixed at one second and not programmable.

Dependencies and integration points: depends on port I/O, miscdevice watchdog ABI, reboot notifier, and board-specific non-probeable hardware.

Risks and edge cases: open-state flag is not atomic and can race. There is no magic close despite normal watchdog expectations. The driver warns in module description that it cannot probe hardware, so loading on wrong systems can write unrelated ports.

Test signals: correct board-only loading policy, I/O port reservation, concurrent open race testing, fixed timeout ioctl, nowayout release behavior, and reboot notifier disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_epx_c3.c -->
