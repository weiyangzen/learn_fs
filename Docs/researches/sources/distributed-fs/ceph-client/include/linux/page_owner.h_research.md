<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_owner.h -->
# sources/distributed-fs/ceph-client/include/linux/page_owner.h

## Purpose
This header declares page-owner tracking hooks that record allocation stack/metadata for debugging page leaks and fragmentation.

## Important APIs, types, and functions
With `CONFIG_PAGE_OWNER`, it exports `page_owner_inited`, `page_owner_ops`, and implementation hooks for reset, set, split, folio owner copy, migration reason, dump, and pagetype mixed-count printing. Inline wrappers `reset_page_owner()`, `set_page_owner()`, `split_page_owner()`, `folio_copy_owner()`, `folio_set_owner_migrate_reason()`, and `dump_page_owner()` call implementations only when the static key is enabled. Disabled builds provide no-ops.

## Control flow
Page allocation calls set-owner when page owner is initialized. Free/reset clears owner data. Folio split/copy/migration updates metadata. Dump paths print owner info for diagnostics. Static key gating keeps disabled overhead low.

## State and persistence
Page-owner data persists in page_ext client storage while pages are allocated or tracked. Static key state records whether page-owner tracking is initialized.

## Dependencies and integration points
It depends on jump labels/static keys, page_ext operations, allocation/free paths, folio split/migration, seq_file pagetype reporting, and debugfs/page_owner users.

## Risks and test signals
Risks include missing hooks causing stale owner data, static key not enabled when expected, page_ext offset bugs, split/copy owner inconsistencies, and high overhead when enabled. Test `CONFIG_PAGE_OWNER`, debugfs page_owner output, allocation/free/split/migration paths, mixed pagetype reporting, and disabled no-op compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_owner.h -->
