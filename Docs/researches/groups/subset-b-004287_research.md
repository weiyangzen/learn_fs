# subset-b-004287 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdpstore.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdpstore.c

Purpose: implements the MTD backend for `pstore/blk`, storing persistent kernel oops/panic dmesg records in fixed-size zones inside one MTD partition. It binds by configured MTD name or number and exposes pstore zone operations for read, normal write, erase, and panic write.

Important APIs and types: the file centers on the global `mtdpstore_context` with pstore config/device objects, the selected `struct mtd_info`, and three bitmaps: `usedmap`, `rmmap`, and `badmap`. The pstore callbacks are `mtdpstore_read()`, `mtdpstore_write()`, `mtdpstore_erase()`, and `mtdpstore_panic_write()`. Device lifetime is handled through `mtdpstore_notify_add()`, `mtdpstore_notify_remove()`, `mtdpstore_init()`, and `mtdpstore_exit()`.

Control flow: module init reads `pstore_blk_get_config()`, parses `info->device`, then registers an MTD notifier. On matching MTD add, it validates size, eraseblock, write-size alignment, allocates bitmaps, fills `pstore_device_info`, and calls `register_pstore_device()`. Reads skip bad blocks, tolerate ECC errors by returning available data, classify empty zones as unused, and run a security pass. Writes reject bad/used zones with `-ENOMSG`, write through `mtd_write()`, mark the zone used, and may erase another block to keep at least one free zone available for panic logging. Erase marks a zone unused and either erases the whole eraseblock or lazily marks it removed if live zones remain. Removal flushes removed zones by read/erase/writeback before unregistering.

State and persistence: log payloads persist in flash. The bitmaps are volatile rebuild aids populated through reads and writes during the active session; `badmap` is especially important because panic context cannot call `mtd_block_isbad()`. Removed zones are scrubbed lazily at unregister time if sharing an eraseblock with retained records.

Dependencies and integration points: depends on MTD erase/read/write/panic_write APIs, bad-block support, `pstore_blk`, kernel bitops, and the MTD notifier chain. It currently advertises only `PSTORE_FLAGS_DMESG`.

Risks and test signals: key risks are bitmap sizing and zone/eraseblock alignment, lazy removal preserving valid neighboring logs, panic write operating only from cached bad-block state, and partial/ECC read handling. Tests should exercise configuration by name and number, all validation failures, full-device security erase behavior, bad-block skip paths, deletion of one zone in a multi-zone eraseblock, ECC error reads, panic write on used/bad/free zones, and notifier remove flush ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdpstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdsuper.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdsuper.c

Purpose: provides common superblock mounting helpers for filesystems that live directly on MTD devices rather than normal block devices. Filesystems call `get_tree_mtd()` during mount and `kill_mtd_super()` during teardown.

Important APIs and types: exported APIs are `get_tree_mtd()` and `kill_mtd_super()`. Internal helpers are `mtd_get_sb()` and `mtd_get_sb_by_nr()`. The code attaches `struct mtd_info` to `super_block.s_mtd`, uses `sget_dev()` with `MKDEV(MTD_BLOCK_MAJOR, mtd->index)`, and calls the filesystem-provided `fill_super()` callback.

Control flow: `get_tree_mtd()` requires `fc->source`. It first accepts modern `mtd:<name>` syntax via `get_mtd_device_nm()`, then `mtdN` numeric syntax via `get_mtd_device()`. With `CONFIG_BLOCK`, it also supports legacy `/dev/mtdblockN`-style sources by resolving a block device and checking `MTD_BLOCK_MAJOR`. `mtd_get_sb()` either reuses an already-mounted superblock and releases the extra MTD reference, or initializes a fresh superblock, assigns `s_mtd`, gets the shared MTD backing-dev info, invokes `fill_super()`, and activates the superblock.

State and persistence: there is no on-flash state management here. Runtime state is the superblock reference, the held MTD device reference, `s_mtd`, `s_bdi`, and the filesystem root in the mount context.

