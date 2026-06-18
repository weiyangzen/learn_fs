# sources/distributed-fs/ceph-client/arch/x86/kernel/pvclock.c

## Purpose
Provides common x86 paravirtual clock helpers used by KVM and Xen to convert hypervisor-provided pvclock structures into monotonic clocksource and wall-clock values.

## APIs, Types, And Functions
Key state is `valid_flags`, global atomic `last_value`, and `pvti_cpu0_va`. Public functions include `pvclock_set_flags()`, `pvclock_tsc_khz()`, `pvclock_touch_watchdogs()`, `pvclock_resume()`, `pvclock_read_flags()`, `pvclock_clocksource_read()`, `pvclock_clocksource_read_nowd()`, `pvclock_read_wallclock()`, `pvclock_set_pvti_cpu0_va()`, and exported `pvclock_get_pvti_cpu0_va()`.

## Control Flow
Readers use pvclock version retry loops to read consistent vCPU time or wall-clock structures. Clocksource reads calculate nanoseconds from ordered TSC, optionally clear `PVCLOCK_GUEST_STOPPED` and touch watchdogs, return directly when stable-TSC is valid, or otherwise enforce monotonicity through `last_value` compare-exchange. Wall-clock reads combine boot wall time with pvclock elapsed time.

## State And Persistence
`valid_flags` filters trusted hypervisor flags. `last_value` persists as a global monotonic floor and is reset on resume. `pvti_cpu0_va` stores the CPU0 pvclock vsyscall mapping pointer and must be set before VDSO pvclock use.

## Dependencies And Integration
Depends on pvclock structure definitions, TSC ordering, clocksource/watchdog APIs, RCU stall and hung-task watchdog resets, VDSO clock mode, fixmap/vgtod integration, and hypervisor-specific KVM/Xen setup.

## Risks And Test Signals
Risks include time going backwards, stale guest-stopped flags, incorrect TSC frequency calculation, and the 32-bit seconds limit in `pvclock_wall_clock`. Test signals include KVM/Xen guest clocksource tests, suspend/resume time continuity, watchdog behavior after guest stop, VDSO pvclock smoke tests, and monotonic clock stress across vCPUs.
