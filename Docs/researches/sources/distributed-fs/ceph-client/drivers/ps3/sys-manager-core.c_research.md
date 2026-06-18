# sources/distributed-fs/ceph-client/drivers/ps3/sys-manager-core.c Research

## Purpose
`sys-manager-core.c` is the statically linked bridge between generic PS3 power-control entry points and the loadable PS3 system-manager driver. It lets the module register callbacks while preserving always-available poweroff/restart/halt symbols.

## Important APIs, Types, And Functions
`ps3_sys_manager_register_ops()` copies a supplied `struct ps3_sys_manager_ops` into a static global after `BUG_ON()` checks that both the ops pointer and `ops->dev` are present. `ps3_sys_manager_power_off()` and `ps3_sys_manager_restart()` call registered callbacks if present, then fall through to `ps3_sys_manager_halt()`. `ps3_sys_manager_halt()` logs an emergency halt message, disables local interrupts, and loops forever in `lv1_pause(1)`.

## Control Flow
The system-manager module registers or updates callbacks during its probe/remove lifecycle. Poweroff and restart paths dereference the last registered ops and pass the stored device pointer to the callback. If no callback is registered, or if the callback returns, the code enters the non-returning halt loop.

## State And Persistence
The only state is the static `ps3_sys_manager_ops` copy. There is no locking or reference counting around the registered module/device pointer. The final halt state is persistent by design because execution never returns.

## Dependencies And Integration Points
It depends on `asm/ps3.h` for `struct ps3_sys_manager_ops`, LV1 pause calls, exported GPL symbols, and platform power management code that invokes these functions as machine poweroff/restart handlers.

## Risks
Registration uses a raw struct copy with no lifetime protection, so remove paths must avoid leaving stale callback pointers. `BUG_ON()` makes invalid registration fatal. Callback failure is not reported because halt is unconditional afterward.

## Test Signals
Test signals are mostly platform integration checks: registered callbacks fire on poweroff and restart, missing callbacks still halt cleanly, invalid registration is caught in debug/fault tests, and no stale callback is reachable after system-manager module removal.
