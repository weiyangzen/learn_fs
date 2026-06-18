# Research: subset-b-004288

Grouped research report for the NAND/OneNAND files assigned to `subset-b-004288`. Each section is wrapped for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_base.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_base.c

## Purpose
`onenand_base.c` is the generic MTD OneNAND core. It translates MTD read, write, erase, bad-block, lock, suspend/resume, panic write, and optional OTP operations into OneNAND register commands, and exposes `onenand_scan()` / `onenand_release()` for platform glue drivers. It also handles Flex-OneNAND address conversion, SLC/MLC boundary management, BufferRAM caching, OOB layout selection, ECC status interpretation, and bad block table integration.

## Important APIs, Types, and Functions
The exported entry points are `onenand_scan()`, `onenand_release()`, `onenand_addr()`, and `flexonenand_region()`. The core works through `struct onenand_chip` callbacks: `read_word`, `write_word`, `command`, `wait`, `bbt_wait`, `read_bufferram`, `write_bufferram`, `chip_probe`, `unlock_all`, `scan_bbt`, and `block_markbad`. Generic helpers include `onenand_command()`, `onenand_wait()`, `onenand_read_ops_nolock()`, `onenand_mlc_read_ops_nolock()`, `onenand_write_ops_nolock()`, `onenand_erase()`, `onenand_do_lock_cmd()`, and the OTP walker functions under `CONFIG_MTD_ONENAND_OTP`.

Key state lives in `struct onenand_chip`: register base, device/version IDs, geometry shifts, DDP density masks, Flex-OneNAND boundaries/diesizes, BufferRAM tags, page/OOB/verify buffers, lock/waitqueue state, ECC/feature option bits, and bad-block management. Module parameters `flex_bdry[]` and `otp` can alter Flex-OneNAND boundary programming and OTP lock behavior at load time.

## Control Flow
`onenand_scan()` fills missing callbacks with defaults, probes IDs with `onenand_probe()`, allocates buffers, initializes locks, selects an OOB layout by OOB size/Flex mode, wires MTD methods, unlocks blocks unless skipped, scans the BBT, and optionally applies requested Flex-OneNAND boundaries. Reads acquire the device with `onenand_get_device()`, use BufferRAM hits when possible, issue `ONENAND_CMD_READ` / `READOOB`, wait for completion, copy DataRAM/SpareRAM, and translate ECC stats into return codes. Writes enforce subpage alignment, fill DataRAM and SpareRAM, program pages, optionally cache-program, verify if configured, and invalidate BufferRAM on errors. Erase validates block alignment and bad blocks, then chooses block-by-block or multi-block erase plus verify. Lock/unlock issues either continuous-range or per-block commands depending on feature bits.

## State and Persistence
Persistent flash effects are page/OOB programming, block erasure, block lock state, OTP writes/locks, bad-block marker writes, and Flex-OneNAND PI boundary changes. Volatile kernel state includes BufferRAM cache tags, MTD ECC counters, allocated buffers, BBT RAM, current chip state, waitqueue/completion state, and feature flags. Flex-OneNAND boundary changes are especially persistent because `flexonenand_set_boundary()` erases/programs PI metadata after checking that converted blocks are erased.

## Dependencies and Integration Points
The file depends on the Linux MTD core, `linux/mtd/onenand.h`, `linux/mtd/partitions.h`, waitqueues, completions, IRQs, jiffies, and I/O accessors. Platform drivers integrate by pre-populating callbacks before calling `onenand_scan()`. Bad-block support integrates through `onenand_default_bbt()` and `onenand_bbt_read_oob()`. MTD clients use the installed `_read_oob`, `_write_oob`, `_erase`, `_sync`, `_lock`, `_unlock`, `_suspend`, `_resume`, `_block_isbad`, and `_block_markbad` methods.

## Risks
This code is hardware-stateful and sensitive to register ordering, BufferRAM selection, and DDP/Flex address translation. Alignment checks reject invalid writes, but partial-page paths still depend on correct subpage geometry. Multi-block erase must not cross DDP boundaries incorrectly. Flex boundary programming can corrupt data if erase-state checks are wrong. `onenand_get_device()` waits uninterruptibly, so stuck state transitions can hang callers. ECC accounting intentionally returns success for corrected data but may surface `-EBADMSG` after full-length reads. OTP lock behavior is controlled by a module parameter and is irreversible on real devices.

