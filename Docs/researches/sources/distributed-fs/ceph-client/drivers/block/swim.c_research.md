# sources/distributed-fs/ceph-client/drivers/block/swim.c

## Purpose
Implements the original Macintosh SWIM floppy controller driver for m68k-era hardware. It probes internal/external drives, exposes them as floppy block devices, and performs read-only MFM sector reads through timing-sensitive low-level helper routines.

## Important APIs, types, and functions
- Register layouts `struct swim` and `struct iwm` define SWIM/IWM MMIO offsets.
- `struct floppy_state` stores physical drive location, media geometry, disk state, refcount, `gendisk`, tag set, and parent controller.
- Hardware helpers: `set_swim_mode()`, `get_swim_mode()`, `swim_select()`, `swim_action()`, `swim_readbit()`, `swim_drive()`, `swim_motor()`, `swim_eject()`, `swim_seek()`, `swim_track00()`.
- Data path: `swim_read_sector()`, `floppy_read_sectors()`, and `swim_queue_rq()`.
- Block operations: `floppy_open()`, `floppy_release()`, `floppy_ioctl()`, `floppy_getgeo()`, and `floppy_check_events()`.
- Probe/remove: `swim_probe()`, `swim_floppy_init()`, `swim_remove()`.

## Control flow
Platform probe reserves MMIO, switches the chip to SWIM mode, allocates controller state, scans internal and external drives, registers floppy major, allocates a small blk-mq disk for each drive, and adds `fdN` disks. Open powers the motor, sets MFM mode, detects media geometry if needed, validates write protection, and updates capacity. Queueing serializes with `swd->lock`, rejects writes or no-media requests, translates sector numbers to track/head/sector, reads sectors with retries through assembly helpers, updates the block request, and completes it.

## State and persistence behavior
Per-drive state tracks inserted/ejected media, media type, write protection, geometry, current track, open refcount, and registration. This state is volatile and refreshed on open after eject/media change. The driver registers fixed floppy major `FLOPPY_MAJOR` and one minor per detected drive.

## Dependencies and integration points
Depends on platform device resources, m68k Macintosh VIA helpers, raw MMIO access, blk-mq, floppy ioctls, and `swim_asm.S` functions `swim_read_sector_header()` and `swim_read_sector_data()`.

## Risks and test signals
- Writes are rejected in queueing even though open checks write protection; read-only behavior should be explicit in user tests.
- `swim_read_sector()` returns `0` when header fields mismatch, causing retries until failure.
- Timing loops use sleeps and local IRQ disabling around low-level reads; hardware-only testing is needed for regressions.
- `FDGETPRM` copies the entire `floppy_type` array, which may not match traditional ioctl expectations.
- Test drive detection, no media, media change, eject, write attempts, bad sectors, and cleanup after partial disk registration failure.
