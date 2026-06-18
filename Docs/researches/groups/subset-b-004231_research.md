# Research Group: subset-b-004231

This grouped report covers the MemoryStick block drivers and host adapters under `sources/distributed-fs/ceph-client/drivers/memstick/`, plus the Fusion MPT build hooks and base MPI protocol header under `sources/distributed-fs/ceph-client/drivers/message/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.c Research

## Purpose
`ms_block.c` implements the legacy Sony MemoryStick block-device driver. It binds legacy/Duo storage cards through the memstick core, builds an in-memory flash translation layer from boot/OOB metadata, exposes the medium as a blk-mq disk named `msblkN`, and serializes all media I/O through memstick TPC state machines.

## Important APIs, Types, And Functions
The public integration surface is `struct memstick_driver msb_driver`, `msb_probe`, `msb_remove`, optional `msb_suspend`/`msb_resume`, `msb_check_card`, `msb_stop`, and `msb_start`. Block-layer integration is via `msb_init_disk`, `msb_queue_rq`, `msb_io_work`, `msb_bdops`, and `msb_mq_ops`. The core media logic is split into state-machine callbacks (`h_msb_read_page`, `h_msb_write_block`, `h_msb_send_command`, `h_msb_reset`, `h_msb_parallel_switch`) and synchronous wrappers (`msb_read_page`, `msb_write_block`, `msb_erase_block`, `msb_update_block`). FTL setup is handled by `msb_read_boot_blocks`, `msb_read_bad_block_table`, `msb_ftl_initialize`, and `msb_ftl_scan`. Cache behavior lives in `msb_cache_init`, `msb_cache_read`, `msb_cache_write`, `msb_cache_flush`, and `msb_cache_flush_timer`.

## Control Flow
Probe allocates `struct msb_data`, resets and initializes the card, optionally switches to parallel mode, reads boot blocks, allocates FTL/cache buffers, reads factory bad-block tables, scans every physical block OOB, and then registers a blk-mq disk. A blk-mq request is accepted only if no request is already active; an ordered workqueue maps the request scatterlist, converts sector offsets to logical-block/page coordinates, and executes read or write loops one page at a time. Reads consult the write cache before issuing `MS_CMD_BLOCK_READ`. Whole-block writes bypass cache and allocate a replacement physical block; partial writes are coalesced in a block-size cache and later flushed by timer or before conflicting writes.

## State And Persistence
Persistent on-card state is the boot block, OOB logical-address fields, overwrite/management flags, factory bad-block tables, erased/free block state, and card data pages. Runtime-only state includes `lba_to_pba_table`, used and erased bitmaps, per-zone free counts, cached block data, request pointer, memstick register-window cache, and state-machine counters. The driver never persists a separate mapping table; it reconstructs the FTL from OOB metadata at probe/resume. Bad blocks/pages are persisted by clearing overwrite flag bits. Serious internal consistency failures switch the device read-only.

## Dependencies And Integration Points
This file depends on the Linux memstick core request protocol, blk-mq, gendisk lifetime, scatterlist helpers, timers, workqueues, IDR allocation, endian helpers, and the register/format constants from `<linux/memstick.h>` and `ms_block.h`. Host adapters must implement `memstick_host::set_param`, request submission, INT retrieval, and optional parallel/auto-INT capabilities. The block layer sees a single logical disk with logical block size equal to the MemoryStick page size.

## Risks
The FTL assumes single-threaded I/O and relies on one active blk-mq request; any future concurrency change would need stronger locking around bitmaps, cache, and register windows. Partial-write cache loss on sudden removal/power loss can leave updates pending. Error handling erases or marks blocks bad aggressively after resets, so host-controller false errors can cause avoidable wear or data loss. `msb_sg_copy` uses small temporary SG arrays in several paths; unexpected SG fragmentation beyond local limits would be a correctness risk. Resume validation is only active under `CONFIG_MEMSTICK_UNSAFE_RESUME`; otherwise the card is marked dead.

## Test Signals
Useful tests include module load/unload with legacy MemoryStick media, read-only class detection, serial-to-parallel fallback, full-card scan with factory bad blocks, random read/write/fsck cycles, partial-page writes that force cache fill and flush, bad-page/bad-block injection, suspend/resume with same and swapped cards, removal during active I/O, `verify_writes=1`, `debug=2`, and blk status checks for media errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.h -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.h Research

## Purpose
`ms_block.h` defines the private data structures, constants, boot-page layouts, state enums, and debug helpers used by the legacy MemoryStick block driver in `ms_block.c`.

## Important APIs, Types, And Functions
Key constants include `MS_BLOCK_MAX_SEGS`, `MS_BLOCK_MAX_PAGES`, `MS_BLOCK_MAX_BOOT_ADDR`, `MS_BLOCK_BOOT_ID`, `MS_BLOCK_INVALID`, `MS_MAX_ZONES`, and `MS_BLOCKS_IN_ZONE`. Error and OOB helper masks group memstick status/interrupt/overwrite/management bits. Packed on-card layout types include `struct ms_boot_header`, `struct ms_system_item`, `struct ms_system_entry`, `struct ms_boot_attr_info`, `struct ms_cis_idi`, and `struct ms_boot_page`. `struct msb_data` is the central runtime object shared by the FTL, request queue, cache, state machines, and block disk. Enums define legal state values for read-page, write-block, simple-command, reset, and parallel-switch handlers.

## Control Flow
The header does not execute code, but it controls the state-machine topology used by `ms_block.c`. Each enum value corresponds to a switch branch in a `h_msb_*` callback. `struct msb_data` fields connect probe initialization, FTL scanning, blk-mq processing, memstick TPC callbacks, cache timers, and suspend/remove handling.

## State And Persistence
The packed boot structures mirror persistent MemoryStick boot metadata read from flash. `struct msb_data` is volatile per-card state and stores pointers to persistent metadata copies (`boot_page`) and reconstructed in-memory indexes (`lba_to_pba_table`, used/erased bitmaps, free counts). The header’s sentinel values, especially `MS_BLOCK_INVALID`, define how erased/free or unmapped locations are represented.

## Dependencies And Integration Points
It depends on memstick core declarations for register/status constants and types such as `struct ms_register`, `struct ms_register_addr`, and `struct memstick_dev`. It also exposes block-layer and kernel infrastructure fields through `gendisk`, `request_queue`, `blk_mq_tag_set`, `hd_geometry`, scatterlists, workqueues, timers, and spinlocks.

## Risks
The header fixes `MS_MAX_ZONES` at 16 while the runtime computes `zone_count` from card block count; unsupported larger media could overflow `free_block_count`. Packed structures must remain byte-accurate against card format, and endian conversion must be performed by the C file before normal use. The include guard name `MS_BLOCK_NEW_H` is historical and easy to confuse with a public API.

## Test Signals
Compile coverage with `CONFIG_MEMSTICK` and `CONFIG_MEMSTICK_UNSAFE_RESUME` toggles is important. Runtime tests should validate parsed boot attributes, zone counts, invalid-block sentinels, all state-machine transitions, and debug output gating through the `debug` module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/mspro_block.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/mspro_block.c Research

## Purpose
`mspro_block.c` implements block-device support for Sony MemoryStick PRO storage cards. Unlike the legacy driver, it relies on the card’s PRO logical addressing and attribute table rather than building a private FTL.

## Important APIs, Types, And Functions
The main runtime object is `struct mspro_block_data`, which stores the memstick device, blk-mq disk/queue, current request, protocol handler callback, scatterlist progress, sysfs attributes, geometry, interface mode, and active/eject flags. Driver entry points are `mspro_block_probe`, `mspro_block_remove`, optional PM callbacks, and `mspro_block_driver`. Block integration uses `mspro_queue_rq`, `mspro_block_issue_req`, `mspro_block_complete_req`, `mspro_block_stop`, `mspro_block_start`, `mspro_block_init_disk`, and `ms_block_bdops`. Protocol flow uses `h_mspro_block_req_init`, `h_mspro_block_transfer_data`, `h_mspro_block_wait_for_ced`, `h_mspro_block_get_ro`, and `h_mspro_block_setup_cmd`. Attribute parsing and sysfs exposure use `mspro_block_read_attributes` plus `mspro_block_attr_show_*`.

## Control Flow
Probe initializes card register windows, waits for CED, negotiates serial/4-bit/8-bit interface, reads write-protect state, reads the attribute directory, creates a sysfs `media_attributes` group, and registers `mspblkN`. Queue submission accepts one request at a time, maps request segments, programs a PRO parameter register with data count/address, sends read/write commands, pages data through `READ_LONG_DATA` or `WRITE_LONG_DATA`, and completes or chunks the blk request when the memstick callback chain reports CED or error.

## State And Persistence
Persistent media state is represented by the PRO attribute table, system info, device info, MBR/PBR/specfile records, and card data. Runtime state includes parsed copies of sysfs attributes, current segment/page counters, negotiated `system` bus mode, `read_only`, `active`, and `eject`. There is no driver-maintained on-card mapping; capacity comes from `user_block_count`, `block_size`, and `unit_size`.

## Dependencies And Integration Points
The driver integrates with the memstick core, blk-mq, sysfs, register-block helpers in `<linux/memstick.h>`, IDR disk numbering, gendisk, SCSI-like geometry reporting, and host capabilities such as `MEMSTICK_CAP_PAR4`, `MEMSTICK_CAP_PAR8`, and `MEMSTICK_CAP_AUTO_GET_INT`.

## Risks
Only one request is tracked, so blk-mq parallelism is intentionally constrained. `h_mspro_block_transfer_data` assumes per-segment page-size multiples and maps a single page-sized transfer view from each SG segment. Attribute parsing trusts card-provided offsets and sizes after bounded count validation; malformed attributes can exercise allocation and range logic. Resume under `CONFIG_MEMSTICK_UNSAFE_RESUME` validates only sysinfo identity, not all media state.

## Test Signals
Test with PRO cards in serial, 4-bit, and 8-bit-capable hosts; read/write workloads across SG boundaries; sysfs attribute reads for sysinfo/model/MBR/devinfo; write-protect changes; request errors and STOP command paths; removal during active I/O; suspend/resume with identical and swapped media; and dynamic major allocation through the `major` parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/mspro_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/Kconfig Research

## Purpose
This Kconfig file declares the selectable MemoryStick host-controller drivers used by the memstick core.

## Important APIs, Types, And Functions
The symbols are `MEMSTICK_TIFM_MS`, `MEMSTICK_JMICRON_38X`, `MEMSTICK_R592`, and `MEMSTICK_REALTEK_USB`. They map user-visible configuration choices to the corresponding host modules: `tifm_ms`, `jmb38x_ms`, `r592`, and, per help text, `rts5139_ms` although the Makefile builds `rtsx_usb_ms.o`.

## Control Flow
Kconfig has no runtime control flow. Its dependency graph controls compilation: TI and Ricoh/JMicron hosts require PCI; TI selects `TIFM_CORE`; Realtek USB depends on `MISC_RTSX_USB`. If a symbol is built as module, the matching object is included by the host Makefile.

## State And Persistence
The file contributes persistent kernel configuration state through `.config`. No runtime state is stored here.

## Dependencies And Integration Points
This file integrates with the top-level memstick Kconfig and build system. It ensures host drivers are only visible when their bus/framework dependencies exist.

## Risks
The Realtek help text says the module is `rts5139_ms`, while the actual object and platform driver are `rtsx_usb_ms`; this can confuse users and package scripts. Minimal dependencies mean functional runtime still depends on the core memstick layer and specific parent bus drivers being configured correctly elsewhere.

## Test Signals
Run `oldconfig`/`menuconfig` visibility checks, build each symbol as `y` and `m`, verify dependency auto-selection for `TIFM_CORE`, and confirm module names produced by `make modules`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/Makefile Research

## Purpose
This Makefile maps MemoryStick host-controller Kconfig symbols to their object files.

## Important APIs, Types, And Functions
The build rules are `obj-$(CONFIG_MEMSTICK_TIFM_MS) += tifm_ms.o`, `obj-$(CONFIG_MEMSTICK_JMICRON_38X) += jmb38x_ms.o`, `obj-$(CONFIG_MEMSTICK_R592) += r592.o`, and `obj-$(CONFIG_MEMSTICK_REALTEK_USB) += rtsx_usb_ms.o`.

## Control Flow
There is no runtime control flow. Kbuild evaluates the `obj-*` variables and includes built-in or modular objects according to the resolved configuration.

## State And Persistence
The only state is build configuration encoded in `.config` and generated Kbuild metadata.

## Dependencies And Integration Points
This file integrates the host directory with the kernel recursive build system. Its object names must match the C files and the module names expected by Kconfig/help text and module aliases.

## Risks
The Realtek Kconfig help names `rts5139_ms`, while this Makefile builds `rtsx_usb_ms.o`; mismatch can cause documentation or packaging confusion even though compilation is correct.

## Test Signals
Build all four host drivers as modules and built-ins, inspect generated `.ko` names, and verify disabled symbols omit the corresponding objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/jmb38x_ms.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/jmb38x_ms.c Research

## Purpose
`jmb38x_ms.c` implements a PCI memstick host adapter for JMicron JMB38x MemoryStick readers. It translates memstick core requests into MMIO TPC commands, FIFO or DMA transfers, and card-detect notifications.

## Important APIs, Types, And Functions
`struct jmb38x_ms_host` stores per-slot MMIO address, IRQ, tasklet, timer, current request, transfer flags, FIFO residue, and interface mode. `struct jmb38x_ms` stores the PCI device and flexible array of memstick hosts. Important functions include `jmb38x_ms_issue_cmd`, `jmb38x_ms_complete_cmd`, `jmb38x_ms_isr`, `jmb38x_ms_abort`, `jmb38x_ms_req_tasklet`, `jmb38x_ms_set_param`, `jmb38x_ms_probe`, and `jmb38x_ms_remove`.

## Control Flow
Probe enables PCI/DMA, requests BAR regions, powers PMOS rails, counts 256-byte MMIO slot BARs, allocates one memstick host per slot, requests the shared IRQ, and registers each host. Request submission schedules a tasklet that pulls the next memstick request, programs the TPC register, optionally maps one SG entry for DMA, otherwise enables FIFO interrupts or uses inline register payloads for transfers up to 8 bytes. The IRQ handler handles transfer completion, FIFO readiness, command completion, errors, and media in/out events. A timer aborts hung commands.

## State And Persistence
All state is volatile hardware/runtime state: MMIO registers, PCI config PMOS/clock bits, `host->req`, `cmd_flags`, FIFO partial words, DMA mapping, LED state, interface mode, and timeout. No persistent media metadata is stored by the host.

## Dependencies And Integration Points
The driver depends on PCI, DMA mapping, IRQ sharing, tasklets, timers, memstick host APIs, and JMicron PCI IDs. It advertises `MEMSTICK_CAP_PAR4 | MEMSTICK_CAP_PAR8` and implements `request`/`set_param` callbacks consumed by `ms_block.c` and `mspro_block.c`.

## Risks
DMA maps exactly one scatterlist entry, so callers must present a compatible long-data SG. PIO code casts byte buffers to `unsigned int *`, which assumes suitable alignment and endian handling for the platform. Error paths can complete a request from IRQ context and immediately issue more work, so locking and request ownership are sensitive. `no_dma` is a global module parameter affecting all slots.

## Test Signals
Test multi-slot JMicron cards, media insertion/removal interrupts, DMA and `no_dma=1` PIO modes, short register TPCs, long reads/writes, serial/4-bit/8-bit interface transitions, timeout aborts, shared IRQ behavior, suspend/resume with detect-change replay, and module unload during an active request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/jmb38x_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/r592.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/r592.c Research

## Purpose
`r592.c` implements a PCI memstick host adapter for Ricoh R5C592 readers. It executes memstick TPCs through Ricoh MMIO registers, a 512-byte FIFO, optional DMA, and a dedicated request-processing kernel thread.

## Important APIs, Types, And Functions
The private state is `struct r592_device` from `r592.h`. Important functions include register helpers (`r592_read_reg`, `r592_write_reg`, raw big-endian FIFO helpers), power/interface functions (`r592_enable_device`, `r592_set_mode`, `r592_host_reset`), DMA/FIFO functions (`r592_transfer_fifo_dma`, `r592_transfer_fifo_pio`, `r592_write_fifo_pio`, `r592_read_fifo_pio`), TPC execution (`r592_execute_tpc`), request processing (`r592_process_thread`, `r592_submit_req`), card-detect handling (`r592_irq`, `r592_detect_timer`, `r592_update_card_detect`), and PCI lifecycle (`r592_probe`, `r592_remove`, PM callbacks).

## Control Flow
Probe allocates a memstick host, enables PCI, maps BAR0, initializes locks/completions/kfifo/timer, detects DMA capability, starts `r592_io`, allocates a dummy DMA page, requests the shared IRQ, arms card-detect interrupts, and registers the host. The memstick core calls `r592_submit_req`, waking the thread. The thread pulls one request with `memstick_next_req`, executes it synchronously, and then loops. `r592_execute_tpc` validates card presence and FIFO capacity, writes request data by DMA or PIO, triggers the TPC, waits for RDY/CED, reads errors and INT bits, and reads response data.

## State And Persistence
State is volatile: current request, parallel-mode flag, DMA capability/error/completion, MMIO state, card-detect timer, PIO spill kfifo, and dummy DMA address. No persistent media state is managed here.

## Dependencies And Integration Points
The driver integrates with PCI, DMA mapping, kthreads/freezer-aware scheduling primitives, completions, kfifo, timers, IRQs, and the memstick host API. It advertises `MEMSTICK_CAP_PAR4`; block drivers above it decide legacy versus PRO semantics.

## Risks
DMA is only accepted for long-data requests exactly `R592_LFIFO_SIZE` bytes, with a documented hidden assumption that SG entries count as one. PIO FIFO code uses 32-bit casts on byte buffers. Polling waits up to 1 second and can tie up the I/O thread. Remove stops the thread before draining current requests, so request error completion must remain correct.

## Test Signals
Exercise DMA enabled/disabled, 512-byte and non-512-byte long transfers, short register transfers, card insertion/removal debounce, serial/parallel switching, CRC/send/receive error handling, timeout paths, suspend/resume, and unload while requests are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/r592.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/r592.h -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/r592.h Research

## Purpose
`r592.h` defines Ricoh R5C592 register offsets, bit masks, private device state, and logging macros for `r592.c`.

## Important APIs, Types, And Functions
Register definitions cover TPC execution (`R592_TPC_EXEC`), status (`R592_STATUS_*`), I/O control (`R592_IO_*`), power (`R592_POWER_*`), mode (`R592_IO_MODE_*`), card/IRQ/FIFO register (`R592_REG_MSC_*`), DMA registers, FIFO PIO window, and debug registers. `struct r592_device` stores the PCI device, memstick host, current request, MMIO base, IRQ locks, detect timer, I/O thread, parallel mode, PIO kfifo, DMA capability/error/completion, and dummy DMA page. Macros `message`, `dbg`, `dbg_verbose`, and `dbg_reg` are gated by the C file’s `debug` variable.

## Control Flow
The header itself has no runtime logic, but its register masks define the branch conditions in `r592_wait_status`, `r592_irq`, `r592_execute_tpc`, DMA setup/teardown, and card-detection rearming.

## State And Persistence
All represented state is controller-runtime state. The header does not describe persistent media formats.

## Dependencies And Integration Points
It includes memstick, spinlock, interrupt, workqueue, kfifo, and ctype headers. The MMIO definitions are private to the Ricoh host and are not shared with other host adapters.

## Risks
The include guard is `#ifndef R592_H` without a visible `#define R592_H`, so multiple inclusion would not be guarded in the conventional way. Some register comments mark inferred or debug behavior, which means hardware variance could break assumptions. The `debug` variable used by macros is defined in `r592.c`, making the header unsuitable for independent inclusion without that symbol.

