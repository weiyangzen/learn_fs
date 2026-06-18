# sources/distributed-fs/lustre-release/lustre/llite/dir.c

## Purpose
`dir.c` implements llite directory operations and many directory ioctls: hash-cookie readdir, striped directory layout creation/query, metadata layout get/set, HSM controls, quota aggregation, FID removal, migration, ladvise, PCC state/detach, seek/open/release/flush, and `ll_dir_operations`.

## Important APIs, Types, and Functions
Core functions include `ll_get_dir_folio()`, `ll_release_dir_folio()`, `ll_dir_read()`, `ll_iterate()`, `ll_dir_setdirstripe()`, `ll_dir_setstripe()`, `ll_dir_get_default_lmv()`, `ll_dir_get_default_layout()`, `ll_dir_getstripe_default()`, `ll_get_mdt_idx_by_fid()`, `ll_ioc_copy_start()`, `ll_ioc_copy_end()`, quota iterator helpers, `quotactl_ioctl()`, `ll_rmfid()`, `ll_dir_ioctl()`, `ll_dir_seek()`, and `ll_dir_flush()`.

## Control Flow
Readdir uses name hashes as cookies. `ll_iterate()` prepares encryption, striped-directory parent FID context, and `md_op_data`, then `ll_dir_read()` fetches directory folios, emits entries, translates encrypted names when needed, advances by `ldp_hash_end`, removes collision pages, and maps internal end/hash cookies to user-visible offsets. Striping paths validate user layout metadata, handle older-server hash compatibility, apply security and encryption inheritance, send metadata RPCs, and prepare returned inodes. `ll_dir_ioctl()` validates and copies user buffers, dispatches a large command switch, releases requests/buffers, and falls back to generic llite or data-target ioctl handlers.

## State and Persistence Behavior
Directory page cache and file-private hash position are local. `fd_partial_readdir_rc` delays partial striped-readdir errors until flush. Persistent state can be changed through setstripe, rmfid, remove-entry, quota mutation, HSM progress/request, migration, and PCC detach. Quota all-iteration state is temporarily held in `sbi->ll_all_quota_list` until drained or cleaned.

## Dependencies and Integration Points
The file integrates with VFS file operations, folio/page cache APIs, Lustre metadata and OBD RPCs, LMV/LOV layouts, llcrypt filename conversion, SELinux/security hooks, HSM coordinator APIs, quota services, PCC, and llite stats.

## Risks and Edge Cases
Readdir depends on hash-cookie stability, collision handling, and 32-bit translation. Encrypted readdir may fail during name conversion. Ioctl user-copy paths require strict size/NUL/magic checks. Layout logic must distinguish LOV, LMV, default, specific, composite, and foreign metadata. Quota iterator cleanup and partial drains must avoid leaks. The encrypted no-key stat size path deserves focused validation.

## Test Signals
Cover normal/striped/collision/encrypted/foreign readdir, 32-bit cookies, all layout get/set variants, too-small buffers, invalid ioctl inputs, HSM copy start/end data-version checks, quota permission/iterator flows, subdir `rmfid`, migration validation, ladvise constraints, PCC cached/uncached cases, seek translation, and partial-readdir flush behavior.
