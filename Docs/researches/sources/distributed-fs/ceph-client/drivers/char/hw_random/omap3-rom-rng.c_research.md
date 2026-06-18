# sources/distributed-fs/ceph-client/drivers/char/hw_random/omap3-rom-rng.c

Purpose: Nokia N900/OMAP3 ROM RNG wrapper that obtains random data by calling platform ROM code.

Important APIs, types, and functions: `struct omap_rom_rng`, `omap3_rom_rng_read()`, runtime suspend/resume handlers, `omap_rom_rng_finish()`, and `omap3_rom_rng_probe()`.

Control flow: probe obtains the hwrng read function from OF match data, platform ROM callback from `platform_data`, clock `ick`, enables runtime PM autosuspend, registers cleanup action, and registers hwrng. Read runtime-resumes, passes the physical address of the caller buffer to ROM with `RNG_GEN_HW`, returns 4 bytes on success, then autosuspends. Runtime resume enables the clock and initializes ROM RNG; suspend resets ROM RNG and disables the clock.

State and persistence: per-device state stores clock, device, hwrng ops, and ROM callback. No persistent state beyond PM configuration.

Dependencies and integration: platform data callback is mandatory, OF match supplies read method, uses runtime PM, clock framework, physical address conversion, and hwrng.

Risks and test signals: `virt_to_phys(data)` assumes a directly mapped kernel buffer suitable for ROM DMA/write. Tests should cover missing callback/match data, clock failures, ROM init/reset failure logging, runtime PM read error path, and autosuspend cleanup action.
