# Research: subset-b-004283

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0020.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0020.c

Purpose: implements the MTD NOR command-set driver for CFI primary/alternate command set `0x0020`, the ST Advanced Architecture command set. It turns CFI geometry and ST extended-query data into an `mtd_info` device and provides read, buffered write, writev, erase, lock, unlock, sync, suspend, resume, and destroy callbacks.

Important APIs, types, and functions: `cfi_cmdset_0020()` is the exported command-set entry called by generic CFI probing. `cfi_staa_setup()` builds erase-region metadata and installs the MTD callbacks. `do_read_onechip()`, `do_write_buffer()`, `do_erase_oneblock()`, `do_lock_oneblock()`, and `do_unlock_oneblock()` are the per-chip state-machine operations. `cfi_staa_write_buffers()` enforces write-buffer boundaries, while `cfi_staa_writev()` coalesces vectored writes around the ECC-sized write unit.

Control flow: probe reads the ST PRI table with `cfi_read_pri()`, validates version 1.0 through 1.3, byteswaps feature masks, initializes each `flchip`, and calls setup. Runtime operations split requests by chip and erase-region boundaries, acquire each chip mutex, wait or sleep on the chip wait queue until the state is usable, issue ST/Intel-style command sequences through `map_write()`, poll status bit `0x80`, and wake waiters after state changes. Reads can suspend an in-progress erase when supported, copy data, then resume erase.

State and persistence: state is per-chip `flchip.state`, `oldstate`, wait queues, mutexes, adaptive write/erase timing fields, and hardware status/VPP state. MTD geometry persists in `mtd_info` erase regions and write-buffer size. Suspend marks idle chips `FL_PM_SUSPENDED`; resume sends reset/read-array and restores `FL_READY`.

Dependencies and integration points: depends on CFI/map helpers, `struct cfi_private`, `map_info` accessors, `ENABLE_VPP`/`DISABLE_VPP`, CFI geometry macros, and generic MTD callbacks. It is loaded indirectly by `gen_probe.c` when CFI reports `P_ID_ST_ADV`.

Risks: write-buffer alignment is strict and returns `-EINVAL` for unaligned starts. Long erase/lock/unlock paths use coarse sleeps and polling. `cfi_staa_unlock()` only calls one block helper despite taking a length, so range-unlock expectations need scrutiny. `writev()` has fragile partial-buffer accounting around `thislen`. Status handling merges interleaved-chip errors only in erase.

Test signals: successful CFI detection of ST advanced parts, correct erase-region layout, reads during erase suspend/resume, aligned and boundary-crossing buffered writes, `-EROFS` on locked blocks, suspend returning `-EAGAIN` during active operations, and no stuck `FL_*` states or waiters after timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_probe.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_probe.c

Purpose: implements the CFI-specific chip probe used by the generic NOR probe framework. It enters CFI query mode, confirms the `QRY` signature, reads the CFI identification table, discovers manufacturer/device IDs, applies early fixups, and registers the `cfi_probe` chip driver.

Important APIs, types, and functions: `cfi_probe()` delegates to `mtd_do_chip_probe()`. `cfi_probe_chip()` validates a candidate base address, enters query mode, handles alias detection, and records additional chips. `cfi_chip_setup()` allocates and fills `struct cfi_ident`, byteswaps CFI fields, reads autoselect manufacturer/id values, and applies `cfi_early_fixup_table`. `fixup_s70gl02gs_chips()` corrects bad Spansion/S70GL02GS geometry before generic chip enumeration relies on it.

Control flow: generic probing calls `cfi_probe_chip()` for geometry permutations and map offsets. The first successful base triggers `cfi_chip_setup()`, which reads erase-region count and the variable-length CFI table while in query mode, then exits query mode before autoselect. Later bases are compared with earlier chip locations to reject aliases before marking new chip bits.

State and persistence: the file populates `cfi_private` fields: `cfiq`, `cfi_mode`, `sector_erase_cmd`, `mfr`, `id`, number of chips, interleave, and device type. No persistent storage exists beyond the CFI structures passed to command-set drivers.

Dependencies and integration points: uses `linux/mtd/xip.h` guards for execute-in-place builds, `cfi_qry_mode_on/off()`, `cfi_qry_present()`, `cfi_send_gen_cmd()`, `gen_probe.h`, and chip-driver registration in `chipreg.c`.

