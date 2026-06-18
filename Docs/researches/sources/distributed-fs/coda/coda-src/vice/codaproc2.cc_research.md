# sources/distributed-fs/coda/coda-src/vice/codaproc2.cc

## Purpose
`codaproc2.cc` implements server-side reintegration of disconnected client mutations. It receives a client modification log, validates and replays CML records atomically against the local volume, performs or defers file-data transfers, records resolution logs, updates COP/version-vector state, and returns volume version/callback status.

## Important APIs, types, and functions
- `struct rle` is the parsed reintegration-log entry. It stores opcode, store ID, mtime, up to three fids/VVs, names, and opcode-specific fields for create, mkdir, symlink, remove, rmdir, store, setattr, and rename.
- `FS_ViceReintegrate` is the full reintegration RPC. It processes piggybacked COP2 data, validates parameters, gathers objects, checks/performs operations, and releases/finalizes state.
- `FS_ViceOpenReintHandle`, `FS_ViceQueryReintHandle`, `FS_ViceSendReintFragment`, and `FS_ViceCloseReintHandle` support staged transfer of large store data into a temporary inode before replaying a single-store reintegration.
- `ValidateReintegrateParms` translates volume IDs, fetches and unpacks the client reintegration log via RPC2 side effects, checks duplicate/retry store IDs, and obtains the volume in exclusive mode.
- `GetReintegrateObjects` preallocates created vnodes, builds the fid-ordered `vlist`, resolves parent/child fids by name where needed, and locks existing vnodes.
- `CheckSemanticsAndPerform` walks the log in client order, calls operation-specific semantic checks, applies mutations with `Perform*` helpers, spools resolution records, adjusts disk usage, and fetches deferred store data.
- `PutReintegrateObjects` frees log memory, finalizes COP/version state with `ReintFinalCOP`, reports stale directories, persists through `PutObjects`, and updates the volume's reintegrator replay-detection table.
- `AddChild`, `LookupChild`, and `AddParent` are helper routines also useful to repair code.
- `ReintNormalVCmp`, `ReintPrelimCOP`, `ReintFinalCOP`, and `ValidateRHandle` encode reintegration-specific version comparison, preliminary store-id stamping, final COP1/COP2 handling, and temporary handle validation.

## Control flow
The file documents reintegration as four phases. Phase 0 optionally drains piggybacked COP2. Phase 1 receives a serialized CML log into memory, unpacks entries into a linked list, translates fids from VSG to local RW volume IDs, checks replay history, validates optional reintegration handles, and locks the volume exclusively. Phase 2 allocates vnodes for creates, builds a complete fid set including parents and named children, then acquires existing objects in fid order to avoid deadlocks. Phase 3 replays each record: stores prepare a replacement inode and delay bulk transfer; setattr/create/remove/link/rename/mkdir/rmdir/symlink check semantics, update weak-equality state, perform mutations, mark stale directories, spool VM log records, and adjust block accounting. At the end of phase 3, store data is fetched back from the client under the host lock unless it was pre-sent through a reintegration handle. Phase 4 frees the parsed log, finalizes COP state, returns stale directory/version status, puts objects, and releases the exclusive volume lock.

## State and persistence behavior
The file mutates persistent vnode metadata, directory contents, file inode references, volume disk usage, resolution logs, volume version vectors, COP-pending entries, and the per-volume `reintegrators` replay table. Store reintegration can create temporary server-side inodes via `icreate`; failed side effects truncate or discard intermediate data. Successful finalization calls `NewCOP1Update` for each mutated vnode and either adds pending COP entries or spools `ResolveNULL_OP` for directories needing resolution.

## Dependencies and integration points
It depends on RPC2 side effects, callback fetches, LWP scheduling via `PollAndYield`, RVM/volume/vnode management, `coppend`, `lockqueue`, VRDB/VLDB translation, CML unpackers, `operations.h` check/perform functions, resolution-log spooling, `inconsist.h`, and callback host locks. It calls helpers from `codaproc.cc` such as `FS_ViceCOP2`, `GetMyVS`, `SetVSStatus`, `NewCOP1Update`, and `PollAndYield`.

## Risks
The replay path is high risk because it combines client-supplied serialized data, name-to-fid lookups that can change during replay, persistent mutation, bulk transfer, and manual memory cleanup. The code uses raw `malloc/free/strdup`, assumes a valid exclusive volume lock across phases, and relies on `Index` for partial failure reporting. Delayed store transfer means semantic mutations happen before file bytes arrive, so failure cleanup must be exact. Replay detection depends on store-id uniquifier ranges and can be disabled by clients using large uniquifiers. Several comments call out historical retry and rename-version comparison uncertainties.

## Test signals
Test disconnected replay for every CML opcode, mixed-operation atomicity, repeated reintegration retry detection (`VLOGSTALE`), staged store handles including partial fragments and old server start times, failed callback fetch rollback, stale directory reporting, block accounting, weak-equality file stores, and RVM crash recovery. Logs around `ValidateReintegrateParms`, `GetReintegrateObjects`, `CheckSemanticsAndPerform`, `SpoolVMLogRecord`, and `CBFetch` are primary diagnostics.
