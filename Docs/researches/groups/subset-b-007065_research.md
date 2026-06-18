# subset-b-007065 GlusterFS libglusterfs research

This grouped report covers the requested GlusterFS libglusterfs headers and graph source files. Each section is source-tree aligned and is intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lkowner.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lkowner.h

Purpose: `lkowner.h` provides inline helpers for `gf_lkowner_t`, the lock-owner token carried on call stacks and syncop contexts for POSIX/Gluster lock identity. It converts owners to printable hex, initializes owners from pointer/`uint64_t` values, compares owners, detects null owners, and copies owner bytes.

Important APIs and types: `lkowner_unparse()` formats `lkowner->data`; `set_lk_owner_from_ptr()` and `set_lk_owner_from_uint64()` encode little-endian bytes; `is_same_lkowner()` compares length and data with `memcmp`; `is_lk_owner_null()` treats NULL, zero length, or all-zero bytes as no owner; `lk_owner_copy()` copies length and payload. The actual `gf_lkowner_t` type is defined by broader Gluster headers.

Control flow and state: all behavior is inline and caller-owned. No global state or persistence exists. Data is written directly into the caller-provided `gf_lkowner_t` or output buffer.

Dependencies and integration: used by `stack.h` and `syncop.h` to preserve lock ownership across copied call stacks and synthetic sync frames. It relies on standard memory/string routines and on the lock-owner length not exceeding the backing array.

Risks: `lkowner_unparse()` has manual buffer accounting and uses `sprintf` for the non-fast path, so boundary behavior should be tested with small buffers and long owners. Copy/init helpers do not validate destination capacity. Pointer encoding is architecture-size dependent.

Test signals: unit tests should cover same/different owners, null/all-zero owners, 32-bit versus 64-bit length assumptions where applicable, formatting with exactly 16, 17, and truncated buffer sizes, and preservation of owners through `copy_frame()`/syncop-created frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lkowner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/locking.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/locking.h

Purpose: `locking.h` centralizes GlusterFS mutex naming and Darwin spinlock compatibility. It gives the rest of libglusterfs a stable `gf_lock_t` alias and `LOCK_*` macros over pthread mutex calls.

Important APIs and types: `gf_lock_t` is `pthread_mutex_t`. `LOCK_INIT`, `LOCK`, `TRY_LOCK`, `UNLOCK`, and `LOCK_DESTROY` map directly to pthread calls. On Darwin, `pthread_spinlock_t` and spinlock operations are mapped to `OSSpinLock` primitives.

Control flow and state: the header has no runtime control flow besides macro expansion. All state is owned by the lock objects embedded in structures such as call stacks, rbthash buckets, memory pools, rotating buffers, and token buckets.

Dependencies and integration: every subsystem that uses `gf_lock_t` depends on this stable wrapper. `mem-pool.h`, `rbthash.h`, `rot-buffs.h`, and `stack.h` include it either directly or transitively.

Risks: the macros expose raw pthread return values only if callers inspect them; many call sites ignore failures. The Darwin `OSSpinLock` mapping is legacy and has priority-inversion concerns on modern Darwin systems. There is no debug ownership tracking at this layer.

Test signals: concurrency tests should focus on higher-level users. Portability builds should compile on Linux and Darwin paths. Static analysis should flag unbalanced `LOCK`/`UNLOCK` and destroyed-while-held patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/locking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/logging.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/logging.h

Purpose: `logging.h` declares GlusterFS logging levels, output formats, logger backends, runtime log handle state, suppression buffers, and the public macros used throughout translators and libglusterfs.

Important APIs and types: `gf_loglevel_t` spans none/emerg/alert/critical/error/warning/notice/info/debug/trace. `gf_log_handle_t` stores mutexes, current levels, syslog toggles, filenames, `FILE *` handles, logger/format choices, suppression LRU state, flush timer, and rotate flags. `log_buf_t` records suppressed message metadata. Core functions include `gf_log_globals_init`, `gf_log_init`, `gf_log_cleanup`, `_gf_msg`, `_gf_log`, `gf_log_set_loglevel`, `gf_log_flush`, command-log helpers, suppression tuning, and structured `_gf_smsg`.

Control flow and state: macros such as `gf_msg`, `gf_msg_debug`, `gf_msg_trace`, `gf_log`, `GF_DEBUG`, and `GF_LOG_*` capture file/function/line and delegate to implementation functions. State is process/global-context scoped through `glusterfs_ctx_t` and, for structured macros, `global_ctx`.

Dependencies and integration: logging is foundational for graph parsing, option validation, memory allocation failures, runner operations, and graph lifecycle diagnostics. It depends on list handling, timers, pthread mutexes, and message-id headers.

Risks: macros evaluate variadic arguments at call sites and can hide control flow. Structured `GF_LOG*` macros require `global_ctx` and generated message definitions. Suppression, rotation, and flush timers are shared mutable state and need careful shutdown ordering.

Test signals: validate log-level filtering, message-id formatting, syslog enable/disable, rotate flags, suppression buffer limits, no-allocation `gf_msg_nomem` paths, and structured log macro builds with generated message headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lvm-defaults.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lvm-defaults.h

Purpose: `lvm-defaults.h` defines hard-coded paths to LVM command-line tools used by GlusterFS components that manage or inspect logical volumes.

Important APIs and types: it exports only macros: `LVM_RESIZE`, `LVM_CREATE`, `LVM_CONVERT`, `LVM_REMOVE`, and `LVS`, all pointing under `/sbin`.

Control flow and state: no runtime state or logic. Callers embed these strings when invoking external commands, usually through the runner/syscall stack.

Dependencies and integration: integrates with storage-management code outside this subset. It is related to `run.h` because these command paths are ultimately executed as child processes.

