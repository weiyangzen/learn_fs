# sources/distributed-fs/ceph-client/drivers/char/hw_random/pic32-rng.c

Purpose: Microchip PIC32 RNG driver exposing enhanced TRNG mode through hwrng.

Important APIs, types, and functions: `struct pic32_rng`, `pic32_rng_init()`, `pic32_rng_read()`, `pic32_rng_cleanup()`, and `pic32_rng_probe()`.

Control flow: probe allocates state, maps MMIO, enables clock, fills hwrng hooks, and registers. Init writes `TRNGEN | TRNGMOD`. Read polls `RNGRCNT` until 64 bits are available, reads seed registers as a 64-bit sample, and returns 8 bytes; if not ready it loops only for blocking reads and otherwise returns `-EIO`. Cleanup disables `RNGCON`.

State and persistence: per-device base pointer and hwrng object; hardware enable state lives in `RNGCON`.

Dependencies and integration: platform/OF matching, clock framework, MMIO, and hwrng core.

Risks and test signals: read casts `buf` to `u64 *`, so alignment and `max >= 8` assumptions depend on hwrng core. Tests should cover non-waiting unavailable data, timeout behavior, clock failures, init/cleanup writes, and seed register ordering.
