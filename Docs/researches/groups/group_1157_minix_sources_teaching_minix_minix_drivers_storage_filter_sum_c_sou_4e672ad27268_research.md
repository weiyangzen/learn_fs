# Group Research: group_1157_minix_sources_teaching_minix_minix_drivers_storage_filter_sum_c_sou_4e672ad27268

Scope: learn_fs subset A, source tree `sources/teaching/minix`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/sum.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/sum.c

## Purpose

Implements the filter driver's checksum-aware logical-to-physical transfer layer. It maps user-visible logical sectors into a physical layout where groups of data sectors are followed by checksum sectors, computes or verifies checksums, and optionally verifies writes by reading data back from the underlying disk drivers.

## Main Entry Points

- `sum_init()`: allocates static backing buffers for expanded I/O and write-readback checks.
- `transfer()`: central read/write path; expands logical data into checksum layout for writes, collapses checksum layout for reads, and delegates actual I/O to `read_write()`.
- `convert()`: converts raw disk size to user-visible size by subtracting checksum sectors.
- `calc_sum()`: computes the configured checksum type: nil, XOR, CRC32, or MD5.
- `make_sum()` / `check_sum()`: generate or validate checksum sectors across expanded transfer buffers.
- `check_write()`: reads written data back from the main and optional mirror disk, then compares it to the expanded write buffer.
- `expand()` / `collapse()`: convert between contiguous logical data and interspersed checksum layout.

## Control Flow And State

The layout macros define groups of `NR_SUM_SEC` logical data sectors followed by one checksum sector. `transfer()` short-circuits directly to `read_write()` if checksum layout is disabled. Otherwise it computes the physical start offset, expands the request into `ext_buffer`, and performs one lower-level I/O over the physical span.

For writes, the code copies user data into the expanded layout, reads partial checksum/data tails where needed, updates checksums, writes the expanded data, optionally read-verifies, and returns the logical byte count through `collapse_size()`. For reads, it reads expanded data, verifies checksum sectors, and copies only logical sectors back to the caller.

`make_sum()` handles partial group writes carefully: it reads existing checksum sectors and any gap data so unrelated sectors in the same checksum group are preserved. `check_sum()` walks the expanded buffer group by group and returns `RET_REDO` through `bad_driver()` behavior on checksum failure.

## Dependencies

Depends on filter globals and policy macros from `inc.h`, checksum implementations from `crc.h` and `md5.h`, `flt_malloc()`/`flt_free()`, `read_write()`, and lower-driver failure handling through `bad_driver()`.

## Risks

Correctness depends on sector-aligned requests and exact agreement between `LOG2PHYS()`, `SEC2SUM_NR()`, `expand_sizes()`, and `collapse_size()`. Partial writes are the highest-risk path because they preserve existing checksum sectors and gap data. `check_write()` has early returns after compare failures without freeing readback buffers, which is safe only if the process is expected to continue with bounded static buffers or abort/retry soon after. The checksum code also stores sector numbers through `unsigned long *`, so checksum byte layout is architecture-sensitive.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/sum.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/util.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/filter/util.c

## Purpose

Provides small utility helpers for the filter driver: conditional contiguous-memory allocation and a single outstanding alarm abstraction.

## Main Entry Points

- `flt_malloc()`: returns a supplied static buffer when large enough; otherwise allocates contiguous memory with `alloc_contig()`.
- `flt_free()`: frees only dynamically allocated buffers, leaving static backing buffers untouched.
- `flt_alarm()`: sets, clears, or queries the filter driver's single alarm deadline.

## Control Flow And State

`flt_malloc()` is optimized for common small transfers by reusing caller-provided static buffers. Larger requests are contiguous allocations and panic on failure. `flt_alarm()` maintains `next_alarm`; negative `dt` queries the current alarm, zero clears an existing one, and positive values set a new alarm using `sys_setalarm()` and `getticks()`.

## Dependencies

Uses MINIX contiguous allocation/free routines, `sys_setalarm()`, `getticks()`, and shared declarations from `inc.h`.

## Risks

The alarm helper intentionally supports only one active alarm and panics on clearing an unset alarm or overwriting an existing one. Callers must pair `flt_malloc()` and `flt_free()` with the same size/static-buffer arguments or risk freeing static memory incorrectly.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/filter/util.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/floppy/Makefile

## Purpose

Builds the MINIX floppy disk service.

## Build Role

Defines `PROG=floppy` with sources `floppy.c` and `liveupdate.c`. Links against `libblockdriver`, `libsys`, and `libtimers`, then includes `minix.service.mk` to build/install it as a MINIX service.

## Dependencies

The service depends on block driver support, low-level system calls, and MINIX timer helpers.

## Risks

The Makefile is simple; build correctness mostly depends on keeping `liveupdate.c` linked with `floppy.c` because the main driver declares live update callbacks externally.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/floppy.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/floppy/floppy.c