Risks: probing manipulates live flash modes and disables interrupts briefly under XIP. Alias detection can be fooled when actual flash contents equal CFI markers or IDs. Bad CFI tables require early fixups because `chipshift` and chip count are derived immediately after the first setup.

Test signals: detection logs with expected bank width/interleave, correct CFI table byteswapping on big/little-endian maps, no duplicate alias chips, S70GL02GS split geometry, XIP boot stability, and successful handoff to primary or alternate command-set drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_util.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_util.c

Purpose: provides geometry-aware helpers shared by CFI command-set and probe drivers. It builds command words and command addresses for arbitrary bank width/interleave/device type combinations, enters and exits CFI query mode, reads primary/alternate extended query tables, applies fixup tables, and iterates variable erase regions for lock/erase-style operations.

Important APIs, types, and functions: exported helpers include `cfi_udelay()`, `cfi_build_cmd_addr()`, `cfi_build_cmd()`, `cfi_merge_status()`, `cfi_send_gen_cmd()`, `cfi_qry_present()`, `cfi_qry_mode_on()`, `cfi_qry_mode_off()`, `cfi_read_pri()`, `cfi_fixup()`, and `cfi_varsize_frob()`.

Control flow: command helpers compute bus-scaled offsets and replicate command/status patterns across interleaved chips. Query-mode entry tries multiple known vendor command sequences, including Intel, ST M29DW, old SST, and SST39VF640xB variants, then verifies `QRY`. `cfi_read_pri()` switches into query mode, copies a requested extended table, and switches back to read mode. `cfi_varsize_frob()` validates erase-region alignment, then calls a caller-supplied block callback across chips and regions.

State and persistence: this file owns no long-lived state. It mutates flash mode transiently and uses `cfi_private` geometry and IDs to build commands and apply special reset behavior for ST M29W128G-like parts.

Dependencies and integration points: consumed by CFI probes, Intel/AMD/ST command sets, and FWH lock fixups. It depends on `map_info` accessors, CFI endian conversion macros, XIP helpers, and MTD erase-region metadata.

Risks: small geometry mistakes broadcast wrong commands to every interleaved chip. Query entry intentionally sends several vendor-specific sequences, so false positives or side effects on odd parts are possible. `cfi_varsize_frob()` assumes the request is non-empty and begins inside a valid region.

Test signals: command address/word correctness for x8/x16/x32 and interleave 1/2/4/8, successful query-mode entry for Intel/ST/SST variants, clean query-mode exit, fixup execution by mfr/id, and range operations over mixed erase-region maps without off-by-one region advances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/chipreg.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/chipreg.c

Purpose: supplies the small registry that map drivers use to discover and invoke MTD chip drivers by name. It hides module lookup/loading and provides the shared `do_map_probe()` and `map_destroy()` lifecycle helpers.

Important APIs, types, and functions: `register_mtd_chip_driver()` and `unregister_mtd_chip_driver()` maintain the global list. `do_map_probe()` finds or requests a named module and calls its `.probe`. `map_destroy()` calls the selected chip driver `.destroy`, drops the module reference held by the mapped device, and frees `mtd_info`.

Control flow: chip drivers register at module init under `chip_drvs_lock`. A board/map driver calls `do_map_probe("cfi_probe", map)` or similar; the registry tries the current list, then `request_module(name)`, then probes. On success, the probe usually sets `map->fldrv` and takes its own module reference; `do_map_probe()` releases the temporary probe-driver reference.

State and persistence: global state is only `chip_drvs_list` protected by a spinlock. Per-device lifetime is represented by `map->fldrv` and module refcounts, not by this file.

Dependencies and integration points: used by CFI/JEDEC/map_ram/map_rom/map_absent drivers and platform map drivers. It depends on kernel module loading and the `struct mtd_chip_driver` contract from `linux/mtd/map.h`.

Risks: callers must unregister the MTD device before `map_destroy()`. A driver that fails to set `map->fldrv` or take a module reference can break lifetime assumptions. Registry lookup is name-based, so module aliases and registration names must remain consistent.

Test signals: probing built-in and modular chip drivers, module autoload by probe name, unregister/reload races, correct module refcount behavior after probe-only modules hand off to command-set modules, and clean `map_destroy()` without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/chipreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/fwh_lock.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/fwh_lock.h

