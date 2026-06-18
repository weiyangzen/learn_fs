# sources/distributed-fs/ceph-client/arch/arm/kernel/spectre.c

Purpose: reports ARM Spectre v1/v2 mitigation status through CPU vulnerability sysfs files and tracks cumulative v2 mitigation state.

Important APIs/types/functions: `cpu_show_spectre_v1`, `spectre_v2_update_state`, and `cpu_show_spectre_v2`. It checks unprivileged eBPF enablement when reporting v2 status.

Control flow: mitigation code elsewhere calls `spectre_v2_update_state` with a state and method bit. Sysfs show functions format v1 as user pointer sanitization and v2 as not affected, vulnerable, vulnerable due to unprivileged eBPF, or a mitigation method string.

State and persistence: static `spectre_v2_state` keeps the highest observed vulnerability/mitigation state; `spectre_v2_methods` ORs all mitigation methods.

Dependencies and integration: CPU vulnerability sysfs, BPF sysctl, and architecture spectre mitigation code.

Risks: status strings are user-visible security reporting; state aggregation can over/understate mixed CPU systems. Test signals include `/sys/devices/system/cpu/vulnerabilities/spectre_v*`, toggling unprivileged BPF, and CPU errata mitigation initialization.