## Test Signals
Compile with warnings enabled to catch include-guard issues, validate register values against hardware traces, and run debug levels 1-3 to confirm logging paths do not change behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/r592.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/rtsx_usb_ms.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/rtsx_usb_ms.c Research

## Purpose
`rtsx_usb_ms.c` implements a MemoryStick host for Realtek RTS5129/RTS5139-class USB card readers exposed through the `rtsx_usb` core. It translates memstick core requests into Realtek register-command batches and USB bulk transfers.

## Important APIs, Types, And Functions
`struct rtsx_usb_ms` stores the platform device, Realtek USB core pointer, memstick host, current request, mutex/work items, card polling work, clock/SSC settings, power/interface state, eject flag, and system suspend flag. Important functions include `ms_power_on`, `ms_power_off`, `ms_transfer_data`, `ms_write_bytes`, `ms_read_bytes`, `rtsx_usb_ms_issue_cmd`, `rtsx_usb_ms_handle_req`, `rtsx_usb_ms_request`, `rtsx_usb_ms_set_param`, `rtsx_usb_ms_poll_card`, probe/remove, and PM callbacks.

## Control Flow
Probe obtains the parent `rtsx_ucr`, allocates a memstick host, initializes work and delayed polling, enables runtime PM, and registers the host. Requests schedule a work item. The worker runtime-resumes the device, repeatedly pulls memstick requests, takes the Realtek device mutex, checks exclusive card ownership, issues the command, stores the request error, and lets `memstick_next_req` advance the queue. Long data uses `MS_TRANSFER` plus USB bulk transfer through a ring buffer; short data uses ping-pong buffer register batches. If card INT is required, serial mode explicitly reads `MS_TPC_GET_INT`, while parallel mode derives memstick INT bits from Realtek status.

