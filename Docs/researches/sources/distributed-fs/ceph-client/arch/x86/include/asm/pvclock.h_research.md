<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h

Purpose: supplies x86 pvclock helper declarations and inline read/scale primitives used by KVM and Xen clock sources. Important APIs include `pvclock_clocksource_read()`, `pvclock_read_flags()`, `pvclock_tsc_khz()`, `pvclock_read_wallclock()`, `pvclock_resume()`, `pvclock_touch_watchdogs()`, `pvclock_read_begin()`, `pvclock_read_retry()`, `pvclock_scale_delta()`, `__pvclock_read_cycles()`, and pvti CPU0 accessors.

Control flow: callers read a stable version, copy time fields, compute scaled TSC deltas with architecture-specific multiply code, then retry if the hypervisor version changed. Clocksource and wallclock paths use the same ABI structures to produce nanoseconds or wall time.

State and persistence: uses hypervisor-updated pvclock pages and optional per-CPU vsyscall time info; no disk persistence. Dependencies include pvclock ABI, virtual memory barriers, clocksource, paravirt clock config, and x86 asm multiply semantics. Risks include torn reads, scaling overflow/shift bugs, unstable TSC flags, and incorrect 32-bit multiply constraints. Test signals include pvclock monotonicity, 32/64-bit builds, migration/resume, watchdog touch behavior, and vDSO/paravirt clock access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock.h -->
