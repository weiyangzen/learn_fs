# sources/distributed-fs/coda/coda-src/vol/vrdb.cc

Purpose: implements the in-memory replicated volume database and conversion helpers between replicated volume ids and per-server replica ids.

Important APIs/classes: global `VRDB`; `vrtab` maintains two hash tables, by replicated volume id and by name. `CheckVRDB` reads `db/VRList`, parses entries, and populates `VRDB`. `DumpVRDB` writes current entries. `XlateVid` maps replicated ids to this server's replica id and returns count/position/type; non-replicated or replica ids are handled as pass-through with metadata. `ReverseXlateVid` maps replica id back to replicated id. `vrent` supplies host/index lookup, check-version-vector construction, `VolumeInfo` filling, network byte-order conversion, print, and dump.

Control flow/state: `VRDB.clear` removes both hash-table links before reload. `vrent::index` selects the local replica by `ThisServerId`, while `ReverseFind` scans all entries. Replicated ids are identified by high-byte pattern `0x7f`.

Dependencies/integration: used by volume location, client volume info, resolution, and test/build tools. Depends on intrusive hash/list helpers, `volume.h`, `srv.h`, server id globals, and Coda volume id encoding macros. Risks include line parse assertions killing process on malformed VRList, name hash as simple byte sum, reverse lookup O(n), and assumptions about replicated id encoding. Test signals: load valid/malformed VRList, lookup by name/id, local replica selection for each server id, reverse translation, dump/reload round trip, and `GetVolumeInfo` with missing host address.
