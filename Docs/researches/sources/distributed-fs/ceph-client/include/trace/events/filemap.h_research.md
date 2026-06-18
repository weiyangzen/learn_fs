<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filemap.h -->
# sources/distributed-fs/ceph-client/include/trace/events/filemap.h

## Purpose
Declares filemap and page-cache tracepoints for folio insertion/removal, page-cache range lookup/mapping, filemap faults, and writeback error sequence handling.

## APIs, Control Flow, and State
The `mm_filemap_op_page_cache` class backs `mm_filemap_delete_from_page_cache` and `mm_filemap_add_to_page_cache`, recording inode identity, device, folio PFN, page-cache index, and folio order. The range class backs `mm_filemap_get_pages` and `mm_filemap_map_pages`, recording address-space host identity and index range. `mm_filemap_fault` records a faulting mapping and index. `filemap_set_wb_err` records a mapping and errseq value; `file_check_and_advance_wb_err` records file pointer, inode identity, old errseq, and the file's new `f_wb_err`. Device selection falls back from `host->i_sb->s_dev` to `host->i_rdev` for special mappings. The header does not own page-cache or errseq state.

## Dependencies, Integration, Risks, and Tests
Depends on folio/page-cache structures, `address_space`, memcg-visible MM includes, device number helpers, and errseq APIs. Integration points are add/delete page-cache paths, buffered read fault handling, readahead/page-cache lookup, mmap fault mapping, and writeback error propagation to files. Risks include assuming `folio->mapping` and `mapping->host` are valid at trace time, offset calculations overflowing in unusual index ranges, and confusing per-mapping writeback errors with per-file advanced state. Test signals include buffered read/write tests with tracing, page-cache add/delete under reclaim, mmap fault tests, writeback error injection, special-file mapping coverage, and large folio order tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filemap.h -->
