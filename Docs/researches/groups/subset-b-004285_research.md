# Research: subset-b-004285

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c

Purpose: implements the block-translation runtime for INFTL, exposing M-Systems DiskOnChip NAND as a 512-byte-sector `mtd_blktrans` device. It accepts only NAND MTDs named `DiskOnChip`, mounts INFTL metadata, computes disk geometry, and services sector reads/writes through virtual-unit chains stored in NAND OOB.

Important APIs, types, and functions: `inftl_tr` wires `.readsect`, `.writesect`, `.getgeo`, `.add_mtd`, and `.remove_dev`. `struct INFTLrecord` owns `PUtable`, `VUtable`, geometry, erase size, free counts, and the backing `mtd_info`. Core helpers include `inftl_read_oob()`, `inftl_write_oob()`, `INFTL_findfreeblock()`, `INFTL_findwriteunit()`, `INFTL_foldchain()`, `INFTL_makefreeblock()`, `INFTL_deleteblock()`, `inftl_readblock()`, and `inftl_writeblock()`.

Control flow: `inftl_add_mtd()` filters devices, allocates `INFTLrecord`, calls `INFTL_mount()`, derives CHS geometry, and registers the block translator. Reads walk the VU chain until a sector OOB state is `SECTOR_USED`, return zeroes for absent/deleted sectors, and tolerate corrected bitflips. Writes skip all-zero data by deleting the logical sector; non-zero writes find a free sector in the existing chain or allocate/fold chains before writing data plus `SECTOR_USED` OOB. Folding copies live sectors into the newest target unit, then erases older units oldest-first.

State and persistence: persistent truth is on-flash OOB metadata: unit headers, previous-unit pointers, ANAC/NAC counters, erase marks, and per-sector status bytes. In-memory `PUtable` and `VUtable` are reconstructed by mount and updated after allocation, fold, erase, and delete. Free space tracking is volatile and recomputed at mount.

Dependencies and integration points: depends on NAND MTD, OOB operations, `linux/mtd/inftl.h`, `linux/mtd/nftl.h`, raw NAND bad-block support, and the MTD block translation layer via `module_mtd_blktrans()`.

Risks: no modern wear-leveling is implemented; chain folding is a minimal free-space recovery path. Power loss during fold/delete relies on mount recovery and oldest-first erase ordering. Chain walking has loop guards but corruption still risks data loss or reserved blocks. Write errors are not always checked deeply after `inftl_write()`. Test signals are mount success, correct VU/PU chain dumps under debug, sector read/write/delete behavior, free-block accounting under low space, bad-block handling, and recovery after interrupted folds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c

Purpose: mounts and validates an INFTL volume by finding the media header, reading partition geometry, constructing virtual-to-physical erase-unit chains, formatting unusable units, and initializing free-block state for `inftlcore.c`.

Important APIs, types, and functions: exported functions are `INFTL_mount()`, `INFTL_formatblock()`, `INFTL_dumptables()`, and `INFTL_dumpVUchains()`. Internal helpers include `find_boot_record()`, `check_free_sectors()`, `memcmpb()`, and `format_chain()`. The code consumes `struct INFTLMediaHeader`, `struct INFTLPartition`, `struct inftl_unithead1`, and `struct inftl_unittail` from INFTL/NFTL headers.

Control flow: `INFTL_mount()` calls `find_boot_record()` to scan erase units for a `BNAND` media header plus matching spare header, endian-converts fields, validates partition counts, chooses the BDTL partition, allocates `PUtable`/`VUtable`, reserves boot/media/bad units, and sizes `mbd`. Pass 1 explores OOB unit headers to link chains by logical block and previous-unit pointer. Invalid chains are formatted. Pass 2 detects loops and ANAC discontinuities, fixing table links. Pass 3 formats unreferenced blocks and counts free units.

State and persistence: mount reconstructs volatile tables from persistent OOB headers and erase marks. `INFTL_formatblock()` erases each physical eraseblock in a logical unit, verifies erased data/OOB as `0xff`, writes the erase mark tail, and marks failed physical blocks bad through MTD.

Dependencies and integration points: relies on MTD reads, erases, bad-block APIs, INFTL OOB helpers from `inftlcore.c`, and DiskOnChip media layout definitions. It feeds `inftlcore.c` with mounted geometry, free counts, and chain tables.

Risks: source text includes an apparent duplicated `PUtable = kmalloc_array(...)` line in the allocation block, which is a build-level red flag in this snapshot. Quick-mount hidden blocks are erased rather than supported. Formatting invalid/unreferenced blocks is destructive by design. Test signals are successful media-header detection, rejection of invalid headers, correct bad-unit reservation, loop/corruption warnings, free count consistency, and erase-mark verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig

Purpose: defines the LPDDR and LPDDR2 PCM MTD configuration menu. It gates legacy LPDDR flash command support, QINFO probing, and LPDDR2-NVM PCM support behind `MTD`.

Important APIs, types, and functions: Kconfig symbols are `MTD_LPDDR`, `MTD_QINFO_PROBE`, and `MTD_LPDDR2_NVM`. `MTD_LPDDR` selects `MTD_QINFO_PROBE`; `MTD_QINFO_PROBE` depends on `MTD_LPDDR`; `MTD_LPDDR2_NVM` depends on `MTD && ARM` because the driver uses `writel_relaxed()`.

Control flow: selecting `MTD_LPDDR` builds the QINFO probe and LPDDR command-set object through the Makefile. Selecting `MTD_LPDDR2_NVM` builds the platform driver for LPDDR2-NVM devices.

State and persistence: no runtime state; this file controls which drivers are compiled into the kernel or modules.

Dependencies and integration points: integrates with the parent MTD Kconfig tree and with `drivers/mtd/lpddr/Makefile`. The `select MTD_QINFO_PROBE` relationship ensures LPDDR chip detection is available whenever command support is enabled.

