# Group Research: group_885_linux_sources_os_linux_linux_mm_damon_sysfs_schemes_c_sources_os_lin_364d1af45270

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-schemes.c -->
# File Research: sources/os/linux/linux/mm/damon/sysfs-schemes.c

Implements the DAMON sysfs subtree for DAMOS schemes. It defines the per-scheme kobject hierarchy below a context's `schemes` directory, exposes all tunable scheme parameters, converts sysfs configuration into runtime `struct damos` objects, and mirrors runtime statistics/tried-region snapshots back into sysfs.

Key responsibilities:
- Creates and destroys `schemes/<idx>/` kobjects and nested directories for `access_pattern`, `dests`, `quotas`, `watermarks`, `filters`, `core_filters`, `ops_filters`, `stats`, and `tried_regions`.
- Exposes DAMOS action names (`willneed`, `cold`, `pageout`, `hugepage`, `nohugepage`, `lru_prio`, `lru_deprio`, `migrate_hot`, `migrate_cold`, `stat`) through the `action` attribute.
- Represents access-pattern bounds using shared `damon_sysfs_ul_range` directories for size, access count, and age.
- Manages quotas, quota weights, quota goals, effective quota reporting, and quota goal tuner mode.
- Represents watermark controls with metric, interval, high, mid, and low attributes.
- Represents migration destinations as dynamically sized `dests/<idx>/` entries with node id and weight.
- Represents filters split into legacy/all (`filters`), core-handled (`core_filters`), and ops-handled (`ops_filters`) directories.
- Converts configured filters, quota goals, migration destinations, and action parameters into `struct damos` instances used by the DAMON core.
- Updates sysfs-visible scheme stats and tried-region snapshots from running DAMON contexts.

Sysfs object model:
- `struct damon_sysfs_schemes` owns a dynamic array of `struct damon_sysfs_scheme *` and the `nr_schemes` attribute.
- `struct damon_sysfs_scheme` owns the complete per-scheme subtree and stores action, apply interval, and target NUMA node.
- `struct damon_sysfs_stats` exposes `nr_tried`, `sz_tried`, `nr_applied`, `sz_applied`, `sz_ops_filter_passed`, `qt_exceeds`, `nr_snapshots`, and writable `max_nr_snapshots`.
- `struct damon_sysfs_scheme_regions` owns the tried-region list and `total_bytes`; each `struct damon_sysfs_scheme_region` exposes start, end, access count, age, and filter-passed bytes.
- `struct damon_sysfs_scheme_filter` stores filter type, matching polarity, allow/reject behavior, memcg path, address range, hugepage-size range, and target index.

Important flows:
- `nr_schemes_store()` parses the requested scheme count, takes `damon_sysfs_lock`, and calls `damon_sysfs_schemes_add_dirs()` to rebuild the scheme directory array.
- `damon_sysfs_scheme_add_dirs()` creates all mandatory nested directories for a scheme and carefully unwinds partially created kobjects on error.
- `damon_sysfs_mk_scheme()` builds a runtime `struct damos` from one sysfs scheme by copying access pattern, action, apply interval, quotas, watermarks, target node, quota goals, filters, migration destinations, and max snapshot count.
- `damon_sysfs_add_schemes()` iterates configured sysfs schemes, creates runtime DAMOS schemes, and adds them to a `damon_ctx`; on failure it destroys any schemes already added to the context.
- `damos_sysfs_set_quota_scores()` commits only quota goals into an already running DAMON context, allowing live quota feedback updates without rebuilding the full context.
- `damon_sysfs_schemes_update_stats()` copies runtime scheme counters into `stats/`.
- `damos_sysfs_populate_region_dir()` is called during a DAMOS walk to populate `tried_regions/` or only accumulate `total_bytes`.
- `damon_sysfs_schemes_clear_regions()` removes all tried-region child kobjects and resets total bytes.

