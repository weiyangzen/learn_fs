# subset-b-006066 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ftrace.c -->
# sources/distributed-fs/ceph-client/kernel/trace/ftrace.c

## Purpose

`ftrace.c` is the core Linux function tracing implementation in this source tree. It maintains the global `ftrace_ops` callback list, discovers instrumentable `mcount`/`fentry` callsites, patches those callsites between NOPs and calls, exposes tracefs/sysctl controls, supports per-instance filter hashes, handles module callsites and init-memory removal, implements function profiling, PID filtering, graph filter files, function probes, and optional direct-call/IPMODIFY coordination. The file is mostly generic infrastructure; architecture hooks provide the actual instruction patching and trampoline generation.

## Important APIs, Types, and Functions

- Global tracer state: `ftrace_enabled`, `ftrace_disabled`, `ftrace_lock`, `ftrace_ops_list`, `ftrace_trace_function`, `function_trace_op`, `global_ops`, `ftrace_list_end`, and dynamic `ftrace_page` lists holding `struct dyn_ftrace` records.
- Registration APIs: `register_ftrace_function()`, `unregister_ftrace_function()`, internal `ftrace_startup()`, `ftrace_shutdown()`, `__register_ftrace_function()`, and `__unregister_ftrace_function()`.
- Dynamic callsite APIs: `ftrace_update_record()`, `ftrace_test_record()`, `ftrace_get_addr_new()`, `ftrace_get_addr_curr()`, `ftrace_modify_all_code()`, `ftrace_run_update_code()`, and weak/arch hooks such as `arch_ftrace_update_code()`, `ftrace_make_call()`, `ftrace_make_nop()`, `ftrace_modify_call()`, `ftrace_init_nop()`, and `arch_ftrace_update_trampoline()`.
- Filter/hash APIs: `alloc_ftrace_hash()`, `free_ftrace_hash()`, `ftrace_lookup_ip()`, `ftrace_hash_move()`, `ftrace_set_filter_ip()`, `ftrace_set_filter_ips()`, `ftrace_set_filter()`, `ftrace_set_notrace()`, `ftrace_set_global_filter()`, `ftrace_set_global_notrace()`, and `ftrace_free_filter()`.
- Tracefs file handlers: `ftrace_avail_fops`, `ftrace_enabled_fops`, `ftrace_touched_fops`, `ftrace_filter_fops`, `ftrace_notrace_fops`, graph filter fops, PID fops, and profiler fops.
- Module and memory lifecycle: `ftrace_process_locs()`, `ftrace_module_init()`, `ftrace_module_enable()`, `ftrace_release_mod()`, `ftrace_free_mem()`, and `ftrace_free_init_mem()`.
- Optional direct-call APIs under `CONFIG_DYNAMIC_FTRACE_WITH_DIRECT_CALLS`: `register_ftrace_direct()`, `unregister_ftrace_direct()`, `modify_ftrace_direct()`, `update_ftrace_direct_add()`, `update_ftrace_direct_del()`, and `update_ftrace_direct_mod()`.
- Probe APIs: `register_ftrace_function_probe()`, `unregister_ftrace_function_probe_func()`, `clear_ftrace_function_probes()`, and `register_ftrace_command()`.
- Lookup/export helpers: `ftrace_location_range()`, `ftrace_location()`, `ftrace_text_reserved()`, `ftrace_lookup_symbols()`, `ftrace_mod_address_lookup()`, and `ftrace_mod_get_kallsym()`.

## Control Flow

Boot-time dynamic setup runs through `ftrace_init()`: the arch hook initializes ftrace, the linker-provided `__start_mcount_loc`/`__stop_mcount_loc` array is sorted if needed, `ftrace_process_locs()` allocates `ftrace_page` groups, fills `dyn_ftrace` records after `ftrace_call_adjust()`, converts initial calls to NOPs with `ftrace_update_code()`, enables `ftrace_enabled`, and applies boot filters from `ftrace_filter=`/`ftrace_notrace=`. For modules, `ftrace_module_init()` builds records while disabled; `ftrace_module_enable()` later validates records, accounts currently active filters, patches eligible module callsites, and then processes cached `:mod:` filters.

