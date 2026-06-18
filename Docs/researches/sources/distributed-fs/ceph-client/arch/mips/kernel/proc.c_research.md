# sources/distributed-fs/ceph-client/arch/mips/kernel/proc.c

## Purpose
Formats MIPS `/proc/cpuinfo` output and provides a raw notifier chain for platform code to append CPU-specific cpuinfo lines.

## Important APIs, Types, and Functions
- `vced_count` and `vcei_count` track VCE D/I exception counters printed in cpuinfo.
- `register_proc_cpuinfo_notifier()` and `proc_cpuinfo_notifier_call_chain()` expose extension hooks.
- `show_cpuinfo()` emits per-CPU model, ISA, ASEs, options, topology, watchpoint, timer, cache, and platform data.
- `cpuinfo_op` is the exported `seq_operations` for procfs iteration.

## Control Flow
The procfs seq iterator maps positions to CPU indexes. `show_cpuinfo()` skips offline CPUs under SMP, prints system type and machine name for CPU 0, reports model/FPU/BogoMIPS/wait/timer/TLB/watch details, appends feature strings from `cpu_has_*` predicates, prints topology/VPE data, reports VCE counters, then invokes the notifier chain with `proc_cpuinfo_notifier_args`.

## State and Persistence
No persistent storage. It reads `cpu_data[]`, feature flags, topology, and exception counters at display time. The notifier chain is statically initialized and expected to be registered during early boot.

## Dependencies and Integration Points
Depends on MIPS CPU feature probing, `get_system_type()`, `mips_get_machine_name()`, seq_file, procfs, and optional platform notifiers. It consumes machine name set by `prom.c` and CPU data initialized by `setup.c`.

## Risks
Feature list drift can hide or misreport CPU capabilities. The raw notifier has no lock and is documented as early-boot-only for writes. CPU hotplug can produce sparse cpuinfo entries. Formatting changes may affect user-space parsers.

## Test Signals
`cat /proc/cpuinfo` should show correct system/machine names, online CPU entries, feature flags, watchpoint masks, topology, and notifier-provided platform lines. Offline CPUs should not print stale entries on SMP.
