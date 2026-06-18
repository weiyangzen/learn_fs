<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/erofs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/erofs.h

## Purpose
Defines EROFS filesystem tracepoints for lookup, inode loading, folio reads/readahead, and logical-to-physical block mapping.

## APIs, Control Flow, and State
Events are `erofs_lookup`, `erofs_fill_inode`, `erofs_read_folio`, `erofs_readahead`, `erofs_map_blocks_enter`, and `erofs_map_blocks_exit`. Formatting helpers print major/minor device and EROFS nid pairs, file type, block-map request flags (`FIEMAP`, `READMORE`, `FINDTAIL`), and resulting map flags (`MAPPED`, `META`, `PARTIAL_MAPPED`, `PARTIAL_REF`, `FRAGMENT`). Mapping entry captures logical address and requested length; exit adds physical address, physical length, result flags, and return code. The header stores no filesystem state; it snapshots inode fields and `struct erofs_map_blocks`.

## Dependencies, Integration, Risks, and Tests
Depends on EROFS inode helpers such as `EROFS_I()`, `erofs_iloc()`, `erofs_blknr()`, and map flag definitions supplied by including implementation files. Integration points are VFS lookup, inode fill from metadata, compressed or raw folio read paths, readahead, fiemap, and map-block resolution. Risks include formatter/header coupling to EROFS private definitions without direct includes, tracing invalid map structures on failed paths, and confusing raw-vs-compressed read interpretation. Test signals include mount/read workloads with trace events enabled, lookup of files/directories, fiemap over fragmented data, compressed-file readahead, and negative map return coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/erofs.h -->
