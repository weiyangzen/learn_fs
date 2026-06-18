# Research: subset-b-006791

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/multiorder.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/multiorder.c

Purpose: userspace tests for multi-order XArray/radix-tree entries, covering iteration over sibling-covered ranges, marked iteration, RCU deletion races, and `xa_load()`/`xa_find()` behavior while multi-order entries are repeatedly created and removed.

Important APIs/types/functions: `item_insert_order()` wraps `XA_STATE_ORDER`, `xas_store()`, `xas_nomem()`, and `xas_error()` to allocate `struct item` entries with an order; `multiorder_iteration()` and `multiorder_tagged_iteration()` validate `xas_for_each()` and `xas_for_each_marked()` against fixed index/order tables; `creator_func()`, `iterator_func()`, `load_creator()`, and `load_worker()` are pthread race bodies; `multiorder_checks()` is the exported suite entry point; the weak `main()` makes the file standalone.

Control flow: deterministic tests insert fixed multi-order entries, sweep starting indexes 0..255, and assert that iterator indexes, node shifts, item indexes, and marks match the covered ranges. Race tests create one writer and many readers based on CPU count: one inserts/deletes order `RADIX_TREE_MAP_SHIFT - 1` entries with RCU freeing while readers iterate and call `xas_retry()`, then another writer cycles marked sibling entries near chunk boundaries while readers exercise `xa_load()` and marked `xa_find()`.

State and persistence: all state is in an in-memory static `DEFINE_XARRAY(array)` and global `stop_iteration`; entries are heap allocated through `item_create()` and released through `item_kill_tree()` or `item_delete_rcu()`. No persistent files are touched.

Dependencies/integration: depends on the radix-tree userspace harness in `test.h`, pthreads, RCU registration, XArray internals, and `radix_tree_cpu_dead(0)` cleanup. It integrates into the broader radix-tree test runner through `multiorder_checks()`.

Risks and test signals: assertions catch wrong sibling expansion, stale internal-node exposure, mark propagation errors, and RCU iterator/load races. The races are timing-sensitive and CPU-count-dependent; `stop_iteration` is an unsynchronized boolean, acceptable for stress testing but not a portable synchronization primitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/multiorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression.h -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression.h

Purpose: small header declaring the four radix-tree regression test entry points.

Important APIs/types/functions: declares `regression1_test()`, `regression2_test()`, `regression3_test()`, and `regression4_test()` behind `__REGRESSION_H__`.

Control flow: no executable flow; it is included by the main radix-tree runner and individual regression sources to share prototypes.

State and persistence: no state and no persistence.

Dependencies/integration: provides the C linkage contract among the regression sources and the radix-tree userspace test harness.

Risks and test signals: risk is limited to prototype drift if regression implementations are renamed or signatures change; build failures are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression1.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression1.c

Purpose: reproduces a historical radix-tree RCU lookup deadlock where a reader loops on a stale slot after tree contraction and deletion of the zero-index item.

Important APIs/types/functions: defines a local `struct page` with mutex, RCU head, refcount, and index; `page_alloc()`, `page_free()`, and `page_rcu_free()` model page lifecycle; `find_get_pages()` mimics page-cache lookup using `XA_STATE`, `xas_for_each()`, `xas_retry()`, `xas_reload()`, and `xas_reset()`; `regression1_fn()` drives reader/writer threads; `regression1_test()` starts and joins them.

Control flow: two threads synchronize on a barrier. The serial thread repeatedly inserts pages at indexes 0 and 1, deletes index 1 causing contraction, then deletes index 0 and queues both pages for RCU freeing. The other thread repeatedly calls `find_get_pages()` under RCU, retrying when the page moved or has zero count. Completion without hanging is the expected signal.

State and persistence: uses static `RADIX_TREE(mt_tree, GFP_KERNEL)`, a pthread barrier, and a heap thread array. Page objects are heap allocated and released after RCU grace periods; no persistent output.

Dependencies/integration: uses Linux radix-tree/XArray APIs, pthreads, userspace RCU shims, and `printv()` from the harness. It is invoked via `regression1_test()`.

Risks and test signals: the test can be long due to 1,000,000 writer loops and 100,000,000 reader loops. It is intentionally race-sensitive; hang indicates the regression, while normal completion plus RCU cleanup indicates pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression2.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression2.c

Purpose: verifies that range tag copying does not leave a false root tag that can make tagged gang lookup spin forever after tree extension and deletion.

Important APIs/types/functions: defines page-cache tag aliases for `XA_MARK_0..2`, a static `RADIX_TREE(mt_tree)`, local `struct page`, `page_alloc()`, and `regression2_test()`.

Control flow: fills one radix-tree chunk, tags the last slot dirty, copies dirty-to-towrite tags over a range that excludes the dirty item, inserts a new item to extend tree height, clears the original dirty tag, deletes the original chunk, then calls `radix_tree_gang_lookup_tag_slot()` for `PAGECACHE_TAG_TOWRITE`. The lookup must return rather than loop.

State and persistence: `page_count` monotonically labels heap pages; all inserted pages are freed with `radix_tree_delete()`. No persistent state.

Dependencies/integration: uses `tag_tagged_items()` from `test.c` and radix-tree tag APIs; exported as `regression2_test()`.

Risks and test signals: any stale root/internal tag can hang the test. The comments note `start` must not be zero for the reproducer. Final `BUG_ON(!radix_tree_empty())` validates cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression3.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression3.c

Purpose: checks iterator retry and resume helpers after concurrent-like insertion during radix-tree slot and tagged iteration.

Important APIs/types/functions: `regression3_test()` uses `RADIX_TREE`, `radix_tree_for_each_tagged()`, `radix_tree_for_each_slot()`, `radix_tree_iter_retry()`, `radix_tree_iter_resume()`, and `radix_tree_deref_retry()`.

Control flow: starts with one tagged entry, inserts a second entry during tagged iteration, exercises retry handling, deletes/reinserts during untagged iteration, then forces `radix_tree_iter_resume()` from index 0 for both untagged and tagged iteration. It deletes both entries at the end.

State and persistence: only stack-local tree and constant pointer values are used. No heap allocation and no persistence.

Dependencies/integration: declared by `regression.h`; uses kernel radix-tree iterator macros and `printv()`.

Risks and test signals: the historical failure was NULL dereference or stale cached tag state after resume. Completion with "passed" is the signal; assertions are implicit through crash avoidance and iterator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression4.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression4.c

Purpose: stress-tests lookup stability for an existing radix-tree entry while another thread repeatedly inserts and deletes a neighboring entry.

Important APIs/types/functions: static `worker_barrier`, `obj0`, `obj1`, and `RADIX_TREE(mt_tree)`; `reader_fn()` performs one million RCU-protected lookups of index 0; `writer_fn()` performs one million insert/delete cycles at index 1; `regression4_test()` starts both threads.

Control flow: index 0 is inserted once before the barrier. Reader and writer run concurrently; the reader aborts if `radix_tree_lookup(&mt_tree, 0)` returns anything other than `&obj0`.

State and persistence: in-memory static tree and object addresses only. The code does not delete index 0 after the test, so repeated invocations in one process may hit existing state.

Dependencies/integration: depends on pthread barriers, RCU registration, radix-tree insert/delete/lookup, and `printv()`.

Risks and test signals: abort on a wrong pointer is the main failure signal. The static tree lifetime and lack of barrier destruction are acceptable in one-shot test execution but are not reusable-test friendly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/tag_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/tag_check.c

