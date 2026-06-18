# sources/distributed-fs/ceph-client/arch/hexagon/kernel/reset.c

## Purpose

`reset.c` provides Hexagon machine halt, poweroff, and restart hooks using the virtual machine stop primitive. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public hooks are `machine_halt`, `machine_power_off`, `machine_restart`, and exported `pm_power_off`. Concrete declarations observed in the file: Includes: `linux/reboot.h`, `linux/smp.h`, `asm/hexagon_vm.h`. Functions/syscalls: `machine_power_off`, `machine_halt`. Exported symbols: `pm_power_off`.

## Control Flow, State, And Persistence

Runtime flow is direct: halt/poweroff/restart call `__vmstop`, with SMP stop available through generic shutdown paths.

## Dependencies And Integration Points

It integrates with reboot core, PM poweroff, SMP stop, and `asm/hexagon_vm.h`.

## Risks And Test Signals

Risks are restart behaving like halt or missing platform-specific reset. Test signals are reboot, halt, and poweroff command smoke tests under VM or hardware.
 A local static signal for this file is that it has 26 lines and 393 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