Risks: hard-coded `/sbin` paths can be wrong on distributions using `/usr/sbin`, merged `/usr`, containers, or custom LVM installations. These constants should not be assumed portable without configure-time checks or override paths.

Test signals: packaging tests should assert that referenced paths exist or are configured for the target platform. Any LVM workflow tests should verify command-not-found handling and user-facing diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lvm-defaults.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-pool.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-pool.h

Purpose: `mem-pool.h` defines GlusterFS allocation wrappers, memory-accounting headers, debug sentinels, string/memory duplication helpers, and the optional per-thread fixed-size object pool API.

Important APIs and types: `struct mem_acct` and `struct mem_acct_rec` track allocation counts and, under `DEBUG`, sizes and object lists. `struct mem_header` stores accounting pointer, allocation size, type, and magic. Public allocators are `__gf_malloc`, `__gf_calloc`, `__gf_realloc`, `__gf_free`, `GF_MALLOC`, `GF_CALLOC`, `GF_REALLOC`, and `GF_FREE`. Pool APIs include `mem_pool_new_fn`, `mem_get_malloc`, `mem_get_calloc`, `mem_put_pool`, `mem_pool_destroy`, `mem_pools_init`, and `mem_pools_fini`.

Control flow and state: default allocation wrappers log no-memory alerts. With mempool enabled, `struct mem_pool` links to `glusterfs_ctx_t->mempool_list`, tracks active allocations, and uses per-thread hot/cold lists guarded by spinlocks. With `GF_DISABLE_MEMPOOL`, `mem_pool` becomes a size wrapper and `mem_get`/`mem_put` fall back to normal GF allocation.

Dependencies and integration: nearly every file in this subset uses these macros for source-type accounting. `stack.h` allocates call frames/stacks from pools; graph and parser code allocate translators and lists with common memory types.

Risks: use-after-free detection depends on magic/header discipline. `FREE` poisons raw pointers but `GF_FREE` ownership is implementation-defined. Pool object headers reduce available size and require correct size-class selection. Thread-local pool destruction and sweeper behavior are concurrency-sensitive.

Test signals: allocation accounting tests, debug magic corruption tests, mempool enabled/disabled builds, thread exit destructor behavior, and leak/statedump validation are high-value. Fuzzing should include zero-size and realloc failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-types.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-types.h

Purpose: `mem-types.h` enumerates common allocation type IDs used by the GlusterFS memory accounting system.

Important APIs and types: `enum gf_common_mem_types_` includes type IDs for core objects such as event pools, fd/inode tables, translators, volume options, timers, iobufs, rpc structures, graph objects, trie nodes, runner argv/log buffers, statedump buffers, store handles, syncop tasks/envs, throttle buckets, volfiles, and generic integer/pointer/data pairs. `gf_common_mt_end` terminates the enum.

Control flow and state: no logic. The enum values are persisted only indirectly in allocation accounting records and debug diagnostics.

Dependencies and integration: `mem-pool.h` stringizes these constants in `GF_MALLOC`/`GF_CALLOC` calls, and many source files choose a type ID to make statedumps and leak diagnosis meaningful.

Risks: changing enum order can confuse any tooling that assumes numeric stability in dumps. New subsystems need distinct entries to avoid misleading accounting. Overusing generic entries reduces diagnostic value.

Test signals: build coverage should catch missing enum names. Runtime memory-accounting/statedump tests should assert allocations are attributed to expected type strings for translators, graph objects, sync tasks, and parser allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/monitoring.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/monitoring.h

Purpose: `monitoring.h` declares the small metrics-export entry point for GlusterFS runtime monitoring.

Important APIs and types: `GLUSTER_METRICS_DIR` is `/var/run/gluster/metrics`. `gf_monitor_metrics(glusterfs_ctx_t *ctx)` returns a `char *`, likely a generated metrics payload or path depending on implementation.

Control flow and state: no inline logic. Runtime behavior is deferred to the implementation and depends on `glusterfs_ctx_t`.

Dependencies and integration: it includes `glusterfs.h` for context types and integrates with translator `dump_metrics` hooks declared in `xlator.h`.

Risks: `/var/run` path assumptions can fail under containers, non-root services, or changed runtime directories. The returned `char *` ownership contract is not documented here, so callers must consult the implementation.

Test signals: monitoring tests should cover missing metrics directory, permission failures, empty graphs, translators with and without `dump_metrics`, and memory ownership of the returned string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/monitoring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/options.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/options.h

Purpose: `options.h` defines translator volume option metadata, validation categories, and macros that initialize/reconfigure typed option values from dictionaries.

Important APIs and types: `volume_option_type_t` covers string, integer, size, percent, boolean, xlator, path, time, double, address/list, priority, size-list, and auth address options. `volume_option_t` stores aliases, type, validation range, allowed values, defaults, description, op-version/deprecation arrays, flags, tags, setkey, level, and category. APIs include `xlator_options_validate`, `xlator_option_validate`, address-list validation, option lookup, and generated `xlator_option_init_*`/`xlator_option_reconf_*` functions.

Control flow and state: `DEFINE_INIT_OPT` fetches metadata from the translator, chooses explicitly set value over default, converts with a provided converter, then validates. `DEFINE_RECONF_OPT` repeats this flow for reconfiguration using `dict_get_strn`. `GF_OPTION_INIT` and `GF_OPTION_RECONF` jump to caller error labels on failure.

Dependencies and integration: depends on `xlator.h`, dictionaries, logging, and message IDs. Graph activation calls option validation before translator init. GD2 compatibility comments make `volume_option_t` layout ABI-sensitive.

Risks: macros hide gotos and require converter signatures to match. Struct member ordering is externally constrained. Missing defaults produce zero values without validation. Reconfiguration uses string length from `strlen(key)` and relies on stable dictionary ownership.

