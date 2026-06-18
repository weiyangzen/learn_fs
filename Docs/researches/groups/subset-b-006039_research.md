# subset-b-006039 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/test-ww_mutex.c -->
# sources/distributed-fs/ceph-client/kernel/locking/test-ww_mutex.c

## Purpose
Provides a loadable kernel selftest for the wound/wait mutex API. It validates basic mutual exclusion, recursive/self acquisition rejection, ABBA deadlock detection, slowpath recovery, cyclic dependency recovery, and stress behavior for both wound-wait and wait-die ww classes.

## Important APIs, Types, And Functions
The module defines `wd_class` and `ww_class`, a global unbound workqueue, and sysfs attribute `run_tests`. Core tests are `test_mutex`, `test_aa`, `test_abba`, `test_cycle`, and `stress`. Worker helpers include `test_mutex_work`, `test_abba_work`, `test_cycle_work`, `stress_inorder_work`, `stress_reorder_work`, and `stress_one_work`. It exercises `ww_mutex_lock`, `ww_mutex_trylock`, `ww_mutex_lock_slow`, `ww_mutex_unlock`, `ww_acquire_init`, and `ww_acquire_fini`.

## Control Flow
`test_ww_mutex_init` seeds the random state, creates the workqueue and `/sys/kernel/test_ww_mutex/run_tests`, then runs all test classes once. A sysfs write reruns the same suite under `run_lock`. The suite first checks ordinary mutual exclusion, then self-acquire behavior, then ABBA and multi-thread cycles with and without slowpath resolution, followed by timed stress loops over randomized lock orders.

## State And Persistence
State is transient: stack-allocated test structures, allocated stress arrays, random order arrays, completions, and the workqueue. The only persistent runtime interface is the sysfs kobject/attribute until module unload.

## Dependencies And Integration Points
Depends on kernel workqueues, completions, random state, sysfs kobjects, module init/exit, and `linux/ww_mutex.h`. It integrates with debug ww mutex deadlock injection by disabling injection in deterministic deadlock tests when `CONFIG_DEBUG_WW_MUTEX_SLOWPATH` is set.

## Risks And Edge Cases
The tests are timing-sensitive because they use short completion timeouts and concurrent workqueue scheduling. Stress coverage may miss rare races because failures are logged with `pr_err_once`. The ABBA and cycle tests rely on completions ordering worker progress correctly. Memory allocation failures are handled, but a failed stress helper allocation can silently reduce coverage.

## Test Signals
Useful signals are module load success, `All ww mutex selftests passed`, no WARNs from `READ_ONCE(mutex.ctx)` checks, and clean sysfs reruns. Failures log specific scenarios such as mutual exclusion failure, missed ABBA deadlock, unresolved cyclic deadlock, or stress worker errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/test-ww_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/ww_mutex.h -->
# sources/distributed-fs/ceph-client/kernel/locking/ww_mutex.h

## Purpose
Implements the internal wound/wait mutex policy shared by regular mutex and RT mutex builds. It abstracts waiter traversal and wait-lock handling, orders ww acquisition contexts, decides when a transaction should die or wound another owner, and maintains `ww_mutex.ctx` accounting.

## Important APIs, Types, And Functions
The file defines the `MUTEX`, `MUTEX_WAITER`, and `WAIT_LOCK` aliases for normal versus `WW_RT` builds. Traversal helpers are `__ww_waiter_first`, `__ww_waiter_next`, `__ww_waiter_prev`, `__ww_waiter_last`, and `__ww_waiter_add`. Policy helpers include `ww_mutex_lock_acquired`, `__ww_ctx_less`, `__ww_mutex_die`, `__ww_mutex_wound`, `__ww_mutex_check_waiters`, `ww_mutex_set_context_fastpath`, `__ww_mutex_kill`, `__ww_mutex_check_kill`, `__ww_mutex_add_waiter`, and `__ww_mutex_unlock`.

## Control Flow
On acquisition, `ww_mutex_lock_acquired` records the context and increments its acquired count. Fastpath acquisitions publish `lock->ctx`, use a memory barrier against the waiters flag, then scan waiters if contention appeared. Slowpath waiter insertion sorts context waiters by transaction priority and stamp, kills younger wait-die contexts early, or wounds younger holders for wound-wait. Unlock clears the context and decrements the acquired count.

## State And Persistence
State lives in `struct ww_acquire_ctx` fields such as `stamp`, `acquired`, `wounded`, `contending_lock`, and `is_wait_die`, and in `struct ww_mutex.ctx`. No durable persistence exists. Memory ordering is explicit around context publication and waiter visibility.

## Dependencies And Integration Points
Depends on mutex internals, rtmutex internals under `WW_RT`, lockdep annotations, wake queues, scheduler blocked-on tracking, and optional RT/deadline priority comparisons. It is included by the mutex and rtmutex implementations rather than being a standalone public header.

## Risks And Edge Cases
Correctness depends on sorted waiter iteration, matching barriers between fastpath context publication and slowpath waiter insertion, and not mixing wait-die with wound-wait in one class. RT mode adds task priority and deadline ordering, while non-RT mode cannot use unstable PI priority. Debug checks catch recursive acquisition, class mismatches, and wrong post-`-EDEADLK` recovery.

## Test Signals
Signals come from ww mutex selftests, lockdep warnings, RT and non-RT build coverage, ABBA/cycle deadlock tests, and stress runs that force repeated `-EDEADLK` plus `ww_mutex_lock_slow` recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/ww_mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/ww_rt_mutex.c -->
# sources/distributed-fs/ceph-client/kernel/locking/ww_rt_mutex.c

