# Research: subset-b-004254

Grouped research for misc driver files under `sources/distributed-fs/ceph-client/drivers/misc`. Each file section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.c -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.c

## Purpose
`bcm_vk_msg.c` implements the Broadcom Valkyrie misc-device message transport between host user space and the VK card firmware. It synchronizes BAR-advertised message queues, allocates per-open contexts, rewrites user transport IDs into driver-owned message IDs, enqueues host-to-card messages, dequeues card-to-host responses, handles shutdown messages, drains outstanding work on reset or close, and runs heartbeat monitoring.

## Important APIs, Types, and Functions
The public entry points are `bcm_vk_msg_init()`, `bcm_vk_msg_remove()`, `bcm_vk_sync_msgq()`, `bcm_vk_msgq_irqhandler()`, `bcm_vk_open()`, `bcm_vk_read()`, `bcm_vk_write()`, `bcm_vk_poll()`, `bcm_vk_release()`, `bcm_to_h_msg_dequeue()`, `bcm_vk_send_shutdown_msg()`, `bcm_vk_hb_init()`, `bcm_vk_hb_deinit()`, and `bcm_vk_drv_access_ok()`. Queue helpers include `msgq_avail_space()`, `msgq_occupied()`, `msgq_blk_addr()`, `bcm_to_v_msg_enqueue()`, `bcm_to_v_q_doorbell()`, and pending-list helpers. DMA transfer messages use `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()` through each `bcm_vk_wkent`.

## Control Flow
Initialization sets context locks, hash buckets, message-ID bitmap state, and queue locks, then tries to read queue metadata from BAR1. Open allocates a `bcm_vk_ctx` tied to the caller's TGID. Write validates block alignment, copies user message blocks, assigns an internal message ID, optionally converts transfer-buffer user pointers into DMA SGLs, appends in-band SGL data if there is queue space, adds the entry to the host-to-card pending list, writes blocks into the BAR queue, advances `wr_idx`, and rings the doorbell. The IRQ handler schedules work; `bcm_to_h_msg_dequeue()` drains card queues, matches responses by queue and internal message ID, and moves complete entries to the read queue for the owning context. Read returns only responses for the file's context and restores the user's original message ID before copying to user space. Release waits briefly for outstanding DMA, drains both pending queues, frees the context, and sends a last-session shutdown message when appropriate.

## State and Persistence
State is volatile driver memory plus BAR queue indices. Persistent per-device state includes context slots, PID hash lists, pending queues per message channel, a message-ID bitmap, heartbeat counters, and `msgq_inited`. Per-open state tracks PID, queue number, pending response count, pending DMA count, and wait queue. No data persists across driver removal, reset drain, or close.

## Dependencies and Integration Points
The file depends on `bcm_vk.h` for BAR accessors, reset/access state, workqueues, alerts, and device fields; `bcm_vk_msg.h` for message layouts; `bcm_vk_sg.h` for DMA SGL conversion; and Linux misc, poll, list, bitmap, waitqueue, spinlock, mutex, interrupt, timer, and user-copy APIs. It integrates with firmware through BAR0 doorbells, BAR1 queue descriptors, queue memory, and host alert bits.

## Risks and Edge Cases
Queue index corruption is treated as fatal and blocks driver access, but queue sizes are assumed power-of-two because masking is used. `bcm_to_v_msg_enqueue()` returns success after `idx_err`, so callers may not see a low-level enqueue failure after access is blocked. DMA close handling waits at most two seconds and then frees SGL resources even if firmware might still touch buffers. `bcm_vk_write()` trusts message layout enough to locate `_vk_data` from `size` and plane count after only limited bounds checks. PID translation assumes the PID is packed in `arg` with a fixed mask. Heartbeat detection intentionally uses relaxed timing but may block access on repeated unchanged uptime reads.

## Test Signals
Useful tests include open/write/read/poll round trips with multiple contexts and queues, message-ID wrap and overflow, short read buffer `-EMSGSIZE`, DMA upload/download with multiple planes, queue-full retry returning `-EAGAIN`, reset drain while responses are pending, last-session shutdown emission, invalid BAR queue metadata, heartbeat loss alerting, and close while DMA is outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.h -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.h

## Purpose
`bcm_vk_msg.h` defines the host/card message-queue ABI and in-kernel bookkeeping structures used by the Broadcom VK misc-device transport.

## Important APIs, Types, and Functions
Key wire-facing structures are `struct bcm_vk_msgq`, the BAR1 queue descriptor, and `struct vk_msg_blk`, the fixed 16-byte message unit. Driver-side structures include `struct bcm_vk_sync_qinfo`, `struct bcm_vk_ctx`, `struct bcm_vk_wkent`, `struct bcm_vk_qs_cnts`, and `struct bcm_vk_msg_chan`. Constants define queue counts, block size, transport ID fields, function IDs (`VK_FID_TRANS_BUF`, `VK_FID_SHUTDOWN`, `VK_FID_INIT`), command masks, context limits, PID hash size, BAR segment sizing, and shutdown types.

## Control Flow
The header supports the lifecycle implemented in `bcm_vk_msg.c`: synchronize queue descriptors into `bcm_vk_sync_qinfo`, allocate a context for each open file, wrap a user request in `bcm_vk_wkent`, track it on a channel pending list, attach DMA SGL state when needed, and complete it when a matching response arrives.

## State and Persistence
The structures are runtime-only and persist only for the lifetime of a VK device or file descriptor. `bcm_vk_ctx` tracks per-open counters and wait queues; `bcm_vk_wkent` owns the copied outbound message, optional inbound response, DMA descriptors, and original user message ID; channel state owns queue locks and per-priority pending lists.

## Dependencies and Integration Points
The header includes the VK UAPI header and `bcm_vk_sg.h`. It is consumed by the VK core, message transport, and SGL code. `struct vk_msg_blk` is an ABI boundary with firmware and user space, so its size and field interpretation are integration-critical.

## Risks and Edge Cases
The flexible-array `bcm_vk_wkent` is sized dynamically by callers and depends on correct `to_v_blks` accounting, especially when in-band SGL blocks are appended. Queue count constants distinguish maximum allocated arrays from firmware-advertised usable queues. Transport IDs combine queue and message ID in one field, so helper use must be consistent.