Test signals: validate each option type, min/max/range flags, alias matching, default precedence, bad conversion, op-version/deprecation handling, unknown option logging, and GD2 layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/parse-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/parse-utils.h

Purpose: `parse-utils.h` exposes a regex-backed incremental parser helper for repeatedly extracting matches from a complete string.

Important APIs and types: `struct parser` owns a compiled `regex_t`, one `regmatch_t`, the complete string under parse, the regex text, and a temporary offset string. `parser_init`, `parser_set_string`, `parser_unset_string`, `parser_deinit`, and `parser_get_next_match` form the lifecycle.

Control flow and state: callers create a parser for a regex, set the target string, repeatedly request the next match, unset the string when done, and finally deinit. State is per-parser and not global.

Dependencies and integration: includes POSIX `<regex.h>` and uses Gluster allocation/logging in the implementation. It is useful for parsing option or command output strings without open-coding regex loops.

Risks: ownership of returned match strings is not documented in the header. Regex compilation and match offsets must handle empty matches carefully to avoid infinite loops. Parser reuse requires `parser_unset_string` discipline.

Test signals: tests should cover invalid regex, NULL/empty strings, no match, repeated matches, escaped patterns, zero-length matches, and cleanup under allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/parse-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/quota-common-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/quota-common-utils.h

Purpose: `quota-common-utils.h` defines packed quota limit/metadata formats and helpers for quota dictionaries and quota configuration files.

Important APIs and types: `GF_QUOTA_CONF_VERSION`, `QUOTA_CONF_HEADER`, and `QUOTA_CONF_HEADER_1_1` identify supported conf formats. `gf_quota_conf_type_t` distinguishes usage and object quota records. `quota_limits_t` stores hard/soft limits; `quota_meta_t` stores size, file count, and directory count. APIs convert `data_t` to metadata, get/set metadata in dictionaries, and read/skip quota conf headers, versions, and GFIDs.

Control flow and state: no inline logic. Functions operate on caller-provided dictionaries, buffers, file descriptors, and metadata structs. Persistent behavior centers on the quota conf file wire format.

Dependencies and integration: includes `iatt.h` for inode type information and depends on dict/data APIs. Translators and glusterd quota logic use these helpers to share a stable binary metadata representation.

Risks: packed structs are ABI/wire-format sensitive and need endian/alignment awareness. Version parsing uses floats, which can be fragile. File descriptor reads must handle short reads and corrupt headers.

Test signals: quota tests should cover v1.1/v1.2 headers, usage versus object entries, dictionary round trips for file and directory IA types, null metadata detection, malformed/truncated files, and cross-architecture packed-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/quota-common-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rbthash.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rbthash.h

Purpose: `rbthash.h` defines a hash table whose buckets are red-black trees, providing keyed lookup/removal/replacement with per-bucket locking.

Important APIs and types: `rbthash_entry_t` holds data, key, key length, key hash, and a list node. `rbthash_bucket` holds an `rb_table *` and `gf_lock_t`. `rbthash_table_t` stores size, bucket count, entry mempool, table lock, buckets, hash and destroy callbacks, pool ownership, and list linkage. Public APIs initialize, insert, get, remove, replace, destroy, and traverse.

Control flow and state: callers provide a hash function and optional data destructor. The table owns bucket structures and possibly an entry pool. Inserts place entries into bucket RB trees keyed by hash/key. Removal returns data ownership to the caller; destroy uses the destroy callback.

Dependencies and integration: depends on Gluster context, list, locking, and memory pools. Useful for caches where hash distribution plus ordered bucket search is desired.

Risks: caller-provided hash/key equality semantics must match implementation expectations. Concurrent traversal versus mutation requires lock discipline in implementation. Data ownership differs between remove/replace/destroy paths and can cause leaks or double frees.

Test signals: tests should include collisions, duplicate insert semantics, replacement destruction behavior, removal ownership, traversal under many buckets, custom entry pool ownership, and concurrent lookup/insert/remove stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rbthash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/refcount.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/refcount.h

Purpose: `refcount.h` provides a small embedded atomic reference-counting helper with a release callback and convenience macros for structures that include `GF_REF_DECL`.

Important APIs and types: `gf_ref_t` contains an atomic `cnt`, a `gf_ref_release_t`, and release data. `_gf_ref_init` initializes a refcount, `_gf_ref_get` attempts to acquire a reference, and `_gf_ref_put` drops one and invokes release when the count reaches zero. Macros `GF_REF_INIT`, `GF_REF_GET`, and `GF_REF_PUT` operate on embedded `_ref` members.

Control flow and state: state is per-object. The release callback receives the owning object pointer when used through the macros. `_gf_ref_get` returns NULL/0 when a reference cannot be taken, protecting against resurrecting a dead object if implemented with compare-and-swap semantics.

Dependencies and integration: depends on Gluster atomics. It is a common primitive for async graph, inode, fd, rpc, or transport objects that outlive a single stack frame.

Risks: finalizer reentrancy and object ownership are outside the header. Callers must avoid using objects after `GF_REF_PUT` returns zero. Missing initial reference or unbalanced get/put causes leaks or premature destruction.

Test signals: concurrent get/put race tests, release-called-once assertions, get-after-zero behavior, and sanitizer coverage around finalizer paths are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/revision.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/revision.h

Purpose: `revision.h` embeds the repository revision string used in startup diagnostics or build identity output.

Important APIs and types: it defines `GLUSTERFS_REPOSITORY_REVISION` as `git://git.gluster.org/glusterfs.git`.

Control flow and state: no control flow or mutable state.

Dependencies and integration: graph startup diagnostic code references this macro in disabled dump code. Other build/version reporting paths may include it.

Risks: the value is static and does not identify the actual checked-out commit. If used as provenance, it can be misleading for downstream forks or mirrored repositories.

