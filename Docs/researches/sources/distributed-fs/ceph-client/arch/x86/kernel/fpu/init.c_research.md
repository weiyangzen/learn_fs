# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/init.c

## Purpose
Performs boot and CPU-online FPU initialization, legacy no-CPUID probing, MXCSR mask detection, xstate sizing bootstrap, and dynamic task-struct sizing.

## Important APIs, Types, And Functions
`fpu__init_cpu()` initializes CR0/CR4 and CPU xstate, then enables kernel FPU use on the CPU. `fpu__probe_without_cpuid()` detects legacy FPU presence. `fpu__init_system()` is the boot CPU orchestration entry. Helpers initialize MXCSR mask, default fpstate, legacy xstate sizes, and `arch_task_struct_size`.

## Control Flow
System init sets `TIF_NEED_FPU_LOAD`, probes FPU if CPUID is unavailable, halts if no FPU and no math emulation, initializes the boot CPU FPU, builds default fpstate, reads MXCSR mask through FXSAVE, seeds legacy sizes, calls xstate initialization, and computes the task allocation size with the dynamic fpstate size. CPU-online init sets CR4 OSFXSR/OSXMMEXCPT, clears CR0 TS/EM as appropriate, initializes x87, and enables kernel FPU sections.

## State, Persistence, And Dependencies
Persistent state includes CPU feature caps, `mxcsr_feature_mask`, `init_fpstate`, FPU config sizes/features, `arch_task_struct_size`, CR0/CR4 bits, and per-CPU `kernel_fpu_allowed`. It depends on xstate init, task allocation layout, math emulation config, and CPU feature detection.

## Integration Points
Runs before task creation and CPU hotplug FPU usage; its sizing directly affects task slab layout and `x86_task_fpu()` pointer arithmetic.

## Risks
Task-struct sizing requires `struct fpu.__fpstate` to remain last. Incorrect MXCSR mask or xstate sizes break signal/ptrace/KVM ABIs. FPU absence without emulation is fatal by design.

## Test Signals
Boot should report valid FPU/xstate sizing, online CPUs should allow kernel FPU after init, no-CPUID legacy systems should probe accurately, and task allocation should satisfy FPU alignment assumptions.
