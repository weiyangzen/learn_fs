# subset-b-004286 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sa1100-flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/sa1100-flash.c

Purpose: SA11x0 platform CFI flash map driver. It discovers one or more platform memory resources, builds one `map_info` per chip select, probes the selected map driver from `flash_platform_data->map_name`, optionally concatenates multiple banks with `mtd_concat_create()`, and registers parsed or platform partitions through `mtd_device_parse_register()`.

Important APIs/types/functions: `struct sa_subdev_info`, `struct sa_info`, `sa1100_set_vpp()`, `sa1100_probe_subdev()`, `sa1100_setup_mtd()`, `sa1100_mtd_probe()`, `sa1100_destroy()`. It depends on platform resources, `flash_platform_data`, SA1100 MSC bankwidth bits, `simple_map_init()`, `do_map_probe()`, and MTD partition parsers `"cmdlinepart"` and `"RedBoot"`.

Control flow: probe fetches platform data, allocates flexible subdevice state, calls optional platform `init()`, probes each memory resource, accepts partial success when later banks return `-ENXIO`, concatenates multiple successful banks, then registers partitions. Remove unregisters the exposed MTD, destroys concatenation if present, unmaps each bank, releases regions, frees state, and calls optional platform `exit()`.

State and persistence: persistent flash state is entirely on hardware; driver state tracks mapped windows, probed MTDs, and a global VPP refcount protected by `sa1100_vpp_lock`. VPP nesting is process-wide, so all subdevices share one programming-voltage lifetime.

Risks and test signals: VPP refcount underflow would call platform `set_vpp(0)` incorrectly; only callers following map-layer pairing keep it safe. Bankwidth inference only handles CS0/CS1 and defaults unknown bases to CS0. Tests should exercise single-bank, multi-bank concat, missing second bank, platform init failure, partition parser fallback, remove cleanup, and nested write operations that toggle VPP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sa1100-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sbc_gxx.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/sbc_gxx.c

Purpose: legacy x86 MTD map driver for Arcom SBC-MediaGX/GXm/GX1 boards. It exposes up to 16 MiB of x8 Intel StrataFlash through a 16 KiB memory window and two I/O paging registers, then registers three static partitions for boot, data, and application areas.

Important APIs/types/functions: `sbc_gxx_map`, `sbc_gxx_page()`, `sbc_gxx_read8()`, `sbc_gxx_write8()`, `sbc_gxx_copy_from()`, `sbc_gxx_copy_to()`, `init_sbc_gxx()`, `cleanup_sbc_gxx()`. It depends on low-level port I/O (`outw()`), `ioremap()`, `request_region()`, custom map callbacks, `do_map_probe("cfi_probe")`, and `mtd_device_register()`.

Control flow: init maps the fixed memory aperture, reserves paging ports, logs address ranges, probes CFI over custom map operations, and registers static partitions. Each map access takes `sbc_gxx_spin`, pages the target flash address into the 16 KiB window if needed, then performs byte or bulk I/O. Cleanup unregisters and destroys the MTD, unmaps the aperture, and releases I/O ports.

State and persistence: persistent state is board flash. Runtime state is global: `page_in_window`, `iomapadr`, `all_mtd`, and spinlock. The page cache avoids repeated port writes but has no hardware validation.

Risks and test signals: access serialization is critical because reads/writes change a global hardware page register. Bulk copy paths must handle window-boundary splitting exactly. Probe failure cleanup should release both mappings and I/O ports. Tests should cover reads/writes across 16 KiB boundaries, partition sizes, failed `ioremap()`, failed `request_region()`, and absent CFI flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sbc_gxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sc520cdp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/sc520cdp.c

Purpose: AMD Elan SC520 Customer Development Platform map driver. It exposes two 8 MiB 32-bit flash banks and an optional 512 KiB DIL flash, optionally reprogramming SC520 PAR registers to avoid BIOS aliasing, then concatenates the two main banks into one MTD device.

Important APIs/types/functions: `sc520cdp_map[]`, `mymtd[]`, `merged_mtd`, `sc520cdp_setup_par()`, `init_sc520cdp()`, `cleanup_sc520cdp()`, `struct sc520_par_table`, `SC520_PAR_ENTRY()`. It depends on MMCR `ioremap()`, `readl()/writel()` PAR access, `simple_map_init()`, map probes (`cfi_probe`, `jedec_probe`, `map_rom`), and `mtd_concat_create()`.