Risks: `MTD_QINFO_PROBE` both depends on and is selected by `MTD_LPDDR`, so it is not useful as an independent probe choice. The ARM-only LPDDR2 guard means non-ARM compile coverage is intentionally absent unless the dependency changes. Test signals are expected object inclusion in `.config`, menu visibility under `MTD`, and successful builds for module and built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile

Purpose: maps the LPDDR Kconfig symbols to their object files.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_QINFO_PROBE) += qinfo_probe.o`, `obj-$(CONFIG_MTD_LPDDR) += lpddr_cmds.o`, and `obj-$(CONFIG_MTD_LPDDR2_NVM) += lpddr2_nvm.o`.

Control flow: Kbuild includes probe support, command-set support, and LPDDR2-NVM platform support independently according to configuration. `lpddr_cmds.o` exports `lpddr_cmdset()` while `qinfo_probe.o` registers the chip probe driver that calls it.

State and persistence: no runtime state; this is build orchestration only.

Dependencies and integration points: consumes the symbols declared in `lpddr/Kconfig` and produces modules/objects linked into the MTD subsystem.

Risks: if `MTD_LPDDR` were enabled without a matching QINFO probe object, LPDDR devices would not bind; Kconfig currently avoids that by selecting `MTD_QINFO_PROBE`. Test signals are presence of expected objects in build logs and no unresolved `lpddr_cmdset` symbol when QINFO probing is modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c

Purpose: platform MTD driver for LPDDR2-NVM PCM memories. It maps the memory array plus controller registers, verifies the PFOW overlay window, and provides MTD read, write, erase, lock, and unlock operations.

Important APIs, types, and functions: `struct pcm_int_data` stores controller MMIO and bus width. Helpers `ow_enable()`, `ow_disable()`, `ow_reg_add()`, `lpddr2_nvm_do_op()`, and `lpddr2_nvm_do_block_op()` implement overlay-window command execution. MTD callbacks are `lpddr2_nvm_read()`, `lpddr2_nvm_write()`, `lpddr2_nvm_erase()`, `lpddr2_nvm_lock()`, and `lpddr2_nvm_unlock()`. `lpddr2_nvm_probe()` builds `map_info` and `mtd_info`.

Control flow: probe allocates private structures, maps memory resource 0 as the array and resource 1 as controller registers, initializes a simple map, populates erase/write sizes, verifies PFOW by reading `P`, `F`, `O`, `W`, and registers the MTD. Reads copy directly from the mapped array. Writes enable OW, choose single-word overwrite for unaligned addresses and buffer overwrite for aligned chunks, poll status until OK, then disable OW. Block operations iterate erase-size chunks for erase/lock/unlock.

State and persistence: persistent state is PCM contents and lock status in device hardware. Runtime state is the global `lpdd2_nvm_mutex`, overlay window enable state, and mapped controller registers.

Dependencies and integration points: uses platform resources, `simple_map_init()`, MTD map APIs, MTD partition registration, and ARM relaxed IO helpers.

Risks: `lpddr2_nvm_do_op()` polls without a timeout, so a stuck device can hang the caller. Bus width is hard-coded to x32 constants. The file contains an extra stray comment opener before PFOW verification, but it does not alter behavior in the viewed text. Test signals are PFOW detection, correct resource ordering, unaligned and buffered writes, erase/lock/unlock over multi-block ranges, and failure behavior when status reports errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr2_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c

Purpose: implements the MTD command set for first-generation LPDDR flash discovered through QINFO/PFOW. It provides NOR-like read, write-buffer, erase, lock/unlock, and direct-point operations with chip-state arbitration.

Important APIs, types, and functions: exported `lpddr_cmdset()` allocates and fills `mtd_info`, initializes `flchip` and `flchip_shared` state, and installs MTD callbacks. Core helpers are `get_chip()`, `chip_ready()`, `put_chip()`, `wait_for_ready()`, `do_write_buffer()`, `do_erase_oneblock()`, `lpddr_writev()`, `lpddr_point()`, and `do_xxlock()`.

Control flow: operations take the target chip mutex, arbitrate shared write/erase ownership, optionally suspend erase for reads/points, issue PFOW commands, and wait for DSR ready/error bits. Writes split vectors on program-buffer boundaries, fill the PFOW program buffer, execute buffer program, and update `retlen`. Erases walk uniform erase blocks. `point()` exposes linear memory when map layout permits and increments chip point references until `unpoint()`.

State and persistence: persistent state is flash contents plus hardware block locks. Runtime state includes `flchip.state`, `oldstate`, wait queues, erase/write suspend flags, point reference counts, and shared write/erase ownership across hardware partitions.

Dependencies and integration points: depends on `linux/mtd/pfow.h`, `linux/mtd/qinfo.h`, map APIs, and QINFO probe code that sets `map->fldrv_priv`. It exports `lpddr_cmdset()` for `qinfo_probe.c`.

Risks: concurrency is intricate: shared engine handoff, suspend/resume, and wait-queue paths must preserve chip state. Timeout values derive from QINFO and default to busy polling when absent. VPP, XIP, and OTP are TODOs. Test signals include buffer writes across boundaries, erase suspend during reads, lock/unlock failures on protected blocks, point/unpoint refcounting, DSR error decoding, and parallel partition contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/lpddr_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c

Purpose: registers an MTD chip probe named `qinfo_probe` for LPDDR devices that expose QINFO records through a PFOW overlay window.

Important APIs, types, and functions: `struct mtd_chip_driver lpddr_chipdrv` calls `lpddr_probe()`. Helpers `lpddr_pfow_present()`, `lpddr_info_query()`, `lpddr_get_qinforec_pos()`, `lpddr_chip_setup()`, and `lpddr_probe_chip()` verify PFOW and populate `struct lpddr_private` and `struct qinfo_chip`.

Control flow: `lpddr_probe()` calls `lpddr_probe_chip()`, which bounds-checks `pfow_base`, reads the `PFOW` signature, allocates QINFO storage, reads manufacturer/device IDs and size/timing/features records, calculates virtual chip count from hardware partitions, and returns private chip state. The map's `fldrv_priv` is then passed to `lpddr_cmdset()` to create the MTD.

State and persistence: runtime state is the allocated `lpddr_private`, its QINFO table, chip count, chip shift, manufacturer ID, and device ID. No persistent state is written.

Dependencies and integration points: depends on map accessors, PFOW command/status registers, QINFO definitions, and the exported `lpddr_cmdset()` from `lpddr_cmds.c`. It registers/unregisters through `register_mtd_chip_driver()`.

Risks: query polling has a fixed 20-attempt microdelay loop and does not return an explicit timeout error. Unknown QINFO strings call `BUG()`. Allocation cleanup is incomplete on some early failure paths after `qinfo` allocation. Test signals are successful PFOW signature reads, correct QINFO-derived MTD size/erase/write sizes, visibility reduction when map size is smaller than chip size, and module unload unregistering the chip driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig

Purpose: defines MTD map-driver configuration for physical, platform, PCI, PCMCIA, legacy board, SoC, and firmware-ROM mappings.

Important APIs, types, and functions: key symbols include `MTD_COMPLEX_MAPPINGS`, `MTD_PHYSMAP`, `MTD_PHYSMAP_OF`, `MTD_PHYSMAP_GPIO_ADDR`, platform add-ons `MTD_PHYSMAP_VERSATILE`, `MTD_PHYSMAP_GEMINI`, `MTD_PHYSMAP_IXP4XX`, and individual board/chipset drivers such as `MTD_AMD76XROM`, `MTD_ICHXROM`, `MTD_ESB2ROM`, `MTD_CK804XROM`, `MTD_PCMCIA`, `MTD_PCI`, `MTD_PLATRAM`, `MTD_PISMO`, and `MTD_LANTIQ`.

Control flow: menu visibility requires `MTD!=n` and `HAS_IOMEM`. Symbols select or depend on chip probe families, buses, architectures, OF, GPIO, syscon, PCI, or PCMCIA as needed. Compat options provide static physmap start/length/bankwidth, while OF/platform paths use runtime resources.

State and persistence: no runtime state; it controls compiled code and module availability.

Dependencies and integration points: ties map drivers to chip drivers (`MTD_CFI`, `MTD_JEDECPROBE`, `MTD_ROM`, `MTD_RAM`, `MTD_LPDDR`) and architecture/platform options.

Risks: many entries target legacy boards and BIOS flashing; incorrect enablement can expose writable firmware. Some compile paths depend on `MTD_COMPLEX_MAPPINGS` for custom map hooks. Test signals are Kconfig dependency resolution, module names matching help text, and build coverage for OF/platform/legacy combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile

Purpose: maps MTD map-driver Kconfig symbols to Kbuild objects.

Important APIs, types, and functions: `map_funcs.o` is built when `CONFIG_MTD_COMPLEX_MAPPINGS=y`. `physmap.o` is composed from `physmap-core.o` plus optional `physmap-versatile.o`, `physmap-gemini.o`, and `physmap-ixp4xx.o`. Remaining lines build board, chipset, platform, PCI, PCMCIA, and SoC map drivers.

Control flow: selected objects are compiled into the MTD maps directory. The physmap composite links optional OF add-ons into the single `physmap` module/builtin.

State and persistence: no runtime state; this file determines link composition.

Dependencies and integration points: consumes symbols from `maps/Kconfig` and produces map driver objects used by the MTD core and chip probe layer.

Risks: `map_funcs.o` is required for out-of-line simple map functions under complex mappings; missing it would break drivers expecting `simple_map_init()`. Optional physmap add-ons must only be linked when their stubs/prototypes match config. Test signals are expected object lists in build output and no unresolved map helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c

Purpose: exposes BIOS flash behind AMD76x/AMD8111 southbridge ROM windows as MTD devices, allowing firmware image access through CFI/JEDEC probes.

Important APIs, types, and functions: `struct amd76xrom_window` tracks the global ROM window, PCI device, resource, ioremap, and discovered maps. `struct amd76xrom_map_info` wraps each found MTD. `amd76xrom_init_one()`, `amd76xrom_cleanup()`, `init_amd76xrom()`, and `cleanup_amd76xrom()` are the main paths. Module parameter `win_size_bits` can widen the BIOS-configured window.

Control flow: init scans a static PCI ID table, adjusts PCI config register `0x43` window-size bits, derives top-of-address-space window start, reserves and ioremaps it, enables writes via register `0x40`, and probes every 64 KiB from at most the last 4 MiB with supported bank widths and `cfi_probe`/`jedec_probe`. Found chips have CFI chip starts offset to the full window and are registered as MTDs.

State and persistence: runtime state is the singleton window and per-chip list. Hardware state includes PCI ROM window size and write-enable bit, which cleanup disables.

Dependencies and integration points: uses PCI config access, `iomem_resource`, `simple_map_init()`, CFI/JEDEC map probes, and MTD registration.

Risks: write-enabling BIOS flash is inherently dangerous. The driver bypasses normal `pci_driver` registration and uses the first matching device. Probing can touch firmware-hub lock registers, so it avoids lower regions. Test signals are correct window sizing, probe discovery, resource reservation behavior when BIOS reserved ranges exist, cleanup disabling writes, and no probing below the guarded address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/amd76xrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c

Purpose: static CFI map driver for the Flaga digital module flash at physical address `0x40000000`.

Important APIs, types, and functions: `flagadm_map` describes a 4 MiB, 16-bit map. `flagadm_parts` defines bootloader, kernel, initial ramdisk, and persistent storage partitions. `init_flagadm()` and `cleanup_flagadm()` handle lifecycle.

Control flow: module init ioremaps the fixed flash window, initializes simple map methods, probes with `cfi_probe`, sets module ownership, and registers the four static partitions. Cleanup unregisters the MTD, destroys the map, and unmaps IO memory.

State and persistence: persistent state is flash contents in fixed partitions. Runtime state is the global `mymtd` and `flagadm_map.virt`.

Dependencies and integration points: depends on PowerPC 8xx/Flaga platform config, MTD CFI, map APIs, and static partition registration.

Risks: fixed addresses and partitions must match board wiring. Failure to register partitions is not checked after `mtd_device_register()`. Test signals are successful ioremap, CFI detection, partition names/sizes, and clean unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c

Purpose: maps BIOS ROM windows on NVIDIA CK804 and MCP55 southbridges as MTD flash devices.

Important APIs, types, and functions: `struct ck804xrom_window`, `struct ck804xrom_map_info`, `ck804xrom_init_one()`, `ck804xrom_cleanup()`, `init_ck804xrom()`, and `cleanup_ck804xrom()` implement discovery. Module parameter `win_size_bits` overrides BIOS window-size bits; device IDs distinguish `DEV_CK804` and `DEV_MCP55`.

Control flow: init scans PCI IDs, takes a device reference, programs CK804 register `0x88` or MCP55 registers `0x88/0x8c/0x90`, computes the ROM window, reserves/ioremaps it, enables writes through register `0x6d`, then scans every 64 KiB with bank widths down from 32 and `cfi_probe`/`jedec_probe`. Found MTDs are registered and tracked on a list.

State and persistence: runtime state is singleton window state plus per-map resources. Hardware state includes ROM decode windows and write-enable bit, disabled during cleanup.

Dependencies and integration points: PCI, IO resource reservation, MTD map probes, CFI private chip-start adjustment, and MTD device registration.

Risks: BIOS flashing danger, chipset-specific register assumptions, and disabled normal `pci_driver` path. Resource reservation failures are logged but may not stop probing. Test signals are matching CK804/MCP55 IDs, correct 4/5/16 MiB window handling, successful MTD registration, and cleanup unmapping and disabling writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ck804xrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/dc21285.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/dc21285.c

Purpose: map driver for flash behind the Intel/DEC DC21285 companion chip used on Footbridge boards such as EBSA285 and NetWinder.

Important APIs, types, and functions: `dc21285_map` supplies custom read/write/copy hooks selected by ROM bus width from `CSR_SA110_CNTL`. `nw_en_write()` gates NetWinder writes through the CPLD. Lifecycle functions are `init_dc21285()` and `cleanup_dc21285()`.

Control flow: init reads hardware bus-width bits, installs 8/16/32-bit map operations, ioremaps the 16 MiB flash aperture, probes `cfi_probe` on EBSA285 or `jedec_probe` otherwise, registers parsed partitions from RedBoot/cmdline, and adjusts EBSA285 flash timing registers. Writes program `CSR_ROMWRITEREG` for subword access and optionally enable NetWinder write gate before each write.

State and persistence: persistent state is flash contents and partition tables. Runtime state is global MTD pointer, selected map operations, and mapped aperture.

Dependencies and integration points: depends on Footbridge hardware headers, machine-type checks, MTD map probes, partition parsers, and custom IO register access.

Risks: hardware-specific write timing and CPLD gating make write failures board-sensitive. Cleanup assumes `dc21285_mtd` exists. Test signals include correct bankwidth detection, CFI/JEDEC probe choice by machine, partition parser output, EBSA timing programming, and verified write/readback on NetWinder and EBSA285.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/dc21285.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c

Purpose: maps firmware hub BIOS flash behind Intel ESB/ESB2-style southbridge decode windows as MTD devices.

Important APIs, types, and functions: `struct esb2rom_window`, `struct esb2rom_map_info`, `esb2rom_init_one()`, `esb2rom_cleanup()`, `init_esb2rom()`, and `cleanup_esb2rom()`. Register constants cover `BIOS_CNTL`, `FWH_DEC_EN1`, and decode masks from 0.5 MiB to 8 MiB.

Control flow: init scans PCI IDs, reads decode enable bits to find the continuous ROM window, expands the mapping 4 MiB lower to include firmware-hub lock/control areas, refuses to enable writes if BIOS lock is active, sets BIOS write enable, reserves/ioremaps the window, limits probing to the top 4 MiB where necessary, scans 64 KiB steps with bank widths and `cfi_probe`/`jedec_probe`, adjusts CFI chip offsets, and registers discovered MTDs.

State and persistence: runtime state is the singleton window and map list. Hardware state includes BIOS write enable; cleanup clears it and releases resources.

Dependencies and integration points: PCI config access, CFI/JEDEC probes, MTD registration, IO resource reservation, and top-of-memory firmware hub layout.

Risks: write enabling firmware is risky and blocked when firmware access control indicates lock. Probe logic assumes top-address firmware hub layout and no paging support. Test signals are decode-mask interpretation, locked BIOS refusal, successful window ioremap, discovered flash sizes, and cleanup disabling writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/esb2rom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c

Purpose: maps BIOS firmware hub flash on Intel ICH2/3/4/5-family southbridges as MTD devices.

Important APIs, types, and functions: `struct ichxrom_window`, `struct ichxrom_map_info`, `ichxrom_init_one()`, `ichxrom_cleanup()`, `init_ichxrom()`, and `cleanup_ichxrom()`. Register constants include `BIOS_CNTL`, `FWH_DEC_EN1`, `FWH_DEC_EN2`, `FWH_SEL1`, and `FWH_SEL2`.

Control flow: init scans a PCI ID table, derives the active ROM window from FWH decode registers, subtracts 4 MiB for lock-register reachability, refuses locked BIOS write enable, sets write enable, reserves/ioremaps the window, scans at 64 KiB increments with supported bank widths and `cfi_probe`/`jedec_probe`, adjusts CFI chip starts to the full window, and registers each found MTD.

State and persistence: runtime state is a singleton window and discovered map list. Hardware state includes BIOS write enable, which cleanup clears.

Dependencies and integration points: PCI config space, MTD CFI/JEDEC map probes, `simple_map_init()`, `iomem_resource`, and MTD registration.

Risks: BIOS access is destructive if misused. The code uses manual PCI scanning rather than enabled `pci_driver` registration. Probe avoidance of lower 4 MiB is required because probe cycles can alter FWH lock registers. Test signals are correct decode window computation, lock-bit refusal, MTD registration at expected top-of-memory addresses, and cleanup releasing resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/ichxrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c

Purpose: board map driver for implementa impA7 NOR flash, exposing two fixed 8 MiB banks.

Important APIs, types, and functions: `impa7_map[]` contains two `map_info` entries, `impa7_mtd[]` stores detected devices, `partitions[]` defines a single `FileSystem` partition, and lifecycle functions are `init_impa7()` and `cleanup_impa7()`.

Control flow: init iterates two fixed physical windows, ioremaps each, initializes simple map hooks, probes with `jedec_probe`, registers the single partition on each found chip, and unmaps banks that do not probe. Cleanup unregisters/destroys/unmaps each detected MTD.

State and persistence: persistent state is NOR contents in fixed banks. Runtime state is the two map structures and MTD pointers.

Dependencies and integration points: depends on ARM, JEDEC probe support, MTD partition registration, and static board memory map.

Risks: first-bank ioremap failure returns without cleaning previously mapped banks in unusual partial-failure cases. Partition size is fixed to 8 MiB and assumes bank size. Test signals are both bank probes, correct `impa7-%d` mtdparts naming expectation from comments, partition registration, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/l440gx.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/l440gx.c

Purpose: maps the BIOS flash chip on Intel L440GX motherboards as an MTD device and enables board-specific write paths.

Important APIs, types, and functions: `l440gx_map` describes a 1 MiB, 8-bit map at `0xfff00000`. `l440gx_set_vpp()` reference-counts VPP through PM IO ports. `init_l440gx()` and `cleanup_l440gx()` control lifecycle.

Control flow: init locates PIIX4 ISA/PM PCI devices, maps the BIOS window, initializes map methods, configures PM IO base if missing, enables XBCS, turns on VPP, enables the WE gate through a tri-buffer port, probes `jedec_probe` then falls back to `map_rom`, and registers the MTD.

State and persistence: persistent state is BIOS flash contents. Runtime state includes PM IO base, VPP reference count, map mapping, and MTD pointer.

Dependencies and integration points: PCI, port IO, MTD JEDEC/ROM probes, and Intel PIIX4 register assumptions.

Risks: there are suspicious PCI reference/lifetime sequences around `pci_dev_put(dev)` before `dev` is later used. VPP hook is disabled in `map_info` behind `#if 0`, while init still enables VPP globally. Test signals are successful PIIX discovery, WE/VPP enablement, JEDEC or ROM probe, and unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/l440gx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c

