# sources/distributed-fs/ceph-client/drivers/char/hw_random/octeon-rng.c

Purpose: Cavium Octeon RNG driver exposing RNM hardware through `hwrng`.

Important APIs, types, and functions: `struct octeon_rng`, `octeon_rng_init()`, `octeon_rng_cleanup()`, `octeon_rng_data_read()`, and `octeon_rng_probe()`.

Control flow: probe fetches two memory resources, maps control/status and result registers, copies a local `hwrng` template into per-device state, and registers it. Init writes RNM control bits to enable entropy and RNG; cleanup writes zero; data reads one 32-bit value from the result CSR and returns 4 bytes.

State and persistence: per-device state stores the hwrng ops and two mapped CSR pointers. Hardware enable state is controlled by hwrng init/cleanup and is not persisted.

Dependencies and integration: depends on Octeon architecture headers (`cvmx_*`), platform memory resources, devm allocation/mapping, and hwrng core.

Risks and test signals: probe maps fixed 64-bit CSR windows and returns `-ENOENT` for several distinct failures. Tests should cover missing resources, mapping failures, hwrng registration failure, init/cleanup CSR writes, and repeated reads while enabled.
