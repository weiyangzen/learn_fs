# sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.c

Purpose: shared PMC support for AT91 clock providers: DT clock lookup, `pmc_data` allocation, clock-range parsing, and backup-mode suspend/resume clock context integration.

Important APIs and data: `of_at91_get_clk_range()` reads two-u32 min/max properties. `of_clk_hw_pmc_get()` resolves two-cell clock specifiers by type (`CORE`, `SYSTEM`, `PERIPHERAL`, `GCK`, `PROGRAMMABLE`) and index. `pmc_data_allocate()` allocates one flexible array and partitions it into typed `clk_hw **` tables.

Control flow: range parsing returns errors from property reads. Provider lookup validates type/index and returns the matching `clk_hw` or `ERR_PTR(-EINVAL)`. Allocation computes total clocks, uses a flexible array allocation, and assigns contiguous slices. Under `CONFIG_PM`, `pmc_register_ops()` finds compatible PMC and SECURAM nodes, maps SECURAM, and registers syscore suspend/resume hooks.

State and persistence: `pmc_data` persists for each SoC provider. Backup suspend state is determined by a SECURAM word; if set, syscore suspend calls `clk_save_context()` and resume calls `clk_restore_context()`.

Dependencies and integration: every monolithic SoC setup uses `pmc_data_allocate()` and `of_clk_hw_pmc_get()`. PM support depends on DT compatibles, `atmel,sama5d2-securam`, `of_iomap`, and common-clock context callbacks implemented by individual providers.

Risks: `pmc_register_ops()` calls `of_node_put(np)` before `of_iomap(np, 0)`, making the local sequence fragile; lookup logs errors for invalid specifiers but cannot diagnose missing registered entries. Test signals include phandle clock resolution by type/index, allocation table sizing, backup suspend/resume invoking provider callbacks, and no invalid type/index errors in boot logs.
