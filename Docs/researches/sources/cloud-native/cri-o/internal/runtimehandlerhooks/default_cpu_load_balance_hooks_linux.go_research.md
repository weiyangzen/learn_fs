# sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_linux.go

Purpose: Linux hook that disables `cpuset.sched_load_balance` on stopped container cgroups to avoid stale cgroups interfering with exclusive CPU scheduling.

Important APIs/types/functions: `DefaultCPULoadBalanceHooks` embeds `cgmgr.CgroupManager`; lifecycle no-op methods; `PostStop`.

Control flow: `PostStop` skips spoofed containers and cgroup v2, errors if no cgroup manager exists, resolves pod/container cgroup managers, and calls `disableCPULoadBalancingV1`.

State and persistence behavior: writes cgroup v1 cpuset files through helper functions; no CRI-O state is stored.

Dependencies and integration points: integrates with cgroup manager abstractions, node cgroup-version detection, sandbox cgroup parent, and container ID.

Risks: only meaningful on cgroup v1. Missing or stale cgroup paths can cause post-stop errors. Incorrect writes can affect CPU scheduling for unrelated cgroups.

Test signals: high-performance hook tests verify default hook selection when CPU-load-balancing annotations are allowed globally.