Dependencies and integration points: integrates VFS fs_context mount flow, MTD device lookup/reference APIs, optional block-device lookup compatibility, and the MTD core backing-dev object. Direct consumers include MTD-backed filesystems that need common parsing and reference handling.

Risks and test signals: correctness hinges on balanced `get_mtd_device*()`/`put_mtd_device()` references, reuse of existing superblocks, and error unwind after `fill_super()` failure. Tests should cover `mtd:<name>`, `mtdN`, legacy block source with and without `CONFIG_BLOCK`, nonexistent devices, non-MTD sources, duplicate mounts, and `kill_mtd_super()` releasing the MTD reference after `generic_shutdown_super()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdsuper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdswap.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/mtdswap.c

Purpose: implements an `mtd_blktrans` block device that can be used as swap on raw MTD while doing log-structured page remapping, garbage collection, and eraseblock wear leveling.

Important APIs and types: `struct mtdswap_dev` holds logical-to-physical `page_data`, reverse `revmap`, per-eraseblock `swap_eb` records, red-black trees for clean/used/dirty/fragmented/bitflip/failing blocks, counters, current write block, and I/O buffers. Module parameters select `partitions`, spare eraseblock percentage, and optional built-in swap header. The block translation callbacks are `mtdswap_readsect()`, `mtdswap_writesect()`, `mtdswap_discard()`, `mtdswap_flush()`, `mtdswap_background()`, `mtdswap_add_mtd()`, and `mtdswap_remove_dev()`.

Control flow: add probes only configured MTD indexes, validates erase/write/OOB geometry, computes usable size and spare blocks, allocates maps, scans eraseblocks through OOB clean/dirty markers, and registers a blktrans disk. Writes invalidate any old physical page, trigger foreground GC when free pages are low, append data into the current clean eraseblock, and update both maps. Reads translate a logical page, return zeroes for unmapped pages, retry transient errors, mark bitflip/read-error eraseblocks, and expose an optional fake `SWAPSPACE2` header. Discard clears mappings and feeds affected eraseblocks back into the correct tree. GC picks dirty, fragmented, bitflip, failing, or low-wear blocks, moves active pages, erases, writes clean markers, and reinserts blocks.

State and persistence: logical mappings are volatile and reconstructed from flash contents and OOB markers after attach. Persistent state is page data plus clean/dirty OOB markers carrying erase counts. Erase counts are recovered from markers, with median estimation for no-magic blocks after interrupted erase/header writes.

Dependencies and integration points: depends on MTD read/write/OOB/erase/bad-block APIs, `mtd_blktrans`, Linux swap headers, rbtree ordering by erase count, debugfs statistics, and MTD OOB free bytes for markers.

Risks and test signals: high-risk areas include crash recovery after interrupted marker writes, `spare_eblks` accounting, write-error bad-block transitions, current-write block races with background GC, OOB marker layout, and wear-leveling selection. Tests should simulate bitflips, ECC errors, bad-block marking, short reads/writes, discard after write, header mode page offsets, GC under low clean-block counts, median erase-count recovery, and debugfs counters under the blktrans lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/mtdswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/Kconfig

Purpose: defines the top-level NAND Kconfig menu and selects the generic NAND core, NAND family submenus, and ECC engine options.

Important APIs and types: configuration symbols include `MTD_NAND_CORE`, `MTD_NAND_ECC`, `MTD_NAND_ECC_SW_HAMMING`, `MTD_NAND_ECC_SW_HAMMING_SMC`, `MTD_NAND_ECC_SW_BCH`, `MTD_NAND_ECC_MXIC`, `MTD_NAND_ECC_MEDIATEK`, and `MTD_NAND_ECC_REALTEK`. It sources OneNAND, raw NAND, and SPI-NAND Kconfig trees.

Control flow: enabling a NAND family can select or depend on `MTD_NAND_CORE`. ECC symbols select `MTD_NAND_ECC`, which in turn selects core support. Software Hamming defaults on with raw NAND, while BCH and hardware engines are opt-in. Hardware engines constrain builds with `HAS_IOMEM`, SoC architecture predicates, `HAS_DMA` for Realtek, or `COMPILE_TEST`.

State and persistence: this file has no runtime state. Its persistent effect is build-time feature selection that controls which NAND framework and ECC drivers are compiled.

Dependencies and integration points: integrates the generic NAND build with `drivers/mtd/nand/onenand`, `raw`, and `spi`. It maps directly to object inclusion in the sibling Makefile and indirectly to device-tree compatible drivers at runtime.

Risks and test signals: regressions appear as missing objects, invalid dependencies, or unusable ECC choices. Build tests should cover allnoconfig fragments for software-only NAND, raw NAND default Hamming, each hardware ECC under `COMPILE_TEST`, Realtek with DMA availability, and SmartMedia byte-order Hamming only when Hamming is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/Makefile

Purpose: maps NAND Kconfig selections to build objects for the generic NAND core, optional ECC engines, Qualcomm shared code, and NAND family subdirectories.

Important APIs and types: `nandcore-objs := core.o bbt.o` builds the base framework. Conditional additions include `ecc.o`, `ecc-sw-hamming.o`, `ecc-sw-bch.o`, and `ecc-mxic.o` into `nandcore`, while MediaTek and Realtek hardware ECC are separate objects. Subdirectories `onenand/`, `raw/`, and `spi/` are always visited through `obj-y`.

Control flow: `obj-$(CONFIG_MTD_NAND_CORE) += nandcore.o` gates the generic framework. `nandcore-$(CONFIG_...)` composes built-in framework pieces based on ECC options. Separate platform-driver ECC engines are emitted as their own modules/objects. `qpic_common.o` is shared by SPI QPIC SNAND and raw Qualcomm NAND configs.

State and persistence: no runtime state. Build products determine which exported NAND symbols and platform drivers are present.

Dependencies and integration points: tied to symbols declared in `drivers/mtd/nand/Kconfig` and subdirectory Kconfigs. The object grouping matters because software ECC helpers and generic ECC code become part of `nandcore`, while on-host platform engines can probe independently.

Risks and test signals: risks include unresolved symbols if ECC helper objects are excluded incorrectly, duplicate inclusion of shared QPIC code, or missing subdirectory traversal. Test signals are successful builds for core-only, software BCH/Hamming, MXIC as core-integrated support, MediaTek/Realtek module builds, and combinations of QPIC configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/bbt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/bbt.c

Purpose: provides the generic in-memory NAND bad block table (BBT) cache used by the NAND core to track eraseblock status values.

Important APIs and types: exported functions are `nanddev_bbt_init()`, `nanddev_bbt_cleanup()`, `nanddev_bbt_update()`, `nanddev_bbt_get_block_status()`, and `nanddev_bbt_set_block_status()`. The cache is `nand->bbt.cache`, a packed bitmap where each eraseblock consumes `fls(NAND_BBT_BLOCK_NUM_STATUS)` bits.

Control flow: init allocates enough bitmap bits for all eraseblocks. Get validates the entry, computes the containing word and bit offset, stitches across a word boundary when necessary, and masks the status field. Set validates the entry, clears and writes the packed status bits, and handles cross-word writes. Update is currently a no-op because on-flash BBT persistence is not implemented in this generic layer.

State and persistence: the BBT is volatile memory only. It can cache unknown, good, worn, factory-bad, or reserved status values, but persistence to NAND is intentionally absent here; low-level bad-block markers and future on-flash BBT support are separate concerns.

Dependencies and integration points: used by `nanddev_isbad()`, `nanddev_markbad()`, and `nanddev_isreserved()` in `core.c`. Depends on NAND geometry helpers, bitmap allocation/free, and exported GPL symbols for NAND drivers.

Risks and test signals: packed-bit arithmetic is the main risk, especially statuses crossing `BITS_PER_LONG`. Tests should cover entry 0, last entry, out-of-range entries, all status enum values, cross-word offsets on 32-bit and 64-bit builds, cleanup after failed init callers, and the current no-op behavior of `nanddev_bbt_update()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/bbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/core.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/core.c

