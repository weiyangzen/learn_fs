## sources/distributed-fs/openafs/src/libafscp/afscp_volume.c

Purpose: Resolves AFS volumes by name or id and caches volume metadata in each `afscp_cell`. It converts VLDB entries into `afscp_volume` structures with server index lists.

Important APIs and functions: `afscp_VolumeByName` and `afscp_VolumeById`. Internal comparators `icompare` and `ncompare` key `tsearch` trees by volume id and by name plus type. `union allvldbentry` supports multiple VLDB wire formats.

Control flow: Lookup first probes the relevant cache tree. On miss, the code tries the newest VLDB entry RPC and falls back through older `N` and original formats when it receives `RXGEN_OPCODE`. It selects the requested or detected volume type, copies the volume id/name, filters server entries by VLDB flags, resolves each server by UUID or address, stores server indexes, then inserts the same volume object into both name and id caches.

State and persistence: Per-cell `volsbyname` and `volsbyid` trees cache heap allocated `afscp_volume` structures. Volumes carry stat and directory cache roots used by other files. No durable persistence.

Dependencies and integration: Depends on ubik VLDB clients, server lookup from `afscp_server.c`, AFS volume constants, and consumers in directory, file, fid, and dirops modules.

Risks: `ncompare` has a suspicious condition `if (vb->voltype < va->voltype)` instead of directly testing `va->voltype < vb->voltype`; equivalent for strict ordering in common cases but easy to misread. `afscp_VolumeById` tries `ubik_VL_GetEntryByNameU` using a decimal id string before ID fallback, which may be intentional compatibility but is surprising. Missing `nservers` or zero id returns `EIO` only in name lookup; ID lookup does not perform the same explicit validation. Tree operations are not synchronized.

Test signals: Cover cache hit paths, RW/RO/BACK selection, fallback across VLDB entry versions, UUID and IPv4 server entries, missing volume, volumes with no matching servers, id-to-type detection, and cross-check by name after id lookup.
