# sources/distributed-fs/ceph-client/include/linux/device-mapper.h

Purpose: Defines the in-kernel Device Mapper target and mapped-device API, including target callbacks, table management, device acquisition, bio/request mapping return codes, queue modes, DAX hooks, zoned-device support, events, and logging helpers.

Important APIs, types, and functions: Key types include `enum dm_queue_mode`, `status_type_t`, `union map_info`, `struct dm_dev`, `struct target_type`, `struct dm_target`, `struct dm_arg_set`, `struct dm_arg`, and zoned `struct dm_report_zones_args`. Callback typedefs cover target construction/destruction, bio and request mapping, endio, suspend/resume, status, messages, ioctls, report_zones, busy checks, device iteration, I/O hints, and DAX operations. APIs register targets, parse args, get/put underlying devices, create/hold/reference mapped devices, suspend/resume, wait/emit events, create/complete/swap tables, get live tables under SRCU, and manipulate geometry/queue limits.

Control flow: A DM target module registers a `target_type`; table loading calls its `ctr()` with parsed arguments and target geometry, target code opens underlying devices via `dm_get_device()`, and I/O dispatch invokes `map()`/request callbacks. Targets return submitted, remapped, requeue, delay-requeue, or kill codes; endio callbacks can complete, defer, or requeue. Tables are built empty, populated per target, completed, then swapped into a suspended mapped device.

State and persistence: Runtime state includes target private data, opened lower devices, target feature flags, per-I/O private data, live tables, mapped-device references, event numbers, queue mode, and table queue limits. Persistent mapping configuration is provided by userspace/device-mapper ioctl or early boot parameters, not stored in this header.

Dependencies and integration points: Integrates with block layer bios/requests, gendisks, queue limits, blk crypto, zoned block devices, DAX, ratelimited printk, ioctls, module registration, and early boot `dm-mod.create=`.

Risks and test signals: Risks include wrong map/endio return codes, leaking `dm_dev` references, accepting partial bios incorrectly, unsafely swapping tables without suspend, inconsistent feature flags, DAX offset mistakes, zoned model misreporting, and logging/status buffer overflows. Test table load/unload, suspend/resume and event waits, bio/request targets, flush/discard/write-zeroes paths, partial bio acceptance, zoned report/reset/append behavior, DAX targets, arg parsing errors, and target module init/exit.
