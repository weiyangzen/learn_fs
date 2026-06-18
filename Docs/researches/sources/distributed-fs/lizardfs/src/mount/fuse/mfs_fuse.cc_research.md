# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.cc

## Purpose
This file is the normal low-level FUSE adapter. It translates each kernel FUSE request into a `LizardClient` call, converts reply structures and errors back to libfuse, tracks per-request user/group context, and handles file descriptor state handoff between `fuse_file_info` and `LizardClient::FileInfo`.

## Important APIs, Types, And Functions
`get_reduced_context()` converts `fuse_req_ctx()` uid/gid/pid/umask into `LizardClient::Context`; `get_context()` additionally discovers secondary groups and calls `LizardClient::updateGroups()`. Linux uses `fuse_req_getgroups()` with a 10-second LRU pid cache, while macOS/FreeBSD use `sysctl` process credentials. `fuse_file_info_wrapper` mirrors `flags`, `direct_io`, `keep_cache`, `fh`, and `lock_owner` into `LizardClient::FileInfo` and writes modified values back on destruction. `make_fuse_entry_param()` converts `LizardClient::EntryParam` into libfuse's entry reply. Every exported `mfs_*` function wraps a `LizardClient` operation and catches `RequestException`.

## Control Flow
Most operations follow a direct pattern: build context, call `LizardClient`, reply with `fuse_reply_*`, or return `e.system_error_code`. Directory open creates a synthetic `fh` session id and registers it with `LizardClient::update_readdir_session()`. `mfs_readdir()` requests a bounded number of client entries, packs them with `fuse_add_direntry()`, updates the session's last inode, and replies with a buffer. `mfs_read()` uses `fuse_reply_iov()` for normal file reads and direct buffers for special inodes. Create/open paths remove client file info if libfuse reports `-ENOENT` while replying.

## State And Persistence
The file owns `gPidToContextCache` and `gLockInterruptData`. It mutates per-FUSE-request `fuse_file_info`, directory session state in `LizardClient`, and interrupt data for blocking locks. It does not persist data itself; durable effects are delegated to `LizardClient` and master/chunkserver communication.

## Dependencies And Integration Points
It depends on libfuse low-level request APIs, platform credential APIs, `GroupCache`, `ThreadSafeMap`, `lock_conversion`, `LizardClient`, protocol constants, and `ReadCache` iovec conversion. It is installed by `main.cc` into the normal `fuse_lowlevel_ops` table.

## Risks And Test Signals
The secondary-group cache invalidation uses `gPidToContextCache.erase(ctx.uid)` despite pid-keyed caching, which deserves review. Other risks include reply-time cleanup when FUSE rejects open/create replies, fixed 50 KB readdir buffers, ignored FUSE 3 rename flags, unsupported `security.capability`, and interrupt data lifetime for blocking locks. Test signals include FUSE operation tests, lock interrupt tests, group membership changes, xattr compatibility, and iovec reply coverage from `iovec_traits_unittest.cc`.
