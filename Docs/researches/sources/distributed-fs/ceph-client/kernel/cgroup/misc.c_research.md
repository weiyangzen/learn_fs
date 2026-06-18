# sources/distributed-fs/ceph-client/kernel/cgroup/misc.c

## Purpose

`misc.c` implements the miscellaneous cgroup controller for scalar host resources that do not justify a dedicated controller, such as AMD SEV/SEV-ES ASIDs and Intel TDX HKIDs when configured.

## Important APIs, Types, and Functions

The controller uses `struct misc_cg` and `struct misc_res` from `linux/misc_cgroup.h`, a root `misc_cg`, and global `misc_res_capacity[]`. Exported APIs are `misc_cg_set_capacity()`, `misc_cg_try_charge()`, and `misc_cg_uncharge()`. User files are `misc.max`, `misc.current`, `misc.peak`, `misc.capacity`, `misc.events`, and `misc.events.local`.

## Control Flow and State

Resource providers set host capacity with `misc_cg_set_capacity()`. Charging walks from the target cgroup to the root, atomically adding usage and checking both the cgroup's `max` and host capacity. On failure, it increments local and hierarchical event counters, notifies the relevant cgroup files, and cancels all partial charges. Uncharge walks the same hierarchy and subtracts usage. Watermarks are maintained with a compare/exchange loop.

## Dependencies and Integration Points

The file integrates with cgroup core cftypes, atomic64 counters, cgroup file notification, and resource providers in KVM/TDX code that call the exported charge APIs around resource allocation and free.

## Risks and Edge Cases

No global mutex protects limit updates or capacity updates, so correctness relies on atomic counters and `READ_ONCE`/`WRITE_ONCE`; racing changes may make a charge observe old limits. The capacity value `0` means unsupported/uninitialized and causes charge failure. Charge/uncharge symmetry is essential, and underflow produces a warning. Event propagation differs between local and hierarchical files.

## Test Signals

Tests should register nonzero and zero capacities, write numeric and `max` limits, charge below and above limits, check rollback after failures, verify peak/current/capacity output, assert events and events.local notifications, and run concurrent charge/uncharge stress.