Validation and conversion details:
- Filter type strings are validated against the filter directory's handling layer: `core_filters` rejects ops-only filters, `ops_filters` accepts only ops-handled filters, and `filters` accepts both.
- Memcg filters and memcg quota goals resolve a user-provided cgroup path into a memcg id using `mem_cgroup_iter()` and skip offline memcgs.
- Address filters reject `end < start`; hugepage-size filters reject `min > max`.
- Quota goals with `target_value == 0` are skipped during runtime conversion.
- Node/memcg quota goals copy `nid` and resolve memcg ids as needed; user-input quota goals copy the current value directly.
- Migration destinations allocate node-id and weight arrays on the runtime scheme; if no destinations are configured, the vaddr backend falls back to the scheme's `target_nid`.

Concurrency and lifecycle notes:
- Dynamic directory count stores use `mutex_trylock(&damon_sysfs_lock)` and return `-EBUSY` if sysfs state is being used by command handling.
- String attributes such as filter `memcg_path` and quota goal `path` allocate a replacement buffer before taking the lock, then swap and free the previous value while locked.
- Kobject release functions own final `kfree()` of their containing sysfs structs; array rebuild functions drop references with `kobject_put()`.
- The code assumes parent removal routines remove child directories before dropping the parent kobject.

Notable detail:
- `damos_sysfs_populate_region_dir()` increments `sysfs_regions->nr_regions` both in the child name argument and again after `list_add_tail()`, which means the counter advances by two for a successfully materialized tried-region entry. That behavior is worth checking against expected sysfs naming/count semantics if this area is modified.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs-schemes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs.c -->
# File Research: sources/os/linux/linux/mm/damon/sysfs.c

Implements the top-level DAMON sysfs administration interface under `/sys/kernel/mm/damon/admin`. It builds the kdamond/context/target/region controls, translates sysfs input into `damon_ctx` objects, starts/stops worker threads, commits live configuration, and dispatches scheme stats/region/quota update commands.

Key responsibilities:
- Creates the root `damon/admin/kdamonds` sysfs tree during `subsys_initcall()`.
- Manages dynamic kdamond directories with `nr_kdamonds`, refusing rebuild while any represented kdamond is running.
- Restricts each kdamond to at most one context for now.
- Exposes context operations as `vaddr`, `fvaddr`, and `paddr`, with `avail_operations` filtered by registered DAMON ops.
- Exposes address unit, intervals, interval feedback goal, min/max region count, targets, target regions, schemes, state, pid, and refresh interval.
- Converts configured targets and regions into runtime DAMON targets, including PID lookup for virtual-address operations.
- Dispatches commands written to `state`.

Command handling:
- `state` accepts `on`, `off`, `commit`, `commit_schemes_quota_goals`, `update_schemes_stats`, `update_schemes_tried_bytes`, `update_schemes_tried_regions`, `clear_schemes_tried_regions`, `update_schemes_effective_quotas`, and `update_tuned_intervals`.
- `on` builds a new `damon_ctx`, starts DAMON, stores the context, and installs a repeated DAMON callback for periodic sysfs refresh.
- `off` calls `damon_stop()` but keeps the context pointer until the next `on` or kdamond directory rebuild, preserving final results.
- `commit` validates new parameters against a test copy, then commits them to the live context.
- Stats/effective quota/tuned interval updates run through `damon_call()` so the worker thread reads its own context safely.
- Tried-region updates use `damos_walk()` and `sysfs-schemes.c` helpers.

Input validation:
- Negative object counts are rejected; context count greater than one is rejected.
- `addr_unit` must be nonzero and is only meaningful for physical-address monitoring.
- Explicit region lists must be ordered and non-overlapping.
- Physical-address monitoring rejects multiple targets.
- PID targets require `find_get_pid()` to succeed when operations are PID-backed.
- DAMON attributes are validated by `damon_set_attrs()`.

Concurrency and lifecycle notes:
- `damon_sysfs_lock` serializes sysfs tree mutation and command execution.
- Dynamic directory stores return `-EBUSY` if the interface is busy.
- `state_store()` holds `damon_sysfs_lock` while parsing and dispatching commands.
- `damon_sysfs_repeat_call_fn()` periodically updates tuned intervals, scheme stats, and effective quotas when `refresh_ms` is nonzero.
- Kobject release for `damon_sysfs_kdamond` destroys any retained `damon_ctx`.

