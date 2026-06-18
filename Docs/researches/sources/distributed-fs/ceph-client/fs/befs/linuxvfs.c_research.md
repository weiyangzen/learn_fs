# sources/distributed-fs/ceph-client/fs/befs/linuxvfs.c

Purpose: connects BeFS metadata readers to the Linux VFS: mount, inode loading, regular-file reads, directory lookup/readdir, symlinks, statfs, exportfs, NLS filename conversion, and module registration.

Important APIs/types/functions: `befs_read_folio`, `befs_get_block`, `befs_lookup`, `befs_readdir`, `befs_iget`, inode cache helpers, `befs_symlink_read_folio`, `befs_utf2nls`, `befs_nls2utf`, export callbacks, mount option parsing, `befs_fill_super`, `befs_reconfigure`, `befs_statfs`, and filesystem init/exit.

Control flow: mount allocates `befs_sb_info`, copies parsed options, forces read-only, reads the superblock at PPC or x86 offset, validates it, sets blocksize and VFS ops, loads root inode, and loads NLS. Inode loading reads a raw inode block, validates it, sets mode/uid/gid/times/size/blocks, selects file/dir/symlink operations, and handles short vs long symlinks. Directory lookup and readdir query the BeFS B+tree and convert filenames when an NLS table is active.

State and persistence: in-memory superblock stores parsed persistent fields and mount options; inode private state stores persistent datastreams, inode addresses, and inline symlink data. The driver does not write BeFS data; write block creation returns errors and reconfigure disallows read-write.

Dependencies and integration: uses `super.c`, `inode.c`, `datastream.c`, `btree.c`, `io.c`, NLS APIs, buffer-head address_space operations, exportfs helpers, fs_context parser, and module registration.

Risks: filename conversion failures can make entries inaccessible. Parent export uses stored parent address fields and must remain consistent with inode numbering. Read-only enforcement is critical because lower mapping code does not implement allocation or journaling.

Test signals: mount read-only and attempted read-write; lookup/readdir with UTF-8 and mounted `iocharset`; read regular files and long/short symlinks; statfs values; NFS export file handles; corrupted superblock/inode paths.