Purpose: validates radix-tree/XArray tag semantics, including set/get/clear behavior, tag copying, tag propagation when trees grow/shrink, gang lookup for tagged entries, and leak-sensitive cleanup.

Important APIs/types/functions: `__simple_checks()` and `simple_checks()` exercise single-index tag operations; `extend_checks()` and `contract_checks()` validate propagation through height changes; `gang_check()` verifies tagged gang lookup order against a side array; `do_thrash()` mutates a million-entry model with insert/delete/tag/untag chunks; `thrash_tags()`, `leak_check()`, `__leak_check()`, `single_check()`, and `tag_check()` compose the suite.

Control flow: `tag_check()` runs single, extension, contraction, leak, simple, and randomized thrasher checks with `rcu_barrier()` and allocation count diagnostics between phases. The thrasher maintains a byte array model (`NODE_ABSENT`, `NODE_PRESENT`, `NODE_TAGGED`) and repeatedly cross-checks every modeled index plus gang lookup output.

State and persistence: all test trees are local `RADIX_TREE` instances; `thrash_state` is heap allocated and freed. The only external state is the harness `nr_allocated` counter used for leak diagnostics.

Dependencies/integration: uses helpers from `test.h`, radix-tree tag APIs, `tag_tagged_items()`, `verify_tag_consistency()`, and `item_kill_tree()`.

Risks and test signals: intentionally expensive due to full scans over `THRASH_SIZE` and nested chunk combinations. Assertions catch stale tags, missing tags, double-delete behavior, and inconsistent internal tag bitmaps; allocation logs help identify leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/tag_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.c

Purpose: shared userspace test helpers for radix-tree and XArray tests, providing `struct item` lifecycle, assertions, gang scans, tag copying, tag consistency verification, tree cleanup, and height checks.

Important APIs/types/functions: wrappers `item_tag_set()`, `item_tag_clear()`, `item_tag_get()`; allocation/lifecycle helpers `item_create()`, `item_insert()`, `item_sanity()`, `item_free()`, `item_delete()`, `item_delete_rcu()`; lookup assertions; `item_gang_check_present()` and `item_full_scan()`; `tag_tagged_items()` modeled after page writeback tagging; recursive `verify_node()`/`verify_tag_consistency()`; `item_kill_tree()`; `tree_verify_min_height()`.

Control flow: helpers are called by tests rather than run directly. `tag_tagged_items()` locks an XArray, walks marked entries, sets a second mark, periodically pauses/unlocks and waits for RCU to exercise iterator restart. `item_kill_tree()` iterates the XArray, frees non-value entries, clears slots, and asserts emptiness.

State and persistence: no private persistent state; operates on caller-owned trees and heap items. RCU deletion defers freeing through `call_rcu()`.

Dependencies/integration: includes Linux type/kernel/bitops shims and exposes prototypes via `test.h`. It reaches normally private radix-tree helpers such as `entry_to_node()`, `root_tag_get()`, `node_maxindex()`, and `shift_maxindex()` for structural validation.

Risks and test signals: helpers rely heavily on `assert()`, so disabled assertions would weaken the suite. `item_sanity()` is central for multi-order correctness, ensuring covered indexes share the same order mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.h -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.h

Purpose: shared interface for radix-tree/XArray userspace tests.

Important APIs/types/functions: defines `struct item` with `rcu_head`, `index`, and `order`; declares item lifecycle/lookup/tag helpers, scan helpers, `tag_tagged_items()`, test-suite entry points (`xarray_tests()`, `tag_check()`, `multiorder_checks()`, `iteration_test()`, `benchmark()`, `idr_checks()`, `ida_tests()`), allocation counter, and normally-private radix-tree internals used for validation.

Control flow: no direct control flow; this is a contract header included by the test programs.

State and persistence: declares external `nr_allocated` and `radix_tree_preloads`; otherwise no state.

Dependencies/integration: includes Linux GFP/types/radix-tree/RCU headers. It is the main coupling point between standalone test files and the userspace kernel-library shims.

Risks and test signals: broad exposure of private radix-tree internals is intentional for tests but tightly couples the suite to implementation layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/xarray.c -->
# sources/distributed-fs/ceph-client/tools/testing/radix-tree/xarray.c

Purpose: userspace shim that compiles and runs the kernel `lib/test_xarray.c` suite.

Important APIs/types/functions: includes `xarray-shared.h`, `test.h`, undefines `XA_DEBUG`, includes `../../../lib/test_xarray.c`, defines `xarray_tests()` as `xarray_checks()` plus `xarray_exit()`, and provides a weak standalone `main()`.

Control flow: standalone mode registers the RCU thread, initializes radix-tree/XArray infrastructure, runs XArray checks, simulates CPU teardown, waits for RCU, reports nonzero `nr_allocated`, unregisters RCU, and exits.

State and persistence: no file state; heap/XArray state is created by the imported kernel test and cleaned by `xarray_exit()`/RCU barriers.

Dependencies/integration: bridges kernel XArray selftest code into the userspace tools test harness. The weak `main()` lets another runner link this file without duplicate main conflicts.

Risks and test signals: correctness depends on imported `test_xarray.c`; nonzero `nr_allocated` after `rcu_barrier()` signals leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/radix-tree/xarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/rbtree/Makefile

Purpose: builds userspace red-black tree and interval-tree test binaries from kernel library sources plus local shims.

Important APIs/types/functions: `TARGETS = rbtree_test interval_tree_test`; `OFILES` combines shared objects and `rbtree-shim.o`, `interval_tree-shim.o`, `maple-shim.o`; `DEPS` tracks rbtree/interval headers and library C files; adds `CONFIG_INTERVAL_TREE_SPAN_ITER` for interval-tree shim and test object.

Control flow: default `targets` builds both binaries after including `../shared/shared.mk`; target-specific dependencies force rebuilds when kernel headers/library code changes; `clean` removes binaries, objects, copied/generated files.

State and persistence: writes build outputs in the directory/OUTPUT context; no runtime state.

Dependencies/integration: integrated with the tools/testing shared userspace build system and kernel `lib/rbtree.c`, `lib/interval_tree.c`, `lib/rbtree_test.c`, and `lib/interval_tree_test.c`.

Risks and test signals: stale dependency lists can miss rebuilds after kernel API changes. Build success is the primary signal for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/interval_tree_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/rbtree/interval_tree_test.c

Purpose: userspace wrapper for the kernel interval-tree test suite.

Important APIs/types/functions: includes shared shims and `../../../lib/interval_tree_test.c`; `usage()` documents runtime tunables; `interval_tree_tests()` calls imported init/exit functions; `main()` parses `-n`, `-p`, `-q`, `-s`, `-a`, `-m`, and `-r` into imported globals such as `nnodes`, `perf_loops`, `nsearches`, `search_loops`, `search_all`, `max_endpoint`, and `seed`.

Control flow: parse options, initialize maple-tree support with `maple_tree_init()`, then run the interval-tree tests.

State and persistence: imported test globals hold configuration; no persistent files are written.

Dependencies/integration: links with interval-tree kernel library and maple-tree shared support. It is built by the local rbtree Makefile.

Risks and test signals: invalid options call `usage()` and exit `-1`; functional and performance results are produced by the imported test body.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/interval_tree_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/rbtree_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/rbtree/rbtree_test.c

Purpose: userspace wrapper for the kernel red-black tree test suite.

Important APIs/types/functions: includes `../../../lib/rbtree_test.c`; `usage()` explains `-n`, `-p`, `-c`, `-r`; `rbtree_tests()` calls imported `rbtree_test_init()` and `rbtree_test_exit()`; `main()` populates imported globals `nnodes`, `perf_loops`, `check_loops`, and `seed`.

