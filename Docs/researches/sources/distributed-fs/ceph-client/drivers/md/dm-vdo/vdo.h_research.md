# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.h

## Purpose
`vdo.h` declares the central VDO object model and public in-driver API used by the dm-vdo implementation. It defines thread topology, read-only notification infrastructure, persistent metadata wrappers, admin state fields, statistics counters, and the large `struct vdo` that ties component subsystems together.

## Important APIs, Types, and Functions
Important types include `enum notifier_state`, `struct read_only_listener`, `struct vdo_thread`, `struct atomic_bio_stats`, `struct atomic_statistics`, `struct read_only_notifier`, `struct thread_config`, `struct vdo_geometry_block`, `struct vdo_super_block`, `struct vdo_administrator`, and `struct vdo`. Function declarations cover construction/destruction, thread creation, superblock and geometry persistence, synchronous flush, admin-state access, compression, statistics, read-only/recovery mode, thread assertions, physical-zone lookup, and status dumping.

## Control Flow
The header establishes the contracts used by `vdo.c` and other VDO components. Callers construct a VDO through `vdo_make()`, create required work queues with `vdo_make_thread()` or `vdo_make_default_thread()`, transition the instance through load/save/admin operations, and eventually call `vdo_destroy()`. Read-only flow is exposed through listener registration, entry enablement, notification drain/re-enable, and forced entry APIs.

## State and Persistence Behavior
`struct vdo` holds both atomic current mode (`state`) and encoded component states (`states`) destined for the superblock. `vdo_geometry_block` and `vdo_super_block` pair VIOs with fixed buffers for on-disk metadata. `read_only_notifier` stores the first read-only error and notification state under a spinlock. Statistics are atomic because bios and metadata I/O complete from multiple contexts.

## Dependencies and Integration Points
The header includes Linux atomic, blk, completion, kcopyd, list, and spinlock types, plus VDO-specific admin-state, encodings, workqueue, packer, physical-zone, statistics, thread-registry, and type definitions. It is a high-fanout interface consumed by VIO, zones, admin paths, target code, and statistics reporting.

## Risks and Test Signals
The largest risk is struct contract drift: many subsystems assume fields are initialized in a specific order and accessed only from expected VDO threads. Tests should validate read-only listener registration restrictions, state access from arbitrary threads, correct bio-ack queue detection, and that stats counters remain coherent under concurrent bio submission/completion.
