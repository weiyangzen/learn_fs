# sources/distributed-fs/ceph-client/arch/mips/kernel/reset.c

## Purpose
Provides generic MIPS restart, halt, poweroff, and final hang behavior, with platform hooks for machine-specific reset/halt implementations.

## Important APIs, Types, and Functions
- `_machine_restart`, `_machine_halt`, and exported `pm_power_off` are platform callback pointers.
- `machine_hang()` disables/masks interrupts and loops in low-power wait or busy loop.
- `machine_restart()`, `machine_halt()`, and `machine_power_off()` call platform/generic hooks, stop SMP, then hang if control returns.

## Control Flow
Restart first calls `_machine_restart` if installed, stops other CPUs on SMP, calls `do_kernel_restart()`, waits one second, logs failure, then hangs. Halt calls `_machine_halt`, stops SMP, and hangs. Poweroff calls `do_kernel_power_off()`, stops SMP, and hangs. `machine_hang()` disables interrupts, masks all interrupt lines, repeatedly executes `wait` directly on MIPS R CPUs or calls `cpu_wait()`, and clears Compare to avoid timer interrupts repeatedly waking the CPU.

## State and Persistence
Only runtime hardware state: interrupt masks, CP0 Compare, SMP stop state, and platform power/reset side effects. No persistence.

## Dependencies and Integration Points
Integrates with Linux reboot/poweroff core, platform reset hooks, SMP stop, CPU wait implementations, CP0 status/compare, and exported `pm_power_off` used by drivers/platforms.

## Risks
If platform hooks return, the system must reliably stop doing useful work. Calling `cpu_wait()` can re-enable interrupts, so the code remasks/disables afterward. Some CPUs wake from wait despite masked interrupts, requiring Compare clearing.

## Test Signals
Reboot, halt, and poweroff commands should either transition platform state or end in a quiet hang with interrupts masked. Failed reboot should log `"Reboot failed -- System halted"`.