## Test Signals
Useful signals are successful `onenand_scan()` and `mtd_device_register()` in platform drivers, correct geometry/OOB layout logs, BBT scan results, ECC corrected/failed counters, lock/unlock status logs, erase verify failures, and boot tests across normal read/write/erase, OOB-only access, panic write, suspend/resume, DDP boundary access, and Flex-OneNAND boundary changes. Kconfig variants with `CONFIG_MTD_ONENAND_VERIFY_WRITE` and `CONFIG_MTD_ONENAND_OTP` should be compiled when touching those paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_bbt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_bbt.c

## Purpose
`onenand_bbt.c` implements the memory-resident bad block table used by the generic OneNAND core. It scans factory bad-block markers in OOB, builds a two-bit-per-block RAM table, and provides the `isbad_bbt` callback used by `onenand_base.c`.

## Important APIs, Types, and Functions
The public function is `onenand_default_bbt(struct mtd_info *mtd)`, which allocates `struct bbm_info`, selects the default marker descriptor, and calls `onenand_scan_bbt()`. Internals include `check_short_pattern()`, `create_bbt()`, `onenand_memory_bbt()`, `onenand_isbad_bbt()`, and the static `largepage_memorybased` `struct nand_bbt_descr` with the `{ 0xff, 0xff }` good-block pattern at OOB offset 0.

## Control Flow
`onenand_default_bbt()` installs the default pattern and delegates to `onenand_scan_bbt()`. `onenand_scan_bbt()` allocates `bbm->bbt`, stores the erase shift, defaults `bbm->isbad_bbt`, then calls `onenand_memory_bbt()`. `create_bbt()` iterates all eraseblocks, reads the first two pages' OOB marker bytes with `onenand_bbt_read_oob()`, treats fatal read errors as scan failure, and marks a block bad if the read returns a non-fatal BBT error or if the expected `0xff` pattern is missing. Flex-OneNAND uses `flexonenand_region()` and `mtd->eraseregions[]` to advance by variable erase sizes.

## State and Persistence
The BBT is RAM-only and allocated under `this->bbm->bbt`; it is freed by `onenand_release()`. It mirrors persistent factory or software OOB bad-block markers but does not itself persist to flash. `mtd->ecc_stats.badblocks` is incremented for detected initial bad blocks.

## Dependencies and Integration Points
This file depends on `struct onenand_chip`, `struct bbm_info`, `struct nand_bbt_descr`, `onenand_bbt_read_oob()`, `onenand_block()`, and `flexonenand_region()` from the OneNAND core/header. `onenand_base.c` installs this scanner when platform drivers do not provide a custom `scan_bbt`.

## Risks
The table size uses `this->chipsize` and `this->erase_shift`, while Flex devices may expose variable `mtd->size` and erase regions; scan correctness depends on the Flex advancement logic. The descriptor expects a short OOB pattern at offset 0 and does not do a full empty-page check. Non-fatal read/ECC errors during marker reads cause the block to be marked bad, which is conservative but can reduce usable capacity if read paths are noisy.

