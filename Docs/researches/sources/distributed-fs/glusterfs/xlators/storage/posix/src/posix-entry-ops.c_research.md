# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-entry-ops.c

## Purpose
`posix-entry-ops.c` implements POSIX storage namespace FOPs: lookup, mknod, mkdir, unlink, rmdir, symlink, rename, link, create, and put. It maps Gluster loc/GFID semantics to backend paths, xattrs, hidden GFID handles, ctime metadata, DHT linkfile handling, and pre/post parent attribute reporting.

## Important APIs, Types, And Functions
- `posix_lookup()` resolves named/nameless locs, fills xattrs, heals GFIDs, and handles stale/unlinked GFID cases.
- `posix_mknod()`, `posix_mkdir()`, `posix_symlink()`, and `posix_create()` create backend entries and set ownership, ACLs, entry xattrs, GFIDs, ctime, pgfid metadata, and gfid2path metadata.
- `posix_unlink()` removes entries while preserving open deleted files through `.glusterfs/unlink` when required.
- `posix_rmdir()` removes or landfill-renames directories.
- `posix_rename()` handles replacement, victim cleanup, GFID handle rewrites, pgfid/gfid2path migration, and parent ctime.
- `posix_link()` creates hardlinks while enforcing `max_hardlinks`.
- `posix_put()` performs create/write/fsetxattr/flush through syncops.

## Control Flow
Most FOPs validate inputs, construct backend paths through handle macros, collect preparent stats, execute a backend syscall, update xattrs/GFID handles/ctime, collect postparent stats, and unwind through `STACK_UNWIND_STRICT`. Lookup additionally blocks `.glusterfs`, supports nameless GFID lookup and `.glusterfs/unlink` status lookup, heals missing GFIDs, fills requested xattrs, and initializes pgfid link-count xattrs. Rename and unlink have the most complex flows because they must preserve open files, update hardlink metadata, and clean or recreate GFID handles.

## State And Persistence Behavior
The file mutates namespace entries, `trusted.gfid`, ACL xattrs, entry-create xattrs, ctime metadata, pgfid link-count xattrs, gfid2path xattrs, DHT linkto xattrs, `.glusterfs` GFID handles, `.glusterfs/unlink`, and `.glusterfs/landfill`. Runtime state includes fd contexts, inode ctx pgfid locks, inode fd counts, unlink flags, and xdata dictionaries.

## Dependencies And Integration Points
It depends on `posix-handle.h`, `posix-gfid-path.h`, `posix-metadata.h`, DHT/AFR/cloudsync/trash xdata keys, syscall wrappers, and inode/fd context helpers. Upper translators coordinate behavior through keys such as `GF_GFIDLESS_LOOKUP`, `GF_UNLINKED_LOOKUP`, `GF_FORCE_REPLACE_KEY`, `DHT_SKIP_OPEN_FD_UNLINK`, `DHT_SKIP_NON_LINKTO_UNLINK`, `GET_LINK_COUNT`, and preop check keys.

## Risks And Edge Cases
Create and rename operations are multi-step and can leave metadata inconsistent after partial failure. `posix_put()` explicitly lacks atomic rollback. Rename combines multiple inode locks and persistent xattr updates. Unlink correctness depends on open-fd counts and unlink flags. gfid2path and pgfid metadata can become mixed if options change mid-run. Hidden `.glusterfs` protection and DHT stale-linkfile behavior are critical invariants.

## Test Signals
Cover named/nameless lookup, stale handle cleanup, hidden directory lookup/mkdir/rmdir rejection, GFID heal, duplicate-GFID mkdir, internal DHT linkfile create/mknod, stale linkto replacement, ACL propagation, SGID inheritance, pgfid update on create/link/unlink/rename, gfid2path add/remove/rename/link limits, unlink with open fds, rmdir landfill, rename over files/directories, max-hardlink enforcement, ctime updates, preop failures, and put failure after each syncop step.
