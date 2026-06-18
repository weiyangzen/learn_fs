# sources/distributed-fs/ceph-client/drivers/mtd/maps/solutionengine.c

Purpose: Hitachi Solution Engine map driver for a 4 MiB flash device and a 4 MiB EPROM that may appear at either of two physical locations. It probes flash first, swaps flash/EPROM mapping if needed, registers EPROM as ROM, and parses flash partitions.

Important APIs/types/functions: `soleng_eprom_map`, `soleng_flash_map`, `init_soleng_maps()`, `cleanup_soleng_maps()`, `flash_mtd`, `eprom_mtd`, partition probe list `{ "RedBoot", "cmdlinepart" }`. It depends on SH direct segment address macros `P1SEGADDR()`/`P2SEGADDR()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, `do_map_probe("map_rom")`, and `mtd_device_parse_register()`.

Control flow: init assigns default flash at physical 0/P2 and EPROM at 0x01000000/P1, initializes maps, and probes CFI. If absent, it swaps the address assignments and probes again. Once flash is found, it probes EPROM as map ROM and registers it if present, then parses and registers flash partitions. Cleanup unregisters EPROM if present, then unregisters flash and destroys maps.

State and persistence: no dynamic allocation or resource reservation; static map structures are mutated to reflect detected placement. Flash and EPROM contents persist independently.

Risks and test signals: no `ioremap()` or resource request means this assumes architecture-specific direct mappings and exclusive board ownership. Cleanup assumes `flash_mtd` exists because module init fails otherwise. Tests should cover both flash placements, absent EPROM, partition parser order, failure when neither flash location probes, and unregister ordering.
