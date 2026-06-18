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
