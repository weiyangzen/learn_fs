# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-core.c

## Purpose

`sun8i-ce-core.c` is the platform, capability, queue, interrupt, runtime-PM, and CryptoAPI registration layer for the Allwinner Crypto Engine used by H3/R40/D1/A64/H5/H6/H616-class SoCs. It selects a `ce_variant` from device tree, registers supported skcipher, ahash, RNG, and optional hwrng algorithms, and provides the shared descriptor execution helper used by cipher, hash, PRNG, and TRNG files.

## Important APIs, Types, And Functions

The central routines are `sun8i_ce_probe()`, `sun8i_ce_remove()`, `sun8i_ce_register_algs()`, `sun8i_ce_unregister_algs()`, `sun8i_ce_allocate_chanlist()`, `sun8i_ce_get_engine_number()`, `sun8i_ce_run_task()`, and `ce_irq_handler()`. Static `ce_variant` records encode per-SoC algorithm IDs, error-register layout, clock requirements, byte/word length quirks, word-address descriptors, PRNG/TRNG support, and clock limits. `ce_algs[]` provides CryptoAPI templates for AES/DES3 ECB/CBC, MD5/SHA* hashes, and `stdrng`.

## Control Flow

Probe allocates `sun8i_ce_dev`, maps MMIO, resolves clocks, IRQ, and reset, creates four flow engines with one coherent `ce_task` descriptor each, enables runtime PM, requests the non-secure IRQ, registers algorithms, resumes once to read the die ID and register the optional TRNG, then optionally creates debugfs stats. Crypto requests choose a flow round-robin except flow 3, which is reserved for xRNG users. `sun8i_ce_run_task()` enables the flow interrupt, writes the task descriptor address to `CE_TDQ`, starts execution via `CE_TLR`, waits for IRQ completion, and decodes variant-specific `CE_ESR` error bits.

## State And Persistence Behavior

Persistent runtime state is held in `sun8i_ce_dev`: MMIO base, clocks, reset, mutexes, flow array, round-robin atomic, variant pointer, debugfs dentries, and optional hwrng counters. Each `sun8i_ce_flow` persists its crypto engine, completion, status, coherent descriptor pointer, and physical address. Runtime PM asserts reset and disables clocks on suspend; resume re-enables declared clocks and deasserts reset. Registered TFMs hold runtime PM references through their init/exit paths.

## Dependencies And Integration Points

The file integrates with platform/OF matching, common clock/reset, runtime PM autosuspend, IRQs, DMA coherent allocation, debugfs, `crypto_engine`, internal skcipher/hash/rng registration helpers, and optional `hwrng`. Device-tree compatibles select exact variant behavior, so SoC data is part of the hardware ABI.

## Risks And Test Signals

Risks include wrong variant tables, H3 clock tuning regressions, error-register bit slicing mistakes, descriptor address-size quirks on H616, missing unwind for partially registered algorithms, RNG flow contention, and DMA timeouts hidden until real storage workloads. Test with CryptoAPI selftests plus LUKS or dm-crypt IO, per-compatible probe/remove, runtime PM suspend/resume, debugfs fallback counters, PRNG/TRNG registration, IRQ completion, and fault injection around `CE_ESR` and clock/reset failures.