Registering an `ftrace_ops` begins at `register_ftrace_function()`, which serializes with `direct_mutex` when direct calls are enabled, checks IPMODIFY/direct sharing, and calls `register_ftrace_function_nolock()`. Startup initializes ops-local hashes, appends the ops to `ftrace_ops_list`, wraps the callback with `ftrace_pid_func` when PID filtering is active, updates trampolines, marks the ops enabled/adding, updates IPMODIFY record flags, increments matching `dyn_ftrace` record reference counts via `ftrace_hash_rec_enable()`, and finally invokes architecture code patching when callsites need changes. Unregister reverses this: it removes the ops from the list, disables IPMODIFY, decrements matching record counts, patches callsites back to NOPs or different trampolines, clears accounting, synchronizes with RCU tasks for dynamic ops, and frees allocated trampolines.

Callsite patching is a two-phase record/accounting flow. `__ftrace_hash_rec_update()` maps an ops filter/notrace hash onto `dyn_ftrace` records and sets count, `FTRACE_FL_REGS`, `FTRACE_FL_TRAMP`, `FTRACE_FL_DIRECT`, and call-ops flags. `ftrace_check_record()` compares desired state with current `_EN` state and returns a specific transition (`MAKE_CALL`, `MAKE_NOP`, `MODIFY_CALL`, or ignore). `__ftrace_replace_code()` computes old/new targets, updates flags, and calls the arch patch primitive. `ftrace_modify_all_code()` coordinates trace function pointer changes by temporarily routing through `ftrace_ops_list_func` before switching to a direct callback/trampoline target.

Runtime dispatch happens in `arch_ftrace_ops_list_func()` and `__ftrace_ops_list_func()`. The dispatcher guards recursion, iterates the RCU-visible `ftrace_ops_list`, skips stubs, enforces RCU-watching constraints for `FTRACE_OPS_FL_RCU`, tests filter hashes with `ftrace_ops_test()`, and invokes each ops callback. If only one ops is active and it can be called directly, `update_ftrace_function()` selects a faster function/trampoline path; otherwise it falls back to the list dispatcher. `ftrace_ops_get_func()` inserts `ftrace_ops_assist_func()` when recursion or RCU assist is required.

Tracefs filtering uses open/write/release staging. `ftrace_regex_open()` creates a per-open copy of the active filter/notrace hash. Writes parse globs, indexes, addresses, or commands such as `func:mod:module` into the staging hash. On release, `ftrace_hash_move_and_update_ops()` atomically swaps the committed hash under `regex_lock` and `ftrace_lock`, then patches callsites if the affected ops is enabled. Graph filters have their own `graph_lock` and hashes. PID tracefs writes create or replace `trace_pid_list` objects, register scheduler callbacks as needed, update per-CPU ignore state, and reselect PID wrapper callbacks.

## State and Persistence Behavior

The durable kernel state is in memory: `dyn_ftrace` pages for callsites, RCU-protected filter hashes, ops lists, cached module filter lists on each `trace_array`, PID lists, graph filter hashes, direct-function hash, module symbol maps, and profiler per-CPU pages. There is no disk persistence in this file; userspace state is mediated through tracefs files and the `kernel.ftrace_enabled` sysctl. Boot command-line filters are transient `__initdata` buffers consumed during initialization. When modules or init memory are freed, corresponding records are removed from ftrace pages and their hash entries are poisoned to `ip = 0` so stale filters cannot match freed text.

Concurrency is central. `ftrace_lock` protects ops and record mutation, `regex_lock` protects a given ops hash, `direct_mutex` serializes direct-call mutations, `graph_lock` protects graph hashes, `trace_types_lock` protects trace-array walks, RCU protects readers of hash/list/module-map data, and `synchronize_rcu_tasks_rude()` is used where ftrace callbacks can run outside ordinary RCU watching. Stop-machine is the generic fallback for code modification.

## Dependencies and Integration Points