## State And Persistence
State is volatile: power mode, clock, SSC depth, interface mode, in-flight request, delayed polling, runtime PM references, and error bits in the Realtek core. No card metadata is persisted here.

## Dependencies And Integration Points
The file depends on `rtsx_usb` register helpers, USB bulk pipes, runtime/system PM, memstick host callbacks, workqueues, delayed work, platform-device binding, and Realtek card-sharing arbitration. It advertises `MEMSTICK_CAP_PAR4`.

## Risks
Runtime PM reference balancing is subtle because power-on takes an extra no-resume reference and removal compensates for active state. Card detection is polling-based after power-on, so latency and runtime suspend interactions matter. The host mutex exists but request execution mostly serializes through work and the parent device mutex; removal must safely drain `host->req`. Error decoding differs for read/write byte TPCs and can return timeout for status combinations that are not CRC/INT errors.

## Test Signals
Test probe/remove as platform child of `rtsx_usb`, runtime suspend/resume with no card and with card powered off, system suspend ordering, insertion/removal polling, serial and 4-bit mode, short-byte commands, long bulk read/write paths, exclusive-card conflicts with SD/XD functions, and forced USB transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/rtsx_usb_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/tifm_ms.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/host/tifm_ms.c Research

## Purpose
`tifm_ms.c` implements a MemoryStick host for Texas Instruments FlashMedia sockets. It connects the TIFM socket event model to the memstick core and handles TPC execution through TIFM MemoryStick/FIFO/DMA registers.

