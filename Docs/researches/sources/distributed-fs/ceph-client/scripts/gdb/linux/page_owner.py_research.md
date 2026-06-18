# sources/distributed-fs/ceph-client/scripts/gdb/linux/page_owner.py

## Purpose
`page_owner.py` registers `lx-dump-page-owner`, a GDB implementation of page-owner inspection for allocation and free stack traces tied to PFNs.

## Important APIs, Types, and Functions
`DumpPageOwner` reads `page_ext`, `page_owner`, `page_owner_ops.offset`, `migrate_reason_names`, and PFN bounds. `lookup_page_ext()`, `page_ext_get()`, and `get_page_owner()` locate metadata. `read_page_owner_by_addr()` prints one PFN; `read_page_owner()` scans allocated pages.

## Control Flow
`invoke()` checks `CONFIG_PAGE_OWNER` and `page_owner_inited`, initializes `mm.page_ops`, reads global bounds, and dispatches either to full scan or `--pfn`. Full scan skips invalid PFN ranges in `MAX_ORDER_NR_PAGES` chunks and jumps by allocation order after a hit.

## State and Persistence Behavior
Read-only. It reconstructs page ownership from persistent kernel `page_ext` state and stackdepot handles; no data is cached across invocations except class fields updated during command execution.

## Dependencies and Integration Points
It depends on `mm.py` for PFN/page conversion and `stackdepot.py` for stack trace printing. It requires page owner, page extension, and stack depot debug symbols/constants.

## Risks and Test Signals
PFN validation and page extension offsets are architecture/config-sensitive. Full scans can be expensive on large memory dumps. Test with a small page-owner-enabled kernel, known allocated PFNs, invalid PFNs, and freed-page records.