Control flow: optional PAR setup maps MMCR, finds ROMCS0/ROMCS1/BOOTCS PAR entries by target-device bits, rewrites them, or falls back to BIOS addresses. Init maps each flash window, initializes map callbacks, probes in CFI/Jedec/ROM order, records successful MTDs, concatenates banks 0 and 1 when at least two devices are found, and separately registers the third DIL flash when present. Cleanup unregisters concat/DIL devices, destroys maps, and unmaps windows.

State and persistence: runtime state is static arrays of map descriptors and MTD pointers. Reprogrammed PAR settings persist at least until platform reset and alter physical decode behavior.

Risks and test signals: `devices_found >= 2` assumes banks 0 and 1 exist, even though the count is not tied to indices. PAR programming failures silently fall back per bank. Tests should simulate missing banks, failed maps, probe fallback order, cleanup after partial discovery, and variable PAR table matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sc520cdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/scb2_flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/scb2_flash.c

Purpose: PCI-attached BIOS flash map for Intel SCB2 boards using a ServerWorks CSB5 bridge. It enables southbridge decoding of a 1 MiB ROM window, probes CFI flash, and rewrites MTD geometry to model unusual x16 wiring exposed as byte-linear x8 access.

Important APIs/types/functions: `scb2_flash_probe()`, `scb2_flash_remove()`, `scb2_fixup_mtd()`, `scb2_map`, `scb2_mtd`, `scb2_flash_pci_ids`. It depends on PCI config register `CSB5_FCR`, `request_mem_region()`, `ioremap()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, CFI private data, `mtd_device_register()`, and lock/unlock helpers.

Control flow: PCI probe enables decode, attempts to reserve the ROM region but continues if BIOS/e820 already reserved it, maps the window, probes CFI, validates x16 async interface, shrinks logical size to the map, halves erase sizes, trims erase regions to the visible high-address window, then registers the MTD. Remove locks the whole flash, unregisters, destroys, unmaps, and releases the region when it was reserved.

State and persistence: flash contents persist; driver state is one global map, MTD pointer, mapping pointer, and `region_fail` flag. The southbridge decode bit remains changed while loaded.

Risks and test signals: geometry surgery is fragile and assumes a specific wiring and CFI layout. The probe path calls `mtd_device_unregister()` before registration if fixup fails. Tests should cover CFI interface rejection, oversized chips, erase-region trimming, reserved-region continuation, and remove-time lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/scb2_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/scx200_docflash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/scx200_docflash.c

Purpose: NatSemi SCx200 DOCCS flash map driver. It either probes an existing BIOS mapping or allocates/programs a DOCCS memory aperture, sets 8/16-bit width, probes the requested flash type, and registers four boot/BIOS/filesystem partitions.

Important APIs/types/functions: module parameters `probe`, `size`, `width`, `flashtype`; `docmem`; `scx200_docflash_map`; `init_scx200_docflash()`; `cleanup_scx200_docflash()`. It depends on PCI bridge discovery, `scx200_cb_present()`, SCx200 DOCCS config registers, PMR width bit, `allocate_resource()` or `request_resource()`, `ioremap()`, `do_map_probe()`, and static MTD partitions.

Control flow: init locates the SCx200 bridge and config block. In probe mode it validates an existing base/control mapping, checks power-of-two size, infers width, and reserves the resource. In setup mode it validates parameters, allocates a high memory region, writes DOCCS base/control, and updates PMR width. It maps the aperture, probes `flashtype`, derives high-BIOS and filesystem partition bounds from detected size, and registers partitions. Cleanup unregisters/destroys and releases mappings/resources.

State and persistence: module parameters drive hardware configuration. DOCCS base/control and PMR writes alter chipset state. Partition boundaries depend on detected MTD size at runtime.

Risks and test signals: `docmem.end = base + size` is inclusive-style suspicious compared with common `end = start + size - 1`. Invalid non-power-of-two sizes are rejected. Tests should cover probe/setup modes, width validation, resource conflicts, mapping smaller than flash warning, partition size calculation, and cleanup after probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/scx200_docflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/solutionengine.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/solutionengine.c

Purpose: Hitachi Solution Engine map driver for a 4 MiB flash device and a 4 MiB EPROM that may appear at either of two physical locations. It probes flash first, swaps flash/EPROM mapping if needed, registers EPROM as ROM, and parses flash partitions.

Important APIs/types/functions: `soleng_eprom_map`, `soleng_flash_map`, `init_soleng_maps()`, `cleanup_soleng_maps()`, `flash_mtd`, `eprom_mtd`, partition probe list `{ "RedBoot", "cmdlinepart" }`. It depends on SH direct segment address macros `P1SEGADDR()`/`P2SEGADDR()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, `do_map_probe("map_rom")`, and `mtd_device_parse_register()`.

