# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap_repair.c

## Purpose
`rtbitmap_repair.c` reconstructs the realtime bitmap file for an rtgroup. It builds a new bitmap in an xfile from gaps in the realtime rmapbt, fixes bitmap geometry and inode mapping problems, copies the reconstructed blocks into a temporary file, atomically exchanges contents with the real bitmap file, and reaps old mappings.

## Important APIs, types, and functions
`xrep_setup_rtbitmap` creates a tempfile, xfile, and reservation estimate. Word helpers include `xfbmp_load`, `xfbmp_store`, `xfbmp_copyin`, and `xfbmp_copyout`. Rebuild helpers are `xrep_rtbitmap_mark_free`, `xrep_rtbitmap_walk_rtrmap`, `xrep_rtbitmap_find_freespace`, `xrep_rtbitmap_prep_buf`, `xrep_rtbitmap_data_mappings`, `xrep_rtbitmap_geometry`, and exported `xrep_rtbitmap`.

## Control flow
Repair requires rtrmapbt and exchange-range support. It repairs metadata inode forks, joins the bitmap inode, converts unwritten mappings when possible, fixes superblock geometry and file size, flushes busy extents, then reconstructs free bits by walking rtrmap records and marking gaps as free. Free regions must be rt extent aligned and must not overlap rtrefcount shared or CoW records. The xfile bitmap is copied into a preallocated tempfile with proper rtbitmap buffer headers, the tempfile size is set, `xrep_tempexch_contents` swaps data fork contents, and the old bitmap blocks are reaped from the temp inode.

## State and persistence
Persistent updates include superblock realtime geometry counters, bitmap inode size/fork contents, converted written extents, and exchanged bitmap data. Temporary state includes xfile words, tempfile inode, `xrep_tempexch`, `prep_wordoff`, and rtrmap walk cursor `next_rgbno`.

## Dependencies and integration points
It depends on rtrmap as the truth source for used realtime blocks, rtrefcount for shared/CoW exclusion, tempfile/tempexch repair helpers, bmap conversion, extent busy flushing, rtbitmap buffer verifiers, and metadata inode repair.

## Risks and test signals
Risks include deriving free space from corrupt rtrmap data, alignment errors at word/rt extent boundaries, reservation underestimation before dirty transactions, exchange-range failure after staging, and mishandling legacy versus rtgroup bitmap headers. Tests should cover fragmented free gaps, word-boundary gaps, final tail free space, shared/CoW conflicts, unwritten bitmap extents, large bitmap files, busy extents, no exchange-range support, and post-repair bitmap/summary/rtrmap scrub.
