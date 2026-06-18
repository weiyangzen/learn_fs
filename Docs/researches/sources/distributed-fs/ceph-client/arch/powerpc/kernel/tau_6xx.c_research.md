# sources/distributed-fs/ceph-client/arch/powerpc/kernel/tau_6xx.c

## Purpose
Implements thermal monitoring for 6xx/750-class CPUs with Thermal Assist Units (TAU), maintaining low/high temperature thresholds and optionally handling TAU interrupts.

## Important APIs, Types, and Functions
- `struct tau_temp tau[NR_CPUS]` stores interrupt count, low/high thresholds, and whether the window grew.
- `set_thresholds()` writes THRM1/THRM2 threshold SPRs.
- `TAUupdate()` reads THRM1/THRM2, adjusts thresholds when low/high trips, and clears threshold registers.
- `TAUException()` handles TAU interrupts when `CONFIG_TAU_INT`.
- `tau_timeout()` periodically polls/updates thresholds, shrinks the window, and restarts THRM3 sampling.
- `TAU_init()` initializes all CPUs, starts an ordered workqueue, and exposes `tau_initialized`.
- `cpu_temp_both()`, `cpu_temp()`, and `tau_interrupts()` expose readings/counters.

## Control Flow and State
Initialization checks `CPU_FTR_TAU`, decides whether interrupts are usable for ppc750, allocates an ordered workqueue, initializes thresholds on each CPU, then queues recurring work. The work sleeps for `shrink_timer`, runs `tau_timeout()` on each CPU, and requeues itself. Interrupt mode updates thresholds immediately in `TAUException`.

## State and Persistence Behavior
Per-CPU threshold state persists in `tau[]` and hardware THRM SPRs. The workqueue is long-lived. `tau_int_enable` and `tau_initialized` are global mode indicators.

## Dependencies and Integration Points
Depends on CPU feature/spec detection, THRM SPR definitions, interrupt entry macros, `on_each_cpu()`, workqueues, and consumers of exported temperature helper functions.

## Risks
Threshold adjustments are heuristic and uncalibrated. Workqueue recursion has no teardown path here. Incorrect TAU interrupt enablement or SPR writes can cause interrupt storms or stale temperature windows.

## Test Signals
Boot on TAU-capable and non-TAU CPUs, observe threshold movement under thermal load, test interrupt and polling configs, CPU hotplug/SMP behavior, and helper return values.