Control flow: init assigns default flash at physical 0/P2 and EPROM at 0x01000000/P1, initializes maps, and probes CFI. If absent, it swaps the address assignments and probes again. Once flash is found, it probes EPROM as map ROM and registers it if present, then parses and registers flash partitions. Cleanup unregisters EPROM if present, then unregisters flash and destroys maps.

State and persistence: no dynamic allocation or resource reservation; static map structures are mutated to reflect detected placement. Flash and EPROM contents persist independently.

Risks and test signals: no `ioremap()` or resource request means this assumes architecture-specific direct mappings and exclusive board ownership. Cleanup assumes `flash_mtd` exists because module init fails otherwise. Tests should cover both flash placements, absent EPROM, partition parser order, failure when neither flash location probes, and unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/solutionengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sun_uflash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/sun_uflash.c

Purpose: OpenFirmware/platform driver for user-programmable Sun EBus flashprom devices. It intentionally binds only flash nodes with a `user` property and avoids OBP flash, maps the resource, probes CFI, and registers a whole-device MTD.

Important APIs/types/functions: `struct uflash_dev`, `uflash_map_templ`, `uflash_probe()`, `uflash_devinit()`, `uflash_remove()`, OF match name `"flashprom"`. It depends on OF properties (`user`, `model`), platform resources, `of_ioremap()`/`of_iounmap()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, and `mtd_device_register()`.

Control flow: platform probe checks the OF node for `user`, then rejects devices with `resource[1].flags` as unsupported non-CFI flash. It allocates per-device state, copies the map template, sizes it from resource 0, uses the model as map name when present, maps the resource, probes CFI, registers the MTD, and stores driver data. Remove unregisters/destroys the MTD, unmaps the resource, and frees state.

State and persistence: state is per platform device, not global. Flash content persists; no partitions are parsed here. Model-derived names affect sysfs and MTD naming.

Risks and test signals: the `resource[1]` access assumes platform resources are populated as expected. Unsupported non-CFI hardware is hard rejected. Tests should cover absent `user`, non-CFI marker, missing model fallback, failed map/probe cleanup, registration success, and remove idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/sun_uflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ts5500_flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/ts5500_flash.c

Purpose: fixed physical map driver for the Technology Systems TS-5500 board flash. It maps a 2 MiB 8-bit window at `0x09400000`, probes JEDEC flash with ROM fallback, and registers three static partitions named Drive A, BIOS, and Drive B.

Important APIs/types/functions: `ts5500_map`, `ts5500_partitions`, `init_ts5500_map()`, `cleanup_ts5500_map()`, `mymtd`. It depends on `ioremap()`, `simple_map_init()`, `do_map_probe("jedec_probe")`, `do_map_probe("map_rom")`, `mtd_device_register()`, and static board partition definitions.

Control flow: init maps the fixed window, initializes the map, probes JEDEC then ROM, sets module owner, and registers the partitions. If mapping or probing fails, it unwinds the map and returns `-EIO` or `-ENXIO`. Cleanup unregisters and destroys the MTD if present, then unmaps the window.

State and persistence: all runtime state is static and single-device. Flash contents persist; partition boundaries are hard-coded and reflect BIOS/RFD layout assumptions.

Risks and test signals: no memory-region reservation is performed, so conflicts are not detected. ROM fallback can expose read-only flash while still using static partitioning. Tests should cover absent flash, ROM fallback, partition offsets/sizes, failed mapping cleanup, and successful unregister/unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ts5500_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/tsunami_flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/tsunami_flash.c

Purpose: Alpha Tsunami TIG-bus flash map driver. It implements byte-wide custom map callbacks over `tsunami_tig_readb()`/`tsunami_tig_writeb()`, enables flash access through a TIG port, probes several ROM/flash types, and registers a whole-device MTD.

Important APIs/types/functions: `tsunami_flash_read8()`, `tsunami_flash_write8()`, `tsunami_flash_copy_from()`, `tsunami_flash_copy_to()`, `tsunami_flash_map`, `init_tsunami_flash()`, `cleanup_tsunami_flash()`. It depends on Alpha Tsunami core I/O helpers, custom `map_info` callbacks, `do_map_probe()` for CFI/JEDEC/ROM, and `mtd_device_register()`.

Control flow: init writes the flash-enable byte, tries `cfi_probe`, `jedec_probe`, then `map_rom`, and registers the first successful MTD. Custom copy loops stop at `MAX_TIG_FLASH_SIZE`. Cleanup unregisters and destroys the probed MTD.

State and persistence: static global `tsunami_flash_mtd` tracks registration. Hardware enable state is modified on init; the defined disable byte is not used on cleanup. Flash contents persist.

Risks and test signals: copy callbacks silently stop at max size rather than reporting short transfer. No locking is used around TIG access, relying on MTD serialization. Tests should cover probe fallback, boundary reads/copies near 12 MiB, write/copy behavior, cleanup after no MTD, and whether platform code expects flash disable on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/tsunami_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/uclinux.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/uclinux.c

Purpose: generic uClinux direct-mapped ROM/RAM filesystem MTD driver. It exposes a ROMfs image directly following kernel BSS, or at a module-supplied physical address, as a single `"ROMfs"` MTD partition using either `map_rom` or `map_ram` depending on configuration.

Important APIs/types/functions: `uclinux_ram_map`, `physaddr` module parameter, `uclinux_point()`, `uclinux_mtd_init()`, `uclinux_romfs`. It depends on linker symbol `__bss_stop`, `phys_to_virt()`, ROMfs size at offset 8 in network byte order, `PAGE_ALIGN()`, `simple_map_init()`, `do_map_probe("map_rom"/"map_ram")`, and `mtd_device_register()`.

Control flow: device init selects physical base, derives size from the ROMfs header when not preset, sets 32-bit bankwidth, translates to virtual memory, initializes the map, probes the matching map driver, overrides `_point` for direct access, saves the MTD pointer, and registers one partition.

State and persistence: the mapped image is persistent only if backed by ROM/flash; RAM mode is volatile. `_point` exposes direct virtual and optional physical addresses for XIP/NOMMU-style users.

Risks and test signals: it trusts the image header at `phys + 8` and casts physical addresses directly while deriving size before `phys_to_virt()`. There is no cleanup path because it uses `device_initcall`. Tests should validate boot-time image discovery, explicit `physaddr`, invalid/missing mapping, size alignment, `_point` address translation, and ROM vs RAM config behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/uclinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/vmu-flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/maps/vmu-flash.c

Purpose: Sega Dreamcast Visual Memory Unit memory-card MTD driver. Unlike simple map drivers, it implements MTD `_read` and `_write` over the Maple bus, discovers VMU partitions via `GETMINFO`, and registers one MTD device per VMU partition.

Important APIs/types/functions: `struct memcard`, `struct vmupart`, `struct vmu_cache`, `struct mdev_part`, `ofs_to_block()`, `maple_vmu_read_block()`, `maple_vmu_write_block()`, `vmu_flash_read()`, `vmu_flash_write()`, `vmu_queryblocks()`, `vmu_connect()`, `vmu_disconnect()`, and Maple driver registration. It depends on Maple packet commands, `mtd_device_register()`, wait queues, `atomic_t busy`, and kmsg device hotplug behavior.

Control flow: Maple probe installs unload/error handlers and calls `vmu_connect()`, which decodes function data, allocates card/partition/MTD arrays, stores drvdata, and sends an async meminfo request. `vmu_queryblocks()` receives partition geometry, allocates names/cache/private data, fills `mtd_info` callbacks and geometry, registers the MTD, then recursively queries further partitions. Reads convert offsets to blocks, use a one-second valid block cache, and fetch missing blocks through phased Maple reads. Writes read-modify-write full VMU blocks and invalidate cache. Disconnect unregisters all partition MTDs and frees arrays.

State and persistence: persistent state is VMU flash blocks. Runtime state includes per-partition cache buffers, Maple busy state, pending read buffer pointer, partition metadata, and registered MTD objects.

Risks and test signals: hot-unplug is explicitly awkward; read/write paths must translate `busy == 2` to errors. Several failure paths allocate nested objects and require precise cleanup. Tests should cover phased read/write counts, cache hit/expiry, boundary truncation, interrupted waits, unplug during I/O, multi-partition recursion, and open-ref refusal in `vmu_can_unload()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/vmu-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtd_blkdevs.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtd_blkdevs.c