Purpose: implements the generic NAND device framework: erased-page checking, bad/reserved block handling, generic erase helpers, ECC engine setup, and core NAND device initialization.

Important APIs and types: exported functions include `nand_check_erased_ecc_chunk()`, `nanddev_isbad()`, `nanddev_markbad()`, `nanddev_isreserved()`, `nanddev_mtd_erase()`, `nanddev_mtd_max_bad_blocks()`, `nanddev_ecc_engine_init()`, `nanddev_ecc_engine_cleanup()`, `nanddev_init()`, and `nanddev_cleanup()`. It consumes `struct nand_device`, `nand_ops`, `nand_memory_organization`, `nand_pos`, BBT helpers, and ECC helper APIs.

Control flow: erased-buffer checking counts zero bits against a threshold across data, ECC bytes, and optional protected OOB, restoring buffers to `0xff` on tolerated bitflips. Bad-block checks use expert-analysis bypass, then the BBT with lazy low-level `isbad()` lookup, or direct ops when no BBT exists. Markbad calls the low-level hook, updates BBT status to worn, persists through `nanddev_bbt_update()`, and increments `mtd->ecc_stats.badblocks`. Generic erase walks eraseblocks in a requested range and refuses bad/reserved blocks. ECC init reads device-tree user config, selects none/software/on-die/on-host engine, initializes its context, and warns if it is weaker than datasheet requirements. Device init validates ops and memory geometry, derives row conversion shifts, fills MTD geometry, and allocates the BBT.