## Purpose

Implements the user-space MINIX floppy disk controller driver for PC NEC PD765-compatible FDC hardware, including disk density probing, DMA setup, sector I/O, formatting support, partition handling, motor timers, interrupts, retries, resets, and SEF startup.

## Main Entry Points

- `main()`: starts SEF and enters `blockdriver_task()`.
- `sef_cb_init_fresh()`: allocates the DMA buffer, initializes per-drive state/timers, registers the floppy IRQ, and announces the block driver.
- `f_transfer()`: central block transfer path for reads, writes, and format devices.
- `f_do_open()` / `f_do_close()`: open/close handling and automatic density detection.
- `f_prepare()` / `f_part()` / `f_geometry()`: minor-device selection, partition lookup, and geometry reporting.
- `dma_setup()`: programs the ISA DMA controller for a one-sector transfer.
- `start_motor()` / `stop_motor()`: manage drive motor state and delayed spin-down.
- `seek()`, `recalibrate()`, `f_reset()`: position and recover the FDC.
- `fdc_transfer()`, `fdc_command()`, `fdc_out()`, `fdc_results()`, `f_intr_wait()`: low-level command, interrupt, and status handling.
- `test_read()`: probes media/drive density combinations.

## Control Flow And State

The driver keeps one `struct floppy` per drive with current cylinder, target CHS, density, class mask, geometry, partitions, and motor timer. Global state tracks the selected drive/device, density parameters, controller reset need, current motor bitmap, busy state, and FDC result bytes.

`f_transfer()` validates sector alignment and EOF, truncates to device size, maps iovecs to track sectors, starts the motor, configures FDC timing/rate, seeks, and transfers one sector at a time through the DMA buffer. On errors it retries up to `MAX_ERRORS`, recalibrating halfway, and stops immediately for nonretryable errors such as write protection. Formatting uses a special minor bit and consumes `struct disk_parameter_s` from the request.

Open on typed devices selects density directly. Open on `/dev/fdN` probes density through `test_order`, reading a diagnostic sector and then parsing partitions on success. Cleanup schedules a motor-off timer after each request.

Interrupt waits use `driver_receive()` and local timer expiration to distinguish real hardware interrupt from timeout. FDC status reads reenable IRQs after consuming result bytes. Reset strobes DOR, flushes sense results for all four possible drives, and marks all configured drives uncalibrated.

## Dependencies

Depends on MINIX blockdriver/drvlib/syslib/sysutil APIs, timers, safe copy grants, PC port I/O, IRQ policy calls, ISA DMA registers, `machine/diskparm.h`, and live update callbacks supplied by `liveupdate.c`.

## Risks

This is hardware-state-heavy code. Risks include ISA DMA address restrictions below 16 MB, timing-sensitive motor/seek/FDC operations, controller reset sequencing, lost or spurious interrupts, density misdetection, and retry behavior that mutates iovecs in place. The format-device path trusts controller validation for most formatting parameters after only checking sector count. Live update and termination must avoid stopping while `f_busy` indicates active I/O.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/floppy.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/floppy.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/floppy/floppy.h

## Purpose

Provides the shared include wrapper for floppy driver source files.

## API Surface

Includes `minix/drivers.h`, `minix/blockdriver.h`, and `minix/drvlib.h`, making the block driver and MINIX driver APIs available to `floppy.c` and `liveupdate.c`.

## Dependencies

Depends only on MINIX driver headers.

## Risks

No logic is present. Its importance is keeping the live update file and main driver on the same driver API declarations.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/floppy.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/liveupdate.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/floppy/liveupdate.c

## Purpose

Implements floppy-driver SEF live update readiness and state diagnostics.

## Main Entry Points

- `sef_cb_lu_prepare()`: reports whether the driver can enter the requested live update state.
- `sef_cb_lu_state_isvalid()`: accepts standard SEF live update states and the custom motor-off state.
- `sef_cb_lu_state_dump()`: prints driver state and readiness diagnostics.

## Control Flow And State

The file imports `f_busy`, `motor_status`, `f_drive`, and `last_was_write` from `floppy.c`. Standard request/protocol-free states require no pending request. The custom `FL_STATE_MOTOR_OFF` also requires the selected drive motor to be stopped. Dump output reports each condition for operational diagnostics.

## Dependencies

Depends on SEF live update macros, `floppy.h`, and global state exported by `floppy.c`.

## Risks

The readiness logic only checks the current selected drive for motor state. If multiple drive motors could be on, this custom state may not represent all physical activity. The read/write-pending helper macros are defined but not used in readiness checks.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/floppy/liveupdate.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/memory/Makefile

## Purpose

Builds the MINIX memory driver and embeds the boot image ramdisk object.

## Build Role

