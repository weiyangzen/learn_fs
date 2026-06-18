# sources/distributed-fs/ceph-client/fs/nilfs2/page.h

## Purpose

`page.h` declares NILFS2's page-cache and buffer-head helpers and defines NILFS-specific buffer state bits. It is the interface between low-level folio/buffer manipulation in `page.c`, metadata file code, btree/node caches, and the segment constructor.

## Important APIs, Types, and Functions

The extended buffer states begin at `BH_PrivateStart`: `BH_NILFS_Allocated`, `BH_NILFS_Node`, `BH_NILFS_Volatile`, `BH_NILFS_Checked`, and `BH_NILFS_Redirected`. `BUFFER_FNS()` generates accessors for node, volatile, checked, and redirected states. These bits distinguish btree node buffers, temporary or volatile buffers, verified buffers, and buffers redirected to copies during construction.

The declared helpers cover buffer acquisition (`nilfs_grab_buffer()`), forgetting/copying buffers, folio cleanliness and bug diagnostics, copying dirty pages to shadow mappings, copying pages back, clearing folio/page dirty state, counting clean buffers, and finding uncommitted delayed extents.

## Control Flow

Callers include the header when they need to tag buffers for NILFS-specific writeback or manipulate metadata shadows. Segment construction sets and clears async/volatile/redirected states through helpers declared here. Metadata code uses the dirty copy/restore helpers while GC or DAT operations need rollback-capable state.

## State and Persistence Behavior

The buffer bits are volatile state, but they control persistence decisions. `BH_NILFS_Node` changes how folio writeback completion handles split btree node pages. `BH_NILFS_Volatile` and `BH_NILFS_Redirected` are cleared after successful log write. `BH_Delay` discovery identifies data not yet committed to a segment.

## Dependencies and Integration Points

The header depends on Linux buffer heads and `nilfs.h`. It is included by `mdt.h`, `segment.c`, `segbuf.c`, recovery code, and likely bmap/btree modules that need NILFS buffer annotations.

## Risks and Edge Cases

Adding or reordering private buffer bits can collide with other buffer-head users if `BH_PrivateStart` assumptions change. Callers must not treat NILFS-specific flags as durable metadata. Correct handling of node buffers is important because btree node folios can be split and completed more than once during a log write.

## Test Signals

Test signals include state-bit transitions during btree updates, redirected-buffer cleanup after successful and failed construction, uncommitted delayed-buffer search, and dirty-page clearing in both data and metadata mappings.
