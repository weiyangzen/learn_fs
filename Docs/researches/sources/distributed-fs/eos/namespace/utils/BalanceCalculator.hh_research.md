# sources/distributed-fs/eos/namespace/utils/BalanceCalculator.hh

## Purpose
`BalanceCalculator.hh` defines an in-memory statistics accumulator for summarizing file data distribution by filesystem ID, EOS space, scheduling group, and size order.

## Important APIs, Types, and Functions
`BalanceCalculator` initializes several `google::dense_hash_map` members with required empty keys. `account(const std::shared_ptr<IFileMD>&)` adds one file's size to per-filesystem, per-space, per-scheduling-group, and first-location size-distribution counters. `printSummary(S&)` emits human-readable lines for each accumulated dimension.

## Control Flow
For each file location, `account()` reads the location ID and file size. Location zero is logged and skipped. It updates `filesystembalance`, uses the first nonzero location to bin size by `log10(size)`, then acquires a read lock on `FsView::gFsView.ViewMutex`, looks up the filesystem, snapshots it, and adds size to space and scheduling-group maps. `printSummary()` iterates each map and uses `StringConversion::GetReadableSizeString()` to format byte totals and averages.

## State and Persistence Behavior
All state is local to the calculator instance. It reads global filesystem view state under lock but does not modify it. Output is emitted to the caller's stream.

## Dependencies and Integration Points
Although the header does not include all visible dependencies itself, it relies on EOS file metadata, global `FsView`, filesystem snapshots, dense hash maps, XRootD string types, math functions, and common string conversion. It is likely included from contexts that already provide those definitions.

## Risks and Edge Cases
The header is sensitive to include order because dependencies are not explicit in this file. The size-bin lower-limit calculation uses `((bin) - 1) > 0`, which makes low bins display zero lower bounds. Only the first location contributes to size-distribution counts, while all locations contribute to balance volumes. Missing filesystem snapshots simply omit space/group accounting.

## Test Signals
No local tests were read. Tests should account files with multiple locations, zero location, missing filesystem view entries, and known sizes crossing powers of ten, then verify printed summaries.
