# subset-b-006071 research

Grouped research for subset B work item `subset-b-006071`. Each section preserves the source path in its title and is wrapped with the exact reconciliation markers requested.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events.c

## Purpose
`trace_events.c` is the core event-tracing manager for the kernel trace subsystem copy in the distributed-fs/Ceph-client source tree. It registers `struct trace_event_call` definitions, creates per-trace-array `struct trace_event_file` instances, builds the tracefs/eventfs `events/` hierarchy, exposes enable/filter/format/id/trigger/PID-control files, and coordinates event enablement with tracepoint registration, perf, triggers, modules, early boot tracing, and self-tests.

Although this path sits under the Ceph-client source mirror, the file is generic Linux tracing infrastructure. It is relevant to distributed filesystem observability because Ceph client tracepoints use this common machinery for runtime enablement, filtering, formatting, tracefs control, and module lifetime handling.

## Important APIs, Types, and Functions
- Global state: `event_mutex`, `ftrace_events`, `ftrace_generic_fields`, `ftrace_common_fields`, `event_subsystems`, `module_strings`, `field_cachep`, `file_cachep`, and `eventdir_initialized` hold registered event calls, shared field definitions, subsystem descriptors, module-owned replacement strings, slab caches, and tracefs initialization state.
- Field management: `trace_define_field()`, `trace_define_field_ext()`, `trace_define_generic_fields()`, `trace_define_common_fields()`, `trace_destroy_fields()`, `trace_event_get_offsets()`, `event_define_fields()`, `trace_find_event_field()`, and `update_event_fields()` build the `format` metadata and filterable field list.
- Print-format validation and updating: `test_event_printk()`, `process_pointer()`, `process_string()`, `handle_dereference_arg()`, `update_event_printk()`, and `trace_event_update_all()` validate unsafe `%p*`/`%s` dereferences and replace enum/eval names with numeric values.
- Event registration: `trace_event_raw_init()`, `event_init()`, `__register_event()`, `trace_add_event_call()`, `trace_remove_event_call()`, `event_remove()`, and `__trace_remove_event_call()` register/unregister event calls and their trace event IDs.
- Event enablement: `trace_event_reg()`, `__ftrace_event_enable_disable()`, `trace_event_enable_disable()`, `ftrace_event_enable_disable()`, `ftrace_set_clr_event()`, `trace_set_clr_event()`, and `trace_array_set_clr_event()` translate tracefs writes and in-kernel requests into tracepoint probe registration/unregistration.
- Ring-buffer entry path: `trace_event_buffer_reserve()` reserves trace records after PID-filter checks and initializes `struct trace_event_buffer`.
- Tracefs/eventfs interfaces: file operations for `available_events`, `set_event`, `show_event_filters`, `show_event_triggers`, `set_event_pid`, `set_event_notrace_pid`, event `enable`, event `format`, event `filter`, subsystem `filter`, subsystem `enable`, and header files connect user-visible tracefs files to seq-file/read/write handlers.
- PID filters: `event_pid_write()`, `register_pid_events()`, `unregister_pid_events()`, `trace_event_follow_fork()`, scheduler hooks, `ignore_task_cpu()`, and `trace_event_ignore_this_pid()` maintain per-trace-array include/exclude PID lists.
- Directory and lifetime handling: `event_subsystem_dir()`, `event_create_dir()`, `remove_event_file_dir()`, `event_file_get()`, `event_file_put()`, `event_trace_add_tracer()`, and `event_trace_del_tracer()` manage eventfs hierarchy, subsystem refcounts, and per-instance file lifetime.
- Module support: `event_mod_load`, `cache_mod()`, `update_mod_cache()`, `trace_module_add_events()`, `trace_module_remove_events()`, and `trace_module_notify()` support module event registration and deferred `set_event:mod:` enablement.
- Dynamic ftrace event commands: under `CONFIG_DYNAMIC_FTRACE`, `event_enable_func()` and associated probe ops implement `enable_event`/`disable_event` ftrace function commands.
- Initialization and tests: `trace_event_init()`, `event_trace_enable()`, `event_trace_init()`, `early_enable_events()`, `event_trace_enable_again()`, `event_trace_self_tests_init()`, and helpers for `CONFIG_EVENT_TRACE_STARTUP_TEST`.

