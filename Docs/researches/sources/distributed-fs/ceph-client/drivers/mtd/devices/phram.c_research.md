# sources/distributed-fs/ceph-client/drivers/mtd/devices/phram.c

Purpose: maps physical RAM or reserved-memory/platform regions as MTD RAM devices. It supports module/built-in `phram=` parameters and OF platform devices compatible with `phram`.

Important APIs/types/functions: `struct phram_mtd_list` embeds `mtd_info`, list node, and cached mapping flag. MTD callbacks are `phram_erase()`, `phram_point()`, `phram_read()`, and `phram_write()`. Mapping/lifecycle helpers are `phram_map()`, `phram_unmap()`, `register_device()`, `unregister_devices()`, `phram_setup()`, `phram_param_call()`, `phram_probe()`, and `phram_remove()`.

Control flow: init first enforces `security_locked_down(LOCKDOWN_DEV_MEM)`, registers a platform driver, and for built-in mode parses deferred boot parameters. Parameter parsing accepts `<name>,<start>,<length>[,<erasesize>]`, supports `ki/Mi/Gi`, validates lengths and erase alignment, maps the region, and registers an `MTD_RAM`. OF probe maps the first memory resource and names the MTD from OF label via `mtd_set_of_node()`.

State and persistence: data persists only as long as the mapped physical RAM contents persist. Runtime state is either a global list for parameter-created devices or platform driver data for OF devices. `cached` controls `memremap(MEMREMAP_WB)` versus `ioremap()` and corresponding unmap path.

Dependencies/integration: uses MTD core, platform bus, OF address resources, security lockdown, `memremap`/`ioremap`, and module parameter callback semantics.

Risks: exposing arbitrary physical memory is high impact, hence lockdown gating. The global list is not explicitly protected against concurrent parameter writes. Platform devices pass `NULL` name and depend on OF labels. Incorrect cached/no-map policy can cause cacheability hazards.

Test signals: module parameter parsing with decimal/hex/unit suffixes, too-long names/parameters, erase-size divisibility checks, lockdown rejection, OF `no-map` versus cached mappings, read/write/erase behavior, and cleanup of both parameter and platform devices.