Defines `PROG=memory` with `memory.c` and generated `imgrd.mfs` as sources. Converts the ramdisk image into an object with `objcopy -Ibinary`, disables bitcode, links against `libblockdriver` and `libchardriver`, and includes `minix.service.mk`.

## Control Flow

If `../ramdisk/image` does not exist, `touch-genfiles` creates a deterministic empty placeholder. `imgrd.mfs` symlinks to the ramdisk image. The commented-out recursive make rules indicate this tree avoids invoking parallel sub-makes.

## Dependencies

Depends on the ramdisk image path, host linker/objcopy support for binary objects, and generated symbols consumed by `local.h`.

## Risks

If the ramdisk image is missing, the build can proceed with a placeholder, which is useful for dependency generation but can hide an empty boot image if not regenerated in the intended build flow.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/local.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/memory/local.h

## Purpose

Declares linker-provided symbols for the embedded image ramdisk and defines convenient macros for its address and size.

## API Surface

- `_binary_imgrd_mfs_start`, `_binary_imgrd_mfs_end`: symbols emitted by `objcopy`.
- `imgrd`: pointer to the embedded ramdisk bytes.
- `imgrd_size`: byte size computed from the linker symbol difference.

## Dependencies

Depends on the memory driver Makefile producing `imgrd.mfs.o` with predictable binary-object symbol names.

## Risks

The size computation casts symbol addresses to `size_t`; it assumes the binary object symbols are in the same address space and ordered as expected.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/local.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/memory.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/memory/memory.c

## Purpose

Implements the MINIX memory driver for both character and block devices: `/dev/mem`, `/dev/kmem`, `/dev/null`, `/dev/zero`, `/dev/ram*`, `/dev/boot`, and `/dev/imgrd`.

## Main Entry Points

- `main()`: dispatches incoming messages to either blockdriver or chardriver processing.
- `sef_cb_init_fresh()`: initializes device geometry, embedded image ramdisk mapping, open counts, and `/dev/mem`.
- `m_char_read()` / `m_char_write()`: implement character devices.
- `m_block_transfer()`: implements RAM-disk-style block transfers.
- `m_block_ioctl()`: handles `MIOCRAMSIZE` to allocate or resize RAM disks.
- `m_transfer_mem()`: maps physical memory a page at a time for `/dev/mem`.
- `m_transfer_kmem()`: copies from mapped kernel-memory-style virtual regions.
- `m_block_open()` / `m_block_close()` and `m_char_open()` / `m_char_close()`: validate minors and maintain open counts.

## Control Flow And State

`m_geom[]` stores base/size for each minor and `m_vaddrs[]` stores the mapped or allocated virtual address. Character minors are separated from block minors by `m_is_block()`. `/dev/null` returns EOF on read and discards writes; `/dev/zero` uses `sys_safememset()` on reads and discards writes. `/dev/mem` maps physical pages lazily with `vm_map_phys()` and reuses a one-page window until the page changes.

Block transfers copy between caller grants and device memory, respecting EOF and device size. `MIOCRAMSIZE` only applies to RAM disk minors, the old RAM device, and `IMGRD_DEV`; it refuses resizing while open count is not exactly one, unmaps existing memory, and allocates new anonymous preallocated memory with `mmap()`.

## Dependencies

Depends on MINIX blockdriver/chardriver APIs, safe copy grants, VM physical mapping, memory ioctls, kernel constants/types for device minor definitions, and embedded ramdisk symbols from `local.h`.

## Risks

The `/dev/mem` path exposes raw physical memory and enables I/O privilege on i386 opens. `m_transfer_mem()` appears to compute each page window from `position` updated inside the loop, which is correct only because it increments position per subcount. The block transfer panics on safe-copy failure rather than returning an error. RAM disk resizing depends on open count discipline and careful unmapping of page-aligned portions.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/memory/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/Makefile

## Purpose

Builds the MINIX MMC/SD block driver variants.

## Build Role

Defines two programs: `mmc` and `emmc`. `mmc` builds from `mmcblk.c`, `mmchost_dummy.c`, `mmchost_mmchs.c`, and register headers. `emmc` builds from `emmc.c` and `mmcblk.c`. Both link against `libblockdriver` and `libsys`, set `_SYSTEM=1`, and include `minix.service.mk`.

## Dependencies

Depends on MINIX system-driver privileges, the generic MMC block layer, host-controller implementations, and SD/MMC register headers.

## Risks

The `emmc` target reuses `mmcblk.c` while providing host initialization from `emmc.c`; duplicate host initializer stubs in `emmc.c` are intentional but easy to confuse with the regular `mmc` host selection path.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/emmc.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/emmc.c

## Purpose

Provides a dedicated AM335x/BeagleBone Black eMMC host implementation for the generic MINIX MMC block driver. It initializes MMC1, identifies and configures an eMMC card, and performs single-block read/write I/O through MMCHS registers.

