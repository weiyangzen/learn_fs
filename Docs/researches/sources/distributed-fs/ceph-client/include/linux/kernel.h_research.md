# sources/distributed-fs/ceph-client/include/linux/kernel.h

## Purpose
Acts as a compatibility umbrella for historically common kernel helpers while the kernel continues splitting unrelated content into narrower headers. In this copy it primarily exposes scheduling/sleep annotations, kernel text address queries, boot/system state, and common helper includes.

## Important APIs, Types, And Functions
The header includes many helper headers for alignment, arrays, types, compiler annotations, containers, bitops, conversion, math, min/max, panic, printk, sprintf, static calls, and trace printk. It defines `might_resched()` according to preemption configuration, debug helpers `might_sleep()`, `cant_sleep()`, `cant_migrate()`, `non_block_start/end()`, `might_fault()`, `do_exit()`, kernel text address helpers, `bust_spinlocks()`, `root_mountflags`, `early_boot_irqs_disabled`, `enum system_states`, `system_state`, and `REBUILD_DUE_TO_DYNAMIC_FTRACE`.

## Control Flow
Preemption configuration selects whether `might_resched()` calls `__cond_resched()`, a static call, a dynamic key path, or no-op. Debug atomic-sleep builds route annotations to checking functions; normal builds collapse most checks to no-ops or just rescheduling.

## State And Persistence
State exposed here includes global boot and system-state variables plus per-task debug counters updated by non-block annotations. These are runtime state and not persistent.

## Dependencies And Integration Points
Depends on a broad set of core kernel headers and `asm/byteorder.h`. Integrates with scheduler preemption, lockdep/debug atomic sleep, faulting user access paths, ftrace rebuilds, panic/exit, and code address classification.

## Risks
The header warns against including it from other headers because it drags many dependencies and can worsen build coupling. Missing annotations can hide sleep-in-atomic bugs; over-annotation can generate false positives or overhead in debug builds.

## Test Signals
Signals include build dependency checks, debug atomic sleep tests, preemption configuration matrix builds, lockdep sleep warnings, `might_fault()` user access tests, and system-state transition checks during boot/shutdown/suspend.
