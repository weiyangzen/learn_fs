
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/xilinx-trng.c

Purpose: AMD/Xilinx Versal True Random Number Generator driver. It registers both a crypto RNG named `stdrng` with driver `xilinx-trng` and an hwrng provider backed by Versal TRNG hardware.

Important APIs, types, and functions: `struct xilinx_rng` stores MMIO base, scratchpad, AES derivation-function key, mutex, and `hwrng`. `xtrng_collect_random_data()` starts PRNG/TRNG output and reads 16-byte chunks from output registers. `xtrng_reseed_internal()` enables entropy mode, collects seed material, runs `crypto_drbg_ctr_df()`, writes external seed registers, and triggers reseed. `xtrng_random_bytes_generate()` enables PRNG mode, reads random bytes, then reseeds. Crypto RNG hooks are `xtrng_trng_generate()`, `xtrng_trng_seed()`, and `xtrng_trng_init()`. HWRNG read is `xtrng_hwrng_trng_read()`. Probe/reset/remove own registration and sanitization.

Control flow: probe maps MMIO, allocates AES key and derivation-function scratchpad, resets hardware, performs an initial reseed, sets the global device pointer, initializes mutex, registers crypto RNG, then registers hwrng. Generate/read paths serialize through the mutex, collect requested bytes with optional polling waits, reseed after each generation, and return either crypto success or number of bytes read. Remove unregisters providers, zeros seed registers, holds reset, and clears the global pointer.

State and persistence: hardware state includes control, status, reset, oscillator enable, external seed, personalization, and output registers. Software state includes the global `xilinx_rng_dev`, mutex, scratchpad buffer, and AES key schedule storage. Seed-related buffers/registers are explicitly zeroed in remove and some error paths.

Dependencies and integration points: depends on platform/OF compatible `"xlnx,versal-trng"`, MMIO polling, hwrng framework, crypto RNG API, DRBG CTR derivation function, AES internals, and firmware headers.

Risks and test signals: `xtrng_hwrng_trng_read()` returns the last generation return value rather than total bytes copied, which may underreport successful multi-block reads. `xtrng_readwrite32()` takes a `u8 value` while masks include bits above 7, so setting `TRNG_CTRL_EUMODE_MASK` through this helper would not work if used that way; current high-bit writes mostly use `iowrite32()`. Frequent reseed-after-generate may affect throughput. Test signals include crypto RNG selftests, hwrng reads with wait and non-wait modes, entropy/reseed timeout injection, register zeroization on remove, concurrent readers, and partial byte requests.