## Control Flow
Initialization starts in `trace_event_init()`. It creates slab caches, initializes syscall trace events, runs `event_trace_enable()` to register static trace event calls from the linker section, creates early `trace_event_file` descriptors for the top trace array, applies `trace_event=` boot parameters, starts trace-printk command recording, and registers ftrace event commands. `event_trace_init_fields()` then defines common and generic filter fields. Later, `event_trace_init()` creates the user-visible tracefs files, attaches event directories to the early descriptors, registers the module notifier, and marks event directories initialized.

When a trace event call is registered, `event_init()` invokes its raw init hook, `__register_event()` links it into `ftrace_events`, and `__add_event_to_tracers()` creates matching `trace_event_file` entries for every existing trace array. `trace_create_new_event()` filters by `tr->system_names`, allocates a `trace_event_file`, copies PID-filter state into flags, initializes trigger lists and reference counts, and appends the file to `tr->events`. If eventfs is live, `event_create_dir()` creates `events/<system>/<event>/` entries and defines fields; otherwise early boot only defines fields.

Enable writes flow through either global `set_event`, subsystem `enable`, per-event `enable`, or in-kernel APIs. `ftrace_set_clr_event()` parses `<system>:<event>` and optional `:mod:<module>` forms. `__ftrace_set_clr_event_nolock()` walks matching `trace_event_file` entries, skips ignored or non-registerable events, and calls `ftrace_event_enable_disable()`. The lower-level `__ftrace_event_enable_disable()` controls command/TGID recording side effects, soft-disable reference counts, `EVENT_FILE_FL_ENABLED`, `EVENT_FILE_FL_SOFT_DISABLED`, and calls the event class `reg()` hook. For tracepoint events, `trace_event_reg()` maps this to `tracepoint_probe_register()` or `tracepoint_probe_unregister()`, with perf-specific register operations when enabled.

Runtime event recording normally enters generated tracepoint code, which calls `trace_event_buffer_reserve()`. This checks `EVENT_FILE_FL_PID_FILTER` and the per-CPU `ignore_pid` state, computes tracing context, reserves a ring-buffer event via `trace_event_buffer_lock_reserve()`, and returns the event payload pointer to the generated assign/commit path.

Filter and trigger visibility is split across this file and filter/trigger helpers. Per-event `filter` writes call `apply_event_filter()` from `trace_events_filter.c`; subsystem `filter` writes call `apply_subsystem_event_filter()`. `show_event_filters` and `show_event_triggers` iterate enabled metadata under `event_mutex` and print event-qualified filter or trigger strings.

PID filtering is driven by writes to `set_event_pid` and `set_event_notrace_pid`. `event_pid_write()` updates the appropriate `trace_pid_list`, sets `EVENT_FILE_FL_PID_FILTER` on every file in the trace array, registers scheduler tracepoint probes when needed, synchronizes and frees old lists, and runs `ignore_task_cpu()` on each CPU to seed current per-CPU ignore state. Scheduler hooks update `ignore_pid` before and after sched switch and wakeup events so event probes can cheaply reject records from ignored tasks.

On module load, `trace_module_notify()` adds module trace events under `event_mutex` and `trace_types_lock`, then applies cached `:mod:` requests. On module unload it removes matching event calls, frees module-owned field type strings created by enum/eval replacement, and resets online CPU buffers to avoid stale ring-buffer records being interpreted with reused event IDs.

## State and Persistence
The file has no durable storage. State is in kernel memory, trace arrays, eventfs dentries/inodes, module notifier state, and boot-parameter buffers. Key persistent-for-runtime structures are `struct trace_event_call` in `ftrace_events`, `struct trace_event_file` per trace array, `struct event_subsystem` shared by same-named systems, `struct trace_subsystem_dir` per trace array/system, per-event filters and triggers, PID include/exclude lists, and module-deferred event requests in `tr->mod_events`.

