# sources/distributed-fs/ceph-client/drivers/cdrom/gdrom.c

## Purpose
This file implements the Sega Dreamcast GD-ROM block and CD-ROM interface. It talks directly to Dreamcast GD-ROM ATA-like registers, exposes the drive as a single read-only `gendisk`, registers a Linux CD-ROM device, handles media/session ioctls, and services block-layer read requests through DMA.

## Important APIs, Types, and Functions
Key device state is the singleton `gdrom_unit gd`, holding the `gendisk`, `cdrom_device_info`, blk-mq queue/tag set, pending command flags, transfer flag, cached TOC, and last status. `struct gdromtoc` models the device TOC format, while `struct gdrom_id` receives identify data.

Hardware helpers include `gdrom_is_busy()`, `gdrom_data_request()`, `gdrom_wait_clrbusy()`, `gdrom_wait_busy_sleeps()`, `gdrom_spicommand()`, `gdrom_identifydevice()`, `gdrom_execute_diagnostic()`, and `gdrom_hardreset()`. CD-ROM operations are provided by `gdrom_ops`; block operations by `gdrom_bdops`; blk-mq dispatch by `gdrom_queue_rq()` and `gdrom_readdisk_dma()`. Probe/remove entry points are `probe_gdrom()` and `remove_gdrom()`.

## Control Flow
Module init registers a platform driver and a synthetic platform device named `gdrom`, causing `probe_gdrom()` to run. Probe clears singleton state, executes an ATA diagnostic, reads firmware identity, registers a dynamic block major, allocates CD-ROM and blk-mq/gendisk structures, registers the universal CD-ROM interface, installs command/DMA IRQ handlers, programs DMA mode and access windows, allocates a TOC buffer, then calls `add_disk()`.

CD-ROM command flow allocates a `packet_command`, sets `gd.pending`, issues a packet via `gdrom_packetcommand()`/`gdrom_spicommand()`, and waits on `command_queue` until `gdrom_command_interrupt()` clears pending. Data reads use `gdrom_readdisk_dma()`: derive GD sectors from block-layer 512-byte sectors, program DMA start/length/direction registers, send a read packet, set both pending and transfer, start DMA, wait for `gdrom_dma_interrupt()`, and complete the request.

## State and Persistence Behavior
All driver state is volatile kernel memory or hardware register state. `gd.pending` and `gd.transfer` coordinate interrupt completion with wait queues; `gd.status` captures the command/status register. `gd.toc` persists only while the driver is loaded. Hardware state includes the G1 reset register, DMA control registers, transfer protection window, and drive sense/error state. There is no persistent on-disk metadata written by the driver; writes are rejected.

## Dependencies and Integration Points
The driver depends on Dreamcast SH platform headers (`mach/dma.h`, `mach/sysasic.h`), raw I/O accessors, CD-ROM core, block layer/blk-mq, platform devices, and Dreamcast IRQ events `HW_EVENT_GDROM_CMD` and `HW_EVENT_GDROM_DMA`. It integrates with user space through `/dev/gdrom`, CD-ROM ioctls, disk media-change events, and block reads.

## Risks
The driver is singleton and heavily serialized by global fields; unexpected concurrent packet and DMA activity can corrupt `gd.pending` or `gd.transfer`. DMA assumes one contiguous segment and uses the first bio page directly, so queue limits are essential. Timeouts often clear flags after wait completion, but lower-level hardware may still be active. `wait_event_interruptible_timeout()` return values are mostly ignored, so signals and timeouts collapse into status checks. Register polling uses raw busy loops and fixed timeouts. Probe error unwinding must keep block, CD-ROM, IRQ, and tag-set lifetimes aligned.

## Test Signals
Useful signals are Dreamcast boot/probe logs showing diagnostic success and firmware identity, successful `add_disk()`, media-change events after disc swap, correct multisession LBA from `get_last_session`, successful reads with 2048-byte logical blocks, rejected writes, clean module unload, and no stuck pending/transfer waits under forced IRQ loss or read timeouts.
