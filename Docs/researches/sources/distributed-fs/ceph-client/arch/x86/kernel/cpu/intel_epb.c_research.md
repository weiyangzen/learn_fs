# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/intel_epb.c

Purpose: manages Intel Energy Performance Bias (EPB) across CPU hotplug and system sleep, and exposes a sysfs knob for user policy.

Important APIs and flow: per-CPU `saved_epb` stores the low EPB bits plus an internal saved marker. `intel_epb_save()` reads `MSR_IA32_ENERGY_PERF_BIAS`; `intel_epb_restore()` writes the saved value back or changes firmware-default `performance` to `normal` on first online. Syscore callbacks save/restore the boot CPU during suspend/resume. CPU hotplug callbacks restore EPB on online, save on offline, and merge/unmerge the `power/energy_perf_bias` sysfs group. The sysfs show/store path accepts raw 0-15 values or named strings such as `performance`, `normal`, and `power`. `intel_epb_init()` gates on `X86_FEATURE_EPB`, applies model-specific normal defaults, installs CPUHP state, and registers syscore ops.

State and persistence: EPB lives in per-CPU MSRs and is shadowed in per-CPU RAM across offline/suspend transitions. User writes persist until firmware resets MSRs or the CPU is removed without restore.

Dependencies and integration: depends on CPU hotplug, syscore PM, CPU device sysfs, x86 CPU matching, and MSR access helpers.

Risks and test signals: risks include losing user EPB policy across suspend/hotplug or writing unavailable CPUs. Signals include sysfs read/write behavior, suspend/resume retention, CPU offline/online retention, and boot warning when EPB is normalized from firmware `performance`.
