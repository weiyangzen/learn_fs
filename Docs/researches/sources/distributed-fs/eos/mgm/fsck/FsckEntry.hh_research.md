<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh -->
# sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh

## Purpose

`FsckEntry.hh` declares the per-file fsck repair object and related FST metadata/error types. It is the boundary between fsck engine scheduling and concrete file repair operations.

## Important APIs, Types, and Functions

`enum class FstErr` represents FST-side metadata states: none, no contact, not on disk, no FMD info, and non-existing filesystem. `FstFileInfoT` stores local path, disk size, FST FMD helper, and FST error. Type aliases define `FsckRepairJob` as `DrainTransferJob`, `RepairFnT`, and `RepairFactoryFnT`. `FsckEntry` exposes constructor, destructor, and `Repair()`, with repair helpers made public only under `IN_TEST_HARNESS`.

## Control Flow

The header shows a repair object lifecycle: construct with file id, error fsids, expected error type, best-effort flag, and QDB client; call `Repair()`; the implementation gathers MGM/FST metadata, runs a matching repair helper, and notifies outcome. Helper names reveal the major branches: MGM checksum/size diff, FST checksum/size diff, replica/RAIN inconsistency repair, best-effort repair, metadata collection, FST FMD query, resync, and stats/backend notification.

## State and Persistence Behavior

Per-entry state includes file id, error filesystem ids, converted reported fsck error, best-effort flag, MGM metadata protobuf, FST info map, repair-operation dispatch map, repair-job factory, and QDB client. The object itself is transient; implementation methods can mutate persistent namespace metadata and FST/backend state.

## Dependencies and Integration Points

The header depends on EOS logging, common filesystem/FMD types, drain transfer jobs, namespace file metadata interfaces, QuarkDB qclient, and XRootD client filesystem APIs. It integrates with `Fsck` via `NotifyOutcome()` and with drain/transfer infrastructure through `FsckRepairJob`.

## Risks and Edge Cases

The repair factory signature is broad and easy to misuse: source/destination fsids, exclusion sets, drop-source, app tag, and repair-excluded flags all affect destructive behavior. Test harness exposure changes method visibility. `FstFileInfoT` does not initialize `mDiskSize` in its constructor, so code must set it before reading for successful stats.

## Test Signals

Header-level tests should compile both normal and `IN_TEST_HARNESS` builds. Unit tests should inject a fake repair factory and QDB client, validate dispatch for every supported `FsckErr`, and verify FST error enum handling in metadata collection and repair decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh -->