Control flow: command-line parsing is followed by a single `rbtree_tests()` run.

State and persistence: runtime configuration is kept in imported globals; no persistent state.

Dependencies/integration: depends on shared userspace kernel shims and the kernel `lib/rbtree_test.c` implementation. Built by `tools/testing/rbtree/Makefile`.

Risks and test signals: only thin-wrapper logic is local; behavioral pass/fail comes from imported tests and their assertions/output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/rbtree_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/test.h -->
# sources/distributed-fs/ceph-client/tools/testing/rbtree/test.h

Purpose: declares rbtree userspace test-suite entry points.

Important APIs/types/functions: `rbtree_tests()` and `interval_tree_tests()`.

Control flow: no direct flow; allows wrappers or aggregate runners to call either suite.

State and persistence: none.

Dependencies/integration: coordinates the rbtree and interval-tree wrapper C files.

Risks and test signals: only risk is declaration drift; compile/link failures expose mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/rbtree/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/scatterlist/Makefile

Purpose: builds a userspace scatterlist test harness with copied/generated kernel scatterlist sources and lightweight Linux header stubs.

Important APIs/types/functions: sets include paths, debug/O2/warnings, AddressSanitizer and UBSan flags; supports `BUILD=32`; builds `main` from `main.o scatterlist.o`; `include` target creates `linux/` and `asm/` stubs and copies `include/linux/scatterlist.h`; `scatterlist.c` target uses `sed` to remove `static`, `__always_inline`, and `inline` from kernel `lib/scatterlist.c`.

Control flow: `targets` depends on `include` and binary build; `clean` removes copied/generated headers, source, object files, binary, and `asm` directory.

State and persistence: creates generated files in the test directory during build.

Dependencies/integration: imports kernel scatterlist implementation into a userspace test binary and relies on local `linux/mm.h`/generated stubs.

Risks and test signals: source rewriting via `sed` is brittle if kernel code depends on inlining/static semantics. Sanitizer-enabled build and test execution are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/linux/mm.h -->
# sources/distributed-fs/ceph-client/tools/testing/scatterlist/linux/mm.h

Purpose: minimal userspace replacement for Linux memory-management helpers needed by scatterlist tests.

Important APIs/types/functions: defines page constants, alignment macros, `virt_to_page()`, `page_address()`, PFN/page conversion macros, `min()`/`min_t()`, allocation helpers `__get_free_page()`, `free_page()`, `kmalloc()`, `kmalloc_array()`, `kfree`, error pointer helpers `ERR_PTR()`, `PTR_ERR()`, `IS_ERR()`, and no-op kmemleak/cache helpers.

Control flow: most functions are inline wrappers around `malloc()`/`free()` or assert-only stubs for unsupported kernel operations such as `page_to_phys()` and kmap/kunmap.

State and persistence: heap allocations are process-local; no persistence.

Dependencies/integration: included by the copied scatterlist code and local tests to satisfy kernel API references in userspace.

Risks and test signals: unsupported functions intentionally `assert(0)`, so tests only cover scatterlist paths that do not require real page mapping or physical address translation. The fake `struct page *` model is pointer/PFN arithmetic, not a full page allocator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/linux/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/scatterlist/main.c

Purpose: table-driven userspace tests for scatterlist table allocation and segment coalescing from page arrays.

Important APIs/types/functions: `struct test` captures expected return, input PFNs, optional append PFNs, total size, maximum segment size, and expected segments; `set_pages()` maps PFN arrays to fake page pointers; `fail()` prints diagnostics; `VALIDATE` asserts conditions; `main()` iterates test cases.

Control flow: each case builds fake pages, calls either `sg_alloc_table_from_pages_segment()` or `sg_alloc_append_table_from_pages()`, checks return status, optionally appends a second range, validates `nents` and `orig_nents`, then frees the table. Cases cover contiguous, reversed, fragmented, appended, and max-segment-limited page sequences.

State and persistence: only stack/compound-literal test data and heap allocations inside scatterlist APIs; no files.

Dependencies/integration: includes generated/copied `linux/scatterlist.h` and uses fake page primitives from local Linux stubs.

Risks and test signals: expected segment counts are the core signal. The fake PFN model assumes `PAGE_SIZE`-aligned pointer arithmetic and does not model real memory attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/scatterlist/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/Makefile

Purpose: top-level kselftest makefile enumerating selftest target directories and orchestrating build, run, install, hotplug, packaging, and clean operations.

Important APIs/types/functions: `TARGETS` list, `TARGETS_HOTPLUG`, `SKIP_TARGETS`, `FORCE_TARGETS`, `KBUILD_OUTPUT`/`O` handling, `BUILD`, `KHDR_INCLUDES`, default `all`, `run_tests`, `hotplug`, `run_hotplug`, `install`, `gen_tar`, and `clean` targets.

Control flow: default `all` iterates over targets and optional install dependencies, invoking sub-makes with per-target `OUTPUT`. `run_tests` builds then invokes each target's `run_tests`. `install` copies kselftest runner files, installs each target under `KSFT_INSTALL_PATH`, emits `kselftest-list.txt`, and writes a git-described `VERSION` if available. `gen_tar` packages the install tree.

State and persistence: creates build output trees, install directories, test lists, archives, and optional VERSION. Honors out-of-tree build locations.

Dependencies/integration: central integration point for all `tools/testing/selftests` subdirectories, `scripts/subarch.include`, and `lib.mk` conventions.

Risks and test signals: because `FORCE_TARGETS` defaults empty, the aggregate build can succeed if at least one target builds. `SKIP_TARGETS` excludes BPF and sched_ext by default. Target list ordering and missing target directories affect emitted test inventory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/acct/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/acct/Makefile

Purpose: builds the process accounting syscall selftest.

Important APIs/types/functions: `TEST_GEN_PROGS := acct_syscall`, adds `-Wall`, and includes `../lib.mk`.

Control flow: kselftest `lib.mk` supplies build/run/install behavior for the generated program.

State and persistence: build output only.

Dependencies/integration: part of the top-level selftests `acct` target.

Risks and test signals: build failure or missing syscall headers/libraries are the only local signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/acct/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/acct/acct_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/acct/acct_syscall.c

Purpose: kselftest for the `acct()` syscall, checking that process accounting logs a terminated child process.

Important APIs/types/functions: `main()` uses kselftest header/plan/result helpers, `geteuid()`, `fopen()`, `acct()`, `fork()`, `wait()`, `fseek()`, and `ftell()`.

Control flow: requires root or skips. Creates `process_log`, enables accounting to that file, forks a child, parent waits, measures file size, disables accounting, and passes if the file grew. Child falls through returning failure.

State and persistence: creates/overwrites `process_log` in the current working directory and toggles system process accounting until `acct(NULL)` is called.

Dependencies/integration: depends on kernel process accounting support, root privileges, and kselftest reporting. Built by the acct Makefile.

Risks and test signals: the code checks `errno` after `acct(filename)` without clearing it first, so stale errno could cause false error reporting. Cleanup on fork failure disables accounting but does not close the file; successful path closes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/acct/acct_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/Makefile

Purpose: builds ALSA kselftest binaries and a shared local configuration helper library.

