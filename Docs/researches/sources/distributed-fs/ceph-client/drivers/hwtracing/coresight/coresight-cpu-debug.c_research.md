# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cpu-debug.c

## Purpose
`coresight-cpu-debug.c` implements the CoreSight CPU external debug module driver. It samples per-CPU debug registers, especially EDPCSR, during panic handling and exposes a debugfs knob to keep debug power domains enabled or disabled.

## Important APIs, Types, And Functions
`struct debug_drvdata` stores the MMIO base, clock, associated CPU, feature-presence flags, sampled register values, and device pointer. `debug_init_arch_data()` runs on the target CPU to read EDDEVID/EDDEVID1 and determine whether PC sampling, context ID, virtual context, and PC offset handling are implemented. `debug_read_regs()` unlocks CoreSight/debug registers, requests CPU debug power, samples EDPCSR and related registers, and restores EDPRCR. `debug_dump_regs()` formats the sampled state. `debug_adjust_pc()` handles 64-bit direct PC composition or 32-bit Arm/Thumb offset adjustment.

The panic notifier is `debug_notifier_call()`. User control is through debugfs file operations for `coresight_cpu_debug/enable`. Probe/remove are shared between AMBA and platform paths through `__debug_probe()` and `__debug_remove()`.

## Control Flow
Probe enables clocks, resolves the CPU from firmware, maps registers, stores per-CPU drvdata, calls target-CPU architecture initialization, rejects devices without EDPCSR sampling, initializes the global debugfs/notifier on the first device, and drops runtime PM if debugging is disabled. The enable debugfs write powers all present CPU debug devices; disable drops them. On panic, the notifier takes `debug_lock` opportunistically, checks `debug_enable`, loops possible CPUs, reads registers for each initialized CPU debug block, and emits emergency logs.

## State And Persistence
State is stored per CPU in `DEFINE_PER_CPU(struct debug_drvdata *, debug_drvdata)`, plus global `debug_count`, `debug_enable`, `debug_lock`, and the debugfs directory. Runtime PM references keep debug blocks powered while enabled. Sampled register fields are overwritten on each panic/read pass.

## Dependencies And Integration Points
The driver depends on CoreSight register locking macros, CPU topology lookup, AMBA/platform probing, runtime PM, clocks, panic notifiers, debugfs, SMP calls, and low-level polling. It does not register as a trace path component; it is diagnostic infrastructure adjacent to CoreSight.

## Risks
Accessing debug registers when the CPU power domain is off or the OS double lock is set can lock up hardware; the code mitigates this with EDPRSR checks and power-up requests. Panic-notifier execution must avoid blocking, hence `mutex_trylock()`. Runtime PM refcount rollback in enable failure paths is important. PC adjustment for 32-bit instruction state is architecture-specific and can be implementation-defined for misaligned samples.

## Test Signals
Tests should cover AMBA and platform probe, CPU association failures, missing EDPCSR rejection, debugfs enable/disable refcounting, runtime PM suspend/resume, panic notifier output, powered-off CPU behavior, and 32-bit Thumb/Arm PC adjustment. Fault injection for `pm_runtime_get_sync()` and `smp_call_function_single()` should verify rollback.
