# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvmclock.h

## Purpose
Declares per-CPU KVM pvclock storage accessors for x86 guests using the KVM clocksource.

## Important APIs, Types, And Functions
Exports `DECLARE_PER_CPU(struct pvclock_vsyscall_time_info *, hv_clock_per_cpu)`, `this_cpu_pvti()`, and `this_cpu_hvclock()`. `this_cpu_pvti()` returns the embedded `pvclock_vcpu_time_info`, while `this_cpu_hvclock()` returns the full per-CPU vsyscall time-info object.

## Control Flow
Callers read the current CPU's `hv_clock_per_cpu` pointer and dereference it for time calculations. The helper assumes per-CPU clock storage has been initialized before use.

## State And Persistence
State is per-CPU memory containing pvclock time data shared with the KVM clock implementation. It persists only while the guest kernel runs.

## Dependencies And Integration Points
Depends on Linux per-CPU APIs and pvclock ABI types. It integrates with KVM guest clocksource initialization, vDSO/vsyscall time paths, and paravirtual time updates from the host.

## Risks And Edge Cases
Uninitialized per-CPU pointers or CPU-hotplug mistakes can crash time reads. Time correctness depends on pvclock sequence handling in implementation files outside this header.

## Test Signals
KVM guest boot, CPU hotplug, timekeeping selftests, vDSO clock tests, and suspend/resume under KVM clock exercise these helpers.
