<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/inode.c -->
# sources/distributed-fs/openafs/src/vfsck/inode.c

## Purpose
Provides inode block traversal, inode caching, inode clearing, block range validation, pathname lookup callbacks, diagnostics, and inode allocation/free helpers for the fsck passes.

## Important APIs, Types, And Functions
Important functions are `ckinode`, `iblock`, `chkrange`, `ginode`, `inodirty`, `clri`, `findname`, `findino`, `pinode`, `blkerror`, `allocino`, and `freeino`. `pbp` caches the current inode block. The code uses OpenAFS inode magic helpers from `afs/osi_inode.h` and global maps from `fsck.h`.

## Control Flow
`ckinode` walks direct and indirect block pointers for an inode, skipping special device files and HP-UX fast symlinks, and delegates each data or address range to either `dirscan`, `iblock`, or the supplied callback. `iblock` recursively processes single, double, and triple indirect blocks, truncating pointers beyond file size when pass 1 is checking addresses. `chkrange` rejects block ranges outside filesystem and cylinder-group data bounds. `ginode` loads and caches the block containing a requested inode.

Clearing and allocation helpers are pass-aware. `clri` prompts or preens before clearing a bad inode and its blocks, preserving HP-UX continuation inode cleanup. `blkerror` marks files or directories for clearing after bad or duplicate blocks. `allocino` finds a free inode, allocates an initial block, initializes times, size, and mode, and updates maps. `freeino` releases blocks through `pass4check`, zaps the inode, and updates counters.

## State And Persistence
The file updates cached inode blocks, block maps, link maps, inode state maps, file/block counters, duplicate/bad state, and dirty flags. Durable effects include cleared inodes, adjusted block pointers, newly allocated inodes, and freed blocks written later by `ckfini`.

## Dependencies And Integration Points
It is central to passes 1, 1b, 2, 3, and 4. `dir.c` depends on `ginode`, `allocino`, `freeino`, and `inodirty`; pass callbacks depend on `ckinode` traversal semantics. Platform branches handle Sun large offsets, HP-UX ACL continuation inodes, fast symlinks, and user-name printing.

## Risks And Test Signals
Risks include integer overflow in size-to-block calculations on older platforms, recursive indirect traversal errors, in-place partial truncation of indirect blocks, global inode-block cache invalidation, and K&R prototypes. Tests should cover direct and indirect block traversal, bad block marking, duplicate block marking, partial truncation, HP-UX fast symlink sizes, continuation inode clearing, allocation failure, and owner/mode diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/inode.c -->
