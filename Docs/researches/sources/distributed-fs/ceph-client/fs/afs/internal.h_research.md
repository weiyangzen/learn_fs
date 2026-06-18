<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/internal.h -->
# sources/distributed-fs/ceph-client/fs/afs/internal.h

## Purpose
Central private header for the Linux kAFS client. It defines the shared in-memory model for cells, VL servers, fileservers, volumes, vnodes, calls, operation cursors, mount context, address lists, permits, callbacks, and all internal cross-file entry points.

## Important APIs, Types, And Functions
Key types include `afs_net`, `afs_cell`, `afs_vlserver`, `afs_server`, `afs_volume`, `afs_vnode`, `afs_call`, `afs_operation`, `afs_vl_cursor`, `afs_server_list`, `afs_addr_list`, `afs_endpoint_state`, `afs_permits`, and `afs_fs_context`. Inline helpers bridge VFS objects to AFS state (`AFS_FS_I`, `AFS_FS_S`, `afs_i2net`, `afs_v2net`), manage call state, cache auxiliary data, callback promises, dentry versions, inode size, and operation errors. The header declares the subsystem APIs implemented by address, cell, callback, dir, file, flock, fsclient, fs_operation, fs_probe, inode, mountpoint, proc, rotate, rxrpc, security, server, super, validation, VL, volume, write, xattr, and YFS modules.

## Control Flow
Most source files in `fs/afs` include this header and communicate through the structures it defines. Higher-level VFS operations create `afs_operation` objects, rotation code chooses servers and addresses, RxRPC call helpers send protocol operations, reply parsers update `afs_vnode_param` status/callback state, and validation/security code consume those updates.

## State And Persistence
The state is kernel-resident and mostly per network namespace, superblock, volume, vnode, server, and call. Lifetime is guarded by refcounts, active counts, RCU, workqueues, timers, seqlocks, rwsems, spinlocks, and atomics. Persistent external state is on AFS servers; local caching integrates with fscache/netfs and pagecache.

## Dependencies And Integration Points
Depends on Linux VFS, netfs, fscache, keyrings, RxRPC, DNS resolver, procfs, workqueues, timers, RCU, network namespaces, and tracepoints. It also binds AFS3, YFS, RxKAD, and RxGK protocol support.

## Risks And Edge Cases
The main risks are lifetime mismatches across RCU/refcounted objects, callback promise races, server-list replacement during operations, address/probe staleness, mount context alias switching, and subtle error prioritisation. `ASSERT*` macros can BUG the kernel when internal invariants are violated.

## Test Signals
Useful signals include successful AFS mounts, dynroot/autocell behavior, callback break handling, server failover, VLDB lookup, procfs diagnostics, tracepoint coverage, lockdep/KASAN/KCSAN, and operation retries under server/network failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/internal.h -->
