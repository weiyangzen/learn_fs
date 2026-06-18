<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.h -->
# sources/distributed-fs/ceph-client/net/9p/trans_common.h

This header declares `p9_release_pages()` for 9P transports. It contains no state or inline logic.

Its integration role is to let transport implementations share page-release cleanup without duplicating loops. The contract is that callers pass an array of `struct page *` entries and the number of entries to inspect.

Risks are limited to misuse by callers, especially passing an incorrect count or pages without owned references. Tests are transport-level cleanup tests that verify page refcounts are balanced on success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.h -->
