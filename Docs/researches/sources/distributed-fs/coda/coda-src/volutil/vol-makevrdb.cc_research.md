# sources/distributed-fs/coda/coda-src/volutil/vol-makevrdb.cc

## Purpose

`vol-makevrdb.cc` implements `S_VolMakeVRDB`, the volume utility RPC that translates a textual VRList into Coda's binary Volume Replication Database. The complete 131-line file was read. Its input format is a replicated group name, group volume id, VSG size, up to eight replica volume ids, and an ignored VSG address.

## Important APIs, Types, and Functions

The single service entry point is `S_VolMakeVRDB(RPC2_Handle, RPC2_String)`. It allocates `vrent` records from `vrdb.h`, fills `key`, `volnum`, `nServers`, and `ServerVolnum[]`, calls `vrent::hton()`, and writes fixed-size records to `VRDB_TEMP`.

## Control Flow

The handler creates `VRDB_TEMP`, opens the input file, scans each line with `sscanf`, validates field count and volume-name length, writes one converted `vrent` per valid line, and aborts on parse or write failure. At EOF it renames the temp file to `VRDB_PATH`, logs the number of entries, and calls `CheckVRDB()` so the fileserver refreshes replication metadata.

## State and Persistence Behavior

Persistence is a flat binary database installed by temp-file rename. The handler does not update RVM directly. It deletes each heap-allocated `vrent` after writing; on early error it closes handles but leaves cleanup of any partial temp file to later operations.

## Dependencies and Integration Points

Dependencies include `vrdb.h`, `volume.h`, `vice.h`, `volutil.h`, and RPC2 error conventions. It is the server counterpart for `volclient.cc`'s `makevrdb()` command and feeds the VRDB used by replicated-volume translation such as `XlateVid()`.

## Risks and Test Signals

Risks include accepting `servercount` without validating it against the number of parsed replica ids, fixed `line[500]`, possible stale temp file after failures, and no validation that replica ids are nonzero or unique. Tests should cover valid maximum-width VRList rows, short rows, overlong names, bad writes, rename failure, network-order round trips, and post-build `CheckVRDB()` reload behavior.