Purpose: common block-layer bridge for MTD translation drivers such as `mtdblock`. It lets a translation driver register `struct mtd_blktrans_ops`, creates blk-mq disks for each matching MTD, routes block requests to sector callbacks, and tracks devices through MTD add/remove notifiers.

Important APIs/types/functions: `register_mtd_blktrans()`, `deregister_mtd_blktrans()`, `add_mtd_blktrans_dev()`, `del_mtd_blktrans_dev()`, `do_blktrans_request()`, `mtd_queue_rq()`, `blktrans_open()`, `blktrans_release()`, `mtd_blktrans_work()`, and notifier callbacks. It depends on `mtd_table_mutex`, `__get_mtd_device()`, blk-mq tag sets, `gendisk`, request queues, and translation callbacks (`readsect`, `writesect`, `discard`, `flush`, `background`).

Control flow: registering a translation major installs the MTD notifier, registers a block major, adds the ops to `blktrans_majors`, and scans existing MTDs. Each added device gets a devnum, tag set, disk, queue limits, disk name, capacity, and sysfs attributes. Requests are queued under `queue_lock` and synchronously drained by `mtd_blktrans_work()`, which serializes actual I/O under `dev->lock` and can run one background pass per idle period. Removal deletes the disk, freezes/quiesces the queue, releases any open MTD, nulls `dev->mtd`, and drops references.

