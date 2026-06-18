# sources/distributed-fs/ceph-client/fs/hfs/bfind.c

## Purpose
`bfind.c` implements search cursor setup, teardown, binary search within a B-tree node, root-to-leaf traversal, record read, and cursor movement for HFS B-trees.

## Important APIs, Types, And Functions
`hfs_find_init` initializes `struct hfs_find_data`, allocates search and result key buffers, and locks the appropriate B-tree mutex class based on catalog, extents, or attributes tree CNID. `hfs_find_exit` releases the current bnode, frees buffers, and unlocks the tree. `__hfs_brec_find` performs in-node binary search for the best matching record. `hfs_brec_find` traverses from root to leaf through index records. `hfs_brec_read` finds and reads a record into a caller buffer. `hfs_brec_goto` moves a cursor by record count across neighboring leaf nodes.

## Control Flow
Search initialization must precede all operations and pins the tree lock. `hfs_brec_find` resets cursor offsets, starts at `tree->root`, checks expected node height and type at each level, calls `__hfs_brec_find`, and for index levels reads the child CNID from the found record. On leaf arrival, it leaves `fd->bnode`, record index, key offset/length, entry offset, and entry length populated.

`__hfs_brec_find` binary-searches record offsets, reads candidate keys, compares through `tree->keycmp`, and records either an exact match or the predecessor record. `hfs_brec_goto` moves backward or forward through `prev` and `next` leaf links and refreshes cursor offsets and key data.

## State And Persistence
The file updates only in-memory cursor state and bnode references. It reads persistent B-tree node descriptors, key areas, record offsets, and child pointers through `hfs_bnode_read`.

## Dependencies And Integration Points
It depends on `btree.h`, bnode lookup/reference management, per-tree key comparison, and mutex nesting classes. Catalog, extent, attribute, and xattr code use these search cursors to locate persistent records.

## Risks And Test Signals
Risks include invalid key lengths, inconsistent node height/type, off-by-one predecessor selection, cursor movement across leaf boundaries, and missing unlocks on init errors. Signals include catalog lookup tests, extent lookup tests, malformed B-tree image rejection, lockdep cleanliness for nested B-tree locks, and record iteration coverage.
