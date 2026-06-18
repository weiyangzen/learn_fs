# sources/distributed-fs/ceph-client/drivers/block/swim3.c

## Purpose
Implements the Power Macintosh SWIM3 floppy controller driver. It binds to macio devices, controls SWIM3 and DBDMA registers, exposes floppy disks through blk-mq, and uses a state machine, interrupts, timers, and DMA commands for reads and writes.

## Important APIs, types, and functions
- `enum swim_state` models controller activity: `idle`, `locating`, `seeking`, `settling`, `do_transfer`, `jogging`, `available`, `revalidating`, and `ejecting`.
- `struct floppy_state` holds MMIO/DMA mappings, IRQs, geometry, write-protect state, DMA command buffer, timeout, wait queue, current request, tag set, and macio/media-bay context.
- Request flow: `swim3_queue_rq()`, `act()`, `setup_transfer()`, `swim3_interrupt()`, and `swim3_end_request()`.
- Timer handlers: `scan_timeout()`, `seek_timeout()`, `settle_timeout()`, `xfer_timeout()`.
- Drive access: `grab_drive()`, `release_drive()`, `fd_eject()`, `floppy_open()`, `floppy_release()`, `floppy_revalidate()`, and `floppy_ioctl()`.
- Device setup: `swim3_add_device()`, `swim3_attach()`, `swim3_mb_event()`, and `swim3_init()`.

## Control flow
Attach registers floppy major for the first drive, allocates a blk-mq disk/tag set, maps SWIM3 and DMA MMIO, requests the SWIM3 interrupt, initializes geometry, then adds an `fdN` disk. Queueing accepts one request at a time under `swim3_lock`, rejects absent media/write-protected writes, computes cylinder/head/sector, sets state to `do_transfer`, and calls `act()`. The state machine seeks or locates current cylinder, sets up DBDMA and controller transfer registers, arms interrupts and timeouts, and returns. Interrupts handle sector seen, seek complete, and transfer complete/error, update partial request progress, retry where possible, or end the request.

## State and persistence behavior
State is static per possible drive in `floppy_states[]` and `disks[]`. Current request and controller state are protected by `swim3_lock`; open/ioctl paths use `swim3_mutex`. Media presence and write protection are cached and refreshed through open/revalidate/media-bay events. Timers represent pending hardware timeouts and are cancelled on interrupt completion.

## Dependencies and integration points
Depends on PowerPC macio, Open Firmware matching, DBDMA, media bay APIs, pmac feature calls, raw MMIO, blk-mq, floppy ioctl ABI, and fixed `FLOPPY_MAJOR`.

## Risks and test signals
- There is no remove path shown for freeing disks/resources, so hot-unplug support appears limited.
- DMA address handling uses a local `phys_to_bus` hack with `PCI_DRAM_OFFSET`; architecture assumptions are important.
- Only one active request per drive is supported; queue resource behavior should be tested.
- State-machine retries, timeout cancellation, media bay changes, write-protect checks, and partial-transfer request updates are high-risk areas.
- Test read and write flows, seek failures, transfer CRC/underrun/overrun errors, eject/revalidate, media-bay removal, and module load on systems with zero, one, or two controllers.