Test signals: build/version tests should verify whether generated revision metadata supersedes this constant. Packaging should avoid treating it as a commit hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/revision.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rot-buffs.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rot-buffs.h

Purpose: `rot-buffs.h` defines rotating buffer lists for producer/consumer handoff of `iovec` entries with writer completion tracking.

Important APIs and types: `rbuf_iovec_t` wraps an `iovec` with list linkage. `rbuf_list_t` has completion and buffer locks, a condition variable, pending/completed counters, current vector pointer, used/total counts, sequence range, and list linkage. `rbuf_t` owns a lock, current list, and freelist. APIs initialize/destroy buffers, reserve write space, mark writes complete, get consumable buffers, and wait for completion.

Control flow and state: producers reserve memory, write, and call `rbuf_write_complete`. Consumers obtain a buffer list and can wait until all pending writers complete. Sequence assignment callbacks run during buffer switch under the main buffer lock.

Dependencies and integration: depends on list and locking APIs plus pthread conditions. Likely used where high-throughput event/history/log buffering needs batched iovec handoff.

Risks: correctness depends on pending/completed accounting and lock ordering between `c_lock`, `b_lock`, and `rbuf_t.lock`. Iterator macros copy the list head by value, so mutation during iteration would be unsafe. Starvation is represented by `RBUF_WOULD_STARVE`.

Test signals: multi-producer/multi-consumer tests should verify no lost entries, wait completion, sequence ranges, starvation behavior, and destruction after pending writers complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/rot-buffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/run.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/run.h

Purpose: `run.h` declares the `runner_t` helper for constructing and executing child processes with argument accumulation, logging, and stdio redirection.

Important APIs and types: `runner_t` stores argv, argv length, deferred error, child pid, child file descriptors, and child `FILE *` streams. APIs include `runinit`, `runner_add_arg`, `runner_add_args`, `runner_argprintf`, `runner_log`, `runner_redir`, `runner_start`, `runner_end`, reusable variants, `runner_run`, `runner_run_nowait`, and `runcmd`. `RUN_PIPE` requests a parent-readable pipe.

Control flow and state: callers initialize, add arguments, optionally configure redirections, start the child, interact with child pipes, and end/reap/free. Error handling is deferred during argument construction and surfaced during start/run.

Dependencies and integration: uses logging types and is a safer abstraction for LVM/tool invocations than ad hoc `system()`. It interacts with `syscall.h` wrappers and command path headers such as `lvm-defaults.h`.

Risks: vararg argument sequences must be NULL-terminated. Redirection ownership closes target fds in `runner_end`, so callers must dup fds they need. `runner_run_nowait` assumes success and can hide exec failures. Child-pipe consumers must avoid deadlocks.

Test signals: spawn success/failure, argument quoting/no-shell behavior, pipe redirection, fd ownership, reusable runner paths, nowait behavior, and signal/waitpid status decoding should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/run.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/stack.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/stack.h

Purpose: `stack.h` implements GlusterFS's async call-stack model: frames carry translator context, callback addresses, credentials, lock owner, latency timing, and error state while fops wind down and unwind up translator graphs.

Important APIs and types: `call_pool_t` owns all frames, counters, locks, and frame/stack mempools. `call_frame_t` stores root stack, parent, local data, cookie, `THIS`, return callback, fop index, completion, and trace names. `call_stack_t` stores credentials, pid, groups, client, operation, flags, timestamps, namespace info, and `gf_lkowner_t`. Key macros/functions include `STACK_WIND`, `STACK_WIND_COOKIE`, `STACK_WIND_TAIL`, `STACK_UNWIND_STRICT`, `FRAME_DESTROY`, `STACK_DESTROY`, `STACK_RESET`, `copy_frame`, `create_frame`, and group helpers.

Control flow and state: `STACK_WIND_COMMON` allocates a child frame, links it into the stack, switches global/thread `THIS`, records fop stats/latency, and calls the next translator fop. `STACK_UNWIND_STRICT` restores parent context, updates root error/err_xl, records callback stats, and invokes the typed callback. Destroy/reset paths remove frames under call-pool locks and free locals.

Dependencies and integration: tightly coupled to `xlator.h` fop table layout, `timespec.h`, memory pools, lock owner helpers, dict/client types, and logging. Syncop copies frames to present blocking APIs over this async machinery.

Risks: fop index calculation depends on exact `struct xlator_fops` order. A missing unwind leaks frames. `copy_frame()` must preserve credentials/groups/lkowner without sharing mutable arrays incorrectly. `FRAME_DESTROY` assumes frame-local allocations come from mempools. `THIS` switching is macro-heavy and fragile.

Test signals: translator fop wind/unwind tests, latency/stat counter assertions, error propagation through stacked translators, group allocation over/under `SMALL_GROUP_COUNT`, copied-frame credential preservation, and leak detection for failure paths are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/statedump.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/statedump.h

Purpose: `statedump.h` declares the process/translator diagnostic dump interface used to emit memory, iobuf, callpool, inode, fd, history, latency, and private translator state.

Important APIs and types: `gf_dump_xl_options_t` controls per-translator private/inode/fd/context/history dumps. `gf_dump_options_t` controls global dump classes and output path. `gf_proc_dump_build_key` builds hierarchical keys into a fixed 4096-byte buffer. APIs initialize/fini/cleanup dumping, trigger dump on signal/context, add sections, write key/value entries, dump inode/fd tables, dump memory and mempool info to dicts, and dump xlator profile/history/meminfo/private state.

Control flow and state: `dump_options` is global. Dump functions write either to the dump output or dictionaries. The key-building helper prefixes keys and guards negative snprintf/vsnprintf results.

Dependencies and integration: depends on inode, fd, dict, strfd, xlator, and latency types. Graph cleanup and memory-pool diagnostics rely on statedump visibility.

