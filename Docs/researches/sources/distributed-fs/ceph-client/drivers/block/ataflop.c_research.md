# sources/distributed-fs/ceph-client/drivers/block/ataflop.c

## Purpose

`ataflop.c` is the Atari floppy block driver for WD1772-compatible floppy hardware. It exposes Atari floppy drives through the legacy floppy block major, implements blk-mq request submission, talks directly to Atari DMA/FDC/PSG hardware registers, supports multiple disk geometries, handles media-change detection, and provides floppy ioctls for geometry and track formatting.

The driver is highly state-machine oriented. A single global in-flight request is translated into drive, side, track, sector, DMA address, and command state; subsequent FDC interrupts, timers, and completion callbacks advance or abort that state.

## Important APIs, Types, and Data

- `struct atari_disk_type` describes geometry: format name, sectors per track, total blocks, FDC speed, and track stretch.
- `struct atari_floppy_struct unit[FD_MAX_UNITS]` stores per-drive connection status, current media type, cached head position, write-protect state, blk-mq tag set, disks for geometry minors, ref/open state, and retry count.
- `minor2disktype[]` maps block minors to predefined media formats and maximum drive classes.
- Global request state includes `fd_request`, `SelectedDrive`, `ReqCmd`, `ReqBlock`, `ReqSide`, `ReqTrack`, `ReqSector`, `ReqCnt`, `ReqData`, `ReqBuffer`, `Probing`, `NeedSeek`, and formatting flags.
- `DMABuffer` and `TrackBuffer` are Atari ST-RAM DMA buffers. `TrackBuffer` caches whole tracks for reads when enabled.
- Timers: `motor_off_timer`, `readtrack_timer`, `timeout_timer`, and `fd_timer` handle drive deselection, multi-sector read progress, FDC timeouts, and media-change polling.
- Block operations are `floppy_fops` (`open`, `release`, `ioctl`, `check_events`) and blk-mq ops are `ataflop_mq_ops.queue_rq = ataflop_queue_rq`.
- Hardware helpers are the `FDC_READ` and `FDC_WRITE` macros plus Atari-specific globals such as `dma_wd`, `sound_ym`, `st_dma_ext_dmahi`, and `stdma_*`.

## Control Flow

Initialization starts in `atari_floppy_init()`. It rejects non-Atari machines, allocates one blk-mq tag set per possible drive, preallocates the default disk for each drive, chooses track-buffer policy, allocates ST-RAM for DMA/track buffering, adds default disks, probes hardware with `config_types()`, and registers `FLOPPY_MAJOR` with on-demand minor probing through `ataflop_probe()`.

`ataflop_probe()` lazily allocates and registers additional format minors. `ataflop_alloc_disk()` creates the `gendisk`, sets `FLOPPY_MAJOR`, one minor, no partitions, media-change events, `floppy_fops`, and a conservative maximum capacity.

Request submission enters `ataflop_queue_rq()`. The function serializes on `ataflop_lock`, refuses a second request while `fd_request` is live, claims Atari shared DMA via `stdma_try_lock()`, initializes the request, disables FDC interrupts while state is prepared, selects or probes a disk geometry, sets global request parameters with `setup_req_params()`, and starts the hardware state machine with `do_fd_action()`.

`do_fd_action()` first services reads from the whole-track cache when possible, then ensures the right drive is selected, calibrates if the track is unknown, seeks if the head is elsewhere, formats if a format command is active, or starts sector I/O with `fd_rwsec()`.

The normal read/write path is asynchronous:

- `fd_calibrate()` issues `RESTORE`; `fd_calibrate_done()` records track 0 or retries on failure.
- `fd_seek()` writes the target track and issues `SEEK`; `fd_seek_done()` updates `unit[].track` or restarts error handling.
- `fd_rwsec()` programs DMA, side, sector, FDC command, and timeout, then waits for an interrupt.
- `floppy_irq()` swaps out `FloppyIRQHandler`, reads FDC status, and calls the active completion routine.
- `fd_rwsec_done()` cancels whole-track timer state and calls `fd_rwsec_done1()`.
- `fd_rwsec_done1()` validates DMA/FDC status, handles autoprobe geometry fallback, copies data between DMA buffers and request memory, advances to the next sector, or completes the request and calls `finish_fdc()`.