Important APIs/types/functions: verifies `pkg-config --exists alsa`; adds ALSA CFLAGS/LDLIBS, pthreads, output rpath, and `KHDR_INCLUDES`; sets `TEST_GEN_PROGS` to `mixer-test`, `pcm-test`, `test-pcmtest-driver`, `utimer-test`; `TEST_GEN_PROGS_EXTENDED` to `libatest.so` and `global-timer`; `TEST_FILES` to `conf.d` and `pcm-test.conf`; builds `libatest.so` from `conf.c`; links programs against `-latest`.

Control flow: `lib.mk` handles kselftest targets; pattern rules make each C test depend on the shared library and header.

State and persistence: writes binaries and `libatest.so` under `OUTPUT`; installs config files as test assets.

Dependencies/integration: requires ALSA development package and libasound. Integrates all ALSA selftests with shared config lookup code.

Risks and test signals: build hard-fails if ALSA pkg-config metadata is missing. Runtime rpath assumes tests can locate `libatest.so` in the execution directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/alsa-local.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/alsa-local.h

Purpose: public header for ALSA selftest configuration helpers.

Important APIs/types/functions: declares `get_alsalib_config()`, config load/free functions, card lookup, subtree and typed getters, string-array getter, `struct card_cfg_data` with card id, ALSA config pointer, filename, config id, and linked-list pointer, plus global `conf_cards`.

Control flow: no executable flow; used by `conf.c`, PCM tests, and mixer tests.

State and persistence: declares global linked-list state populated by `conf_load()`.

Dependencies/integration: includes `alsa/asoundlib.h` and exposes libasound `snd_config_t` usage to tests.

Risks and test signals: callers share mutable global `conf_cards`; failure to call `conf_free()` leaks configuration nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/alsa-local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.c

Purpose: implements ALSA selftest configuration loading, sysfs matching, card-specific config assignment, and typed lookup helpers.

Important APIs/types/functions: `get_alsalib_config()` builds a minimal `ctl.hw`/`pcm.hw` libasound config; fallback `snd_config_load_string()` supports older ALSA; `conf_load_from_file()` parses config files; `sysfs_get()` and `sysfs_match()` read `/sys` values and apply regexes; `match_config()`, `assign_card_config()`, and `assign_card_configs()` populate `conf_cards`; getters include `conf_get_subtree()`, `conf_get_count()`, `conf_get_string()`, `conf_get_long()`, `conf_get_bool()`, and `conf_get_string_array()`.

Control flow: `conf_load()` scans `conf.d` for `.conf` files, parses those whose global sysfs block matches the host, records each card block, then associates matching blocks with `/sys/class/sound/card*`. Consumers later fetch per-card config and typed values.

State and persistence: global linked list `conf_cards` owns matched card configs and filename strings for matched files. It reads sysfs and config files but writes nothing.

Dependencies/integration: depends on libasound config APIs, POSIX directory/sysfs IO, regex, and kselftest failure helpers. Used by ALSA PCM and mixer tests.

Risks and test signals: `conf_free()` deletes `conf->config` but does not free each `card_cfg_data` node, so process-exit cleanup hides a leak. `sysfs_match()` returns false on missing files but fatal-exits on malformed config, making config syntax a hard gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.d/Lenovo_ThinkPad_P1_Gen2.conf -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.d/Lenovo_ThinkPad_P1_Gen2.conf

Purpose: host-specific ALSA selftest configuration for Lenovo ThinkPad P1 Gen2 HDA audio.

Important APIs/types/functions: defines a global `sysfs` match against `class/dmi/id/product_sku`; defines `card.hda` with card-level sysfs matches for subsystem device/vendor; configures `pcm.0.0` PLAYBACK tests `time1`, `time2`, `time3` and a CAPTURE presence block.

Control flow: loaded by `conf.c` only if the global sysfs regex matches. If card sysfs matches, PCM tests use the card-specific `pcm.*` blocks for required devices and system-specific timing tests.

State and persistence: declarative config only; no runtime writes.

Dependencies/integration: consumed by ALSA `conf_load()`, `missing_devices()`, and `run_time_tests()`.

Risks and test signals: regexes are hardware-specific and stale DMI/subsystem strings would silently skip the config. Uncommented missing-device blocks can convert absent PCMs into explicit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/conf.d/Lenovo_ThinkPad_P1_Gen2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/global-timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/global-timer.c

Purpose: helper executable for `utimer-test` that opens a global ALSA timer, counts async tick callbacks for a timeout, and prints the total.

Important APIs/types/functions: global `ticked`; `async_callback()` increments it; `bind_to_timer()` constructs `hw:CLASS=...,DEV=...,SUBDEV=...`, opens timer nonblocking, sets auto-start/ticks, registers async handler, starts timer, busy-waits until timeout, then stops/closes; `main()` parses device/subdevice/timeout.

Control flow: line-buffer stdout, parse arguments, bind to requested timer, print "Timer has started", wait for ticks, print "Total ticks count".

State and persistence: in-process tick counter only; no files.

Dependencies/integration: libasound timer API and SIGIO async delivery. Invoked by `utimer-test` via `popen()`.

Risks and test signals: busy-wait loop consumes CPU. `perror("Usage: ...")` is semantically wrong because no errno is set. Failure to open/configure timer exits nonzero and causes parent test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/global-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/mixer-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/mixer-test.c

Purpose: kselftest that enumerates ALSA mixer controls on all cards and validates readability, naming conventions, writable value ranges, invalid-write handling, and event generation.

Important APIs/types/functions: `struct card_data` and `struct ctl_data` store card/control metadata; `find_controls()` opens cards through local ALSA config, enumerates controls, subscribes to events, and builds linked lists; `wait_for_event()` polls/read control events; `ctl_value_index_valid()` and `ctl_value_valid()` validate boolean/integer/integer64/enumerated values; `test_ctl_get_value()`, `test_ctl_name()`, `write_and_verify()`, `test_ctl_write_default()`, valid/invalid write helpers, and event summary tests implement checks.

Control flow: `main()` prints a kselftest header, discovers controls, plans `num_controls * TESTS_PER_CONTROL`, then for each control runs get, name, default-write, valid-write, invalid-write, missing-event, and spurious-event tests. Writable tests restore the default value after mutation.

State and persistence: maintains linked lists of opened card handles and control metadata; writes mixer controls on the live system and relies on restoring defaults. No persistent files.

Dependencies/integration: libasound control API, poll, kselftest, and `get_alsalib_config()` from `conf.c`.

Risks and test signals: can interfere with active audio because it writes controls. Volatile controls cannot be compared exactly. Source contains a suspicious extra closing brace in `wait_for_event()` and duplicated `snd_ctl_elem_value_alloca(&val)` in invalid boolean testing; if present in the exact build, these are compile/logic risks. Event counters expose missing or spurious kernel notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/mixer-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.c

Purpose: kselftest that enumerates ALSA PCM devices and runs timing-based playback/capture tests using default and system-specific configurations.

Important APIs/types/functions: `struct card_data` and `struct pcm_data`; global `pcm_list`, `pcm_missing`, `default_pcm_config`, and `results_lock`; timestamp helpers; config parsing helpers `device_from_id()`, `missing_device()`, `missing_devices()`; discovery `find_pcms()`; core `test_pcm_time()`; `run_time_tests()`; per-card thread `card_thread()`; `main()`.

Control flow: loads `pcm-test.conf`, loads host-specific `conf.d`, discovers PCM devices/subdevices/streams, records configured-but-missing devices, computes kselftest plan, reports unmatched configs/missing PCMs, then spawns one thread per card to run default and system-specific time tests. Each time test opens `hw:card,device,subdevice`, applies configured access/format/rate/channel/period/buffer params, writes or reads two seconds of silence, drains, and checks elapsed time within 100 ms.

