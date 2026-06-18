# sources/distributed-fs/ceph-client/fs/lockd/lockd.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/lockd.h` is the main private header for lockd. It defines debug masks, core host/request/file/block/share-facing structures, internal status constants, public cross-file prototypes, host monitor hooks, server/client integration points, and inline lock/address helpers. The source was read as a complete 452-line file.

## Important APIs, Types, and Functions

Core types include `struct nlm_host`, `struct nsm_handle`, `struct nlm_lockowner`, `struct nlm_wait`, `struct nlm_rqst`, `struct nlm_file`, and `struct nlm_block`. Important inlines include `nlm_addr`, `nlm_srcaddr`, `nlmsvc_file_file`, `nlmsvc_file_inode`, `nlmsvc_file_cannot_lock`, `nlm_privileged_requester`, `nlm_compare_locks`, and `lockd_set_file_lock_range4`. The header declares client, host, monitor, server lock, server file, share, and lock-manager entry points.

## Control Flow

The header does not execute flow directly, but it defines how modules communicate. Client code allocates `nlm_rqst`, binds `nlm_host`, and uses `nlm_wait` for GRANTED callbacks. Server code uses `nlm_file` and `nlm_block` to manage NFS-exported file locks. NSM monitor code maps `nsm_handle` into reboot handling. Inline privileged-request helpers enforce loopback plus privileged-port checks for sensitive operations.

## State and Persistence Behavior

All state is in memory and refcounted: hosts own RPC clients and lock lists, NSM handles own monitor identity, requests own wire argument/result buffers, files own open VFS files and share/block lists, and blocks own callback/deferred request state. Constants define wire and internal-only statuses.

## Dependencies and Integration Points

The header depends on exportfs, socket address types, VFS file locking, SUNRPC service/client headers, NLM XDR structures, and the public lockd bind API. It is included across nearly all lockd implementation files.

## Risks and Edge Cases

Changing structure layout or ownership semantics affects many files. `nlm_compare_locks` treats `F_UNLCK` in the second lock as a wildcard. `lockd_set_file_lock_range4` must handle length zero and arithmetic overflow as EOF. Privileged requester checks intentionally accept only local privileged ports.

## Test Signals

Signals include allmodconfig/build coverage, sparse type checks for network-byte-order statuses, lock range conversion boundary tests, privileged requester tests for IPv4/IPv6 loopback and mapped addresses, and integration tests that exercise client and server structure lifetimes.
