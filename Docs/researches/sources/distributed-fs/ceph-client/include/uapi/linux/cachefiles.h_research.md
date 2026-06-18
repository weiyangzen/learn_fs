
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h

## Purpose
Defines the UAPI control protocol for CacheFiles, the local disk-cache backend used by FS-Cache/Netfs clients. It names the devnode, daemon control commands, error classes, and object-state notifications exchanged through the cachefiles control interface.

## APIs, Control Flow, and State
The header exports the cachefiles devnode name and single-character command identifiers such as bind, brun, bcull, bstop, cull, debug, dir, frun, fcull, fstop, inuse, secctx, tag, and xcalloc/xdebug/xdir/xsecctx/xstat variants. It also defines error classes like daemon bind error, daemon error, cull error, and restore error, plus state identifiers including absent, available, active, burried, and culled. The header is macro-only; control flow occurs in the cachefiles daemon and kernel control parser, where commands transition cache availability and object state. Persistent state is the on-disk cache tree and daemon policy, not the header.

## Dependencies, Integration, Risks, and Tests
Integration points are the cachefiles daemon, FS-Cache users such as network filesystems, security-context setup, cache culling, and cache restore paths. Risks include string-command compatibility, daemon/kernel version mismatch, unsafe cache-directory permissions, SELinux/security-context handling errors, and stale object-state assumptions after crashes. Test signals include cachefilesd control-command tests, FS-Cache/netfs read-through workloads, culling and restore simulations, security-context tests, and crash/restart validation of object states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h -->
