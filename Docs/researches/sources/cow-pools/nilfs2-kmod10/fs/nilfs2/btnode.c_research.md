# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.c

Implements the page-cache-backed cache for NILFS B-tree node blocks. It creates, reads, deletes, and rekeys node buffers used by B-tree mappings.

Key behavior:
- Initializes the B-tree node cache inode as a regular GFP_NOFS buffer-cache inode.
- Creates node buffers with NILFS node flags, checking for duplicate/reused node block addresses.
- Submits node reads, translating virtual node block numbers through DAT when needed, and supports limited readahead.
- Deletes node buffers by forgetting the buffer and invalidating the page-cache range when clean.
- Supports changing a node block’s cache key either by moving a whole folio when block size equals page size or by copying into a newly created buffer.

Risk/notes: the key-change path explicitly does not support folio sizes larger than page size. Duplicate node address detection is treated as severe metadata inconsistency.