Reference counts protect subsystem directories and event files: subsystem refs are incremented on open and when reused across trace arrays; event files are refcounted for eventfs file lifetime and freed after `EVENT_FILE_FL_FREED` is set. RCU is used for PID lists and filters, while tracepoint synchronization ensures old probes and filters are no longer executing before memory is freed.

Boot state includes `bootup_event_buf` for `trace_event=` and `bootup_triggers` for `trace_trigger=`. These are applied during early initialization so events can be active before tracefs exists, then later attached to real eventfs directories.

## Dependencies and Integration Points
This file depends on the tracing core (`trace.h`, `trace_output.h`, trace arrays, trace buffers, trace parser, trace flags), eventfs/tracefs, tracepoints, perf events, syscall tracing, ftrace function probes, trigger and histogram files, PID list helpers, ring-buffer formatting, module notifiers, security lockdown checks, RCU, SRCU/tracepoint synchronization, lockdep, workqueues, kthreads, and boot parameter parsing.

Important integration points include generated `TRACE_EVENT` descriptors, `trace_events_filter.c` for parsing/applying filters, trigger code for `trigger` and boot triggers, perf for `id` files and event profile filters, module lifecycle hooks for load/unload, scheduler tracepoints for PID filters, and function tracing commands for function-probe-based event enable/disable.

## Risks
- Lock ordering is delicate: many paths require `event_mutex`; directory creation/removal also uses `trace_types_lock` and `trace_event_sem`; module notifications nest these locks. Reordering can deadlock.
- Enable/disable and soft-disable behavior is subtle. Soft mode keeps tracepoints registered while suppressing event recording, so removal paths must explicitly reject enabled files and not rely only on normal disable calls.
- RCU-protected filters and PID lists require delayed freeing and tracepoint synchronization. Freeing too early risks use-after-free in active tracepoint probes.
- Module unload can leave stale event IDs in ring buffers, so reset behavior is required. Missing it can cause later decoding with the wrong event format.
- Field metadata is shared by event classes. Defining, updating, and destroying fields must account for class reuse and module-owned strings.
- `test_event_printk()` is a heuristic validator, not a full C expression parser. It catches common unsafe dereferences but can allow or warn on unusual formatting expressions.
- Tracefs write handlers mutate user buffers after parsing to restore separators; callers that reuse strings must tolerate this convention.

## Test Signals
Useful signals include successful creation of `available_events`, `set_event`, `events/<system>/<event>/format`, `enable`, `filter`, and `trigger` files; boot with `trace_event=` and `trace_trigger=`; enabling/disabling individual, subsystem, and all events; writes to `set_event_pid` and `set_event_notrace_pid`; module load/unload with `:mod:` cached enablement; `show_event_filters` and `show_event_triggers` output; tracefs lockdown denial paths; perf event ID availability; and `CONFIG_EVENT_TRACE_STARTUP_TEST` logs showing per-event, per-subsystem, all-event, and function-tracer-combined tests passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter.c

## Purpose
`trace_events_filter.c` implements the generic event-filtering engine used by trace events and perf tracepoint events. It parses filter expressions written to tracefs `filter` files or supplied by perf, validates fields and operands, compiles logical expressions into a small forward-branching predicate program, evaluates that program against trace records, and manages filter lifetime under RCU.

The implementation supports numeric fields, static strings, dynamic strings, relative dynamic strings, `char *` strings, user-space string pointers via `.ustring`, current CPU and `CPUS{}` masks, `COMM`, stacktrace pseudo-fields, kernel function address matching via `.function`, and restricted function-trace `ip` filters for perf/ftrace.

