# sources/distributed-fs/ceph-client/fs/ocfs2/symlink.c

Purpose: implements OCFS2 symlink inode operations, including the fast-symlink address-space operation that reads inline symlink targets stored inside the dinode.

Important APIs and functions: exports `ocfs2_fast_symlink_aops` with `.read_folio = ocfs2_fast_symlink_read_folio`, and `ocfs2_symlink_inode_operations` with `page_get_link`, `ocfs2_getattr`, `ocfs2_setattr`, `ocfs2_listxattr`, and `ocfs2_fiemap`. The core helper is `ocfs2_fast_symlink_read_folio`.

Control flow: for fast symlinks, VFS page-cache link resolution calls `ocfs2_fast_symlink_read_folio`; it reads the inode block, interprets the buffer as an OCFS2 dinode, copies the inline target from `id2.i_symlink` into the folio, ends folio read success or failure, and releases the buffer head. Non-fast symlink link resolution uses `page_get_link` with normal address-space backing.

State and persistence behavior: fast symlink data is persistent inline dinode payload. The read path does not modify metadata; it populates the page cache folio with a NUL-terminated copy bounded by `ocfs2_fast_symlink_chars`.

Dependencies and integration points: depends on `ocfs2_read_inode_block`, dinode layout, VFS folio/page symlink helpers, OCFS2 getattr/setattr/filemap/xattr handlers, and buffer_head I/O. `symlink.h` supplies the predicate for selecting fast symlink handling during inode setup.

Risks: correctness depends on only assigning fast symlink aops to symlink inodes with inline data and `i_blocks == 0`. The copy includes `len + 1`, so the source must be NUL-terminated within the inline symlink capacity. Read errors must end the folio read with failure to avoid stale page-cache data.

Test signals: create/read short fast symlinks, longer non-fast symlinks, corrupted or unreadable inode block during symlink read, xattr/listxattr/getattr on symlink inodes, and page-cache repeated lookup behavior.
