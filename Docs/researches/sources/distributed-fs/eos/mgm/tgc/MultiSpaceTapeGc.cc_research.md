# sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.cc

## Purpose
`MultiSpaceTapeGc.cc` implements the coordinator for tape-aware garbage collection across multiple EOS spaces. It enables spaces, starts one population worker, dispatches file access events to per-space GCs, exposes stats and JSON diagnostics, and coordinates shutdown.

## Important APIs, Types, And Functions
Implemented methods include constructor/destructor, `setTapeEnabled()`, `start()`, `stop()`, `isGcActive()`, `fileOpenedForWrite()`, `fileOpenedForRead()`, `fileConverted()`, `dispatchFileAccessedToGc()`, `getStats()`, `handleFSCTL_PLUGIO_tgc()`, `workerThreadEntryPoint()`, and `populateGcsUsingQdb()`.

## Control Flow
`setTapeEnabled()` records configured spaces. `start()` validates enablement and inactive state, creates per-space `TapeGc` objects, starts the multi-space worker, and marks active. The worker scans QuarkDB via `ITapeGcMgm::getSpaceToDiskReplicasMap()`, feeds file IDs into each space GC's LRU, marks population complete, then starts each space GC worker. File-open and conversion callbacks ignore events until tape is enabled and population is complete, then call `gc.fileAccessed()`. `stop()` sets the stop flag, joins the worker, destroys all GCs, and clears active/populated flags.

## State And Persistence
State is process-local: atomic enable/active/stop/populated flags, configured space set, startup mutex, worker thread, and `SpaceToTapeGcMap`. The coordinator rebuilds in-memory LRUs from QuarkDB at startup; it does not persist them itself.

## Dependencies And Integration Points
The coordinator is constructed by `XrdMgmOfs` with `RealTapeGcMgm`. File open paths in `XrdMgmOfsFile`, conversion jobs, admin stats (`NsCmd`), and `cmd=SFS_FSCTL_PLUGIO arg1=tgc` diagnostics integrate with it. It depends on `TapeGc`, `SpaceToTapeGcMap`, `ITapeGcMgm`, XRootD error buffers, and EOS logging.

## Risks And Edge Cases
`fileOpenedForRead()` and `fileConverted()` use `if (!m_tapeEnabled && !m_gcsPopulatedUsingQdb)` while write uses `||`; the read/convert condition allows dispatch when only one flag is false, likely before full readiness. `handleFSCTL_PLUGIO_tgc()` allocates a reply but leaks it on `MaxLenExceeded` before buffer ownership transfer, and uses `strlen(reply + 1)`, apparently skipping the first byte when setting length. `m_stop` is not reset in `start()`, so restarting after stop can make the new worker exit population immediately. Exceptions in the worker leave `m_gcIsActive` true until explicit stop.

## Test Signals
Existing `MultiSpaceTapeGcTests` cover construction and start/stop variants. Additional tests should cover readiness gating for read/convert events, restart after stop, FSCTL unauthorized and maxLen paths, reply length correctness, worker failure states, population stop requests, and event dispatch to unknown spaces.
