# sources/distributed-fs/ceph-client/arch/s390/kernel/ctlreg.c

## Purpose
Coordinates system-wide s390 control-register updates and maintains a global save copy in absolute lowcore once initialized.

## Important APIs, Types, And Functions
Exports `system_ctlreg_lock()`, `system_ctlreg_unlock()`, and `system_ctlreg_modify()`. `system_ctlreg_init_save_area()` initializes control-register save areas. Internal `ctlreg_callback()` applies modifications on a CPU, and `system_ctlreg_update()` dispatches locally during early boot or with `on_each_cpu()` later.

## Control Flow
Callers request set-bit, clear-bit, or load operations. `system_ctlreg_modify()` builds `ctlreg_parms`, updates the absolute-lowcore saved register copy under `system_ctl_lock` if initialized, then applies the change on all CPUs. During early boot, interrupts are disabled and only the local CPU is updated.

## State And Persistence
Global state includes `system_ctl_lock`, `system_ctlreg_area_init`, and saved control-register values in absolute lowcore. Hardware control registers on every CPU are modified.

## Dependencies And Integration Points
Depends on lowcore, absolute lowcore mapping, local control-register load/store helpers, SMP callbacks, and irq state. Entry and early setup rely on these helpers for low-address protection and other control bits.

## Risks And Edge Cases
All-CPU synchronization is critical. Updating saved lowcore state without matching hardware registers can break restart and dump paths. Early-boot behavior must avoid unavailable SMP infrastructure.

## Test Signals
Signals include boot tests, CPU hotplug/control register consistency checks, low-address protection behavior, lockdep coverage, and fault injection around absolute lowcore mapping.
