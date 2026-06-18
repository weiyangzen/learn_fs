# sources/control-plane/mayastor/io-engine/tests/lock_lba_range.rs

Purpose: SPDK reactor tests for LBA range locking on a nexus bdev, including overlapping lock serialization and front-end I/O blocking while a range lock is held.

Important APIs/types/functions: `test_ini`/`test_fini` create/destroy a two-child AIO nexus. `lock_range` and `unlock_range` use `UntypedBdev::lock_lba_range`/`unlock_lba_range`. `recv_from` polls current reactor until a crossbeam channel receives. Tests use `LbaRange`, `LbaRangeLock`, `DmaBuf`, and `reactor_poll!`.

Control flow: `lock_unlock` obtains and releases one range. `multiple_locks` acquires one lock, schedules another overlapping lock and confirms it does not complete until the first unlocks. `lock_then_fe_io` acquires a lock, schedules a write to an overlapping block, verifies the I/O does not complete, unlocks, then verifies the write completes.

State and persistence: temporary `/tmp/disk{n}.img` files and in-memory lock state on the nexus bdev. Tests run under `common::spdk_test`.

Dependencies and integration points: SPDK reactor polling, nexus front-end I/O path, bdev range locking, AIO children.

Risks and edge cases: manual reactor polling can be timing-sensitive. Fixed temp paths. The test allows holding RefCell refs across awaits via file-level lint allow.

Test signals: strong coverage that LBA locks serialize overlapping locks and gate front-end writes.