Relationships:
- Uses scheme helpers from `sysfs-schemes.c`.
- Includes `tests/sysfs-kunit.h` so static helpers can be tested with `CONFIG_DAMON_SYSFS_KUNIT_TEST`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/core-kunit.h -->
# File Research: sources/os/linux/linux/mm/damon/tests/core-kunit.h

KUnit tests for the DAMON core, included by the core implementation under `CONFIG_DAMON_KUNIT_TEST`.

Coverage areas:
- Region and target lifecycle.
- Aggregation reset.
- Region splitting and merging.
- Operations registration.
- Explicit region setting.
- Access-rate conversions and monitoring result updates.
- Attribute validation in `damon_set_attrs()`.
- Moving-sum helper behavior.
- DAMOS filter allocation and commit semantics.
- Quota goal, quota, and migration destination commit semantics.
- DAMOS scheme commit behavior for pageout and migrate-hot examples.
- Target-region commit behavior and `damon_commit_ctx()` validation.
- Address-range filter splitting behavior.
- Feedback-loop next-input behavior.
- Default-reject calculation for mixed core and ops filters.
- Minimum region count enforcement.
- `damon_is_last_region()` correctness while appending regions.

Important invariants:
- Merging adjacent regions uses size-weighted access count and age calculations.
- Splitting preserves access-rate, last-access, and age metadata in both halves.
- `damon_set_attrs()` rejects invalid region and interval settings.
- `damon_commit_ctx()` rejects non-power-of-two `min_region_sz`.
- Quota goal commits preserve relevant PSI state and resize destination lists to source length.
- Migration destination commits handle growth, shrink, empty, and nonempty cases.
- Filter commits copy type-specific fields for memcg, address, target, and hugepage-size filters.
- Address filters can split regions at filter boundaries.
- Core and ops filters affect default reject policy differently by layer.

Structure:
- Test functions are registered in `damon_test_cases`.
- Suite name: `damon`.
- Allocation or impossible setup failures skip the relevant test.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/core-kunit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/sysfs-kunit.h -->
# File Research: sources/os/linux/linux/mm/damon/tests/sysfs-kunit.h

KUnit tests for DAMON sysfs target conversion, included by `sysfs.c` under `CONFIG_DAMON_SYSFS_KUNIT_TEST`.

Coverage:
- Counts runtime targets in a `damon_ctx`.
- Finds an existing PID in a numeric range.
- Builds a minimal `damon_sysfs_targets` object containing one `damon_sysfs_target`.
- Creates a `damon_ctx`, calls `damon_sysfs_add_targets()`, and checks that target count increases.
- Changes the sysfs target PID, calls `damon_sysfs_add_targets()` again, and checks that the context now has two targets.

Important behavior documented:
- `damon_sysfs_add_targets()` appends targets; it does not clear existing targets first.
- PID-backed target addition depends on valid `struct pid` lookup.
- Empty sysfs region configuration is allowed at this layer.

Structure:
- Suite name: `damon-sysfs`.
- Single test case: `damon_sysfs_test_add_targets`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/sysfs-kunit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/vaddr-kunit.h -->
# File Research: sources/os/linux/linux/mm/damon/tests/vaddr-kunit.h

KUnit tests for the virtual-address DAMON backend, included by `vaddr.c` under `CONFIG_DAMON_VADDR_KUNIT_TEST`.

Coverage:
- Builds a synthetic VMA maple tree.
- Tests `__damon_va_three_regions()` on a representative mapping layout.
- Tests `damon_set_regions()` behavior when applying the three-region abstraction to existing monitoring regions.
- Covers slightly changed regions, removed subranges, moved middle regions, and fully replaced second/third regions.

Important behavior documented:
- DAMON vaddr simplifies an address space into three monitored ranges separated by the two largest unmapped gaps.
- The ranges cover mapped VMAs while excluding the two largest holes.
- Applying new three-region ranges adjusts existing target region boundaries, removes out-of-range regions, and creates new regions when spans move.

Structure:
- Suite name: `damon-operations`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/tests/vaddr-kunit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/damon/vaddr.c -->
# File Research: sources/os/linux/linux/mm/damon/vaddr.c

