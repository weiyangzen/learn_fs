# sources/distributed-fs/ceph-client/mm/page_owner.c

## Purpose
`page_owner.c` records allocation and free provenance for physical pages when booted with `page_owner=on`. It stores stack-depot handles and metadata in `page_ext`, exposes current allocation records and stack aggregates through debugfs, and supports diagnostics such as migration reason tracking and mixed pageblock analysis.

## Important APIs, Types, And Functions
- `struct page_owner` stores allocation order, migrate reason, GFP mask, alloc/free stack handles, timestamps, pid/tgid, and command names.
- `page_owner_ops` registers a `page_ext_operations` provider with early initialization.
- `save_stack()`, `inc_stack_record_count()`, and `dec_stack_record_count()` manage stack depot records and per-stack live page counts.
- `__set_page_owner()`, `__reset_page_owner()`, `__split_page_owner()`, `__folio_copy_owner()`, and `__folio_set_owner_migrate_reason()` are allocator/migration hooks.
- `pagetypeinfo_showmixedcount_print()` scans zones for pageblocks whose allocated pages have a migratetype different from the pageblock type.
- `read_page_owner()`, `print_page_owner()`, `__dump_page_owner()`, and stack seq-file helpers expose diagnostics.
- `pageowner_init()` creates `debugfs` files `page_owner` and `page_owner_stacks/*`.

## Control Flow
Early boot parses `page_owner=`, requests early stack depot, then `init_page_owner()` registers dummy/failure/early stack handles, annotates pages allocated before the machinery was ready, seeds stack-list entries, and enables the static key. Allocation hooks save a stack, write metadata to every base page in the allocation, set `PAGE_EXT_OWNER` and `PAGE_EXT_OWNER_ALLOCATED`, and increment the stack record by base page count. Free hooks save a free stack, clear allocated state, store free metadata, and decrement the allocation stack count except for early placeholders. Migration copy moves ownership metadata from old to new folio and preserves refcount balance by assigning the new folio's prior handle back to the old folio. Debugfs reads scan PFNs, skip free/tail/unowned pages, copy metadata out from under page_ext access, and format stack/memcg details to userspace.

## State And Persistence Behavior
All state is volatile kernel debug state. Per-page metadata lives in page extensions, stack traces live in stack depot, stack aggregate list nodes are allocated dynamically, and debugfs exposes snapshots. Static branch `page_owner_inited` gates overhead after boot. No data persists across reboot.

## Dependencies And Integration Points
The file integrates with page allocator hooks, `page_ext`, stack depot, stacktrace capture, debugfs, seq_file, memcg, migration reason names, pageblock migratetypes, zone iteration, and `pagetypeinfo`. It must avoid recursion because stack capture and list insertion can allocate memory.

## Risks
- Metadata is diagnostic and can race with allocation/free scans; debugfs may miss pages or show sampled state.
- Recursive allocation while recording ownership would deadlock or corrupt attribution without `current->in_page_owner`.
- Stack record refcounts are maintained manually because this code does not use `STACK_DEPOT_FLAG_GET`.
- Early allocated pages use a special handle and do not participate in normal decrement balancing.
- Large zone scans can be expensive and should remain debug-only.

## Test Signals
- Boot with and without `page_owner=on`, verify static-key gating and debugfs file creation.
- Allocate/free high-order pages, split pages, migrate folios, and compare `page_owner` output and stack aggregate counts.
- Exercise memcg-charged pages and offline memcgs in formatted output.
- Run `pagetypeinfo` mixed counts with movable/unmovable allocations.
- Use KASAN/KCSAN/lockdep to catch recursion, list publication, and page_ext lifetime issues.