State and persistence: runtime state is lists of translation majors/devices, request lists, open counts, krefs, queue locks, and writable flags. Persistent data lives behind underlying MTDs.

Risks and test signals: request code maps only the first bio page for read/write loops, so assumptions about request segment layout matter. Removal races are controlled through queue freezing and `queuedata = NULL`. Tests should cover open/remove races, dynamic MTD add/remove, readonly devices, flush/discard errors, background stop behavior, devnum allocation, and module refcounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtd_blkdevs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtd_virt_concat.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtd_virt_concat.c

Purpose: device-tree-driven virtual concatenation layer. It discovers partitions linked by the `part-concat-next` phandle property, withholds component partitions from normal registration, creates a concatenated MTD once all components are available, and restores individual partitions when a concat is destroyed.

Important APIs/types/functions: `struct mtd_virt_concat_node`, `mtd_virt_concat_node_create()`, `mtd_virt_concat_add()`, `mtd_virt_concat_create_join()`, `mtd_virt_concat_destroy()`, `mtd_virt_concat_destroy_joins()`, `mtd_virt_concat_destroy_items()`. It depends on OF node iteration/phandle refs, global `concat_node_list`, `mtd_concat_create()`, `add_mtd_device()`, `del_mtd_device()`, and partition locking from `mtdcore`.

Control flow: node discovery finds available nodes with `part-concat-next`, skips nodes already part of another concat, counts linked phandles plus the defining node, allocates an item and concat container, and stores node references. As partitions are allocated, `mtd_virt_concat_add()` captures matching MTD pointers instead of registering them individually. Join creation waits until all subdevices are present, builds a hyphenated name with `"concat"` suffix, creates an `mtd_concat`, copies parent device identity from the first subdevice, and registers the concat. Destroy unregisters concat, releases subdevice refs, re-adds remaining child MTDs when needed, and drops OF refs.

State and persistence: global list entries hold OF node refs, subdevice pointers, counts, and concat metadata. Persistent data is unchanged; only the visible MTD topology changes.

Risks and test signals: name allocation and duplicate detection are delicate. `mtd_virt_concat_destroy_joins()` dereferences `item->concat` before its null check. Tests should cover phandle chains, duplicate membership, missing component devices, re-creation with same name, destroy-on-component removal, OF ref balancing, and restoration of individual partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtd_virt_concat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdblock.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdblock.c

Purpose: writable block-device emulation for MTD devices. It registers an `mtd_blktrans_ops` named `mtdblock` and implements sector reads/writes with an eraseblock-sized read-modify-write cache so partial 512-byte writes can be applied to erase-oriented flash.

Important APIs/types/functions: `struct mtdblk_dev`, `erase_write()`, `write_cached_data()`, `do_cached_write()`, `do_cached_read()`, `mtdblock_open()`, `mtdblock_release()`, `mtdblock_flush()`, `mtdblock_add_mtd()`, `mtdblock_tr`. It depends on the blktrans framework, `mtd_read()`, `mtd_write()`, `mtd_erase()`, `mtd_sync()`, `vmalloc()` for cache data, and MTD geometry/flags.

