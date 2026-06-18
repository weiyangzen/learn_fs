<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c

Purpose: generic platform RAM map driver for memory regions described by `struct platdata_mtd_ram`.

Important APIs, types, and functions: `struct platram_info` owns device, MTD, map, and platform data. `platram_setrw()` calls the optional platform read-write/read-only control. Lifecycle functions are `platram_probe()` and `platram_remove()`.

Control flow: probe requires platform data, allocates state, maps resource 0, fills map name/physical address/size/bankwidth, initializes simple map hooks, probes configured map drivers or falls back to `map_ram`, sets the device read-write, parses/registers partitions, and, if platform data supplied partitions, also registers the entire device. Remove unregisters/destroys the MTD, leaves RAM read-only, and frees state.

State and persistence: backing RAM is volatile, though platform wiring may preserve content across soft resets. Runtime state is the platform map, MTD pointer, and RW state controlled by callbacks.

Dependencies and integration points: platform driver name `mtd-ram`, MTD map/partition APIs, `linux/mtd/plat-ram.h`, and optional platform `set_rw`.

Risks: registering parsed partitions and then the whole device when `nr_partitions` is nonzero is unusual and should be validated against MTD core expectations. Error paths call remove-style cleanup. Test signals are platform data validation, `set_rw` toggles, partition parser behavior, fallback `map_ram`, and unload leaving read-only state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c -->