## Main Entry Points

- `host_initialize_host_structure_mmchs()`: registers the eMMC host callbacks used by `mmcblk.c`.
- `emmc_host_init()`: validates BBB hardware, maps AM335x MMC1 registers, configures voltage, clocks, timeouts, interrupts, and MMCHS block length.
- `emmc_card_initialize()`: performs the eMMC initialization sequence and fills `slot->card`.
- `emmc_read()` / `emmc_write()`: read/write logical blocks through single-block commands.
- `send_cmd()` / `send_cmd_check_r1()`: low-level command submission and response validation.
- `read_data()` / `write_data()` / `read_busy()`: interrupt-driven data/busy transfer helpers.
- `cim_read_block()` / `cim_write_block()`: command-plus-data single-block operations.

## Control Flow And State

The host maps AM335x MMC1 registers, mutates the `regs_v1` offset table into virtual addresses, registers IRQ 28, and configures pins GPMC_AD4-7 for 8-bit mode when possible. Initialization resets MMCHS, powers the bus, starts at 400 kHz, enables clocks, sets auto-idle, programs 512-byte blocks, and enables command/data interrupts.

Card initialization sends CMD0, switches command line open-drain, repeats CMD1 until OCR ready, reads CID/CSD, assigns RCA 2, switches push-pull, selects the card, reads EXT_CSD, derives capacity from CSD or EXT_CSD sector count, switches high-speed mode, changes clock to 24 or 48 MHz, sets 4- or 8-bit bus width, and sets 512-byte block length. The card is then exposed as one disk with partition arrays cleared.

Data I/O loops one 512-byte block at a time. For cards at or below 2 GiB, addresses are byte addresses; above that they are sector addresses. Writes are denied if CSD write-protect bits were set.

## Dependencies

Depends on AM335x MMCHS register definitions in `omap_mmc.h`, SD/MMC command/register macros in `sdmmcreg.h`, board detection, MMIO helpers, IRQ/alarm APIs, blockdriver message queueing, and the generic `mmchost.h` contract.

## Risks

The file mutates the global `regs_v1` register-offset structure into virtual addresses, so reinitialization would add the base twice unless the process starts fresh. It supports only instance 0 and BBB MMC1. Interrupt waits queue unrelated messages while waiting for hardware; wrong alarm/IRQ handling can stall the driver. The implementation uses single-block PIO, so performance is limited. Capacity/addressing and EXT_CSD byte-order assumptions are critical.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/emmc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmcblk.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmcblk.c

## Purpose

Implements the generic MINIX blockdriver layer for MMC/SD cards, abstracting host-controller operations behind `struct mmc_host`.

## Main Entry Points

- `main()`: parses environment arguments, initializes SEF, and enters `blockdriver_task()`.
- `apply_env()`: selects the host driver (`mmchs` by default on ARM or `dummy`) and applies `log_level` and `instance`.
- `block_open()` / `block_close()`: detect/initialize cards, parse partitions, maintain open count, and release cards.
- `block_transfer()`: validates block-aligned iovecs and performs block-by-block read/write through host callbacks.
- `block_ioctl()`: supports `DIOCOPENCT` and `DIOCFLUSH`.
- `block_part()`: maps MINIX disk/partition/subpartition minor numbers to `struct device`.
- `get_slot()`: maps supported minors to the single supported slot.
- `hw_intr()`: forwards leftover interrupts to the host.

## Control Flow And State

The driver keeps one global `struct mmc_host host`. It supports a single card/slot exposed as disk 0 plus primary and MINIX subpartitions. On first open, it detects a card, initializes it if not already in data transfer mode, parses partitions with `partition()`, and increments `open_ct`. Subsequent opens increment `open_ct` without reinitialization. Last close calls `card_release()`.

Transfers require position and every iovec size to be multiples of the card block size, and require the block size to fit the 4 KiB `copybuff`. The code copies one block at a time between caller grants and `copybuff`, then calls `host->read()` or `host->write()` for one block. EOF truncation happens at the selected partition size.

## Dependencies

Depends on `mmchost.h`, MINIX blockdriver/drvlib/log/env APIs, safe-copy grants, partition parsing, and host implementations that fill all required callback pointers.

## Risks

The return values from `host->read()` and `host->write()` inside `block_transfer()` are ignored, so media errors may be reported as successful transfers. The driver mutates neither iovec sizes nor offsets but uses fixed `i * blk_size` offsets per iovec, so each iovec is independently handled. It only supports the first disk/slot despite structures allowing more. Signal termination refuses SIGTERM while open count is nonzero.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmcblk.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost.h

## Purpose

Defines the host/card abstraction contract between `mmcblk.c` and MMC/SD host-controller implementations.

## API Surface

