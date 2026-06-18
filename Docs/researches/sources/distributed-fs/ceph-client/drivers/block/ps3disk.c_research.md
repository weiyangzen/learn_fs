# sources/distributed-fs/ceph-client/drivers/block/ps3disk.c

## Purpose
Implements the PlayStation 3 disk block driver. It exposes PS3 hypervisor storage regions as Linux block devices and translates blk-mq read, write, and flush requests into LV1 storage calls using a single 64 KiB DMA bounce buffer.

## Important APIs, Types, And Functions
`struct ps3disk_private` stores the blk-mq tag set, gendisk, current request, block-size conversion factor, raw capacity, model string, and spinlock. `struct lv1_ata_cmnd_block` models the command block used for ATA IDENTIFY through LV1.

The blk-mq entry point is `ps3disk_queue_rq()`, backed by `ps3disk_do_request()`, `ps3disk_submit_request_sg()`, and `ps3disk_submit_flush_request()`. Interrupt completion is handled by `ps3disk_interrupt()`. Probe/remove lifecycle is implemented by `ps3disk_probe()` and `ps3disk_remove()`, and module setup uses `ps3disk_init()` and `ps3disk_exit()`.

ATA helper functions copied from libata, including `ata_id_n_sectors()` and `ata_id_c_string()`, decode capacity and model information after `ps3disk_identify()` sends `ATA_CMD_ID_ATA`.

## Control Flow
Module init first checks `FW_FEATURE_PS3_LV1`, registers a dynamic block major, and registers a `ps3_system_bus_driver` matching PS3 storage disk devices. Probe reserves a disk index, allocates private state and a DMA bounce buffer, calls `ps3stor_setup()` with the interrupt handler, identifies the disk, allocates a single-queue blk-mq tag set and disk, sets queue limits, sets capacity from the selected PS3 storage region, and publishes the disk.

For I/O, `ps3disk_queue_rq()` starts the request, takes `priv->lock`, and submits it. Reads and writes are converted from Linux 512-byte sectors to device block sectors using `blocking_factor`. Writes gather request segments into `dev->bounce_buf` before `lv1_storage_write()`. Reads call `lv1_storage_read()` and scatter the bounce buffer back to bio segments in the interrupt handler. Flushes issue `LV1_STORAGE_ATA_HDDOUT`. On completion, `ps3disk_interrupt()` fetches async status, checks the tag, completes non-block-layer commands through `dev->done`, or ends the block request and restarts hardware queues.

## State And Persistence Behavior
The driver does not own persistent metadata. Persistent data is the physical PS3 disk content behind LV1 storage. Runtime state includes one outstanding block request in `priv->req`, a global disk-index bitmap `ps3disk_mask`, the bounce buffer and logical partition address managed by PS3 storage helpers, and cached capacity/model information. Removal clears the bitmap bit, deletes the disk, synchronizes disk cache, tears down PS3 storage, frees the bounce buffer and private data, and clears driver data.

## Dependencies And Integration Points
Depends on PS3 platform firmware and hypervisor interfaces (`asm/lv1call.h`, `asm/ps3stor.h`, `FW_FEATURE_PS3_LV1`), blk-mq, Linux ATA identify helpers/macros, and the PS3 system bus. It is wired from the parent block `Makefile` under `CONFIG_PS3_DISK` and aliases `PS3_MODULE_ALIAS_STOR_DISK`.

## Risks
The single `priv->req` field means the queue model depends on one in-flight request at a time; queue-depth changes would require careful redesign. The 64 KiB bounce buffer caps hardware request size and all segment copying must stay within queue limits. Interrupt code logs tag mismatches but still proceeds, so request/tag consistency is important. Error handling around `ps3disk_identify()` is permissive: probe continues after identify failure, which may leave model/capacity metadata incomplete but capacity still comes from the PS3 region. Cache flush during remove is best-effort and hardware-specific.

## Test Signals
Meaningful testing requires PS3 LV1 hardware or an emulator with compatible storage behavior. Signals include successful probe logs with model/capacity, read/write filesystem smoke tests, flush/fsync tests, removal/shutdown cache sync, request failure injection from LV1 calls, and boot/module load on non-PS3 platforms returning `-ENODEV`.
