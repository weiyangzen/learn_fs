<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c

## Purpose
Implements Xen PV virtual PMU integration for x86 guests. It maps Xen's per-vCPU PMU shared page into Linux perf handling, emulates PMU MSR reads/writes while a Xen PMU interrupt is being processed, exposes PMC reads, updates the PMU LAPIC LVT state through Xen, and registers perf guest callbacks so dom0 can attribute samples to guest contexts.

## Important APIs, Types, And Functions
Key state is `struct xenpmu` in `xenpmu_shared`, plus `is_xen_pmu`. CPU-family setup is in `xen_pmu_arch_init`. MSR dispatch is handled by `is_amd_pmu_msr`, `is_intel_pmu_msr`, `xen_amd_pmu_emulate`, `xen_intel_pmu_emulate`, and exported `pmu_msr_chk_emulated`. Runtime hooks are `xen_read_pmc`, `pmu_apic_update`, `xen_pmu_irq_handler`, `xen_pmu_init`, and `xen_pmu_finish`.

## Control Flow
`xen_pmu_init` allocates one zeroed page per CPU, passes its MFN to `XENPMU_init`, stores it in percpu state, and on the first success registers perf guest callbacks and initializes vendor PMU register layout. During `VIRQ_XENPMU`, the handler marks `XENPMU_IRQ_PROCESSING`, converts Xen register state into `pt_regs`, invokes `x86_pmu.handle_irq`, flushes changed PMU state with `XENPMU_flush`, and clears the flag. PMU MSR access only redirects to shared-page state while that flag is active; otherwise PMC reads fall back to native MSR reads.

## State And Persistence
State is per-CPU shared pages, per-CPU IRQ-processing flags, read-mostly vendor PMU register layout, and perf callback registration. There is no durable persistence, but hypervisor PMU registration persists until `XENPMU_finish`, CPU hotplug teardown, suspend, or shutdown.

## Dependencies And Integration Points
Depends on Xen `xenpmu_op`, `xen_pmu_data` layout, x86 vendor/CPUID MSR definitions, Linux perf x86 PMU hooks, Xen event IRQ binding in SMP code, and `xen-ops.h` declarations. It integrates with suspend/resume through `xen_arch_suspend` and `xen_arch_resume`, and with SMP PV interrupt setup through `VIRQ_XENPMU`.

## Risks And Edge Cases
High-risk areas are vendor-specific MSR range detection, AMD family 15h K7 mirror handling, Intel fixed/general/alias counter indexing, shared-page offset arithmetic, and only treating MSRs as emulated while IRQ processing is active. Hypercall failures disable or degrade PMU support. Incorrect guest-state attribution can mislead perf in dom0. HVM domains intentionally return early.

## Test Signals
Useful signals are x86 Xen PV boots with perf enabled, successful `VIRQ_XENPMU` binding, perf sampling inside dom0 and guests, MSR emulation tests for Intel fixed/general counters and AMD family 10h/15h counters, CPU hotplug PMU init/finish, and suspend/resume with PMU active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/pmu.c -->
