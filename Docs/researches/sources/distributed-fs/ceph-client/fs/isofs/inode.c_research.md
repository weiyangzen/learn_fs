## sources/distributed-fs/ceph-client/fs/isofs/inode.c

Purpose: core ISOFS superblock, mount option, inode, block mapping, and module lifecycle implementation.

Important APIs/types: defines `struct isofs_options`, super operations, dentry operations, address-space operations for normal files, inode cache allocation, fs-context operations, and `iso9660_fs_type`. Mount parsing supports Rock Ridge/Joliet toggles, hide/showassoc, `cruft`, `uid`, `gid`, `mode`, `dmode`, `iocharset`, `session`, `sbsector`, block size, and `nocompress`. Exported internal APIs include `isofs_get_blocks`, `isofs_bread`, and `__isofs_iget`.

Control flow: `isofs_fill_super` validates device block size, finds the volume descriptor from explicit sbsector or CD multisession data, detects ISO/High Sierra/Joliet descriptors, enforces read-only mount, sets block size/time bounds/maxbytes, loads NLS for Joliet, initializes `isofs_sb_info`, reads the root inode, chooses Rock Ridge versus Joliet fallbacks for broken media, sets dentry comparison rules, and creates the root dentry. `isofs_read_inode` reads the directory record, handles split records, sets mode/uid/gid/times/extent/size, processes Level 3 multi-extent files, applies Rock Ridge overrides, and installs file/dir/symlink/special inode operations.

State and persistence: ISOFS is read-only; persistent state is only read from media. Runtime state includes superblock options, inode cache entries with directory-record identity, mapped section chains for multi-extent files, and page-cache address-space ops. `isofs_get_blocks` maps logical file blocks across Level 3 sections and never allocates.

Dependencies and integration points: uses fs_context, block devices, cdrom multisession ioctls, NLS, mpage read/readahead, exportfs, Rock Ridge, Joliet, zisofs, and VFS inode/dentry operations.

Risks and test signals: major risks are untrusted descriptor parsing, block-size mismatches, broken-media fallbacks, multi-extent loops, High Sierra flag offsets, permission override semantics, and optional feature interactions. Test plain ISO, High Sierra, Joliet-only, Rock Ridge plus Joliet, broken empty primary root, multisession media, Level 3 multi-extent files, compressed files, symlinks/devices from Rock Ridge, read-only remount, and malformed descriptors/records.