## Important APIs, Types, And Functions
The private `struct tifm_ms` stores the TIFM device, timeout timer, current request, tasklet, mode mask, transfer offset, use-DMA/eject flags, command flags, and PIO residue. Important functions are `tifm_ms_issue_cmd`, `tifm_ms_complete_cmd`, `tifm_ms_data_event`, `tifm_ms_card_event`, `tifm_ms_req_tasklet`, `tifm_ms_set_param`, `tifm_ms_abort`, `tifm_ms_probe`, and `tifm_ms_remove`.

## Control Flow
Probe verifies card presence, allocates a memstick host, registers tasklet/timer callbacks, assigns TIFM socket `card_event` and `data_event` handlers, advertises parallel capability if the socket supports it, and adds the host. Request submission schedules a tasklet that pulls memstick requests and programs the TIFM command path. Long-data power-of-two transfers may use TIFM DMA; other transfers use FIFO PIO with partial-word handling. Data and card events set `FIFO_READY`, `CMD_READY`, and `CARD_INT`; when required conditions are met, completion advances to the next memstick request.

## State And Persistence
State is transient host-controller state: socket registers, DMA mapping, FIFO residue, command flags, eject flag, timer, and current request. Persistent MemoryStick media state is handled by upper block drivers.

## Dependencies And Integration Points
The driver depends on the TIFM core (`struct tifm_dev`, socket registers, DMA helpers, `tifm_eject`), memstick host callbacks, tasklets, timers, scatterlist/highmem helpers, and module parameter `no_dma`.

