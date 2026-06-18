<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c

## Purpose
`pwrseq.c` implements the common MMC power-sequence registry and dispatch layer. It lets platform power-sequence providers register `struct mmc_pwrseq` objects and lets MMC hosts bind to one through an `mmc-pwrseq` device-tree phandle.

## Important APIs, Types, And Functions
The exported registration API is `mmc_pwrseq_register()` and `mmc_pwrseq_unregister()`. Host-facing helpers are `mmc_pwrseq_alloc()`, `mmc_pwrseq_pre_power_on()`, `mmc_pwrseq_post_power_on()`, `mmc_pwrseq_power_off()`, `mmc_pwrseq_reset()`, and `mmc_pwrseq_free()`. Internal state is the global `pwrseq_list` protected by `pwrseq_list_mutex`.

## Control Flow
During host setup, `mmc_pwrseq_alloc()` reads the `mmc-pwrseq` phandle from the host parent's OF node, scans the registered provider list for a matching provider device node, takes the provider module reference with `try_module_get()`, and stores the provider in `host->pwrseq`. If the phandle exists but no provider has registered, it returns `-EPROBE_DEFER`. Later MMC power transitions call the dispatcher helpers, which invoke only the implemented callbacks in `pwrseq->ops`.

## State And Persistence
The file persists provider registrations in a global list and stores the selected provider pointer in `host->pwrseq`. It also owns module reference lifetime for the bound provider and drops it in `mmc_pwrseq_free()`. Hardware state changes are delegated to provider modules; this file only dispatches callbacks.

## Dependencies And Integration Points
It depends on device tree phandles, Linux module reference counting, device-node matching, MMC host state, and provider implementations in files such as `pwrseq_simple.c`, `pwrseq_emmc.c`, and `pwrseq_sd8787.c`. Core power paths call the pre/post/off/reset dispatchers around host power changes and hardware reset fallback.

## Risks And Edge Cases
Provider probe ordering can legitimately produce `-EPROBE_DEFER`. A provider with missing `ops` or `dev` is rejected at registration, but individual callbacks are optional. `try_module_get()` failure leaves the host without a pwrseq and logs an error. Unregistering a provider while a host still holds a module reference should be prevented by module lifetime, but stale device-tree references or missing providers block host probe.

## Test Signals
Validation includes hosts with no `mmc-pwrseq` phandle returning success, hosts with a phandle deferring until the provider loads, provider register/unregister operations, module reference balancing, and visible invocation of pre-power-on, post-power-on, power-off, and reset callbacks during host power transitions and hardware reset fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c -->