## Test Signals
Boot logs should show bad-block scan progress and any initial bad block notices. Tests should verify `mtd->_block_isbad` results before and after `onenand_block_markbad()`, BBT behavior on Flex-OneNAND variable erase regions, scan failure on `ONENAND_BBT_READ_FATAL_ERROR`, and clean release of `bbm->bbt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_bbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_omap2.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_omap2.c

## Purpose
`onenand_omap2.c` is the OMAP2/OMAP3 OneNAND platform glue. It maps the OneNAND memory window behind OMAP GPMC, optionally uses a GPIO interrupt for wait completion, optionally uses DMAengine for BufferRAM transfers, programs optimized GPMC/OneNAND timings, calls the generic `onenand_scan()`, and registers the MTD device.

## Important APIs, Types, and Functions
The central type is `struct omap2_onenand`, which embeds `struct mtd_info`, `struct onenand_chip`, GPMC chip-select state, physical base, optional interrupt GPIO, completions, and a DMA channel. Key functions are `omap2_onenand_probe()`, `omap2_onenand_remove()`, `omap2_onenand_shutdown()`, `omap2_onenand_wait()`, `omap2_onenand_set_cfg()`, `omap2_onenand_get_freq()`, and the DMA-backed `omap2_onenand_read_bufferram()` / `omap2_onenand_write_bufferram()`.

## Control Flow
Probe reads the DT `reg` property as the GPMC chip select, allocates state, maps the memory resource, obtains optional `int` GPIO, requests an IRQ when present, and installs `onenand.wait = omap2_onenand_wait`. It then requests a memcpy DMA channel; if available, it overrides BufferRAM read/write callbacks. After initializing `mtd.priv`, parent device, and OF node, it calls `onenand_scan()`. If the OneNAND version encodes a known frequency, it chooses latency, calls `gpmc_omap_onenand_set_timings()`, writes OneNAND sync/burst configuration, and finally calls `mtd_device_register()`.

`omap2_onenand_wait()` uses short polling for reset/preparing erase/verify erase, interrupt GPIO waits for non-read operations, and polling with interrupts disabled for reads. It checks ECC status on read completion, updates MTD ECC counters, and reports controller/timeout/write-protect errors. BufferRAM DMA paths use DMA only for aligned, DMA-addressable, sufficiently large transfers outside panic writes, with PIO fallback.

## State and Persistence
Persistent flash state is handled by the generic OneNAND core. This driver maintains volatile completions, optional DMA channel ownership, GPMC timing configuration, OneNAND SYS_CFG1 sync/burst mode, and a shutdown-time BufferRAM zeroing workaround to keep OMAP boot ROM detection stable after soft reset.

## Dependencies and Integration Points
It depends on OF platform matching `"ti,omap2-onenand"`, OMAP GPMC timing helpers, GPIO descriptors, DMAengine memcpy support, `linux/mtd/onenand.h`, and MTD registration. The generic core consumes the callbacks installed by this glue.

## Risks
Wait behavior mixes GPIO interrupts and polling and includes retry logic for long operations; false GPIO values or missed interrupts can cause timeouts. DMA fallback must preserve partial trailing bytes and avoid panic-write DMA. The write path calls `dma_unmap_page()` after `dma_map_single()`, which is suspicious in this source and should be checked against the kernel version's DMA API expectations. Incorrect GPMC timing or latency selection can produce intermittent data/ECC failures.

## Test Signals
Probe logs should show chip select, physical/virtual base, and DMA/PIO mode. Hardware tests should cover read/write/OOB/erase under DMA and PIO fallback, IRQ and no-IRQ configurations, panic write fallback, optimized timing logs, suspend/removal cleanup, and shutdown BufferRAM clearing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_omap2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_samsung.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_samsung.c

## Purpose
`onenand_samsung.c` provides Samsung S3C6400/S3C6410/S5PC110 OneNAND controller support. For S3C64xx it emulates the generic OneNAND BufferRAM model using controller command windows and private buffers. For S5PC110 it mostly uses generic OneNAND operations but overrides BufferRAM reads with controller DMA support.

## Important APIs, Types, and Functions
`enum soc_type` selects TYPE_S3C6400, TYPE_S3C6410, or TYPE_S5PC110. `struct s3c_onenand` stores the platform device, MTD pointer, mapped controller/AHB/DMA bases, SoC type, pseudo BufferRAM buffers, mapping callbacks, DMA state, physical base, and completion. Major functions are `s3c_onenand_setup()`, `s3c_onenand_probe()`, `s3c_onenand_remove()`, `s3c_onenand_command()`, `s3c_onenand_wait()`, `s3c_onenand_readw()`, `s3c_onenand_writew()`, `s3c_unlock_all()`, `s3c_onenand_bbt_wait()`, `s5pc110_read_bufferram()`, `s5pc110_dma_poll()`, and `s5pc110_dma_irq()`.

## Control Flow
Probe allocates a combined MTD/chip object and global driver state, derives the SoC type from platform IDs, calls `s3c_onenand_setup()`, maps resources, sets `this->base`, skips unlock-status checks, and then diverges by SoC. S3C64xx maps an AHB command window and allocates pseudo page/OOB BufferRAMs; S5PC110 maps DMA registers and chooses polling or IRQ-driven DMA. It then calls `onenand_scan()`, adjusts S3C subpage settings, logs sync burst mode, and registers MTD partitions from platform data.

S3C command execution builds SoC-specific mapped command addresses from block/page/sector fields. Reads fill private main/OOB buffers, writes drain them to the controller, erase/unlock commands write controller command values, and generic BufferRAM callbacks copy between MTD buffers and those private buffers. Wait handling polls Samsung interrupt/error status bits, acknowledges them, checks ECC and lock/program/erase failures, and updates MTD ECC counters.

## State and Persistence
Persistent state is flash content, block lock state, and erase/program results. Volatile state includes the file-scope `onenand` pointer, pseudo BufferRAM contents, controller interrupt status, DMA configuration, completion state, and platform-data partition registration. Resume calls `unlock_all()`, which may change block protection state after power management transitions.

## Dependencies and Integration Points
The driver depends on Samsung-specific register definitions in `samsung.h`, platform device IDs (`s3c6400-onenand`, `s3c6410-onenand`, `s5pc110-onenand`), MTD OneNAND core callbacks, DMA mapping, IRQs, and optional platform partitions. It does not use OF matching in this file.

## Risks
The global `onenand` pointer makes the implementation effectively single-instance. S3C64xx emulation must match generic BufferRAM expectations exactly; any index mismatch corrupts read/write staging. DMA completion in `s5pc110_dma_irq()` ignores timeout/error return after waiting and always returns 0 from the DMA helper. PM resume unconditionally unlocks all blocks. Illegal generic register accesses are logged but still route to mapped commands in some cases.

## Test Signals
Test on each supported SoC ID path. Signals include successful MTD registration, manufacturer/device probing, sync burst log, read/write/OOB/erase behavior, ECC failure accounting, lock/unlock status checks, DMA polling versus IRQ mode on S5PC110, and suspend/resume ensuring expected lock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/samsung.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/samsung.h

## Purpose
`samsung.h` is the private register/bit definition header for the Samsung OneNAND controller driver. It gives `onenand_samsung.c` symbolic offsets for controller registers and interrupt/error bits.

## Important APIs, Types, and Functions
The file defines no functions or structs. Register offsets include memory configuration, burst length, reset, interrupt/error status/mask/acknowledge, ECC status, manufacturer/device IDs, buffer sizes, technology, address-width registers, transfer-spare control, interrupt pin enable, access clock, flash version ID, and an S3C64xx auxiliary control offset. It also defines reset command values and status bits such as `CACHE_OP_ERR`, `RST_CMP`, `RDY_ACT`, `INT_ACT`, `UNSUP_CMD`, `LOCKED_BLK`, `BLK_RW_CMP`, `ERS_CMP`, `PGM_CMP`, `LOAD_CMP`, `ERS_FAIL`, `PGM_FAIL`, `INT_TO`, `LD_FAIL_ECC_ERR`, and `TSRF`.

## Control Flow
There is no runtime control flow in the header. The constants drive control flow in `onenand_samsung.c`: reset waits for `RST_CMP`, wait paths look for `LOAD_CMP` / `PGM_CMP` / `ERS_CMP` / `BLK_RW_CMP`, ECC/error paths inspect `LD_FAIL_ECC_ERR`, lock failures use `LOCKED_BLK`, and OOB transfer toggles `TSRF`.

## State and Persistence
The header itself stores no state. Its offsets address volatile controller registers whose writes can trigger persistent flash operations such as erase, program, and lock/unlock when used by the driver.

## Dependencies and Integration Points
It is included only by the Samsung OneNAND platform driver. It depends on the controller hardware layout remaining consistent with S3C64xx/S5PC1xx expectations.

## Risks
Incorrect offsets or bit definitions would directly break probing, wait completion, ECC/error handling, and spare-area transfer. Because these macros are untyped and shared across SoC variants, variant-specific differences must be handled in the C driver rather than here.

## Test Signals
Compile coverage comes through `onenand_samsung.c`. Runtime signals are correct device ID reads, reset completion, accurate interrupt acknowledgement, ECC error reporting, and successful spare-area transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/samsung.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/qpic_common.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/qpic_common.c

## Purpose
`qpic_common.c` provides exported common DMA helpers for Qualcomm QPIC NAND controller drivers. It abstracts BAM and ADM DMA descriptor construction, submission, register/data transfer helpers, read-register buffer synchronization, and controller allocation/unallocation.

## Important APIs, Types, and Functions
Exported functions include `qcom_alloc_bam_transaction()`, `qcom_free_bam_transaction()`, `qcom_clear_bam_transaction()`, `qcom_qpic_bam_dma_done()`, `qcom_nandc_dev_to_mem()`, `qcom_prepare_bam_async_desc()`, `qcom_prep_bam_dma_desc_cmd()`, `qcom_prep_bam_dma_desc_data()`, `qcom_prep_adm_dma_desc()`, `qcom_read_reg_dma()`, `qcom_write_reg_dma()`, `qcom_read_data_dma()`, `qcom_write_data_dma()`, `qcom_submit_descs()`, `qcom_clear_read_regs()`, `qcom_nandc_alloc()`, and `qcom_nandc_unalloc()`. It relies on `struct qcom_nand_controller`, `struct bam_transaction`, `struct desc_info`, and QPIC constants from `linux/mtd/nand-qpic-common.h`.

## Control Flow
Allocation sets a 32-bit coherent DMA mask, allocates a small data buffer, register shadow structures, and a register-read buffer. BAM-capable controllers map the read buffer, request `tx`, `rx`, and `cmd` channels, and allocate an initial one-codeword BAM transaction; non-BAM controllers request a single `rxtx` ADM channel. Per-operation helpers append command or data scatterlist entries. BAM command descriptors collect command elements, split SGLs at `NAND_BAM_NEXT_SGL`, and may immediately prepare fenced command descriptors on `NAND_BAM_NWD`. ADM descriptors configure slave source/destination, maxburst, optional CRCI flow control, map one SGL, and enqueue it. `qcom_submit_descs()` finalizes any pending BAM SGLs, submits all descriptors, waits for BAM completion via the last command descriptor callback or ADM completion via `dma_sync_wait()`, then unmaps and frees all descriptors.

## State and Persistence
No flash state is directly persisted here; this layer schedules DMA that other QPIC code uses to issue flash commands. Volatile state includes BAM position counters, command/data SGL arrays, descriptor lists, DMA mappings, channel handles, register read cursor, and the completion used to signal BAM transaction completion.

## Dependencies and Integration Points
The file depends on DMAengine, Qualcomm ADM/BAM DMA APIs, platform DMA channel names, QPIC register-address helpers/macros, and MTD QPIC controller code that prepares NAND operations. It exports symbols for raw NAND and SPI-NAND QPIC drivers.

## Risks
Descriptor array bounds are checked, but flag sequencing is subtle; missing `NAND_BAM_NEXT_SGL`, `NAND_BAM_NWD`, or interrupt flags can leave no completion callback or wrong fences. `qcom_submit_descs()` assumes BAM `last_cmd_desc` exists before assigning the callback. DMA mappings must be unmapped on all error paths; the common cleanup loop handles queued descriptors but callers must clear transaction positions between operations. Allocation cleanup for BAM frees channels/mappings but `qcom_nandc_unalloc()` does not free `bam_txn`, so callers must pair it with `qcom_free_bam_transaction()`.

## Test Signals
Test with both BAM and ADM controller variants. Useful signals are DMA channel probe success/failure, descriptor queue lengths, timeout returns from `qcom_submit_descs()`, correct read ID/status flow-control reads, clean unmap/free under injected descriptor preparation failures, and successful page read/write paths in the consuming QPIC NAND drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/qpic_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Kconfig

## Purpose
`raw/Kconfig` declares the raw/parallel NAND subsystem menu and controller feature options. It gates which raw NAND controller drivers can be built, selects shared ECC/core dependencies, and documents platform dependencies.

## Important APIs, Types, and Functions
This is Kconfig metadata, not C code. The top-level `menuconfig MTD_RAW_NAND` is a tristate that selects `MTD_NAND_CORE` and `MTD_NAND_ECC`. Individual symbols include many controller options such as `MTD_NAND_AMS_DELTA`, `MTD_NAND_OMAP2`, `MTD_NAND_QCOM`, `MTD_NAND_ARASAN`, `MTD_NAND_ATMEL`, `MTD_NAND_GPIO`, and simulation/misc options such as `MTD_NAND_NANDSIM`, `MTD_NAND_RICOH`, and `MTD_NAND_DISKONCHIP`. It also sources subdirectory Kconfigs for some controller families.

## Control Flow
Kconfig evaluation starts at `MTD_RAW_NAND`; when disabled, the contained controller symbols are not offered. Dependencies constrain visibility and buildability by architecture, OF, DMA, clocks, I/O memory, bus helpers, and ECC helper libraries. Some options select helper symbols such as `BCH`, `GENERIC_ALLOCATOR`, `MFD_ATMEL_SMC`, `REED_SOLOMON`, or controller-family core symbols. The `MTD_NAND_OMAP_BCH_BUILD` def_tristate bridges OMAP controller and optional BCH support.

## State and Persistence
The file has no runtime state. Its persistent effect is the generated kernel configuration, which determines object inclusion and compiled code paths.

## Dependencies and Integration Points
It integrates with `drivers/mtd/nand/raw/Makefile`, subdirectory Kconfig files, architecture symbols, MTD core symbols, and helper library symbols. Driver source files rely on the matching config symbols for compilation.

## Risks
Incorrect dependencies can expose drivers on platforms that cannot link or hide valid compile-test coverage. Missing `select` entries can produce link failures for helper APIs; over-broad selects can force unwanted libraries. Because this menu covers many SoCs, changes can have broad build-matrix impact.

## Test Signals
Run `olddefconfig`/`allmodconfig`/`allyesconfig` and targeted randconfig builds across representative architectures. Confirm that `CONFIG_MTD_NAND_ARASAN` pulls BCH, `CONFIG_MTD_NAND_ATMEL` descends into the atmel Makefile, and each visible symbol produces the object listed in `raw/Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Makefile