Risks: dump routines often run during failure or signal-triggered diagnostics, so lock ordering and allocation behavior are sensitive. Fixed key buffer truncation can merge/lose detail. Dumping private translator data can expose inconsistent state if translators mutate concurrently.

Test signals: statedump smoke tests should verify section/key formatting, disabled/enabled option filtering, dictionary dump paths, long key handling, and no deadlock while active fops are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/statedump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/store.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/store.h

Purpose: `store.h` declares a simple persistent key/value file store used by glusterd-style management code.

Important APIs and types: `gf_store_handle_t` tracks path, active fd, temp fd, read `FILE *`, and local lock state. `gf_store_iter_t` tracks an open file, filepath, and read buffer. `gf_store_op_errno_t` distinguishes success, null key/value, EOF, ENOMEM, and stat failure. APIs create directories/handles/temp files, sync directory entries, rename/unlink temp paths, tokenize lines, retrieve/save values/items, iterate entries, stringify store errors, and lock/unlock handles.

Control flow and state: callers create or retrieve a handle, optionally lock it, write to temp files, sync, rename into place, iterate entries, and destroy the handle. Persistence relies on temp-file then rename patterns plus directory sync.

Dependencies and integration: includes compatibility and Gluster core headers. Graph mux pidfile logic is separate but follows similar lock-and-file persistence concerns.

Risks: key/value tokenization must handle malformed lines and buffer limits. Atomicity depends on correct temp path, fsync, rename, and directory sync ordering. `locked` is local state and must match actual `lockf` state.

Test signals: crash-safety tests around temp rename, lock contention, iteration EOF/errors, malformed key/value lines, long values near 8192 bytes, missing directories, and cleanup of temp files are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/strfd.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/strfd.h

Purpose: `strfd.h` defines an in-memory string-backed file-descriptor-like buffer for printf-style accumulation.

Important APIs and types: `strfd_t` stores a data pointer, allocated size, current size, and position. APIs are `strfd_open`, `strprintf`, `strvprintf`, and `strfd_close`.

Control flow and state: callers open a buffer, append formatted data through `strprintf`/`strvprintf`, then close it. State is per-buffer and grows dynamically in the implementation.

Dependencies and integration: used by statedump helpers to construct textual dump output without writing directly to a file descriptor. It depends on stdarg/size/off_t types from includers or implementation.

Risks: ownership of `data` after `strfd_close` is not documented here. Formatting growth must guard integer overflow and allocation failures. `pos` and `size` semantics need consistency if random-access behavior is supported.

Test signals: tests should cover repeated appends, large formatted strings, allocation failure, close semantics, empty buffers, and integration with statedump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/strfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop-utils.h

Purpose: `syncop-utils.h` declares higher-level synchronous traversal and lookup helpers built on the syncop framework.

Important APIs and types: `syncop_dir_scan_fn_t` is a callback for directory entries. APIs include `syncop_ftw`, `syncop_mt_dir_scan`, `syncop_dir_scan`, `syncop_dirfd`, `syncop_is_subvol_local`, `syncop_gfid_to_path`, throttled file-tree walk, inode find, and hard/soft GFID-to-path resolution.

Control flow and state: these helpers issue syncop fops against a subvolume and invoke caller callbacks for directory entries or path resolution. `syncop_mt_dir_scan` adds bounded parallelism via `max_jobs` and `max_qlen`.

Dependencies and integration: depends on `xlator_t`, `call_frame_t`, `loc_t`, `gf_dirent_t`, `inode_table_t`, dictionaries, and syncop primitives. Used by heal, rebalance, quota, or management code needing blocking traversal semantics.

Risks: traversal callbacks can mutate state and need clear ownership of `gf_dirent_t` and loc data. Multi-threaded scans risk queue growth and callback reentrancy. GFID-to-path hard resolution can be expensive and must handle stale inode state.

Test signals: directory traversal over empty/deep/wide trees, callback error propagation, throttling sleep/count behavior, local-subvol detection, GFID lookup misses, and queue bounds for multi-threaded scan should be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop.h

Purpose: `syncop.h` exposes synchronous/blocking wrappers over GlusterFS's asynchronous translator fops and defines the cooperative synctask scheduler used to implement blocking-style workflows.

Important APIs and types: `synctask`, `syncproc`, and `syncenv` implement user-context tasks, processor threads, run/wait queues, scheduler state, and stack sizing. `synclock`, `synccond`, and `syncbarrier` provide task-aware synchronization. `syncargs` stores common callback outputs and wait state. `syncopctx` carries override uid/gid/groups/pid/lkowner. APIs create/destroy/scale syncenvs, spawn/join/wake/yield/sleep tasks, set ids, initialize locks/conds/barriers, and perform many `syncop_*` filesystem operations.

Control flow and state: `SYNCOP` detects whether it runs inside a synctask. Inside a synctask it copies the current op frame; outside it creates a new frame and waits on pthread condition variables. It winds the async fop with `STACK_WIND_COOKIE`, yields or blocks until callback wakeup, then destroys the temporary stack. `syncop_create_frame` fills credentials/groups from `syncopctx` or process state.

Dependencies and integration: deeply depends on `stack.h`, `timer.h`, dict, iatt, iobuf, lock migration, and translator fop callback conventions. It bridges async translators to management/heal code that is easier to express synchronously.

Risks: scheduler state and ucontext stacks are delicate, especially with sanitizer integration. The header as read contains duplicated tokens (`else {` and duplicate `int`/prototype lines), indicating generated or source-quality hazards that builds/tests must catch. Errno decoding differs inside and outside synctasks. Callback wakeup must happen exactly once.

Test signals: build warnings, sanitizer runs, syncop success/error errno behavior, nested syncops, timeout/sleep/yield behavior, credential/group/lkowner propagation, barrier/lock semantics, and each fop wrapper's callback output ownership should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syscall.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syscall.h

