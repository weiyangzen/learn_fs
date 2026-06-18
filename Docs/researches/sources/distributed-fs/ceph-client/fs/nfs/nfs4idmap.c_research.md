# sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.c

## Purpose

`nfs4idmap.c` maps between NFSv4 owner/group strings and Linux kuid/kgid values. It uses the kernel keyring id resolver, supports a legacy rpc_pipefs upcall path, handles user namespaces, maps numeric strings directly when possible, and provides helpers to map/free owner/group strings embedded in NFS file attributes.

## Important APIs, Types, and Functions

Public APIs include `nfs_idmap_init`, `nfs_idmap_quit`, `nfs_idmap_new`, `nfs_idmap_delete`, `nfs_fattr_init_names`, `nfs_fattr_free_names`, `nfs_fattr_map_and_free_names`, `nfs_map_string_to_numeric`, `nfs_map_name_to_uid`, `nfs_map_group_to_gid`, `nfs_map_uid_to_name`, and `nfs_map_gid_to_group`.

Important internal types are `struct idmap`, containing the rpc_pipefs object, pipe data, in-flight legacy upcall, mutex, and user namespace, and `struct idmap_legacy_upcalldata`, containing a pipe message, idmap message, auth key, and idmap pointer.

## Control Flow

Module initialization creates kernel credentials with a `.id_resolver` thread keyring and registers modern and legacy key types. Per-client setup allocates `struct idmap`, records the RPC credential's user namespace, creates rpc_pipefs pipe data, registers a pipe directory object, and attaches it to `clp->cl_idmap`.

Name-to-ID mapping accepts numeric strings without `@` directly; otherwise it builds a key description like `uid:name` or `gid:name`, requests `id_resolver`, and falls back to `id_legacy`. ID-to-name mapping requests `user:id` or `group:id` unless `NFS_CAP_UIDGID_NOMAP` is set, then falls back to decimal numeric strings. Legacy downcalls validate message contents before instantiating keys.

## State and Persistence Behavior

The id resolver keyring caches mapping results for `nfs_idmap_cache_timeout` seconds. Each `nfs_client` owns an `idmap` object and user namespace reference. Decoded owner/group strings live in `nfs_fattr` until mapped and freed; successful mapping sets numeric UID/GID validity bits. No mapping database is persisted by this code.

## Dependencies and Integration Points

The file depends on Linux keyrings, request-key auth, rpc_pipefs, net namespaces, user namespaces, NFS tracepoints, and NFS attribute structures. `nfs4client.c` creates/deletes per-client idmaps. `nfs4xdr.c` calls mapping functions while encoding setattr owner/group and decoding owner/group attributes. `nfs4super.c` initializes and quits the idmap subsystem.

## Risks and Edge Cases

Concurrency is restricted in the legacy path to one in-flight upcall per idmap. Downcalls must match the outstanding request to prevent wrong key instantiation. User namespace conversion can fail with invalid kuid/kgid and returns `-ERANGE`. Security-sensitive areas include key permissions, root invalidation flags, kernel credentials for request_key, and validation of userspace pipe data.

## Test Signals

Tests should cover numeric owner/group strings, domain-qualified names through request-key, legacy rpc_pipefs upcalls/downcalls, failed downcalls, cache timeout behavior, user namespace ID validity, `NFS_CAP_UIDGID_NOMAP` fallback, module init/quit cleanup, and xdr owner/group encode/decode integration.
