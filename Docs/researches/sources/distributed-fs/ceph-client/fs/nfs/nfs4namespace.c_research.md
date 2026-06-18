# sources/distributed-fs/ceph-client/fs/nfs/nfs4namespace.c

## Purpose

`nfs4namespace.c` implements NFSv4 namespace-specific behavior: converting NFSv4 path components to POSIX paths, validating fs_locations referrals, negotiating security on WRONGSEC, following referrals by trying returned server locations, parsing server names, handling submounts, and replacing transports during filesystem migration.

## Important APIs, Types, and Functions

Public functions are `nfs_parse_server_name`, `nfs4_negotiate_security`, `nfs4_submount`, and `nfs4_replace_transport`. Internal helpers include `nfs4_pathname_len`, `nfs4_pathname_string`, `nfs_path_component`, `nfs4_path`, `nfs4_validate_fspath`, `nfs_find_best_sec`, `try_location`, `nfs_follow_referral`, `nfs_do_refmount`, and `nfs4_try_replacing_one_location`.

## Control Flow

Referral handling starts in `nfs4_submount`. The code re-lookups the mountpoint with `nfs4_proc_lookup_mountpoint` to obtain attributes and selected security flavor. If the attributes indicate a referral, `nfs_do_refmount` fetches `fs_locations`, validates that the server-provided `fs_root` prefixes the current dentry path, then iterates locations and server lists. `try_location` updates the fs_context hostname/export path/source, parses a server address, sets the NFS port, and calls `nfs4_get_referral_tree` until one succeeds.

Security negotiation uses `nfs4_proc_secinfo` to fetch server-supported flavors for a lookup name, then searches them in server-returned order for a locally supported flavor allowed by the mount's `sec=` list. Transport replacement for migration iterates fs_locations, parses server addresses, duplicates hostnames, and calls `nfs4_update_server` for the first usable location.

## State and Persistence Behavior

Most mutations are to transient `fs_context` fields while preparing referral mounts: hostname, export path, source string, address, and selected flavor. Migration mutates the live `nfs_server` indirectly through `nfs4_update_server`, replacing its transport/client association. There is no durable local namespace state.

## Dependencies and Integration Points

The file depends on VFS dentry/mount/fs_context structures, SUNRPC client/auth/address helpers, NFS DNS resolution, NFSv4 procedure calls for SECINFO/FS_LOCATIONS/LOOKUP mountpoints, and `nfs4client.c` server update/referral creation paths. `nfs4proc.c` wires `nfs4_submount` into NFSv4 inode operations.

## Risks and Edge Cases

Path validation prevents following referrals whose `fs_root` does not prefix the current mounted path, but it depends on correct path rendering and length checks. IPv6 scoped addresses containing a scope delimiter are skipped. `nfs_find_best_sec` must shut down cloned RPC clients when credential setup fails. Migration transport replacement assumes the server is quiescent.

## Test Signals

Tests should cover referrals with multiple locations/servers, invalid fs_root prefixes, DNS and IPv6 literal parsing, secinfo negotiation with mount `sec=` filtering, WRONGSEC recovery, submounts without referral attributes, migration to a new address, failed cloned auth credentials, and exhausted fs_locations returning `-ENOENT`.