## Important APIs, Types, and Functions
- Operators and errors: `enum filter_op_ids`, `ops[]`, `ERRORS`, `err_text[]`, and `struct filter_parse_error` define supported operators (`~`, `!=`, `==`, `<=`, `<`, `>=`, `>`, `&`) and user-facing parse errors.
- Predicate representation: `struct filter_pred` stores a field, operation, comparison value(s), regex, cpumask, predicate function number, offset, and inversion flag. `enum filter_pred_fn` selects the concrete evaluator.
- Program representation: `struct prog_entry` stores a predicate, branch target, and branch condition. `predicate_parse()` compiles logical expressions with `&&`, `||`, `!`, and parentheses into a forward-only program ending in TRUE/FALSE sentinel entries.
- Evaluation: `filter_match_preds()` runs the compiled program against a trace record, using `filter_pred_fn_call()` to dispatch to typed predicate evaluators.
- Predicate evaluators: generated scalar functions handle equality and comparison for 8/16/32/64-bit signed and unsigned fields; cpumask helpers handle scalar-to-mask and mask-to-mask comparisons; string predicates handle fixed arrays, dynamic string locations, relative dynamic string locations, kernel `char *`, user `char *`, `COMM`, CPU, cpumask, and function address ranges.
- Regex/glob support: `filter_parse_regex()`, `filter_build_regex()`, `regex_match_full()`, `regex_match_front()`, `regex_match_middle()`, `regex_match_end()`, and `regex_match_glob()` implement the limited string/glob matching used by `~`, `==`, and `!=`.
- Type assignment: `filter_assign_type()` classifies trace event field type strings into filter categories such as dynamic string, relative dynamic string, static string, pointer string, cpumask, or other.
- Filter construction and application: `create_event_filter()`, `apply_event_filter()`, `apply_subsystem_event_filter()`, `create_filter()`, `create_system_filter()`, `process_preds()`, and `process_system_preds()` allocate, parse, install, or remove filters.
- Lifetime helpers: `free_event_filter()`, `free_prog()`, `try_delay_free_filter()`, `delay_free_filter()`, `filter_free_subsystem_filters()`, and list-based delayed freeing coordinate RCU tasks trace and normal RCU grace periods before freeing old filters.
- Printing: `print_event_filter()` and `print_subsystem_event_filter()` provide tracefs read output.
- Perf integration: `ftrace_profile_set_filter()` and `ftrace_profile_free_filter()` attach filters to perf tracepoint events; function-event special handling maps ORed `ip == pattern`/`ip != pattern` clauses to ftrace filter/notrace hashes.
- Startup tests: under `CONFIG_FTRACE_STARTUP_TEST`, the file includes `trace_events_filter_test.h`, builds synthetic filter test records, and verifies both matching results and short-circuit behavior.

## Control Flow
Applying a per-event filter starts in `apply_event_filter()` while `event_mutex` is held by the caller. The string `"0"` removes the filter: the event filtered flag is cleared, the current filter pointer is cleared, and old memory is freed after tracepoint-safe synchronization. Other strings call `create_filter()`, which allocates an `event_filter`, copies the filter string for tracefs visibility, allocates parse-error state, and calls `process_preds()`.

`process_preds()` first calls `calc_stack()` to count predicates and maximum parenthesis depth while checking quote and parenthesis balance. It then calls `predicate_parse()`. `predicate_parse()` performs a first pass over tokens, uses an operator stack to handle nested parentheses and inversion, gives `&&` higher precedence than `||`, and emits program entries with branch metadata. A second pass optimizes branches that jump to labels with equivalent conditions, and a third pass folds `!` inversion into each entry's branch condition while verifying every target moves forward.

`parse_pred()` is called for each leaf predicate. It extracts the field name, resolves it with `trace_find_event_field()`, parses optional `.ustring` and `.function` suffixes, identifies the operator, and then parses an operand. Operand handling selects one of several paths: function symbol/address lookup, special function-trace `ip` strings, `CPUS{}` masks, quoted strings, or integers. The parser validates field type and operator compatibility, fills `struct filter_pred`, builds regex matchers for strings, allocates per-CPU string-copy buffers for pointer strings when needed, and selects the evaluator function.

