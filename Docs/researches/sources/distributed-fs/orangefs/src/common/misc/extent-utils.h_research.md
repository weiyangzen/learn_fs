<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/extent-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/extent-utils.h

Purpose: declares handle-extent parsing, membership, counting, and release helpers.

Important APIs: `PINT_create_extent_list()` returns a linked list of `PVFS_handle_extent` parsed from text. `PINT_handle_in_extent()`, `PINT_handle_in_extent_array()`, and `PINT_handle_in_extent_list()` test membership. `PINT_extent_array_count_total()` returns the total inclusive handle count represented by an extent array. `PINT_release_extent_list()` frees a list created by the parser.

State behavior: list ownership transfers to the caller, and callers must release it with `PINT_release_extent_list()`. Array APIs do not own or mutate caller data. There is no persistence.

Dependencies include PVFS internal/types/storage headers, string parsing utilities, and the local linked-list API. Integration points include server configuration, fsck, handle allocation validation, or any subsystem checking whether a handle belongs to a configured range.

Risks: the header exposes no error details for parse failure beyond returning `NULL`. It also does not specify whether extents should be sorted, normalized, or non-overlapping. Tests should verify ownership, null handling, boundary inclusion, and count behavior for invalid or unsorted arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/extent-utils.h -->