## Purpose
`raw/Makefile` maps raw NAND Kconfig symbols to the object files and subdirectories built by Kbuild. It also defines the composite `nand.o` core from raw NAND base, legacy, BBT, timing, ID, ONFI/JEDEC, and vendor-specific ID support.

## Important APIs, Types, and Functions
This is build metadata. Important entries include `obj-$(CONFIG_MTD_RAW_NAND) += nand.o`, controller object mappings such as `obj-$(CONFIG_MTD_NAND_AMS_DELTA) += ams-delta.o`, `obj-$(CONFIG_MTD_NAND_QCOM) += qcom_nandc.o`, `obj-$(CONFIG_MTD_NAND_ARASAN) += arasan-nand-controller.o`, and subdirectory descents such as `atmel/`, `ingenic/`, `gpmi-nand/`, `brcmnand/`, and `bcm47xxnflash/`. `omap2_nand-objs := omap2.o` aliases the OMAP object into a module name.

## Control Flow
Kbuild evaluates each `obj-*` line after configuration. Enabled symbols add object files or directories to the build. The final `nand-objs` list composes the raw NAND core module from multiple implementation files and vendor helpers.

## State and Persistence
No runtime state exists. Persistent effects are generated build artifacts and module composition.

## Dependencies and Integration Points
The file must stay synchronized with `raw/Kconfig` symbols and actual source filenames. Composite object names affect module names and symbol linkage. Subdirectory entries depend on child Makefiles.