## Risks
Timeout abort calls `tifm_eject`, which is a heavy recovery action for slow cards. DMA is disabled unless long-data length is a power of two, creating two distinct data paths. Remove contains a likely direction typo in `tifm_unmap_sg` arguments for active DMA cleanup, which deserves review. FIFO PIO casts raw buffers to `unsigned int *`, with the usual alignment/endian concerns.

## Test Signals
Test TIFM card insertion/removal, serial and parallel interface modes, DMA and `no_dma=1`, non-power-of-two PIO transfers, timeout/eject behavior, CRC and timeout status bits, suspend/resume, and module removal during active DMA/PIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/host/tifm_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/Makefile -->
# sources/distributed-fs/ceph-client/drivers/message/Makefile Research

## Purpose
This Makefile is the build entry point for MPT-based message-passing device drivers.

## Important APIs, Types, And Functions
It contains one build rule: `obj-$(CONFIG_FUSION) += fusion/`, which descends into the Fusion MPT subdirectory when the `FUSION` menuconfig is enabled.

## Control Flow
There is no runtime logic. Kbuild uses the `CONFIG_FUSION` value to decide whether to enter `drivers/message/fusion/`.

## State And Persistence
The file only contributes build-time state derived from kernel configuration.

## Dependencies And Integration Points
It integrates the message driver subtree with the broader kernel build. The downstream `fusion/Kconfig` and `fusion/Makefile` define actual driver symbols and objects.

