# sources/distributed-fs/ceph-client/drivers/char/hw_random/pasemi-rng.c

Purpose: PA Semi PWRficient on-chip RNG driver.

Important APIs, types, and functions: global `pasemi_rng`, `pasemi_rng_init()`, `pasemi_rng_cleanup()`, `pasemi_rng_data_present()`, `pasemi_rng_data_read()`, and `rng_probe()`.

Control flow: probe maps the platform resource, stores the base in the global hwrng, and registers it. Init resets/selects the raw random generator source and key size. Data-present polls the valid-count field up to 20 times with 10 microsecond delays. Data-read reads the value register. Cleanup clears random-generator enables.

State and persistence: global hwrng state contains the MMIO base in `priv`; hardware state is enable bits in the control register. No persistence.

Dependencies and integration: platform OF matching, little-endian MMIO helpers, delay loops, and hwrng core.

Risks and test signals: global state is not multi-instance safe and `data_read()` trusts `data_present()` sequencing. Tests should cover control-register programming, valid-count polling with and without wait, cleanup clearing both RNG sources, OF aliases, and mapping/registration failure.
