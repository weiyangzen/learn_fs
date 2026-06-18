# sources/distributed-fs/openafs/src/afs/AIX/osi_vnodeops.c

## Purpose
This file is the AIX vnode and VFS operation adapter for the OpenAFS cache manager. It translates AIX gnode/vnode/VFS callbacks into the portable AFS operations, manages the AIX VM segment path for file I/O, queues asynchronous buffers for background daemons, and exports both raw and global-lock-wrapped operation tables.

## Important APIs, Types, And Functions
The public vnode entry points are `afs_gn_lookup`, `afs_gn_create`, `afs_gn_open`, `afs_gn_close`, `afs_gn_rdwr`, `afs_gn_fsync`, `afs_gn_fclear`, `afs_gn_ftrunc`, directory mutators, symlink/readlink, `afs_gn_lockctl`, `afs_gn_ioctl`, `afs_gn_strategy`, and unsupported ACL/PCL/revoke slots. `afs_vm_rdwr` is the VM-backed read/write engine, while `afs_direct_rdwr` handles 64-bit offsets beyond `afs_vmMappingEnd`. `afs_gn_vnodeops`, `locked_afs_gn_vnodeops`, `locked_Afs_vfsops`, and `afs_gfs` are the integration objects AIX consumes.

## Control Flow
Most vnode operations acquire arguments in AIX form, compute OpenAFS flags or `vattr` values, call the common `afs_*` function, trace the result, and return AIX errno values. Open/create perform access checks, non-share waiting on `tvp->opens`, fake open setup for NFS translator paths, and truncation if requested. Reads/writes verify the vcache, flush stale pages, save credentials for later daemon work, select VM or direct I/O, fake open/close writes where AIX does not provide normal open/close RPCs, and optionally return fresh attributes. The strategy path receives a linked buffer list, inserts buffers into the global async queue by vnode/subspace/block order, merges compatible adjacent buffers, and wakes the async daemon.

## State And Persistence
State is stored in `struct vcache` fields such as `segid`, `vmh`, `credp`, `opens`, `vc_error`, `f.states` bits (`CDirty`, `CMAPPED`, `CNSHARE`, `CPageHog`), length/date metadata, and the attached AIX gnode segment. Global async I/O state uses `afs_asyncbuf`, `afs_asyncbuf_lock`, `afs_asyncbuf_cv`, and monotonic `afs_biotime`. The file also maintains `vmPageHog` accounting for very large writes. VFS global state is mostly delegated to `Afs_vfsops`, but the locked wrapper tables persist the correct AIX registration view.

## Dependencies And Integration Points
The file depends on AIX vnode, gnode, VM, shared-memory, buffer, and VFS APIs; OpenAFS cache-manager APIs for lookup, access, create, open, read/write, partial writeback, locking, ioctl, and inactive handling; global AFS locking; ICL tracing; and NFS translator credential conventions. It is the AIX platform bridge for normal filesystem syscalls, mmap-like segment use, NFS server reentry, and background cache I/O.

## Risks
The highest-risk behavior is lock and reference ordering around the global AFS lock, vcache locks, AIX VM segment calls, and asynchronous buffer queues. Errors in fake open/close or saved credential handling can corrupt writer counts or use stale credentials. VM/direct mixed I/O near `afs_vmMappingEnd`, page protection around extending writes, quota/error propagation through `vc_error`, and buffer merging in `afs_gn_strategy` are fragile. Many function-pointer casts and AIX-version conditionals make ABI drift risky.

## Test Signals
Useful signals include successful AIX mount/root/statfs/unmount flows, create/open/truncate/close with `FTRUNC` and `FNSHARE`, NFS translator reads/writes, large writes crossing chunk and VM mapping boundaries, mmap/map/unmap reference counts, lockctl get/set/unlock, ioctl redirection, async strategy queue draining, forced shutdown, and recovery from `EDQUOT`/`ENOSPC`. Trace counters (`AFS_STATCNT`) and ICL events should match syscall activity without leaked vnodes, credentials, or buffers.
