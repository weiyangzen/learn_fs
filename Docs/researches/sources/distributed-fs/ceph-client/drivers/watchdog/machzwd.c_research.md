<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c`

Purpose: legacy MachZ ZF-Logic watchdog driver using fixed I/O ports and a kernel timer to bridge a short hardware watchdog interval to a user-space heartbeat window.

Important APIs, types, and functions: fixed port helpers access ZF registers through index/data ports. `zf_timer_on()` programs WD1/WD2, sets `next_heartbeat`, starts the kernel timer, and enables WD1 with selected action. `zf_ping()` feeds WD2 and toggles `RESET_WD1` while user heartbeat is fresh. File ops implement writes, keepalive ioctl, open/close, and magic close.

Control flow: init verifies ZF-Logic version, maps module `action` to RESET/SMI/NMI/SCI, reserves I/O ports, registers reboot notifier and misc device, then clears status/control. Open enforces single-open and starts internal/hardware timers. User writes extend `next_heartbeat`. The kernel timer pings every ~500 ms until the user heartbeat expires. Close disables only with magic close, otherwise it deletes the internal timer and leaves hardware to reset. Reboot notifier turns timers off.

State and persistence: software state includes `zf_is_open`, `zf_expect_close`, `next_heartbeat`, selected action, spinlock, and kernel timer. Hardware has two cascading watchdog timers; WD2 eventually resets unconditionally after WD1 expires.

Dependencies and integration points: fixed I/O base `0x218`, misc watchdog ABI, reboot notifier, timer API, spinlock-protected port access, and module action/nowayout parameters.

Risks and test signals: risks include action-bit mapping, kernel timer deletion causing intentional reset, no timeout ioctl, and short hardware interval sensitivity. Test hardware detection, all action modes, magic close, unexpected close reset path, reboot notifier, and timer keepalive cadence under scheduler stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/machzwd.c -->