Purpose: header-only helper for Intel Firmware Hub style block lock registers. It installs lock/unlock callbacks that write FWH lock-control registers located 4 MiB below the flash address window rather than issuing normal flash array lock commands.

Important APIs, types, and functions: `enum fwh_lock_state` models register values such as `FWH_UNLOCKED` and `FWH_DENY_WRITE`. `struct fwh_xxlock_thunk` carries the desired register value and visible `flstate_t`. `fwh_xxlock_oneblock()` performs one block operation. `fwh_lock_varsize()`, `fwh_unlock_varsize()`, and `fixup_use_fwh_lock()` integrate with MTD/CFI callbacks.

Control flow: command-set fixups call `fixup_use_fwh_lock()`, replacing `mtd->_lock` and `_unlock`. Range calls use `cfi_varsize_frob()` to validate region alignment and iterate blocks. Each block callback maps the target block to a lock-register address, gets exclusive chip access with `get_chip()`, writes the desired lock byte, restores the previous chip state, and calls `put_chip()`.

State and persistence: persistent state lives in hardware lock registers. Software state is limited to transient `flchip` state changes under the chip mutex.

Dependencies and integration points: intended to be included by CFI Intel-extension code. It depends on `cfi_varsize_frob()`, `get_chip()`, `put_chip()`, `map_write()`, and the CFI map geometry model.

Risks: comments explicitly state FWH parts are not interleaved and the code is likely wrong for interleaved chips. It refuses chips below 4 MiB to avoid underflow, but odd map offsets can still be hazardous. These are register writes with no status polling.

Test signals: lock and unlock on FWH/LPC firmware flash, correct register address calculation on 64 KiB boundaries, `-EIO` below the required address window, successful protection against writes after lock, and no regressions on non-FWH CFI parts where the fixup is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/fwh_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/gen_probe.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/gen_probe.c

Purpose: common probing layer for CFI-like NOR probes. It tries bus/interleave/device-width permutations, identifies all non-aliased chips in a map, then dispatches to the command-set driver advertised by the populated CFI/Jedec identification data.

Important APIs, types, and functions: `mtd_do_chip_probe()` is exported and called by `cfi_probe.c` and `jedec_probe.c`. `genprobe_ident_chips()` builds the final `cfi_private` and `flchip` array. `genprobe_new_chip()` iterates interleave and device type. `check_cmd_set()` selects built-in command sets or `cfi_cmdset_unknown()` to request `cfi_cmdset_%04X`.

Control flow: the first chip must probe at offset zero. Its CFI/Jedec `DevSize` plus interleave determine `chipshift`, which bounds the chip bitmap. The helper probes each possible chip slot, copies valid slot starts into the allocated `cfi_private`, and initializes each chip as `FL_READY`. It then tries the primary command set, then the alternate command set, and trims MTD visibility to the map size if needed.

State and persistence: allocates the persistent `cfi_private`, `cfi_ident`, chip array, mutexes, and wait queues used by command-set drivers. Temporary state includes stack `cfi_private` and chip bitmap.

Dependencies and integration points: bridges probe-specific `struct chip_probe` callbacks to command-set modules `cfi_cmdset_0001`, `0002`, and `0020`. It depends on module symbol lookup for command sets that are not directly configured.

Risks: first-chip geometry controls all later probing, so a bad table or false match mis-sizes the whole map. Missing command-set support leaves allocated CFI data to be freed here. Symbol/module lookup is string-based for unknown command sets.

Test signals: correct detection across bank widths and interleave values, alias rejection from probe callbacks, proper fallback to alternate command set, module autoload of command-set drivers, and clean failure when no command set supports a detected chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/gen_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/jedec_probe.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/jedec_probe.c

Purpose: probes legacy JEDEC/autoselect NOR flash chips that do not provide usable CFI tables. It contains a static manufacturer/device table and synthesizes CFI-like geometry so generic command-set drivers can operate the chips.

Important APIs, types, and functions: `jedec_table[]` describes name, manufacturer ID, device ID, size, erase regions, command set, supported device widths, and unlock-address variant. `jedec_probe_chip()` is the probe callback. `jedec_match()` validates IDs, size fit, device width, unlock addresses, and ID disappearance after reset. `cfi_jedec_setup()` allocates and fills synthetic `struct cfi_ident`. `jedec_reset()`, `jedec_read_mfr()`, and `jedec_read_id()` drive autoselect access.

