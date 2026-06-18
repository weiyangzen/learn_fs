# sources/distributed-fs/openafs/src/WINNT/afsd/test/btreetest.c

## Purpose
Standalone Windows test harness for OpenAFS B+ directory tree and filename normalization lookup behavior. It verifies exact, inexact, and ambiguous-style directory matching with Unicode normalization and 8.3 aliases.

## Important APIs, Types, And Functions
Provides fake `cm_SetFid`, `cm_FindSCache`, `cm_ReleaseSCache`, `cm_ApplyDir`, and `afsi_log`. `initialize_tests` initializes OSI, normalization, B+ dir support, and fake logging. `simple_test` uses `initBtree`, inserts normalized names and generated 8.3 aliases, then uses `bplus_Lookup`, `getSlot`, data-node iteration, and `comparekeys(..., EXACT_MATCH)`.

## Control Flow
`wmain` runs initialization and `simple_test`. Each row inserts filesystem strings as normalized/client forms, then looks up a client string. Exact match returns success, a single non-exact candidate returns `CM_ERROR_INEXACT_MATCH`, multiple candidates would be ambiguous, and missing entries return `ENOENT`.

## State And Persistence
All state is in-memory: B+ tree nodes, fake scache/fid values, and counters. No disk/cache persistence.

## Dependencies And Integration Points
Includes `afsd.h` and uses normalization, 8.3 generation, directory B+ tree, locks, and OSI logging. It validates directory lookup behavior used by the Windows cache manager.

## Risks
Fake cache functions can mask integration bugs. Exit status/reporting is limited. Unicode coverage is useful but not comprehensive.

## Test Signals
Expected run has zero failed tests and matching vnode IDs. Additional ambiguity, deletion, duplicate short-name, and real enumeration cases would strengthen coverage.