Implements DAMON operations for process virtual address spaces (`DAMON_OPS_VADDR`) and fixed virtual address ranges (`DAMON_OPS_FVADDR`). It derives monitoring regions from VMAs, samples page-table young/idle state, validates target lifetime, and applies supported DAMOS actions through `madvise`, stat walks, and NUMA migration.

Key responsibilities:
- Converts a target `struct pid` into task and `mm_struct` references safely.
- Initializes and updates monitored regions using the three-region abstraction.
- Prepares access checks by selecting a random sampling address and clearing young/idle state.
- Checks accesses by walking page tables and reading young bits, folio idle state, and MMU notifier state.
- Implements DAMOS actions: `WILLNEED`, `COLD`, `PAGEOUT`, `HUGEPAGE`, `NOHUGEPAGE`, `MIGRATE_HOT`, `MIGRATE_COLD`, and `STAT`.
- Provides scheme scoring for pageout and migration actions.
- Registers both `vaddr` and `fvaddr` operation sets.

Region initialization:
- `__damon_va_three_regions()` walks VMAs, identifies the two largest unmapped gaps, sorts them, and returns three aligned ranges.
- `damon_va_init()` initializes target regions only if the user did not provide explicit regions.
- `damon_va_update()` periodically recalculates the three ranges and applies them.
- `DAMON_OPS_FVADDR` disables automatic init/update.

Access sampling:
- `damon_va_mkold()` clears young state for PTE, PMD THP, and HugeTLB entries.
- `damon_va_young()` reports access through PTE/PMD young bits, folio idle state, or MMU notifier state.
- `__damon_va_check_access()` caches the last checked folio-sized range for a target.
- Missing `mm_struct` is treated as not accessed.

DAMOS application:
- `damos_madvise()` invokes `do_madvise()` for advice-based actions.
- `damos_va_filter_out()` evaluates ops filters, with a vaddr-specific fast path for young filters.
- `damos_va_stat()` counts bytes that pass ops filters for `DAMOS_STAT`.
- `damos_va_migrate()` isolates folios into per-destination lists and migrates them.
- Weighted migration destinations use a weighted-interleave calculation; if none are configured, migration uses `target_nid`.
- Duplicate folio accounting is avoided with `scheme->last_applied`.

