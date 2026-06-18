# sources/distributed-fs/ceph-client/drivers/char/hw_random/powernv-rng.c

Purpose: bare-metal PowerNV hwrng driver for IBM POWER7+ and newer systems.

Important APIs, types, and functions: global `powernv_hwrng`, `powernv_rng_read()`, `powernv_rng_probe()`, and OF match `ibm,power-rng`.

Control flow: probe registers a single global hwrng and treats `-EEXIST` as `-ENODEV` to ignore additional matched devices. Reads compute how many native `unsigned long` values fit in the requested buffer and call `pnv_get_random_long()` for each.

State and persistence: no per-device state beyond the global hwrng. Hardware/firmware state is outside the driver.

Dependencies and integration: PowerNV arch random API, platform OF device, and hwrng core.

Risks and test signals: `powernv_rng_read()` returns 0 if `max < sizeof(unsigned long)` and assumes hwrng buffers are at least word-sized. Tests should cover duplicate device registration, small buffer handling, proper byte count, and absence of explicit wait semantics.
