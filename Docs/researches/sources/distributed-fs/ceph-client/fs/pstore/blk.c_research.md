# sources/distributed-fs/ceph-client/fs/pstore/blk.c

## Purpose
`blk.c` implements the pstore block-device frontend to the pstore/zone manager, registering either a dedicated `pstore_device_info` supplied by another driver or a best-effort generic block device.

## Important APIs, types, and functions
External APIs are `register_pstore_device`, `unregister_pstore_device`, and `pstore_blk_get_config`. Important helpers include `__register_pstore_device`, `__register_pstore_blk`, `psblk_generic_blk_read`, `psblk_generic_blk_write`, `early_boot_devpath`, `__best_effort_init`, and `__best_effort_exit`.

## Control flow
Registration validates zone callbacks and total size, applies module/Kconfig sizes for kmsg, pmsg, console, and ftrace, sets zone ownership, and calls `register_pstore_zone`. Best-effort mode resolves and opens `blkdev`, verifies it is a block device, derives total bytes, and exposes kernel read/write callbacks to the zone manager.

## State and persistence
Global state under `pstore_blk_lock` tracks `psblk_file` and the active `pstore_device_info`. Persistent data lives on the configured block device and is partitioned by `zone.c`.

## Dependencies and integration points
It depends on block devices, kernel file I/O, early boot device lookup for built-in use, module parameters, and the exported pstore/zone backend registration API.

## Risks and test signals
Risks include using best-effort writes without a panic-safe `panic_write`, block-device exclusive open failures, size alignment surprises, single-backend conflicts, and write rejection from interrupt context. Test signals include invalid `blkdev`, PARTUUID/major-minor resolution, aligned and unaligned size parameters, unregister cleanup, and panic/oops capture with and without a dedicated panic writer.
