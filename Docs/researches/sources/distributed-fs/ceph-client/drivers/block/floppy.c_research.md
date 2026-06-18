# sources/distributed-fs/ceph-client/drivers/block/floppy.c

## Purpose
Implements the legacy PC floppy block driver for Linux. It probes floppy disk controllers, registers `/dev/fd*` disks, translates block-layer requests into FDC commands, handles DMA or pseudo-DMA transfer setup, maintains media-change and geometry state, exposes the historical floppy ioctl ABI, and supports optional raw FDC commands and 32-bit compatibility ioctls.

## Important APIs, Types, And Functions
- Global drive/controller state is held in `drive_params[]`, `drive_state[]`, `write_errors[]`, `fdc_state[]`, `current_type[]`, `floppy_sizes[]`, `disks[][]`, `tag_sets[]`, and the shared track buffer variables `floppy_track_buffer`, `buffer_track`, `buffer_drive`, `buffer_min`, and `buffer_max`.
- `floppy_type[]` describes built-in media geometries, including sector count, heads, tracks, stretch/side-swap/sector-base behavior, data rate, gaps, and printable format names.
- `lock_fdc()`, `unlock_fdc()`, `set_fdc()`, `set_dor()`, `floppy_grab_irq_and_dma()`, and `floppy_release_irq_and_dma()` serialize and manage FDC, IRQ, DMA, IO-port, and motor resources.
- `floppy_interrupt()`, `result()`, `output_byte()`, `reset_fdc()`, `fdc_specify()`, `fdc_configure()`, `fdc_dtr()`, and `perpendicular_mode()` implement low-level command, result, reset, and controller-configuration sequencing.
- The continuation tables `rw_cont`, `format_cont`, `poll_cont`, `reset_cont`, `raw_cmd_cont`, `wakeup_cont`, and `intr_cont` drive the asynchronous state machine through interrupt, retry, error, and completion callbacks.
- `floppy_queue_rq()`, `process_fd_request()`, `redo_fd_request()`, `make_raw_rw_request()`, `rw_interrupt()`, `copy_buffer()`, and `request_done()` are the main blk-mq request path.
- `fd_locked_ioctl()`, `set_geometry()`, `do_format()`, `user_reset_fdc()`, `floppy_raw_cmd_ioctl()`, and the `CONFIG_COMPAT` helpers implement user-visible control operations.
- `floppy_open()`, `floppy_release()`, `floppy_check_events()`, `floppy_revalidate()`, `fd_getgeo()`, and `floppy_fops` integrate the driver with block-device lifetime and media-change handling.
- `do_floppy_init()`, `floppy_init()`, `floppy_probe()`, `floppy_alloc_disk()`, and module init/exit code register the driver, devices, platform nodes, timers, workqueue, and lazy type-minor disks.

## Control Flow
Initialization allocates one tag set and default disk per possible drive, registers the floppy major with a probe callback, initializes controller state, claims IRQ/DMA/IO regions, resets each FDC, detects controller version with `get_fdc_version()`, reads CMOS drive types in `config_types()`, and registers platform devices plus default disks for available drives. Non-module builds schedule this initialization asynchronously so boot is not blocked.

Open-time flow serializes with `floppy_mutex` and `open_lock`, rejects aliasing through `opened_disk[]`, increments the per-drive reference count, allocates a DMA-safe track buffer on first open, sets the selected minor/type, revalidates media unless opened nonblocking, and enforces write protection for write opens. Release decrements `fd_ref` and clears `opened_disk[]` when the last opener leaves.

Request flow starts in `floppy_queue_rq()`. The blk-mq request is queued on `floppy_reqs`, FDC ownership is acquired through `fdc_busy`, a timeout is armed, and `process_fd_request()` schedules `redo_fd_request()` on the ordered floppy workqueue. The redo path picks the next request, starts or selects the motor, handles disk-change/fake-change failure, autodetects a format when needed, builds a `default_raw_cmd`, and schedules `floppy_start()`. The hardware state machine then performs selection delay, data-rate setup, optional seek/recalibration, DMA setup, FDC command output, interrupt completion, error interpretation, buffer copying, retry/reset decisions, and request completion.

Read/write transfer construction is concentrated in `make_raw_rw_request()`. It maps `blk_rq_pos()` to track, head, sector, and in-sector offsets according to the current floppy geometry; handles stretched, swapped-side, sector-base, and 2M special cases; chooses read or write commands; uses the track buffer for read caching and partial-sector read-modify-write; computes DMA length aligned to physical sector size; and applies the pseudo-DMA multi-track workaround before returning whether the request is already satisfied, failed, or must be submitted to hardware.

Media-change and revalidation flow uses both hardware disk-change lines and software flags. `disk_change()` updates `FD_DISK_CHANGED`, `FD_VERIFY`, `FD_DISK_NEWCHANGE`, `current_type[]`, and size defaults. `floppy_check_events()` reports `DISK_EVENT_MEDIA_CHANGE` from those flags, periodic polls, `fake_change`, or missing geometry. `floppy_revalidate()` clears stale state, invalidates the track buffer, increments generation on real changes, optionally reads block 0 through a one-page bio to trigger geometry autodetection, and then updates disk capacity.

