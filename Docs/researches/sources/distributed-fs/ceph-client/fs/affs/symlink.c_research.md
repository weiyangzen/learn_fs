# sources/distributed-fs/ceph-client/fs/affs/symlink.c

## Purpose
`symlink.c` reads AFFS symbolic-link payloads and translates Amiga volume/assign syntax into Linux path strings exposed through the pagecache link helper.

## Important APIs, types, and functions
The main function is `affs_symlink_read_folio()`. Exported tables are `affs_symlink_aops` and `affs_symlink_inode_operations`, using `page_get_link` and `affs_setattr()`.

## Control flow
The read-folio path reads the symlink header block, treats its front as `struct slink_front`, optionally expands a `volume:` or `assign:` prefix with `s_prefix`, converts doubled slashes into parent-directory markers, copies up to the page-sized link buffer, terminates with NUL, marks the folio uptodate, and unlocks it.

## State and persistence
Persistent symlink data is stored inline in the header block's `symname` area. Runtime prefix and volume settings are protected by `symlink_lock`.

## Dependencies and integration points
It integrates with `affs_iget()` and `affs_symlink()` for symlink inode setup, `page_get_link`, buffer-head reads, and mount options `prefix` and `volume`.

## Risks and test signals
Risks include truncation to 1023 bytes, prefix races, malformed non-NUL payloads, volume/assign interpretation differences, and read I/O errors. Test signals include absolute and relative symlinks, assign-containing links, prefix remount changes, long symlinks, double-slash parent encoding, and corrupted/missing header blocks.