This file integrates with architecture ftrace backends, kallsyms, modules, tracefs, trace arrays, the tracing parser, function graph tracer, scheduler tracepoints, kprobes (`kprobe_ftrace_kill()`), perf text-poke/ksymbol events, security lockdown checks, sysctl, RCU, stop_machine, and optional KMSAN/register-save support. `ftrace_internal.h` provides internal prototypes consumed by graph and tracing code. `pid_list.c`/`pid_list.h` back PID filter storage. Module code calls `ftrace_module_init()`, `ftrace_module_enable()`, and `ftrace_release_mod()` during load/unload.

## Risks and Edge Cases

- Code patching failures are fatal for tracing: `FTRACE_WARN_ON*()` calls `ftrace_kill()`, setting `ftrace_disabled`, replacing the callback with `ftrace_stub`, and killing kprobe ftrace integration.
- Filter hash updates must keep record reference counts synchronized with committed hashes. A missed update can leave live callbacks on unintended functions or fail to unpatch callsites.
- Dynamic ops and trampolines require task-RCU synchronization because callbacks can run with preemption disabled or outside normal RCU watching.
- IPMODIFY and direct callbacks are address-sensitive and reject all-function filters; conflicts return `-EBUSY` or require `ops_func` sharing callbacks.
- Module text is initially marked disabled to avoid patching while text permissions are changing; enabling too early would fail instruction validation.
- Tracefs filtering has staged writes. Errors can leave the active hash unchanged, while cached module filters persist until module load or explicit removal.
- The profiler preallocates per-CPU storage; if it runs out of profile records, later functions are silently not counted.

## Test Signals

Useful signals include boot logs reporting allocated ftrace entries/pages/groups, tracefs files `available_filter_functions`, `enabled_functions`, `touched_functions`, `set_ftrace_filter`, `set_ftrace_notrace`, `set_graph_function`, `set_ftrace_pid`, and `function_profile_enabled`, sysctl `kernel.ftrace_enabled`, module load/unload with active filters, direct-call registration/unregistration, and ftrace self-tests guarded by config options such as startup sort tests and weak-function validation. Failures appear as `------------[ ftrace bug ]------------` diagnostics, warnings from bad record/trampoline accounting, `-EINVAL`/`-EBUSY` from filter/direct/IPMODIFY APIs, or `ftrace_is_dead()` returning true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ftrace_internal.h -->
# sources/distributed-fs/ceph-client/kernel/trace/ftrace_internal.h

## Purpose

`ftrace_internal.h` is the private interface shared by function tracing implementation files. It declares registration helpers, dynamic ftrace lifecycle hooks, subops APIs, the global ftrace mutex and global ops object, and graph-tracer state hooks while hiding configuration differences behind small inline fallbacks.

## Important APIs, Types, and Functions

- Always-declared internal registration helpers: `__register_ftrace_function()` and `__unregister_ftrace_function()`.
- Under `CONFIG_FUNCTION_TRACER`, shared globals `ftrace_lock` and `global_ops`.
- Under `CONFIG_DYNAMIC_FTRACE`, prototypes for `ftrace_startup()`, `ftrace_shutdown()`, `ftrace_ops_test()`, `ftrace_startup_subops()`, and `ftrace_shutdown_subops()`.
- Without dynamic ftrace, macro fallbacks call the low-level register/unregister helpers directly, set or clear `FTRACE_OPS_FL_ENABLED`, make `ftrace_ops_test()` always succeed, and reject subops with `-EINVAL`.
- Under `CONFIG_FUNCTION_GRAPH_TRACER`, it exposes `ftrace_graph_active` and, for dynamic ftrace, `fgraph_update_pid_func()`. Without graph tracing, these collapse to zero/no-op definitions.

## Control Flow

The header selects the correct ftrace lifecycle contract at compile time. Dynamic builds call into the full record-patching engine in `ftrace.c`, where ops registration updates filter hashes and machine code. Non-dynamic builds skip callsite patching and directly insert/remove callbacks from the ftrace ops list via `__register_ftrace_function()` and `__unregister_ftrace_function()`. Graph PID integration is similarly conditional: dynamic graph builds update graph callbacks when PID filtering changes; non-graph builds avoid any graph dependency.

