# sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/recov_vollog.h` declares the recoverable volume log used by Coda resolution. The log lives partly in RVM and partly in VM and records directory mutation history for reintegration, resolution, salvage, truncation, and wrap-around management.

## Important APIs, Types, and Functions

The central type is `class recov_vol_log`, with recoverable fields such as version, allocation flags, administrative size limits, block index, recoverable in-use bitmap, recoverable max sequence number, wrap-around vnode/unique/index, and transient fields such as active count, VM in-use bitmap, max sequence number, and `resstats`. Public methods include custom RVM allocation/deallocation, constructor/destructor, `init`, `ResetTransients`, `Increase_Admin_Limit`, `AllocRecord`, `DeallocRecord`, `AllocViaWrapAround`, `RecovPutRecord`, `RecovFreeRecord`, `bmsize`, `LogSize`, `purge`, `SalvageLog`, and print variants. Exported helpers are `CreateRootLog` and `CreateResLog`.

## Control Flow

Callers allocate VM log slots with `AllocRecord` or reuse slots through `AllocViaWrapAround`, then commit records to recoverable storage with `RecovPutRecord`. RVM-only methods grow/free blocks, advance recoverable sequence numbers, purge logs, and salvage allocation bitmaps. Directory vnode writeback in `cvnode.cc` creates logs when needed, while `srvproc.cc` appends, aborts, truncates, or purges records during `PutObjects`.

## State and Persistence Behavior

The class explicitly separates recoverable RVM state from transient VM state. Recoverable fields survive server restart; `ResetTransients` reconstructs VM bookkeeping. The in-use bitmaps track allocated log entries; admin limits cap log size; wrap-around fields record where old entries can be overwritten after bounded attempts.

## Dependencies and Integration Points

It depends on `bitmap`, resolution record types from `res.h`, `cvnode.h`, `volume.h`, `VolumeDiskData`, `Vnode`, `Volume`, `dlist`, and transaction annotations. Friends such as `RS_LockAndFetch`, `DumpLog`, and `DumpVolDiskData` access internals for resolution fetch and dump utilities.

## Risks and Edge Cases

Recoverable layout changes are high risk because the class stores persistent RVM data. Sequence-number growth, wrap-around selection, and bitmap synchronization between RVM and VM must remain consistent after crashes. Admin-limit growth must happen in a transaction. Friend access broadens the mutation surface and can bypass invariants.

## Test Signals

Test log creation for root and directory vnodes, record allocation/free and sequence growth, admin-limit expansion, wrap-around behavior under a full log, crash/restart `ResetTransients`, salvage bitmap repair, purge/truncate through `PutObjects`, and dump/fetch consumers reading expected records.
