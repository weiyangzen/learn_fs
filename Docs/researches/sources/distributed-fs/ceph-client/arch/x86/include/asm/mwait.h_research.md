# sources/distributed-fs/ceph-client/arch/x86/include/asm/mwait.h

## Purpose
Provides inline wrappers and constants for MONITOR/MWAIT, AMD MONITORX/MWAITX, Intel TPAUSE, and idle-loop MWAIT usage.

## Important APIs, Types, And Functions
Defines hint masks, CPUID leaf 5 flags, `MWAIT_ECX_INTERRUPT_BREAK`, `MWAITX_ECX_TIMER_ENABLE`, `MWAITX_MAX_WAIT_CYCLES`, TPAUSE state constants, `__monitor()`, `__monitorx()`, `__mwait()`, `__mwaitx()`, `__sti_mwait()`, `mwait_idle_with_hints()`, and `__tpause()`.

## Control Flow
Idle code checks `need_resched()`, clears CPU buffers if required, sets polling, optionally flushes the monitored address for CPU errata, executes MONITOR on `thread_info.flags`, then either uses interrupt-breaking MWAIT or `sti; mwait` followed by IRQ disable. MWAITX adds a timer in EBX/ECX. TPAUSE encodes the instruction manually.

## State And Persistence
State is CPU-local wait state, polling flags, monitored address state, and optional idle buffer-clearing side effects. No durable persistence.

## Dependencies And Integration Points
Depends on scheduler idle APIs, CPU features, and nospec buffer clearing. It integrates with x86 idle drivers, scheduler reschedule signaling, and CPU errata workarounds.

## Risks And Edge Cases
The `sti; mwait` sequence must be adjacent to avoid missing interrupts. Errata `X86_BUG_MONITOR` and `X86_BUG_CLFLUSH_MONITOR` must be honored. MWAIT hints and timer fields are vendor-specific.

## Test Signals
Idle residency tests, scheduler wakeup latency tests, CPU hotplug, suspend/resume, AMD MWAITX-capable systems, Intel UMWAIT/TPAUSE tests, and errata build coverage are useful.