State and persistence: persistent state is only through low-level erase/markbad hooks and any engine-managed ECC metadata. The generic BBT is in-memory. MTD geometry and ECC context live for the device lifetime.

Dependencies and integration points: integrates MTD core, NAND controller drivers, generic ECC engine selection in `ecc.c`, BBT in `bbt.c`, device tree ECC properties, and chip requirements/defaults supplied by identification layers.

Risks and test signals: risks include lazy BBT cache staleness, mismatched memory geometry shifts, erase range off-by-one handling, and weak ECC accepted with only a warning. Tests should cover invalid ops/geometry, erased chunk thresholds, expert-analysis mode, BBT unknown-to-good/factory-bad transitions, markbad failure and stats, multi-block erase fail address, max-bad-blocks per LUN, all ECC engine types including probe defer, and cleanup after partial ECC init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mtk.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mtk.c

Purpose: drives MediaTek NAND ECC hardware blocks and exports helper APIs used by MediaTek NAND controllers to configure, enable, wait for, and query encode/decode operations.

Important APIs and types: key structures are `mtk_ecc_caps` for SoC register layout and strength tables, and `mtk_ecc` for device state, registers, clock, completion, mutex, sector mask, and parity buffer. Exported APIs include `of_mtk_ecc_get()`, `mtk_ecc_release()`, `mtk_ecc_enable()`, `mtk_ecc_disable()`, `mtk_ecc_wait_done()`, `mtk_ecc_encode()`, `mtk_ecc_get_stats()`, `mtk_ecc_adjust_strength()`, and `mtk_ecc_get_parity_bits()`.

Control flow: probe allocates state, chooses compatible-specific caps, maps registers, gets the clock and IRQ, sets a 32-bit DMA mask, and installs the IRQ handler. Consumers acquire the engine through a `nand-ecc-engine` or legacy `ecc-engine` phandle; acquisition enables the clock and initializes hardware idle/disabled state. `mtk_ecc_enable()` locks the engine, waits idle, programs encode/decode config, arms interrupts when needed, and starts the selected operation. Encode maps the data buffer for DMA, enables the encoder, waits for completion, copies generated parity registers into the caller buffer, unmaps DMA, and disables/unlocks. Decode completion is signaled by IRQ and stats are later read from decode enumeration registers.

State and persistence: state is runtime-only: register programming, clock state, completion, mutex ownership, and per-operation sector mask. ECC bytes become persistent only when the NAND controller writes them to OOB.