Purpose: OF platform map driver for Lantiq SoC NOR flash attached to the External Bus Unit, working around address endianness behavior shared with PCI.

Important APIs, types, and functions: `struct ltq_mtd` stores resource, MTD, and map pointers. Custom map hooks are `ltq_read16()`, `ltq_write16()`, `ltq_copy_from()`, and `ltq_copy_to()`. Probe/remove are `ltq_mtd_probe()` and `ltq_mtd_remove()`.

Control flow: intended probe flow allocates driver state and `map_info`, maps the memory resource, installs 16-bit map hooks, probes with address XOR active in `LTQ_NOR_PROBING`, switches to normal mode, swizzles CFI unlock addresses, and registers the MTD with OF node association. Remove unregisters and destroys the map.

State and persistence: persistent state is NOR contents. Runtime state includes the map mode flag `map_priv_1`, EBU spinlock protection, CFI unlock addresses, and MTD registration.

Dependencies and integration points: depends on Lantiq `ebu_lock`, OF compatible `lantiq,nor`, CFI probing, MTD registration, and platform resources.

Risks: in this snapshot `ltq_mtd_probe()` assigns `ltq_mtd->map->virt` before allocating `ltq_mtd->map`, a clear null-pointer dereference/order bug if compiled as shown. The address-swizzle workaround is fragile and tied to 16-bit CFI. Test signals are probe ordering under KASAN, successful PF/OF resource mapping, correct unlock address swizzle, and read/write behavior while PCI EBU swapping is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c

