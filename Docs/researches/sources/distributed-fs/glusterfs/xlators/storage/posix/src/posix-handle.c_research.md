# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.c

## Purpose
`posix-handle.c` implements GFID handle management for the POSIX translator. It creates, resolves, validates, and removes `.glusterfs/<hash>/<hash>/<gfid>` handles and supports ancestry reconstruction, trash initialization, hardlink handles, directory symlink handles, and unlinked-open recovery.

## Important APIs, Types, And Functions
- `posix_resolve()` maps parent GFID plus basename to inode/iatt.
- `posix_make_ancestryfromgfid()` follows directory handles to root and builds path/dirent ancestry.
- `posix_handle_relpath()`, `posix_handle_path()`, and `posix_handle_gfid_path()` format relative, object, and handle paths.
- `posix_handle_init()` creates/verifies `.glusterfs` and the root GFID symlink.
- `posix_handle_trash_init()` creates `.glusterfs/landfill` and migrates old `.landfill`.
- `posix_handle_hard()`, `posix_handle_soft()`, `posix_handle_unset_gfid()`, and `posix_create_link_if_gfid_exists()` maintain GFID handles.

## Control Flow
Initialization verifies the export path and hidden directory, stores hidden dir inode/dev, and ensures the root GFID handle points to the export root. Path resolution builds the direct hidden handle path, then expands directory symlink handles through a validation-and-pump loop to avoid `ELOOP`. Ancestry walking reads parent symlink targets up to root, stacks components, then resolves downward. Hard handles are hardlinks for files; soft handles are symlinks for directories; unlinked-open recovery links from `.glusterfs/unlink` and renames the recovery target back to the GFID handle.

## State And Persistence Behavior
Persistent state includes `.glusterfs`, hash directories, root GFID symlink, regular-file hardlink handles, directory symlink handles, `.glusterfs/landfill`, old landfill migration, and `.glusterfs/unlink` recovery targets. Runtime state includes `arrdfd[]`, hidden dir inode/dev, inode table references, inode ctx unlink flags, and stack path buffers.

## Dependencies And Integration Points
Called by `posix-common.c` during init and by entry ops during lookup/create/mkdir/unlink/rename/rmdir/link. Depends on `posix-inode-handle.h`, `posix.h`, `posix-metadata.h`, syscall wrappers, inode tables, UUID helpers, and `struct posix_private`.

## Risks And Edge Cases
Malformed symlink validation is security- and correctness-critical. Very deep ancestry fails at `PATH_MAX / 2`. Hardlink handle inode/dev mismatches signal backend inconsistency. Recovery from `.glusterfs/unlink` spans link and rename operations under inode lock and can leave stale state if interrupted. `alloca` path sizing must remain correct.

## Test Signals
Cover hidden directory creation, valid/invalid root handles, hard and soft handle creation, malformed symlink rejection, ELOOP pumping, ancestry reconstruction, deep hierarchy failure, landfill migration, handle removal, normal and unlinked-open `posix_create_link_if_gfid_exists()`, and inode/dev mismatch detection.
