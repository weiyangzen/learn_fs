# sources/distributed-fs/coda/coda-src/venus/venusrecov.h

## Purpose
This header defines the recoverable storage contract for Venus: RVM/VM defaults, persistent global root layout, transaction helpers, flush/truncate APIs, and pointer validation.

## Important APIs, Types, and Functions
It declares constants for default/unset RVM type, data/log sizes, RDS chunk/list counts, flush/truncate periods and sizes, magic/version numbers, and `RecovVenusGlobals`. `RecovVenusGlobals` stores persistent roots for FSDB, VDB, RealmDB, and HDB plus heap bounds, clean-shutdown state, UUID/store id, and validation/print methods. It declares global recovery configuration and functions including `Recov_BeginTrans`, `_Recov_BeginTrans`, `Recov_EndTrans`, `Recov_SetBound`, `RecovInit`, `RecovFlush`, `RecovTruncate`, `RecovTerminate`, `RecovPrint`, RPC2 string helpers, `RECOVD_Init`, `RecovDaemon`, and `Recov_GenerateStoreId`.

## Control Flow
The macro `Recov_BeginTrans()` captures caller file/line and delegates to `_Recov_BeginTrans`. Callers bracket persistent mutations with begin/end, then pass a flush bound to `Recov_EndTrans()`. Recovery initialization must precede modules that dereference `rvg` persistent roots.

## State and Persistence Behavior
This header is the authoritative layout for persisted Venus globals. `RecovVersionNumber` changes are format changes. `VALID_REC_PTR` enforces that persistent root pointers lie inside the loaded RDS heap. `VenusGenID` aliases part of `recov_UUID`.

## Dependencies and Integration Points
It depends on RPC2, rvmlib, Venus private declarations, and forward declarations of persistent database types. It is included by almost every module that touches RVM state.

## Risks and Test Signals
Risks include format-version drift, macro aliasing of UUID fields, and pointer validation only checking heap bounds rather than object type. Tests should verify fresh and recovered `RecovVenusGlobals` layouts, valid/invalid pointer detection, and that persistent root fields are initialized before dependent subsystem init.