## Test Signals
Compile-time checks should preserve `sizeof(struct vk_msg_blk) == 16` and array bounds. Runtime tests should confirm queue selection fallback, internal/user message ID remapping, context accounting, and shutdown message encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.c -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.c

## Purpose
`bcm_vk_sg.c` converts user-space buffers described in VK messages into DMA-mapped scatter-gather lists that firmware can consume, and frees those mappings when a request completes or is drained.

## Important APIs, Types, and Functions
The public APIs are `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()`. Internal helpers `bcm_vk_dma_alloc()` and `bcm_vk_dma_free()` pin user pages, allocate a coherent SGL buffer, map pages with `dma_map_page()`, coalesce physically contiguous mappings up to `BCM_VK_MAX_SGL_CHUNK` (16 MiB), write firmware `_vk_data` entries, and unmap/free resources.

## Control Flow
For each non-empty `_vk_data`, allocation reads the packed user pointer, calculates page span and first-page offset, allocates a page-pointer array, pins pages with write access for device-to-host transfers, allocates coherent memory for the firmware SGL, maps pages, compresses contiguous DMA ranges, and replaces the original user pointer and size with the DMA address and SGL byte size. Public allocation rolls back already completed planes on failure. Free walks all populated DMA descriptors, unmaps each SGL range, frees coherent memory, puts pinned pages, frees the page array, and clears `sglist`.

## State and Persistence
State lives in caller-owned `struct bcm_vk_dma` arrays. Each descriptor owns pinned pages, a coherent SGL buffer, DMA handle, length, mapping direction, and page count. There is no persistent module state.

## Dependencies and Integration Points
The file depends on Linux DMA mapping, GUP, page, vmalloc/slab helpers, unaligned accessors, VK UAPI `_vk_data` layout, and `bcm_vk_msg.c` transfer-buffer handling. Firmware sees the generated little-endian SGL header and entries through the DMA address stored back into `_vk_data`.

## Risks and Edge Cases
Failure paths inside `bcm_vk_dma_alloc()` can leak pinned pages or mappings if coherent allocation or a later page mapping fails before `dma->sglist` is established for outer cleanup. `get_user_pages_fast()` pinning semantics require careful direction handling and dirty-page expectations for `DMA_FROM_DEVICE`. The SGL allocation assumes one entry per page is enough before coalescing. Zero size/address pairs are treated as no-op planes, while half-empty pairs are errors.

## Test Signals
Exercise aligned and unaligned buffers, multi-page buffers, physically contiguous coalescing, four-plane transfers, zero planes, invalid half-empty descriptors, GUP failure, DMA mapping failure fault injection, and free-after-partial-allocation paths with page-pin leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.h -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.h

## Purpose
`bcm_vk_sg.h` declares the VK scatter-gather DMA descriptor format and public allocation/free APIs used by transfer-buffer messages.

## Important APIs, Types, and Functions
`struct bcm_vk_dma` records pinned user pages, coherent SGL memory, DMA handle, SGL length, and direction. `struct _vk_data` is the packed message payload item containing a byte size and 64-bit address. The exported declarations are `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()`. SGL constants describe the firmware list header: number of SG entries, total size, and first `_vk_data` entry offset.

## Control Flow
Message code passes an array of `_vk_data` items and matching `bcm_vk_dma` slots to `bcm_vk_sg_alloc()`. On success the `_vk_data` array has been rewritten from user buffers to firmware-visible SGL descriptors; later `bcm_vk_sg_free()` releases all populated DMA slots.

## State and Persistence
The header defines transient state only. `bcm_vk_dma` contents are owned by a pending work entry and should be freed exactly once after firmware response, drain, or error cleanup.

## Dependencies and Integration Points
It depends on Linux DMA mapping types and is included by `bcm_vk_msg.h`, `bcm_vk_msg.c`, and `bcm_vk_sg.c`. The packed `_vk_data` layout is shared with the VK UAPI message protocol and firmware SGL parser.

## Risks and Edge Cases
Because `_vk_data.address` is rewritten in place, callers must not expect the original user pointer after successful allocation. The SGL header is documented as little-endian `u32` words, but the implementation writes native `u32` values. Ownership and cleanup rely on `sglist != NULL`.

## Test Signals
Validate SGL header words, packed `_vk_data` size/alignment, allocation/free API use for every transfer command path, and cleanup idempotence for empty descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_tty.c -->
# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_tty.c

## Purpose
`bcm_vk_tty.c` exposes VK firmware TTY channels as Linux TTY devices backed by BAR1 circular buffers and BAR0 doorbells/interrupts.

## Important APIs, Types, and Functions
Public integration points are `bcm_vk_tty_init()`, `bcm_vk_tty_exit()`, `bcm_vk_tty_irqhandler()`, `bcm_vk_tty_terminate_tty_user()`, and `bcm_vk_tty_wq_exit()`. TTY operations are `bcm_vk_tty_open()`, `bcm_vk_tty_close()`, `bcm_vk_tty_write()`, and `bcm_vk_tty_write_room()`. `bcm_vk_tty_wq_handler()` drains firmware-to-host buffers into the tty flip buffer, while `bcm_vk_tty_poll()` provides timer polling when IRQ support is not enabled.

## Control Flow
Initialization allocates a dynamic raw tty driver, registers `BCM_VK_NUM_TTY` ports, and creates a single-thread workqueue. Open validates channel readiness from `BAR_CARD_STATUS`, records per-channel BAR offsets, snapshots buffer sizes and indices, and starts a poll timer on first open. The work handler checks card status, skips closed channels, reads firmware `wr` offsets, copies bytes from the `from` circular buffer into the tty flip buffer until the shadow `rd` catches up, pushes the flip buffer, and writes the new read index back to BAR1. TTY writes copy each byte into the `to` circular buffer, advance the shadow write index with wraparound, update BAR1, and ring a TTY doorbell.

## State and Persistence
Per-channel state is stored in `vk->tty[]`: open flag, owning PID, BAR offsets, buffer sizes, shadow read/write indices, and tty port. The timer and workqueue live for the device. State is volatile and reset on close/remove.