## State and Persistence Behavior

This header owns no storage except extern declarations. Its effect on state is indirect: the non-dynamic macros mutate `ops->flags`, while dynamic prototypes route callers to the full state machine in `ftrace.c`. The header's configuration gates make callers compile against a stable API even when underlying state such as `dyn_ftrace` records, graph activity, or subops lists does not exist.

## Dependencies and Integration Points

It depends on definitions from ftrace public/internal kernel headers that provide `struct ftrace_ops`, flags, and graph state. It is included by tracing internals that need ftrace startup/shutdown without depending on all dynamic implementation details. Its prototypes are implemented primarily in `ftrace.c` and consumed by function graph and trace-array setup paths.

## Risks and Edge Cases

- The non-dynamic `ftrace_startup()`/`ftrace_shutdown()` macros deliberately bypass dynamic record filtering, so callers must not assume filter hashes or subops behavior exists in non-dynamic builds.
- Subops callers must handle `-EINVAL` when `CONFIG_DYNAMIC_FTRACE` is off.
- `ftrace_ops_test()` always returns true without dynamic ftrace, so any caller that expects hash-based filtering must be configuration-aware.

## Test Signals

Compile coverage across `CONFIG_FUNCTION_TRACER`, `CONFIG_DYNAMIC_FTRACE`, and `CONFIG_FUNCTION_GRAPH_TRACER` combinations is the main signal. Runtime checks include successful register/unregister paths in non-dynamic builds and graph PID updates becoming no-ops when graph tracing is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/ftrace_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/kprobe_event_gen_test.c -->
# sources/distributed-fs/ceph-client/kernel/trace/kprobe_event_gen_test.c

## Purpose

`kprobe_event_gen_test.c` is a loadable test module for the in-kernel kprobe event generation API. It programmatically creates one kprobe event and one kretprobe event against `do_sys_open`, enables them in the top-level tracing instance, and deletes them on module removal. It is intended as a smoke/integration test for dynamic event command generation, not as production tracing logic.

## Important APIs, Types, and Functions

- Global event handles: `gen_kprobe_test` and `gen_kretprobe_test`, both `struct trace_event_file *`.
- Architecture-specific argument macros map `do_sys_open` arguments to register/stack expressions for x86, arm64, arm, and riscv; unsupported architectures pass `NULL` argument fields.
- `trace_event_file_is_valid()` checks `input && !IS_ERR(input)`.
- `test_gen_kprobe_cmd()` allocates a dynamic event command buffer, initializes `struct dynevent_cmd`, creates a `gen_kprobe_test` kprobe event, adds fields, obtains the event file, and enables the event.
- `test_gen_kretprobe_cmd()` does the same for `gen_kretprobe_test`, using `$retval`.
- `kprobe_event_gen_test_init()` runs both tests at module load.
- `kprobe_event_gen_test_exit()` disables events, drops event-file references, and deletes the generated events.

## Control Flow

On load, `kprobe_event_gen_test_init()` first calls `test_gen_kprobe_cmd()`. That routine allocates `MAX_DYNEVENT_CMD_LEN`, initializes the command with `kprobe_event_cmd_init()`, starts a command with `kprobe_event_gen_cmd_start()`, appends remaining fields via `kprobe_event_add_fields()`, finalizes with `kprobe_event_gen_cmd_end()`, looks up the event through `trace_get_event_file(NULL, "kprobes", "gen_kprobe_test")`, and enables it with `trace_array_set_clr_event()`. If any post-creation step fails, it releases references when necessary and deletes the event with `kprobe_event_delete()`.

The kretprobe path mirrors the kprobe path but uses `kretprobe_event_gen_cmd_start()` and `kretprobe_event_gen_cmd_end()` to create a return probe event with `$retval`. If kretprobe creation fails after the kprobe succeeded, the init path only attempts kretprobe cleanup; the kprobe remains active until module init returns failure handling by the module loader or later exit path, which is a subtle cleanup area to inspect if changing this module.

On unload, both events are disabled before deletion. This ordering matters because trace events cannot be removed while enabled. Each valid `trace_event_file` is returned with `trace_put_event_file()` before the dynamic event is deleted.

