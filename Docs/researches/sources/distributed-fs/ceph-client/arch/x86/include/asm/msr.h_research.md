# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr.h

## Purpose
Implements x86 MSR and PMC access primitives, safe exception-handled variants, trace integration, per-CPU MSR helpers, SMP remote access declarations, and WRMSRNS support.

## Important APIs, Types, And Functions
Types include `struct msr_info`, `struct msr_regs_info`, `struct saved_msr`, and `struct saved_msrs`. Core helpers include `__rdmsr()`, `__wrmsrq()`, `native_rdmsr()`, `native_rdmsrq()`, `native_wrmsr()`, `native_wrmsrq()`, `native_read_msr()`, `native_read_msr_safe()`, `native_write_msr()`, `native_write_msr_safe()`, `native_read_pmc()`, `rdmsr()`, `wrmsr()`, `rdmsrq()`, `wrmsrq()`, `rdmsr_safe()`, `wrmsrq_safe()`, `rdpmc()`, `wrmsrns()`, `msrs_alloc()`, `msrs_free()`, bit set/clear helpers, and `*_on_cpu()` variants.

## Control Flow
Bare primitives emit `rdmsr` or `wrmsr` with exception table fixups. Safe variants return an error instead of faulting. Traced wrappers call trace hooks when enabled. Paravirt builds can override generic wrappers; non-paravirt builds call native helpers. SMP helpers execute MSR operations on target CPUs or fall back to CPU 0 in UP builds.

## State And Persistence
The header manipulates CPU MSR hardware state. Per-CPU `struct msr` allocations store temporary snapshots. Hardware changes persist until overwritten or reset.

## Dependencies And Integration Points
Depends on `msr-index.h`, x86 asm constraints, exception tables, cpumasks, UAPI MSR structs, tracepoints, atomics, and paravirt. It integrates with CPU init, KVM, perf, mitigations, power management, MCE, and debug code.

## Risks And Edge Cases
Invalid MSRs can #GP, so safe variants and exception types must be correct. Register constraints must preserve low/high halves. `wrmsrns()` is feature-gated through alternatives. Tracing must not alter bare primitive semantics.

## Test Signals
MSR selftests, safe invalid-MSR probes, remote CPU MSR tests, tracepoint tests, paravirt builds, and WRMSRNS-capable CPU boot coverage are useful.
