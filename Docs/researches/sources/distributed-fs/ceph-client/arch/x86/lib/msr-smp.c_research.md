# sources/distributed-fs/ceph-client/arch/x86/lib/msr-smp.c

## Purpose
This file provides SMP-aware wrappers for reading and writing x86 model-specific registers (MSRs) on a specified CPU or CPU mask. It lets generic kernel and module code execute MSR operations on the target CPU, return values through shared or per-CPU buffers, and choose either raw or fault-tolerant MSR access paths.

## Important APIs, Types, and Functions
The exported one-CPU APIs are `rdmsr_on_cpu()`, `rdmsrq_on_cpu()`, `wrmsr_on_cpu()`, `wrmsrq_on_cpu()`, `rdmsr_safe_on_cpu()`, `rdmsrq_safe_on_cpu()`, `wrmsr_safe_on_cpu()`, `wrmsrq_safe_on_cpu()`, `rdmsr_safe_regs_on_cpu()`, and `wrmsr_safe_regs_on_cpu()`. Multi-CPU operations are `rdmsr_on_cpus()` and `wrmsr_on_cpus()`, which take a `struct msr __percpu *` result/input area. The local callback helpers use `struct msr_info`, `struct msr_info_completion`, `struct msr_regs_info`, `call_single_data_t`, `smp_call_function_single()`, `smp_call_function_single_async()`, and `smp_call_function_many()`.

## Control Flow
Single-CPU raw reads and writes zero a `struct msr_info`, fill the MSR number and optional value, then synchronously run `__rdmsr_on_cpu()` or `__wrmsr_on_cpu()` on the target CPU. The callbacks either use `this_cpu_ptr(rv->msrs)` for per-CPU arrays or `rv->reg` for scalar results. Multi-CPU calls pin the current CPU with `get_cpu()`, execute locally if the current CPU is in the mask, then call all CPUs in the mask with `smp_call_function_many()` before `put_cpu()`. Safe read uses an asynchronous CSD plus completion so the target CPU can complete the value and error path before the caller resumes.

## State and Persistence
The file has no persistent global state. It transiently shares stack-allocated request structures with remote CPU callbacks while waiting for completion. For mask operations, persistent data is caller-owned per-CPU `struct msr` storage.

## Dependencies and Integration Points
It depends on x86 MSR primitives in `asm/msr.h`, CPU masks, SMP call-function infrastructure, per-CPU accessors, preemption control, completions, and Linux symbol exports. It is used by CPU feature, microcode, performance, virtualization, and platform code that must touch CPU-local MSRs from a non-local context.

## Risks and Test Signals
Risks include invalid target CPUs, hotplug races if callers do not constrain CPU lifetime, using raw access on absent MSRs, writing dangerous MSR values, and assuming multi-CPU operations report per-CPU failures when the raw mask helpers do not. Test signals include successful remote MSR reads on online CPUs, correct propagation of `rdmsr_safe*` and `wrmsr_safe*` errors, CPU hotplug stress, per-CPU buffer contents matching target CPUs, and fault injection with unsupported MSR numbers.