Control flow: generic probe calls the JEDEC callback across geometry permutations. For the first chip, the callback iterates unlock-address variants, enters autoselect, reads IDs, scans the table, and sets up synthetic CFI data on a match. Later chips must match the same mfr/id and are checked against previous chip locations for aliases. Each successful probe resets the device back to read mode.

State and persistence: persistent output is the synthetic `cfi_private` fields: command set, `DevSize`, erase-region table, manufacturer/id, `addr_unlock1/2`, and `CFI_MODE_JEDEC`. The huge table is static read-only device knowledge.

Dependencies and integration points: uses `mtd_do_chip_probe()`, CFI command/address helpers, and chip-driver registration as `jedec_probe`. It hands AMD/Intel/SST-page-style command-set IDs to the same command-set dispatch used by real CFI probes.

Risks: legacy ID probing is inherently ambiguous when flash data resembles IDs or when parts have width-specific IDs not in the table. Unlock-address guessing can issue command sequences to the wrong offsets. The table must be maintained carefully for region order and boot-block variants.

Test signals: known JEDEC chips detected with correct size and erase map, 8-bit versus 16-bit rejection for incompatible entries, alias rejection on mirrored maps, reset returning the array to read mode, and correct command-set handoff for AMD, Intel, SST, and FWH-like devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/jedec_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_absent.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_absent.c

Purpose: implements a placeholder chip driver for socketed or removable map devices when real probing fails. It creates an `MTD_ABSENT` device so expected MTD device nodes can exist even though all data operations fail.

Important APIs, types, and functions: `map_absent_probe()` allocates and initializes `mtd_info`; `map_absent_read()`, `map_absent_write()`, and `map_absent_erase()` all return `-ENODEV`; `map_absent_sync()` and `map_absent_destroy()` are no-ops. The registered chip-driver name is `map_absent`.

Control flow: a board driver can call `do_map_probe("map_absent", map)` after CFI/JEDEC failures. Probe fills size from `map->size`, assigns PAGE_SIZE erase size and writesize 1, takes a module reference, and returns the placeholder MTD.

State and persistence: only the allocated `mtd_info` and `map->fldrv` persist. There is no backing storage or hardware state.

Dependencies and integration points: integrates with the map chip registry and MTD core. It is useful as a fallback policy in board-specific map drivers.

Risks: userspace sees a device but cannot read/write/erase it. Any code that assumes a registered MTD implies usable media must check `type` or operation errors.

