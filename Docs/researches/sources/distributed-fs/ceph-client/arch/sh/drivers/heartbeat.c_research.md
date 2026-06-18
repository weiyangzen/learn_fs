# sources/distributed-fs/ceph-client/arch/sh/drivers/heartbeat.c



Source read size: 152 lines, 3628 bytes.



Purpose: platform driver that toggles a board LED bank as a load-average heartbeat.

Important APIs/types/functions: `heartbeat_drv_probe()`, `heartbeat_timer()`, `heartbeat_toggle_bit()`, `struct heartbeat_data`, default bit positions, and `heartbeat_driver`.

Control flow: probe validates one MMIO resource, uses platform data or allocates defaults, maps the register, derives bit mask and register width, installs a timer, and starts it. The timer toggles one LED bit, bounces between bit positions, and reschedules itself using a period based on the 5-minute load average.

State and persistence: timer state, mapped MMIO base, bit position/mask/regsize, and static scan direction persist while the driver is bound; LED register contents are hardware state.

Dependencies and integration points: depends on board platform devices, `asm/heartbeat.h`, load average accounting, timers, and raw I/O accessors.

Risks and test signals: no remove path unmaps or stops the timer; static `bit`/`up` are shared across devices; invalid platform data can target wrong bits. Test LED cadence under load, 8/16/32-bit resources, inverted mode, and platform-device binding.
