# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose
This file provides the rpc_pipefs upcall channel used by the pNFS block layout driver to resolve legacy simple block-volume signatures into local block device major/minor numbers. It creates a per-network-namespace pipe, handles pipefs mount/unmount notifications, sends mount requests to userspace, and receives downcall replies.

## Important APIs, types, and functions
The public lifecycle functions are `bl_init_pipefs()` and `bl_cleanup_pipefs()`. Device resolution is exposed as `bl_resolve_deviceid()`. Per-net operations are implemented by `nfs4blocklayout_net_init()` and `nfs4blocklayout_net_exit()`, while pipefs event handling uses `rpc_pipefs_event()`.

`bl_pipe_downcall()` copies a `struct bl_dev_msg` reply from userspace into `nn->bl_mount_reply`; `bl_pipe_destroy_msg()` wakes the waiter if an upcall is destroyed with an error. `nfs4_encode_simple()` builds the XDR-like simple volume payload placed after `struct bl_msg_hdr`.

## Control flow
At module initialization, the file registers a pipefs notifier and pernet subsystem. Each network namespace initializes `bl_mutex`, `bl_wq`, creates pipe data with `bl_upcall_ops`, and registers `nfs/blocklayout` in rpc_pipefs if pipefs is already mounted. Later mount/unmount events create or unlink the dentry.

`bl_resolve_deviceid()` serializes requests with `nn->bl_mutex`, appends a single-volume wrapper length, allocates an upcall buffer, queues it through `rpc_queue_upcall()`, sleeps uninterruptibly on `bl_wq`, and inspects `nn->bl_mount_reply`. A successful reply returns `MKDEV(reply->major, reply->minor)`.

## State and persistence behavior
State is per-net in `struct nfs_net`: `bl_device_pipe`, `bl_mutex`, `bl_wq`, and the most recent `bl_mount_reply`. There is no persisted kernel state, but the userspace helper's device choice influences subsequent block-device opens in `dev.c`.

## Dependencies and integration points
The file depends on SUNRPC rpc_pipefs, pernet operations, NFS netns storage, and blocklayout message structures. It integrates with `dev.c` through `bl_resolve_deviceid()` and with userspace through the `nfs/blocklayout` rpc_pipefs node.

## Risks and test signals
Risks include uninterruptible wait hangs if userspace never replies and pipe destruction does not fire, serialized request bottlenecks, stale shared reply storage, PAGE_SIZE request limits, and module/netns lifetime races around pipefs events. Tests should exercise pipefs mounted before and after module load, userspace success and malformed downcall sizes, queue failure wakeups, netns teardown, and simple-volume mount failure behavior.
