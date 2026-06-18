# sources/distributed-fs/coda/coda-src/volutil/vol-makevldb.cc

## Purpose

`vol-makevldb.cc` implements the server-side `S_VolMakeVLDB` RPC used by `volutil makevldb` to rebuild Coda's binary Volume Location Database from a textual VolumeList. The complete 552-line file was read. It converts read-write, read-only, backup, and non-replicated volume records into hash-indexed `struct vldb` entries, writes `VLDB_TEMP`, atomically renames it to `VLDB_PATH`, and asks the fileserver to reload volume-location state.

## Important APIs, Types, and Functions

The public entry point is `S_VolMakeVLDB(RPC2_Handle, RPC2_String)`. Core helpers are `Pass()`, `VolumeEntry()`, `AddReadWriteEntry()`, `AddReadOnlyEntry()`, `AddBackupEntry()`, `Lookup()`, `Add()`, `Replace()`, `AddServer()`, `AddAssociate()`, `CheckRWindex()`, and `GetArgs()`. File-level state includes `vldb_array`, `Dates`, `RWindex`, `vldbSize`, `vldbHashSize`, `haveEntry`, and `AddedEntries`. `InitAddEntry()` maps Coda volume types to per-type add handlers.

## Control Flow

`S_VolMakeVLDB` opens the input file, runs `Pass('P')` to count lines, allocates an oversized in-memory VLDB/hash array, and then replays the file in type order: read-write, read-only, backup, then non-replicated. Each data pass parses single-letter fields such as `I`, `H`, `W`, `D`, `B`, and `C`, creates both numeric-key and name-key entries, and lets type-specific handlers decide whether to add, replace, or merge with existing entries. After header initialization, the whole array is written to `VLDB_TEMP`, renamed, and `VCheckVLDB()` is called.

## State and Persistence Behavior

Persistence is file-based rather than RVM-based. The rebuilt database is staged in a temporary file and installed with `rename()`. VLDB entries store network-order volume ids and a hash-chain stride in `hashNext`; copy, backup, or creation dates are kept only in the transient `Dates` array to select newest entries. Read-only servers are merged into a single entry when creation dates match, and associated read-only/backup ids are copied into matching read-write entries through `RWindex`.

## Dependencies and Integration Points

The file depends on `vldb.h`, `voltypes.h`, `voldefs.h`, `volume.h`, `vutil.h`, `srv.h`, `vice_file.h`, RPC2 error codes, and `HashString()`. It is invoked by the generated volutil RPC stub and by the client command in `volclient.cc`. It integrates with the fileserver through `VCheckVLDB()`.

## Risks and Test Signals

Risks include fixed-size line/argument buffers, no bounds check while probing for the next free hash slot, limited error propagation from `Pass()`, possible `nServers` overflow in `AddServer()`, and full-array binary writes that rely on exact on-disk struct layout. Useful tests include VolumeList fixtures for all four volume classes, duplicate/newer backup handling, read-only server merging, malformed field rejection, hash collision stress, temp-file rename failure, and reload notification verification.
