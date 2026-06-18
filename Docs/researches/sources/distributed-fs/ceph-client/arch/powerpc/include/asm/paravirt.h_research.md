<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h

## Purpose
This header provides PowerPC paravirtualization helpers for shared-processor detection, steal-time accounting, virtual CPU yield/prod operations, idle/preempt state checks, and paravirtual spin unlock selection.

## Important APIs, Types, And Functions
It declares the `shared_processor` static key and defines `is_shared_processor()`, `paravirt_steal_clock()`, `yield_count_of()`, `yield_to_preempted()`, `prod_cpu()`, `yield_to_any()`, `is_vcpu_idle()`, `vcpu_is_dispatched()`, `vcpu_is_preempted()`, and `pv_is_native_spin_unlock()`, with SPLPAR, KVM guest, and fallback variants.

## Control Flow
On shared SPLPAR systems, helpers read lppaca dispatch/yield fields and issue hypervisor calls to yield to or prod target CPUs. Fallback paths either return native defaults or reference bad-call stubs to catch impossible calls.

## State And Persistence Behavior
State is hypervisor-owned dispatch/yield accounting plus per-CPU lppaca/PACA fields. Static keys determine whether shared-processor fast paths are active.

## Dependencies And Integration Points
It depends on jump labels, SMP, PPC64 PACA/lppaca/hvcall, KVM guest detection, and cputhreads. It integrates with scheduler accounting and spinlock slow paths.

## Risks And Edge Cases
Calling yield/prod helpers on unsupported configs should fail at build/link time via bad stubs. CPU numbering must map to the correct hardware thread/lppaca. Steal-time reads need stable dispatch data.

## Test Signals
Run pseries SPLPAR under shared and dedicated modes, verify steal accounting, lock contention benchmarks, KVM guest behavior, and static-key transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h -->