State and persistence: uses linked lists and libasound handles; no persistent writes. It reads config files and live ALSA/sysfs state.

Dependencies/integration: libasound PCM/control APIs, pthreads, kselftest, `alsa-local` helpers, `pcm-test.conf`, and optional per-host config.

Risks and test signals: can conflict with active audio. Timing checks can be flaky under heavy scheduler load. Source includes duplicated `if (err < 0)` and an apparent stray comment terminator in the system test result block; these are build/maintenance risks if not patched elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.conf -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.conf

Purpose: default ALSA PCM timing-test matrix consumed by `pcm-test`.

Important APIs/types/functions: declares `pcm.test.time1` through `time7` with descriptions, primary `S16_LE` format, alternate `S32_LE`, rates from 8 kHz to 96 kHz, channels, period sizes, and buffer sizes.

Control flow: `pcm-test.c` iterates the `pcm.test` compound and runs each block as a `time` test unless overridden.

State and persistence: declarative config only.

Dependencies/integration: parsed by libasound config APIs through `conf_load_from_file()`.

Risks and test signals: `time6` description says 6 channel but `channels 2`, which may be an intentional label error or stale config. Unsupported formats/rates become skips/failures depending on default versus system-specific class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/pcm-test.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/test-pcmtest-driver.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/test-pcmtest-driver.c

Purpose: kselftest harness for the virtual `snd-pcmtest` driver, validating PCM playback/capture data patterns, non-interleaved access, and reset ioctl behavior.

Important APIs/types/functions: `struct pattern_buf`, `patterns[CH_NUM]`, `struct pcmtest_test_params`; `read_patterns()` reads debugfs pattern files; `get_test_results()` reads debugfs result flags; `get_sec_buf_len()` and `setup_handle()` configure ALSA PCM parameters; fixture `pcmtest`; tests `playback`, `capture`, `ni_capture`, `ni_playback`, and `reset_ioctl`.

Control flow: fixture setup requires root, reads `/sys/kernel/debug/pcmtest` patterns, finds ALSA card named `PCM-Test`, and fills default params. Playback tests generate expected channel-interleaved or non-interleaved pattern buffers and expect debugfs `pc_test` to become 1. Capture tests read from the device and compare against patterns. Reset test calls `snd_pcm_reset()` and checks `ioctl_test`.

State and persistence: reads debugfs state and writes/reads ALSA PCM streams; heap sample buffers are temporary.

Dependencies/integration: requires `snd-pcmtest` module/debugfs, libasound, root, and kselftest harness.

Risks and test signals: skips if root or module/debugfs prerequisites are missing. `read_patterns()` uses `%u` into an `int` field and fixed 1024-byte buffers; oversized debugfs pattern lengths would be unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/test-pcmtest-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/utimer-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/utimer-test.c

Purpose: tests userspace-driven ALSA timers (`CONFIG_SND_UTIMER`) and invalid timer creation handling.

Important APIs/types/functions: fixture `timer_f` creates a user timer with `SNDRV_TIMER_IOCTL_CREATE`; `ticking_func()` triggers ticks; parsers `parse_timer_output()` and `parse_timer_result()` consume `global-timer` output; `TEST_F(timer_f, utimer)` coordinates helper process and trigger thread; `TEST(wrong_timers_test)` checks invalid create inputs.

Control flow: setup requires root and opens `/dev/snd/timer`, skipping if utimer ioctls are unsupported. The main utimer test launches `./global-timer`, waits until it prints started, spawns a thread issuing `SNDRV_TIMER_IOCTL_TRIGGER` once per second, parses total tick count, and expects it to equal `TICKS_COUNT`. The negative test sends zero-resolution and NULL create requests and expects failure/no id update.

State and persistence: creates a kernel user timer file descriptor and closes it in teardown; no files written.

Dependencies/integration: depends on ALSA timer device, sound UAPI headers, pthreads, kselftest harness, and the built `global-timer` helper.

Risks and test signals: `pthread_join(ticking_thread, NULL)` assumes the started line was seen and the thread was created. Timing deltas make the test slow and sensitive to helper startup or output parsing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/utimer-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/Makefile

Purpose: registers AMD P-state shell selftests with kselftest.

Important APIs/types/functions: empty `all` target prevents accidental `run_tests`; normalizes `ARCH`; on x86 adds AMD and Intel pstate tracer scripts to `TEST_FILES`; sets `TEST_PROGS += run.sh`; adds `basic.sh`, `tbench.sh`, and `gitsource.sh`; includes `../lib.mk`.

Control flow: kselftest invokes `run.sh`; files are installed as dependencies.

State and persistence: build/install metadata only.

Dependencies/integration: integrates with top-level selftests and power tracer utilities under `tools/power/x86`.