Dependencies and integration points: depends on platform devices, OF matching for `mediatek,*-ecc`, clocks, IRQs, DMA mapping, I/O polling, and `<linux/mtd/nand-ecc-mtk.h>`. It is a provider library for host controller drivers, not a generic `nand_ecc_engine` registration.

Risks and test signals: risks include strength table selection, IRQ status clearing, timeout paths unlocking the mutex, DMA map/unmap balance, and suspend/resume clock transitions. Tests should cover each compatible caps table, invalid strength rejection, NFI versus non-NFI modes, encode timeout and success, decode stats for corrected/failed sectors, phandle probe defer, clock enable failure, and concurrent callers serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mxic.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mxic.c

Purpose: implements the Macronix Data Processing Engine NAND ECC controller, supporting both external on-host ECC and a pipelined/mapping mode used with specific host controllers.

Important APIs and types: `mxic_ecc_engine` owns registers, optional IRQ, completion, mutex, and two `nand_ecc_engine` objects. `mxic_ecc_ctx` stores selected data/OOB step sizes, parity/meta sizes, per-step status bytes, request tweak context, temporary OOB-with-status buffer, scatterlists, and current request. Exported integration helpers include `mxic_ecc_get_pipelined_ops()`, `mxic_ecc_get_pipelined_engine()`, `mxic_ecc_put_pipelined_engine()`, and `mxic_ecc_process_data_pipelined()`.

Control flow: common context init rejects small-OOB NAND, installs a custom OOB layout, enables status interrupts, chooses strength from user or chip requirements, forces 1 KiB steps, tunes strength to fit OOB, validates hardware spare/meta/parity sizing, and allocates request/OOB buffers. External prepare on writes tweaks the request, inserts status-byte gaps in OOB, DMA maps data and OOB, processes each step through SDMA, then copies calculated ECC bytes back into the linear OOB layout. External finish on reads runs the engine per step, extracts status bytes, reconstructs OOB, restores the original request, and updates ECC stats. Pipelined prepare maps buffers and programs DMA addresses while leaving processing to the host path; finish unmaps, extracts read status, and restores. Probe maps registers, disables engine/interrupts, optionally requests an IRQ or falls back to polling, initializes the external engine, and registers it as an on-host hardware engine.

State and persistence: runtime state includes hardware configuration, DMA mappings, status bytes, and request bounce buffers. Persistent state is the NAND OOB ECC layout generated or consumed by the controller.

Dependencies and integration points: integrates with the generic NAND ECC engine registry, MTD OOB layout helpers, DMA scatterlists, platform/OF phandles, optional IRQ completion, and host drivers using the pipelined API.

Risks and test signals: risks include OOB/status-byte reconstruction, strength downgrade to fit OOB, lock lifetime across pipelined prepare/finish, DMA unmap on early errors, IRQ versus polling behavior, and preserving bad-block markers by requiring packed layout. Tests should cover external read/write, pipelined read/write, missing IRQ polling, timeout handling, invalid OOB geometry, phandle probe defer, status values for no-error/erased/corrected/uncorrectable, and cleanup after partial init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-mxic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-realtek.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-realtek.c

Purpose: provides a Realtek RTL93xx on-host hardware ECC engine for a vendor-specific BCH OOB layout used by supported 2 KiB-page NAND systems.

Important APIs and types: `rtl_ecc_engine` owns the generic `nand_ecc_engine`, mutex, noncoherent DMA buffer, DMA address, and regmap. `rtl_ecc_ctx` stores the engine pointer, request tweak context, step count, BCH mode, strength, and parity size. Engine hooks are `rtl_ecc_init_ctx()`, `rtl_ecc_cleanup_ctx()`, `rtl_ecc_prepare_io_req()`, and `rtl_ecc_finish_io_req()`.

