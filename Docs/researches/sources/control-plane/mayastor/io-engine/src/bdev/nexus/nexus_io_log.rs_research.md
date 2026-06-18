<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs

Purpose: provides per-core write-range logging for partial rebuild. When a synced child faults, the nexus can track write/unmap/write-zero ranges that occur while the child is absent and later rebuild only modified segments.

Important APIs/types/functions: `IOLogChannelInner`, `IOLogChannel`, `IOLog`, `IOLog::new`, `current_channel`, `IOLogChannelInner::log_io`, `take_segments`, and `IOLog::finalize`.

Control flow: `IOLog::new` creates one `IOLogChannel` per SPDK core, each with its own `SegmentMap`. Active nexus channels hold the current core's `IOLogChannel` and call `log_io` for write-like operations. `finalize` consumes all channel segment maps, merges them, and returns a `RebuildMap` for the target device.

State and persistence: log state is in-memory only. Each channel owns an `UnsafeCell<Option<SegmentMap>>`; `take_segments` consumes it so later access panics. The merged `RebuildMap` becomes input to rebuild logic, not a persisted artifact here.

Dependencies/integration: depends on core `SegmentMap`, rebuild `RebuildMap` and `SEGMENT_SIZE`, SPDK core enumeration/current core, parking-lot mutex, and nexus channel write logging. It is started/stopped from `NexusChild`.

Risks: `log_io` asserts the caller is on the channel's core, so cross-core misuse panics. The `UnsafeCell` design is lockless but relies on SPDK single-thread-per-channel discipline. Debug formatting unwraps the first channel and assumes at least one core. Access after `finalize` panics. Segment size and block-length conversions must match rebuild expectations.

Test signals: per-core channel creation, write/write-zero/unmap marking, read/flush/reset not marking, merge of multiple core maps, access-after-finalize panic expectations, current-core lookup, empty/invalid device creation assertions, and rebuild map ranges matching logged LBNs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs -->
