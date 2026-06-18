<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c

Purpose: legacy miscdevice watchdog for Sun RIO systems using a NatSemi Super I/O power-management logical device.

Important APIs, types, and functions: `struct riowd` stores two-byte indexed register window and a spinlock. Key functions are `riowd_writereg()`, miscdevice open/release/write/ioctl handlers, probe, remove, and OF match.

Control flow: probe allows only one device, maps two bytes from the OF resource, publishes global `riowd_device`, and registers `/dev/watchdog`. Keepalive writes the timeout in minutes to index `WDTO_INDEX`; disable writes zero. `WDIOC_SETTIMEOUT` accepts seconds, validates 60..15300, rounds up to minutes, writes hardware, and returns seconds.

State and persistence behavior: state is global pointer, spinlock, and module parameter `riowd_timeout` in minutes. Hardware timeout state persists in Super I/O register index 0x05 until changed.

Dependencies and integration points: depends on OF platform resource mapping with `of_ioremap()`, miscdevice watchdog ABI, indexed Super I/O register access, and the Sun BBC reset wiring described in comments.

Risks and edge cases: no open-exclusion bit is used, so multiple opens can race. The driver has no magic close or nowayout handling. Timeout granularity is minutes, and SETTIMEOUT rounds up. If misc registration fails, the global pointer is cleared, but remove does not clear it.

Test signals: OF resource map/unmap, timeout rounding, enable/disable ioctl, concurrent opens/writes, status ioctls, and reset-line behavior on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/riowd.c -->