## Dependencies and Integration Points
The file depends on Linux TTY core, flip buffers, timers, workqueues, signal delivery, and VK BAR access helpers. It integrates with firmware through fixed BAR1 channel offsets, `BAR_CARD_STATUS` readiness bits, BAR1 circular-buffer registers, and a BAR0 TTY doorbell.

## Risks and Edge Cases
`bcm_vk_tty_write()` does not check available circular-buffer space and can overwrite unread firmware data if user space writes more than firmware has consumed; `write_room()` simply returns `to_size - 1`. The poll timer is device-wide but is deleted on the last close according to the current tty's count, which can be fragile across multiple channels. `kill_pid(find_vpid(pid), SIGKILL, 1)` assumes recorded PIDs are still meaningful. Invalid firmware write offsets are logged but do not close the TTY.

## Test Signals
Test open refusal when channel readiness is absent, byte ordering through both circular buffers, wraparound reads and writes, multiple TTY channels, timer and IRQ-driven receive paths, close/remove races with pending work, and large user writes that exceed ring capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bh1770glc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/bh1770glc.c

## Purpose
`bh1770glc.c` is an I2C driver for ROHM BH1770GLC and OSRAM SFH7770 combined ambient-light and proximity sensors. It powers the chip, detects the variant, exposes lux and proximity controls through sysfs, handles runtime/system PM, and processes sensor interrupts.

## Important APIs, Types, and Functions
The central state is `struct bh1770_chip`, containing platform data, regulators, mutex, waitqueue, IRQ/work state, lux calibration/rate/threshold fields, and proximity threshold/rate/persistence fields. Probe/remove are `bh1770_probe()` and `bh1770_remove()`. PM callbacks are `bh1770_suspend()`, `bh1770_resume()`, `bh1770_runtime_suspend()`, and `bh1770_runtime_resume()`. Device control helpers include `bh1770_chip_on()`, `bh1770_chip_off()`, `bh1770_detect()`, `bh1770_lux_rate()`, `bh1770_lux_update_thresholds()`, `bh1770_lux_read_result()`, `bh1770_prox_mode_control()`, and `bh1770_prox_read_result()`. `bh1770_irq()` is the threaded IRQ handler.

## Control Flow
Probe allocates state, requires platform data, initializes defaults, gets and temporarily enables regulators, detects manufacturer/part, starts the chip, enables runtime PM, computes correction factors, creates sysfs attributes, requests a threaded level/falling IRQ, then disables regulators for idle. Writing `power_state` resumes runtime PM, configures lux rate/interrupts, primes thresholds, waits for the first ALS result, and applies proximity mode if enabled. IRQ handling reads ALS/proximity status, acknowledges by reading interrupt control, updates raw lux and wakes waiters, temporarily disables interrupt logic, notifies sysfs on lux/proximity changes, calls proximity filtering, restores interrupt enables, and schedules delayed work to synthesize a missing no-proximity transition.

## State and Persistence
All state is in memory. Runtime PM controls regulator state and chip register programming. Lux correction combines platform glass attenuation, chip factor, and sysfs calibration. Proximity state tracks enable refcount, persistence counter, adjusted result, hardware threshold, absolute threshold, and separate rates above/below threshold. Sysfs writes persist only until driver removal.

## Dependencies and Integration Points
The driver depends on I2C SMBus operations, regulator bulk APIs, platform data from `linux/platform_data/bh1770glc.h`, sysfs device attributes, threaded IRQs, delayed work, waitqueues, and runtime PM. It does not use the modern IIO subsystem; user space consumes sensor values through legacy sysfs names such as `lux0_input` and `prox0_raw`.

## Risks and Edge Cases
Many I2C writes during mode changes ignore individual return values. Some sysfs setters, including proximity persistence and absolute threshold, update state without taking `chip->mutex`. `bh1770_lux_read_result()` ignores the return from `bh1770_lux_get_result()` before converting cached raw data. Proximity readings are suppressed above a fixed lux raw limit, which may hide real near events under bright light. Probe powers on, enables runtime PM, and then disables regulators manually, so PM state must remain consistent.

## Test Signals
Validation should cover probe with both manufacturer IDs, missing platform data, regulator failures, runtime suspend/resume, system suspend/resume with enabled sensors, lux wait timeout, threshold sysfs updates while powered off/on, proximity persistence filtering, IRQ notification paths, delayed no-proximity work, and calibration values that would produce zero correction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/bh1770glc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/c2port/Kconfig

## Purpose
`c2port/Kconfig` declares build options for Silicon Labs C2 port support and the Eurotech Duramar 2150 board adapter.

## Important APIs, Types, and Functions
`menuconfig C2PORT` is a tristate option for the core C2 programming class and builds the `c2port_core` module. `config C2PORT_DURAMAR_2150` is a tristate child option, depends on `X86`, and builds the Duramar-specific client module.

## Control Flow
The child option is visible only inside the `if C2PORT` block. Enabling the core makes the exported C2 registration API and sysfs class available; enabling the Duramar option adds an I/O-port backend that registers one C2 device.

## State and Persistence
The file stores configuration metadata only. Runtime state is created by `core.c` and `c2port-duramar2150.c` when the selected objects are built and loaded.

## Dependencies and Integration Points
The Kconfig integrates `drivers/misc/c2port` into the kernel configuration system. The board adapter's `depends on X86` reflects direct use of legacy x86 I/O ports.

## Risks and Edge Cases
The help text uses old wording and assumes module names. The core option does not select a concrete backend, so enabling only `C2PORT` creates infrastructure but no board device.

## Test Signals
Configuration tests should build the core built-in and as a module, ensure the Duramar option is hidden without `C2PORT` or non-X86, and confirm module names match Makefile output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/c2port/Makefile