Purpose: provides out-of-line simple map IO operations when complex mappings are enabled.

Important APIs, types, and functions: `simple_map_init()` validates bank width and installs `simple_map_read()`, `simple_map_write()`, `simple_map_copy_from()`, and `simple_map_copy_to()`. The helpers wrap `inline_map_*` operations and are marked `__xipram`.

Control flow: drivers call `simple_map_init(&map)` after filling `virt`, `size`, `bankwidth`, and names. After that, chip probes use the installed hooks for reads, writes, and copies.

State and persistence: no persistent state. It mutates function pointers in caller-provided `struct map_info`.

Dependencies and integration points: depends on `linux/mtd/map.h`, `linux/mtd/xip.h`, and `map_bankwidth_supported()`. It exports `simple_map_init()` for map drivers.

Risks: unsupported bank width triggers `BUG_ON`, so callers must validate configuration first. Test signals are successful use by simple physmap/board drivers under `CONFIG_MTD_COMPLEX_MAPPINGS` and correct IO behavior matching inline map operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c

Purpose: static map driver for the AMD NetSc520 demonstration board flash region and its predefined partitions.

Important APIs, types, and functions: `netsc520_map` defines the flash window, `partition_info[]` defines boot kernel, low BIOS, filesystem, and high BIOS partitions, and lifecycle functions are `init_netsc520()` and `cleanup_netsc520()`.

