# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose
`xfs_attr_sf.h` defines helpers for XFS shortform extended attributes stored inline in the inode attr fork. It supplies the sort descriptor used by attr list code and inline routines for sizing and walking packed shortform entries.

## Important APIs, types, and functions
The header defines `xfs_attr_sf_sort_t`, containing original entry number, name length, value length, flags, hash, and pointers to name/value. It defines `XFS_ATTR_SF_ENTSIZE_MAX`, the maximum representable name or value length for shortform fields, and inline helpers `xfs_attr_sf_entsize_byname`, `xfs_attr_sf_entsize`, `xfs_attr_sf_firstentry`, `xfs_attr_sf_nextentry`, and `xfs_attr_sf_endptr`.

## Control flow
Shortform users treat the attr fork as a header followed by variable-length entries. `xfs_attr_sf_firstentry` starts iteration immediately after the header, `xfs_attr_sf_nextentry` advances by the computed entry size, and `xfs_attr_sf_endptr` points to the end of valid bytes using the big-endian `totsize` header field. Add/remove/list/verify code in sibling files builds on these pointer operations.

## State and persistence behavior
The packed shortform format stores each entry with one-byte name and value lengths, flags, and a flexible name/value byte array. The helpers do not log or persist by themselves; they encode the layout used by inode attr fork mutation code. `XFS_ATTR_SF_ENTSIZE_MAX` is the boundary that forces conversion to leaf format when names or values cannot be represented in u8 fields.

## Dependencies and integration points
The header depends on on-disk shortform structure definitions from XFS format headers and endian helpers. It is used by `xfs_attr.c`, `xfs_attr_leaf.c`, and attr list code that needs to sort shortform entries by hash for list output.

## Risks and edge cases
All helpers perform raw pointer arithmetic over packed variable-length data, so callers must verify buffer bounds before trusting on-disk or recovered data. `xfs_attr_sf_entsize_byname` takes `uint8_t` lengths; callers must check larger lengths before conversion. The end pointer depends on `totsize`; corrupted `totsize` can make iteration unsafe unless the verifier is run first.

## Test signals
Tests should cover minimum header-only forks, several packed entries, maximum u8 name/value sizes, conversion rejection when lengths exceed shortform limits, malformed `totsize`, zero-length names, and list sorting by hash using `xfs_attr_sf_sort_t`.