Control flow: probe maps registers through regmap, allocates a single noncoherent DMA buffer, initializes an external on-host `nand_ecc_engine`, and registers it globally. Context init strictly validates geometry and user ECC config: 2048-byte page, at least 64 OOB bytes, BCH, strength 6, OOB placement, and 512-byte step. It installs an OOB layout with 6 free bytes per step, reserving the first two for bad-block indicators, and parity after all free-byte regions. Prepare tweaks partial requests and, on writes, runs each 512-byte step through the engine to fill parity. Finish restores writes directly; on reads it decodes each step, falls back to `nand_check_erased_ecc_chunk()` for erased chunks that hardware reports badly, updates ECC stats, restores the original request, and returns max bitflips or `-EBADMSG`.

State and persistence: runtime state is the shared DMA staging buffer and per-NAND context. Persistent state is the fixed OOB arrangement containing protected free bytes and parity bytes.

Dependencies and integration points: depends on generic NAND ECC registry, MTD OOB layouts, DMA sync APIs for noncoherent memory, regmap MMIO, platform OF compatible `realtek,rtl9301-ecc`, and erased-page checking from NAND core.

Risks and test signals: risks include the intentionally narrow geometry support, protected bad-block indicator compatibility, noncoherent DMA synchronization, polling timeout, and handling all-ones erased chunks. Tests should cover unsupported geometry/config rejection, OOB layout offsets, encode/decode per step, bitflip stat accumulation, uncorrectable reads, erased-chunk fallback, raw mode no-op, cleanup unregistering the engine, and concurrent requests serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-realtek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-bch.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-bch.c

Purpose: implements the generic software BCH NAND ECC engine using the kernel BCH library, supporting multi-bit correction for large-page NAND.

Important APIs and types: exported helpers are `nand_ecc_sw_bch_calculate()`, `nand_ecc_sw_bch_correct()`, `nand_ecc_sw_bch_init_ctx()`, `nand_ecc_sw_bch_cleanup_ctx()`, and `nand_ecc_sw_bch_get_engine()`. The private `nand_ecc_sw_bch_conf` holds the BCH control object, code size, ECC mask, error-location array, request tweak context, and OOB calculation/code buffers.

Control flow: context init requires large-page OOB, installs a large-page OOB layout if none exists, derives step size/strength from user config or defaults, optionally maximizes strength from available OOB space, computes code size, allocates buffers, initializes BCH parameters, builds an erased-page ECC mask, and validates OOB layout capacity. Prepare ignores raw and data-less OOB-only operations, expands partial requests, and on writes calculates BCH ECC for each step and stores it through `mtd_ooblayout_set_eccbytes()`. Finish ignores raw operations, restores write requests, and on reads extracts stored ECC bytes, recalculates ECC, corrects each step through `bch_decode()`, updates `mtd->ecc_stats`, restores the request, and returns max corrected bitflips.

State and persistence: runtime state is per-NAND BCH context and temporary buffers. Persistent state is the ECC bytes written into the NAND OOB layout.

Dependencies and integration points: depends on `lib/bch`, generic NAND ECC request tweaking, MTD OOB layout helpers, and `ecc.c` software engine selection for `NAND_ECC_ALGO_BCH`.

Risks and test signals: risks include invalid BCH parameter derivation, OOB capacity mismatch, erased-page mask correctness, partial request bounce behavior, and stat handling for uncorrectable errors. Tests should cover default config, user config, maximize mode, impossible OOB layouts, raw operations, write ECC placement, one or more corrected bitflips, ECC-area-only errors, uncorrectable pages, and cleanup after allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-bch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-hamming.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-hamming.c

Purpose: implements the generic software Hamming ECC engine for 256- or 512-byte NAND ECC steps, correcting one data bit and detecting common multi-bit errors.

Important APIs and types: exported low-level functions are `ecc_sw_hamming_calculate()` and `ecc_sw_hamming_correct()`. NAND-facing exports are `nand_ecc_sw_hamming_calculate()`, `nand_ecc_sw_hamming_correct()`, `nand_ecc_sw_hamming_init_ctx()`, `nand_ecc_sw_hamming_cleanup_ctx()`, and `nand_ecc_sw_hamming_get_engine()`. Lookup tables `invparity`, `bitsperbyte`, and `addressbits` drive parity and correction decoding.

