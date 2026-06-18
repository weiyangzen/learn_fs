# sources/distributed-fs/ceph-client/drivers/s390/block/dcssblk.c

Purpose: implements the s390 DCSS memory block driver. It lets users load named DCSS segments through sysfs, expose them as no-partition block disks, optionally enable DAX for aligned ranges, switch shared/exclusive access, save modified segments, and remove devices.

Important APIs/types/functions: `struct dcssblk_dev_info` tracks one block device and segment list; `struct segment_info` tracks each loaded DCSS. Sysfs stores are `dcssblk_add_store()`, `dcssblk_remove_store()`, `dcssblk_shared_store()`, and `dcssblk_save_store()`. I/O paths are `dcssblk_open()`, `dcssblk_release()`, `dcssblk_submit_bio()`, `dcssblk_dax_direct_access()`, and `dcssblk_dax_zero_page_range()`.

Control flow: init registers a root device, `add`/`remove` files, a dynamic block major, and loads module-param segments. Add parses colon-separated segment sets, loads each segment shared, checks uniqueness/continuity/type compatibility, allocates a disk, registers a device, maps DAX if subsection-aligned, adds the disk, and sets readonly based on segment type. Remove requires idle use count, unloads segments, removes DAX/disk/device state, and frees resources.

State and persistence behavior: runtime state is the protected `dcssblk_devices` list, per-device use count, `is_shared`, `save_pending`, loaded segment ranges, DAX mapping, and gendisk. `save` persists segment contents only for savable segment types. Shared/exclusive mode changes are live segment access-mode changes.

Dependencies and integration points: depends on s390 `extmem` segment APIs, block layer bio submission, DAX/dev_pagemap, root devices/sysfs, semaphores, direct kernel virtual mappings of DCSS ranges, and module parameter parsing.

Risks and test signals: I/O requires sector and bio segment page alignment; misaligned bios fail. Shared-mode write checks depend on segment type. Error paths mix device, DAX, pgmap, disk, module ref, and segment unload cleanup. Test multi-segment continuity/type mismatch, duplicate names, DAX-aligned and unaligned segments, busy remove/save, shared-to-exclusive failures, readonly writes, and parameter parsing with `(local)`.