## State and Persistence Behavior

The module's persistent state is only the two event-file pointers and the dynamic events registered in the tracing subsystem. The command buffers are temporary and freed before returning. Event lifetime is tied to module lifetime: generated events appear under the `kprobes` event system while the module is loaded and should be removed by `rmmod`.

## Dependencies and Integration Points

This test depends on the dynamic event generator API in `<linux/trace_events.h>`, kprobe/kretprobe event support, trace event lookup/refcounting, and top-level trace-array event enable/disable. It is gated by `CONFIG_KPROBE_EVENT_GEN_TEST` and must be built as a module. It depends on architecture register naming for meaningful field extraction.

## Risks and Edge Cases

- `KPROBE_GEN_TEST_FUNC` is hard-coded to `do_sys_open`; if that symbol is renamed, absent, not probeable, or ABI-specific, module load fails.
- Unsupported architectures pass `NULL` argument fields, so the kprobe event may be less useful or API behavior may differ.
- Failure during the second test requires careful cleanup of the first event if this code is modified; as written, the module init returns the second failure after attempting kretprobe cleanup.
- Events must be disabled before deletion; skipping disable can make removal fail.
- `trace_event_file_is_valid()` treats `ERR_PTR` as invalid but cleanup paths also sometimes set globals to `NULL` only after failed setup.

## Test Signals

The documented manual test is: build with `CONFIG_KPROBE_EVENT_GEN_TEST`, insert `kernel/trace/kprobe_event_gen_test.ko`, open files to trigger `do_sys_open`, and inspect `/sys/kernel/tracing/trace` for repeated `gen_kprobe_test` and `gen_kretprobe_test` events. Removal with `rmmod` should disable and delete both events without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/kprobe_event_gen_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/pid_list.c -->
# sources/distributed-fs/ceph-client/kernel/trace/pid_list.c

## Purpose

`pid_list.c` implements the sparse PID bitmap used by tracing filters such as `set_ftrace_pid` and related trace PID controls. It stores up to 30-bit PIDs in a two-level upper pointer tree plus lower bitmaps, with a small preallocated chunk cache so scheduler-context operations can avoid allocation. Readers use seqcount retry loops, while writers use a raw spinlock and schedule asynchronous cache refills via irq_work.

## Important APIs, Types, and Functions

- Public operations: `trace_pid_list_alloc()`, `trace_pid_list_free()`, `trace_pid_list_is_set()`, `trace_pid_list_set()`, `trace_pid_list_clear()`, `trace_pid_list_first()`, and `trace_pid_list_next()`.
- Addressing helpers: `pid_split()` breaks a PID into `upper1`, `upper2`, and `lower` indexes; `pid_join()` reconstructs a PID for iteration.
- Chunk cache helpers: `get_upper_chunk()`, `get_lower_chunk()`, `put_upper_chunk()`, and `put_lower_chunk()`.
- Refill worker: `pid_list_refill_irq()` allocates replacement chunks with `GFP_NOWAIT` outside the critical scheduler lock path, then splices them into free lists.
- Emptiness helper: `upper_empty()` detects when an upper chunk has no lower chunk pointers and can be recycled.

## Control Flow

Allocation creates a zeroed `trace_pid_list`, initializes `refill_irqwork`, a raw spinlock, and a seqcount associated with that lock, then preallocates `CHUNK_ALLOC` upper and lower chunks into free lists. The implementation warns if `init_pid_ns.pid_max` exceeds the 30-bit design assumption.

Setting a PID validates the PID with `pid_split()`, takes `pid_list->lock` with IRQ save, starts a seqcount write section, obtains or allocates the needed upper and lower chunks from free lists, sets the lower bitmap bit, ends the seqcount write section, and releases the lock. If free chunks fall to `CHUNK_REALLOC` or below, `get_*_chunk()` queues `refill_irqwork` because direct allocation may not be safe while scheduler runqueue locks are held.