## Purpose
`c2port/Makefile` maps C2 Kconfig symbols to object files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_C2PORT) += core.o` builds the generic C2 class and sysfs programming engine. `obj-$(CONFIG_C2PORT_DURAMAR_2150) += c2port-duramar2150.o` builds the Duramar I/O-port backend.

## Control Flow
Kbuild includes each object when the corresponding symbol is `y` or `m`. The core exports `c2port_device_register()` and `c2port_device_unregister()` for board/client modules.

## State and Persistence
The file has no runtime state. It controls which modules or built-in objects exist.

## Dependencies and Integration Points
It integrates with the Linux Kbuild system and the Kconfig symbols in the same directory.

## Risks and Edge Cases
If the Duramar object is built without a loadable or built-in core, symbol resolution would fail; the Kconfig nesting normally prevents that.

## Test Signals
Build matrix coverage should verify `CONFIG_C2PORT=y/m` and `CONFIG_C2PORT_DURAMAR_2150=y/m` combinations produce the expected objects and exported-symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/c2port-duramar2150.c -->
# sources/distributed-fs/ceph-client/drivers/misc/c2port/c2port-duramar2150.c

## Purpose
`c2port-duramar2150.c` is the board-specific Silicon Labs C2 backend for the Eurotech Duramar 2150. It bit-bangs C2D and C2CK through legacy I/O ports and registers one C2 device with the generic core.

## Important APIs, Types, and Functions
The backend implements `struct c2port_ops`: `duramar2150_c2port_access()`, `duramar2150_c2port_c2d_dir()`, `duramar2150_c2port_c2d_get()`, `duramar2150_c2port_c2d_set()`, and `duramar2150_c2port_c2ck_set()`. Module entry/exit are `duramar2150_c2port_init()` and `duramar2150_c2port_exit()`. The board advertises 30 flash blocks of 512 bytes.

## Control Flow
Module init reserves I/O ports `0x325..0x326`, then calls `c2port_device_register("uc", &duramar2150_c2port_ops, NULL)`. Core sysfs operations later call the ops while bit-banging C2 transactions. Exit sets both lines to input/high impedance through `access(..., 0)`, unregisters the device, and releases the I/O region.

## State and Persistence
Global state is `duramar2150_c2port_dev` and `update_lock`, which serializes read-modify-write updates to the data and direction ports. Hardware line state persists on the board until changed, but the driver tries to leave lines as inputs on unload.

## Dependencies and Integration Points
The file depends on x86-style `inb()`/`outb()`, `request_region()`, `linux/c2port.h`, and the C2 core exported registration API. It integrates directly with fixed board I/O-port wiring.

## Risks and Edge Cases
The fixed I/O port addresses are board-specific and unsafe on the wrong platform. `c2d_get()` reads without `update_lock`, so concurrent line updates can race with reads. Init failure after registration is handled, but no hardware identity is verified before exposing flash programming sysfs.

## Test Signals
Tests should verify region conflict returns `-EBUSY`, registration failure releases the region, unload leaves direction bits as input, and C2 core read/write/reset sysfs operations produce expected C2D/C2CK transitions on the board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/c2port-duramar2150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/core.c -->
# sources/distributed-fs/ceph-client/drivers/misc/c2port/core.c

## Purpose
`c2port/core.c` implements the generic Silicon Labs C2 programming class. It bit-bangs the C2 protocol through backend-provided GPIO/I/O operations and exposes device identification and flash read/write/erase controls through sysfs.

## Important APIs, Types, and Functions
Exported APIs are `c2port_device_register()` and `c2port_device_unregister()`. Low-level protocol helpers include `c2port_reset()`, `c2port_strobe_ck()`, `c2port_write_ar()`, `c2port_read_ar()`, `c2port_write_dr()`, `c2port_read_dr()`, `c2port_poll_in_busy()`, and `c2port_poll_out_ready()`. Sysfs attributes cover `name`, `flash_blocks_num`, `flash_block_size`, `flash_size`, `access`, `reset`, `dev_id`, `rev_id`, `flash_access`, `flash_erase`, and binary `flash_data`.

## Control Flow
Backends register a `struct c2port_device` with line-control ops and flash geometry. The core allocates an ID, creates `c2portN` under a class whose dev_groups expose the sysfs API, and disables access by default. Users must enable `access`, optionally enable `flash_access` through the two-key FPCTL sequence, then use `flash_data` reads/writes or `flash_erase`. Flash block operations select `C2PORT_FPDAT`, send a command, poll busy/ready status, check `C2PORT_COMMAND_OK`, transfer address/length bytes, and then stream up to 128 bytes per sysfs binary operation.

## State and Persistence
Global state is the C2 class and IDR. Per-device state includes ID, name, backend ops, mutex, access flag, flash access flag, and device object. Flash writes/erases persist in the target microcontroller; driver state itself is volatile.

## Dependencies and Integration Points
The core depends on `linux/c2port.h`, class/device/sysfs infrastructure, IDR, delays, local IRQ disabling for sub-5us C2 timing, and backend callbacks for `access`, `c2d_dir`, `c2d_get`, `c2d_set`, and `c2ck_set`.

## Risks and Edge Cases
The C2 bit timings use `udelay()` and local IRQ disabling but are still sensitive to CPU/platform behavior. Sysfs flash writes can permanently alter target firmware and are guarded only by `access`/`flash_access`. Addressing sends only high/low bytes, so large flash geometries would need review. Some comments note missing status checks before access sequences. `devdata` is accepted by `c2port_device_register()` but not stored.

## Test Signals
Validate class creation/destruction, ID allocation/removal, sysfs permission and gating behavior, device/revision reads, flash-access enable sequence, erase arming sequence, 128-byte chunk boundaries, offset at end-of-flash, backend timeout handling, and concurrent sysfs access serialization by the per-device mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/c2port/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/Kconfig

## Purpose
`cardreader/Kconfig` declares misc-driver options for Alcor PCIe card readers, Realtek PCIe card readers, and Realtek USB card readers.

## Important APIs, Types, and Functions
`MISC_ALCOR_PCI` depends on PCI and selects MFD core for AU6601/AU6621/AU6625-style devices. `MISC_RTSX_PCI` depends on PCI and selects MFD core for Realtek PCIe readers including RTS5209, RTS5227/5228/5229, RTS5249/524A, RTS525A, RTL8411, RTS5260/5261/5264. `MISC_RTSX_USB` depends on USB and selects MFD core for USB Realtek readers.

## Control Flow
Enabling these symbols causes Kbuild to compile parent cardreader MFD drivers that create child devices for SD/MMC and MemoryStick functions.

## State and Persistence
The file stores build-time configuration only. Runtime state belongs to the selected PCI/USB parent drivers and their child function drivers.

## Dependencies and Integration Points
It integrates with the Linux config system, PCI/USB subsystems, and MFD core. Help text describes card formats supported by the resulting drivers.

## Risks and Edge Cases
The Alcor help text says "This supports for", and its list omits AU6625 despite the PCI driver including it. Enabling these parent drivers still requires relevant child drivers for card protocols.

## Test Signals
Kconfig tests should confirm dependency visibility, `select MFD_CORE`, module builds, and that help text/device lists stay synchronized with PCI/USB ID tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/Makefile

## Purpose
`cardreader/Makefile` maps cardreader Kconfig symbols to build objects and assembles the Realtek PCIe parent driver from common and chip-specific sources.

## Important APIs, Types, and Functions
`obj-$(CONFIG_MISC_ALCOR_PCI) += alcor_pci.o`; `obj-$(CONFIG_MISC_RTSX_USB) += rtsx_usb.o`; `obj-$(CONFIG_MISC_RTSX_PCI) += rtsx_pci.o`. `rtsx_pci-objs` includes `rtsx_pcr.o` plus chip files `rts5209.o`, `rts5229.o`, `rtl8411.o`, `rts5227.o`, `rts5249.o`, `rts5260.o`, `rts5261.o`, `rts5228.o`, and `rts5264.o`.

## Control Flow
Kbuild links the chip parameter files into one `rtsx_pci` module/object so the common PCI core can select chip-specific init routines by PCI ID.

## State and Persistence
The file has no runtime state.

## Dependencies and Integration Points
It integrates the common Realtek PCI code with per-chip operation tables and ensures the MFD parent can support all configured PCI IDs.

## Risks and Edge Cases
Adding a new Realtek chip requires updating this object list as well as IDs and init dispatch in the common code. Missing a chip object would produce unresolved symbols or unsupported IDs.

## Test Signals
Build tests should verify `MISC_RTSX_PCI=m/y` links every listed chip file and that disabling the symbol excludes the aggregate object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/alcor_pci.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/alcor_pci.c

## Purpose
`alcor_pci.c` is the PCI parent/MFD driver for Alcor Micro AU6601, AU6621, and AU6625 card readers. It maps PCI BAR registers, provides exported register access helpers, configures DMA, and creates SD/MMC and MemoryStick child devices.

## Important APIs, Types, and Functions
Exported helpers are `alcor_write8()`, `alcor_write16()`, `alcor_write32()`, `alcor_write32be()`, `alcor_read8()`, `alcor_read32()`, and `alcor_read32be()`. Driver lifecycle is `alcor_pci_probe()` and `alcor_pci_remove()`, with sleep PM callbacks `alcor_suspend()` and `alcor_resume()`. `alcor_pci_cells[]` declares child MFD cells for SDMMC and MS functions. PCI IDs select `struct alcor_dev_cfg` with a DMA capability flag.

## Control Flow
Probe enables the PCI device with managed helpers, allocates private state and an IDA ID, requests BAR regions, verifies BAR0 is memory, maps it, disables SD/MS interrupts, sets a 32-bit SDMA mask, enables bus mastering, stores driver data, passes the private structure as platform data to each child cell, adds MFD children, and disables PCIe L0s/L1 link states. Remove tears down MFD children, frees the ID, clears bus mastering and driver data. Resume disables L0s/L1 again.

## State and Persistence
Per-device state includes PCI device pointer, parent bridge pointer, device pointer, config pointer, IRQ, mapped BAR base, and IDA ID. Register state lives in hardware; driver state is volatile.

## Dependencies and Integration Points
The driver depends on PCI managed resource APIs, MFD core, DMA mask setup, `linux/alcor_pci.h` constants/shared structures, and child platform drivers that consume the exported MMIO helpers and platform data.

## Risks and Edge Cases
`alcor_pci_cells` is a global array whose `platform_data` and `pdata_size` are rewritten per probe; concurrent multiple devices could race or share stale platform data. The code disables link power states unconditionally, which may affect power consumption. DMA mask failure aborts even for configs with `.dma = 0`. The suspend callback does nothing beyond resume re-disabling link states.

## Test Signals
Test all PCI IDs, multi-device probe/remove, BAR type rejection, DMA-mask failure, MFD child creation failure cleanup, exported register helper endianness, interrupt disable at probe, and link-state policy after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/alcor_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtl8411.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtl8411.c

## Purpose
`rtl8411.c` supplies chip-specific operation tables, power sequencing, card-detect handling, voltage switching, LED control, and pull-control tables for Realtek RTL8411, RTL8411B, and RTL8402 PCIe card readers.

## Important APIs, Types, and Functions
Public init functions are `rtl8411_init_params()`, `rtl8411b_init_params()`, and `rtl8402_init_params()`. Important helpers include `rtl8411_get_ic_version()`, `rtl8411b_is_qfn48()`, vendor-setting fetchers, `rtl8411_extra_init_hw()`, `rtl8411b_extra_init_hw()`, `rtl8411_card_power_on()`, `rtl8411_card_power_off()`, `rtl8411_switch_output_voltage()`, `rtl8402_switch_output_voltage()`, `rtl8411_cd_deglitch()`, and `rtl8411_conv_clk_and_div_n()`. Three `struct pcr_ops` variants bind these functions to the common `rtsx_pcr` core.

## Control Flow
The common PCI core calls one init function based on PCI ID. Initialization sets capabilities, slot count, drive strength defaults, ASPM policy, clock phases, IC version, ops table, and SD/MS pull tables. Vendor settings are read from PCI config space when valid. Hardware init configures drive selection, card-detect pads, and RTL8411B package-specific pull settings. Card power-on ramps BPP power through partial steps before enabling the LDO. Voltage switching updates drive selection and LDO pad voltage. Card-detect deglitch powers briefly when both SD and MS appear, then enables only the detected slot's interrupt path.

## State and Persistence
State is stored in the shared `struct rtsx_pcr`: capabilities, flags, drive selections, ASPM settings, initial phases, IC version, and pull table pointers. Register writes persist in the chip until reset or power transition.

## Dependencies and Integration Points
The file depends on `linux/rtsx_pci.h`, `rtsx_pcr.h`, PCI config accessors, common register helpers, and the Realtek MFD/card core that invokes `pcr_ops` for power, voltage, LED, clock, and card-detect actions.

## Risks and Edge Cases
Package detection changes pull tables and extra init behavior; wrong package mode can misconfigure pins. Card-detect deglitch temporarily powers hardware and assumes SD/MS existence bits settle after 100 ms. Voltage switching only accepts 3.3V and 1.8V. Vendor settings are ignored if the validity marker fails, leaving defaults.

## Test Signals
Validate RTL8411, RTL8411B QFN48/QFN64, and RTL8402 init paths; vendor config parsing; LED/autoblink; card power ramp; 1.8V/3.3V switching; deglitch with no card, SD, MS, and both-card noise; and clock conversion math used by shared clock code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rtl8411.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5209.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5209.c

## Purpose
`rts5209.c` provides chip-specific parameters and operations for the Realtek RTS5209 PCIe card reader.

## Important APIs, Types, and Functions
The public entry point is `rts5209_init_params()`. Helpers include `rts5209_get_ic_version()`, `rts5209_fetch_vendor_settings()`, `rts5209_extra_init_hw()`, `rts5209_optimize_phy()`, LED/autoblink functions, `rts5209_card_power_on()`, `rts5209_card_power_off()`, `rts5209_switch_output_voltage()`, and `rts5209_force_power_down()`. `rts5209_pcr_ops` connects these to the common core.

## Control Flow
Initialization sets SDR50/SDR104/MMC 8-bit capabilities, two slots, default drive strengths, ASPM configuration, clock phases, IC version, and SD/MS pull tables. Vendor settings can enable MS PMOS and override ASPM and drive strengths. Extra hardware init turns off LED, resets ASPM force state, forces CLKREQ low, sets GPIO direction, and programs SD30 drive selection. Card power-on chooses SD or MS masks when MS PMOS is enabled, performs a partial power step and LDO gate update, delays, then fully powers on. Voltage switching writes SD30 drive selection and PHY tuning for 3.3V or 1.8V.

## State and Persistence
All mutable state is in `struct rtsx_pcr` fields such as flags, drive selections, ASPM settings, phases, ops, and pull tables. Hardware register state persists until chip reset/power transition.

## Dependencies and Integration Points
The file depends on the common Realtek PCI register/PHY command helpers and is linked into the aggregate `rtsx_pci` driver. Child card drivers observe the resulting power, clock, and pull-control behavior through the common core.

## Risks and Edge Cases
MS power behavior changes when `PCR_MS_PMOS` is set from vendor config. Voltage switching returns `-EINVAL` for unsupported values but callers must handle that. Extra init forces CLKREQ low, which can affect platform power behavior. PHY tuning uses hard-coded magic values.

## Test Signals
Test default and vendor-setting init, MS PMOS power paths, SD/MS pull tables, PHY optimization, LED controls, forced power down, voltage switching, and card insertion/removal across both slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5209.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5227.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5227.c

## Purpose
`rts5227.c` supplies chip-specific operations for RTS5227 and RTS522A Realtek PCIe card readers, including drive-strength programming, power sequencing, voltage switching, LTR/L1SS configuration, and OCP defaults.

## Important APIs, Types, and Functions
Public init functions are `rts5227_init_params()` and `rts522a_init_params()`. Shared helpers include `rts5227_fetch_vendor_settings()`, `rts5227_init_from_cfg()`, `rts5227_extra_init_hw()`, `rts5227_optimize_phy()`, `rts5227_card_power_on()`, `rts5227_card_power_off()`, `rts5227_switch_output_voltage()`, and LED/autoblink functions. RTS522A-specific helpers include `rts522a_optimize_phy()`, `rts522a_extra_init_hw()`, `rts522a_switch_output_voltage()`, `rts522a_force_power_down()`, and `rts522a_set_l1off_cfg_sub_d0()`.

## Control Flow
The base init sets SDR50/SDR104 capabilities, two slots, default drive types, ASPM mode, phases, pull tables, PM register, and socket polarity defaults. Vendor config may set RTD3, disable MMC, reverse socket/CD/WP behavior, and drive selections. Extra init applies LTR/OOBS choices, GPIO/ASPM/LDO/LED/OBFF setup, drive-strength commands, PETXCFG polarity, resume and RTD3 policy, force-CLKREQ policy, and PM control. RTS522A builds on the RTS5227 flow with alternative PHY values, extra power-management writes, L1 off substate handling, and OCP interrupt defaults.

## State and Persistence
State is stored in `struct rtsx_pcr`, especially `option`, `hw_param`, flags, phases, register IDs, ops, and pull tables. Register and PHY writes persist in hardware until reset or a later power-management transition.

## Dependencies and Integration Points
The file depends on common `rtsx_pcr` helpers, PCIe capability reads, PHY register access, command batching, and card power/voltage callbacks invoked by the Realtek parent and child card stacks.

## Risks and Edge Cases
Several RTS522A extra-init writes ignore return values from the inherited init and subsequent register writes. Reverse-socket and polarity options influence PETXCFG bits and can break card detect/write-protect if misread. OCP is enabled only for RTS522A init, so base RTS5227 lacks those callbacks. Hard-coded delays and PHY constants are hardware-sensitive.

## Test Signals
Test RTS5227 and RTS522A PCI IDs, vendor config combinations, RTD3 on/off, reverse socket/CD/WP, 1.8V and 3.3V switching, LTR/L1SS transitions with and without card present, OCP interrupt configuration for RTS522A, and card power on/off with inrush delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5227.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.c

## Purpose
`rts5228.c` provides Realtek RTS5228 PCIe card reader operations, including SD-only power sequencing, voltage switching, OCP management, ASPM/L1SS handling, PHY tuning, command stop/reset, and a chip-specific PCI clock switcher.

## Important APIs, Types, and Functions
Public functions are `rts5228_init_params()` and `rts5228_pci_switch_clock()`. Important helpers include `rtsx5228_fetch_vendor_settings()`, `rts5228_optimize_phy()`, `rts5228_force_power_down()`, `rts5228_card_power_on()`, `rts5228_card_power_off()`, `rts5228_switch_output_voltage()`, `rts5228_stop_cmd()`, `rts5228_init_ocp()`, `rts5228_process_ocp()`, `rts5228_set_aspm()`, and `rts5228_set_l1off_cfg_sub_d0()`. `rts5228_pcr_ops` exposes these callbacks.

## Control Flow
Initialization sets one SD slot, SDR50/SDR104 caps, register-mode ASPM, phases, autoload PM register, LTR/L1SS defaults, OCP defaults, and pull tables. Vendor settings may set RTD3, disable MMC, reverse socket, and reverse CD/WP. Extra init enables CD resume, configures L1 substate registers, clock/PM force bits, LED defaults, drive strengths, socket polarity, CLKREQ policy, suspend power bits, RTD3 PME policy, and clears D3 delink. Power-on enables OCP, configures LDO1 softstart/full-on and LDO3318, waits, enables SD outputs, initializes SD timing registers, clears stop/error bits, and selects SD30 timing when high-speed modes are supported. OCP processing powers the SD card off and disables outputs on over-current. Clock switching calculates divider, MCU count, SSC depth, optional VPCLK phase reset, and programs SSC registers.

## State and Persistence
Runtime state is held in `struct rtsx_pcr`: current clock, ASPM enabled flag, OCP status, options, capabilities, phases, drive selections, and ops. Hardware register state persists until changed by power, clock, or PM paths.

## Dependencies and Integration Points
The file depends on `rts5228.h` register definitions, common Realtek PCI command/PHY helpers, PCIe link-control helpers, and the common `rtsx_pcr` dispatch layer. `rts5228_pci_switch_clock()` may be called by the shared clock path for this chip.

## Risks and Edge Cases
`rts5228_enable_aspm()` sets `aspm_enabled` to the desired boolean but still programs force bits using only `aspm_en & 0x02`; platform ASPM policy mismatches can be subtle. Many register writes in power/OCP paths ignore errors. Clock calculation rejects low clocks and `n > 396`, and SSC depth remapping is table-limited. Power-off always switches back to 3.3V before disabling power.

## Test Signals
Test one-slot SD operation, vendor config parsing, power-on/off sequencing, OCP now/ever interrupt handling, clock switching across initial and high-speed modes, double-clock and VPCLK paths, ASPM enable/disable, L1 off substate values with card present/absent, and 1.8V/3.3V voltage switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.h -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.h

## Purpose
`rts5228.h` defines RTS5228-specific register addresses, bit masks, voltage/OCP constants, SSC depth values, and the chip-specific clock-switching prototype.

## Important APIs, Types, and Functions
The header defines autoload registers, VREF/pad controls, SSC depth constants, LDO12/LDO1/DV3318 power and tuning masks, over-current thresholds, PME force control bits, LUN constants, and multiply/divide constants for the clock path. It declares `rts5228_pci_switch_clock()`.

## Control Flow
`rts5228.c` uses these constants to implement extra hardware init, SD power sequencing, voltage switching, OCP setup, force power down, and SSC clock programming.

## State and Persistence
The header has no storage. Constants correspond to persistent hardware registers on the card reader.

## Dependencies and Integration Points
It is included by `rts5228.c` and relies on common Realtek types such as `struct rtsx_pcr` and Linux integer/bool definitions being available from including translation units.

## Risks and Edge Cases
Several macro names preserve vendor spelling, including `RTS5228_SSC_DEPTH_DISALBE`, and bit shifts have tight coupling to register layouts. The header exposes a clock API implemented only by the RTS5228 source.

## Test Signals
Build coverage should ensure all constants remain consistent with users in `rts5228.c`; runtime validation should verify LDO/OCP/SSC register writes match documented masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5228.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5229.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5229.c

## Purpose
`rts5229.c` provides chip-specific operations and parameter defaults for the Realtek RTS5229 PCIe card reader.

## Important APIs, Types, and Functions
The public init function is `rts5229_init_params()`. Helpers include `rts5229_get_ic_version()`, `rts5229_fetch_vendor_settings()`, `rts5229_force_power_down()`, `rts5229_extra_init_hw()`, `rts5229_optimize_phy()`, LED/autoblink functions, `rts5229_card_power_on()`, `rts5229_card_power_off()`, and `rts5229_switch_output_voltage()`. Pull-control tables have separate SD variants for IC version C.

## Control Flow
Initialization sets SDR50/SDR104 caps, two slots, default drive types, ASPM config mode, clock phases, IC version, ops table, version-specific SD pull tables, and MS pull tables. Vendor settings override ASPM and mapped drive strengths. Extra init configures GPIO output, ASPM force defaults, forced CLKREQ, LDO power source, LED shine defaults, and SD30 drive selection. Power-on does partial then full SD power with LDO gate changes. Voltage switching writes SD30 drive selection and PHY tuning for 3.3V or 1.8V.

## State and Persistence
Chip state is held in `struct rtsx_pcr`. Register state persists until reset or later callback execution. There is no module-local mutable state.

## Dependencies and Integration Points
The file depends on common Realtek PCI register helpers, command batching, PHY writes, PCI config reads, and the common `rtsx_pcr` dispatch path.

## Risks and Edge Cases
Only SD power masks are used in power functions despite two advertised slots; MemoryStick behavior is primarily pull-table configuration. IC version C changes SD pull values, so version misread affects signal bias. As with sibling files, hard-coded PHY values and delays are hardware-sensitive.

## Test Signals
Test IC version A/B/C init, vendor setting validity, SD/MS pull tables, power sequencing, LED controls, forced power down, voltage switching, and card operations after resume/reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5229.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5249.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5249.c

## Purpose
`rts5249.c` supplies operation tables and parameter initialization for RTS5249, RTS524A, and RTS525A Realtek PCIe card readers. It covers common power/voltage/LED behavior plus newer autoload/efuse, PHY, LTR/L1SS, RTD3, and OCP handling.

## Important APIs, Types, and Functions
Public init functions are `rts5249_init_params()`, `rts524a_init_params()`, and `rts525a_init_params()`. Shared helpers include `rtsx_base_fetch_vendor_settings()`, `rts5249_extra_init_hw()`, `rts5249_optimize_phy()`, `rtsx_base_card_power_on()`, `rtsx_base_card_power_off()`, `rtsx_base_switch_output_voltage()`, and LED/autoblink functions. Newer-chip helpers include `rts52xa_force_power_down()`, `rts52xa_save_content_to_autoload_space()`, `rts524a_write_phy()`, `rts524a_read_phy()`, `rts524a_optimize_phy()`, `rts524a_extra_init_hw()`, `rts5250_set_l1off_cfg_sub_d0()`, `rts525a_card_power_on()`, `rts525a_switch_output_voltage()`, `rts525a_optimize_phy()`, and `rts525a_extra_init_hw()`.

## Control Flow
Base init sets two slots, SDR50/SDR104 caps, drive defaults, ASPM config mode, clock phases, IC version, pull tables, PM register, and LTR defaults. Vendor settings may enable RTD3 for 524A/525A, disable MMC, reverse socket/CD/WP, and override drive strengths. Extra init optionally copies efuse/BIOS content into autoload space, resets L1SUB, GPIO, ASPM, LDO source, LED and drive settings, configures PETXCFG polarity, sends the command batch, applies resume/PME/RTD3 policy, CLKREQ policy, clears PM control bits, and powers efuse off. 524A and 525A replace selected PHY, power, voltage, force-power-down, and L1-off operations.

## State and Persistence
State lives in `struct rtsx_pcr`, including ops, options, hardware OCP settings, phases, drive selections, flags, and register IDs. Efuse/autoload writes and PHY/register programming persist in hardware until reset or power-cycle.

## Dependencies and Integration Points
The file depends on Realtek common PCI helpers, PHY read/write hooks, PCI config space access, chip ID macros, and the aggregate `rtsx_pci` parent driver. It is the bridge between common card logic and several related chip generations.

## Risks and Edge Cases
Efuse/autoload copy loops poll up to 1024 iterations without explicit timeout errors. `rts5249_extra_init_hw()` sends a command batch without checking the return before subsequent direct writes. 524A address translation changes PHY addressing for high-bit addresses. 525A voltage control uses LDO registers instead of the base PHY path. Version-specific PHY constants are numerous and difficult to validate without hardware.

## Test Signals
Test all three init variants, vendor config parsing, efuse/autoload paths with BIOS flag set/clear, RTD3 on/off, voltage switching, OCP interrupt configuration for 524A/525A, L1 off behavior with card present/absent, PHY read/write address translation, and suspend/resume force-power-down behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5249.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.c -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.c

## Purpose
`rts5260.c` provides chip-specific operations and defaults for the Realtek RTS5260 PCIe card reader, with emphasis on SD power sequencing, voltage switching, over-current detection, L1 power-saving setup, and newer register-level PM behavior.

## Important APIs, Types, and Functions
The public init function is `rts5260_init_params()`. Important helpers include `rtsx_base_fetch_vendor_settings()`, `rts5260_fill_driving()`, LED/autoblink functions, `sd_set_sample_push_timing_sd30()`, `rts5260_card_power_on()`, `rts5260_switch_output_voltage()`, `rts5260_stop_cmd()`, `rts5260_card_power_off()`, OCP helpers (`rts5260_init_ocp()`, `rts5260_enable_ocp()`, `rts5260_disable_ocp()`, `rts5260_get_ocpstat()`, `rts5260_clear_ocpstat()`, `rts5260_process_ocp()`), `rts5260_init_hw()`, `rts5260_pwr_saving_setting()`, `rts5260_extra_init_hw()`, and `rts5260_set_l1off_cfg_sub_d0()`.

## Control Flow
Initialization sets two slots, SDR50/SDR104 caps, register-mode ASPM, default drive strengths, phases, pull tables, PM register, ops, LTR/L1SS defaults, and OCP thresholds/glitch masks. Vendor settings may disable MMC and mark reverse socket. Extra init adjusts clock/SSC defaults, applies L1 power-saving policy, disables MIMO/MDIO behavior, tunes SDVCC, sets PCLK mode, runs hardware init, applies force-CLKREQ, and clears PM control. Power-on enables OCP, selects/tunes DV331812 and DVCC, powers SDVDD, waits, optionally sets SD30 timing, initializes SD registers, clears stop/error, and disables infinite pre-read/write mode. OCP processing checks both SDVCC and DV3318 status, powers the card off, disables outputs, clears status, and resets cached status.

## State and Persistence
State is held in `struct rtsx_pcr`: options, OCP status/status2, hardware parameters, pull tables, drive selections, phases, PM register, and ops. Hardware state persists through direct register writes until later callbacks or reset.

## Dependencies and Integration Points
The file depends on `rts5260.h`, common Realtek PCI helpers, L1/LTR helper functions, over-current helpers, and the parent Realtek PCI driver that dispatches through `pcr_ops`.

## Risks and Edge Cases
`rts5260_card_power_off()` overwrites `err` with the second register write, potentially losing the first error. Many power-saving and OCP setup writes ignore errors. OCP handling clears both status banks but `pcr_ops.get_ocpstat` exposes only the first bank; the second is handled privately. Power saving depends on option flags from common code and vendor settings.

## Test Signals
Test init defaults, vendor setting parsing, SD power on/off, 1.8V/3.3V switching, SD30 sample/push timing, OCP status from both banks, stop command DMA reset, L1/L1.1/L1.2 power-saving modes, card-present-sensitive L1 off bits, and error propagation in power-off paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.h -->
# sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.h

## Purpose
`rts5260.h` defines RTS5260-specific power and over-current register constants used by `rts5260.c`.

## Important APIs, Types, and Functions
The header defines control registers and bit masks for DVCC, DVIO, and DV331812 rails, including OCP enable bits, threshold masks, power-on bits, current-limit clear bits, rail selection, and discrete threshold encodings. It has no function declarations.

## Control Flow
`rts5260.c` uses these constants during OCP initialization, SD power-on, voltage switching, and OCP threshold configuration.

## State and Persistence
There is no storage. Constants map to persistent hardware register fields on the RTS5260 card reader.

## Dependencies and Integration Points
The header is included only by the RTS5260 chip implementation and relies on common Realtek register names supplied elsewhere for surrounding code.

## Risks and Edge Cases
Threshold macros encode hardware-specific current levels as bit patterns without type checking. Any register map mismatch would affect power safety and OCP behavior.

## Test Signals
Build coverage should catch renamed constants; hardware tests should confirm programmed DVCC/DVIO/DV331812 thresholds and power bits match expected rail behavior under normal and over-current conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/cardreader/rts5260.h -->