## Purpose
Provides the RT mutex backed implementation of the public `ww_mutex` operations. It compiles `rtmutex.c` with `WW_RT` policy hooks and exports trylock, blocking lock, interruptible lock, and unlock entry points.

## Important APIs, Types, And Functions
Exports `ww_mutex_trylock`, `ww_mutex_lock`, `ww_mutex_lock_interruptible`, and `ww_mutex_unlock`. The central helper is `__ww_rt_mutex_lock`, which wraps lockdep nesting, fastpath `rt_mutex_try_acquire`, and slowpath `rt_mutex_slowlock`.

## Control Flow
Trylock delegates to plain `rt_mutex_trylock` when no ww context is supplied. With a context, it resets `wounded` when the context holds no locks, attempts `__rt_mutex_trylock`, publishes the ww context with `ww_mutex_set_context_fastpath`, then records lockdep nesting. Blocking lock rejects recursive acquisition with `-EALREADY`, performs lockdep acquisition, uses the RT fastpath if possible, and otherwise enters the RT slowpath with the ww context and task state.

## State And Persistence
State is held in the embedded `struct rt_mutex`, the ww context pointer on `struct ww_mutex`, and lockdep maps. Unlock clears ww context accounting before releasing lockdep state and calling `__rt_mutex_unlock`.

## Dependencies And Integration Points
Depends on `rtmutex.c`, `ww_mutex.h`, lockdep, scheduler sleep rules, and exported module symbols. It is the PREEMPT_RT-compatible backend for users of the generic `linux/ww_mutex.h` API.

## Risks And Edge Cases
The main risks are preserving ww semantics while RT priority inheritance reorders waiters, resetting `wounded` only when no locks are held, and keeping lockdep nesting paired on all failure paths. Recursive same-context locking must return `-EALREADY` without corrupting lockdep state.

## Test Signals
Coverage should include RT builds, `test-ww_mutex`, lockdep-enabled kernels, interruptible wait interruption, trylock behavior with and without contexts, and deadlock recovery paths returning `-EDEADLK` from the RT slowpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/ww_rt_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/module/Kconfig

## Purpose
Defines the kernel configuration surface for loadable module support. It enables the module subsystem itself and selects optional features for debugging, unloading, symbol versioning, signatures, compression/decompression, namespace import enforcement, modprobe path configuration, exported symbol trimming, and fast module address lookup.

## Important APIs, Types, And Functions
This is Kconfig rather than C code. Symbols include `MODULES`, `MODULE_DEBUGFS`, `MODULE_DEBUG`, `MODULE_STATS`, `MODULE_DEBUG_AUTOLOAD_DUPS`, `MODULE_FORCE_LOAD`, `MODULE_UNLOAD`, `MODULE_FORCE_UNLOAD`, `MODULE_UNLOAD_TAINT_TRACKING`, `MODVERSIONS`, `GENKSYMS`, `GENDWARFKSYMS`, `EXTENDED_MODVERSIONS`, `BASIC_MODVERSIONS`, `MODULE_SIG`, `MODULE_SIG_FORCE`, `MODULE_SIG_ALL`, `MODULE_COMPRESS`, `MODULE_DECOMPRESS`, `MODULE_ALLOW_MISSING_NAMESPACE_IMPORTS`, `MODPROBE_PATH`, `TRIM_UNUSED_KSYMS`, and `MODULES_TREE_LOOKUP`.

## Control Flow
At configuration time, `MODULES` gates the rest of the menu. Nested choices select versioning implementation, signature hash, and compression algorithm. Several symbols select support libraries, for example `MODULE_SIG` selects `MODULE_SIG_FORMAT`, compression selects crypto/decompression code, and module tree lookup is enabled when perf, tracing, or CFI need frequent lookups.

## State And Persistence
The file persists build-time policy in `.config`. Runtime effects include whether syscalls are available, whether module unload paths exist, whether signatures are enforced, and what `/proc/sys/kernel/modprobe` defaults to.

## Dependencies And Integration Points
Integrates Kbuild, modpost, signing tools, OpenSSL requirements, crypto libraries, debugfs, sysfs/procfs consumers, userspace `modprobe`, and architecture capabilities such as `HAVE_ASM_MODVERSIONS`.

## Risks And Edge Cases
Incompatible options can change ABI expectations: forced loads taint kernels, strict signature enforcement rejects unsigned modules, compression requires matching userspace and in-kernel support, and extended modversions are important for long names and Rust support. Missing namespace imports can be fatal unless explicitly relaxed.

## Test Signals
Signals are Kconfig dependency resolution, allmodconfig/defconfig builds, module load/unload tests under each feature set, signature enforcement tests, compressed module loading, and debugfs/procfs/sysfs presence when corresponding options are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/Makefile -->
# sources/distributed-fs/ceph-client/kernel/module/Makefile

## Purpose
Selects the object files that implement the kernel module subsystem for the active configuration.

## Important APIs, Types, And Functions
This Kbuild file always builds `main.o`, `strict_rwx.o`, and `kmod.o`. Optional objects include `dups.o`, `decompress.o`, `signing.o`, `livepatch.o`, `tree_lookup.o`, `debug_kmemleak.o`, `kallsyms.o`, `procfs.o`, `sysfs.o`, `kdb.o`, `version.o`, `tracking.o`, and `stats.o`. It also disables KCOV instrumentation for `main.o`.

## Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments and links only the enabled support files into the kernel. The object selection mirrors the Kconfig feature matrix.

## State And Persistence
No runtime state is stored here. It persists build graph decisions and instrumentation policy.

