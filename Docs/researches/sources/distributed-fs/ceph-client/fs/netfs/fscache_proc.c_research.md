<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_proc.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_proc.c

## Purpose
Creates the FS-Cache procfs inspection interface under the netfs proc tree and a compatibility symlink `/proc/fs/fscache` to `/proc/fs/netfs`.

## Important APIs, Types, And Functions
Defines `fscache_proc_init()` and `fscache_proc_cleanup()`. It installs seq files for `fs/netfs/caches`, `fs/netfs/volumes`, and `fs/netfs/cookies` using seq operations from cache, volume, and cookie code.

## Control Flow
Initialization creates the symlink first, then each seq file. Any failure removes the symlink and returns `-ENOMEM`. Cleanup removes the `fs/fscache` subtree; the broader `fs/netfs` subtree is owned by netfs main initialization and cleanup.

## State And Persistence
No persistent storage. Runtime visibility reflects global cache, volume, and cookie lists guarded in their respective modules.

## Dependencies And Integration Points
Depends on `CONFIG_PROC_FS`, procfs helpers, `seq_file`, and `internal.h` declarations for `fscache_caches_seq_ops`, `fscache_volumes_seq_ops`, and `fscache_cookies_seq_ops`. Called by FS-Cache init/exit.

## Risks
Partial proc creation failures are simple but only remove the symlink by name; ownership with netfs main proc tree must stay aligned. Seq operation providers must remain valid for the lifetime of proc entries.

## Test Signals
With procfs enabled, verify `/proc/fs/fscache` symlink, `caches`, `volumes`, and `cookies` files exist after load and are removed on unload. Failure injection in proc creation should not leave stale entries.
