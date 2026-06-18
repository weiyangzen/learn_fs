# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/proc.c

## Purpose

This file implements x86-specific `/proc/cpuinfo` rendering and optional per-thread x86 feature rendering for procfs. It converts `struct cpuinfo_x86`, topology data, feature bitmaps, bug bitmaps, power flags, and frequency data into the stable text interface consumed by userspace.

## Important APIs, Types, And Functions

The exported proc sequence operations are exposed through `const struct seq_operations cpuinfo_op`. Core functions are `show_cpuinfo()`, `show_cpuinfo_core()`, architecture-specific `show_cpuinfo_misc()`, iterator callbacks `c_start()`, `c_next()`, and `c_stop()`. When `CONFIG_X86_USER_SHADOW_STACK` is enabled, `arch_proc_pid_thread_features()` reports task thread feature and locked-feature masks with help from `dump_x86_features()`.

## Control Flow

The seq-file iterator walks `cpu_online_mask` and returns `cpu_data()` for each online CPU. `show_cpuinfo()` prints processor identity, model, stepping, microcode, frequency from `arch_freq_get_on_cpu()`, cache size, SMP topology, feature flags, optional VMX flags, bug strings, bogomips, TLB size, cache alignment, address widths, and power-management strings. Feature and bug output loops over the x86 capability arrays and only prints named bits.

## State, Dependencies, And Integration

The file does not persist data; it reads live CPU and task state. It depends on procfs/seq-file APIs, cpufreq, x86 feature-name arrays, topology helpers, shadow-stack prctl state, and `powerflags.c`. The output is a user-visible ABI, even though some values are informational.

## Risks And Test Signals

Changes can break parsers or expose inconsistent per-CPU data. Frequency may be unavailable, CPU hotplug can change iteration results, and feature-name arrays must remain aligned with capability bit numbering. Test signals include `cat /proc/cpuinfo`, CPU hotplug while reading, 32-bit versus 64-bit builds, VMX feature-name builds, and `/proc/<pid>/status`-style thread-feature output when shadow stack support is enabled.