- Constants define partition counts, slot count, and simple card states.
- `struct sd_card_regs`: stores CID, RCA, DSR, CSD, SCR, OCR, SSR, and CSR.
- `struct mmc_command`: generic command descriptor with command, argument, response type, data direction, response buffer, and data buffer.
- `struct sd_card`: holds slot pointer, card registers, block size/count, state, open count, and MINIX partition/subpartition devices.
- `struct sd_slot`: links a host to one card.
- `struct mmc_host`: callback table for instance selection, init, log level, reset, card detection/init/release, interrupt handling, and block read/write.
- Declares `host_initialize_host_structure_mmchs()` and `host_initialize_host_structure_dummy()`.

## Dependencies

Depends on MINIX `struct device` from included driver headers through users of this header and on SD/MMC register definitions for command semantics.

## Risks

The header is the central ABI between the generic driver and hosts. Callback pointers must be fully initialized before `mmcblk.c` starts. Misspellings such as `PARTITONS_PER_DISK` are harmless internally but make the contract easy to misuse. Card states are minimal and do not model removal/error states.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_dummy.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_dummy.c

## Purpose

Implements an in-memory dummy MMC host for testing the generic MMC block layer without real hardware.

## Main Entry Points

- `host_initialize_host_structure_dummy()`: fills the host callback table and initializes slot/card state.
- `dummy_card_initialize()`: sets block size/count, data-transfer state, and full-disk geometry.
- `dummy_host_read()` / `dummy_host_write()`: memcpy data between the caller buffer and the allocated in-memory backing store.
- `dummy_card_release()`: decrements open count and marks the card uninitialized.
- `dummy_host_set_instance()`: accepts only instance 0.

## Control Flow And State

A global `dummy_data` buffer is allocated lazily to `DUMMY_BLOCK_SIZE * DUMMY_SIZE_IN_BLOCKS`. The dummy card exposes one whole-disk partition covering the full buffer. Read and write callbacks use block number and count to compute byte offsets.

## Dependencies

Depends on `mmchost.h`, `sdmmcreg.h`, MINIX logging, and libc allocation/memory routines.

## Risks

No bounds checking exists in dummy read/write callbacks. If the generic block layer passes an out-of-range block, the dummy host will memcpy outside the backing buffer. `init_dummy_sdcard()` allocates backing memory, but `dummy_card_initialize()` does not call it; initialization currently happens during host structure setup.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_mmchs.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_mmchs.c

## Purpose

Implements a general OMAP MMCHS SD-card host driver for BeagleBoard-family hardware, backing the generic MMC block driver.

## Main Entry Points

- `host_initialize_host_structure_mmchs()`: selects board-specific MMCHS instance and fills host callbacks.
- `mmchs_init()`: maps MMCHS registers, resets/configures the controller, powers the bus, sets clocks, sends the initialization stream, and registers IRQs.
- `mmc_send_cmd()` / `mmchs_send_cmd()`: translate generic `mmc_command` descriptors into MMCHS register commands.
- `intr_wait()`, `handle_bwr()`, `handle_brr()`: wait for command/data interrupts and move PIO data through the DATA register.
- `mmchs_card_initialize()`: performs SD card identification and configuration.
- `mmchs_host_read()` / `mmchs_host_write()`: perform single-block reads/writes.
- `card_goto_idle_state()`, `card_identification()`, `card_query_voltage_and_type()`, `card_identify()`, `card_csd()`, `select_card()`, `card_scr()`: SD initialization command steps.
- `enable_4bit_mode()` / `enable_high_speed_mode()`: configure bus width and clock.

## Control Flow And State

Board selection picks either BeagleBone or BeagleBoard-xM register base/IRQ and register layout. `mmchs_init()` grants memory access, maps registers, soft-resets, advertises capabilities, configures power/idle/wakeup, starts at 400 kHz, enables interrupts, sends an init stream, sets data timeout, and enables interrupt signaling.

Command submission writes ARG/CMD, waits for command completion, handles optional data transfers through global `io_data`/`io_len`, and copies responses from MMCHS response registers. SD initialization sends CMD0, CMD8, ACMD41 loops, CMD2, CMD3, CMD9, CMD7, ACMD51, ACMD6, and speed selection based on CSD. The card is exposed as a 512-byte-block disk with size from CSD v2 capacity.

## Dependencies

Depends on `mmchost.h`, `sdmmcreg.h`, `sdhcreg.h`, `omap_mmc.h`, MINIX MMIO, board detection, VM physical mapping, IRQ/alarm APIs, and blockdriver message queueing.

## Risks

The code uses globals for current controller and current data buffer, so concurrent requests would need external serialization. `intr_wait()` queues unrelated messages while waiting but has complex reenable/timeout paths. Several host read/write helpers ignore command failure return values and return `OK`. Only SDHC-like CSD version 2.0 cards are accepted. Card detection is a stub that always reports present.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_mmchs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/omap_mmc.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/omap_mmc.h