Test signals: fallback registration after missing media, open/read/write/erase returning `-ENODEV`, stable device sizing for expected partitions, and clean unregister through `map_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_absent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_ram.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_ram.c

Purpose: exposes a memory-mapped RAM range as an `MTD_RAM` device. It supports direct reads/writes, panic writes, erase-by-filling-0xff, and optional direct `point()` access for XIP-like users.

Important APIs, types, and functions: `map_ram_probe()` initializes `mtd_info` with `MTD_CAP_RAM`; `mapram_read()`, `mapram_write()`, `mapram_erase()`, `mapram_point()`, and `mapram_unpoint()` implement the MTD callbacks. The chip-driver name is `map_ram`.

Control flow: probe currently trusts the map as RAM because the destructive test writes are compiled out. It sets erasesize to PAGE_SIZE and halves it until it divides the mapped size. Read/write use `map_copy_from()` and `map_copy_to()`. Erase writes an all-ones map word across the requested range.

State and persistence: data persists only in the underlying mapped RAM for as long as the platform preserves it. Software state is the `mtd_info` and `map_info`.

Dependencies and integration points: used by map drivers that provide RAM-backed flash-like regions. Direct access is disabled when `map->phys == NO_XIP`.

Risks: no bounds checks are visible in the callbacks, so MTD core validation is relied on. Probe does not verify the memory really is writable RAM. Erase loops in map-bankwidth increments and assumes aligned lengths.

Test signals: read-after-write, panic-write path, erasesize selection for non-page-multiple sizes, erase producing 0xff, `point()` returning virtual and physical addresses when available, and clean module registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_rom.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_rom.c

Purpose: exposes a memory-mapped ROM range as a read-only `MTD_ROM` device. It provides direct reads and optional `point()` access while rejecting writes and erases with `-EROFS`.

Important APIs, types, and functions: `map_rom_probe()` initializes `mtd_info`; `default_erasesize()` reads an optional Device Tree `erase-size` property; `maprom_read()`, `maprom_write()`, `maprom_erase()`, `maprom_point()`, and `maprom_unpoint()` are the callbacks. The chip-driver name is `map_rom`.

Control flow: probe allocates the MTD, sets type/caps/size, installs callbacks, sets erasesize from DT or the whole map size, and takes a module reference. Reads use `map_copy_from()`. `point()` returns direct virtual and optional physical addresses if `map->virt` exists.

State and persistence: no mutable media state exists. The persistent software state is only the mapped address metadata and MTD structure.

Dependencies and integration points: integrates with map drivers, OF properties, and the MTD chip registry. Useful for firmware images or board ROM windows that should be visible through MTD APIs.

Risks: erase size defaults to full map size unless DT supplies `erase-size`, which can affect partition tooling expectations. Like `map_ram`, it relies on upper layers for range validation.

Test signals: read correctness, `point()`/`unpoint()` behavior, write and erase returning `-EROFS`, DT `erase-size` parsing, and successful fallback to full-size erase geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/map_rom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/Kconfig

Purpose: defines Kconfig entries for self-contained MTD device drivers, including PCI/NVRAM/RAM emulation, SPI memories, BCMA serial flash, block-device-backed MTD, PowerNV flash, Intel DG flash, DiskOnChip G3, and ST SPI FSM.

Important APIs, types, and functions: configuration symbols include `MTD_MCHP23K256`, `MTD_MCHP48L640`, `MTD_BCM47XXSFLASH`, `MTD_BLOCK2MTD`, and `MTD_DOCG3`, matching files in this work item. `MTD_DOCG3` selects BCH support and bit-reversal helpers. The menu depends on `MTD != n` and `HAS_IOMEM`.

Control flow: this is build-time control. Symbols gate object inclusion through the Makefile and express dependencies such as `SPI_MASTER`, `BCMA_SFLASH && (MIPS || ARM)`, `BLOCK`, `PPC_POWERNV`, and auxiliary bus/DRM requirements.

State and persistence: no runtime state. It persists kernel configuration choices and selected dependencies.

Dependencies and integration points: consumed by Kbuild, defconfigs, randconfig, and module builds. Help text documents intended hardware and module names.

Risks: incorrect dependencies can expose drivers on unsupported architectures or hide testable drivers from `COMPILE_TEST`. `MTD_DOCG3` help notes write support is experimental/limited, while the current driver does implement write paths, so expectations need care.

Test signals: `olddefconfig`/`menuconfig` visibility, successful builds for each selected symbol, dependency closure for BCH/bitreverse/SPI/BLOCK/BCMA, and module names matching Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/Makefile

Purpose: maps MTD device-driver Kconfig symbols to object files for the `drivers/mtd/devices` subtree.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_DOCG3) += docg3.o`, `obj-$(CONFIG_MTD_BLOCK2MTD) += block2mtd.o`, `obj-$(CONFIG_MTD_MCHP23K256) += mchp23k256.o`, `obj-$(CONFIG_MTD_MCHP48L640) += mchp48l640.o`, and `obj-$(CONFIG_MTD_BCM47XXSFLASH) += bcm47xxsflash.o` cover this work item. `CFLAGS_docg3.o += -I$(src)` supports local trace header inclusion.

Control flow: Kbuild evaluates each `obj-*` line according to configuration, compiling built-in or module objects as requested. The docg3 CFLAGS adjustment ensures `TRACE_INCLUDE_PATH .` can resolve `docg3.h`.

State and persistence: no runtime state. It persists the source-to-object build contract.

Dependencies and integration points: tightly coupled with Kconfig symbol names and source filenames. It integrates with kernel recursive Make and module packaging.

Risks: symbol/filename drift causes silent build omission. The docg3 include-path flag is important for tracepoint generation and can break if the trace header layout changes.

Test signals: all selected objects appear in build logs, modules have expected names, `docg3.o` builds with tracepoints, and unselected drivers do not compile unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.c

Purpose: MTD driver for BCMA ChipCommon-attached serial flash on Broadcom BCM47xx-style systems. It supports ST-compatible and Atmel DataFlash-like controller command paths, a fast memory window for reads, and partition probing with `bcm47xxpart`.

