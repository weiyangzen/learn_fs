# sources/distributed-fs/ceph-client/kernel/printk/sysctl.c

## Purpose
`printk/sysctl.c` registers the `/proc/sys/kernel` sysctl controls for printk behavior, rate limiting, devkmsg policy, dmesg restrictions, and kernel pointer exposure restrictions.

## Important APIs, types, and functions
`printk_sysctls[]` declares entries for `printk`, `printk_ratelimit`, `printk_ratelimit_burst`, `printk_delay`, `printk_devkmsg`, `dmesg_restrict`, and `kptr_restrict`. `proc_dointvec_minmax_sysadmin()` wraps `proc_dointvec_minmax()` and requires `CAP_SYS_ADMIN` on writes. `printk_sysctl_init()` registers the table under `kernel`.

## Control flow
During printk sysctl initialization, the table is registered once. Reads and writes then dispatch to standard proc handlers. `printk_delay` is bounded between zero and `ten_thousand`. `dmesg_restrict` and `kptr_restrict` use the CAP_SYS_ADMIN-enforcing wrapper and min/max bounds. `printk_devkmsg` delegates parsing to `devkmsg_sysctl_set_loglvl()`.

## State and persistence behavior
The file exposes existing kernel variables rather than owning persistent state: `console_loglevel`, `printk_ratelimit_state.interval`, `printk_ratelimit_state.burst`, `printk_delay_msec`, `devkmsg_log_str`, `dmesg_restrict`, and `kptr_restrict`. Changes persist only for the running kernel unless userspace reapplies them.

## Dependencies and integration points
It integrates proc sysctl registration, capability checks, printk internals, ratelimit state, and security-sensitive kernel information controls consumed by `/proc/kmsg`, `dmesg`, and pointer formatting.

## Risks and invariants
Permission and bounds are the key risks. Relaxing write checks for `dmesg_restrict` or `kptr_restrict` can expose sensitive data; missing bounds on `printk_delay` can create pathological stalls. The table data pointers must match object sizes and handler expectations.

## Test signals
Useful tests are sysctl read/write permission checks as privileged and unprivileged users, min/max validation, `printk_devkmsg` string parsing, rate-limit behavior changes, and verifying `register_sysctl_init("kernel", ...)` creates the expected entries.