Control flow: the blktrans notifier creates one device per MTD index. Opening initializes cache state, warns for NAND, and sets cache size to erasesize unless `MTD_NO_ERASE`. Reads use cached dirty/clean data if the requested sector belongs to the cached eraseblock, otherwise read from MTD. Writes either erase/write a full sector-sized eraseblock directly or load an eraseblock into cache, patch bytes, and mark dirty. Flush/release write dirty cache and sync writable devices; last close frees cache.

State and persistence: runtime state tracks open count, cache mutex, cache buffer, cached eraseblock offset/size, and dirty state. Persistent flash is only updated on full-block writes or cache writeback, not immediately for every partial write.

Risks and test signals: power loss before cache flush can lose partial writes. Cache allocation happens lazily in write path and returns `-EINTR` on allocation failure. Tests should cover partial writes across eraseblock boundaries, full eraseblock writes bypassing cache, bitflip-tolerant reads, readonly MTDs, NAND warning, flush-on-release, and EIO cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdblock_ro.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdblock_ro.c

Purpose: simple block-device emulation variant that marks disks read-only while still providing a `writesect` callback for RAM-backed or otherwise writable use through the common translation layer. It avoids the eraseblock writeback cache used by `mtdblock.c`.

Important APIs/types/functions: `mtdblock_readsect()`, `mtdblock_writesect()`, `mtdblock_add_mtd()`, `mtdblock_remove_dev()`, and `mtdblock_tr`. It depends on `mtd_read()`, `mtd_write()`, `mtd_is_bitflip()`, blktrans registration, and MTD index/size fields.

Control flow: the add callback allocates a generic `mtd_blktrans_dev`, sets devnum from `mtd->index`, size from `mtd->size >> 9`, marks it readonly, warns for NAND, and calls `add_mtd_blktrans_dev()`. Sector reads and writes perform one 512-byte MTD read/write at `block * 512`. Removal delegates to `del_mtd_blktrans_dev()`.

State and persistence: no cache or private state beyond the allocated blktrans device. Persistent behavior is immediate and entirely delegated to the underlying MTD.

Risks and test signals: write callback ignores short `retlen`; read callback treats ECC bitflips as success but also ignores short reads. Because the disk is readonly, normal block writes should be blocked by block-layer policy. Tests should cover readonly flag, RAM-write path if enabled, NAND warning, add/remove, short I/O handling, and bitflip read status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdblock_ro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdchar.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdchar.c

Purpose: MTD character-device frontend for `/dev/mtdX` and `/dev/mtdXro`. It implements open/read/write/lseek/ioctl/mmap hooks, exposes erase/OOB/OTP/raw/bad-block/partition operations to userspace, and serializes ioctl mutation through the master MTD chrdev lock.

Important APIs/types/functions: `struct mtd_file_info`, `mtdchar_open()`, `mtdchar_read()`, `mtdchar_write()`, `mtdchar_ioctl()`, `mtdchar_read_ioctl()`, `mtdchar_write_ioctl()`, `mtdchar_readoob()`, `mtdchar_writeoob()`, `mtdchar_blkpg_ioctl()`, `init_mtdchar()`, `cleanup_mtdchar()`. It depends on `get_mtd_device()`, `put_mtd_device()`, all public MTD operation wrappers, user-copy helpers, compat ioctl conversion, and `mtdcore.h`.

Control flow: open maps minor to MTD index, rejects write opens on ro minors or non-writable devices, gets an MTD ref, and stores mode state. Read/write clamp to device size, allocate a degraded-size bounce buffer via `mtd_kmalloc_up_to()`, then loop through normal, raw, or OTP operations. Ioctl first classifies commands into safe/dangerous and requires write mode for destructive commands, then handles info, erase, OOB, MEMREAD/MEMWRITE, lock/unlock, bad block, OTP, ECC layout/stats, raw/OTP file modes, and BLKPG partition add/delete. Close syncs write opens and drops refs.

State and persistence: per-open state holds the selected MTD and file mode. Persistent effects include writes, erases, bad-block marks, locks, OTP changes, and dynamic partitions.

Risks and test signals: ioctl surface is broad and must maintain ABI compatibility. OOB length adjustment and ECC error reporting are subtle. Tests should cover permission checks, ro minors, raw mode, OTP mode switching, ECC read returns, OOB-only operations, dynamic partition ioctls, compat OOB ioctls, size clamping, and mmap behavior on NOMMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdchar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdconcat.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdconcat.c