Clearing a PID follows the same split and lock path, clears the bit if present, and recycles the lower chunk when its bitmap becomes empty. If the containing upper chunk then has no lower chunks, it is recycled too. Iteration through `trace_pid_list_next()` scans upper1, upper2, and lower bitmap positions under the spinlock and returns the first PID at or after the requested start. `trace_pid_list_first()` is a convenience wrapper starting at zero.

Membership testing is optimized for scheduler hot paths. `trace_pid_list_is_set()` validates the PID, then repeatedly snapshots the relevant pointers and bit under `read_seqcount_begin()`/`read_seqcount_retry()` until no concurrent writer invalidated the read. It avoids taking the raw spinlock on the read side.

Freeing synchronizes pending irq_work, drains free-list chunks, walks all active upper/lower chunks, frees everything, and then frees the list object.

## State and Persistence Behavior

The state is entirely in-memory. `trace_pid_list` contains a 256-entry upper pointer array, two free lists, free counts, lock, seqcount, and irq_work item. Active PID membership lives in lower bitmap chunks. Empty subtrees are returned to the free lists instead of left attached. Free chunk counts are maintained under the raw spinlock, and warnings catch negative counts. No state is persisted outside the owning tracing subsystem.

## Dependencies and Integration Points

The code depends on the layout constants and structures in `pid_list.h`, tracing helpers in `trace.h`, kernel raw spinlocks, seqcount, irq_work, bitmap operations, and slab allocation helpers. It is used by ftrace PID filtering and other trace PID filters to support checks from scheduler switch/fork/exit paths.

## Risks and Edge Cases

- PID validation rejects values `>= MAX_PID`; callers must handle `-EINVAL`.
- If the chunk cache is exhausted, `trace_pid_list_set()` returns `-ENOMEM` instead of allocating directly in a sensitive path.
- `pid_list_refill_irq()` uses `GFP_NOWAIT`; allocation failures stop the current refill attempt and leave future sets dependent on remaining cache.
- Readers rely on seqcount correctness. Any writer that mutates tree pointers without the seqcount would make lockless reads unsafe.
- Iteration uses the raw spinlock and can scan the sparse tree, so very sparse high PID sets may cost more than membership tests.
- Free must call `irq_work_sync()` before releasing memory to avoid use-after-free by pending refill work.

## Test Signals

Direct unit signals are allocation success, set/is_set/clear behavior for low, boundary, and invalid PIDs, first/next iteration ordering, cache refill after more than `CHUNK_ALLOC` sparse insertions, and freeing with pending refill work. Integration signals include ftrace PID tracefs behavior, scheduler switch filtering, and fork/exit propagation of trace PID lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/pid_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/pid_list.h -->
# sources/distributed-fs/ceph-client/kernel/trace/pid_list.h

## Purpose

`pid_list.h` defines the sparse PID bitmap data structure used internally by tracing. It documents the page-table-like layout that divides a PID into two 8-bit upper indexes and one 14-bit lower bitmap index, providing compact storage for sparse PID sets without allocating a full PID_MAX bitmap.

## Important APIs, Types, and Functions

- Layout constants: `UPPER_BITS`, `UPPER_MAX`, `UPPER1_SIZE`, `UPPER2_SIZE`, `LOWER_BITS`, `LOWER_MAX`, `LOWER_SIZE`, `UPPER1_SHIFT`, `UPPER2_SHIFT`, `LOWER_MASK`, `UPPER_MASK`, and `MAX_PID`.
- Cache constants: `CHUNK_ALLOC` preallocates six upper and lower chunks; `CHUNK_REALLOC` queues refill when only two chunks remain.
- `union lower_chunk` is either a free-list `next` pointer or a lower bitmap array of `LOWER_SIZE` unsigned longs.
- `union upper_chunk` is either a free-list `next` pointer or an array of `UPPER2_SIZE` lower-chunk pointers.
- `struct trace_pid_list` stores the seqcount, raw spinlock, refill irq_work, top-level upper array, free lists, and free counters.

## Control Flow