## Risks
Stale object mappings cause enabled Kconfig options to build nothing or fail. Composite `nand-objs` omissions can remove required core/vendor support. Always-built `obj-y += ingenic/` means that subdirectory Makefile must internally gate objects by config.

## Test Signals
Build with `CONFIG_MTD_RAW_NAND=m` and selected controller symbols as both built-in and module where applicable. Verify expected `.o`/`.ko` outputs and that each source added by Kconfig has a corresponding Makefile entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ams-delta.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ams-delta.c

## Purpose
`ams-delta.c` is a GPIO-driven raw NAND controller driver for the Amstrad E3/Delta platform. It implements the modern raw NAND `exec_op` interface by bit-banging command, address, data, read-enable, write-enable, chip-enable, ready, and write-protect GPIOs.

## Important APIs, Types, and Functions
`struct gpio_nand` embeds `struct nand_controller` and `struct nand_chip`, GPIO descriptors for control lines, an optional data GPIO array, data direction state, timing fields `tRP`/`tWP`, and byte I/O callbacks. Key functions are `gpio_nand_probe()`, `gpio_nand_remove()`, `gpio_nand_exec_op()`, `gpio_nand_setup_interface()`, `gpio_nand_attach_chip()`, `gpio_nand_io_read()`, `gpio_nand_io_write()`, `gpio_nand_dir_input()`, `gpio_nand_dir_output()`, `gpio_nand_read_buf()`, and `gpio_nand_write_buf()`.