Control flow: init ioremaps the fixed window, initializes simple map methods, probes in order with `cfi_probe`, `map_ram`, then `map_rom`, sets module ownership, and registers static partitions. Cleanup unregisters/destroys the MTD and unmaps the window.

State and persistence: flash contents persist in static partitions. Runtime state is global map and MTD pointer.

Dependencies and integration points: depends on MELAN/Sc520 platform config, MTD CFI/map RAM/ROM probes, and MTD partition registration.

Risks: comments describe a 16 MiB flash bank but `WINDOW_SIZE` is 1 MiB in the viewed source, so partition sizes extending beyond the map require validation against actual platform mapping. BIOS partitions are dangerous to mount/write. Test signals are probe fallback behavior, partition boundaries, and filesystem partition accessibility without touching BIOS partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c

Purpose: map driver for SnapGear/SecureEdge/NETtel x86 boards using AMD and optional Intel flash behind AMD SC520 PAR windows.

Important APIs, types, and functions: `nettel_amd_map`, optional `nettel_intel_map`, partition arrays for AMD and Intel layouts, `nettel_init()`, `nettel_cleanup()`, and optional `nettel_reboot_notifier()` for Intel CFI reset-to-read mode.

Control flow: init maps SC520 MMCR, programs CPU clock, manipulates PAR registers to probe AMD boot flash first, then, when `CONFIG_MTD_CFI_INTELEXT` is enabled, determines Intel boot/kernel flash layout, remaps PARs to detected sizes, reprobes combined Intel chips, adjusts partitions based on AMD-vs-Intel boot, registers Intel then AMD MTDs, and registers reboot notifier. Cleanup unregisters notifier and MTDs, destroys maps, and unmaps MMCR/flash windows.