Purpose: `syscall.h` declares GlusterFS wrapper functions around POSIX filesystem, xattr, I/O, socket, and platform-specific system calls.

Important APIs and types: wrappers include stat/open/read/write/dirent, mkdir/link/symlink/rename/unlink/chmod/chown/truncate/time, readv/writev/pread/pwrite, statvfs, close/fsync/fdatasync, xattr list/get/set/remove on path/fd, access, fallocate, socket/accept, copy_file_range, kill, and FreeBSD sysctl. It also normalizes xattr prefixes and flags such as `GF_XATTR_CREATE` and `GF_XATTR_REPLACE`.

Control flow and state: no inline logic. Implementations likely centralize portability, retry behavior, logging, or namespace handling. `gf_add_prefix`/`gf_remove_prefix` allocate transformed xattr names.

Dependencies and integration: graph code uses `sys_stat`, `sys_unlink`, `sys_close`, and `sys_ftruncate`. Store and translator implementations can use wrappers for consistent platform behavior.

Risks: wrappers must preserve errno semantics exactly enough to look like syscalls. Platform differences for xattrs, `off64_t`, `copy_file_range`, and Darwin/BSD behavior are high risk. Prefix helpers have allocation ownership contracts not documented here.

Test signals: syscall-wrapper parity tests, errno preservation, xattr namespace behavior on Linux/Darwin/BSD, large-offset copy_file_range, partial read/write behavior, and FreeBSD type compatibility should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/template-component-messages.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/template-component-messages.h

Purpose: `template-component-messages.h` is a template for defining stable component-scoped structured log/message IDs.

Important APIs and types: it includes `glfs-message-id.h` and documents use of `GLFS_COMPONENT`, `GLFS_NEW`, `GLFS_OLD`, and `GLFS_GONE`. The file intentionally contains no real component messages.

Control flow and state: no runtime behavior. It is a developer template and compile-time message catalog pattern.

Dependencies and integration: integrates with structured logging macros in `logging.h`, especially `gf_smsg` and `GF_LOG_*` generated-data macros. Components copy/adapt this template to add message definitions.

Risks: message ordering is stable ABI/user-facing behavior. Adding messages anywhere but the end changes IDs. Removing IDs can cause reuse, so deprecation must leave placeholders. The template guard `_component_MESSAGES_H_` must be renamed for real components.

Test signals: generated message headers should compile, message IDs should remain stable across releases, and logging tests should verify new/old/gone behavior in structured logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/template-component-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/throttle-tbf.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/throttle-tbf.h

Purpose: `throttle-tbf.h` declares a token-bucket filter used to throttle operation classes such as hash, read, and readdir.

Important APIs and types: `tbf_ops_t` enumerates operation buckets. `tbf_opspec_t` defines an op, token rate, max limit, and generation interval in microseconds. `tbf_bucket_t` stores a lock, token generator thread, current rate/tokens/max, queued requests, and interval. `tbf_t` owns an array of buckets. APIs initialize, modify, and throttle; `TBF_THROTTLE_BEGIN/END` wrap throttle calls.

Control flow and state: `tbf_init` creates buckets from specs. A token generator thread refills tokens. `tbf_throttle` consumes requested tokens or queues/sleeps requests until capacity is available. `tbf_mod` updates specs.

Dependencies and integration: uses Gluster list and lock wrappers plus pthreads. It is suitable for translators/features that need bounded background work rates.

Risks: token generation threads need lifecycle management not visible in this header. Queue fairness, wakeups, and dynamic modification are concurrency-sensitive. `TBF_THROTTLE_END` is empty, so callers cannot rely on paired cleanup.

Test signals: rate-limit accuracy, burst max behavior, multi-threaded fairness, runtime modification, shutdown with queued waiters, and invalid op/spec handling should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/throttle-tbf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timer.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timer.h

Purpose: `timer.h` declares a per-context timer registry for delayed callbacks.

Important APIs and types: `gf_timer_t` has list/next/prev linkage, scheduled `timespec`, callback, callback data, owning translator, and fired flag. `gf_timer_registry_t` has an active list, mutex, condition variable, thread, and finish flag. APIs schedule callbacks after a delta, cancel events, and destroy the registry.

Control flow and state: timers are inserted into a context registry, a registry thread waits until the next deadline, fires callbacks, and cancellation removes pending events. State is attached to `glusterfs_ctx_t`.

Dependencies and integration: includes `xlator.h` and pthread/time headers. Logging suppression flush, syncop sleeps/timeouts, and other delayed tasks can use this registry.

Risks: callback lifetime depends on caller-owned `data` and `xl` staying valid until fire/cancel. Races between cancellation and fired callbacks are central. Registry destruction must stop the thread after draining or invalidating callbacks.

Test signals: schedule/cancel races, immediate and delayed timers, destroy with pending timers, callback ordering, fired flag behavior, and translator cleanup interactions should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timespec.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timespec.h

Purpose: `timespec.h` provides time helpers for monotonic/realtime timestamps, arithmetic, and comparison.

Important APIs and types: macros `TS`, `NANO`, and `GIGA` convert or scale nanosecond values. APIs include `timespec_now`, `timespec_now_realtime`, `timespec_now_monotonic_raw`, `timespec_adjust_delta`, `timespec_sub`, and `timespec_cmp`.

Control flow and state: functions fill or manipulate caller-provided `struct timespec` values. No global state is declared.

Dependencies and integration: `stack.h` uses `timespec_now` for frame latency. `timer.h` uses timespec deadlines. Syncop and latency/stat systems rely on accurate comparisons and deltas.

Risks: `TS(ts)` can overflow if applied to very large seconds values. Realtime versus monotonic selection matters for timers and latency; wall-clock changes should not skew monotonic measurements. Nanosecond normalization is required after add/subtract.