## Purpose

Defines OMAP MMCHS controller structures, register-offset tables, and bit masks used by the MINIX MMC host drivers.

## API Surface

- `struct omap_mmchs`: virtual/physical base, size, IRQ, and register-layout pointer.
- `struct omap_mmchs_registers`: named offsets for SYSCONFIG, SYSSTATUS, CON, BLK, ARG, CMD, response registers, DATA, PSTATE, HCTL, SYSCTL, interrupt registers, and capability registers.
- `regs_v1`: AM335x register layout.
- `regs_v0`: DM37xx register layout shifted by 0x100.
- Macros define reset, idle, power, bus width, clock, command, present-state, timeout, interrupt, and capability bit fields.

## Dependencies

Consumed by `emmc.c` and `mmchost_mmchs.c` together with MINIX MMIO helpers.

## Risks

The register tables are static objects. `emmc.c` mutates `regs_v1` into absolute virtual addresses, while `mmchost_mmchs.c` treats offsets as offsets under `io_base`; mixing those usage patterns in one process would be unsafe. Bit-mask correctness is hardware-critical, and one typo in command or interrupt bits can break all card I/O.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/omap_mmc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/sdhcreg.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/sdhcreg.h

## Purpose

Provides NetBSD/OpenBSD-derived SD Host Controller standard register offsets, bit definitions, and helper macros.

## API Surface

Defines SDHC register offsets for DMA address, block size/count, argument, transfer mode, command, response, data, present state, host/power/clock control, software reset, interrupt status/enables, capabilities, and host version. It also defines bit masks for command responses, data direction, card presence, buffer readiness, errors, voltages, DMA, high speed support, and diagnostic bit strings.

## Dependencies

Included by MMCHS host code as a reference/compatibility header for SDHC-style constants.

## Risks

This header is declarative. Risks are primarily semantic drift if hardware-specific code assumes these standard SDHC offsets apply directly to OMAP MMCHS registers. The OMAP driver mostly uses `omap_mmc.h` for actual register offsets.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/sdhcreg.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/sdmmcreg.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/mmc/sdmmcreg.h

## Purpose

Provides NetBSD/OpenBSD-derived MMC and SD command numbers, OCR/R1/CSD/CID/SCR/EXT_CSD bit definitions, response decoding macros, and a bitfield extraction helper.

## API Surface

Defines MMC commands, SD commands, SD application commands, OCR voltage/capacity bits, R1 status bits, RCA helpers, EXT_CSD fields and bus-width values, SPI status bits, CSD/CID/SCR field extraction macros, SDHC capacity decoding, speed constants, and `MMC_RSP_BITS()` backed by `__bitfield()`.

## Dependencies

Used by eMMC, MMCHS, and dummy host implementations to build commands and interpret card register responses.

## Risks

All capacity, speed, write-protect, and bus-width decisions rely on correct bit numbering. `__bitfield()` extracts from a byte view of response words and is intentionally endian-sensitive to the response layout expected by imported code. A mismatch between host response register ordering and these macros can silently miscompute capacity or capabilities.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/mmc/sdmmcreg.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ramdisk/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/ramdisk/Makefile

## Purpose

Builds the boot ramdisk image used by the MINIX memory driver and boot flow.

## Build Role

Defines a generated `image` target from proto files, service binaries, configuration files, generated `/dev` entries, and optional architecture-dependent components. Common programs include `fsck_mfs`, `loadramdisk`, `mfs`, `mount`, `procfs`, `minix-service`, shell, `sysenv`, and `umount`. i386 adds storage/input/bus services such as `floppy`, `pci`, `pckbd`, `at_wini`, optionally `ahci`, `virtio_blk`, `ext2`, and `acpi`. ARM adds `mmc`.

## Control Flow

The Makefile copies configuration files, creates password databases, generates device proto entries with `MAKEDEV.sh`, strips selected binaries, preprocesses the proto template with ramdisk feature defines, and invokes `TOOL_MKFSMFS` to create the MFS image. Recursive make rules are commented out to avoid parallel make issues.

## Dependencies

Depends on NetBSD/MINIX build variables, proto templates, host tools (`mkfsmfs`, `mtree`, `toproto`, `pwd_mkdb`, `sed`, `strip`), and prebuilt service binaries under the object tree.

## Risks

The ramdisk contents are conditional on architecture and build flags. Missing binaries are not built recursively by this file, so the surrounding build must provide them. Proto generation strips comments and blank lines through preprocessing; incorrect defines can materially change the boot image.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ramdisk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ramdisk/rc -->
# File Research: sources/teaching/minix/minix/drivers/storage/ramdisk/rc

## Purpose

Boot-time shell script run from the MINIX ramdisk to start early services, locate the root device, check/mount the root filesystem, and hand off to `/etc/rc`.

