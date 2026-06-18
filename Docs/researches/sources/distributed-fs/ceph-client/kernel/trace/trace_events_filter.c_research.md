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