Important APIs, types, and functions: `bcm47xxsflash_cmd()` starts controller opcodes and polls controller busy. `bcm47xxsflash_poll()` waits for flash ready using ST `RDSR` or Atmel status. MTD callbacks are `bcm47xxsflash_erase()`, `bcm47xxsflash_read()`, and `bcm47xxsflash_write()`, with type-specific `bcm47xxsflash_write_st()` and `_write_at()`. `bcm47xxsflash_bcma_probe()` maps resources and registers the MTD.

Control flow: platform probe receives `struct bcma_sflash` platform data, maps the memory window cached or uncached based on ChipCommon revision, infers flash type from BCMA capabilities, fills `mtd_info`, and registers partitions. Reads use the direct window for the first 16 MiB and indirect `FLASHADDR`/`FLASHDATA` reads beyond it. Writes loop until all data is written, because ST writes can stop at page boundaries or after one byte on old controllers and Atmel writes buffer/program one page at a time.

State and persistence: `struct bcm47xxsflash` stores BCMA ChipCommon accessors, type, mapped window, block geometry, size, and embedded `mtd_info`. Persistent media state is serial NOR/DataFlash content and controller registers.

Dependencies and integration points: depends on BCMA, platform devices created by BCMA, ChipCommon register definitions, MTD partition parsers, and `bcm47xxsflash.h` opcodes.

Risks: `bcm47xxsflash_read()` returns `orig_len` instead of zero on success, which is unusual for MTD callbacks and worth checking against caller expectations. Indirect reads always use an ST 4-byte read opcode even for the generic tail path. Cache mapping differs by SoC revision due to corruption risk. Erase/write lack explicit range checks in write path.

Test signals: successful BCMA probe, partition detection, read correctness through window and indirect paths, ST page-program behavior on old/new ChipCommon revisions, Atmel partial-page preservation, erase block size selection, and no timeout logs from controller or flash polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.h

Purpose: private header for the BCMA serial flash driver. It defines controller opcode constants, status bits, the 16 MiB direct window size, supported flash-type enum, and `struct bcm47xxsflash`.

Important APIs, types, and functions: ST opcodes include write-enable, status read, page program, sector erase, subsector erase, and 4-byte read. Atmel opcodes cover buffer load/write/program, page/block erase, status, and compare/reprogram operations. `struct bcm47xxsflash` stores BCMA ChipCommon pointer, register access callbacks, flash type, MMIO window, geometry, and embedded `mtd_info`.

Control flow: no executable code. Constants are consumed by `bcm47xxsflash.c` command helpers and MTD operations.

State and persistence: state layout is the driver-private structure; media persistence is external flash content.

Dependencies and integration points: includes `linux/mtd/mtd.h` and forward-declares `struct bcma_drv_cc`. It is local to the BCMA serial flash implementation.

Risks: opcode values are controller-encoded rather than raw SPI opcodes in several cases, so reuse outside this driver would be unsafe. Adding flash types requires updates to both the enum and status/write/erase logic.

Test signals: build coverage for all constants used by the C file, correct geometry fields from BCMA platform data, and compile-time detection of struct/API drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/block2mtd.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/block2mtd.c

Purpose: emulates an MTD RAM-like device on top of a writable block device. It is useful for testing MTD filesystems on block media or exposing compact-flash-like media through MTD interfaces.

Important APIs, types, and functions: `struct block2mtd_dev` stores the backing block-device file, embedded `mtd_info`, list node, and write mutex. MTD callbacks are `block2mtd_read()`, `block2mtd_write()`, `block2mtd_erase()`, and `block2mtd_sync()`. `add_device()` opens the block device and registers the MTD. `block2mtd_setup()` and `block2mtd_setup2()` parse the `block2mtd=` module/kernel parameter.

Control flow: parameter parsing accepts `<dev>[,[<erasesize>][,<label>]]`, with human-readable size suffixes. During early boot, non-module builds defer parameter handling until `late_initcall`. Reads and writes operate through the block device address-space page cache. Erase reads pages and fills non-0xff pages with 0xff. Writes and erases are serialized by `write_mutex`, dirty pages are rate-limited, and sync calls `sync_blockdev()`.