## Main Steps

On i386, it starts ACPI when configured, PCI, input/keyboard, procfs, and one primary storage stack: AHCI, virtio block, or AT disk, with floppy started non-critically. It probes virtio by checking `/proc/pci` unless the environment overrides it. On ARM, it starts the MMC driver.

It then starts ramdisk-local procfs, determines `rootdevname` from environment, CD probing, `/dev/ram`, or embedded image ramdisk mode, optionally loads a RAM disk image, runs `fsck_mfs` unless CD boot is active, mounts the root filesystem, reopens standard descriptors away from the ramdisk, mounts procfs on the real root, and executes NetBSD rc infrastructure.

## Dependencies

Depends on `sysenv`, `minix-service`, `mount`, `umount`, `grep`, `cdprobe`, `loadramdisk`, `fsck_mfs`, and service binaries placed in the ramdisk image by the Makefile.

## Risks

Root selection is environment-sensitive. The script tolerates some early service failures but exits if required root selection fails or CD probing cannot find media. Storage-driver selection order matters: AHCI overrides virtio, which overrides AT disk unless environment variables change behavior.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/ramdisk/rc -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/Makefile

## Purpose

Builds the MINIX virtio block driver service.

## Build Role

Defines `PROG=virtio_blk` from `virtio_blk.c`. Links against `libblockdriver`, `libsys`, `libmthread`, and `libvirtio`, then includes `minix.service.mk`.

## Dependencies

Requires the multithreaded blockdriver support and the MINIX virtio library.

## Risks

The library list is essential: the driver uses blockdriver_mt worker sleep/wakeup and virtio queue/device APIs directly.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.c

## Purpose

Implements a MINIX virtio-blk block driver with partition support, multithreaded request handling, virtqueue submission, flush support, geometry reporting, and graceful termination.

## Main Entry Points

- `main()`: parses environment, starts SEF, runs `blockdriver_mt_task()`, then cleans up.
- `sef_cb_init_fresh()`: probes the requested virtio block instance and announces the service.
- `virtio_blk_probe()`: sets up the virtio device, queue, request buffers, config, ready state, and IRQs.
- `virtio_blk_open()` / `virtio_blk_close()`: enforce read-only feature, parse partitions on first open, manage worker count and open count.
- `virtio_blk_transfer()`: maps caller buffers, constructs virtio-blk requests, submits them, sleeps until completion, and returns bytes/errors.
- `virtio_blk_flush()`: submits a flush request when supported.
- `virtio_blk_intr()` / `virtio_blk_device_intr()`: process used queue entries and wake the worker thread associated with each request.
- `virtio_blk_part()` / `virtio_blk_geometry()` / `virtio_blk_device()`: partition, geometry, and device-id callbacks.

## Control Flow And State

The driver negotiates a fixed feature table and keeps one global `blk_dev`. It allocates one request header and one status cell per worker thread in contiguous memory. First open initializes partition tables from the configured capacity and enables four workers; last close flushes, returns to one worker, and may terminate if SIGTERM was requested.

`virtio_blk_transfer()` validates sector-aligned iovecs, truncates at partition boundaries, maps grants to physical vectors with `sys_vumap()`, prepares a header with direction and sector, marks virtio descriptor write/read bits, appends the status byte, submits to queue 0 with the current thread id as callback data, and sleeps. The interrupt handler drains all completed queue entries and wakes the stored thread ids.

## Dependencies

Depends on MINIX blockdriver_mt, virtio library APIs, safe virtual-to-physical grant mapping, disk ioctls, partition parsing, and definitions from `virtio_blk.h`.

## Risks

Correctness depends on per-thread request/status storage matching the worker id returned by `blockdriver_mt_get_tid()`. Queue completion must wake exactly the submitted thread. The driver assumes 512-byte logical sectors even if the host advertises another block size. Partial partition truncation adjusts vectors in place before mapping. Flush is optional and returns `EOPNOTSUPP` if unsupported; close ignores that return.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.h -->
# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.h

## Purpose

Provides BSD-licensed virtio-blk protocol constants and structures.

## API Surface

Defines virtio-blk feature bits, ID size, packed `struct virtio_blk_config`, request command types, barrier/flush/get-id flags, `struct virtio_blk_outhdr`, `struct virtio_scsi_inhdr`, and status byte values.

## Dependencies

Used by `virtio_blk.c` together with MINIX integer typedefs and the virtio library.

## Risks

The packed config layout and feature bit numbers must match the virtio specification. The driver reads config offsets manually, so any mismatch between this structure and manual offset assumptions would be dangerous.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/vnd/Makefile -->
# File Research: sources/teaching/minix/minix/drivers/storage/vnd/Makefile

## Purpose

Builds the MINIX vnode disk driver service.

## Build Role

Defines `PROG=vnd` from `vnd.c`, links against `libblockdriver` and `libsys`, and includes `minix.service.mk`.

