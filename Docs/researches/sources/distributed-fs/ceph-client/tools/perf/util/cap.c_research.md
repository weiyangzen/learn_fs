# sources/distributed-fs/ceph-client/tools/perf/util/cap.c

Purpose: checks whether the current process has a Linux capability, falling back to a root-user check when `capget` cannot be used.

Important APIs/functions: exports `perf_cap__capable(int cap, bool *used_root)`.

Control flow: initializes `used_root` false, calls `SYS_capget`, retries a compatibility version case, falls back to `geteuid() == 0` on syscall failure, then extracts the requested effective capability bit from the returned capability data.

State and persistence: no persistent state; output is the boolean return plus `*used_root`.

Dependencies and integration: uses `linux/capability.h`, `syscall(SYS_capget)`, `errno`, `geteuid`, and perf debug logging. Supports permission decisions for perf features such as perfmon, syslog, or BPF access.

Risks: `used_root` must be non-NULL. Capability word selection must stay aligned with Linux capability versions. Root fallback is coarser than real capability checks.

Test signals: run under normal user, root, and file capability contexts; verify old-header compatibility and permission-sensitive diagnostics.