## Dependencies And Integration Points
Integrates module Kconfig symbols with the kernel build. `KCOV_INSTRUMENT_main.o := n` prevents noisy or unsafe coverage from hot module loader paths called by SLUB stack tracing.

## Risks And Edge Cases
Missing an object breaks references declared in `internal.h`; adding an object without the right Kconfig guard can create dead code or unresolved symbols. Instrumenting `main.o` could produce excessive or misleading coverage.

## Test Signals
Build coverage across module configurations is the primary signal, especially combinations of `CONFIG_MODULES`, `CONFIG_SYSFS`, `CONFIG_KALLSYMS`, `CONFIG_MODULE_SIG`, `CONFIG_MODULE_DECOMPRESS`, and `CONFIG_MODULE_UNLOAD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/debug_kmemleak.c -->
# sources/distributed-fs/ceph-client/kernel/module/debug_kmemleak.c

## Purpose
Provides kmemleak integration for loaded modules. It prevents kmemleak from scanning module memory ranges that are writable but not executable and are not the primary data or init-data allocations.

## Important APIs, Types, And Functions
Defines `kmemleak_load_module(const struct module *mod, const struct load_info *info)`. It iterates all module memory types with `for_each_mod_mem_type` and calls `kmemleak_no_scan` for selected allocations.

## Control Flow
After a module has been allocated and moved into final memory, `layout_and_allocate` calls `kmemleak_load_module`. The helper skips `MOD_DATA`, `MOD_INIT_DATA`, and ROX memory, marking the remaining writable non-executable module regions as no-scan.

## State And Persistence
It changes kmemleak metadata for module allocation bases. No module loader state is owned by this file.

## Dependencies And Integration Points
Depends on `linux/kmemleak.h`, `struct module`, module memory type iteration, and `internal.h`. It is compiled only with `CONFIG_DEBUG_KMEMLEAK`.

## Risks And Edge Cases
Incorrect classification can hide real leaks or cause false positives by scanning memory that contains non-pointer data. It relies on `mod->mem[type].is_rox` and memory type assignment already being correct.

## Test Signals
Kmemleak-enabled module load/unload tests should show fewer false positives without suppressing leaks in normal module data. Build coverage with and without `CONFIG_DEBUG_KMEMLEAK` validates the inline stub contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/debug_kmemleak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/decompress.c -->
# sources/distributed-fs/ceph-client/kernel/module/decompress.c

## Purpose
Implements in-kernel decompression for compressed module files loaded through `finit_module` with `MODULE_INIT_COMPRESSED_FILE`. It supports exactly the compression algorithm selected at build time: gzip, xz, or zstd.

## Important APIs, Types, And Functions
External functions are `module_decompress` and `module_decompress_cleanup`. Allocation helpers are `module_extend_max_pages` and `module_get_next_page`. Algorithm-specific helpers are `module_gzip_decompress`, `module_xz_decompress`, and `module_zstd_decompress`. When sysfs is enabled, `compression_show` exposes the active format.

## Control Flow
`module_decompress` records compressed length for stats, preallocates a page pointer array, runs the selected decompressor into highmem pages, then `vmap`s the pages into `info->hdr` and sets `info->len` to decompressed size. Cleanup unmaps, frees pages, and frees the page array. `init_module_from_file` frees the original compressed buffer immediately after decompression.

## State And Persistence
Temporary state is stored in `load_info.pages`, `max_pages`, `used_pages`, `hdr`, and `len`. A read-only `/sys/module/compression` style attribute under the module kset is registered late when sysfs support exists.

## Dependencies And Integration Points
Depends on zlib, xz, or zstd libraries, highmem mapping, vmap/vunmap, sysfs, and module stats. It feeds the ordinary ELF validation path by producing the same `load_info.hdr` buffer shape as uncompressed reads.

## Risks And Edge Cases
Input magic and frame validation are critical. Gzip optional filename parsing, xz stream termination, zstd window limits, page array growth, and partial output pages are failure-prone. Cleanup must handle partially filled `load_info` after decompressor or allocation failure.

## Test Signals
Load valid and corrupt `.ko.gz`, `.ko.xz`, and `.ko.zst` files under matching configs. Verify decompression failures increment stats, cleanup leaves no leaks, sysfs reports the expected format, and signature verification still applies to the decompressed module content path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/dups.c -->
# sources/distributed-fs/ceph-client/kernel/module/dups.c

## Purpose
Suppresses duplicate in-kernel module autoload requests so concurrent `request_module()` calls for the same module do not trigger repeated userspace `modprobe` and repeated `finit_module` memory pressure.

## Important APIs, Types, And Functions
Exports internal helpers `kmod_dup_request_exists_wait` and `kmod_dup_request_announce`. State is represented by `struct kmod_dup_req`, the RCU-protected `dup_kmod_reqs` list, `kmod_dup_mutex`, `first_req_done`, `complete_work`, and `delete_work`. The boot/module parameter `module.enable_dups_trace` controls WARN versus warning logging.

## Control Flow
Before launching modprobe, `__request_module` asks `kmod_dup_request_exists_wait`. A synchronous first request inserts an entry; duplicate synchronous callers wait for completion and reuse the first return value; duplicate nowait callers return success immediately. When modprobe completes, `kmod_dup_request_announce` stores the result and queues completion work, which wakes waiters and later schedules deletion of the tracking entry.

## State And Persistence
Tracking entries persist briefly in memory after completion and are deleted by delayed work after about 60 seconds. No durable persistence exists.

## Dependencies And Integration Points
Depends on workqueues, completions, RCU lists, mutexes, module parameters, and `internal.h`. It is called from `kmod.c` around userspace helper execution and configured by `CONFIG_MODULE_DEBUG_AUTOLOAD_DUPS`.

## Risks And Edge Cases
The first nowait request cannot anchor a synchronous wait because it has no meaningful result to share. Entry deletion is heuristic, so late repeated requests can still reach userspace. Return sharing must not complete before the first caller records the result. String length handling assumes module names fit `MODULE_NAME_LEN`.

## Test Signals
Concurrent `request_module()` storms should emit duplicate warnings, avoid repeated synchronous modprobe work, and return consistent status to waiters. Tests should cover nowait first requests, wait first requests, killable waits, trace mode, and delayed deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/dups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/internal.h -->
# sources/distributed-fs/ceph-client/kernel/module/internal.h

## Purpose
Defines private shared declarations for the module subsystem. It centralizes `struct load_info`, symbol lookup structures, module use tracking, memory layout encoding helpers, feature-gated prototypes, and inline stubs used by the split implementation files.

## Important APIs, Types, And Functions
Key types are `struct kernel_symbol`, `struct load_info`, `enum mod_license`, `struct find_symbol_arg`, `struct module_use`, `enum fail_dup_mod_reason`, `struct mod_fail_load`, `struct mod_unload_taint`, `struct mod_tree_root`, and `struct modversion_info_ext`. Important declarations cover signature checks, symbol resolution, kallsyms layout, sysfs setup, version checks, decompression, tree lookup, strict RWX, stats, duplicate autoload suppression, taint tracking, and kmemleak hooks.

## Control Flow
The header has no runtime control flow, but it defines the contracts that `main.c` calls during load and unload. Most optional subsystems expose real functions under their Kconfig guard and no-op or permissive inline stubs otherwise.

## State And Persistence
`struct load_info` is the central transient load transaction state: ELF header, section headers, section strings, string table, module pointer, indices for special sections, decompression pages, signature result, and kallsyms offsets. Global state declarations include `module_mutex`, `modules`, linker-provided symbol tables, and `mod_tree`.

## Dependencies And Integration Points
Depends on ELF, modules, mutex/RCU, memory management, Kconfig feature symbols, and linker-defined ksymtab/kcrctab ranges. It links all module subfiles to the loader core without exporting these interfaces publicly.

## Risks And Edge Cases
The `sh_entsize` encoding reserves high bits for memory type and lower bits for offsets; overflow or mismatched masks corrupt layout. Stub behavior must match feature-off expectations. Changes to `load_info.index` or `struct kernel_symbol` must stay synchronized with modpost, linker output, and versioning code.

## Test Signals
Compile coverage across feature permutations is essential. Runtime signals include successful module load paths using signatures, compression, kallsyms, sysfs, modversions, and unload tracking, plus absence of unresolved references when options are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kallsyms.c -->
# sources/distributed-fs/ceph-client/kernel/module/kallsyms.c

## Purpose
Implements kallsyms support for modules: symbol table layout, runtime symbol metadata population, build-id extraction, address-to-symbol lookup, symbol-name lookup, and iteration over module symbols.

## Important APIs, Types, And Functions
Important functions are `layout_symtab`, `add_kallsyms`, `init_build_id`, `module_address_lookup`, `lookup_module_symbol_name`, `module_get_kallsym`, `module_kallsyms_lookup_name`, `find_kallsyms_symbol_value`, and `module_kallsyms_on_each_symbol`. Internal helpers include `lookup_exported_symbol`, `is_exported`, `elf_type`, `is_core_symbol`, `find_kallsyms_symbol`, and `__find_kallsyms_symbol_value`.

## Control Flow
During layout, the full ELF symtab and strtab are kept in init memory while a filtered core kallsyms copy is appended to module data. `add_kallsyms` builds typetabs, copies retained core symbols and names, and publishes `mod->kallsyms` to init-time data with RCU. After module init, `main.c` switches to `mod->core_kallsyms`. Lookup paths use RCU to find the containing module and scan its kallsyms for nearest symbols or exact names.

## State And Persistence
Symbol metadata persists in module init memory until init is freed, then in `mod->core_kallsyms` for the module lifetime. Livepatch modules keep all symbols. Optional build IDs are copied into `mod->build_id`.

## Dependencies And Integration Points
Depends on `CONFIG_KALLSYMS`, build-id parsing, exported symbol tables, module address lookup, RCU, and `/proc/kallsyms` style interfaces. It cooperates with `sysfs.c` for section address visibility.

## Risks And Edge Cases
Filtering must preserve enough symbols for diagnostics while dropping init symbols after init memory is freed. Name copying uses bounded `strscpy`; bad size accounting could truncate or desynchronize names. Lookup is linear per module symbol table and intentionally avoids heavy locking in oops paths.

## Test Signals
Signals include correct `/proc/kallsyms` module entries, stack traces resolving module symbols, build-id reporting, livepatch symbol availability, `module_kallsyms_on_each_symbol` iteration, and safe behavior while modules load/unload under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kdb.c -->
# sources/distributed-fs/ceph-client/kernel/module/kdb.c

## Purpose
Adds module listing support to KDB through an `lsmod`-style command implementation.

## Important APIs, Types, And Functions
Defines `kdb_lsmod(int argc, const char **argv)`. It reads global `modules`, `module_refcount`, module memory ranges, and `struct module_use` lists when unloading support is enabled.

## Control Flow
The command rejects arguments, prints a header, then iterates the module list and skips `MODULE_STATE_UNFORMED` entries. For each visible module, it prints per-memory-type sizes, module struct address, refcount if available, state label, memory bases, and the modules it uses.

## State And Persistence
No state is stored. It produces debugger output from live module list state.

## Dependencies And Integration Points
Depends on KDB, module internals, optional `CONFIG_MODULE_UNLOAD`, and the global module list. It is built only when `CONFIG_KGDB_KDB` selects `kdb.o`.

## Risks And Edge Cases
KDB may run in fragile contexts, so traversal assumes debugger usage and avoids complex synchronization. Pointer output is sensitive and should follow kernel pointer formatting policy. Unformed modules must remain hidden to avoid partially initialized data.

## Test Signals
Entering KDB and running `lsmod` should show live/loading/unloading modules with coherent sizes and use lists. Build coverage with and without module unload is needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kmod.c -->
# sources/distributed-fs/ceph-client/kernel/module/kmod.c

## Purpose
Implements the in-kernel autoload path that calls userspace `modprobe` for `request_module()` consumers.

## Important APIs, Types, And Functions
Exports `__request_module`. Internal helpers are `call_modprobe` and `free_modprobe_argv`. Global state includes `modprobe_path`, the `kmod_concurrent_max` semaphore, `MAX_KMOD_CONCURRENT`, and `MAX_KMOD_ALL_BUSY_TIMEOUT`.

## Control Flow
`__request_module` rejects synchronous requests from async context with a warning, checks that `modprobe_path` is enabled, formats the module name, applies LSM `security_kernel_module_request`, and acquires a bounded concurrency semaphore. It emits a tracepoint, consults duplicate suppression, and if needed calls `call_modprobe`, which builds argv/envp and runs `call_usermodehelper_exec` with either wait-for-process or wait-for-exec behavior. Completion is announced to duplicate waiters.

## State And Persistence
The modprobe path is a runtime sysctl-backed buffer declared here and initialized from `CONFIG_MODPROBE_PATH`. The concurrency semaphore limits live helpers. No durable module state is modified directly.

## Dependencies And Integration Points
Depends on usermode helper infrastructure, LSM hooks, tracepoints, duplicate suppression in `dups.c`, async subsystem rules, and sysctl exposure from `main.c`.

## Risks And Edge Cases
Recursive module dependencies can exhaust all helper slots; the timeout fails new requests. Synchronous autoload from async workers can deadlock module init and is warned. Overlong names fail with `-ENAMETOOLONG`; disabled modprobe path fails with `-ENOENT`. Callers must verify the requested facility appeared after success.

## Test Signals
Exercise `request_module()` success/failure, disabled modprobe path, LSM denial, duplicate request suppression, nowait versus wait behavior, concurrency saturation, and tracepoint output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/kmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/livepatch.c -->
# sources/distributed-fs/ceph-client/kernel/module/livepatch.c

## Purpose
Persists enough original ELF metadata for livepatch modules after ordinary module init memory is freed.

## Important APIs, Types, And Functions
Defines `copy_module_elf` and `free_module_elf`. It fills `mod->klp_info` with a copied ELF header, section header table, section string table, and symbol table index.

## Control Flow
When `main.c` recognizes a livepatch module and kallsyms have been populated, `copy_module_elf` allocates `mod->klp_info`, duplicates the section headers and section strings from `load_info`, records `symndx`, and rewrites the symtab section address to point at `mod->core_kallsyms.symtab`. Unload cleanup calls `free_module_elf`.

## State And Persistence
The copied ELF metadata persists for the lifetime of the livepatch module. It is independent of the temporary load buffer and init-memory kallsyms that will be freed.

## Dependencies And Integration Points
Depends on `CONFIG_LIVEPATCH`, `struct klp_modinfo`, module kallsyms layout, and `main.c` livepatch checks. It allows the livepatch subsystem to inspect sections and symbols after load.

## Risks And Edge Cases
Allocation failure must unwind partially copied metadata. The symtab address rewrite assumes livepatch modules keep a complete core kallsyms symtab; if kallsyms filtering changed, livepatch resolution could break.

## Test Signals
Load and unload livepatch modules, verify symbol/section resolution after init memory is freed, and run failure-injection on each allocation path to confirm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/livepatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/main.c -->
# sources/distributed-fs/ceph-client/kernel/module/main.c

## Purpose
Implements the core Linux module loader and unloader. It validates ELF module images, checks signatures and version compatibility, lays out sections into executable/data module memory, resolves symbols, applies relocations, creates sysfs/proc/debug integration hooks, runs module init and exit code, handles reference counting and dependencies, and provides module address lookup.

## Important APIs, Types, And Functions
User entry points are `init_module`, `finit_module`, and `delete_module`. Exported helpers include `register_module_notifier`, `unregister_module_notifier`, `find_symbol`, `find_module`, `try_module_get`, `module_put`, `__symbol_get`, `__symbol_put`, `symbol_put_addr`, `module_refcount`, `module_flags`, `search_module_extables`, `is_module_address`, `__module_address`, `is_module_text_address`, `__module_text_address`, `module_for_each_mod`, and `print_modules`. Central load helpers include `elf_validity_cache_copy`, `early_mod_check`, `layout_and_allocate`, `add_unformed_module`, `simplify_symbols`, `apply_relocations`, `post_relocation`, `complete_formation`, `prepare_coming_module`, `load_module`, and `do_init_module`.

## Control Flow
`init_module` copies a user buffer; `finit_module` reads an fd, optionally decompresses, and deduplicates same-inode loads. Both call `load_module`. The loader checks signatures first, validates ELF headers/sections/indices/string tables, rewrites section headers, checks blacklist/vermagic/modversions, allocates final module memory, inserts an unformed unique module, allocates percpu data, discovers optional sections, resolves symbols and dependencies, applies relocations, finalizes arch/kallsyms/extables, parses parameters, sets up sysfs/livepatch/codetag state, frees the temporary image, then runs `do_init_module`. Successful init switches state to live, sends notifiers/uevents, drops the initial refcount, switches to core kallsyms, makes ro-after-init read-only, removes init memory from lookup structures, and queues init memory freeing. Unload via `delete_module` verifies capability, dependency and refcount state, marks the module going, runs exit, notifiers, livepatch/ftrace cleanup, and frees all module resources.

## State And Persistence
Global state includes `module_mutex`, RCU list `modules`, `mod_tree`, module address bounds, `module_wq`, notifier chain, sysctl-controlled `modules_disabled`, blacklist, last unloaded module diagnostics, and async init-free work. Per-module persistent state includes memory ranges, exported symbols, use links, taints, parameters, args, kallsyms, sysfs kobjects, percpu storage, and optional livepatch/codetag/debug metadata.

## Dependencies And Integration Points
Integrates with LSM/audit, ELF and arch relocation hooks, execmem and strict RWX, kallsyms, modversions, module signatures, sysfs/procfs/debugfs, ftrace, livepatch, jump labels, tracepoints, BTF, dynamic debug, CFI, exception tables, kmemleak, percpu allocator, codetags, async, kmod, and userspace module tools.

## Risks And Edge Cases
The path has many ordered invariants: signatures must be stripped before ELF validation; duplicate module detection occurs before and after final allocation; state transitions protect symbol users; RCU grace periods protect module lists and kallsyms; init memory freeing is deferred; strict RWX changes must happen after relocation and before execution. Error unwinding is high risk because each stage owns different resources. Forced loading/unloading taints the kernel and can bypass compatibility checks. Symbol namespace, GPL-only symbol, and proprietary-taint inheritance rules must be enforced consistently.

## Test Signals
Signals include successful `insmod`/`rmmod`, duplicate load races returning `-EEXIST` or `-EBUSY`, modversion mismatch rejection, forced load tainting, signature enforcement, compressed loads, bad ELF rejection, dependency refcount correctness, sysfs/proc visibility, kallsyms stack traces, strict RWX permission checks, livepatch module load, and fault-injection coverage for every cleanup label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/procfs.c -->
# sources/distributed-fs/ceph-client/kernel/module/procfs.c

## Purpose
Implements `/proc/modules`, the traditional userspace listing of loaded modules.

## Important APIs, Types, And Functions
Defines seq-file callbacks `m_start`, `m_next`, `m_stop`, and `m_show`, plus `modules_open`, `proc_modules_init`, `module_total_size`, and unload-specific `print_unload_info`.

## Control Flow
Opening `/proc/modules` creates a seq file and stores whether module text addresses may be shown based on `kallsyms_show_value`. Iteration holds `module_mutex`, walks `modules`, skips unformed modules, prints name, total size, unload/refcount/dependency fields, state, text address or hidden pointer, and taint flags.

## State And Persistence
No persistent state beyond registering the proc entry at module init. Output reflects current module list state.

## Dependencies And Integration Points
Depends on procfs, seq_file, kallsyms pointer visibility policy, `module_mutex`, module use lists, and optional `CONFIG_MODULE_UNLOAD`.

## Risks And Edge Cases
The output format is userspace ABI-like and must remain compatible with `lsmod` consumers. Pointer hiding must match kallsyms policy. Holding `module_mutex` while formatting avoids list mutation but means slow readers interact with module load/unload.

## Test Signals
Check `/proc/modules` formatting, address hiding for restricted credentials, dependency and permanent-module fields, taint display, and behavior during concurrent module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/signing.c -->
# sources/distributed-fs/ceph-client/kernel/module/signing.c

## Purpose
Performs module signature detection, PKCS#7 signature verification, and signature enforcement policy for module loads.

## Important APIs, Types, And Functions
Exports `is_module_sig_enforced` and `set_module_sig_enforced`. Internal entry points are `mod_verify_sig` and `module_sig_check`. The runtime parameter `module.sig_enforce` can only enable enforcement.

## Control Flow
`module_sig_check` detects the appended module signature marker unless the module was mangled by ignore-vermagic or ignore-modversions flags. It strips the marker, calls `mod_verify_sig`, and sets `info->sig_ok` on success. Unsigned, unsupported-crypto, or missing-key cases are rejected when enforcement is active; otherwise lockdown policy decides. Other verification errors are fatal even without enforcement.

## State And Persistence
State is `sig_enforce` and `load_info.sig_ok`. `mod_verify_sig` also shortens `info->len` so subsequent ELF parsing ignores the appended signature.

## Dependencies And Integration Points
Depends on `module_signature.c` for trailer sanity, PKCS#7 verification, secondary keyring use, LSM lockdown, module parameters, and `uapi/linux/module.h` flags. It is called at the start of `load_module`.

## Risks And Edge Cases
Forced/mangled modules must not be accepted as signed because stripped metadata invalidates the signature. Signature length arithmetic must prevent trailer underflow/overflow. Enforcement and lockdown interactions determine whether unsigned modules are rejected or merely taint later in `main.c`.

## Test Signals
Load signed, unsigned, bad-signature, missing-key, unsupported-crypto, and mangled modules under enforcing and permissive configs. Verify `info->len` truncation and `TAINT_UNSIGNED_MODULE` behavior downstream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/signing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/stats.c -->
# sources/distributed-fs/ceph-client/kernel/module/stats.c

## Purpose
Collects debug statistics about module load successes and failures, with emphasis on virtual memory wasted by failed or duplicate module loads.

## Important APIs, Types, And Functions
Exports counters and helpers declared in `internal.h`: `total_mod_size`, `total_text_size`, `invalid_kread_bytes`, `invalid_decompress_bytes`, `modcount`, `failed_kreads`, `failed_decompress`, `try_add_failed_module`, `mod_stat_bump_invalid`, and `mod_stat_bump_becoming`. It defines `read_file_mod_stats` and initializes debugfs files under `mod_debugfs_root`.

## Control Flow
The loader increments byte and count counters at specific failure stages. Duplicate failures are tracked in `dup_failed_modules` with a bitmask distinguishing becoming-stage and load-stage failures. The debugfs `stats` file builds a bounded text report with totals, averages, wasted virtual memory, and a capped duplicate-failure table.

## State And Persistence
State is in atomic counters and an RCU list of `struct mod_fail_load` entries for the lifetime of the boot. It is not durable across reboot.

## Dependencies And Integration Points
Depends on debugfs, atomic counters, `module_mutex` for duplicate list mutation, module decompression stats, and `main.c` failure labels. It is enabled by `CONFIG_MODULE_STATS`.

## Risks And Edge Cases
Counters must match the failure stage to avoid misleading memory pressure conclusions. The debugfs preamble has explicit size expectations and WARNs on overflow. Duplicate list allocation failure is non-fatal but loses diagnostic data.

## Test Signals
Fault-inject kernel reads, decompression, duplicate loads before and after allocation, and module init failures. Verify debugfs counters, average calculations, duplicate reason masks, and no sleeps/deadlocks from atomic accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/strict_rwx.c -->
# sources/distributed-fs/ceph-client/kernel/module/strict_rwx.c

## Purpose
Applies strict memory permissions to module allocations and rejects invalid writable-executable module sections.

## Important APIs, Types, And Functions
Exports `module_enable_text_rox`, `module_enable_rodata_ro`, `module_enable_rodata_ro_after_init`, `module_enable_data_nx`, `module_enforce_rwx_sections`, and `module_mark_ro_after_init`. The local helper `module_set_memory` wraps permission changes for one module memory type.

## Control Flow
Before layout, `module_enforce_rwx_sections` rejects any ELF section with both write and execute flags under `CONFIG_STRICT_MODULE_RWX`. `module_mark_ro_after_init` tags known sections such as `.data..ro_after_init`, `__jump_table`, and optionally `.static_call_sites`. After relocation, `complete_formation` makes rodata read-only, data non-executable, and text executable/read-only. After init, ro-after-init memory becomes read-only.

## State And Persistence
It updates page table permissions for `mod->mem[]` regions and section flags used by layout. Permissions persist until the module is unloaded or memory is restored/freed.

## Dependencies And Integration Points
Depends on vmalloc/set_memory APIs, execmem ROX restoration, `rodata_enabled`, module memory type iteration, and loader sequencing in `main.c`.

## Risks And Edge Cases
Permission changes are architecture-sensitive and can fail. Text memory may already be ROX from execmem and must be restored rather than blindly changed. Section tagging must happen before layout or ro-after-init data lands in the wrong memory range. W+X rejection is a security boundary.

## Test Signals
Load normal modules under strict RWX, inject W+X sections and expect `-ENOEXEC`, verify text is executable but not writable, data is NX, rodata and ro-after-init become read-only, and error paths restore/free ROX memory correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/strict_rwx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/sysfs.c -->
# sources/distributed-fs/ceph-client/kernel/module/sysfs.c

## Purpose
Creates and tears down `/sys/module/<name>` state for loaded modules, including module parameters, modinfo attributes, holder links, section addresses, and note sections.

## Important APIs, Types, And Functions
Exports `mod_sysfs_setup`, `mod_sysfs_teardown`, and `init_param_lock`. Internal helpers include `add_sect_attrs`, `remove_sect_attrs`, `add_notes_attrs`, `remove_notes_attrs`, `add_usage_links`, `del_usage_links`, `module_add_modinfo_attrs`, `module_remove_modinfo_attrs`, `mod_sysfs_init`, `mod_sysfs_fini`, and `mod_kobject_put`.

## Control Flow
Setup first initializes the module kobject under `module_kset`, rejects duplicate kobjects, creates `holders`, registers parameters, adds modinfo attributes, creates holder symlinks to dependency targets, then adds section and note attribute groups. Each failure label unwinds the already-created pieces in reverse. Teardown removes links, modinfo, parameters, driver/holder kobjects, note/section groups, and the module kobject.

## State And Persistence
State persists as sysfs kobjects, attributes, binary attributes, symlinks, `mod->sect_attrs`, `mod->notes_attrs`, `mod->modinfo_attrs`, `mod->holders_dir`, and parameter locks for the module lifetime.

## Dependencies And Integration Points
Depends on sysfs, module ktypes, kallsyms for section visibility and pointer hiding, module parameter sysfs helpers, `module_mutex`, and module use lists.

## Risks And Edge Cases
Section and note attributes share section names, so setup ordering matters. Pointer exposure must respect `kallsyms_show_value`. Kobject lifetime is synchronized through a completion in `mod_kobject_put`. Partial setup failure must remove exactly the initialized resources.

## Test Signals
Load modules with parameters, dependencies, note sections, and kallsyms enabled. Verify `/sys/module` attributes, holder links, pointer visibility restrictions, and clean teardown under load failure and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/tracking.c -->
# sources/distributed-fs/ceph-client/kernel/module/tracking.c

## Purpose
Tracks unloaded modules that had taint flags, preserving diagnostic evidence after the module is gone.

## Important APIs, Types, And Functions
Exports `try_add_tainted_module` and `print_unloaded_tainted_modules`. Debugfs support defines seq operations and an `unloaded_tainted` file under `mod_debugfs_root`. State entries use `struct mod_unload_taint`.

## Control Flow
During module free, `main.c` calls `try_add_tainted_module`. The helper ignores untainted modules, increments an existing entry if the same module name and taints were already seen, or allocates a new list entry. `print_unloaded_tainted_modules` appends the tracked list to module diagnostics. Debugfs seq iteration exposes the same list.

## State And Persistence
State is an in-memory RCU list `unloaded_tainted_modules` containing module name, taint mask, and count. It persists until reboot.

## Dependencies And Integration Points
Depends on module taint formatting from `main.c`, `module_mutex` for mutation, RCU list traversal, debugfs, and seq_file.

## Risks And Edge Cases
Allocation failure loses diagnostics but should not block unload. Matching requires overlapping taint bits for the same name; changed taint combinations may create separate entries. Debugfs iteration must use RCU.

## Test Signals
Unload tainted modules multiple times, inspect oops/module print output and debugfs `unloaded_tainted`, and verify untainted unloads do not create entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/tree_lookup.c -->
# sources/distributed-fs/ceph-client/kernel/module/tree_lookup.c

## Purpose
Provides fast module address lookup using a latched red-black tree, optimized for perf, tracing, CFI, and stack unwinding paths that may query module addresses frequently or from restrictive contexts.

## Important APIs, Types, And Functions
Exports `mod_tree_insert`, `mod_tree_remove_init`, `mod_tree_remove`, and `mod_find`. Internal latch tree callbacks are `mod_tree_less` and `mod_tree_comp`; helpers `__mod_tree_val`, `__mod_tree_size`, `__mod_tree_insert`, and `__mod_tree_remove` operate on `struct module_memory` tree nodes.

## Control Flow
When a module enters the global list, every non-empty memory type is inserted into `mod_tree`. After successful init, init memory ranges are removed by `mod_tree_remove_init`. On unload or failed load cleanup, all remaining memory ranges are removed. Lookups call `latch_tree_find` with an address and return the owning module.

## State And Persistence
State lives in `mod_tree.root` and each `mod->mem[type].mtn` node. It is valid while the module memory range is registered and protected by module loader sequencing plus RCU lookup rules.

## Dependencies And Integration Points
Depends on `CONFIG_MODULES_TREE_LOOKUP`, `linux/rbtree_latch.h`, `module_mutex` serialization for updates, and `main.c` address bounds checks in `__module_address`.

## Risks And Edge Cases
Insert/remove operations must exactly mirror module memory lifetime. Removing init ranges after they are queued for freeing prevents stale lookup hits. Overlapping or zero-sized ranges would corrupt lookup semantics; zero sizes are skipped.

## Test Signals
Stress stack unwinding and module load/unload with perf/tracing/CFI enabled, verify `__module_address` and `__module_text_address` results, and check no stale init-memory matches after init cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/tree_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/version.c -->
# sources/distributed-fs/ceph-client/kernel/module/version.c

## Purpose
Implements module symbol version compatibility checks for `CONFIG_MODVERSIONS`, including traditional `__versions` records and extended CRC/name sections.

## Important APIs, Types, And Functions
Defines `check_version`, `check_modstruct_version`, `same_magic`, `modversion_ext_start`, `modversion_ext_advance`, and exported marker function `module_layout`.

## Control Flow
For each resolved symbol, `check_version` compares the exporting symbol CRC against either extended version entries or traditional `struct modversion_info` records. Missing CRCs from exporters are allowed; missing versions in the importing module can force-load only when configured. `check_modstruct_version` specifically validates `module_layout`. `same_magic` ignores the leading kernel version when CRCs are present.

## State And Persistence
No persistent state is owned here. It reads version sections cached in `load_info.index` and influences whether the module load continues or taints through forced loading.

## Dependencies And Integration Points
Depends on `find_symbol`, module force-load policy, ksymtab CRCs, modpost-generated version sections, and vermagic checks in `main.c`.

## Risks And Edge Cases
Extended version CRC and name sections must remain paired and aligned by `main.c` validation. Missing symbol versions are tolerated for broken toolchains, but mismatched CRCs reject the module. Forcing versionless modules weakens ABI safety and taints the kernel.

## Test Signals
Load modules with matching, mismatched, missing, and extended modversions; verify `module_layout` mismatch rejection, `--force` behavior, warnings for missing entries, and vermagic comparison when CRCs are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module_signature.c -->
# sources/distributed-fs/ceph-client/kernel/module_signature.c

## Purpose
Validates the fixed trailer metadata of an appended module signature before PKCS#7 verification is attempted.

## Important APIs, Types, And Functions
Defines `mod_check_sig(const struct module_signature *ms, size_t file_len, const char *name)`.

## Control Flow
The helper rejects signatures whose big-endian `sig_len` would consume the whole file, rejects non-PKCS#7 signature types, and rejects any non-zero legacy algorithm/hash/signer/key-id/padding fields. A clean trailer returns 0 so higher-level code can verify the detached PKCS#7 blob.

## State And Persistence
No state is stored. The function only validates a caller-provided `struct module_signature`.

## Dependencies And Integration Points
Depends on `linux/module_signature.h`, byte-order conversion, printk, and callers in `kernel/module/signing.c`.

## Risks And Edge Cases
Trailer arithmetic prevents out-of-bounds signature extraction; mistakes here can cause malformed modules to reach PKCS#7 parsing. The expectation that algo/hash/signer/key-id fields are zero is part of the current module-signing ABI.

## Test Signals
Feed valid trailers, overlong `sig_len`, wrong `id_type`, and non-zero metadata fields. `module_sig_check` should map these to the expected load failures or unsupported-package errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/module_signature.c -->
