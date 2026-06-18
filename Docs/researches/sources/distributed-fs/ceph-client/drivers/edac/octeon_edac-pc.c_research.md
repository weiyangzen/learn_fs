# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-pc.c

## Purpose
Registers an EDAC device for Octeon primary instruction and data cache errors. It receives cache-error notifications from architecture code, reads CP0 cache error registers, reports I-cache and D-cache CE/UE events, and clears the hardware error indication.

## Important APIs, Types, And Functions
- `struct co_cache_error` owns a notifier block and EDAC device pointer.
- `co_cache_error_event` is the notifier callback for recoverable and unrecoverable cache errors.
- `co_cache_error_probe` allocates the EDAC device with one CPU instance per possible CPU and two cache blocks.
- `co_cache_error_remove` unregisters the notifier and frees EDAC state.

## Control Flow
Probe allocates private state with devm, sets the notifier callback, allocates an EDAC device named `octeon-cpu`/`cache`, registers it with the EDAC core, and then registers the architecture cache-error notifier. When notified, the callback reads the I-cache error register and either reads the D-cache error register or consumes the saved unrecoverable D-cache error from `cache_err_dcache[core]`. It logs raw register data and error EPC, reports I-cache errors as CE, reports D-cache errors as CE or UE based on the notifier event, and clears CP0 cache error registers.

## State And Persistence
Driver state persists in `co_cache_error` and the EDAC control object. It also depends on external per-core `cache_err_dcache[]` state for unrecoverable D-cache events. Hardware CP0 error state is cleared in the notifier callback.

## Dependencies And Integration Points
Depends on Octeon architecture notifier registration functions, CP0 cache error accessors, `cache_err_dcache`, SMP CPU/core identification, and EDAC device APIs. It is registered as the `octeon_pc_edac` platform driver.

## Risks And Edge Cases
The callback returns `NOTIFY_STOP`, so notifier ordering matters. It maps I-cache errors only to CE even when the event is unrecoverable, while D-cache uses the event to choose UE. Correct indexing assumes `cvmx_get_core_num()` aligns with `cache_err_dcache[]`. Remove must unregister the notifier before freeing the EDAC device to avoid callbacks into freed memory.

## Test Signals
Trigger recoverable and unrecoverable D-cache notifications, I-cache error register bits, Octeon II D-cache clear semantics, multi-CPU instance indexing, and notifier unregister on module removal.