State and persistence: persistent state is board flash contents and static partition data. Runtime state includes MMCR mapping, PAR register programming, AMD/Intel MTD pointers, and reboot notifier state.

Dependencies and integration points: uses SC520 MMCR/PAR hardware, JEDEC probe for AMD, CFI Intel extended command support, MTD partition registration, reboot notifier, and root device environment indirectly through board layout.

Risks: direct PAR and cache flush manipulation is platform-sensitive. Partition sizing is adjusted at runtime and must preserve BIOS regions. Error paths are complex and can leave partially changed PARs. Test signals are AMD-only and Intel+AMD layouts, reboot reset-to-read behavior, partition count adjustments, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c

Purpose: generic PCI MTD map driver for flash on add-in devices, specifically Intel IQ80310 ATU and Intel/DEC DC21285 blank-ROM programming mode.

Important APIs, types, and functions: `struct mtd_pci_info` supplies per-device init/exit/translate/map probe data. `struct map_pci_info` embeds `map_info`, PCI base mapping, and callbacks. Generic map hooks are `mtd_pci_read8/read32`, `mtd_pci_write8/write32`, and copy helpers. PCI lifecycle is `mtd_pci_probe()` and `mtd_pci_remove()`.

Control flow: PCI probe enables the device, requests regions, allocates map state, calls the matched device init, probes the requested map type (`cfi_probe` or `jedec_probe`), registers the MTD, and stores it as PCI driver data. IQ80310 init remaps BAR0, temporarily changes window base config, and translates offsets with page programming. DC21285 init maps ROM resource or BAR2 fallback and handles ROM enable/disable.

State and persistence: runtime state is PCI device enablement, mapped BAR/ROM aperture, saved IQ80310 window config, and MTD registration. Persistent state is flash contents.

Dependencies and integration points: PCI core, MTD map probes, CFI/JEDEC, and device-specific PCI resources/config registers.

Risks: probe error path calls `map->exit` even if per-device init failed before setting resources, so callback robustness matters. DC21285 BAR/ROM comments indicate incomplete resource migration. Test signals are PCI bind/unbind, saved config restoration, map translate correctness, and MTD registration on both supported IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c

Purpose: PCMCIA memory-card MTD driver for linear flash, SRAM, or ROM cards, including cards larger than a single host memory window.

Important APIs, types, and functions: `struct pcmciamtd_dev` tracks the PCMCIA device, mapped window, current offset, map, MTD, VPP, and name. Module parameters control bank width, speed, forced size, VPP, and memory type. Key functions include `remap_window()`, remapping/direct read/write/copy hooks, `pcmciamtd_set_vpp()`, CIS tuple parsers, `card_settings()`, `pcmciamtd_config()`, `pcmciamtd_probe()`, and `pcmciamtd_detach()`.

Control flow: probe allocates device state and runs config. Config parses CIS/product data, sets map size/width/name, requests the largest possible common-memory window by shrinking on failure, ioremaps it, enables the PCMCIA device, probes RAM/ROM or JEDEC/CFI flash, switches to faster direct hooks if the whole MTD fits in the window, registers the MTD, and logs `mtdN`. Detach unregisters/destroys the MTD, releases the PCMCIA window/device, and frees state.

State and persistence: persistent state is card memory contents. Runtime state includes current remapped card offset, VPP refcount, module parameter choices, MTD pointer, and PCMCIA resource window.

Dependencies and integration points: PCMCIA core/CIS parsing, MTD map probes, map IO hooks, and optional anonymous card matching.

Risks: window remapping must be correct across reads/writes spanning window boundaries. VPP values can be dangerous. Card removal returns zero data or drops writes through DEV_REMOVED checks. Test signals are CIS parsing, forced RAM/ROM modes, large-card remap reads/writes, direct-mode switch, suspend/resume callbacks, and hot removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c

Purpose: generic physical-memory map driver for NOR, ROM, RAM, and LPDDR-like devices described by platform data, Device Tree, or legacy Kconfig compatibility.

Important APIs, types, and functions: `struct physmap_flash_info` stores maps, per-map MTDs, concatenated MTD, VPP state, probe/partition types, GPIO address extension state, and static partitions. Major functions are `physmap_flash_probe()`, `physmap_flash_remove()`, `physmap_flash_of_init()`, `physmap_flash_pdata_init()`, `physmap_set_vpp()`, GPIO-assisted map hooks, and `physmap_flash_shutdown()`.

