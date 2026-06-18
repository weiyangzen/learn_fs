# sources/distributed-fs/ceph-client/fs/ocfs2/symlink.h

Purpose: declares OCFS2 symlink operation tables and provides the fast-symlink predicate used by inode setup.

Important APIs and types: exports `ocfs2_symlink_inode_operations`, `ocfs2_fast_symlink_aops`, and inline `ocfs2_inode_is_fast_symlink`.

Control flow: the inline predicate returns true for symlink inodes with `i_blocks == 0`, identifying targets stored inline in the dinode rather than in allocated data clusters. Callers use that decision to attach fast symlink address-space operations.

State and persistence behavior: no state is stored in the header. The predicate encodes the on-disk convention that zero-block symlink inodes are fast symlinks.

Dependencies and integration points: used by OCFS2 inode initialization and symlink handling, and tied to the implementation in `symlink.c`.

Risks: if inode block accounting is wrong, a symlink may be treated as fast when no inline target exists, or as slow when inline data should be used. That would surface as failed link resolution or stale target data.

Test signals: inode setup for symlink modes with zero and nonzero `i_blocks`, fast-symlink read path selection, and fsck/corruption cases where symlink metadata is inconsistent.
