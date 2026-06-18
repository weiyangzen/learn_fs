<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h

Purpose: defines central x86 CPU and task-processor state used across boot, scheduling, entry code, CPU feature detection, idle, mitigations, and low-level helpers. Important APIs/types include `cpuinfo_topology`, `cpuinfo_x86`, x86 vendor IDs, `x86_hw_tss`, `x86_io_bitmap`, `tss_struct`, entry/IRQ stack objects, `thread_struct`, `task_pt_regs()`, CR3 helpers, prefetch helpers, `start_thread()`, TSC control macros, LLC/L2 helpers, AMD divider clearing, L1TF/MDS mitigation enums, and `weak_wrmsr_fence()`.

Control flow: most logic is inline glue that callers use during CPU bring-up, context switching, entry handling, and mitigation paths. Boot and CPU hotplug populate `boot_cpu_data`, `new_cpu_data`, and per-CPU `cpu_info`; scheduler and entry code consume `thread_struct`, top-of-stack, TSS, and I/O bitmap fields; CR3 and CR4-related users rely on the helper wrappers to preserve encryption and serialization constraints.

State and persistence: owns declarations for per-CPU CPU descriptors, TSS pages, IRQ stack pointers, top-of-stack values, task thread state, CPU capability masks, bootloader identity, mitigation settings, and cache-coherency indicators. All state is runtime kernel state, with some fields visible through `/proc/cpuinfo`, ELF aux vectors, ptrace/debug paths, and task context switches.

Dependencies and integration points: includes FPU, segments, page tables, CPUID, special instructions, percpu, memory encryption, shadow stack, and paravirt hooks. It integrates with scheduler switch code, entry assembly, SMP bring-up, CPU detection, microcode, idle selection, x86 mitigations, FPU state placement, and TSS/I/O permission management.

Risks: layout changes in `thread_struct`, `pt_regs` placement helpers, TSS, or I/O bitmap offsets can break entry assembly and hardware ABI expectations. Capability and topology fields feed userspace ABI and mitigation decisions. CR3 and WRMSR helpers must preserve SME encryption bits and ordering for weakly ordered MSR uses. Test signals include boot on 32/64-bit, SMP CPU hotplug, ptrace/FPU/debug register tests, I/O permission tests, idle selection, `/proc/cpuinfo`, and mitigation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/processor.h -->