Risks and test signals: tracer files are only included on x86; non-x86 still installs shell tests but runtime skips are handled by `run.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/basic.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/basic.sh

Purpose: basic AMD P-state unit-test module loader check.

Important APIs/types/functions: inclusion guard `FILE_BASIC`; `amd_pstate_basic()` prints a banner, dry-runs `modprobe amd-pstate-ut`, loads it, removes it, and exits skip/fail on errors.

Control flow: called by `run.sh` for `basic` or `all`; successful load/unload prints `amd-pstate-basic: ok`.

State and persistence: temporarily loads kernel module `amd-pstate-ut`.

Dependencies/integration: requires `/sbin/modprobe`, root privileges from parent prerequisite, and `ksft_skip`.

Risks and test signals: load failure is a hard fail after dry-run says module exists; missing module is skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/config

Purpose: kselftest kernel config fragment for AMD P-state unit testing.

Important APIs/types/functions: sets `CONFIG_X86_AMD_PSTATE_UT=m`.

Control flow: no runtime flow.

State and persistence: declarative build configuration.

Dependencies/integration: used by kselftest/config tooling to request the test module.

Risks and test signals: if the kernel is not built with this module, `basic.sh` skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/gitsource.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/gitsource.sh

Purpose: AMD P-state performance/power benchmark using a Git source tree build/test workload across governors.

Important APIs/types/functions: inclusion guard `FILE_GITSOURCE`; globals for Git 2.15.1 archive and governors; CSV helpers; cleanup helpers; `install_gitsource()` downloads/extracts source; `run_gitsource()` starts AMD pstate tracer and runs `make test` under `perf stat` and `/usr/bin/time`; `parse_gitsource()`, `gather_gitsource()`, comparison helpers, `plot_png_gitsource()`, and `amd_pstate_gitsource()` orchestrate metrics.

Control flow: clears prior outputs, ensures source tree exists, writes CSV headers, backs up governors, loops over `ondemand` and `schedutil`, switches governors, runs workload `LOOP_TIMES`, parses desired performance/frequency/load/time/energy/performance-per-watt, plots PNGs, calculates comparisons, restores governors, and cleans transient logs.

State and persistence: downloads `git-2.15.1.tar.gz`, extracts `git-2.15.1`, writes CSV/result/log/PNG files, modifies cpufreq governors, and creates tracer result directories.

Dependencies/integration: sourced by `run.sh`; relies on `TRACER`, `PERF`, `MAKE_CPUS`, `CPUFREQROOT`, `bc`, `awk`, `gnuplot`, `wget`, `tar`, and benchmark/toolchain availability.

Risks and test signals: network dependency and large workload make it slow/flaky. Shell has typos such as "Comprison" and "Permance"; division by zero is possible if energy parsing fails. Governor restoration depends on backup log integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/gitsource.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/run.sh

Purpose: main AMD P-state kselftest driver that validates prerequisites, parses options, dispatches basic/tbench/gitsource/all tests, and manages shared environment.

Important APIs/types/functions: inclusion guard `FILE_MAIN`; sources `basic.sh`, `tbench.sh`, `gitsource.sh`; globals for tracer/perf/sysfs/output/loop/timing; helpers `scaling_name()`, `count_cpus()`, governor backup/restore/switch, `amd_pstate_all()`, `help()`, `parse_arguments()`, prerequisite command checks, `prerequisite()`, `do_test()`, cleanup helpers.

Control flow: parse CLI, verify x86 AMD CPU, verify current scaling driver or comparative driver, require root-like `/dev` write access, check perf/tbench as needed, locate sysfs/cpufreq, clear dumps, run selected function through `tee`, then remove transient logs.

State and persistence: reads `/proc/cpuinfo` and sysfs, modifies cpufreq governors, writes output CSV/log/PNG files through sourced scripts, and removes some logs at end.

Dependencies/integration: kselftest invokes this script; depends on shell utilities, cpufreq sysfs, perf, tbench/dbench, tracer scripts, and root privileges.

Risks and test signals: message uses `COMPARISON_TEST` typo instead of `COMPARATIVE_TEST`; `cat /proc/cpuinfo | grep` is inefficient but harmless. Governor mutation is invasive; failed exits can leave governors changed if restoration is bypassed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/tbench.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/tbench.sh

Purpose: AMD P-state throughput/power benchmark using `tbench` across governors.

Important APIs/types/functions: inclusion guard `FILE_TBENCH`; governor list; CSV/cleanup helpers; `run_tbench()` starts tracer and `tbench_srv`, runs `tbench` under `perf stat`, kills server, waits for jobs; `parse_tbench()`, `gather_tbench()`, comparison helpers, `plot_png_tbench()`, and `amd_pstate_tbench()` orchestrate results.

Control flow: clears prior outputs, writes CSV headers, backs up governors, for each governor switches policy governors, loops benchmark runs, parses tracer CPU metrics, throughput, energy, and performance per watt, restores governors, plots, computes comparisons, and cleans logs.

State and persistence: starts/kills `tbench_srv`, modifies governors, writes CSV/result/PNG/log/tracer output directories, then removes many transient files.

Dependencies/integration: sourced by `run.sh`; requires tbench, perf energy events, AMD pstate tracer, `bc`, `awk`, `gnuplot`, and cpufreq sysfs.

Risks and test signals: `kill $pid` can misbehave if `pidof tbench_srv` returns empty or multiple PIDs. Plot file name has typo `tbench_perfromance.png`. Metrics depend on perf energy availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/tbench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/Makefile

Purpose: top-level dispatcher for arm64 kselftest subtargets.

Important APIs/types/functions: detects `ARCH`, sets `ARM64_SUBTARGETS` to `tags signal pauth fp mte bti abi gcs` on arm64/aarch64, configures CFLAGS/include paths/KHDR includes, exports `CFLAGS` and `top_srcdir`, and defines `all`, `install`, `run_tests`, `emit_tests`, and `clean` loops.

Control flow: each target iterates subdirectories, creates `OUTPUT` subdir, and invokes make in the subtarget with optional `FORCE_TARGETS` failure behavior. Non-arm64 emits no tests.

State and persistence: creates per-subtarget output directories.

Dependencies/integration: integrates arm64 subtests with top-level kselftest and header include layout.

Risks and test signals: host/cross compile depends on `ARCH` override. Empty `ARM64_SUBTARGETS` on non-arm64 prevents noisy emit output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/Makefile

Purpose: builds arm64 ABI selftests.

Important APIs/types/functions: `TEST_GEN_PROGS := hwcap ptrace syscall-abi tpidr2`; includes `../../lib.mk`; declares `syscall-abi` dependency on C and assembly; builds `tpidr2` as static freestanding nolibc binary with stripped/optimized flags.

Control flow: kselftest `lib.mk` builds generated programs; explicit rules handle assembly-linked and nolibc cases.

State and persistence: build outputs only.

Dependencies/integration: depends on arm64 compiler, nolibc include tree, and kselftest build variables.

Risks and test signals: `tpidr2` intentionally avoids libc because TPIDR2 is libc-managed; build flags are sensitive to toolchain support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/hwcap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/hwcap.c

Purpose: validates consistency among arm64 HWCAP auxv bits, `/proc/cpuinfo` feature strings, and instruction-level SIGILL/SIGBUS behavior for many architecture extensions.

Important APIs/types/functions: numerous `*_sigill()` and `*_sigbus()` probes execute representative instructions; `struct hwcap_data` maps feature name, auxv selector, bit, cpuinfo string, probe functions, and reliability flags; signal handlers skip faulting instructions by advancing PC; `cpuinfo_present()` scans `Features`; `inst_raise_sigill()`/`inst_raise_sigbus()` are generated by macros; `main()` iterates all features.

Control flow: for every `hwcaps[]` entry, the test checks auxv bit against `/proc/cpuinfo`, runs the SIGILL probe if available, and only runs SIGBUS probe when SIGILL did not occur. Reliable probes must fault when missing and not fault when present; unreliable missing probes are skipped with diagnostics.

State and persistence: signal handler globals record seen signals; no persistent writes.

Dependencies/integration: uses arm64 UAPI HWCAP definitions, auxv, signal/ucontext, kselftest, and direct instruction encodings for extensions that assemblers may not know.

Risks and test signals: feature list is tightly coupled to kernel headers and CPU architecture. Some probes intentionally rely on undefined/unavailable instruction behavior and may be skipped when not reliable. `uninstall_sigaction()` calls `sigaction(signum, NULL, NULL)`, which queries rather than restores default disposition, so installed handlers remain for process lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/hwcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/ptrace.c

Purpose: tests arm64 ptrace ABI register sets for TLS/TPIDR values and hardware debug resource reporting.

Important APIs/types/functions: `have_sme()` checks `HWCAP2_SME`; `test_tpidr()` exercises `PTRACE_GETREGSET`/`SETREGSET` with `NT_ARM_TLS` for TPIDR and optional TPIDR2; `test_hw_debug()` reads `NT_ARM_HW_WATCH` and `NT_ARM_HW_BREAK`; `do_child()` requests tracing and stops; `do_parent()` waits, confirms stop signal, runs tests, and kills child.

Control flow: parent forks child. Child does `PTRACE_TRACEME` and raises SIGSTOP. Parent waits for the expected stop, then performs register-set tests on the stopped child and finally kills it. Main plans `EXPECTED_TESTS` and reports counts.

State and persistence: parent/child process state only; no files.

Dependencies/integration: ptrace, wait/signal APIs, arm64 regset constants, auxv, and kselftest.

Risks and test signals: if child exits unexpectedly, the test fails. TPIDR2 expectations vary with SME support: with SME it should round-trip, without SME it may read zero. Hardware debug arch field must be nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi-asm.S

Purpose: assembly engine for `syscall-abi.c`, loading synthetic GPR/FPSIMD/SVE/SME state, issuing a syscall, and saving post-syscall state for C-side validation.

Important APIs/types/functions: exports `do_syscall`; defines SME instruction encoding macros `_ldr_za`, `_str_za`, `_ldr_zt`, `_str_zt`; uses globals `gpr_in/out`, `fpr_in/out`, `z_in/out`, `p_in/out`, `ffr_in/out`, `za_in/out`, `zt_in/out`, and `svcr_in/out`.

Control flow: saves callee-saved registers and input VLs, optionally writes SVCR and loads ZA/ZT0, loads GPRs and either FPSIMD or SVE predicate/vector/FFR state, executes `svc #0`, stores all relevant register state, records SVCR/ZA/ZT0 when SME is active, clears SVCR for future tests, restores callee-saved registers, and returns.

