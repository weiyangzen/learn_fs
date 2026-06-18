# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_int.h

Purpose: central internal contract for the DASD subsystem. It defines DASD device states, request structures, discipline callbacks, block/device state containers, profiling data, stop/flag bits, chunk allocators, path-state helpers, and cross-file prototypes.

Important APIs/types/functions: key structures are `struct dasd_ccw_req`, `struct dasd_discipline`, `struct dasd_device`, `struct dasd_block`, `struct dasd_path`, `struct dasd_profile`, and copy-relation structs. Important helpers include `dasd_get_device()`/`dasd_put_device()`, static chunk-list alloc/free helpers, `dasd_check_blocksize()`, `dasd_get_callback_data()`, EER stubs/entry points, and the many `dasd_path_*` bitmask helpers.

Control flow: no standalone runtime loop lives here, but the header encodes the subsystem state machine from `NEW` through `ONLINE` and the callback table that each discipline uses for probing, analysis, I/O building, formatting, ERP, ESE, PPRC, path events, and info/ioctl handling. Inline path helpers mutate per-channel flags and aggregate path masks used by the core and disciplines.

State and persistence behavior: state is in-memory per-device/per-block state: CCW queues, timers, tasklets/work items, path flags, refcounts, profile counters, copy-pair metadata, and feature bits copied from devmap. Persistent media changes are delegated to discipline operations such as format, release-space, and copy-pair swap.

Dependencies and integration points: binds DASD core, devmap, gendisk, ioctl, proc, ERP, EER, ECKD/FBA/DIAG disciplines, s390 ccw/cio APIs, debugfs/s390 debug, blk-mq, and userspace ABI structs from `asm/dasd.h`.

Risks and test signals: macro/inline helpers are widely shared, so path-bit changes can affect failover, HPF disablement, FC security reporting, and path verification. Static chunk allocators require lock discipline by callers. Compile coverage across `CONFIG_DASD_EER` and `CONFIG_DASD_PROFILE`, path failover tests, reference-count leak checks, and blocksize boundary tests are important.
