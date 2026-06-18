# File Research: sources/cow-pools/bcachefs-tools/src/commands/fusemount.rs

## Purpose
Implements `bcachefs fusemount`, a FUSE filesystem bridge over bcachefs internal btree and inode operations. It allows mounting bcachefs without kernel filesystem support, using `fuser` callbacks backed by C/Rust bcachefs bindings.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("fusemount", ...)`
- FUSE implementation type: `BcachefsFs`
- Main command handler: `cmd_fusemount`
- Thread setup helpers:
  - `ensure_thread_init`
  - `RcuGuard`

## Behavior
- Scans member superblocks with `scan_sbs`, opens the filesystem with `nostart`, then starts the filesystem after daemonization decisions.
- Implements FUSE callbacks for lookup, getattr, setattr, readlink, mknod, mkdir, unlink, rmdir, symlink, rename, hardlink, open, read, write, readdir, statfs, and create.
- Maps FUSE inode `1` to bcachefs root inode `4096` in subvolume `1`; all other inode numbers pass through.
- Translates bcachefs inode metadata into `fuser::FileAttr`.
- Reads and writes file data using aligned buffers and bcachefs async read/write helpers through `block_on`.
- Handles unaligned writes with read-modify-write of partial start/end blocks.
- In foreground mode, initializes shrinkers, starts the filesystem, then calls `fuser::mount2`.
- In daemon mode, forks before thread creation, uses a pipe to signal parent readiness from the FUSE `init` callback, redirects child stderr to `/tmp/bcachefs-fuse.log`, then starts the filesystem and mounts.

## Dependencies and Coupling
- Heavy coupling to C shim functions:
  - `rust_fuse_lookup`
  - `rust_fuse_setattr`
  - `rust_fuse_create`
  - `rust_fuse_unlink`
  - `rust_fuse_rename`
  - `rust_fuse_link`
  - `rust_fuse_readdir`
  - `rust_fuse_update_inode_after_write`
  - `rust_bch2_fs_usage_read_short`
  - `rust_fuse_count_inodes`
  - thread-local current/RCU setup helpers.
- Uses `Fs::borrow_raw` and deliberately `mem::forget`s the opened `Fs` so `BcachefsFs::destroy` owns shutdown.
- Uses `AlignedBuf` for O_DIRECT/block-aligned data I/O.

## Important Implementation Notes
- Each FUSE worker thread calls `ensure_thread_init`, establishing bcachefs `current` and URCU registration. `RcuGuard` unregisters on thread exit.
- Negative lookup caching returns an empty entry for ENOENT instead of just `reply.error`.
- Symlink creation creates an inode, writes NUL-terminated target data, then re-reads inode state.
- `statfs` computes available blocks from short usage accounting and counts inodes through a C helper.
- Mount subtype uses `MountOption::CUSTOM("subtype=bcachefs")` because direct root mount syscalls may drop `Subtype`.

## Risks and Edge Cases
- The inode mapping is hardcoded to subvolume `1`, so snapshot subvolumes with colliding inode numbers cannot be represented correctly in a single FUSE mount.
- Many callbacks print debug output unconditionally to stderr.
- FUSE daemon mode writes logs to a fixed `/tmp/bcachefs-fuse.log`.
- `destroy` calls `bch2_fs_exit` directly on the raw pointer; ownership discipline depends on the earlier `mem::forget`.
- The code assumes block-size alignment and correct behavior from the C shim wrappers.
