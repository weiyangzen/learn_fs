# sources/distributed-fs/ceph-client/fs/nfsd/idmap.h

## Purpose
`idmap.h` declares NFSD's NFSv4 name/id mapping interface and provides no-op lifecycle stubs when NFSv4 server support is disabled.

## Important APIs, types, and functions
The header declares `nfsd_idmap_init()`, `nfsd_idmap_shutdown()`, `nfsd_map_name_to_uid()`, `nfsd_map_name_to_gid()`, `nfsd4_encode_user()`, and `nfsd4_encode_group()`. The lifecycle functions are real only under `CONFIG_NFSD_V4`; otherwise inline stubs return success or do nothing.

## Control flow
Callers can unconditionally initialize and shut down idmapping as part of per-net NFSD setup. NFSv4 attribute encode/decode paths call the mapping helpers to translate owner/group strings to kernel ids and kernel ids to protocol strings.

## State and persistence
The header itself has no state. Enabled builds rely on per-net id-to-name and name-to-id caches stored in `struct nfsd_net`, while disabled builds eliminate that runtime state.

## Dependencies and integration points
It depends on SUNRPC service request types and kernel NFS idmap definitions. It integrates with NFSv4 ACL and attribute XDR handling, user namespace mapping, and per-net NFSD cache setup.

## Risks and test signals
Risks include enabled/disabled build drift, returning malformed owner/group names, idmapping cache misses surfacing as NFS errors, and user-namespace mismatches. Test signals include NFSv4 disabled builds, idmap cache init/shutdown per namespace, numeric and named owner/group encodes, unknown principal decode errors, and ACL paths that contain both special and named principals.
