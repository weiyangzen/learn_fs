# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/rng.c

## Purpose
`rng.c` exposes supported ath9k AR9300-generation devices as Linux `hwrng` providers. It samples ADC/PHY observation registers, filters repeated or sentinel values, and registers a device-managed random source with the kernel.

## Important APIs, types, and functions
`ath9k_rng_start()` names and registers `sc->rng_ops` for AR9300 2.0 or later devices, with `quality = 320`. `ath9k_rng_stop()` unregisters it. `ath9k_rng_read()` implements the `struct hwrng` read callback with optional blocking/retry behavior. `ath9k_rng_data_read()` wakes the device, selects PHY observation sources, reads `AR_PHY_TST_ADC`, filters invalid pairs, updates `sc->rng_last`, and returns bytes produced. `ath9k_rng_delay_get()` backs off after repeated empty reads.

## Control flow and integration
Startup is called from ath9k device initialization and is skipped for old revisions or already registered RNGs. Reads enter through the hwrng core, wake the hardware using ath9k power-save helpers, configure observation muxes, sample pairs into 32-bit words, restore power state, and return either produced bytes or `-EIO` if a blocking read repeatedly fails. Registration uses `devm_hwrng_register`, while stop explicitly unregisters if active.

## State and persistence behavior
The persistent software state is `sc->rng_ops.read`, `sc->rng_name`, and `sc->rng_last`. `rng_last` suppresses duplicate sample reuse across reads. Hardware observation mux state is changed for sampling but not stored by this file beyond register writes.

## Dependencies
The file depends on Linux `hw_random`, ath9k power management, `ath9k.h`, `hw.h`, and AR9003 PHY register definitions. It relies on `REG_READ`, `REG_RMW_FIELD`, and `REG_CLR_BIT`.

## Risks
Risks include low entropy under poor RF/ADC conditions, repeated empty reads causing latency, interaction with PHY observation state used by diagnostics, and assuming AR9300 ADC behavior across all supported revisions. The warning in carl9170's RNG Kconfig does not apply directly, but any hardware RNG over device buses should still be treated conservatively.

## Test signals
Signals include hwrng registration visibility, successful reads with nonzero byte counts, no power-save imbalance, no repeated `-EIO` under normal RF conditions, entropy health tests in the hwrng framework, and suspend/remove paths leaving no registered callback.
