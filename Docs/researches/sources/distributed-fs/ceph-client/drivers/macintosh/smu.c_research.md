# sources/distributed-fs/ceph-client/drivers/macintosh/smu.c

Purpose: implements the PowerMac G5 SMU system controller driver. It provides queued command transport, RTC/power operations, SMU-backed I2C commands, SMU SDB partition extraction, OF child exposure, and a `/dev/smu` misc userspace command interface.

Important APIs and functions: exported command APIs include `smu_queue_cmd()`, `smu_queue_simple()`, `smu_poll()`, `smu_done_complete()`, `smu_spinwait_cmd()`, `smu_present()`, `smu_get_sdb_partition()`, and `smu_get_ofdev()`. Power/RTC helpers are `smu_get_rtc_time()`, `smu_set_rtc_time()`, `smu_shutdown()`, and `smu_restart()`. Low-level transport uses `smu_start_cmd()` and `smu_db_intr()`. I2C support centers on `smu_queue_i2c()`, `smu_i2c_low_completion()`, and retry timer logic. File operations implement `/dev/smu`.

Control flow: early init locates the `smu` node, allocates a low-2GB command buffer via memblock, finds doorbell/message GPIO nodes, maps a doorbell pointer buffer, and marks SMU as system controller. Core init maps/requests IRQs and sets up the I2C retry timer. Commands are queued under `smu->lock`; `smu_start_cmd()` copies data to the shared buffer, flushes cache, writes the physical address, and rings the doorbell. Completion IRQ validates ack, copies replies, updates status, starts the next command, then invokes callbacks outside the lock.

State and persistence: single global `smu_device`, command queue/current command, I2C queue/current command, retry timer, OF platform device, SDB partition properties cached onto the SMU OF node, and per-open `/dev/smu` state.

Dependencies and integration: depends on PMac feature GPIO calls, OF/platform devices, memblock, cache flushes, miscdevice, completions, timers, wait queues, and `asm/smu.h`.

Risks: no general command timeout is implemented. Command buffer cache coherency and low-memory address assumptions are hardware-critical. I2C retry code is complex and queue manipulation should be reviewed carefully. `/dev/smu` exposes raw commands to userspace; event mode is stubbed. SDB partition reads add OF properties dynamically.

Test signals: boot on SMU G5, command completion by IRQ and early poll fallback, RTC get/set, shutdown/restart command issue, SMU I2C read/write retries, SDB partition property creation, `/dev/smu` blocking/nonblocking reads, poll readiness, and child `smu-sensors` platform device creation without device-model deadlock.
