## sources/distributed-fs/openafs/src/vlserver/vlserver.p.h

Purpose: private VLDB server layout header. It defines constants and persistent in-memory/on-disk structures used by `vlserver`, `vlutils`, `vlprocs`, and `vldb_check`.

Important APIs/types/functions: defines hash and allocation constants (`HASHSIZE`, `VLDBALLOCCOUNT`, `MAXSERVERID`, `BADSERVERID`, `MAXPARTITIONID`, `MAXBUMPCOUNT`, `MAXLOCKTIME`), volume-id array indexes (`RWVOL`, `ROVOL`, `BACKVOL`), entry flags (`VLFREE`, `VLDELETED`, `VLLOCKED`, `VLCONTBLOCK`), release-lock masks, and per-repsite flags. `struct vlheader` contains `vital_vlheader`, server address map, name hash table, id hash tables, and multihome extension pointer `SIT`. `struct vlentry` is the older compact entry with `OMAXNSERVERS`; `struct nvlentry` is the newer entry with `NMAXNSERVERS`. `struct extentaddr` overlays extension-block headers with multihomed address entries and exposes field aliases such as `ex_count`, `ex_hostuuid`, `ex_addrs`, and `ex_uniquifier`.

Control flow: no runtime flow; it fixes storage layout and semantic constants. The `DOFFSET` macro computes byte offsets for in-place field writes into the Ubik database.

State and persistence: most definitions here are persistent VLDB format. `vlheader`, `vlentry`, `nvlentry`, and `extentaddr` are serialized in network byte order by helper code. `VLCONTBLOCK` lets sequential scanners skip 8192-byte multihome extension blocks inside the same database file. `IpMappedAddr` entries either hold a single IP or an encoded multihome reference beginning with `0xff`.

Dependencies: includes VLDB wire definitions from `vldbint.h` and utility declarations from `afs/afsutil.h`; uses `afs_uint32`, `afs_int32`, `afsUUID`, and VLDB constants such as `MAXTYPES`, `VL_MAXNAMELEN`, `OMAXNSERVERS`, and `NMAXNSERVERS`.

Integration points: this is the shared contract between live server logic, offline checker, and generated/public RPC structures. Any layout change must coordinate byte-order conversion in `vlutils.c`, validation/repair in `vldb_check.c`, and client compatibility in conversion routines in `vlprocs.c`.

Risks: changing sizes or constants can make existing VLDB files unreadable or misinterpreted. The header mixes old and new entry formats, so `maxnservers`/version handling must remain exact. The `extentaddr` union depends on flags being in the same position as `vlentry.flags`. `MAXSERVERID` and encoded multihome sentinel values constrain future expansion.

Test signals: compile-time size/layout checks, database migration/open tests across `OVLDBVERSION`, `VLDBVERSION`, and `VLDBVERSION_4`, byte-order conversion round trips, multihome encoded address decoding, and offline `vldb_check` compatibility against live server-written databases.
