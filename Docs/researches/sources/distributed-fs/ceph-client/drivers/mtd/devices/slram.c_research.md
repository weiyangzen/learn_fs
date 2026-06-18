# sources/distributed-fs/ceph-client/drivers/mtd/devices/slram.c

Purpose: maps contiguous system RAM excluded from normal kernel use into one or more uncached/cached MTD RAM devices. It is configured by `slram=` boot parameter or module `map=` array.

Important APIs/types/functions: `slram_priv_t` stores mapped start/end pointers; `slram_mtd_list_t` links allocated MTDs. MTD callbacks are `slram_erase()`, `slram_point()`, `slram_read()`, and `slram_write()`. Setup helpers are `register_device()`, `unregister_devices()`, `handle_unit()`, `parse_cmdline()`, `mtd_slram_setup()`, and `init_slram()`.

Control flow: init parses triples of name/start/end-or-+length. `parse_cmdline()` handles decimal/hex plus K/M suffixes, converts an absolute end into length unless a `+length` form is used, validates `SLRAM_BLK_SZ` alignment, maps memory with `memremap()`, allocates MTD/private/list nodes, and registers the device. Cleanup unregisters all devices and unmaps memory.

State and persistence: contents are physical RAM and generally volatile. Runtime state is the global singly linked list of MTD devices plus each mapped range. Erase means setting bytes to `0xff`.

Dependencies/integration: module params or early boot `__setup`, `memremap(MEMREMAP_WB|WT|WC)`, MTD core, and command-line memory reservation by the user.

Risks: this older driver has partial allocation unwind gaps in `register_device()` if later allocation or `memremap()` fails. It exposes arbitrary physical ranges and assumes users avoided kernel/device memory conflicts. No locking protects the global list, but devices are normally created only at init.

Test signals: valid module and built-in command-line parsing, `+length` and absolute-end forms, unit suffixes, block-size alignment rejection, read/write/erase round trips, multi-device cleanup, and failure injection around allocation/mapping/register paths.
