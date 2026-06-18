# sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.hh

## Purpose
`MultiSpaceTapeGc.hh` declares the multi-space tape-aware garbage-collector coordinator. It is the MGM-facing object that receives lifecycle calls, file access notifications, statistics requests, and FSCTL diagnostics.

## Important APIs, Types, And Functions
The class exposes constructor/destructor, deleted copy/assignment, exceptions `GcAlreadyStarted` and `GcIsNotEnabled`, `setTapeEnabled()`, `start()`, `stop()`, `isGcActive()`, file event methods for write/read/convert, `getStats()`, and `handleFSCTL_PLUGIO_tgc()`. Private helpers include `workerThreadEntryPoint()`, `populateGcsUsingQdb()`, and `dispatchFileAccessedToGc()`.

## Control Flow
The header defines a two-stage lifecycle: enable spaces, then start GC. Start creates per-space GC objects and launches population/worker startup; stop joins and destroys them. Event methods are no-ops until tape support is enabled and metadata population is complete.

## State And Persistence
Private state includes atomic flags, an `ITapeGcMgm` reference, `SpaceToTapeGcMap`, stop flag, startup mutex, worker thread, population flag, and configured spaces. All state is in memory and rebuilt on startup.

## Dependencies And Integration Points
The class depends on XRootD FSCTL types, EOS identities, `ITapeGcMgm`, `SpaceToTapeGcMap`, `TapeGcStats`, and namespace file IDs. It is owned by `XrdMgmOfs` and called from MGM file, conversion, and admin-control paths.

## Risks And Edge Cases
Thread lifecycle is sensitive: the coordinator owns one worker while per-space `TapeGc` objects own their own workers. Atomic flags and mutex-protected startup must stay consistent across start/stop/restart. Header comments contain minor typos, but the API contract is clear.

## Test Signals
Tests should cover lifecycle exceptions, idempotent stop/destructor behavior, configured-space accumulation, active flag semantics, and FSCTL behavior with local/non-local identities.
