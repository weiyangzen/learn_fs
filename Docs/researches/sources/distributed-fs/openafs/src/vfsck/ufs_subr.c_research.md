<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_subr.c -->
# sources/distributed-fs/openafs/src/vfsck/ufs_subr.c

## Purpose
Provides user-space copies of UFS fragment and block bitmap helper routines needed by pass 5 and allocation logic.

## Important APIs, Types, And Functions
Functions are `fragacct`, `isblock`, `clrblock`, `setblock`, `scanc`, `skpc`, and `locc`. It uses tables `around`, `inside`, and `fragtbl` declared in `ufs_tables.c`.

## Control Flow
`fragacct` decodes a free-fragment bit pattern and increments or decrements fragment summary counts for each fragment size. `isblock`, `clrblock`, and `setblock` specialize bitmap operations for filesystems with 1, 2, 4, or 8 fragments per block. `scanc`, `skpc`, and `locc` are C implementations of legacy byte-scanning helpers.

## State And Persistence
The functions mutate caller-supplied cylinder group maps and fragment summary arrays. They do not maintain global state beyond reading the static tables.

## Dependencies And Integration Points
Pass 5 uses `fragacct` while rebuilding free fragment summaries. Filesystem allocation helpers can use `isblock`/`setblock`/`clrblock` semantics. The routines depend on UFS `struct fs` geometry and `panic` from `utilities.c` for impossible fragment sizes.

## Risks And Test Signals
Risks include unsupported `fs_frag` values, signedness assumptions in bitmap indexing, and table mismatch with UFS layout. Tests should verify fragment accounting for fragment sizes 1, 2, 4, and 8 and ensure pass 5 summary output matches known-good UFS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_subr.c -->