Target lifecycle:
- `damon_va_target_valid()` checks whether the target PID still resolves.
- `damon_va_cleanup_target()` drops the PID reference.
- Includes `tests/vaddr-kunit.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/damon/vaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/debug.c -->
# File Research: sources/os/linux/linux/mm/debug.c

Provides MM debugging dump helpers and flag-name tables. It centralizes human-readable output for pages, folios, VMAs, mm structs, and VMA merge state, and implements optional page-struct poisoning controlled by `vm_debug`.

Key responsibilities:
- Exports migration reason names and trace print flag tables for page, GFP, and VMA flags.
- Maps encoded page types to names such as slab, hugetlb, offline, guard, table, buddy, and unaccepted.
- Dumps folio/page state including refcount, mapcount, mapping, index, PFN, large-folio metadata, memcg data, type, flags, page type, raw `struct page` bytes, and large-folio head bytes.
- Exports `dump_page()` and calls `dump_page_owner()`.
- Under `CONFIG_DEBUG_VM`, exports `dump_vma()`, `dump_mm()`, and `dump_vmg()`.
- Implements `vm_debug` parsing and `page_init_poison()`.
- Provides `vma_iter_dump_tree()` when maple-tree VMA debugging is enabled.

Important flows:
- `dump_page()` detects poisoned pages, otherwise snapshots the page before dumping.
- `dump_vma()` prints VMA bounds, mm, protection, anon_vma, vm_ops, file, private data, optional VMA refcount, and decoded flags.
- `dump_mm()` prints address-space layout, page-table pointer, refcounts, RSS/VM high-water marks, VM counters, bounds, flags, and optional subsystem fields.
- `dump_vmg()` prints `vma_merge_struct` state and recursively dumps associated mm/VMAs when present.
- `setup_vm_debug()` treats bare `vm_debug` as enabling all controllable debug features, supports `vm_debug=-`, and `vm_debug=p`.

Concurrency and diagnostic caveats:
- Some state can race while dumping; the code accepts this because output is diagnostic.
- Many helpers compile only with `CONFIG_DEBUG_VM`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/debug_page_alloc.c -->
# File Research: sources/os/linux/linux/mm/debug_page_alloc.c

Implements early configuration and guard-page helpers for page allocator debugging.

Key responsibilities:
- Defines `_debug_pagealloc_enabled_early`, initialized from `CONFIG_DEBUG_PAGEALLOC_ENABLE_DEFAULT`, and exports it.
- Defines and exports the `_debug_pagealloc_enabled` static key.
- Defines `_debug_guardpage_enabled` and `_debug_guardpage_minorder`.
- Parses `debug_pagealloc=` as a boolean early parameter.
- Parses `debug_guardpage_minorder=` and rejects values greater than `MAX_PAGE_ORDER / 2`.
- Implements `__set_page_guard()` and `__clear_page_guard()`.

Guard-page behavior:
- `__set_page_guard()` refuses orders greater than or equal to the configured minimum order, marks the page as guard, initializes its buddy list, and stores the order in page private data.
- `__clear_page_guard()` clears the guard flag and zeroes page private data.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/debug_page_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/debug_page_ref.c -->
# File Research: sources/os/linux/linux/mm/debug_page_ref.c

Defines page reference-count tracepoint wrappers. The file creates the `page_ref` tracepoints and exports both wrapper functions and tracepoint symbols for page refcount instrumentation.

Key responsibilities:
- Defines `CREATE_TRACE_POINTS` before including `trace/events/page_ref.h`.
- Implements exported wrappers for refcount set, modification, modification-and-test, modification-and-return, modification-unless, freeze, and unfreeze events.
- Each wrapper calls the corresponding `trace_page_ref_*` tracepoint.

Exported functions:
- `__page_ref_set()`
- `__page_ref_mod()`
- `__page_ref_mod_and_test()`
- `__page_ref_mod_and_return()`
- `__page_ref_mod_unless()`
- `__page_ref_freeze()`
- `__page_ref_unfreeze()`
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/debug_page_ref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/debug_vm_pgtable.c -->
# File Research: sources/os/linux/linux/mm/debug_vm_pgtable.c

Late-init self-test for architecture page-table helper semantics. It validates generic expectations from `Documentation/mm/arch_pgtable_helpers.rst` against architecture PTE/PMD/PUD/P4D/PGD helpers, swap encodings, soft-dirty handling, migration entries, THP entries, HugeTLB entries, and huge-vmap helpers.

Key responsibilities:
- Allocates a synthetic `mm_struct`, VMA, page-table hierarchy, and optional base/huge pages.
- Chooses a random user virtual address.
- Finds fixed valid PFNs from usable memory ranges.
- Constructs swap and migration entries.
- Runs `WARN_ON()`-based semantic checks at late init.
- Frees allocated pages, page tables, VMA, and mm state after testing.

Test categories:
- PTE basic and advanced transforms.
- PMD/PUD THP basic and advanced operations.
- PMD/PUD leaf checks for huge entries.
- Huge vmap helpers.
- Upper-level clear/populate helpers, accounting for folded levels.
- PTE special and protnone semantics.
- PTE/PMD soft-dirty and swap soft-dirty helpers.
- Swap exclusive helpers and raw swap encode/decode helpers.
- PMD softleaf helpers for THP migration entries.
- Migration swap entry helpers.
- HugeTLB basic dirty/write helpers.
- THP invalidation semantics.

Initialization details:
- `init_args()` allocates `mm`, `vma`, page tables, fixed PFNs, swap entries, and the largest useful page size available.
- `init_fixed_pfns()` scans memblock ranges for aligned usable memory and falls back to `start_kernel`.
- `destroy_args()` frees huge pages, base pages, page-table pages, VMA, and mm state.

Locking and safety:
- PTE tests use `pte_offset_map_lock()`.
- PMD, PUD, and top-level tests take their respective locks.
- Cache flushing follows entry installation where architecture page flags require it.
- Unsupported feature tests become no-ops.

Execution:
- `debug_vm_pgtable()` is registered with `late_initcall()`.
- Failures are warnings rather than KUnit assertions.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/debug_vm_pgtable.c -->