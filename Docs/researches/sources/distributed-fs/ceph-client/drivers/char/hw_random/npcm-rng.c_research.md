# sources/distributed-fs/ceph-client/drivers/char/hw_random/npcm-rng.c

Purpose: platform hwrng driver for Nuvoton NPCM RNG variants.

Important APIs, types, and functions: `struct npcm_rng`, `npcm_rng_init()`, `npcm_rng_cleanup()`, `npcm_rng_read()`, runtime PM callbacks, and OF matches for `nuvoton,npcm750-rng` and `nuvoton,npcm845-rng`.

Control flow: probe allocates state, maps registers, enables runtime PM, selects clock programming from match data, sets mode, and registers `hwrng`. Reads runtime-resume the device, then either poll `NPCM_RNG_DATA_VALID` or return immediately if non-waiting; each ready iteration reads one byte from `NPCM_RNGD_REG`.

State and persistence: per-device state holds base, hwrng object, device pointer, and clock-programming bits. Runtime PM suspend disables RNG while keeping clock-selection bits.

Dependencies and integration: uses platform MMIO, OF match data, `readb_poll_timeout()`, runtime PM autosuspend, and hwrng registration.

Risks and test signals: `pm_runtime_get_sync()` return is ignored in read, so PM failures may be masked. Tests should validate timeout path returns `-EIO` only for blocking reads with no bytes, autosuspend/resume toggles enable bits, match-data clock fields, and cleanup on registration failure/remove.
