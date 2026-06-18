# sources/distributed-fs/openafs/src/butc/recoverDb.c

## Purpose
`recoverDb.c` implements the `ScanDumps` worker that scans backup tapes and optionally reconstructs BUDB dump/tape/volume records from tape labels and volume headers.

## Important APIs, Types, and Functions
`struct tapeScanInfo` carries scan labels, reconstructed dump state, initial dump id, and DB-add mode. `scanVolData()` reads one tape volume file and finds its trailer. `readDump()` scans one dump, validates fragments, queues DB entries, follows continuation tapes, and finishes tape/dump records. `readDumps()` also handles appended dumps. `getScanTape()` validates scan tape labels. `ScanDumps()` is the worker entry point. Helpers include `nextTapeLabel()`, `validatePath()`, `volumesetNamePtr()`, `extractDumpName()`, `extractTapeSeq()`, `databaseTape()`, and `RcreateDump()`.

## Control Flow
The RPC layer starts `ScanDumps()`, which takes the device latch, instantiates tape I/O, mounts an initial tape, and calls `readDumps()`. Scanning reads volume files through `scanVolData()`, creates dump/tape records lazily when valid media data is seen, queues volume rows, flushes successful complete fragments, prompts for continuation tapes, and then finishes reconstructed dump state.

## State and Persistence Behavior
Without `addDbFlag`, state is transient and printed. With `addDbFlag`, the file persists reconstructed BUDB entries via `bcdb_CreateDump`, `useTape`, `addVolume`, `finishTape`, `finishDump`, and `flushSavedEntries`. `tapepos` stores the current label position. Incomplete fragments are flushed as failed so partial volume rows are not accepted as successful.

## Dependencies and Integration Points
Uses `butm` tape APIs, format parsers from `lwps.c`, DB queue helpers, BUDB client calls, operator prompting, status/abort helpers, and naming helpers also used by dump/restore paths.

## Risks and Test Signals
Risks include trusting media headers to reconstruct BUDB, dotted numeric tape-name assumptions, old-version EOD inference from read errors, fixed-size copies, and limited path validation. Test scan with/without DB add, multi-tape and appended dump sets, corrupt/missing trailers, continuation tape mismatch, database/null/bad labels, and abort cleanup.