## Risks
Because `FUSION` is a bool gate with no object itself, disabling it hides all nested Fusion drivers. Misconfigured parent Kconfig inclusion would silently omit all MPT drivers.

## Test Signals
Verify `CONFIG_FUSION=n` skips the directory and `CONFIG_FUSION=y` descends into it, then build selected Fusion children as modules and built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/Kconfig Research

## Purpose
This Kconfig file defines the Fusion Message Passing Technology driver menu and child driver symbols for SPI, Fibre Channel, SAS, ioctl control, Fibre Channel LAN, scatter-gather sizing, and logging.

## Important APIs, Types, And Functions
The parent `FUSION` bool depends on `PCI && HAS_IOPORT`. Child symbols include `FUSION_SPI`, `FUSION_FC`, `FUSION_SAS`, `FUSION_MAX_SGE`, `FUSION_CTL`, `FUSION_LAN`, and `FUSION_LOGGING`. Dependencies/selects connect the storage transports to SCSI transport attributes (`SCSI_SPI_ATTRS`, `SCSI_FC_ATTRS`, `SCSI_SAS_ATTRS`), networking (`NET_FC`), and control device support.

## Control Flow
Kconfig controls visibility and compilation. If `FUSION=n`, all child options are skipped. If enabled, individual transport modules can be built independently while sharing common base/scsi helper objects via the Makefile.

