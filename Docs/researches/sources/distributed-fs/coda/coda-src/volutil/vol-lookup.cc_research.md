## sources/distributed-fs/coda/coda-src/volutil/vol-lookup.cc

Purpose: `vol-lookup.cc` returns human-readable VLDB/location information for a volume specified by name or id.

Important APIs/types/functions: RPC `S_VolLookup` writes `/tmp/vollookup.tmp` and transfers it with SMARTFTP. It uses `VGetVolumeInfo`, `HashLookup`, `SRV_RVM(VolumeList[index]).data.volumeInfo`, `gethostbyaddr`, and a local `voltypes` string table.

Control flow: initialize volutil, open temp output, parse the input as a hex volume id if possible and present in the volume hash, otherwise treat it as a name. Fetch `VolumeInfo`, print primary volume id/type, associated read-write/readonly/backup ids, and server hostnames, then transfer the temp file to the client.

State and persistence behavior: read-only against volume/VLDB state. Creates/overwrites fixed `/tmp/vollookup.tmp` on the server.

Dependencies/integration points: depends on volume hash, VLDB, volume info service, host DNS lookup, RPC2 side effects, and server RVM volume list state.

Risks: fixed temp filename is unsafe under concurrency. If `VGetVolumeInfo` fails, the function jumps to exit without closing `infofile`, leaking the descriptor and leaving a partial file. `status` is never set on lookup error, so error return behavior can be misleading. Hostname output skips numeric fallback when reverse lookup fails.

Test signals: lookup by name, by hex id, invalid key, missing reverse DNS, multi-server replicated volumes, concurrent lookups, and side-effect failure. Check descriptor cleanup on errors.
