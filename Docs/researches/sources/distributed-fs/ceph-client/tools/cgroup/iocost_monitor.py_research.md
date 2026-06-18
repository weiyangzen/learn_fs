# sources/distributed-fs/ceph-client/tools/cgroup/iocost_monitor.py

Purpose: drgn-based monitor for blk-iocost controller state and per-cgroup IO cost statistics.

Important APIs, types, and functions: `BlkgIterator` recursively walks blkcg hierarchy and resolves `struct blkcg_gq` by queue id. `IocStat` snapshots controller-global fields such as period, vtime rates, busy level, and auto parameters. `IocgStat` snapshots per-cgroup weights, hweights, inflight, usage, wait, debt, delay, and address. Main code locates the target queue/iocg through `blkcg_root.blkg_tree`.

Control flow: Parses target device, optional cgroup regex, interval, and JSON flag; validates kernel iocost symbols; resolves constants; finds the requested device's queue id and root `ioc`; exits early for interval 0; otherwise loops, builds global and per-cgroup output, filters inactive or regex-mismatched groups, prints table or JSON lines, flushes, and sleeps.

State and persistence: Read-only against live kernel memory. Maintains local filter and interval state. No files are written.

Dependencies and integration points: Requires drgn, kernel debug info/symbols, blk-cgroup and iocost enabled, and access to live kernel memory. Integrates with block controller internals rather than stable UAPI.

Risks: Kernel structure changes can break field access. Broad exception handling while locating queues may hide unexpected errors. Table path truncates cgroup names from the left. JSON mode emits one JSON object per line rather than a single array.

Test signals: Run on kernels with and without iocost, valid and invalid device names, `--interval 0`, table and JSON modes, cgroup filtering, and inactive group omission.
