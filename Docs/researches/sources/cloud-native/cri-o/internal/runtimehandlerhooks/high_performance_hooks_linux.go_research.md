# sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_linux.go

Purpose: Linux implementation of CRI-O high-performance runtime hooks for CPU isolation, IRQ balancing, CPU quota, shared CPU handling, CPU power/frequency tuning, and exec CPU affinity.

Important APIs/types/functions: `HighPerformanceHooks`, lifecycle methods `PreCreate`, `PreStart`, `PreStop`, `PostStop`, `RestoreIrqBalanceConfig`, `ServiceManager`, `CommandRunner`, CPU/IRQ constants, and helpers for cgroup v1/v2 cpuset partitioning, IRQ SMP masks, CFS quota, c-states, frequency governors, shared CPUs, housekeeping CPUs, and exec cgroups.

Control flow: `PreCreate` checks eligibility, handles shared CPU annotations, injects isolated/shared/housekeeping env vars, and sets OCI `ExecCPUAffinity`. `PreStart` resolves cgroup managers, sets shared CPU child cgroups and quotas, disables CPU/IRQ load balancing, disables quota, tunes c-state/governor files, and optionally pre-creates an exec cgroup. `PreStop` reverses load-balancing, c-state, and governor changes. `PostStop` restores IRQ affinity when needed and delegates stale cgroup load-balance cleanup to the default hook.

State and persistence behavior: writes cgroup files, `/proc/irq/default_smp_affinity`, irqbalance config, system CPU power/cpufreq files, and backup files under `/var/run/crio/cpu`. It tracks disabled IRQ-affinity container IDs in memory and caches full CPU set once.

Dependencies and integration points: integrates with CRI-O config, annotations, sandbox/container objects, OCI specs, opencontainers cgroups, systemd/cgroup managers, kube cpuset parsing, resource quantities, `systemctl`, `irqbalance`, and node cgroup version detection.

Risks: host-level writes are high impact and require locking. Cgroup v2 partition setup assumes CRI-O can manage parent cpuset files. IRQ rollback only covers part of the update path. Global service/command runners and cached CPU set must be reset in tests. Incorrect annotations can alter CPU scheduling for the node.

Test signals: extensive tests cover IRQ masks, service restart vs oneshot fallback, housekeeping sibling logic, c-state/governor save-restore, irqbalance restore, rollback on config update failure, annotation parsing, shared CPU errors, exec affinity selection, hook retrieval, and concurrent IRQ-mask updates.
