# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.c

## Purpose
Implements the `gfid-access` GlusterFS feature translator. It exposes a virtual `/.gfid` directory whose children are canonical GFID names, maps those virtual dentries back to the real inode table, and forwards most normal fops to the child translator after translating virtual locs to real locs. It also handles special FUSE auxiliary setxattr payloads for GFID-addressed new-file creation and heal lookup.

## Important APIs, Types, and Functions
- `ga_valid_inode_loc_copy()` copies a `loc_t` and replaces virtual parent/inode pointers with real inodes stored in inode ctx.
- `ga_newfile_parse_args()` and `ga_heal_parse_args()` decode packed big-endian control payloads from `GF_FUSE_AUX_GFID_NEWFILE` and `GF_FUSE_AUX_GFID_HEAL`.
- `ga_fill_tmp_loc()` builds a temporary child loc under the real parent, creates or finds the target inode, and injects `"gfid-req"` into xdata.
- `ga_lookup()` is the core virtual namespace handler for `/.gfid`, GFID-name lookup, revalidation, and normal lookup forwarding.
- `ga_virtual_lookup_cbk()` rewrites successful directory lookups to return a virtual inode/GFID while retaining inode ctx back-pointers to the real inode.
- `ga_new_entry()` and `ga_heal_entry()` run helper create/lookup flows on copied frames and unwind the original setxattr request.
- Entry and inode fops (`ga_mkdir`, `ga_unlink`, `ga_rename`, `ga_stat`, `ga_getxattr`, etc.) either reject invalid virtual namespace operations or translate locs with `ga_valid_inode_loc_copy()`.

## Control Flow
Normal lookups wind through `ga_lookup_cbk()`, which caches root stat data and manufactures the `.gfid` directory stat by changing the last GFID byte to `GF_AUX_GFID`. A nameless lookup on the auxiliary GFID or a path lookup of `/.gfid` is satisfied locally. A lookup below `/.gfid` validates the basename as a UUID, deletes `"gfid-req"` from xdata, then performs a GFID lookup against the child. For directory targets, the callback links or finds the real inode and stores it in ctx on the virtual inode, then returns a random/virtual GFID to avoid aliasing the real directory inode in the virtual namespace.

The setxattr path first checks for the two auxiliary payload keys. New-file payloads are parsed, converted to a temp loc, and dispatched as mkdir, symlink, or mknod after setting frame uid/gid. Mknod sends a named lookup first so DHT can clean stale linkto files. Heal payloads run a GFID-targeted lookup. Other setxattr/getxattr/stat/setattr/removexattr and removal/link/rename paths copy the loc and substitute real inodes before winding.

## State and Persistence
The translator keeps only in-memory state: `ga_private_t` stores cached root and virtual `.gfid` stat buffers plus mem pools, and inode ctx maps virtual inodes to real inodes. No on-disk metadata is written by this translator directly. Persistence is delegated to lower translators through normal fops and `"gfid-req"` xdata.

## Dependencies and Integration Points
This code depends on GlusterFS inode ctx APIs, `loc_t`, dict/xdata helpers, stack winding/unwinding, mem pools, `gfid_to_ino`, and default callback helpers. It integrates with FUSE auxiliary GFID requests via xattr keys, with DHT via the mknod pre-lookup, and with statedump via `ga_dump_inodectx()`.

## Risks and Edge Cases
Parsing uses packed blobs and pointer casts; malformed lengths, missing NUL bytes, or unaligned data are important risk points. Directory virtual GFIDs are intentionally random, so ctx lifetime and `forget` cleanup are critical. Some error paths initialize `op_errno` to `ENOMEM` even when parse failures are more like `EINVAL`, which may make diagnostics less exact. `init()` destroys `newfile_args_pool` on failure but does not destroy `heal_args_pool` in the same cleanup branch.

## Test Signals
Exercise lookups for `/`, `/.gfid`, valid/invalid `/.gfid/<uuid>`, file and directory revalidation, and ESTALE-to-ENOENT conversion. Cover auxiliary setxattr newfile/heal payloads for mkdir, symlink, mknod, malformed blobs, and DHT stale lookup behavior. Confirm virtual directory fops reject unsupported mutation and that statedump shows real GFIDs for virtual inode ctx.
