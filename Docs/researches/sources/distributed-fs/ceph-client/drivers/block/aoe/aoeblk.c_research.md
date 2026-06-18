# sources/distributed-fs/ceph-client/drivers/block/aoe/aoeblk.c

Purpose: provides the Linux block-device front end for AoE devices. It creates gendisks and blk-mq queues, exposes sysfs/debugfs state, queues requests into the AoE command engine, handles open/release/ioctl/getgeo, and owns the per-device `struct buf` slab cache.

Important APIs and functions: sysfs show functions expose state, MAC, network interfaces, firmware version, and payload size. `aoe_debugfs_show()` reports RTT, skb pool, target frame state, congestion, taint, and interface names. `aoeblk_open()` validates device state and increments `nopen`. `aoeblk_release()` decrements and triggers config rediscovery on last close. `aoeblk_queue_rq()` starts by checking `DEVFL_UP`, appends requests to `d->rq_list`, and calls `aoecmd_work()`. `aoeblk_gdalloc()` performs sleeping disk allocation from workqueue context. `aoeblk_init/exit()` create and destroy the buffer cache and debugfs root.

Control flow: `aoecmd` identifies a remote device and sets `DEVFL_GDALLOC`; deferred work calls `aoeblk_gdalloc()`. Disk allocation creates a mempool for `struct buf`, initializes a blk-mq tag set, allocates a disk with queue limits, fills major/minor/name/private data, sets `DEVFL_UP`, calls `device_add_disk()` with AoE attributes, and registers debugfs. Queue requests remain under `d->lock` and are transformed asynchronously by `aoecmd.c`.

State and persistence: per-device block state includes `gd`, `blkq`, `tag_set`, `bufpool`, `nopen`, `ssize`, and sysfs/debugfs visibility. The module parameter `aoe_maxsectors` controls maximum request sectors.

Dependencies and integration points: depends on `aoe.h`, Linux blk-mq, gendisk, sysfs attribute groups, debugfs, mempools, and command/device code. It calls `aoecmd_cfg()` on release and `aoecmd_work()` on queueing.

Risks: allocation failure requeues work and can loop if memory pressure persists. `aoeblk_queue_rq()` returns I/O error for down devices after starting the request but does not complete it in the same branch, which is a behavior worth verifying against blk-mq expectations. Test signals include disk creation after AoE discovery, sysfs/debugfs contents, open/close rediscovery, request completion under load, and teardown while requests are queued.
