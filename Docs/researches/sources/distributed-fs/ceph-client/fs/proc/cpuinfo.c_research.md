# sources/distributed-fs/ceph-client/fs/proc/cpuinfo.c

Purpose: Registers `/proc/cpuinfo` and delegates architecture-specific CPU information iteration to `cpuinfo_op`.

Important APIs and types: Uses external `const struct seq_operations cpuinfo_op`, `cpuinfo_open()`, `cpuinfo_proc_ops`, `proc_create()`, and seq read/seek/release helpers.

Control flow: `proc_cpuinfo_init()` creates the proc entry. Opening the file calls `seq_open(file, &cpuinfo_op)`, and read/lseek/release are handled by generic seq_file operations.

State and persistence: This file stores no CPU state; architecture code behind `cpuinfo_op` supplies live or boot-time CPU data.

Dependencies and integration points: Integrates with arch CPU info providers, cpufreq headers, procfs, and seq_file. The proc ops are marked `PROC_ENTRY_PERMANENT`.

Risks: Correctness mostly depends on the architecture `cpuinfo_op`. Proc registration failure is not checked. Output format is userspace ABI for many tools.

Test signals: Boot on each architecture, hotplug CPUs if supported, verify seq iteration across all CPUs, and compare expected `/proc/cpuinfo` fields after cpufreq/topology changes.
