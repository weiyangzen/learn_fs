# sources/distributed-fs/ceph-client/drivers/watchdog/pika_wdt.c

## Purpose
`pika_wdt.c` is a legacy miscdevice driver for PIKA FPGA watchdog hardware. It uses a short hardware watchdog timeout and a kernel timer to bridge a longer userspace heartbeat interval.

## Important APIs, types, and functions
Global `pikawdt_private` stores FPGA MMIO, next heartbeat, open bit, magic-close state, bootstatus, and timer. Important functions are `pikawdt_reset`, `pikawdt_ping`, `pikawdt_keepalive`, `pikawdt_start`, file operations, and module init/exit.

## Control flow
Init finds `pika,fpga`, maps it, reads firmware version, maps `pika,fpga-sd` to read POST watchdog reset status, initializes timer, and registers `/dev/watchdog`. Open enforces single access and starts a timer ticking every 500 ms. Timer writes the FPGA reset-control register while userspace heartbeat remains valid, or while not nowayout and the device is closed; otherwise it stops feeding and logs that reset will occur. Writes scan for magic `V` and extend heartbeat. Release deletes the timer when close is not expected, clears open state, and leaves hardware behavior to nowayout/timer state.

## State and persistence
State is global runtime state plus FPGA registers. POST reset cause is read at init. The FPGA watchdog cannot be disabled once enabled according to comments; software controls only whether to keep feeding it.

## Dependencies and integration points
It depends on OF node lookup/mapping, big-endian MMIO accessors, timers, miscdevice `WATCHDOG_MINOR`, classic watchdog ioctls, and module parameters `heartbeat` and `nowayout`.

## Risks and test signals
Risks include nonstandard release semantics where unexpected close deletes the software timer, no validation of `WDIOC_SETTIMEOUT`, hardware timeout comment mismatch with programmed value macro naming, and global singleton assumptions. Test signals include OF mapping failures, POST bootstatus, firmware version read, timer feed expiration, magic close, timeout ioctl validation gaps, and nowayout behavior.
