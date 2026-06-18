# sources/distributed-fs/ceph-client/fs/overlayfs/namei.c

## Purpose
`namei.c` implements OverlayFS pathname lookup, origin-file-handle validation, redirect following, metacopy lower-data resolution, index lookup, and lower-positive checks. It is the bridge between VFS dentry lookup and OverlayFS' multi-layer model: for each overlay dentry it discovers the upper dentry, lower stack, optional data-only lower path, redirect metadata, index entry, and final overlay inode.

## Important APIs, types, and functions
The local `struct ovl_lookup_data` carries lookup state such as current layer, name, directory/opaque status, redirect strings, metacopy state, and stop/last flags. `struct ovl_lookup_ctx` owns the objects assembled for the final dentry: upper dentry, lower stack, origin path, index dentry, `ovl_entry`, and inode.

Public entry points include `ovl_lookup()`, `ovl_lower_positive()`, `ovl_path_next()`, `ovl_verify_lowerdata()`, file-handle helpers such as `ovl_check_fb_len()`, `ovl_uuid_match()`, `ovl_decode_real_fh()`, `ovl_check_origin_fh()`, `ovl_verify_origin_xattr()`, and index helpers such as `ovl_get_index_name()`, `ovl_get_index_fh()`, `ovl_lookup_index()`, `ovl_index_upper()`, and `ovl_verify_index()`.

## Control flow
`ovl_lookup()` validates name length, switches to mounter credentials with `with_ovl_creds()`, and delegates to `ovl_lookup_layers()`. Lookup starts in the parent's upper dentry when present, checks upper redirects/origin/metacopy, then walks lower layers from top to bottom unless a whiteout, opaque directory, non-directory conflict, or final usable result stops the search. `ovl_lookup_layer()` handles absolute redirect paths element by element; `ovl_lookup_single()` performs the actual `lookup_one_unlocked()` call, filters whiteouts, validates casefold consistency, detects opaque/xwhiteout directories, rejects weird dentries, and rewrites `d->name` when a redirect xattr is followed.

After layer walking, the code enforces redirect/metacopy policy in `ovl_check_follow_redirect()`, rejects metacopy files without data, optionally installs origin-path lookups, verifies lower origins for indexed/NFS-export cases, looks up an index entry, allocates an `ovl_entry`, and calls `ovl_get_inode()`. `d_splice_alias()` attaches the resulting inode. Lazy lower-data lookup for data-only layers is deferred to `ovl_verify_lowerdata()`, which resolves the absolute redirect with `LOOKUP_BENEATH | LOOKUP_NO_SYMLINKS | LOOKUP_NO_XDEV` and then validates fs-verity digest when configured.

## State and persistence
Persistent state is carried in OverlayFS xattrs: `overlay.origin`, `overlay.redirect`, `overlay.upper`, `overlay.metacopy`, and whiteout/opaque markers. `ovl_fix_origin()` can add a missing origin xattr and mark the upper parent impure. Index entries are named by hex-encoded lower file handles and may be whiteouted to represent stale exported handles. In-memory state is stored in dentry flags, `ovl_entry` lower stacks, inode flags such as `OVL_UPPERDATA`, `OVL_HAS_DIGEST`, and `OVL_VERIFIED_DIGEST`, and redirect strings owned by `ovl_inode`.

## Dependencies and integration points
The file depends on VFS lookup, exportfs encode/decode, xattrs, mount idmaps, fs-verity helpers via `util.c`, index/workdir setup from `super.c`, inode creation from `inode.c`, and constants/types from `overlayfs.h` and `ovl_entry.h`. It is called by the overlay directory inode operations and supports export operations by resolving file handles and index entries.

## Risks
The main risks are stale or malicious xattrs, conflicting lower UUIDs, redirect traversal security, metacopy files without accessible lower data, casefold mismatch after offline changes, and index corruption. The code mitigates with strict lookup flags for data-only redirects, capability checks for file-handle decode, trap inode checks for overlapping layers, type validation, rate-limited warnings, and policy gates for redirect/metacopy following.

## Test signals
Useful tests include lookups across upper/lower/merged directories, whiteout and opaque behavior, absolute and relative redirects, metacopy with and without data-only layers, fs-verity require/on/off modes, NFS export/index stale-handle behavior, lower UUID conflicts, casefold consistency, negative dentry handling, and `ovl_lower_positive()` results after copy-up and whiteout.