State and persistence: global `blkmtd_device_list` tracks registered devices. Backing state persists on the block device through the page cache and block layer. Each MTD name is allocated, and the block-device file reference is held until exit.

Dependencies and integration points: depends on block layer file opening, address-space page cache, MTD core registration, kernel parameter plumbing, and early boot device lookup for built-in usage.

Risks: no partition parser is used; the whole block device is exposed. Erase size must divide device size. Using an MTD block device as backing is rejected to avoid recursion. Page-cache manipulation means writeback and invalidation behavior are central correctness risks.

Test signals: module parameter parsing, early-boot deferred creation, read/write/erase across page boundaries, sync flushing, rejection of invalid erase sizes and MTD block backends, custom labels, and clean unregister/free on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/block2mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.c

Purpose: platform MTD NAND driver for M-Systems/SanDisk DiskOnChip G3 devices. It reverse-engineers ASIC register sequences, two-plane page addressing, OOB/ECC layout, bad-block table loading, erase/write/read_oob operations, DPS protection keys, debugfs views, and suspend/resume for cascaded floors.

Important APIs, types, and functions: `docg3_probe()` maps IO space, creates a `docg3_cascade`, initializes BCH, probes up to four floors, registers MTD partitions, and sysfs/debugfs. `doc_probe_device()` identifies chip IDs and fills `mtd_info` through `doc_set_driver_info()`. Core flash paths include `doc_read_oob()`, `doc_write_oob()`, `doc_erase()`, `doc_block_isbad()`, `doc_read_page_prepare()`, `doc_write_page()`, and `doc_ecc_bch_fix_data()`. Sysfs DPS helpers expose key status and key insertion.

Control flow: read paths select the floor, reset the ASIC, seek both planes, start hardware ECC, stream data/OOB through the data area, collect hardware BCH syndrome bytes, optionally correct data using the kernel BCH library, finish the page, and reset selection to floor 0. Write paths can cache OOB for a later data write or write data plus OOB in one page operation, optionally filling Hamming/BCH OOB bytes from hardware. Erase validates block alignment and erases paired plane blocks.

State and persistence: `docg3_cascade` owns shared IO base, BCH control, floor array, and a mutex serializing all hardware access. Each `docg3` stores floor id, reliable-mode setting, maximum block, BBT cache, and a one-page OOB staging buffer. Media state includes NAND data, OOB/ECC, protection areas, and bad-block metadata.

Dependencies and integration points: depends on platform resources or DT compatible `m-systems,diskonchip-g3`, MTD partition parsers `cmdlinepart` and `saftlpart`, BCH and bitrev libraries, debugfs, sysfs, tracepoints defined in `docg3.h`, and the MTD NAND OOB layout API.

Risks: comments note no public specification and unknown timings; many flows rely on observed NOP delays. `doc_probe_device()` allocates the BBT before `max_block` is set, which deserves scrutiny. OOB staging is explicitly unsafe for concurrent applications that split OOB and data writes. Suspend can fail if a floor refuses powerdown. Reliable mode changes size and erase geometry.

Test signals: floor detection, chip-id inverse check, BBT load, read_oob with corrected and uncorrectable ECC stats, raw versus auto/place OOB modes, page writes with hardware ECC OOB fill, erase paired planes, DPS sysfs key paths, debugfs register views, suspend/resume, and tracepoint visibility for register IO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.h

Purpose: private DiskOnChip G3 hardware definition header. It describes IO-space layout, page/OOB/wear geometry, ECC constants, register offsets, command/sequence values, protection bits, cascade and per-floor state structures, logging macros, and a trace event for register IO.

Important APIs, types, and functions: `struct docg3_cascade` stores floor MTDs, shared MMIO base, BCH context, and mutex. `struct docg3` stores device pointer, cascade pointer, floor id, interface/reliable mode, max block, BBT cache, and OOB staging state. Constants define 512-byte data pages, 16-byte OOB, two planes, BCH(14,4) parameters, block layout, and all ASIC registers.

