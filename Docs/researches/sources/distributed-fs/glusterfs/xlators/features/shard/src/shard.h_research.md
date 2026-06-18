# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h

## Purpose

`sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h` is the private interface and shared type definition header for the GlusterFS shard translator. It defines shard directory/xattr constants, valid-bit masks for cached inode attributes, block-index macros, lock/unwind/create/read-metadata helper macros, callback typedefs, and the central private/local/inode-context structures used by `shard.c`. The source was read as a complete 359-line file for this report.

## Important APIs, Types, and Functions

Important constants include `GF_SHARD_DIR` (`.shard`), `GF_SHARD_REMOVE_ME_DIR` (`.remove_me`), `SHARD_MIN_BLOCK_SIZE`, `SHARD_MAX_BLOCK_SIZE`, `SHARD_XATTR_PREFIX`, and `GF_XATTR_SHARD_BLOCK_SIZE`. Attribute mask macros (`SHARD_MASK_BLOCK_SIZE`, `SHARD_MASK_PROT`, `SHARD_MASK_NLINK`, `SHARD_MASK_UID`, `SHARD_MASK_GID`, `SHARD_MASK_SIZE`, `SHARD_MASK_BLOCKS`, `SHARD_MASK_TIMES`, `SHARD_MASK_OTHERS`, `SHARD_MASK_REFRESH_RESET`) compose into `SHARD_INODE_WRITE_MASK`, `SHARD_LOOKUP_MASK`, and `SHARD_ALL_MASK`. `get_lowest_block` and `get_highest_block` map logical byte ranges to shard block numbers.

Externally visible functions declared here are `shard_unlock_inodelk`, `shard_unlock_entrylk`, and the `shard_local_wipe`/`shard_set_size_attrs` functions used by implementation macros. Operational macros include `SHARD_ENTRY_FOP_CHECK`, `SHARD_INODE_OP_CHECK`, `SHARD_STACK_UNWIND`, `SHARD_STACK_DESTROY`, `SHARD_INODE_CREATE_INIT`, `SHARD_MD_READ_FOP_INIT_REQ_DICT`, `SHARD_SET_ROOT_FS_ID`, `SHARD_UNSET_ROOT_FS_ID`, and `SHARD_TIME_UPDATE`.

Key types are `shard_bg_deletion_state_t`, `shard_unlink_thread_t`, `shard_priv_t`, `shard_inodelk_t`, `shard_entrylk_t`, callback typedefs for post-fop stages, `shard_local_t`, `shard_inode_ctx_t`, and `shard_internal_dir_type_t`.

## Control Flow

This header has no standalone runtime flow, but its macros encode important control-flow conventions used throughout `shard.c`. Entry/inode checks jump to caller labels with `EPERM` for protected internal paths. The stack unwind/destroy macros release internal locks and wipe pooled local state before returning to the caller. Create/mknod initialization macros attach block-size and logical-size xattrs to new files. Metadata-read macros request logical size xattrs. FS-id macros temporarily elevate internal operations to uid/gid zero. `SHARD_TIME_UPDATE` preserves monotonic-ish cached timestamp behavior by reconciling seconds and nanoseconds between cached and returned attributes.

## State and Persistence Behavior

The header defines both persistent metadata names and in-memory state layout. Persistent backend state is addressed by `GF_XATTR_SHARD_BLOCK_SIZE`, `GF_XATTR_SHARD_FILE_SIZE` from the included message/xattr ecosystem, and internal directory names. In-memory translator-wide state in `shard_priv_t` persists for the translator lifetime and includes configured block size, internal GFIDs/inodes, shard LRU accounting, background deletion state, first-lookup cleanup trigger, LRU limit, and unlink thread state.

`shard_local_t` is per-call state and carries operation result fields, block range and counts, fop identity, offsets/sizes, xattr dicts, loc/fd references, inode lists, iobufs, lock descriptors, sync barriers, post-stage handlers, deletion parameters, and base GFID. `shard_inode_ctx_t` is attached to GlusterFS inodes and caches block size and logical stat fields; for shard inodes it also carries LRU linkage, base GFID/block number, refresh flags, pending-fsync linkage, fsync counters, and base/shard inode references.

## Dependencies and Integration Points

Direct includes are `<glusterfs/xlator.h>`, `<glusterfs/compat-errno.h>`, `"shard-messages.h"`, and `<glusterfs/syncop.h>`. The header assumes GlusterFS core definitions for `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, `dict_t`, `inode_t`, `struct iatt`, `gf_lock_t`, `gf_boolean_t`, `syncbarrier_t`, `gf_dirent_t`, `struct list_head`, and fop identifiers.

The header is tightly coupled to `shard.c`, the shard memory-type definitions, GlusterFS xattr constants, translator stack-wind/unwind semantics, syncop APIs, and option/lifecycle registration in the implementation file.

## Risks and Edge Cases

Macro side effects are a key risk because several macros allocate memory, mutate dictionaries, change frame credentials, call unlock functions, jump to caller labels, and free local state. Callers must pass labels and initialized locals consistently. `SHARD_INODE_CREATE_INIT` allocates buffers that become dict-owned only after successful `dict_set_bin`; error paths must not double free or leak them.

Structure layout changes have broad blast radius because `shard_local_t` and `shard_inode_ctx_t` are shared across many asynchronous callbacks. Adding fields without wiping/unref handling in `shard_local_wipe` can leak references. Changing mask semantics can make cached stats stale or incomplete. Any caller of FS-id macros must pair set/unset around all exits to avoid credential leakage on a frame.

## Test Signals

Compile coverage of all shard translator sources is the first signal because this header carries most type contracts. Runtime signals should verify protected path checks, creation xattr initialization, logical metadata read requests, lock release during unwind, timestamp cache updates, fs-id restoration on success and failure, inode-context mask behavior, and local cleanup after error paths that allocate locs/fds/dicts/iobufs or auxiliary lock frames.