## State And Persistence
Configuration state is persisted in `.config`. `FUSION_MAX_SGE` sets a compile-time/default maximum scatter-gather limit between 16 and 128. `FUSION_LOGGING` compiles in debug logging support controlled later through sysfs.

## Dependencies And Integration Points
The file integrates Fusion MPT drivers with PCI, SCSI transport classes, Fibre Channel networking, misc-device ioctl control, and the build rules in `fusion/Makefile`.

## Risks
Transport symbols cause repeated inclusion of common objects (`mptbase.o`, `mptscsih.o`) through separate module lists; build rules must continue to avoid duplicate built-in conflicts. `FUSION_MAX_SGE` below hardware/workload expectations can reduce I/O segmentation capability. `FUSION_CTL` exposes powerful firmware/control ioctls and should be enabled deliberately.

## Test Signals
Run Kconfig dependency tests for each child, build SPI/FC/SAS combinations, verify `FUSION_MAX_SGE` bounds, confirm logging sysfs exists only with `FUSION_LOGGING`, and smoke-test module names described in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/Makefile -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/Makefile Research

## Purpose
This Makefile maps Fusion MPT transport/control Kconfig symbols to object files.

## Important APIs, Types, And Functions
Rules build `mptbase.o`, `mptscsih.o`, and a transport object for `FUSION_SPI`, `FUSION_FC`, or `FUSION_SAS`; optional modules are `mptctl.o` for `FUSION_CTL` and `mptlan.o` for `FUSION_LAN`. A commented `ccflags-y := -DMPT_DEBUG_VERBOSE` notes an additional verbose build-time debug option.