At event runtime, generated trace code or perf calls `filter_match_preds()`. A missing filter or missing program matches by default. Otherwise, the evaluator walks the program array, evaluates each predicate against the trace record, and if the predicate result equals `when_to_branch`, jumps to the stored target. The TRUE/FALSE sentinel target determines the final return value. This gives short-circuit behavior without recursion or AST traversal.

Subsystem filters flow through `apply_subsystem_event_filter()`. The string `"0"` removes all per-event filters in that subsystem and clears the subsystem display filter. Otherwise, `create_system_filter()` calls `process_system_preds()`, which attempts to create a separate compiled filter for every event in the subsystem. Events whose fields cannot support the subsystem filter receive a filter object containing the parse error and have filtering disabled; successful events are marked filtered. Old filters are collected and freed after a delayed RCU sequence.

Perf tracepoint filters use `ftrace_profile_set_filter()`. Non-function events keep the compiled filter on `event->filter`. Function trace events are special: their filters must be OR-only clauses on the `ip` field, and each predicate is translated into ftrace `filter` or `notrace` patterns rather than evaluated directly by the event-filter program.

## State and Persistence
Filter state is in `struct event_filter`, which owns the printable `filter_string` and RCU-protected compiled `prog`. Each `prog_entry` owns a `filter_pred`, and predicates may own a `regex` or dynamically allocated `cpumask`. Per-event filters are reached through `trace_event_file->filter`; subsystem filters keep a display object in `event_subsystem->filter` but install per-event compiled filters on each file. Perf filters live on `perf_event->filter`.

There is no durable persistence. Filters persist only until replaced, cleared by writing `"0"`, subsystem-filter reset, event removal, perf close, trace array deletion, or module/event lifetime cleanup. Old filters can outlive replacement briefly through `call_rcu_tasks_trace()` followed by queued RCU work, matching tracepoint unregister synchronization semantics.

`ustring_per_cpu` is a lazily allocated per-CPU buffer used to safely copy kernel or user string pointers before matching. Once allocated, it remains for the lifetime of the kernel session.

## Dependencies and Integration Points
This file depends on `trace_find_event_field()` and field metadata from `trace_events.c`, `event_mutex` locking, RCU pointer assignment for filters, tracepoint synchronization semantics, cpumask parsing and comparison, kallsyms lookup for `.function`, `glob_match()` and string helpers, nofault kernel/user string copy helpers, perf events, ftrace function filters, generated trace event raw structs, and trace logging via `tracing_log_err()`.

The primary integration points are per-event and subsystem tracefs `filter` files in `trace_events.c`, generated tracepoint fast paths that call `filter_match_preds()`, perf tracepoint filter setup, and the optional startup test event declared in `trace_events_filter_test.h`.

## Risks
- Parser correctness is central. Incorrect precedence, parenthesis handling, inversion folding, or branch optimization can silently change filter semantics.
- Filter lifetime crosses tracepoint execution. Any missed RCU/tasks-trace grace period can lead to use-after-free in active probes.
- String pointer predicates copy from potentially invalid kernel or user addresses. The nofault copy helpers reduce crash risk, but bad pointers simply fail to match.
- `.function` depends on kallsyms and function size/offset lookup; unavailable symbols or unusual address ranges produce parse errors.
- `CPUS{}` masks have optimized scalar special cases. Equality/inequality semantics differ between scalar fields and true cpumask fields, so regressions here can be subtle.
- Subsystem filters intentionally partially apply. One event can fail while another succeeds, and user-visible errors must make that clear without rolling back successful filters.
- Function-event perf filters accept only OR-like `ip` predicates. Accepting richer expressions would not map cleanly to ftrace filter/notrace state.

## Test Signals
Signals include tracefs writes such as `common_pid == 1`, `comm ~ "ceph*"`, `CPU == 0`, `CPU & CPUS{0-3}`, dynamic string comparisons, invalid field/operator errors with caret position, clearing filters by writing `0`, subsystem filters that affect only compatible events, and perf tracepoint filters. With `CONFIG_FTRACE_STARTUP_TEST`, `ftrace_test_event_filter()` verifies many nested `&&`/`||`/`!` expressions and checks that predicates expected to be short-circuited are not visited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter_test.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter_test.h

