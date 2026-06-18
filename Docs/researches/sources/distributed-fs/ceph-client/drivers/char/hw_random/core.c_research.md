# sources/distributed-fs/ceph-client/drivers/char/hw_random/core.c

## Purpose
This is the common Linux hardware RNG core. It registers `/dev/hwrng`, manages registered `struct hwrng` providers, selects the current provider by quality or userspace choice, exposes sysfs controls, serializes reads, and runs a kernel thread that feeds hardware randomness into the kernel random subsystem.

## Important APIs, Types, and Functions
- Exported APIs: `hwrng_register()`, `hwrng_unregister()`, `devm_hwrng_register()`, `devm_hwrng_unregister()`, `hwrng_msleep()`, and `hwrng_yield()`.
- Provider selection: `set_current_rng()`, `drop_current_rng()`, `enable_best_rng()`, `get_current_rng()`, and `put_rng()`.
- Userspace ABI: `/dev/hwrng` via `rng_dev_open()` and `rng_dev_read()`.
- Sysfs attributes: `rng_current`, `rng_available`, `rng_selected`, and `rng_quality`.
- `hwrng_fillfn()` continuously reads from the current provider and calls `add_hwgenerator_randomness()`.

## Control Flow
Core init allocates cacheline-sized buffers and registers the misc device. Provider registration validates callbacks/name uniqueness, initializes list state, clamps quality, and may become current if it is the best provider and userspace has not pinned another. Setting current initializes the provider, swaps the RCU pointer, drops the old provider after synchronization, and starts the fill thread. Reads get a refcounted current provider, serialize hardware access with `reading_mutex`, refill `rng_buffer` as needed, copy to userspace, and handle nonblocking/signal cases.

## State and Persistence Behavior
Global state includes RCU `current_rng`, provider list, current user-selection flag, fill thread pointer, buffers, buffered byte count, quality values, and mutexes. Provider lifetime is protected by `kref`, RCU, cleanup work, and cleanup completion. The selected provider persists until unregistered or changed through sysfs.

## Dependencies and Integration Points
It integrates with miscdevice `/dev/hwrng`, sysfs device groups, provider drivers through `linux/hw_random.h`, kthreads, workqueues, RCU, krefs, and the kernel random subsystem.

## Risks
Provider callbacks run under `reading_mutex`, so slow hardware can stall user reads and the fill thread. Obsolete `current_quality` can still override provider quality. `rng_current_store()` accepts provider names from sysfs and can disable the current RNG with `none`, affecting entropy feeding.

## Test Signals
Test provider register/unregister ordering, duplicate names, provider init/cleanup failures, sysfs provider switching, `none` selection, quality changes, blocking/nonblocking `/dev/hwrng` reads, signal interruption, fill-thread startup/stop, and devm unregister behavior.