Test signals: compare/subtract edge cases, nanosecond borrow/carry, monotonic non-decreasing behavior, realtime availability, and latency measurement sanity tests should be included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timespec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/trie.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/trie.h

Purpose: `trie.h` declares a trie structure with approximate/measurement helpers for stored words.

Important APIs and types: opaque `trie_t` and `trienode_t` hide implementation. `trienodevec` carries a node array and count. APIs create/destroy tries, add words, measure a word into a node buffer or vector, reset search state, get node distance, and recover a node word.

Control flow and state: callers build a trie with `trie_add`, run measurements/searches, optionally reset search state, and destroy the trie or individual nodes. Measurement fills caller-provided node storage or a vector.

Dependencies and integration: memory type entries exist for trie objects in `mem-types.h`. It can support option suggestions, spell-like matching, or command parsing.

Risks: opaque ownership of nodes returned by measure APIs needs implementation consultation. Search state inside the trie makes concurrent searches risky unless externally synchronized. Word buffer ownership from `trienode_get_word` is not documented.

Test signals: add/search exact and near matches, empty trie, duplicate words, reset behavior, vector resizing/limits, Unicode or byte-string assumptions, and concurrent read tests should be considered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/trie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/upcall-utils.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/upcall-utils.h

Purpose: `upcall-utils.h` defines shared event and payload structures for server-to-client upcalls such as cache invalidation, lease recall, and lock contention notifications.

Important APIs and types: flag macros describe invalidated attributes/xattrs/dentries and fop-specific bundles such as `UP_WRITE_FLAGS`, `UP_ATTR_FLAGS`, and `UP_NLINK_FLAGS`. `gf_upcall_event_t` enumerates cache invalidation, recall lease, inode lock contention, and entry lock contention. `gf_upcall` carries client UID, GFID, event type, and event data. Specific payload structs carry iatt snapshots, parent stats, xattr dicts, lease type/tid, lock flock/pid/domain, and contention entry names.

Control flow and state: no logic. Producers allocate/populate payloads and consumers interpret based on `event_type` and flags.

Dependencies and integration: depends on iatt, UUID, compat, dict, and lock types. Translators and protocol layers use it to invalidate client caches and coordinate leases/locks.

Risks: flag combinations must be precise or clients may keep stale metadata. Dict and string pointers require clear ownership/lifetime across async delivery. Event type is `uint32_t` in `gf_upcall`, so enum mismatches must be avoided.

Test signals: cache invalidation tests for each fop class, lease recall delivery, lock contention payloads, xattr add/remove flags, parent stat invalidation on rename/unlink/mkdir/create, and serialization/deserialization compatibility are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/upcall-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/xlator.h -->
# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/xlator.h

Purpose: `xlator.h` is the central translator ABI/API definition. It defines locations, all filesystem operation callback and call signatures, fop tables, translator callback/dump operations, the `xlator_t` runtime object, and the exported `xlator_api_t` module contract.

Important APIs and types: `loc_t` carries path/name/inode/parent and GFIDs. Dozens of `fop_*_t` and `fop_*_cbk_t` typedefs define the async filesystem ABI. `struct xlator_fops` must match `glusterfs-fops.x` ordering and contains callback entries after call entries for `STACK_WIND` type checking. `struct xlator_cbks` handles inode/fd/client lifecycle callbacks. `struct xlator_dumpops` supports statedump. `struct _xlator` stores graph links, options, dlopen handles, fops/cbks/dumpops, init/fini/reconfigure hooks, stats, context, inode table, mem accounting, multiplexing IDs, cleanup flags, and topology metadata. `xlator_api_t` is the module export.

Control flow and state: graph parsing fills name/type/options/child links. Dynamic loading fills function tables and hooks. Stack macros call fops through these tables, while graph lifecycle calls init/reconfigure/fini/notify. Per-fop atomic stats and latency live inside each translator.

Dependencies and integration: this header ties together dicts, iobufs, stacks, options, clients, latency, globals, and graph management. `graph.c`, `options.h`, `stack.h`, and `syncop.h` all depend on its layout.

Risks: ABI stability is critical: fop order, `volume_option_t`, and `xlator_api_t` layout are externally constrained. The scanned source shows duplicated prototype text in this header, which should be watched by builds. `cleanup_starting`, notify, and multiplexing fields are race-sensitive.

Test signals: translator module load/init/fini tests, fop index/stat correctness, graph topology traversal, option validation, pass-through fop dispatch, multiplex attach/detach, loc copy/wipe behavior, and ABI/layout checks are high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/xlator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph-print.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/graph-print.c

Purpose: `graph-print.c` serializes an in-memory `glusterfs_graph_t` back into volfile-like text.

Important APIs and types: `struct gf_printer` abstracts writes and tracks length. `gp_write_file` writes to `FILE *`; `gpprintf` formats with `gf_vasprintf` and writes through the printer. `_print_volume_options` emits `option key value` lines. `glusterfs_graph_print` prints volumes in reverse linked-list order, including type, options, subvolumes, and `end-volume`. `glusterfs_graph_print_file` is the public file-backed entry point.

Control flow and state: printing starts from `graph->first`, walks to the linked-list tail, then walks backward through `prev` so subvolumes appear before parents as volfile syntax expects. Options are printed via `dict_foreach`; child links are printed in list order. The printer length accumulates successful writes.

Dependencies and integration: depends on common utils, xlator graph structures, graph-utils declarations, dict iteration, logging, and GF allocation. It complements `graph.y`/`graph.l` parsing.

Risks: dictionary iteration order may not preserve original option ordering, so output may be semantically equivalent but not text-identical. Values are printed unquoted, which can be unsafe for whitespace/special characters. `fwrite(buf, len, 1)` treats partial writes as failure.

