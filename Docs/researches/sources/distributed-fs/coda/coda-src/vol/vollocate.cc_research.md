# sources/distributed-fs/coda/coda-src/vol/vollocate.cc

Purpose: resolves a user-supplied volume key to a local replica/non-replicated volume id.

Important APIs: `VOL_Locate(char *volkey)` tries replicated volume name via `VRDB.find(char *)`, replicated volume id via hex parse and `VRDB.find(VolumeId)`, replica/non-replicated volume name via `VLDBLookup`, and finally returns the parsed numeric id if available. Helper `VREtoVolRepId` selects this server's replica from a `vrent`.

Control flow/state: resolution prioritizes VRDB group names/ids, then VLDB replica names, then raw numeric fallback. `vrent::index()` uses `ThisServerId`, so results are server-local.

Dependencies/integration: depends on server globals, VRDB, VLDB, volume hash types, and `vcrcommon`. Risks include accepting partial `strtoul` parses, returning zero for missing local replica, and ambiguity between hex numeric strings and names. Test signals: locate replicated name, replicated id, replica name, non-replicated numeric id, unknown key, and server without group membership.
