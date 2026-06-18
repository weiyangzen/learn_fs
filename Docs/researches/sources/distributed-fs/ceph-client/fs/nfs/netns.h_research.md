# sources/distributed-fs/ceph-client/fs/nfs/netns.h

## Purpose
`netns.h` defines NFS-private per-network-namespace state accessed through `net_generic()` and `nfs_net_id`. It keeps NFS client lists, callback identity state, block-layout upcall state, RPC stats, and optional procfs roots isolated per network namespace.

## Important APIs, Types, And Functions
`struct bl_dev_msg` represents a block-layout device upcall reply with status and major/minor numbers. `struct nfs_net` is the primary type. It includes DNS resolver cache state, block device pipe/reply/wait/mutex fields, `nfs_client_list`, `nfs_volume_list`, NFSv4-only callback IDR and callback ports, callback user counts by minor version, data-server cache and lock, a namespace-level `nfs_netns_client`, `nfs_client_lock`, boot time, RPC stats, and optional procfs entry.

## Control Flow And Integration Points
Client allocation, lookup, trunking discovery, sysfs/procfs reporting, callback service setup, and pNFS data-server cache management use `struct nfs_net`. In this work item, `nfs40client.c` obtains `struct nfs_net` to manipulate `cb_ident_idr` and walk `nfs_client_list`; `nfs3client.c` includes the header for namespace integration; `internal.h` declares procfs init/exit hooks that populate namespace state.

## State And Persistence Behavior
All fields live for the lifetime of the network namespace. Lists and IDRs are protected by `nfs_client_lock` or other field-specific locks. `boot_time` provides namespace-level timing context. Callback port/user fields persist while NFSv4 callback services are active.

## Dependencies
Dependencies include network namespace generic storage, SunRPC stats and pipes, NFSv4 constants, Linux IDR/list/spinlock/mutex/waitqueue primitives, and procfs when enabled.

## Risks And Edge Cases
Per-net isolation is critical; using global state instead would leak clients across namespaces. Lock ordering around `nfs_client_lock`, callback ID replacement, and list walking must remain consistent. Optional NFSv4 fields are compile-time gated, so non-v4 builds must not reference them.

## Test Signals
Run mounts in multiple network namespaces, NFSv4 callback setup and teardown, trunking discovery under namespace isolation, pNFS data-server cache operations, procfs visibility per namespace, and lockdep on client list and callback IDR operations.