Test signals: round-trip parse/print/parse tests, options containing spaces or quotes, multi-child graphs, empty graph printing, fwrite failure injection, and deterministic output expectations should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph-print.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/graph.c

Purpose: `graph.c` manages GlusterFS translator graphs after parsing: linking, autoload insertion, option validation, initialization, activation, topology comparison, reconfiguration, attach/detach for multiplexed services, cleanup, and pidfile/checksum bookkeeping.

Important APIs and types: key functions include `glusterfs_read_secure_access_file`, `glusterfs_xlator_link`, `glusterfs_graph_insert`, autoload helpers for ACL/WORM/meta/mac-compat/gfid-access, `glusterfs_graph_prepare`, `glusterfs_graph_activate`, `glusterfs_volfile_reconfigure`, `gf_volfile_reconfigure`, `glusterfs_graph_reconfigure`, `glusterfs_graph_destroy`, `glusterfs_graph_fini`, `glusterfs_graph_attach`, `glusterfs_process_svc_attach_volfp`, `glusterfs_process_svc_detach`, and mux pidfile helpers.

Control flow and state: preparation selects graph top, inserts requested autoload translators, stamps DOB/UUID/ID, applies command-line options, and assigns context. Activation counts leaves, validates options, initializes translators, logs unknown options, links graph into `ctx->graphs`, sets `ctx->active`, notifies root of `GF_EVENT_GRAPH_NEW`, and sends parent-up notifications. Reconfiguration parses a new graph, compares topology, and either calls per-translator reconfigure or requires rebuild. Multiplex attach builds a child graph, initializes it, links it under the parent graph, stores checksum/pidfile state, and adds it to context lists. Detach unlinks and spawns cleanup.

Dependencies and integration: depends on `xlator.h`, options, defaults, dict, syscalls, OpenSSL SHA256, pthreads, and parser-provided `glusterfs_graph_construct`.

Risks: many paths manipulate shared graph/context lists and rely on cleanup locks/condition variables. Comments note memory leaks on attach error paths. A scanned call passes `newvolfile_graph->first` where a `char *volume_name` is expected, which should be compile-checked. PID lock setup treats lock failure as non-fatal. Reconfigure topology equality must match mux/server special cases.

Test signals: graph parse/prepare/activate, autoload insertion order, option override, topology equal/not-equal reconfigure, mux attach/detach under concurrent notify, cleanup wait for `child_down_cond`, pidfile update/lock behavior, checksum storage, and failure injection for allocation/init/link errors should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.l -->
# sources/distributed-fs/glusterfs/libglusterfs/src/graph.l

Purpose: `graph.l` is the flex lexer for GlusterFS volfile syntax.

Important APIs and types: it returns tokens for `volume`, `type`, `end-volume`, `subvolumes`, `option`, unquoted IDs, and quoted strings. It defines a `STRING` start condition and accumulates quoted string text in static `text`/`text_size` using `append_string`.

Control flow and state: comments beginning with `#` and whitespace are skipped. Keywords are lowercase regexes. A quote enters `STRING` mode; normal string chunks and escaped characters append to the static buffer; a closing quote returns `STRING_TOK` with `graphyylval = text`. Unquoted words are duplicated and returned as `ID`.

Dependencies and integration: includes `xlator.h` for allocation helpers and `y.tab.h` for parser tokens. The parser in `graph.y` consumes these tokens while holding a graph-construction mutex.

Risks: keyword matching is case-sensitive except for `subvolume[s]` final `s/S`. Unterminated strings are not explicitly reported in the lexer. `append_string` can lose the previous buffer if `GF_REALLOC` fails because it assigns directly to `text`. Static string state is non-reentrant.

Test signals: lexer/parser tests should cover quoted values with escapes, whitespace, comments, uppercase/lowercase keywords, unterminated quotes, allocation failure, and repeated parse invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.y -->
# sources/distributed-fs/glusterfs/libglusterfs/src/graph.y

Purpose: `graph.y` is the yacc/bison parser and constructor for GlusterFS volume files. It turns volume/type/option/subvolume syntax into a linked `glusterfs_graph_t`.

Important APIs and types: grammar rules parse one or more `VOLUME` blocks, each with a header, type line, optional option lines, optional subvolume line, and footer. Helper functions create volumes, set type, set options, link subvolumes, close volumes, report syntax-specific errors, preprocess backtick commands, create graphs, and construct graphs from `FILE *`.

Control flow and state: `glusterfs_graph_construct` creates a graph and temporary file, preprocesses backtick command substitutions, locks a static parser mutex, sets global `graphyyin` and `construct`, and calls `yyparse`. `new_volume` allocates `xlator_t`, rejects duplicate names, initializes options and volume option list, and prepends it to the graph. `volume_type` calls `xlator_set_type`; `volume_option` stores duplicated values in the current xlator dict; `volume_sub` resolves previously defined subvolumes and links parent/child; `volume_end` requires type/fops.

State and persistence: parser state is global/static (`curr`, `construct`, lexer globals) but serialized by `graph_mutex`. Backtick preprocessing executes shell commands via `popen` and writes expanded content to an unlinked temporary file.

Dependencies and integration: depends on `xlator.h`, graph utilities, logging, syscall wrappers, memory allocation, and parser tokens from `graph.l`. Constructed graphs are later prepared/activated by `graph.c`.

Risks: backtick execution is powerful and dangerous for untrusted volfiles. `volume_type` and `volume_option` return `0` even after setting `ret = -1` on some errors, which can mask failures. Static parser globals limit concurrency. Temporary-file and preprocessing allocation failures need cleanup scrutiny.

Test signals: parse valid multi-volume graphs, duplicate volumes/options, undefined/self subvolumes, missing type/subvolume/option values, backtick success/failure/unterminated cases, command-output buffer growth, parser concurrency serialization, and cleanup after parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/graph.y -->
