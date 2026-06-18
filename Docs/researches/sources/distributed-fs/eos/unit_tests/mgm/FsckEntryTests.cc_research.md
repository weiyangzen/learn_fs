# sources/distributed-fs/eos/unit_tests/mgm/FsckEntryTests.cc

## Purpose
Tests MGM fsck entry repair logic for metadata/checksum/size mismatches and replica-set inconsistencies. It validates when repairs mutate MGM metadata, when repair jobs are launched, and when repair fails.

## Important APIs, types, and functions
The fixture constructs `eos::mgm::FsckEntry`, populates MGM `FileMdProto` and FST `FmdBase` metadata, and replaces `mRepairFactory` with a `MockRepairJob`. Tests exercise `FsckEntry::Repair()` across `FsckErr` values including `MgmXsDiff`, `MgmSzDiff`, `FstSzDiff`, `FstXsDiff`, `UnregRepl`, `DiffRepl`, and `MissRepl`.

## Control flow
Setup creates a two-replica file with matching MGM/FST size and checksum. Each test corrupts one dimension, marks an error type, calls `Repair()`, and asserts metadata correction, failure, replica removal/addition, or mock repair-job invocation. Replica tests model unregistered, over-replicated, under-replicated, and missing-on-disk states.

## State and persistence
State is in-memory proto metadata and maps of FST file info. Production equivalents are durable namespace metadata and physical replica records.

## Dependencies and integration points
Depends on Google Test/Mock, layout id helpers, fsck repair internals, string checksum conversion, and FST file metadata structures.

## Risks and test signals
This is a high-value repair oracle. Risks include access to internals under `IN_TEST_HARNESS`, mock factory always reusing one job, and limited layout/checksum variety. Additional tests should cover erasure-coded layouts, excluded source/destination sets, no-contact combinations, and failed repair-job statuses.
