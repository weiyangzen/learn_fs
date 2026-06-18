# sources/distributed-fs/ceph-client/drivers/mtd/maps/tsunami_flash.c

Purpose: Alpha Tsunami TIG-bus flash map driver. It implements byte-wide custom map callbacks over `tsunami_tig_readb()`/`tsunami_tig_writeb()`, enables flash access through a TIG port, probes several ROM/flash types, and registers a whole-device MTD.

Important APIs/types/functions: `tsunami_flash_read8()`, `tsunami_flash_write8()`, `tsunami_flash_copy_from()`, `tsunami_flash_copy_to()`, `tsunami_flash_map`, `init_tsunami_flash()`, `cleanup_tsunami_flash()`. It depends on Alpha Tsunami core I/O helpers, custom `map_info` callbacks, `do_map_probe()` for CFI/JEDEC/ROM, and `mtd_device_register()`.

Control flow: init writes the flash-enable byte, tries `cfi_probe`, `jedec_probe`, then `map_rom`, and registers the first successful MTD. Custom copy loops stop at `MAX_TIG_FLASH_SIZE`. Cleanup unregisters and destroys the probed MTD.

State and persistence: static global `tsunami_flash_mtd` tracks registration. Hardware enable state is modified on init; the defined disable byte is not used on cleanup. Flash contents persist.

Risks and test signals: copy callbacks silently stop at max size rather than reporting short transfer. No locking is used around TIG access, relying on MTD serialization. Tests should cover probe fallback, boundary reads/copies near 12 MiB, write/copy behavior, cleanup after no MTD, and whether platform code expects flash disable on module removal.