Control flow: calculation folds the data buffer into row and column parity values, handles endian differences, optionally emits SmartMedia byte order, and produces three ECC bytes per step. Correction XORs read and calculated ECC, distinguishes no error, single data-bit error, single ECC-bit error, and uncorrectable error, flipping the addressed data bit when possible. Context init installs default small-page or legacy large-page Hamming OOB layouts, chooses 256-byte steps unless the user explicitly selects 512, allocates request tweak and OOB buffers, and sets strength to 1. Prepare and finish mirror the BCH engine: raw/data-less requests are no-ops, writes calculate and place ECC bytes, reads extract OOB ECC, correct data per step, update ECC stats, and restore tweaked requests.

State and persistence: runtime state is the per-device Hamming config and temporary buffers. Persistent state is the three ECC bytes per step in the configured OOB layout.

Dependencies and integration points: selected by generic ECC code for `NAND_ECC_ALGO_HAMMING`; depends on MTD OOB layout helpers, request tweaking, optional `CONFIG_MTD_NAND_ECC_SW_HAMMING_SMC` behavior through config data, and legacy NAND OOB conventions.

Risks and test signals: risks include byte-order compatibility, 256 versus 512 step addressing, unaligned buffers, OOB layout mismatch, and correct classification of ECC-bit-only errors. Tests should cover known ECC vectors, single-bit corrections across first/last byte and bit, single ECC-bit error, double-bit uncorrectable error, SmartMedia ordering, raw mode, small and large OOB layouts, and request bounce restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-hamming.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc.c

Purpose: defines the generic NAND ECC engine abstraction, default OOB layouts, device-tree ECC configuration parsing, request tweaking helpers, software engine lookup, and on-host hardware engine registry.

Important APIs and types: exported front-door APIs are `nand_ecc_init_ctx()`, `nand_ecc_cleanup_ctx()`, `nand_ecc_prepare_io_req()`, and `nand_ecc_finish_io_req()`. Layout exports include `nand_get_small_page_ooblayout()`, `nand_get_large_page_ooblayout()`, and `nand_get_large_page_hamming_ooblayout()`. Configuration and registry APIs include `of_get_nand_ecc_user_config()`, `nand_ecc_is_strong_enough()`, request tweak helpers, software/on-die/on-host getters, hardware engine register/unregister, put, and `nand_ecc_get_engine_dev()`.

Control flow: the prepare/finish wrappers call engine hooks when present. OOB layout helpers describe legacy small-page, large-page, and large-page Hamming ECC/free regions. OF parsing recognizes no-ECC, software ECC, on-die self phandle, on-host phandle, placement, algorithm, step size, strength, and maximize-strength flags. Strength validation compares correction density and absolute strength against chip requirements. Request tweaking expands partial data/OOB I/O into full-page bounce buffers so ECC engines can operate over whole pages, then restores read data or original request metadata. On-host engines register in a mutex-protected global list and are matched by device pointer from `nand-ecc-engine` phandles.

State and persistence: runtime state includes per-device ECC context, temporary bounce buffers, and the global list of registered on-host engines. Persistent state is only the OOB layout and ECC bytes produced by concrete engines.

Dependencies and integration points: central integration point for NAND core, software BCH/Hamming engines, on-die engines supplied by chips, on-host platform engines such as MXIC and Realtek, MTD OOB APIs, platform OF lookup, and device references.

Risks and test signals: risks include OF phandle reference handling, duplicate hardware registration races, partial-request bounce correctness, OOB layout edge cases, and weak-ECC comparison math. Tests should cover all engine types, invalid strings, missing/probe-deferred phandles, software algo defaults, OOB layout regions for 8/16/64/128-byte OOB, request tweak read/write restore paths, engine device indirection, and register/unregister idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Kconfig

Purpose: declares OneNAND support and board/controller-specific OneNAND driver options under the NAND menu.