## Purpose
`trace_events_filter_test.h` declares the synthetic `ftrace_test_filter` trace event used by the `CONFIG_FTRACE_STARTUP_TEST` self-test in `trace_events_filter.c`. It provides a simple event schema with eight integer fields so the filter parser and predicate program can be tested against predictable records and short-circuit expectations.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM test` sets the trace system name for this generated event header.
- `TRACE_EVENT(ftrace_test_filter, ...)` defines the tracepoint prototype, arguments, record layout, assignment, and print format.
- `TP_PROTO(int a, int b, int c, int d, int e, int f, int g, int h)` and `TP_ARGS(...)` define eight integer inputs.
- `TP_STRUCT__entry()` creates fields `a` through `h`, all `int`, which become filterable fields in the generated `struct trace_event_raw_ftrace_test_filter`.
- `TP_fast_assign()` copies the arguments into the trace record.
- `TP_printk()` formats all eight fields in a fixed, human-readable order.
- `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_events_filter_test`, and `<trace/define_trace.h>` enable tracepoint code generation when included with `CREATE_TRACE_POINTS`.

## Control Flow
The header follows the standard trace event header pattern. Include guards allow normal inclusion while `TRACE_HEADER_MULTI_READ` lets trace generation re-read the header. When `trace_events_filter.c` is built with `CONFIG_FTRACE_STARTUP_TEST`, it defines `CREATE_TRACE_POINTS` before including this header. That causes the trace event macros to emit the generated tracepoint, event call, raw record struct, and helper functions.

The startup test then calls `create_filter()` against `event_ftrace_test_filter`, constructs `struct trace_event_raw_ftrace_test_filter` records with different `a` through `h` values, and runs `filter_match_preds()` against those records. The event may also be emitted once through `trace_ftrace_test_filter(1, 2, 3, 4, 5, 6, 7, 8)` to avoid unused tracepoint warnings.

## State and Persistence
The header does not store runtime state itself. It defines the schema that generated trace code uses to create event metadata and raw records. Runtime state for the self-test lives in `trace_events_filter.c`: compiled filters, test data arrays, visited-predicate markers, and the generated `event_ftrace_test_filter` descriptor.

There is no persistence beyond compiled kernel text/data for the test build. The event exists only when the self-test configuration includes it.

## Dependencies and Integration Points
This header depends on `<linux/tracepoint.h>` and the kernel `TRACE_EVENT` macro system. It is included by `trace_events_filter.c` under `CONFIG_FTRACE_STARTUP_TEST`, where generated artifacts integrate with the normal event registration path, field-definition logic in `trace_events.c`, and filter lookup through `trace_find_event_field()`.

Because the fields are plain integers with simple names, the event is ideal for exercising logical-expression compilation without complications from string, cpumask, function, or dynamic-array predicate types.

## Risks
- The header must remain outside ordinary include protection for `<trace/define_trace.h>` at the bottom; moving it inside the guard would break tracepoint generation.
- Field names `a` through `h` are assumed by the test data in `trace_events_filter.c`. Renaming or changing field types would invalidate those tests.
- The generated raw struct name is consumed directly by the test (`struct trace_event_raw_ftrace_test_filter`), so event-name changes require coordinated updates.
- Because this is a startup-test-only header, it may receive less build coverage in configurations without `CONFIG_FTRACE_STARTUP_TEST`.

## Test Signals
The main signal is boot-time output from `ftrace_test_event_filter()`, especially the final `Testing ftrace filter: OK` line. Failures report either filter creation errors, unexpected predicate visits that indicate short-circuit regressions, or mismatched filter results. Successful generation also exposes the synthetic event metadata internally as `event_ftrace_test_filter` and the helper `trace_ftrace_test_filter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter_test.h -->