Control flow: probe validates OF/platform data, counts memory resources, allocates maps and MTD pointers, obtains optional address GPIOs, enables runtime PM, initializes OF or platform properties, maps each resource, installs GPIO/SoC/simple map hooks, probes a specific or fallback map type (`cfi_probe`, `jedec_probe`, `qinfo_probe`, `map_rom`), concatenates multiple maps when present, associates OF node, parses/registers partitions, and returns. Remove unregisters the combined MTD, destroys maps, calls platform exit, and disables PM.

State and persistence: runtime state is per-device map/MTD arrays, VPP refcount, optional GPIO address bank value, and concatenated MTD. Persistent state is backing flash/RAM content.

Dependencies and integration points: platform driver `physmap-flash`, OF match table, partition parsers, MTD concat, CFI endian settings, GPIO descriptors, runtime PM, and optional Gemini/IXP4xx/Versatile add-ons.

Risks: multiple feature combinations make ordering important, especially custom map hooks before `simple_map_init()`. GPIO-assisted addressing supports only one map. `pm_runtime_get_sync()` errors are not explicitly checked. Test signals are OF and platform-data probe paths, multi-map concatenation, GPIO address switching, VPP callbacks, partition parser selection, and shutdown suspend/resume reset-to-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c

Purpose: Gemini-specific physmap add-on that validates parallel flash hardware status and toggles pinctrl states around every map access.

Important APIs, types, and functions: `struct gemini_flash` stores device and pinctrl state. `of_flash_probe_gemini()` is called from physmap OF initialization. Custom hooks are `gemini_flash_map_read()`, `gemini_flash_map_write()`, `gemini_flash_map_copy_from()`, and `gemini_flash_map_copy_to()`.

Control flow: the probe helper returns immediately unless the flash node is compatible with `cortina,gemini-flash`. It allocates singleton state, reads a syscon global status register, rejects non-parallel flash, warns if DT bank width differs from hardware, obtains enabled/disabled pinctrl states, selects disabled as idle, and installs wrappers that enable pins for each inline map operation and disable them afterwards.

State and persistence: runtime state is a static singleton pointer and pinctrl states. Persistent flash contents are untouched except through normal map operations.

Dependencies and integration points: physmap OF path, syscon regmap, pinctrl, Gemini hardware global status bits, and MTD XIP-safe inline map helpers.

Risks: singleton `gf` assumes only one active Gemini flash context. Per-access pin toggling may be expensive and must be safe for nested/concurrent map operations. Test signals are syscon status validation, bank-width warnings, pinctrl state transitions during read/write/probe, and normal physmap registration afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h

Purpose: declares or stubs the Gemini physmap OF add-on entry point.

Important APIs, types, and functions: `of_flash_probe_gemini(struct platform_device *, struct device_node *, struct map_info *)` is declared when `CONFIG_MTD_PHYSMAP_GEMINI` is enabled; otherwise an inline stub returns 0.

Control flow: `physmap-core.c` can call the helper unconditionally during OF map setup. The stub preserves build/link behavior when the feature is disabled.

State and persistence: none.

Dependencies and integration points: depends on `linux/of.h`, `linux/mtd/map.h`, and a forward-visible `platform_device` type through included kernel headers.

Risks: the helper is expected to be side-effect-free when incompatible or disabled. Test signals are successful builds with the config enabled and disabled, and no behavior change for non-Gemini physmap nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c

Purpose: IXP4xx-specific physmap add-on that corrects expansion-bus endianness/address coherency for 16-bit flash.

Important APIs, types, and functions: `flash_read16()` and `flash_write16()` abstract big- vs little-endian behavior. Custom map hooks are `ixp4xx_read16()`, `ixp4xx_copy_from()`, and `ixp4xx_write16()`. `of_flash_probe_ixp4xx()` installs them for `intel,ixp4xx-flash`.

Control flow: for non-IXP4xx nodes the helper returns 0. For matching nodes, it sets custom 16-bit read/write/copy-from operations and leaves `copy_to` NULL because command writes use 16-bit access. Little-endian systems XOR address bit 1 and byte-swap words to undo CPU/expansion-bus swizzling; `ixp4xx_copy_from()` reconstructs byte streams from 16-bit reads including unaligned starts.

State and persistence: no private persistent state; only map function pointers are changed.

Dependencies and integration points: physmap OF path, MTD map APIs, CPU endian config, and `CONFIG_MTD_CFI_BE_BYTE_SWAP` when little-endian CFI data needs unswapping.

Risks: bank width is assumed to match 16-bit access. Missing or wrong byte-swap config can corrupt command/data interpretation. Test signals are byte-accurate reads at odd/even offsets, CFI probe success on little- and big-endian IXP4xx, and write command placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h

Purpose: declares or stubs the IXP4xx physmap OF add-on entry point.

Important APIs, types, and functions: `of_flash_probe_ixp4xx(struct platform_device *, struct device_node *, struct map_info *)` is declared when `CONFIG_MTD_PHYSMAP_IXP4XX` is enabled and otherwise replaced with an inline zero-return stub.

Control flow: allows `physmap-core.c` to call the helper unconditionally while Kconfig controls whether custom IXP4xx hooks are linked.

State and persistence: none.

Dependencies and integration points: includes OF, platform device, and MTD map declarations and is included by `physmap-core.c`.

Risks: disabled stub must not mask required endian handling on actual IXP4xx boards; Kconfig defaults/selects are responsible. Test signals are build coverage for enabled/disabled configs and correct helper behavior on nonmatching OF nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c

Purpose: Versatile/Integrator/RealView physmap add-on that supplies flash protection and VPP callbacks using syscon and, for Integrator/AP, EBI registers.

Important APIs, types, and functions: `of_flash_probe_versatile()` is the physmap hook. Helpers `ap_flash_init()`, `ap_flash_set_vpp()`, `cp_flash_set_vpp()`, and `versatile_flash_set_vpp()` program platform-specific protection bits. `syscon_match[]` identifies the system controller flavor.

