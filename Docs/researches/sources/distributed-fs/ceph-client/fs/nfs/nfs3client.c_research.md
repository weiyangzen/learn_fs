# sources/distributed-fs/ceph-client/fs/nfs/nfs3client.c

## Purpose
`nfs3client.c` implements NFSv3-specific server/client setup beyond the common client allocator. It binds the optional NFSv3 ACL RPC program, creates/clones NFSv3 servers with ACL capability initialization, and constructs pNFS data-server clients that speak NFSv3.

## Important APIs, Types, And Functions
When ACL support is enabled, the file defines `nfsacl_program`, backed by `nfsacl_version3`, and `nfs_init_server_aclclient()`, which binds the NFS ACL program to the server's main RPC client and links it into sysfs. Public functions are `nfs3_create_server()`, `nfs3_clone_server()`, and exported `nfs3_set_ds_client()`.

`nfs3_set_ds_client()` builds `struct nfs_client_initdata` from a metadata server, data-server address/protocol, timeouts, credentials, network namespace, and transport security settings. It fakes a hostname from the data-server address because lockd expects one, propagates `nconnect` for selected transports, preserves no-reserved-port and network-unreachable-fatal flags, marks the client as a data-server client, initializes timeout values, and calls `nfs_get_client()`.

## Control Flow And Integration Points
Common server creation flows through `nfs_create_server()` and then `nfs_init_server_aclclient()`. Clone flows through `nfs_clone_server()` and reinitializes ACL only if the source had a valid ACL client. pNFS layouts call `nfs3_set_ds_client()` to obtain or reuse a data-server `nfs_client` matching address, port, version, and namespace.

## State And Persistence Behavior
ACL capability state is stored in `server->caps` and the bound `server->client_acl` RPC client. Data-server clients are regular `nfs_client` objects with `NFS_CS_DS` set and timeouts tuned for failback through the metadata server. Transport security is inherited for TLS only when the metadata client uses non-default transport security.

## Dependencies
Dependencies include SunRPC program binding, sysfs RPC client linking, NFSv3 ACL XDR version metadata, common server allocation/cloning, net namespace state, address formatting, handshake/TLS constants, and pNFS data-server client lookup.

## Risks And Edge Cases
If ACL binding fails, ACL capability is cleared and the mount continues. The non-ACL configuration clears `NFS_MOUNT_NOACL` and `NFS_CAP_ACLS`, making behavior explicit. `nfs3_set_ds_client()` must handle address-to-string failure, TLS downgrade to TCP when the metadata client lacks transport security, and careful timeout arithmetic. Wrong flag propagation could make pNFS data-server outages fatal instead of recoverable through the MDS.

## Test Signals
Test NFSv3 mounts with and without ACL support, ACL sysfs links, cloned submounts preserving ACL capability, pNFS data-server setup across TCP/RDMA/TLS, `nconnect`, no-reserved-port mounts, and data-server timeout/failover behavior.
