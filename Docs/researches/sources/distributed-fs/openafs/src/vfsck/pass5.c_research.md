<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass5.c -->
# sources/distributed-fs/openafs/src/vfsck/pass5.c

## Purpose
Implements fsck pass 5: rebuild and verify cylinder group and superblock allocation summaries from the block and inode maps built by earlier passes.

## Important APIs, Types, And Functions
The main function is `pass5`; `sbfine` clears `fs_fmod` when superblock summary repair occurs. The pass uses `fragacct`, `cg_chkmagic` or `CG_MAGIC`, `cg_inosused`, `cg_blksfree`, `cg_blktot`, `cg_blks`, `blkmap`, and summary structures `struct csum`, `struct cg`, and old/new cylinder group formats.

## Control Flow
Pass 5 initializes a synthetic cylinder-group image, rounds filesystem-size tail fragments as used, then loops over each cylinder group. It reads the current group, rebuilds inode-used maps from `statemap`, rebuilds free block and fragment accounting from `blockmap`, recomputes per-cylinder block totals and fragment summaries, accumulates `fs_cstotal`, and compares each rebuilt component with on-disk values. `dofix` controls whether mismatches update the superblock or cylinder-group buffers. At the end it compares and fixes total free counts in the superblock.

## State And Persistence
The pass writes cylinder group maps, summary counts, rotors, free fragment summaries, superblock `fs_cstotal`, `fs_ronly`, and `fs_fmod` when repairs are accepted. It does not discover new file data; it persists accounting consistency derived from previous passes.

## Dependencies And Integration Points
It depends on accurate `blockmap`/`statemap` from previous passes and UFS fragment helpers in `ufs_subr.c`/`ufs_tables.c`. It handles Sun dynamic postbl formats when `AFS_NEWCG_ENV` is enabled and old format otherwise.

## Risks And Test Signals
Risks include format-specific layout drift, incorrect `mapsize` comparisons, old-to-new conversion behavior, and summary repairs based on earlier corrupted maps. Tests should cover wrong inode maps, wrong free block maps, wrong cylinder group summaries, wrong superblock totals, dynamic versus 4.2 cylinder group formats, and fragment accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass5.c -->