## Control Flow
Probe allocates the private structure, wires MTD parent/OF node, obtains optional RDY/NWP/NCE/NRE/NWE GPIOs and required ALE/CLE GPIOs, optionally obtains the data GPIO array, installs byte I/O callbacks, runs any platform/OF match-data probe hook, initializes the embedded controller with `gpio_nand_ops`, releases write protection, defaults ECC engine type to software, calls `nand_scan()`, and registers partitions. `gpio_nand_exec_op()` asserts chip select, walks NAND operation instructions, toggles CLE/ALE around command/address writes, performs data reads/writes through GPIO bytes, waits ready via RDY GPIO or soft wait, then deasserts chip select.

## State and Persistence
Runtime state is GPIO direction (`data_in`), timing pulse widths derived from NAND SDR timings, and write-protect/chip-enable line levels. Persistent flash state comes from NAND commands issued through `exec_op`. Remove reapplies write protection before unregistering and cleaning up NAND state.

## Dependencies and Integration Points
It depends on gpiolib, `linux/mtd/rawnand.h`, `linux/mtd/nand-gpio.h`, platform data (`struct gpio_nand_platdata`) or DT GPIO descriptors, and MTD partition registration. Kconfig builds it under `CONFIG_MTD_NAND_AMS_DELTA`.

