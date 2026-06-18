<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c -->
# sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c

Purpose: `freefall.c` is a daemon for HP/DELL-style free-fall sensors that parks disk heads when `/dev/freefall` reports motion and optionally toggles an HDD-protection LED.

Important APIs/functions: `set_unload_heads_path()` validates `/dev/*` input and maps it to `/sys/block/<dev>/device/unload_heads`. `valid_disk()` checks sysfs support. `write_int()` writes numeric sysfs values. `set_led()` writes LED brightness unless missing. `protect()` writes park duration in milliseconds and logs with syslog. `ignore_me()` handles SIGALRM by unparking heads and clearing the LED. `main()` validates the target disk, opens `/dev/freefall`, daemonizes, opens syslog, elevates scheduling to FIFO, locks memory, installs alarm handler, and loops reading sensor events.

Control flow: each successful read from `/dev/freefall` cancels old alarms, parks heads for 21 seconds, turns the LED on, then sets a short alarm to unpark. If `read()` is interrupted by SIGALRM, the loop continues after `ignore_me()` has unparked.

State and persistence: persistent side effects are sysfs writes to `unload_heads` and LED brightness plus syslog messages. Runtime state includes global paths, `noled`, open sensor fd, scheduler policy, and locked memory.

Dependencies/integration: depends on `/dev/freefall`, block-device sysfs `unload_heads`, optional HP LED path, daemon/syslog APIs, realtime scheduling, and memory locking privileges.

Risks and test signals: risks include fixed buffer sizes/truncation, hard-coded LED path, stubbed `on_ac()`/`lid_open()` always returning true, ignored scheduler/mlock failures, and running as a daemon with hardware side effects. Test invalid devices, absent LED, SIGALRM unpark path, read interruption, sysfs write failures, and daemon startup under expected privileges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c -->
