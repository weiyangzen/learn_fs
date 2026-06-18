# sources/distributed-fs/ceph-client/drivers/mtd/ubi/block.c

## Purpose
Provides read-only block devices layered on top of UBI volumes. It supports boot/module `ubi.block=` parameters and runtime create/remove/resize through UBI notifications and ioctls elsewhere in UBI.

## Important APIs, Types, and Functions
Key types are `struct ubiblock_param`, `struct ubiblock_pdu`, and `struct ubiblock`. Public functions are `ubiblock_create()`, `ubiblock_remove()`, `ubiblock_init()`, and `ubiblock_exit()`. Request handling is done by `ubiblock_queue_rq()` and `ubiblock_read()`. Device lifecycle uses `ubiblock_open()`, `ubiblock_release()`, `ubiblock_cleanup()`, `ubiblock_resize()`, `ubiblock_notify()`, and `ubiblock_remove_all()`.

## Control Flow
The `block=` parameter parser accepts a volume path, `ubi_num,vol_id`, or `ubi_num,name`. Init registers a block major and a UBI volume notifier. When matching volumes are added or runtime create is requested, `ubiblock_create()` calculates 512-byte sector capacity, checks duplicates under `devices_mutex`, allocates a device, configures blk-mq, allocates a gendisk/minor, sets capacity, links it globally, and calls `device_add_disk()`. Reads translate sector position to UBI LEB plus offset, split requests at LEB boundaries, and call `ubi_read_sg()`. Remove refuses busy devices; resize updates disk capacity for existing devices; notifications create/remove/resize in response to UBI volume events.

## State and Persistence
Runtime state includes the global ubiblock list, IDR minor allocation, block major, parsed boot parameters, per-device refcount, UBI volume descriptor, gendisk, request queue, tag set, and LEB size. It does not persist new on-flash data and only opens UBI volumes read-only.

## Dependencies and Integration Points
Depends on UBI volume APIs, block layer and blk-mq, scatterlists, IDR, gendisk, and volume notifier infrastructure. It is conditionally compiled into `ubi.o` when `CONFIG_MTD_UBI_BLOCK` is enabled.

## Risks
Only read requests are supported; writes return I/O error. Capacity truncates non-512-byte tail bytes, with warning severity depending on dynamic/static volume type. Removal must coordinate `devices_mutex` and `dev_mutex` to avoid freeing open devices. Request completion maps UBI read errors through `errno_to_blk_status()`.

## Test Signals
Test `ubi.block=` path/name/id forms, UBI volume add/remove/resize/update notifications, read-only mount behavior, write rejection, reads spanning LEB boundaries, busy remove returning `-EBUSY`, and capacity truncation warnings.