## Risks
The driver is timing-sensitive and slow because it bit-bangs every byte. Optional GPIOs allow multiple hardware descriptions, but missing required ALE/CLE or incomplete I/O callbacks abort probe. The FIXME notes write protection is released before `nand_scan()` due to missing core WP control. Direction changes and raw GPIO array ordering must match board wiring exactly.

## Test Signals
Probe should succeed with complete GPIO descriptors and fail clearly with incomplete configuration. Tests should exercise command/address/data instruction sequences, RDY GPIO and soft-wait paths, setup-interface timing updates, software Hamming ECC defaulting, write-protect assertion on remove, and partition registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ams-delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/arasan-nand-controller.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/arasan-nand-controller.c

## Purpose
`arasan-nand-controller.c` is a raw NAND controller driver for Arasan NFC v3p10 and Xilinx ZynqMP. It implements `exec_op`, timing setup for SDR/NV-DDR, multi-chip-select handling including GPIO CS, DMA page transfers, and optional on-host hardware BCH ECC with software BCH correction workaround.

## Important APIs, Types, and Functions
Core types are `struct arasan_nfc` for controller-wide state, `struct anand` for per-chip state, and `struct anfc_op` for parsed hardware operations. Important functions include `anfc_probe()`, `anfc_remove()`, `anfc_chips_init()`, `anfc_chip_init()`, `anfc_parse_cs()`, `anfc_select_target()`, `anfc_exec_op()`, `anfc_check_op()`, `anfc_parse_instructions()`, `anfc_rw_pio_op()`, the operation-type executors, `anfc_setup_interface()`, `anfc_attach_chip()`, `anfc_detach_chip()`, `anfc_init_hw_ecc_controller()`, `anfc_read_page_hw_ecc()`, and `anfc_write_page_hw_ecc()`.