## Control Flow
There is no runtime logic. Kbuild evaluates object lists according to selected symbols and links common/transport components into the appropriate modules or built-in objects.

## State And Persistence
The file only affects build artifacts. Debug verbosity can be changed by editing the commented `ccflags-y`, while normal logging support is controlled by Kconfig.

## Dependencies And Integration Points
It integrates the Fusion source files with Kbuild and relies on `fusion/Kconfig` to prevent invalid symbol combinations. Common objects are shared by multiple transport drivers.

## Risks
Selecting multiple Fusion transports can require careful module composition because the same common object names appear in several `obj-*` lines. Accidental enabling of the commented verbose flag would increase log volume. The Makefile has no direct rule for headers such as `lsi/mpi.h`; header compatibility is enforced only through dependent C compilation.

## Test Signals
Build SPI-only, FC-only, SAS-only, all transports, ioctl, and LAN combinations as modules and built-ins; inspect resulting modules for duplicate symbol/link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi.h Research

## Purpose
`mpi.h` is the base LSI Fusion MPT Message Passing Interface header. It defines product-independent MPI versioning, IOC states, PCI system-interface register offsets, doorbell fields, message function codes, scatter-gather element layouts/macros, standard request/reply headers, and IOC status/log-info constants.

## Important APIs, Types, And Functions
Version constants include `MPI_VERSION_MAJOR`, `MPI_VERSION_MINOR`, `MPI_VERSION`, and `MPI_HEADER_VERSION`. IOC state and fault macros define reset/ready/operational/fault states and PCI parity/bus fault codes. System interface macros define doorbell, write-sequence, diagnostic, interrupt, and request/reply FIFO offsets. Function codes cover SCSI I/O, task management, IOC init/facts/config, port enable, events, firmware upload/download, target mode, FC/SAS/SATA/SMP, diagnostic, LAN, inband, reset, handshake, reply-frame removal, and host page-buffer access. Types include `MPI_VERSION_STRUCT`, `MPI_VERSION_FORMAT`, multiple `SGE_*` simple/chain/transaction structures, `SGE_MPI_UNION`, `MSG_REQUEST_HEADER`, and `MSG_DEFAULT_REPLY`. SGE helper macros pack and unpack flags, lengths, chain offsets, and context reply types.

## Control Flow
The header has no executable control flow, but it defines the wire-format constants used by Fusion drivers to program request frames, parse reply frames, poll/register interrupts, post/free FIFO entries, construct SGLs, and classify controller status.

## State And Persistence
It models hardware/firmware protocol state rather than owning runtime state. Values describe persistent ABI contracts between host drivers and IOC firmware; changing them would break binary protocol compatibility.

## Dependencies And Integration Points
The header depends on base integer typedefs such as `U8`, `U16`, `U32`, `U64`, and `MPI_POINTER` provided by surrounding Fusion headers. It is included by transport-specific and common Fusion MPT drivers that implement SCSI, FC, SAS, LAN, control, and firmware operations.

## Risks
This is ABI-sensitive protocol material: structure packing, field widths, endian expectations, and numeric constants must match firmware. Some macros perform read-modify-write style assignments or rely on caller-provided lvalues. Flexible/placeholder transaction detail arrays require careful sizing. IOCStatus ranges overlap obsolete aliases and transport-specific meanings, so decoding code must mask `MPI_IOCSTATUS_FLAG_LOG_INFO_AVAILABLE`.

## Test Signals
Compile all Fusion transports against the header, run sparse/endian checks, validate request/reply sizes against firmware specs, exercise SGE construction for 32-bit and 64-bit DMA, decode representative IOCStatus/log-info values, and test reset/doorbell/interrupt paths on supported adapters or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi.h -->