Whole-track reads use `read_track`, `MultReadInProgress`, and `fd_readtrack_check()`. The timer samples the DMA address; if enough bytes have landed in the track buffer, it forces an FDC interrupt and completes the read without waiting for the controller to time out on the first nonexistent sector.

Formatting is handled by `fd_locked_ioctl(FDFMTTRK)` and `do_format()`. The queue is frozen/quiesced, shared DMA is locked, raw track data is synthesized into `TrackBuffer`, `IsFormatting` is set, and `do_fd_action()` drives `fd_writetrack()`/`fd_writetrack_done()` until `format_wait` completes.

`finish_fdc()` performs a dummy seek when needed to make the write-protect bit meaningful for future media-change checks, then `finish_fdc_done()` restarts media-change polling, starts delayed motor-off deselection, and releases ST-DMA.

## State and Persistence Behavior

Persistent kernel-visible state is block device state, drive geometry, open counts, and media-change flags. No disk metadata is persisted by the driver except data and formatting written to media.

Geometry state can be transient (`user_params[]` via `FDSETPRM`) or default/permanent for the life of the driver instance (`default_params[]` via `FDDEFPRM`). Media revalidation clears current geometry unless a default geometry is present. Capacity is updated from the active geometry with `set_capacity()`.

The whole-track cache is invalidated on writes, format operations, media changes, and some ioctl flush paths by setting `BufferDrive = -1`. Media changes are inferred through write-protect bit transitions, simulated changes (`fake_change`), and conservative reporting for write-protected media.

The current FDC/head position is cached in `unit[].track`; it is set to `-1` on uncertainty so the next request recalibrates.

## Dependencies and Integration Points

- Linux block layer: blk-mq, `gendisk`, `request_queue`, media-change events, block device operations, request completion/requeue helpers.
- Legacy floppy userspace ABI: `linux/fd.h` ioctls such as `FDGETPRM`, `FDSETPRM`, `FDDEFPRM`, `FDFMTTRK`, `FDCLRPRM`, `FDFLUSH`.
- Atari platform APIs and registers: MFP FDC interrupt, shared ST-DMA locking, Atari ST-RAM allocation, PSG port selection, FDC speed control, DMA cache maintenance.
- Boot/module parameters: `UseTrackbuffer`, `UserSteprate[]`, and non-module `floppy=` setup.
- On-demand block-device probing through `__register_blkdev(FLOPPY_MAJOR, "fd", ataflop_probe)`.

## Risks and Edge Cases

- The driver relies on many global variables for the single active request. Correct serialization through `ataflop_lock`, `fd_request`, and ST-DMA ownership is critical.
- Interrupt/timer races are explicitly handled in `fd_readtrack_check()`, `fd_times_out()`, and handler swapping, but remain a high-risk area because FDC interrupts, timer callbacks, and request completion all share global state.
- Media-change detection is inherently approximate on Atari hardware because it relies on write-protect behavior, so the driver intentionally reports conservative changes for write-protected media.
- Autoprobing changes `UDT` and capacity during error handling. Incorrect probing or stale capacity can affect request bounds and user-visible geometry.
- DMA buffer handling differs between extended DMA-capable hardware and systems requiring bounce buffers. Cache maintenance and physical address programming are correctness-critical.
- Formatting freezes/quiesces the queue and shares the same hardware state machine; failure paths must unquiesce/unfreeze and release FDC/DMA state.
- Cleanup appears to free `DMABuffer` but not separately free `TrackBuffer`, because `TrackBuffer` is an offset into the same allocation.

## Test Signals

- Build on Atari/m68k configurations with `CONFIG_ATARI`-compatible platform support and block layer changes enabled.
- Probe path: verify default disks register, on-demand geometry minors register, disconnected drives fail cleanly, and non-Atari init returns `-ENODEV`.
- I/O path: read/write across sector, side, and track boundaries; forced retries; recalibration after `RECALIBRATE_ERRORS`; final failure after `MAX_ERRORS`.
- Autoprobe: read unknown media and confirm geometry fallback, capacity updates, and no stale track buffer use.
- Media change: write-protect transition, fake changes from flush/format, `disk_check_media_change()` and `floppy_revalidate()` behavior.
- Formatting: `FDFMTTRK` with valid and invalid descriptors, write-protected media, and queue freeze/unfreeze on success and failure.
- Race tests around timeout firing near interrupt completion and whole-track read timer completion.
