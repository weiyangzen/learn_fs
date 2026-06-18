# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-trng.c

## Purpose

`sun8i-ce-trng.c` registers the CE true random generator with the kernel hwrng framework when the selected variant advertises TRNG support. It supports both old and v2 TRNG algorithm IDs, with comments noting that only the second generation is reliable under rngtest.

## Important APIs, Types, And Functions

The main callbacks are `sun8i_ce_trng_read()`, `sun8i_ce_hwrng_register()`, and `sun8i_ce_hwrng_unregister()`. The read path programs a `ce_task` on flow 3, uses `ce->trng.read` as the hwrng callback, and records optional debug counters on `sun8i_ce_dev`.

## Control Flow

Register returns early when the variant has `CE_ID_NOTSUPP`; otherwise it names the hwrng and calls `hwrng_register()`. Reads round the requested byte count to a 32-byte multiple, allocate a sensitive DMA-capable buffer, map it for device output, resume the CE, lock `rnglock`, build a TRNG task descriptor with variant-specific length units and one destination segment, execute flow 3, unlock and drop runtime PM, copy exactly `max` bytes to the hwrng buffer on success, and return the byte count.

## State And Persistence Behavior

No per-consumer state is stored. Hardware execution is per read and serialized by `rnglock` with PRNG. The hwrng registration object lives inside `sun8i_ce_dev` and is unregistered during core driver removal.

## Dependencies And Integration Points

It integrates with the CE core variant table, `sun8i_ce_run_task()`, runtime PM, DMA mapping, Linux hwrng, and optional debug counters. Registration is called from `sun8i_ce_probe()` only after the device has been runtime-resumed.

## Risks And Test Signals

Risks include exposing unreliable first-generation TRNG variants, returning `-ENOMEM` from hwrng read paths under pressure, length unit mismatches, flow-3 contention with PRNG, and ignoring the hwrng `wait` argument. Test hwrng registration on TRNG and non-TRNG compatibles, `rngtest` quality on H6/D1/H616, short and long reads, concurrent RNG access, runtime PM, and remove/unregister sequencing.
