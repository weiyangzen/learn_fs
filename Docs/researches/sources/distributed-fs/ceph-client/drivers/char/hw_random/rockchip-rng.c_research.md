# sources/distributed-fs/ceph-client/drivers/char/hw_random/rockchip-rng.c

Purpose: Rockchip TRNG/RKRNG driver supporting RK3568, RK3576/RK3562/RK3528-style RKRNG, and RK3588 TRNGv1 blocks.

Important APIs, types, and functions: `struct rk_rng`, `struct rk_rng_soc_data`, SoC init/read/cleanup callbacks, `rk_rng_probe()`, runtime PM callbacks, and OF match data.

Control flow: probe maps registers, gets all clocks, applies required or optional resets, configures per-SoC hwrng callbacks/quality, enables runtime PM autosuspend, and registers hwrng. Reads runtime-resume, trigger generation according to SoC, poll ready/status bits, copy up to 32 bytes, clear status/control, and autosuspend.

State and persistence: per-device state stores clock bulk, base, SoC data, and device. Runtime PM init/cleanup owns clock enablement and block programming; RK3588 also configures auto-reseed.

Dependencies and integration: platform/OF, bulk clocks, reset controls, runtime PM, MMIO polling, and hwrng.

Risks and test signals: read paths ignore `wait` and always poll up to timeout; RK3576 uses RK3588 cleanup, intentionally clock-only. Tests should cover each compatible, reset optional vs required, version mismatch, timeout paths, autosuspend resume/suspend, max read length, and status clear behavior.
