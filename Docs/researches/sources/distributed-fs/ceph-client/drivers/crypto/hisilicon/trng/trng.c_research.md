# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/trng.c

## Purpose
This file implements the HiSilicon true random number generator v2 platform driver. It exposes hardware random data through the hwrng framework and, on non-v1 hardware, exposes a Crypto API `stdrng` implementation backed by a hardware/software DRBG register interface.

## Important APIs, Types, And Functions
Key types are `struct hisi_trng`, representing one mapped TRNG device; `struct hisi_trng_list`, the global load-balancing list of devices; and `struct hisi_trng_ctx`, a Crypto API context holding the selected device. The hwrng path uses `hisi_trng_read()`. The Crypto API RNG path uses `hisi_trng_alg` with `hisi_trng_init()`, `hisi_trng_exit()`, `hisi_trng_seed()`, and `hisi_trng_generate()`.

Register helpers include `hisi_trng_set_seed()` to program 48 bytes of seed into 12 seed registers and initialize the DRBG, `hisi_trng_reseed()` to reseed from raw TRNG data after bytes have been generated, and `hisi_trng_get_bytes()` to poll DRBG status, read four 32-bit data registers, copy up to 16 bytes per round, and trigger the next generation.

## Control Flow
Probe allocates `struct hisi_trng`, maps MMIO, initializes locks and version, initializes the global list once, adds the device, optionally registers the Crypto API RNG once using `trng_active_devs`, then registers an hwrng with quality 512. Crypto RNG init chooses the currently least-used TRNG by `ctx_num`, increments its context count, and generation takes the per-device mutex while producing data in chunks up to `SW_MAX_RANDOM_BYTES`. Remove waits until no Crypto API contexts reference the device, then unregisters the Crypto RNG when the last non-v1 device is removed.

## State And Persistence
Runtime state includes the global TRNG device list, active non-v1 device count, per-device context count, MMIO base, hardware version, RNG registration, and `random_bytes` since last seed. There is no persistent storage. Seed material is stack/local data and device registers; the code does not explicitly scrub the temporary reseed buffer.

## Dependencies And Integration Points
The driver depends on ACPI platform enumeration (`HISI02B3`), hwrng, Crypto API RNG internals, MMIO polling, and kernel random headers. It integrates with users through `/dev/hwrng`/hwrng consumers and Crypto API consumers of `stdrng`/`hisi_stdrng`.

## Risks
`hisi_trng_remove()` busy-waits while contexts exist, which can stall module removal. `hisi_trng_init()` assumes the global list is non-empty; a race with remove is mitigated by list locking but depends on registration lifetime. Reseed behavior uses raw TRNG output only after prior generation, so initial `random_bytes = SW_MAX_RANDOM_BYTES` forces first generation through reseed. Poll timeouts return partial hwrng data on raw reads but `-EIO` on DRBG paths.

## Test Signals
Test hwrng reads, Crypto API RNG seed/generate, short seed rejection, large generate split at `SW_MAX_RANDOM_BYTES`, probe/remove with multiple devices, v1 behavior without Crypto API RNG registration, and timeout/error paths via fault injection. Lockdep is useful around list and per-device mutex use.