Purpose: generic MTD concatenation layer. It constructs a virtual `mtd_info` spanning multiple compatible subdevices and routes read/write/OOB/erase/lock/sync/suspend/bad-block operations to the correct child by translating offsets.

Important APIs/types/functions: `struct mtd_concat`, `mtd_concat_create()`, `mtd_concat_destroy()`, `concat_read()`, `concat_write()`, `concat_writev()`, `concat_read_oob()`, `concat_write_oob()`, `concat_erase()`, `concat_lock()/unlock()/is_locked()`, `concat_block_isbad()`, `concat_block_markbad()`. It depends on child MTD operation wrappers and compatibility checks for type, flags, write/OOB geometry, callbacks, and erase regions.

Control flow: create allocates a flexible concat object, copies base geometry from subdevice 0, enables callbacks when the corresponding master supports them, verifies all children are compatible, accumulates total size/bad-block stats, sets OOB layout, and builds uniform or variable erase-region metadata. Operation callbacks iterate children, skip offsets before the target child, limit each sub-operation to child size, update retlen/oobretlen, and continue across boundaries. Erase validates alignment against the virtual erase-region map before issuing per-child erases.

State and persistence: concat owns only virtual metadata and subdevice pointers; data persists in child MTDs. Bad-block and ECC stats are aggregated into the virtual device.

Risks and test signals: cross-device boundary handling is the core risk, especially OOB buffer pointer updates and vector write splitting. Compatibility rejects mixed OOB/ECC geometry but still allows writeability flag differences. Tests should cover reads/writes/OOB spanning boundaries, variable erase regions, lock ranges, bad-block propagation, panic writes, incompatible children, and destroy freeing erase-region metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdconcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.c

Purpose: central MTD registry, device-class implementation, notifier hub, NVMEM/debugfs/sysfs integration, and public operation wrapper layer. It registers MTD devices and partitions, exposes `/proc/mtd`, initializes `mtdchar`, and translates partition-relative operations to master devices.

Important APIs/types/functions: `add_mtd_device()`, `del_mtd_device()`, `mtd_device_parse_register()`, `mtd_device_unregister()`, `register_mtd_user()`, `get_mtd_device()`, `__get_mtd_device()`, `put_mtd_device()`, `mtd_read/write/read_oob/write_oob/erase/panic_write`, OOB layout helpers, OTP helpers, lock/bad-block helpers, `mtd_kmalloc_up_to()`, `init_mtd()`, `cleanup_mtd()`. It depends on global `mtd_idr`, `mtd_table_mutex`, Linux device model, char major registration, partition parser APIs, optional virtual concat, NVMEM, debugfs, reboot notifiers, and LED triggers.

Control flow: module init registers the MTD class, backing device info, `/proc/mtd`, char device, and debugfs. Device registration validates callbacks and geometry, allocates an ID, initializes defaults, optionally unlocks power-up-locked chips, registers sysfs devices and ro char node, adds NVMEM/debugfs, notifies users, and optionally sets root device from DT. Parse-register adds OTP NVMEM, optionally registers partitioned master, parses partitions or fallback parts, joins virtual concats, and installs reboot notifier. Operation wrappers validate ranges and flags, translate offsets through partition hierarchy, update ECC stats, support SLC-on-MLC emulation, and normalize return codes.

State and persistence: persistent data is in devices; core state is IDR entries, krefs, parent/partition hierarchy, notifier list, sysfs/debugfs/proc/NVMEM providers, ECC stats, bitflip threshold, and reboot notifier state.

Risks and test signals: registration and unregister paths are highly stateful and must balance idr/device/kref/module/NVMEM/OF references. Operation wrappers must preserve ABI return semantics for ECC and OOB. Tests should cover duplicate registration, invalid callback combinations, partitioned master on/off, notifier add/remove ordering, refcounted open/remove, OOB validation, SLC emulation translation, OTP NVMEM failures, and cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.h

Purpose: private MTD core header shared by core-adjacent implementation files. It exposes internal registry, partition, parser, and char-device entry points that are intentionally not part of the public driver API.

Important APIs/types/functions: declarations for `mtd_table_mutex`, `mtd_bdi`, `__mtd_next_device()`, `add_mtd_device()`, `del_mtd_device()`, `add_mtd_partitions()`, `del_mtd_partitions()`, `release_mtd_partition()`, `parse_mtd_partitions()`, `mtd_part_parser_cleanup()`, `init_mtdchar()`, `cleanup_mtdchar()`, and `mtd_for_each_device`.

