# sources/distributed-fs/ceph-client/drivers/watchdog/eurotechwdt.c

## Purpose
`eurotechwdt.c` is a legacy miscdevice watchdog for Eurotech CPU-1220/1410/1420 boards using an SMSC Super-I/O watchdog. It can signal timeout by interrupt or reboot output.

## Important APIs, types, and functions
Global state tracks open status, timeout, magic-close flag, I/O base, IRQ, event mode, and spinlock. Helpers include `eurwdt_unlock_chip`, `eurwdt_lock_chip`, `eurwdt_write_reg`, `eurwdt_activate_timer`, `eurwdt_disable_timer`, and `eurwdt_ping`. File operations implement write, ioctl, open, and release, and a reboot notifier disables the timer on shutdown.

## Control Flow
Module init requests the IRQ and I/O range, registers a reboot notifier and `/dev/watchdog`, then unlocks/selects the Super-I/O logical device. Open initializes the default timeout and activates the timer. Writes scan for magic `V` when nowayout is false and ping the timer. Ioctls support status, set options, keepalive, and timeout get/set. Release disables only after magic close; otherwise it pings and leaves the watchdog running.

## State and Persistence
State is global and single-open. Hardware configuration is programmed in Super-I/O registers and may continue after unexpected close or module unload. The driver does not use watchdog core state.

## Dependencies and Integration Points
It depends on fixed/parameterized I/O ports, IRQ handling, miscdevice `/dev/watchdog`, reboot notifier, and legacy watchdog ioctls.

## Risks and Test Signals
Risks include no reliable board probing, IRQ zero handling versus unconditional free, global lock coverage, magic-close semantics, and continuing hardware after unload. Tests should cover both `ev=int` and reboot modes, invalid IRQ handling, timeout bounds, unexpected close, reboot notifier, and I/O region/IRQ conflict paths.
