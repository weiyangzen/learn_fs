# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/default-args.h

## Purpose
Declares helpers that copy translator FOP input arguments and callback results into `default_args_t` and `default_args_cbk_t`. These snapshots support call stubs, wind/resume paths, default pass-through translators, and retry/deferred execution paths.

## APIs, Types, and Functions
The file provides `args_*_store()` for nearly every filesystem operation: lookup/stat/truncate/access, namespace operations, open/create/readv/writev, xattrs, locks, directory reads, checksums, setattr/fallocate/discard/zerofill, ipc/seek/lease, active-lock migration, icreate/namelink, and copy-file-range. Matching `args_*_cbk_store()` helpers store callback outputs including `iatt` pre/post buffers, inodes, fds, dicts, dirents, checksums, leases, and lock lists. `args_wipe()`, `args_cbk_wipe()`, and `args_cbk_init()` manage cleanup and initialization.

## Control Flow, State, and Persistence
Callers build a stack-local or heap call-stub argument object, invoke the appropriate store helper before winding, and later resume or unwind using the saved fields. The state is transient but ownership-sensitive: locs, dicts, iobrefs, fds, and inodes need correct ref/unref behavior in implementations.

## Dependencies and Integration
Depends on `defaults.h` types, `dict_t`, `loc_t`, `fd_t`, `inode_t`, `iatt`, `gf_flock`, dirents, leases, and lock migration structures. It integrates directly with the `default_*` entry points and the translator stack/call-stub framework.

## Risks and Test Signals
Risks include missing deep references, stale pointers to caller-owned data, incorrect paired cleanup, and signature drift when a FOP is extended. Test signals include call-stub replay tests, leak/refcount checks on dict/fd/inode/iobref fields, fault-injection paths through every `args_*_store()`, and compile failures when FOP prototypes change.