The header itself has no executable control flow, but its structure determines `pid_list.c` behavior. A PID is split by shifting and masking: the top 8 bits index `trace_pid_list.upper`, the next 8 bits index an `upper_chunk->data[]` lower-chunk pointer, and the bottom 14 bits select a bit in the lower bitmap. Empty upper/lower chunks can be moved between active tree positions and free lists because the same union memory overlays free-list linkage with active data.

## State and Persistence Behavior

State is maintained in `struct trace_pid_list` instances allocated by `trace_pid_list_alloc()`. The initial top-level array is part of the object, while upper/lower chunks are allocated separately and cached. The structure is not persistent; it is owned by a trace array or trace option and freed when the filter is cleared.

## Dependencies and Integration Points

The header assumes kernel definitions for `seqcount_raw_spinlock_t`, `raw_spinlock_t`, `irq_work`, `BITS_PER_LONG`, and PID maximum constraints from `linux/thread.h`. It is explicitly marked "Do not include this file directly", so it is intended for internal tracing headers/source files rather than general kernel users.

## Risks and Edge Cases

- The design assumes PIDs are less than `1 << 30`; larger PID namespaces would invalidate the split and are guarded by runtime warnings in the implementation.
- The union overlay requires chunks to be zeroed or fully initialized when switching from free-list to active data; stale active pointers or bits would corrupt membership.
- Memory footprint scales with sparse chunks, not PID count, but worst-case sparse PIDs across many upper indexes can allocate many 2 KiB lower bitmaps.
- Cache sizes are policy embedded in constants; changing them affects scheduler-path allocation pressure.

## Test Signals

Test signals are mostly from `pid_list.c`: correct split/join behavior at boundaries, chunk allocation/reuse, empty subtree recycling, and behavior near `MAX_PID - 1` versus `MAX_PID`. Static compile coverage should ensure structure sizes and `LOWER_SIZE` match the comments across 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/pid_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/power-traces.c -->
# sources/distributed-fs/ceph-client/kernel/trace/power-traces.c

## Purpose

`power-traces.c` instantiates and exports selected power-management tracepoints. By defining `CREATE_TRACE_POINTS` before including `<trace/events/power.h>`, it emits the storage and tracepoint definitions for the power event class in exactly one translation unit, then exports key tracepoints for GPL modules.

## Important APIs, Types, and Functions

- Includes power-management and tracing dependencies such as string/types, workqueues, scheduler, and modules.
- `#define CREATE_TRACE_POINTS` controls tracepoint definition generation from `<trace/events/power.h>`.
- `EXPORT_TRACEPOINT_SYMBOL_GPL(suspend_resume)`, `EXPORT_TRACEPOINT_SYMBOL_GPL(cpu_idle)`, and `EXPORT_TRACEPOINT_SYMBOL_GPL(cpu_frequency)` make these tracepoints available to GPL modules.

## Control Flow

There is no runtime function body in this file. Its control flow is compile/link-time tracepoint instantiation: the trace event header expands into tracepoint objects and helper code because `CREATE_TRACE_POINTS` is set. At module/kernel link time, the three named tracepoint symbols are exported.

## State and Persistence Behavior

The generated tracepoint objects are static kernel state created by the trace event macros. Their enabled/disabled runtime state is managed by the common tracepoint/tracing infrastructure, not by explicit code here. No file-local persistent state or cleanup path exists.

## Dependencies and Integration Points

This file integrates with the generic tracepoint system and the power trace event definitions in `<trace/events/power.h>`. Other kernel code and GPL modules can register probes against `suspend_resume`, `cpu_idle`, and `cpu_frequency`. The generated trace events appear through the normal tracing/event infrastructure.

## Risks and Edge Cases

- `CREATE_TRACE_POINTS` must appear in only one translation unit for a given trace event header; duplicating it elsewhere would cause duplicate definitions.
- Removing an export would break GPL modules that attach to these tracepoints.
- The file relies on the event header for actual field schemas and probe call signatures; schema changes happen there, not here.

## Test Signals

Compile/link success is the primary signal because this is a tracepoint definition unit. Runtime signals include the presence of power events in tracefs and successful module/probe registration against `suspend_resume`, `cpu_idle`, and `cpu_frequency`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/power-traces.c -->
