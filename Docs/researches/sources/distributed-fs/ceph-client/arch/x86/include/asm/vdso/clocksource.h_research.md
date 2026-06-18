# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/clocksource.h

Purpose: Advertises x86 vDSO-supported clock modes to the generic vDSO time code.

Important APIs/types/functions: `VDSO_ARCH_CLOCKMODES` lists `VDSO_CLOCKMODE_TSC`, `VDSO_CLOCKMODE_PVCLOCK`, and `VDSO_CLOCKMODE_HVCLOCK`. `HAVE_VDSO_CLOCKMODE_HVCLOCK` signals that Hyper-V clock support exists in the architecture implementation.

Control flow: No code executes here. The macros feed generic vDSO declarations and switch logic elsewhere.

State and persistence: No state is stored. The selected clock mode lives in vDSO datapage state maintained by timekeeping code.

Dependencies and integration points: Consumed by generic `vdso/` time headers and paired with x86 `gettimeofday.h`, paravirtual clock support, and Hyper-V timer support.

Risks: The list must match actual x86 implementations. Advertising a mode without a valid reader can make user-space time calls fail or fall back incorrectly.

Test signals: Build tests for TSC, KVM pvclock, and Hyper-V configs; runtime `clock_gettime()` vDSO behavior on bare metal and hypervisors.