Control flow: no normal runtime functions are implemented, but the `TRACE_EVENT(docg3_io)` declaration is compiled into tracepoints when `docg3.c` defines `CREATE_TRACE_POINTS`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE docg3` rely on the Makefile include path.

State and persistence: the header defines all driver-private state layouts and the persistent flash geometry/protection interpretation used by `docg3.c`.

Dependencies and integration points: includes MTD and Linux tracepoint infrastructure. Consumed directly by `docg3.c`; its trace section integrates with ftrace/perf tooling.

Risks: constants encode reverse-engineered hardware behavior; small mistakes affect all addressing, ECC, protection, and suspend operations. The misspelled `DOC_ECCCONF1_UNKOWN*` names are harmless but signal undocumented bits.

Test signals: successful tracepoint compilation, register reads/writes decoded by `docg3_io`, geometry matching actual media size/OOB layout, BCH constants producing correct correction behavior, and sysfs/debugfs views mapping the expected protection registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp23k256.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp23k256.c

Purpose: SPI MTD RAM driver for Microchip 23K256 and 23LCV1024 serial SRAM devices. It exposes volatile SRAM as `MTD_RAM` with byte-granular read and write operations.

Important APIs, types, and functions: `struct mchp23_caps` describes address width and size. `struct mchp23k256_flash` stores SPI device, mutex, MTD, and selected caps. `mchp23k256_set_mode()` sets sequential mode. `mchp23k256_read()` and `mchp23k256_write()` build two-transfer SPI messages containing opcode/address plus data.

Control flow: probe allocates the private structure, initializes the mutex, writes the status register to enable sequential mode, selects caps from OF match data or defaults to 23K256, fills `mtd_info`, and registers optional platform partitions. Reads and writes serialize SPI access with `flash->lock`, use big-endian address bytes, and report transferred data length excluding command bytes.

State and persistence: SRAM contents are volatile. Persistent software state is the mutex, cap selection, MTD registration, and SPI device pointer. Sequential-mode status register state must remain configured for multi-byte operations.

Dependencies and integration points: depends on SPI core, OF match table, legacy `flash_platform_data` partitions, and MTD core. Compatibles are `microchip,mchp23k256` and `microchip,mchp23lcv1024`.

Risks: the SPI device-id table carries caps in `driver_data`, but probe only uses OF match data and falls back to 23K256, so non-OF 23LCV1024 devices may be sized incorrectly. Bounds checking is left to MTD core. No power-management restore reprograms sequential mode.

Test signals: probe on both compatible strings, non-OF SPI ID sizing check, read/write across address boundaries, retlen accounting, partition registration, and behavior after suspend or power loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp23k256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp48l640.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp48l640.c

Purpose: SPI MTD RAM-like driver for Microchip 48L640 EERAM and Fujitsu MB85RS128TY-compatible nonvolatile serial RAM/FRAM-style devices. It exposes byte-addressed storage through MTD read/write callbacks while honoring device page-transfer quirks.

Important APIs, types, and functions: `struct mchp48_caps` describes size, page size, and whether WEL auto-clears. `mchp48l640_read_status()`, `mchp48l640_waitforbit()`, `mchp48l640_write_prepare()`, and `mchp48l640_set_mode()` manage status and mode bits. `mchp48l640_read_page()`/`write_page()` perform one page-sized SPI transaction; top-level `mchp48l640_read()`/`write()` split requests by page size.

Control flow: probe reads status, sets page-rollover/PRO mode through WREN/WRSR, selects caps from OF match data or defaults, fills `mtd_info`, and registers partitions. Writes wait for ready, enable writes, allocate a DMA-capable command+payload buffer, send opcode/address/data, update retlen, then either wait for WEL auto-clear or explicitly disable writes. Reads wait ready and use `spi_write_then_read()`.

State and persistence: software state is SPI pointer, mutex, MTD, and caps. Device status bits such as RDY, WEL, and PRO are persistent until changed or power-cycled. Media persistence depends on the specific EERAM/FRAM device.

Dependencies and integration points: depends on SPI, jiffies/timeouts, OF matching, legacy `flash_platform_data`, MTD registration, and `linux/string_choices.h` for logging.

Risks: comments say transfers larger than page size return corrupted data despite PRO mode, so request splitting is essential. Probe ignores SPI ID `driver_data` for non-OF instantiation, like the 23K driver. `retlen` assumes non-null in page helpers. Status polling timeout is fixed at 100 ms.

Test signals: status/mode programming, page-split reads and writes for 32-byte and 256-byte variants, WEL auto-clear versus explicit WRDI behavior, timeout handling, retlen correctness, non-OF device sizing, and data retention across resets where hardware supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mchp48l640.c -->