Control flow: the header has no executable flow, but it defines the internal iteration pattern used by notifiers and blktrans: start from `__mtd_next_device(0)` and request the next index after the current `mtd->index`.

State and persistence: it centralizes access to the global registry mutex and backing device info. It does not own persistent state.

Dependencies and integration: included by `mtdcore.c`, `mtdchar.c`, `mtd_blkdevs.c`, `mtdpart.c`, and virtual concat code when they need internal functions outside public `<linux/mtd/*.h>`.

Risks and test signals: because these symbols are internal, accidental external use would couple drivers to core internals. Tests are indirect: successful builds with partition, char, blktrans, and virtual concat configurations; lockdep coverage that callers hold `mtd_table_mutex` where required; and iterator behavior under dynamic add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdoops.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdoops.c

Purpose: kmsg dumper that stores oops/panic logs in a selected MTD partition as fixed-size circular records. It scans existing records, erases blocks as needed, writes oops records from workqueue context, and writes panic records immediately with `mtd_panic_write()`.

Important APIs/types/functions: module parameters `record_size`, `mtddev`, `dump_oops`; `struct mtdoops_hdr`; `struct mtdoops_context`; `mtdoops_notify_add/remove()`, `find_next_position()`, `mtdoops_do_dump()`, `mtdoops_write()`, `mtdoops_erase()`, `mtdoops_inc_counter()`. It depends on MTD notifiers, `mtd_read/write/panic_write/erase`, bad-block helpers, workqueues, `kmsg_dump_register()`, and vmalloc bitmaps/buffers.

Control flow: init validates parameters, allocates the record buffer, initializes work, and registers an MTD notifier. When the configured MTD appears, it validates size/erasesize/limit, allocates a used-page bitmap, registers a kmsg dumper, scans pages for the highest sequence number, marks free pages, and chooses the next slot. Dump callback copies kernel log into the record buffer; panics write synchronously, oopses schedule work. After each write it marks the page used, advances the counter, and erases the next block immediately or asynchronously if needed.

State and persistence: persistent records contain sequence, magic, timestamp, and log text. Runtime state tracks selected MTD, current page/count, used bitmap, work items, busy bit, and buffer.

Risks and test signals: panic path cannot sleep and depends on driver `panic_write`. Record size must be eraseblock-compatible in practice, though validation only checks 4 KiB multiple and erasesize >= record_size. Tests should cover sequence wrap, empty flash detection, bad blocks, erase failures and markbad fallback, concurrent dumps via busy bit, notifier removal while work is pending, and panic-write unsupported errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdoops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdpart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdpart.c

Purpose: MTD partitioning layer. It allocates partition `mtd_info` children, applies offset/size directives, enforces alignment-derived writeability, registers/unregisters partition devices recursively, and runs partition parsers from explicit lists, command line, or device tree.

Important APIs/types/functions: `allocate_partition()`, `mtd_add_partition()`, `mtd_del_partition()`, `add_mtd_partitions()`, `del_mtd_partitions()`, `parse_mtd_partitions()`, parser registry functions, `mtd_part_of_parse()`, `mtd_part_do_parse()`, and `mtd_get_device_size()`. It depends on `mtdcore.h`, parent/master MTD geometry, OF partition nodes, parser modules, `mtd_virt_concat_add()`, sysfs partition offset attribute, and bad/reserved block helpers.

Control flow: allocation copies parent properties, applies `MTDPART_OFS_APPEND`, `NXTBLK`, `RETAIN`, and `SIZ_FULL`, clamps out-of-range partitions, computes child erasesize from parent erase regions, forces misaligned writable partitions read-only, copies ECC settings, and counts bad/reserved blocks. Static or dynamic partition add links the child under the parent lock, registers it, adds sysfs offset, and parses subpartitions. Deletion recursively removes child partitions and devices. Parser flow tries requested parsers, with special OF handling that matches compatible parsers, populates child platform devices, and falls back to fixed partitions.

State and persistence: partition state is an MTD hierarchy with child offsets/sizes, flags, sysfs attributes, and parser-owned partition arrays. Persistent data is shared with parent storage; partitioning only changes the exposed address ranges.

Risks and test signals: alignment math controls write protection and must use master offsets correctly for nested partitions. Error unwinding can recursively delete already-added partitions. Tests should cover append/next-block/retain/full directives, truncation/out-of-range disabled partitions, variable erase regions, nested partitions, parser module loading, OF fixed-partition fallback, virtual concat withholding, and BLKPG add/delete paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdpart.c -->