## Control Flow
Probe allocates controller state, initializes the NAND controller ops, maps registers, resets interrupt state, enables controller and bus clocks, sets a 64-bit DMA mask, parses chip-select wiring, then scans/registers each child NAND node. Per-chip init reads `reg` chip-select indexes and `nand-rb`, sets NAND options (`NAND_BUSWIDTH_AUTO`, `NAND_NO_SUBPAGE_WRITE`, `NAND_USES_DMA`), requires an MTD name/label, calls `nand_scan()`, and registers MTD.

`exec_op` first validates address cycles, transfer length, packet divisibility, and unsupported command+data patterns, then selects the target, writes timing/interface registers, adjusts bus clock if needed, parses NAND instructions into register fields, triggers the operation, waits ready/event bits, and performs PIO data transfers through `DATA_PORT_REG`. Hardware ECC read/write use DMA over full page plus optional OOB. Reads fetch OOB separately, extract hardware syndromes, run software BCH decode because the hardware BCH reporting is unreliable, correct data bits, and update ECC stats. Writes program data with hardware ECC enabled and then checks NAND status.

## State and Persistence
Persistent flash state comes from program/erase commands. Volatile state includes current CS, native/spare CS selection, bus clock rate, per-chip timing/interface registers, ECC configuration, BCH context, error-location buffers, hardware syndrome buffer, and registered MTD devices. GPIO CS descriptors are manually released on remove.

## Dependencies and Integration Points
The driver depends on OF child nodes, clocks named `controller` and `bus`, MMIO registers, DMA mapping, GPIO CS parsing via `rawnand_dt_parse_gpio_cs()`, raw NAND operation parser, BCH library, and MTD registration. It is selected by `CONFIG_MTD_NAND_ARASAN` and matches `"xlnx,zynqmp-nand-controller"` or `"arasan,nfc-v3p10"`.

## Risks
Operation support is constrained: no data-only operations, max five address cycles, max 1 MiB chunks, and packet lengths must divide into supported steps. The controller may read/write rounded-up data cycles, relying on core behavior for harmless extra bytes. Hardware BCH has a known uncorrectable-reporting bug, so the software BCH workaround is critical. Clock changes during target selection can fail and leave the bus clock disabled if re-enable fails. CS parsing rejects ambiguous native/GPIO mixes.

## Test Signals
Run DT probe tests with native CS and GPIO CS layouts, multiple child chips, SDR modes, NV-DDR modes, and the ZynqMP high-speed SDR clock workaround. NAND tests should cover read ID/status, parameter page, page read/write, OOB, erase, raw page I/O, hardware ECC corrected/uncorrectable paths, DMA mapping failures, packet length rejection, and cleanup after partial chip registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/arasan-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/Makefile

## Purpose
`raw/atmel/Makefile` maps `CONFIG_MTD_NAND_ATMEL` to the Atmel NAND controller and PMECC objects.

## Important APIs, Types, and Functions
This is Kbuild metadata. It adds `atmel-nand-controller.o` and `atmel-pmecc.o` when `CONFIG_MTD_NAND_ATMEL` is enabled. Composite definitions map `atmel-nand-controller-objs` to `nand-controller.o` and `atmel-pmecc-objs` to `pmecc.o`.

## Control Flow
When the parent raw NAND Makefile descends into `atmel/`, Kbuild evaluates this file. If the config is enabled, it builds two composite objects from the local source files.

## State and Persistence
There is no runtime state. The persistent effect is object/module composition in the build directory.

## Dependencies and Integration Points
It depends on the parent `raw/Makefile` entry `obj-$(CONFIG_MTD_NAND_ATMEL) += atmel/` and the Kconfig symbol that selects necessary Atmel SMC/generic allocator dependencies.

## Risks
If object names drift from source filenames, the Atmel driver will fail to build. Because both controller and PMECC are tied to the same config symbol, changes to split functionality would require Kconfig and Makefile updates together.

## Test Signals
Enable `CONFIG_MTD_NAND_ATMEL` as built-in and module and verify both composite objects are produced and linked without missing PMECC/controller symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/Makefile -->