Ioctl flow normalizes old floppy command encodings, checks write/admin permissions, copies typed inputs from user space, and dispatches geometry, formatting, polling, status, reset, raw-command, write-error, eject, and twaddle operations. Most operations take the FDC lock and then restart normal request processing through `process_fd_request()` after the synchronous command finishes.

## State And Persistence
The driver has large persistent in-kernel state because the hardware interface is stateful. Per-drive state records open references, selected minor, current/probed geometry, cached track, last media check, maximum block/track touched, media-change flags, write-protect verification, generation, and write-error history. Per-FDC state records controller address, digital output register, data rate, specify bytes, FDC version, reset/configure/perpendicular mode flags, raw-command status, and debug tracks.

The track buffer persists across requests while the driver is in use and is allocated from DMA-capable memory when possible. It caches one region of one track for reads and partial writes; the cache is invalidated when geometry, drive, track, media, or buffer bounds no longer match. `floppy_sizes[]` persists capacity by minor/type and is reset to a conservative default when geometry becomes unknown.

Timers and work items persist across asynchronous operations: `fd_timeout` detects wedged operations, `fd_timer` handles select/spinup/watchdog delays, `floppy_work` runs bottom halves on `floppy_wq`, and `motor_off_timer[]` defers spindle shutdown. The FDC lock state `fdc_busy`, wait queues, `command_status`, `current_req`, `raw_cmd`, and `cont` are transient but globally shared because interrupts need direct access.

Configuration state can come from CMOS, boot parameters or module parameters (`floppy=...`, IRQ, DMA, FIFO, DCL quirks, slow mode), architecture hooks from `asm/floppy.h`, and ioctl-provided geometry/drive parameters. It is not persistent across module unload or reboot.

## Dependencies And Integration Points
This file depends heavily on architecture-specific floppy hooks from `asm/floppy.h` and DMA/IRQ helpers from `asm/dma.h` and `asm/irq.h`. It integrates with the block layer through blk-mq tag sets, `struct gendisk`, request queues, media-change events, `bio` submission for revalidation, and `block_device_operations`.

Hardware dependencies include FDC registers from `linux/fdreg.h`, ISA-style IO-port reservations, IRQ 6/DMA 2 defaults, CMOS drive-type macros, DOR/DIR/DCR/STATUS/DATA register behavior, and controller variants such as 8272A, 82072, 82077, 82078, and PC87306. Platform integration appears through `platform_driver`, per-drive `platform_device`s, sysfs `cmos` attributes, power-management resume reset, PNP module aliases, and architecture-specific eject support.

User-space ABI integration includes `/dev/fd*`, old type minors, `linux/fd.h` ioctl structures, compatibility conversions for 32-bit userspace, deprecated `FDRAWCMD` when enabled, block major aliases, and boot-time `__setup("floppy=", ...)` or module parameters.

## Risks And Edge Cases
The driver is concurrency-sensitive: interrupts, delayed work, timers, blk-mq queue callbacks, open/release, ioctl paths, and media revalidation all touch shared globals. Correct use of `fdc_busy`, `floppy_lock`, `floppy_mutex`, `open_lock`, wait queues, and DMA locks is essential to avoid stuck controllers, lost requests, or use-after-free of the track buffer.

DMA and pseudo-DMA handling are high risk. Buffers must be aligned, DMA-safe, avoid boundary problems handled by architecture allocators, and be freed only after use. Virtual DMA fallback changes command behavior and needs the `virtualdmabug_workaround()` path to prevent overrun on some controllers.

Geometry and media-change state are deliberately permissive for old formats and fragile hardware. Wrong handling can silently corrupt data by writing with stale geometry, failing to detect a disk swap, mishandling swapped sides or non-1 sector bases, or trusting a stale track buffer after a format/ioctl change.

Error recovery uses thresholds for reporting, recalibration, reset, and abort. Mis-tuning or missed state reset can loop retries, mask real failures, or leave the FDC wedged. Raw commands are especially risky because they can disturb controller state and share DMA resources with normal requests.

Initialization and teardown must unwind partially registered disks, tag sets, workqueues, timers, IRQ/DMA resources, IO regions, platform devices, and block major registration. Module unload assumes no unsafe forced unload and must cancel delayed work before releasing hardware resources.

## Test Signals
Useful validation signals include successful module load/unload with no floppy hardware, detection of one or two configured drives, no leaked IO regions or tag sets on initialization failure, and correct sysfs `cmos` output for registered drives.

Request-path tests should cover read and write on fixed type minors, autodetected type minors, partial-sector writes, track-buffer read reuse, writes crossing head/track boundaries, 2M/sector-base formats, write-protected media, end-of-disk short/failing requests, DMA allocation failure fallback when supported, and timeout/reset recovery.

Media and ioctl tests should cover disk-change events, `FDCLRPRM`, `FDSETPRM`, `FDDEFPRM`, `FDGETPRM`, formatting begin/track/end, polling status, reset, write-error reporting/clearing, eject behavior on architectures that implement it, deprecated raw commands when enabled, and 32-bit compat ioctl structure conversion.

Instrumentation signals include stable `fd_ref` counts across aliased opens, no stuck `fdc_busy`, no pending work/timers on release, proper `set_capacity()` changes after revalidation, and no KASAN/KCSAN/lockdep findings around interrupt, workqueue, ioctl, and release interleavings.
