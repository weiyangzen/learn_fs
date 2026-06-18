<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c

Purpose: provides SH CPU identification and `/proc/cpuinfo` output.

Important APIs/types/functions: `get_cpu_subtype()`, `cpuinfo_op`, `show_cpuinfo()`, cache/flag formatting helpers.

Control flow: seq_file iteration walks `cpu_data`, skips offline CPUs, prints machine, subtype, cut, flags, cache geometry, physical bits, and bogomips.

State and persistence: state read from `cpu_data`, online CPU mask, UTS machine, and machvec system type.

Dependencies/integration: integrates CPU probe data, procfs, SMP, cache detection, and exported subtype lookup.

Risks: cpu flag strings must stay aligned with UAPI feature bits; out-of-range type indexes would mislabel CPUs.

Test signals: compare `/proc/cpuinfo` across subtypes, SMP/offline CPUs, cache variants, and feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c -->
