# sources/distributed-fs/ceph-client/include/linux/hw_random.h

## Purpose
Defines the hardware random number generator driver contract and registration API for feeding entropy from device-specific RNGs.

## APIs, Control Flow, and State
`struct hwrng` carries driver callbacks (`init`, `cleanup`, obsolete `data_present`/`data_read`, preferred `read`), private data, quality estimate, and internal list/refcount/work/completion fields. Drivers register through `hwrng_register()` or `devm_hwrng_register()` and unregister through matching unregister functions. `hwrng_msleep()` and `hwrng_yield()` provide cooperative waits tied to RNG lifetime. State persists in the core-maintained hwrng list, reference count, cleanup work, and completion objects.

## Dependencies, Integration, Risks, and Tests
Depends on completions, krefs, workqueues, and typed kernel buffers. Integrates with the kernel hwrng core and random subsystem. Risks are implementing only obsolete callbacks, returning incorrect byte counts or quality, sleeping incorrectly in read paths, or freeing driver state before cleanup completion. Test signals include hwrng device registration, reads under blocking/nonblocking wait modes, unregister race tests, entropy quality exposure, and devm cleanup paths.
