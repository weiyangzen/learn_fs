# sources/distributed-fs/ceph-client/drivers/char/hw_random/pseries-rng.c

Purpose: IBM pSeries VIO hwrng driver backed by the `H_RANDOM` hypervisor call.

Important APIs, types, and functions: `pseries_rng_read()`, `pseries_rng_get_desired_dma()`, global `pseries_rng`, VIO probe/remove, and module init/exit.

Control flow: module init registers a VIO driver. Probe registers the global hwrng. Reads call `plpar_hcall(H_RANDOM)`, copy 8 bytes on success, and return `-EIO` with ratelimited logging on failure. Remove unregisters hwrng; exit unregisters the VIO driver.

State and persistence: global hwrng only; no driver-private persistent state. DMA desired size is always zero for CMO environments.

Dependencies and integration: pSeries VIO bus, POWER hypervisor call ABI, hwrng core, and module init/exit.

Risks and test signals: global hwrng is not multi-instance safe, though VIO match likely exposes one RNG. Tests should cover H_RANDOM failure, probe/remove registration pairing, CMO callback returning zero, and fixed 8-byte response semantics.
