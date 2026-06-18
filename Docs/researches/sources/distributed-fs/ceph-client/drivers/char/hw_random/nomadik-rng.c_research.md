# sources/distributed-fs/ceph-client/drivers/char/hw_random/nomadik-rng.c

Purpose: AMBA driver for the ST-Ericsson Nomadik RNG block, exposing a single 16-bit sample through `hwrng`.

Important APIs, types, and functions: global `struct hwrng nmk_rng`, `nmk_rng_read()`, `nmk_rng_probe()`, `nmk_rng_remove()`, and AMBA ID table `nmk_rng_ids`.

Control flow: probe enables the clock, requests AMBA regions, ioremaps the resource, stores the base address in `nmk_rng.priv`, and registers with `devm_hwrng_register()`. Reads fetch one 32-bit register at offset 8, mask to the lower 16 bits, and return 2 bytes regardless of `wait`.

State and persistence: state is the global hwrng object's `priv` base pointer; the driver assumes at most one device. No persistence beyond device lifetime.

Dependencies and integration: depends on AMBA bus probing, `devm_clk_get_enabled()`, AMBA resource ownership, raw MMIO access, and hwrng core.

Risks and test signals: the global `nmk_rng` is not multi-instance safe; read writes a `u16` to caller buffer and assumes alignment. Tests should cover clock failure, region request failure, register mapping, unregister/remove region release, and non-waiting read latency expectations.