## Dependencies

Requires blockdriver support and system-call helpers for safe copying and service operation.

## Risks

Simple build file; correctness depends on `vnd.c` receiving blockdriver and system libraries.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/vnd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/vnd/vnd.c -->
# File Research: sources/teaching/minix/minix/drivers/storage/vnd/vnd.c

## Purpose

Implements the MINIX vnode disk driver, exposing a regular file as a block device with partitions, geometry, read-only mode, and vnconfig-style ioctls.

## Main Entry Points

- `main()`: initializes SEF and enters `blockdriver_task()`.
- `vnd_init()`: initializes instance number and empty device state.
- `vnd_open()` / `vnd_close()`: validate configured state, enforce read-only access, reparse partitions, and manage open count.
- `vnd_transfer()`: reads/writes the backing file through an intermediate buffer and caller grants.
- `vnd_ioctl()`: handles `VNDIOCSET`, `VNDIOCCLR`, `VNDIOCGET`, `DIOCOPENCT`, and `DIOCFLUSH`.
- `vnd_layout()`: computes device geometry and accessible size from file size or user-provided geometry.
- `vnd_partition()` / `vnd_part()` / `vnd_geometry()`: maintain and expose partition/geometry data.
- `vnd_signal()`: defers termination until open count reaches zero.

## Control Flow And State

Global `state` stores the backing file descriptor, open count, exiting flag, read-only flag, backing file dev/inode, partition arrays, geometry, and 64 KiB transfer buffer. `VNDIOCSET` requires an unconfigured device with only the ioctl opener active, copies the caller's file descriptor into the driver using `copyfd()`, verifies it is a regular file, allocates the transfer buffer with `mmap()`, records read-only and identity state, computes layout, parses partitions, and returns the device size. `VNDIOCCLR` closes and unmaps the backing file, refusing if busy unless forced.

Transfers compute a bounded byte count within the selected partition, then chunk through the intermediate buffer. Reads use `pread()` followed by safe copy to the caller. Writes safe-copy from the caller, then `pwrite()` to the backing file. `BDEV_FORCEWRITE` triggers `fsync()`.

## Dependencies

Depends on MINIX blockdriver/drvlib APIs, partition parsing, `copyfd()` VFS backcall, safe-copy vector APIs, POSIX file operations, `mmap()`, and vnode disk ioctl structures from system headers.

## Risks

The device cannot recover after crash or live restart because it cannot reacquire the backing file descriptor. Forced clear closes the backing file while other opens may still exist, leaving the device unconfigured for later operations. `fsync()` return values are ignored. Intermediate-buffer copy logic is bounded by `VND_BUF_SIZE` and assumes `SCPVEC_NR >= NR_IOREQS`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/drivers/storage/vnd/vnd.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/Makefile

## Purpose

Top-level Makefile for MINIX filesystem services.

## Build Role

Includes `bsd.own.mk`, always builds `mfs` and `pfs`, and when `MKIMAGEONLY` is not `no`, also builds `ext2`, `isofs`, `procfs`, and `ptyfs`. On i386 it additionally builds `hgfs` and `vbfs`. It includes `bsd.subdir.mk` for recursive subdirectory builds.

## Dependencies

Depends on NetBSD bsd make infrastructure and build variables such as `MKIMAGEONLY` and `MACHINE_ARCH`.

## Risks

The conditional appears inverted relative to the variable name: extra filesystems are included when `MKIMAGEONLY != "no"`. That may be intentional for this tree, but it is worth checking before changing build policy.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/Makefile.inc -->
# File Research: sources/teaching/minix/minix/fs/Makefile.inc

## Purpose

Common include for MINIX filesystem service Makefiles.

## Build Role

Sets default install directory `BINDIR?=/service`, disables manual pages with `MAN?=`, and includes the parent `Makefile.inc`.

## Dependencies

Depends on the higher-level MINIX make include one directory above.

## Risks

Small policy file. Changes affect all filesystem services that include it, especially installation location.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/Makefile -->
# File Research: sources/teaching/minix/minix/fs/ext2/Makefile

## Purpose

Builds the MINIX ext2 filesystem service.

## Build Role

Defines `PROG=ext2` with ext2 service sources for block allocation, links, mount, misc, open/protect/read/write, stats, utilities, inode allocation/inode handling, main, path, and superblock logic. Links against `libminixfs`, `libfsdriver`, `libbdev`, and `libsys`, sets `WARNS=3`, and includes `minix.service.mk`.

## Dependencies

Depends on MINIX filesystem service libraries and block-device access library.

## Risks

This Makefile defines the compilation surface for the ext2 service. Missing a source from `SRCS` would remove filesystem behavior at link time; library order also matters because the service uses shared fsdriver/minixfs/bdev support.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/Makefile -->