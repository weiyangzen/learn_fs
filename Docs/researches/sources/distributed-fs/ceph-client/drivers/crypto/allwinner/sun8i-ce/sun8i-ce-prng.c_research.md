# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-prng.c

## Purpose

`sun8i-ce-prng.c` exposes the CE pseudo-random generator as the CryptoAPI `stdrng` implementation registered by the core file. It manages caller-provided seed storage, programs the dedicated xRNG flow, and updates the seed from generated output.

## Important APIs, Types, And Functions

The file exports `sun8i_ce_prng_init()`, `sun8i_ce_prng_exit()`, `sun8i_ce_prng_seed()`, and `sun8i_ce_prng_generate()`. It uses `struct sun8i_ce_rng_tfm_ctx` for seed pointer and length, `struct ce_task` for the hardware descriptor, and `ce->rnglock` to serialize use of flow 3.

## Control Flow

Init zeroes the RNG context. Seed replaces or allocates a sensitive GFP_DMA seed buffer and records the length. Generate refuses unseeded use, rounds requested output plus seed material to a PRNG block multiple, allocates a DMA-capable bounce output buffer, maps seed and destination, resumes the device, locks `rnglock`, fills a flow-3 task with PRNG algorithm ID, key/IV seed pointers, destination SG, and variant-specific byte/word `t_dlen`, runs `sun8i_ce_run_task()`, unlocks and drops runtime PM, then copies requested bytes to the caller and refreshes the seed from subsequent output bytes.

## State And Persistence Behavior

Seed bytes persist in the TFM context until reseed or exit and are freed with `kfree_sensitive()`. Hardware state is not persisted outside each descriptor execution. Flow 3 is a shared CE resource guarded by `rnglock`, so PRNG and TRNG serialize with each other.

## Dependencies And Integration Points

It depends on the core algorithm template for device lookup, variant PRNG algorithm IDs, task execution, runtime PM, DMA mapping, and CryptoAPI RNG callbacks. `PRNG_SEED_SIZE`, `PRNG_DATA_SIZE`, and `PRNG_LD` are defined in `sun8i-ce.h`.

## Risks And Test Signals

Risks include accepting unexpected seed lengths, output rounding mistakes, seed refresh overlap, DMA mapping failures, lack of per-request use of the `src/slen` generate arguments, and contention with TRNG on flow 3. Test unseeded failure, reseed with changed lengths, various output lengths around PRNG block size, rngtest quality, runtime PM transitions, and concurrent RNG users.
