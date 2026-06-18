# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.h

## Purpose
This header defines the per-channel ZL3073x DPLL object and the registration/monitoring APIs used by the common core.

## Important APIs and types
`struct zl3073x_dpll` stores list linkage, parent `zl3073x_dev`, channel ID, monitor flags, ops copy, registered `dpll_device`, tracker, cached lock status, pin list, and change-notification work. Declared APIs allocate/free, register/unregister, initialize fine phase adjustment, and check for changes.

## Control flow and state
The core allocates one object per hardware channel during probe, registers it during `zl3073x_dev_start()`, and unregisters/frees it through devres cleanup. Periodic work calls `zl3073x_dpll_changes_check()` for each list entry.

## Risks and tests
The structure mixes registration lifetime and periodic work state, so unregister must cancel work before dropping DPLL references. Tests should cover probe failure unwinding and reload/flash stop-start cycles.