State and persistence: all state is exchanged through global buffers in the linked C file; no files.

Dependencies/integration: requires arm64 SVE/SME assembler support or raw encodings, `syscall-abi.h` bit definitions, and matching buffer layouts in `syscall-abi.c`.

Risks and test signals: any mismatch between vector length, buffer sizing, or register save order can create false ABI failures. The comment says x8 in GPR input selects syscall number; C-side checks validate preservation rules after return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.c

Purpose: validates arm64 syscall ABI preservation/clearing rules across FPSIMD, SVE, SME streaming mode, ZA, ZT0, predicates, FFR, SVCR, and GPRs.

Important APIs/types/functions: global buffers for each register class; setup/check pairs (`setup_gpr`/`check_gpr`, `setup_fpr`/`check_fpr`, `setup_z`/`check_z`, `setup_p`/`check_p`, `setup_ffr`/`check_ffr`, `setup_svcr`/`check_svcr`, `setup_za`/`check_za`, `setup_zt`/`check_zt`); `regset[]` dispatch table; `do_test()` calls assembly `do_syscall()`; `test_one_syscall()` runs combinations for `getpid()` and `sched_yield()`; `sve_count_vls()` and `sme_count_vls()` enumerate supported VLs; `main()` plans and reports.

Control flow: enumerate SVE/SME vector lengths from high to low, then for each syscall run FPSIMD-only, each SVE VL, each SME VL with SM+ZA, SM, and ZA, and cross-product SVE/SME cases. Setup fills random inputs; assembly performs syscall; check functions enforce expected preservation or zeroing.

State and persistence: random test patterns and output buffers are process globals. No persistence.

Dependencies/integration: requires arm64 auxv HWCAPs, prctl SVE/SME VL controls, signal context size macros, kselftest, and `syscall-abi-asm.S`.

Risks and test signals: test count scales with hardware-supported vector lengths. Emulator slowness is mitigated by `ARCH_SVE_VQ_MAX 16`. Assumes syscall clobber/preserve rules in comments; mismatches print detailed register diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.h

Purpose: shared SVCR bit definitions for the arm64 syscall ABI C and assembly code.

Important APIs/types/functions: defines `SVCR_ZA_MASK`, `SVCR_SM_MASK`, `SVCR_ZA_SHIFT`, and `SVCR_SM_SHIFT`.

Control flow: no runtime flow.

State and persistence: none.

Dependencies/integration: included by `syscall-abi.c` and `syscall-abi-asm.S` to keep bit positions consistent.

Risks and test signals: incorrect constants would invalidate all SME streaming/ZA checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/tpidr2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/tpidr2.c

Purpose: nolibc arm64 selftest for TPIDR2 behavior across default state, read/write, scheduling, fork, and clone-with-CLONE_VM.

Important APIs/types/functions: `set_tpidr2()`/`get_tpidr2()` access system register `S3_3_C13_C0_5`; tests `default_value()`, `write_read()`, `write_sleep_read()`, `write_fork_read()`, `write_clone_read()`; raw `sys_clone()` wrapper; `main()` gates on `/proc/sys/abi/sme_default_vector_length`.

Control flow: if SME support appears present via proc sysctl, plan five tests. The fork test expects child to inherit parent TPIDR2 then change its own; the clone-VM test expects child to start with zero while parent remains unchanged. Without SME support, all tests are skipped.

State and persistence: manipulates TPIDR2 register state in current process/children and allocates an 8 MiB clone stack. No files are written.

Dependencies/integration: built statically with nolibc; depends on SME/TPIDR2 kernel ABI, wait/clone syscalls, kselftest.

Risks and test signals: process/thread semantics are subtle; wrong child exit status maps to test failure. The clone stack is not freed on parent success path, acceptable for process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/tpidr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/Makefile

Purpose: builds freestanding arm64 Branch Target Identification test binaries with and without BTI properties.

Important APIs/types/functions: `TEST_GEN_PROGS := btitest nobtitest`; `CFLAGS_BTI` uses `-mbranch-protection=standard -DBTI=1`; `CFLAGS_NOBTI` uses `-mbranch-protection=none -DBTI=0`; object lists include test, signal, start, syscall, system, stubs, and trampoline variants; links static `-nostdlib` binaries; includes `../../lib.mk`.

Control flow: pattern rules compile every C/S file twice, once BTI and once non-BTI, then link corresponding binaries.

State and persistence: build outputs only.

Dependencies/integration: arm64 toolchain with branch-protection support and local freestanding runtime files.

Risks and test signals: dynamic loader BTI support is intentionally avoided. The `nobtitest` link still uses `$(CFLAGS_BTI)` in the command, but its objects are compiled non-BTI; note/property behavior should be checked if failures appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/assembler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/assembler.h

Purpose: assembly macro support for the BTI freestanding tests.

Important APIs/types/functions: GNU property constants; `startfn`/`endfn` function macros; `emit_aarch64_feature_1_and` emits `.note.gnu.property` with BTI/PAC bits when `BTI` is true; hint macros for `paciasp`, `autiasp`, `bti` variants.

Control flow: macros expand at assembly time only.

State and persistence: emits ELF note metadata into object files.

Dependencies/integration: included by BTI assembly sources.

Risks and test signals: incorrect note encoding would make kernel/loader treat the binary as non-BTI or malformed. Raw hint encodings preserve compatibility with assemblers lacking mnemonic support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/assembler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/btitest.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/btitest.h

Purpose: declares BTI trampoline and target stub functions used by the C test.

Important APIs/types/functions: trampolines `call_using_br_x0()`, `call_using_br_x16()`, `call_using_blr()`; target stubs `nohint_func()`, `bti_none_func()`, `bti_c_func()`, `bti_j_func()`, `bti_jc_func()`, `paciasp_func()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: connects `test.c` with `trampoline.S` and `teststubs.S`.

Risks and test signals: prototype mismatch would affect branch/call ABI and test validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/btitest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.c

Purpose: minimal freestanding signal API wrappers for the BTI tests.

Important APIs/types/functions: `sigemptyset()`, `sigaddset()`, `sigaction()`, and `sigprocmask()` implemented using local signal structures and raw syscalls.

Control flow: set manipulation functions update bitsets; wrappers call `__NR_rt_sigaction` and `__NR_rt_sigprocmask`.

State and persistence: only caller-provided signal sets; no persistence.

Dependencies/integration: uses `system.h` syscall wrapper and Linux signal UAPI. Replaces libc in static freestanding BTI binaries.

Risks and test signals: signal-set sizing must match kernel ABI; wrong mask size would break SIGILL handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.h

Purpose: header for freestanding signal wrappers used by BTI tests.

Important APIs/types/functions: includes Linux signal definitions, aliases `sighandler_t`, and declares `sigemptyset()`, `sigaddset()`, `sigaction()`, `sigprocmask()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: included by `test.c` and implemented by `signal.c`.

Risks and test signals: depends on `system.h` and kernel UAPI definitions matching the running architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/start.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/start.S

Purpose: freestanding process entry point for BTI tests.

Important APIs/types/functions: `_start` moves stack pointer to `x0` and branches to C `start`; emits AArch64 feature note.

Control flow: kernel enters `_start`; `_start` passes initial stack/argc pointer to `start()` without libc setup.

