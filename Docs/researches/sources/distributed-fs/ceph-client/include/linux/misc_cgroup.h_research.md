# sources/distributed-fs/ceph-client/include/linux/misc_cgroup.h

## Purpose
Defines the miscellaneous cgroup controller interface for accounting and limiting special host resources such as SEV/SEV-ES ASIDs and TDX HKIDs when configured.

## Important APIs/Types
`enum misc_res_type` is Kconfig-dependent and ends at `MISC_CG_RES_TYPES`. With `CONFIG_CGROUP_MISC`, `struct misc_res` tracks max, watermark, usage, events, and local events; `struct misc_cg` embeds cgroup state, event files, and resource accounting. APIs set capacity, try-charge, uncharge, map CSS to misc cgroup, get current task's misc cgroup, and put references. Disabled stubs are no-ops.

## Control Flow
Providers set capacity, charge before allocation, and uncharge on release. `get_current_misc_cg` obtains a referenced cgroup and callers later call `put_misc_cg`.

## State And Persistence
Persistent state is per-cgroup counters and event files. References must be balanced.

## Dependencies And Integration Points
Integrates with cgroup core, KVM SEV, Intel TDX, atomic counters, and resource providers needing misc accounting.

## Risks
Kconfig-dependent enum shape, charge/uncharge imbalance, assuming enforcement exists with config disabled, reference leaks, and capacity drift.

## Test Signals
Capacity/limit behavior, watermark/event updates, cgroup file reads, VM create/destroy charge balance, CONFIG-disabled behavior, and refcount leak checks.
