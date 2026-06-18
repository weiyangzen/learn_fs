# File Research: sources/block-storage/kvdo/vdo/vdo.h

## Purpose
Defines core `struct vdo`, VDO thread representation, and public APIs for lifecycle, state, statistics, compression, persistence, assertions, and zone lookup.

## Key Structures
- `struct vdo_thread`: wraps a work queue, owning VDO, thread ID, and allocation-thread registration.
- `struct vdo`: central object containing thread queues, atomic state, component states, read-only notifier, config, layout, block map, recovery journal, slab depot, packer, flusher, logical/physical/hash zones, I/O submitter, data VIO pool, admin state, statistics, sysfs objects, geometry, and compression contexts.

## Public API
- Lifecycle: `vdo_make()`, `vdo_destroy()`, `vdo_make_thread()`, `vdo_make_default_thread()`.
- Sysfs/stats: `vdo_add_sysfs_stats_dir()`, `vdo_fetch_statistics()`, `vdo_dump_status()`.
- Config: `vdo_prepare_to_modify()`, `vdo_get_backing_device()`, `vdo_get_device_name()`.
- State: `vdo_get_state()`, `vdo_set_state()`, `vdo_get_admin_state()`, `vdo_save_components()`.
- Modes: `vdo_enable_read_only_entry()`, `vdo_in_read_only_mode()`, `vdo_in_recovery_mode()`, `vdo_enter_recovery_mode()`.
- Compression: `vdo_set_compressing()`, `vdo_get_compressing()`.
- Thread assertions and helpers: admin/logical/physical/dedupe/CPU assertions, `vdo_get_callback_thread_id()`.
- Physical mapping: `vdo_get_physical_zone()`, `vdo_get_bio_zone()`.

## Inline Helpers
- `vdo_uses_bio_ack_queue()` checks whether a separate bio acknowledgement queue exists.
- `vdo_crc32()` preserves historical VDO CRC initialization/finalization behavior.