State and persistence: no state beyond initial register transfer and ELF note.

Dependencies/integration: linked into both BTI and non-BTI binaries.

Risks and test signals: assumes initial stack layout parsed by `test.c`; no libc initialization is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/start.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/syscall.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/syscall.S

Purpose: raw syscall wrapper for BTI freestanding binaries.

Important APIs/types/functions: `syscall` function starts with `bti c`, moves syscall number from `w0` to `w8`, shifts arguments down from `x1..x7` to `x0..x6`, executes `svc #0`, and returns.

Control flow: direct wrapper from C-like varargs ABI to Linux arm64 syscall ABI.

State and persistence: no persistent state.

Dependencies/integration: used by `system.c` and `signal.c`; emits GNU property note.

Risks and test signals: supports up to seven passed values in the wrapper convention; all callers in this suite fit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/syscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.c

Purpose: tiny freestanding system-call based runtime helpers for BTI tests.

Important APIs/types/functions: `exit()` calls `__NR_exit` and then `unreachable()`; `write()` calls `__NR_write`.

Control flow: wrappers delegate directly to assembly `syscall`.

State and persistence: no internal state; `write()` emits to file descriptors.

Dependencies/integration: included in static BTI binaries with `system.h` and `syscall.S`.

Risks and test signals: no errno handling; callers inspect behavior directly or terminate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.h

Purpose: freestanding type and syscall declarations for BTI tests.

Important APIs/types/functions: defines `size_t` and `ssize_t` from kernel types; includes errno/compiler/hwcap/ptrace/unistd UAPI; declares `syscall()`, `exit()`, and `write()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: common header for BTI C files.

Risks and test signals: bypassing libc means all required types/constants must come from compatible kernel headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/test.c

Purpose: TAP-producing BTI behavior test that calls different landing-pad stubs through different indirect branch forms and verifies expected SIGILL behavior.

Important APIs/types/functions: output helpers `fdputs()`, `putstr()`, `putnum()`; `handler()` handles SIGILL, reports BTYPE, and clears PSTATE BTYPE to resume; `__do_test()` and `do_test` macro run trampoline/stub combinations; `start()` parses auxv, installs handler, runs 18 tests, prints summary, and exits.

Control flow: detects HWCAP/PACA and HWCAP2/BTI from initial stack auxv, reports whether binary was built for BTI, sets SIGILL handler, then tests six target stubs through three trampolines. Expected SIGILLs are disabled when hardware or binary BTI support is absent.

State and persistence: global counters and current-test strings; no file persistence beyond TAP output.

Dependencies/integration: freestanding runtime, signal wrappers, BTI assembly stubs/trampolines, arm64 auxv and signal context definitions.

Risks and test signals: exact expected matrix is architecture-sensitive. Handler must correctly skip/clear BTYPE; unexpected SIGILL exits with 128+signal after printing summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/teststubs.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/teststubs.S

Purpose: branch target functions with different BTI/PAC landing sequences for the BTI test matrix.

Important APIs/types/functions: defines `bti_none_func`, `bti_c_func`, `bti_j_func`, `bti_jc_func`, `paciasp_func`, and `nohint_func`.

Control flow: each function executes its landing hint/PAC pair if applicable and returns.

State and persistence: no state; emits GNU property note.

Dependencies/integration: called by trampolines from `test.c`.

Risks and test signals: landing hints encode the expected valid branch classes; wrong hint would flip expected SIGILL outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/teststubs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/trampoline.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/trampoline.S

Purpose: indirect branch/call trampolines used to enter BTI test stubs with different branch types.

Important APIs/types/functions: `call_using_br_x0()` branches via `br x0`; `call_using_br_x16()` moves target to `x16` then branches; `call_using_blr()` uses PAC prologue/epilogue and `blr x0`.

Control flow: each trampoline receives a function pointer and transfers control, returning to caller for `blr` paths or via target return.

State and persistence: saves/restores frame pointer/link register in `call_using_blr`; emits feature note.

Dependencies/integration: declared in `btitest.h` and used by `test.c`.

Risks and test signals: branch register choice influences PSTATE.BTYPE and expected BTI landing compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/Makefile

Purpose: builds arm64 floating-point, SVE, SME, ZA, ZT, vector-length, and stress selftests.

Important APIs/types/functions: declares many `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, and `TEST_PROGS_EXTENDED`; sets `top_srcdir`, `KHDR_INCLUDES`, and `EXTRA_CLEAN`; custom rules link several assembly/nolibc programs (`fp-pidbench`, `fpsimd-test`, `sve-test`, `ssve-test`, `za-fork`, `za-test`, `zt-test`) and C programs with shared objects such as `asm-utils.o` and `rdvl.o`; includes `../../lib.mk`.

Control flow: kselftest build rules compile the listed generated and extended programs; custom targets supply special link flags where libc must be avoided.

State and persistence: build outputs only.

Dependencies/integration: arm64 compiler, kernel headers, nolibc, local assembly utilities, and FP/SVE/SME source files not all in this subset.

Risks and test signals: toolchain support for SVE/SME instructions and static/nolibc builds is critical. Missing `asm-utils.o` or `rdvl.o` affects multiple targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-offsets.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-offsets.h

Purpose: hard-coded constants for arm64 FP assembly selftests, covering signal structure sizes/offsets and signal constants.

Important APIs/types/functions: defines `sa_sz`, `sa_flags`, `sa_handler`, `sa_mask_sz`, signal numbers, `SA_NODEFER`, `SA_SIGINFO`, and `ucontext_regs`.

Control flow: no runtime flow.

State and persistence: none.

Dependencies/integration: included by assembly tests that need signal/ucontext layout without C-generated offsets.

Risks and test signals: hard-coded ABI offsets must match the target kernel/userspace ABI; drift causes assembly signal handling failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-utils.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-utils.S

Purpose: reusable freestanding assembly utility routines for arm64 FP/SVE/SME tests.

Important APIs/types/functions: functions `putc`, `puts`, `putdec`, `putdecn`, `puthexb`, `puthexnibble`, `dumphex`, `memcpy`, `memfill_ae`, `memclr`, and `memfill`.

Control flow: output helpers use raw `__NR_write` syscalls to stdout; numeric formatting uses division/modulo loops; memory helpers perform bytewise copy/fill loops.

State and persistence: writes only to stdout or caller-provided memory buffers.

Dependencies/integration: includes `assembler.h` for `function` macros and `<asm/unistd.h>` for syscall numbers. Linked into multiple FP/SVE/SME freestanding tests.

Risks and test signals: intentionally minimal implementations may clobber documented registers only; tests relying on additional preservation would be buggy. Output helpers bypass libc and errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-utils.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/assembler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/assembler.h

Purpose: macro library for arm64 FP/SVE/SME assembly tests.

Important APIs/types/functions: recursive `_for`/`__for` macros generate repeated code; `function`/`endfunction` annotate functions; `define_accessor` builds indexed accessor jump tables; `puts` macro emits literal strings and calls runtime `puts`; GCS constants and `enable_gcs` macro issue `prctl(PR_SET_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE)`.

Control flow: all behavior is assembly-time macro expansion except `enable_gcs`, which emits runtime syscall instructions.

State and persistence: may emit string constants into `.rodata`; no persistent state.

Dependencies/integration: included by arm64 FP assembly sources and `asm-utils.S`.

Risks and test signals: recursive macro expansion can stress assembler limits for large ranges. `enable_gcs` assumes current kernel supports the prctl numbers and shadow-stack semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/assembler.h -->
