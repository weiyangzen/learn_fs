<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile

Purpose: maps MTD map-driver Kconfig symbols to Kbuild objects.

Important APIs, types, and functions: `map_funcs.o` is built when `CONFIG_MTD_COMPLEX_MAPPINGS=y`. `physmap.o` is composed from `physmap-core.o` plus optional `physmap-versatile.o`, `physmap-gemini.o`, and `physmap-ixp4xx.o`. Remaining lines build board, chipset, platform, PCI, PCMCIA, and SoC map drivers.

Control flow: selected objects are compiled into the MTD maps directory. The physmap composite links optional OF add-ons into the single `physmap` module/builtin.

State and persistence: no runtime state; this file determines link composition.

Dependencies and integration points: consumes symbols from `maps/Kconfig` and produces map driver objects used by the MTD core and chip probe layer.

Risks: `map_funcs.o` is required for out-of-line simple map functions under complex mappings; missing it would break drivers expecting `simple_map_init()`. Optional physmap add-ons must only be linked when their stubs/prototypes match config. Test signals are expected object lists in build output and no unresolved map helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile -->
