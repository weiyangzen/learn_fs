# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.h

## Purpose
`ena_phc.h` declares ENA PHC state and the PHC lifecycle/query functions shared by the core driver, ethtool timestamp reporting, devlink parameter code, and PHC implementation.

## Important APIs, Types, And Functions
`struct ena_phc_info` contains `ptp_clock_info`, registered `ptp_clock *`, back-pointer to `ena_adapter`, a spinlock, and an `enabled` flag. Public functions are `ena_phc_enable()`, `ena_phc_is_enabled()`, `ena_phc_is_active()`, `ena_phc_get_index()`, `ena_phc_init()`, `ena_phc_destroy()`, `ena_phc_alloc()`, and `ena_phc_free()`.

## Control Flow, State, And Integration
The header has no executable logic, but its state controls whether `ena_phc_init()` will register a PTP clock. `enabled` is kernel/devlink policy, while `clock` indicates active registration. `ena_ethtool.c` calls `ena_phc_get_index()` for timestamp info. `ena_netdev.c` allocates PHC state during probe, initializes during device init/restore, destroys during device teardown, and frees during remove.

## Dependencies
It depends on `<linux/ptp_clock_kernel.h>` and a visible `struct ena_adapter` declaration through including context. It is coupled to `ena_netdev.h` by the adapter’s `phc_info` pointer.

## Risks And Test Signals
Risks are mostly lifetime-related: dangling adapter pointers, double registration, freeing `phc_info` while a PTP clock is active, or incorrectly treating `enabled` as active registration. Test signals include PHC allocation/free under probe-failure unwinds, reset with PHC active, ethtool timestamp output when disabled, and devlink PHC enable/disable paths.