Important APIs and types: symbols include `MTD_ONENAND`, `MTD_ONENAND_VERIFY_WRITE`, `MTD_ONENAND_GENERIC`, `MTD_ONENAND_OMAP2`, `MTD_ONENAND_SAMSUNG`, `MTD_ONENAND_OTP`, and `MTD_ONENAND_2X_PROGRAM`.

Control flow: `MTD_ONENAND` is a `menuconfig` gated by `HAS_IOMEM`; all suboptions are visible only when it is enabled. Generic platform-device support is optional. OMAP2/OMAP3 support requires OF and OMAP GPMC, Samsung support is limited to matching SoCs or compile testing, OTP toggles one-time-programmable support, and 2X program enables a special two-plane programming mode for chips that support it.

State and persistence: no runtime state. The symbols control whether OneNAND core, glue drivers, OTP paths, write verification, and 2X program behavior are compiled.

Dependencies and integration points: maps to `onenand/Makefile`, OneNAND core files, generic platform glue, OMAP/Samsung controller drivers, and MTD partition/device registration at runtime.

Risks and test signals: risks include exposing SoC-specific drivers under wrong architecture constraints or enabling behavioral features without matching chip support. Build tests should cover OneNAND disabled, core only, generic driver as module, OMAP/Samsung compile-test builds, OTP enabled, verify-write enabled, and 2X program enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Makefile

Purpose: builds the OneNAND core and optional board/controller-specific glue drivers.

Important APIs and types: `obj-$(CONFIG_MTD_ONENAND) += onenand.o` builds the core aggregate, while `obj-$(CONFIG_MTD_ONENAND_GENERIC)`, `obj-$(CONFIG_MTD_ONENAND_OMAP2)`, and `obj-$(CONFIG_MTD_ONENAND_SAMSUNG)` include `generic.o`, `onenand_omap2.o`, and `onenand_samsung.o`. `onenand-objs = onenand_base.o onenand_bbt.o` composes the core object.

Control flow: the Makefile follows Kconfig selection directly. Enabling base OneNAND compiles base operations and OneNAND bad-block-table support; platform glue is independent and conditional.

State and persistence: no runtime state. Build outputs determine which OneNAND platform drivers and core symbols are present.

Dependencies and integration points: tied to `onenand/Kconfig`, core OneNAND APIs in `<linux/mtd/onenand.h>`, and platform drivers that register MTD devices.

Risks and test signals: risks are mostly build integration failures: missing core object pieces, glue objects built without core dependencies, or module link errors. Test signals are successful builds for built-in and module variants of `MTD_ONENAND`, plus each optional glue driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/generic.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/generic.c

Purpose: implements a simple platform-device glue layer for memory-mapped OneNAND flash on generic boards.

Important APIs and types: `struct onenand_info` embeds `struct mtd_info` and `struct onenand_chip`. The platform driver uses `generic_onenand_probe()` and `generic_onenand_remove()` under driver name `onenand-flash`. It consumes optional `struct onenand_platform_data` for `mmcontrol` and partition arrays.

Control flow: probe allocates `onenand_info`, reserves the memory resource, ioremaps it into `onenand.base`, copies optional memory-control hook, obtains IRQ 0, initializes `mtd.dev.parent` and `mtd.priv`, scans the chip with `onenand_scan()`, registers the MTD device and partitions with `mtd_device_register()`, and stores drvdata. Error paths unwind ioremap, memory region, and allocation. Remove calls `onenand_release()`, releases the memory region, unmaps the base, and frees the wrapper.

State and persistence: runtime state is the mapped register/window base, IRQ, MTD object, OneNAND chip object, and registered partitions. Persistent state is the flash contents managed by the OneNAND core.

Dependencies and integration points: depends on platform resources, I/O memory mapping, OneNAND core scanning/release, MTD device registration, optional board platform data, and partition registration.

Risks and test signals: risks include resource lifetime ordering, missing/invalid IRQ or memory resources, partition registration failure handling, and compatibility with the renamed `onenand-flash` platform data format. Tests should cover successful probe/remove, no platform data, busy memory region, ioremap failure, IRQ failure, scan failure, partition registration failure, and repeated bind/unbind with resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/generic.c -->