Control flow: the helper acts only for `arm,versatile-flash`. On first use it finds a matching syscon regmap and records the flash-protection type. Integrator/AP additionally maps the EBI, clears protection, unlocks EBI, enables write cycles, and relocks it. The helper installs the correct `map->set_vpp` callback for AP, CP, Versatile, or RealView systems.

State and persistence: runtime state is a static syscon regmap pointer and selected protection type. Hardware state includes VPP/write-protect bits and Integrator EBI write-enable state.

Dependencies and integration points: physmap OF initialization, syscon/regmap, OF address mapping, ARM platform compatibles, and `map_info.set_vpp`.

Risks: static syscon state assumes one protection domain. AP initialization directly touches EBI registers and must match hardware manuals. VPP errors are logged but not propagated during callbacks. Test signals are syscon discovery, AP EBI write enable, VPP toggling on AP/CP/Versatile/RealView, and normal physmap probing afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h

Purpose: declares or stubs the Versatile physmap OF add-on hook.

Important APIs, types, and functions: `of_flash_probe_versatile(struct platform_device *, struct device_node *, struct map_info *)` is declared under `CONFIG_MTD_PHYSMAP_VERSATILE`; otherwise an inline stub returns 0.

Control flow: `physmap-core.c` calls this hook unconditionally during OF setup, while the header hides config-specific linkage.

State and persistence: none.

Dependencies and integration points: includes OF and MTD map declarations and is paired with `physmap-versatile.c`.

Risks: if the config is disabled on a board requiring VPP/protection handling, flash may probe read-only or fail writes. Test signals are enabled/disabled build coverage and no-op behavior on non-Versatile nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c

Purpose: I2C EEPROM discovery driver for PISMO memory modules. It does not map flash directly; it creates `physmap-flash` or `mtd-ram` platform devices based on EEPROM chip-select descriptors.

Important APIs, types, and functions: packed EEPROM formats are `struct pismo_cs_block` and `struct pismo_eeprom`. Runtime structs are `struct pismo_mem` and `struct pismo_data`. Key functions include `pismo_eeprom_read()`, `pismo_add_device()`, `pismo_add_nor()`, `pismo_add_sram()`, `pismo_add_one()`, `pismo_probe()`, and `pismo_remove()`.

Control flow: probe verifies I2C functionality, allocates driver state, reads the 256-byte EEPROM, logs board name, iterates up to five chip selects, converts width encoding, uses platform-provided base addresses, and adds child platform devices for static NOR or SRAM. Child devices carry resources and platform data for physmap or plat-ram. Remove unregisters all child devices and frees state.

State and persistence: persistent state is module EEPROM content and memory devices. Runtime state is child platform-device pointers and optional VPP callback data from platform data.

Dependencies and integration points: I2C core, PISMO platform data, physmap-flash, mtd-ram/plat-ram, and optional VPP forwarding.

Risks: `pismo_probe()` dereferences `pdata->cs_addrs[i]` without a visible null check after optional VPP extraction, so platform data appears required despite being treated partly optional. EEPROM checksum field is not validated. Test signals are EEPROM read size, child device creation for type 2/3 entries, width rejection, VPP forwarding, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c

Purpose: generic platform RAM map driver for memory regions described by `struct platdata_mtd_ram`.

Important APIs, types, and functions: `struct platram_info` owns device, MTD, map, and platform data. `platram_setrw()` calls the optional platform read-write/read-only control. Lifecycle functions are `platram_probe()` and `platram_remove()`.

Control flow: probe requires platform data, allocates state, maps resource 0, fills map name/physical address/size/bankwidth, initializes simple map hooks, probes configured map drivers or falls back to `map_ram`, sets the device read-write, parses/registers partitions, and, if platform data supplied partitions, also registers the entire device. Remove unregisters/destroys the MTD, leaves RAM read-only, and frees state.

State and persistence: backing RAM is volatile, though platform wiring may preserve content across soft resets. Runtime state is the platform map, MTD pointer, and RW state controlled by callbacks.

Dependencies and integration points: platform driver name `mtd-ram`, MTD map/partition APIs, `linux/mtd/plat-ram.h`, and optional platform `set_rw`.

Risks: registering parsed partitions and then the whole device when `nr_partitions` is nonzero is unusual and should be validated against MTD core expectations. Error paths call remove-style cleanup. Test signals are platform data validation, `set_rw` toggles, partition parser behavior, fallback `map_ram`, and unload leaving read-only state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/plat-ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c

Purpose: platform map driver for NOR flash attached to Intel XScale PXA2xx systems.

Important APIs, types, and functions: `struct pxa2xx_flash_info` stores `mtd_info` and `map_info`. `pxa2xx_map_inval_cache()` invalidates cached flash mappings line by line. Lifecycle functions are `pxa2xx_flash_probe()`, `pxa2xx_flash_remove()`, and optional `pxa2xx_flash_shutdown()`.

Control flow: probe reads `flash_platform_data`, obtains memory resource 0, allocates state, fills map name/width/physical/size, ioremaps uncached and optionally cached aliases, installs cache invalidation and simple map methods, probes the platform-specified chip driver, sets parent device, parses/registers RedBoot/cmdline/static partitions, and stores driver data. Remove unregisters, destroys, unmaps both aliases, and frees state. Shutdown suspend/resume returns flash to read mode.

State and persistence: persistent state is NOR contents and partitions. Runtime state is map aliases and MTD pointer.

Dependencies and integration points: PXA flash platform data, MTD map probes, partition parsers, ARM cache maintenance instruction, and platform driver binding `pxa2xx-flash`.

Risks: probe assumes non-null platform data before dereferencing `flash->name` and `flash->width`. Cached mapping is optional but cache invalidation hook still references `map->cached`; callers must avoid invalidation when absent. Test signals are chip probe selection, cached/uncached alias behavior, partition parser output, cache invalidation after writes, and shutdown read-mode recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c -->
