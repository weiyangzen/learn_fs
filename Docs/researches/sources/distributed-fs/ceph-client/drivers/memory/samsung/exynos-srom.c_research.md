# sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.c

Purpose: Samsung Exynos SROM controller driver for static external memory banks. It configures child bank timing from device tree, populates child devices when all banks decode successfully, and saves/restores SROM registers across system sleep.

Important APIs/types/functions: `struct exynos_srom_reg_dump` stores register offset/value pairs. `struct exynos_srom` stores device, MMIO base, and register dump array. Key helpers are `exynos_srom_alloc_reg_dump()`, `exynos_srom_configure_bank()`, `exynos_srom_probe()`, `exynos_srom_save()`, and `exynos_srom_restore()`.

Control flow: probe maps the controller resource, allocates dump entries for `BW` and `BC0..BC3`, then iterates child nodes. Each child must provide `reg` and `samsung,srom-timing`; `reg-io-width` defaults to 1 byte and `samsung,srom-page-mode` sets the page-mode bit. `exynos_srom_configure_bank()` updates the packed `BW` chip-select field and writes the timing register. If any bank is malformed, the driver remains bound for suspend/resume but skips `of_platform_populate()`.

State and persistence: configured SROM register values persist in hardware while powered. The driver keeps a sleep-time snapshot of selected registers in memory and restores them on resume. It does not persist data to disk.

Dependencies and integration: uses OF child parsing, platform MMIO mapping, relaxed I/O accessors, and `of_platform_populate()` for external-memory children. Register bit definitions come from `exynos-srom.h`.

Risks: bank index is converted to a shift and register offset by multiplying by four; bad DT bank numbers can address unintended bank-control offsets because only child parsing validates required properties. The dump array uses `kzalloc_objs()` rather than devm and has no explicit free path, acceptable for builtin lifetime but worth noting. A single bad child prevents all child device population.

Test signals: boot with `samsung,exynos4210-srom`, validate each child bank timing in `BW/BCx`, check 8-bit and 16-bit external devices, inject malformed child timing and confirm no children populate, then run suspend/resume and verify registers are restored.
