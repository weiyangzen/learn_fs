# subset-b-006762 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/evsel.c

## Purpose

`evsel.c` is the main perf event-selector implementation. It turns parsed event requests into initialized `struct evsel` objects, configures `perf_event_attr`, opens perf event file descriptors across CPU/thread maps, reads counts, parses sample records, names events for user output, records event IDs, and applies compatibility fallbacks for older kernels and PMUs.

## Important APIs, Types, and Functions

The file implements `evsel__object_config`, `evsel__init`, `evsel__new_idx`, `evsel__clone`, `evsel__newtp_idx`, `evsel__config`, `evsel__open`, `evsel__close`, `evsel__read_counter`, `evsel__parse_sample`, `evsel__fallback`, `evsel__open_strerror`, `evsel__store_ids`, group helpers, hybrid helpers, and event-name helpers. It owns the global `struct perf_missing_features perf_missing_features`, hardware/software/cache name tables, BPF counter event matching, and weak architecture hooks such as `arch_evsel__hw_name`, `arch__post_evsel_config`, `arch_evsel__set_sample_weight`, and `arch_evsel__open_strerror`.

## Control Flow

Construction starts with libperf `perf_evsel__init`, local defaults, list initialization, optional BPF output and clock-event adjustment, and deep-copy support for parsed-but-unopened selectors. `evsel__config` then combines record options, callchain options, per-event config terms, sample bits, mmap/comm/task tracking, branch stack settings, read formats, inherit behavior, clock IDs, and special off-CPU/dummy/AUX constraints. Opening uses `__evsel__prepare_open`, dispatches tool/hwmon/DRM/TPEBS PMUs to specialized open paths, otherwise loops CPU map indexes and thread indexes through `sys_perf_event_open`, attaching BPF fds and test-attribute logging when enabled. On failure it can remove vanished threads, raise `RLIMIT_NOFILE`, probe missing kernel features, reduce `precise_ip`, close partially opened descriptors, and mark the event unsupported.

Counter reads dispatch to tool/hwmon/DRM/TPEBS/group/single read paths. Group reads require IDs and map each returned ID back through the evlist. Sample parsing follows perf sample ABI order, initializes a `perf_sample`, handles non-sample `sample_id_all` trailers, and bounds-checks every variable-length region before exposing pointers to raw data, callchains, branch stacks, register dumps, stacks, AUX samples, and off-CPU synthesized samples.

## State and Persistence Behavior

Persistent object state lives in `struct evsel`: copied strings, config terms, cgroup references, PMU pointer, fd arrays, counts, previous counts for deltas, per-package masks, side-band callback data, BPF handles, stats, branch-counter metadata, and fallback flags. Global state includes missing-feature probes, cached empty CPU/thread maps, a process-wide clock ID used for errors, and optional private destructors. Runtime kernel resources are perf fds, IDs, BPF attachments, TPEBS resources, and count arrays; `evsel__exit` releases them and frees owned strings and hashmaps.

## Dependencies and Integration Points

This file integrates with libperf (`perf_evsel`, CPU/thread maps), `perf_event_open`, PMU discovery, BPF counters and filters, evlists, stats, histograms, callchains, trace-event parsing, tool PMUs, hwmon/DRM PMUs, Intel TPEBS, cgroups, procfs/sysfs, perf session/env metadata, and architecture-specific hooks. It is used by perf record/stat/report/script/top paths as the common event abstraction.

## Risks and Edge Cases

The highest-risk areas are kernel ABI compatibility probing, sample layout ordering, cross-endian decoding, group read ID matching, hybrid PMU CPU-map remapping, partial-open cleanup, mutable fallback names, and ownership of copied config strings. Incorrect `sample_size` or missing overflow checks can corrupt parsing. Fallbacks can silently change event semantics from hardware cycles to software clocks or from kernel-inclusive to user-only sampling. Feature detection mutates global flags and must preserve `errno` carefully.

## Test Signals

Useful tests include perf attr tests via `PERF_TEST_ATTR`, event open smoke tests for system-wide and per-thread modes, vanished-thread handling, group read with `PERF_FORMAT_ID`, sample parser tests for every sample bit and malformed sizes, cross-endian perf.data parsing, branch stack hardware-index/counter coverage, hybrid PMU stat output, precise-IP fallback, paranoid/EACCES fallback, BPF attachment, cgroup events, and old-kernel missing-feature probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/evsel.h

## Purpose

`evsel.h` declares perf's higher-level event-selector object and its public utility API. It wraps libperf `struct perf_evsel` with perf-tool state used by parsing, recording, counting, reporting, BPF integration, metrics, grouping, and sample decoding.

## Important APIs, Types, and Functions

The central type is `struct evsel`. It embeds `struct perf_evsel core` and adds parsed names, tracepoint metadata, filters, config terms, metric links, count storage, stats, flags, BPF counter state, PMU pointer, fallback state, start-time storage for tool PMUs, and branch-counter metadata. `struct perf_missing_features` records kernel/PMU ABI capabilities that have been probed or disabled. The header exposes constructors/destructors, config/open/read/parse APIs, sample-bit helpers, group iteration macros, name/metric helpers, tracepoint field helpers, fallback/error helpers, leader/group utilities, hybrid and AUX helpers, and PMU config get/set helpers.

## Control Flow

Consumers typically parse an event into an `evsel`, call `evsel__config`, open it with CPU/thread maps, optionally store IDs into an evlist, read counters or parse records, and finally close/delete it. The inline helpers keep sample-bit mutations synchronized with `sample_size`/ID positions through the C implementation. Group iteration macros rely on contiguous evlist ordering and matching leader pointers.

## State and Persistence Behavior

The header defines ownership boundaries that implementations must respect: copied strings in the anonymous parse-state struct, list-owned config terms, refcounted cgroups/maps, BPF objects/fds, count arrays, optional per-package hashmaps, and a tool-specific `priv` pointer guarded by a global destructor. Many booleans are durable per-selector policy, such as `tracking`, `supported`, `disabled`, `skippable`, `forced_leader`, and fallback markers.

## Dependencies and Integration Points

It depends on Linux perf ABI headers, libperf internal/public evsel headers, CPU/thread maps, PMU metadata, symbol configuration, traceevent types when available, BPF skeleton forward declarations, `hashmap`, stats, record options, and target definitions. It is included across perf util and builtin code as the primary contract for event selection.

## Risks and Edge Cases

Because the struct is large and manually cloned/freed, any new owned field must be added to clone and teardown logic. The anonymous struct comments explicitly warn parse-time fields need clone handling. Group macros assume list layout; misuse outside an evlist can walk invalid memory. The pointer/integer mix around `hashmap` and BPF state requires precise ownership discipline.

## Test Signals

Header-level regressions show up as compile failures in perf builtins, clone/free leaks, group iteration errors, and sample parser mismatches. Tests should cover adding config-term types, struct-size extension through `evsel__object_config`, event grouping, BPF/bperf predicates, and synthesized sample-type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_config.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/evsel_config.h

## Purpose

`evsel_config.h` defines per-event configuration terms parsed from event modifiers and later applied by `evsel__config`. It is the data contract between parse-events code and the event-selector configuration path.

## Important APIs, Types, and Functions

`enum evsel_term_type` enumerates supported modifiers: period, frequency, time, callgraph, stack size, inherit, max stack/events, overwrite, driver config, branch stack, percore, AUX output/action/sample size, user-changed `config` through `config4`, and `ratio-to-prev`. `struct evsel_config_term` stores the term type, whether a string must be freed, a union value, a `weak` override flag, and list linkage. `evsel__get_config_term` wraps `__evsel__get_config_term` with enum-token construction.

## Control Flow

Parser code allocates these terms and appends them to `evsel::config_terms`. `evsel__apply_config_terms` walks the list, mutates `perf_event_attr`, configures callgraphs and branch stacks, applies weak override semantics, and records user-changed PMU config bits so later defaults do not overwrite explicit user settings.

## State and Persistence Behavior

Each term persists until `free_config_terms` or `evsel__exit`. String-valued terms use `free_str` to distinguish owned strings from borrowed values. The `weak` flag lets defaults be superseded by global user options without losing the parsed term object.

## Dependencies and Integration Points

The header depends on list heads, Linux integer types, and booleans. It integrates directly with parse-events, PMU format packing, callchain parsing, AUX trace configuration, and `evsel.c` clone/free logic.

## Risks and Edge Cases

Adding a term requires updates in parsers, clone/free paths, and `evsel__apply_config_terms`; otherwise modifiers may parse but never take effect or may leak. The union requires the selected member to match `type`. Incorrect `free_str` handling causes leaks or invalid frees.

## Test Signals

Tests should parse events with every modifier, clone selectors before opening, then verify resulting `perf_event_attr` fields, config-term lifetime under failure paths, and weak override behavior for global period/frequency options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.c

## Purpose

`evsel_fprintf.c` formats event selectors and sample symbol/callchain data for text output. It supports compact event printing, verbose attribute dumps, grouped-event rendering, tracepoint field listing, and symbolized sample/callchain lines.

## Important APIs, Types, and Functions

`evsel__fprintf` prints either a single event or a full group depending on `struct perf_attr_details`. It can append verbose `perf_event_attr` fields or sample frequency/period. `sample__fprintf_callchain` walks a committed `callchain_cursor` and prints IPs, symbols, DSO names/offsets, source lines, arrows, inline markers, and stop-list behavior. `sample__fprintf_sym` delegates to callchain printing when a cursor is present or prints one resolved address location.

## Control Flow

Formatting starts with `comma_fprintf`, which inserts the initial colon and later commas for attribute-like suffixes. Group mode prints only from leaders and iterates members. Trace-field mode validates the event is a tracepoint and walks libtraceevent format fields. Callchain output commits the cursor, loops nodes, skips ignored symbols if requested, maps IPs through maps, resolves symbols/source lines, stops on configured backtrace stop symbols, and advances the cursor.

## State and Persistence Behavior

The file does not own long-lived state. It reads `evsel`, `perf_sample`, callchain cursor, map, symbol, DSO, and strlist state owned elsewhere. Output persistence is only the bytes written to the caller-provided `FILE *`.

## Dependencies and Integration Points

It integrates with event naming, perf-event attribute formatting, traceevent formats, callchain cursors, maps, symbols, DSOs, source-line lookup, address locations, and strlists. It is a presentation layer used by tools such as `perf evlist`, `perf script`, and report-like flows.

## Risks and Edge Cases

Null cursors print an explicit memory warning. Symbol/map pointers may be absent, so unknown-address formatting flags matter. Trace-field printing depends on tracepoint format availability. Callchain cursor state must be prepared by callers; otherwise no frames are printed. Oneline mode changes separators and newline behavior.

## Test Signals

Tests should compare output for grouped and ungrouped events, verbose/frequency modes, tracepoint field mode, callchains with and without symbols/maps/source lines, ignored-symbol skip lists, deferred-callchain cookies, and oneline versus multiline formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.h

## Purpose

`evsel_fprintf.h` declares the text-formatting contract for event selectors and sample symbol/callchain output.

## Important APIs, Types, and Functions

`struct perf_attr_details` selects frequency, verbose, event group, forced, and trace-field output modes. `EVSEL__PRINT_*` bit flags control IP, symbol, DSO, symbol offset, DSO offset, one-line output, source lines, unknown-address handling, callchain arrows, and ignored-frame skipping. The header declares `evsel__fprintf`, `sample__fprintf_callchain`, `sample__fprintf_sym`, the attribute callback type, and `perf_event_attr__fprintf`.

## Control Flow

Callers construct `perf_attr_details` or print-option bitmasks and pass the relevant `evsel`, `perf_sample`, `addr_location`, callchain cursor, stop list, and output stream. The implementation performs all formatting and returns the printed character count.

## State and Persistence Behavior

No state is stored in the header. The option structs and bit flags define transient formatting policy; output is persisted only through the supplied `FILE *`.

## Dependencies and Integration Points

It forward-declares perf sampling, address-location, callchain, and strlist types so reporting and script code can include the API without pulling full implementations. It also exposes the generic perf-event-attribute formatter callback contract used by verbose event output.

## Risks and Edge Cases

The print flags are bit positions, so new flags must avoid collisions. `perf_attr_details.force` is declared here but not used by the inspected implementation, so consumers should verify intended semantics before relying on it.

## Test Signals

Compile coverage across report/script/evlist users, golden-output tests for each flag combination, and ABI checks for new print flags are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evswitch.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/evswitch.c

## Purpose

`evswitch.c` implements event-driven filtering windows for perf output. It lets a tool discard samples until a named switch-on event appears and resume discarding when a named switch-off event appears.

## Important APIs, Types, and Functions

`evswitch__init` resolves `on_name` and `off_name` into `struct evsel *` objects from an evlist and initializes starting discard state. `evswitch__discard` decides whether a sample/event for a given evsel should be suppressed and toggles state when on/off events are seen. `evswitch__fprintf_enoent` prints missing-event diagnostics.

## Control Flow

Initialization first resolves the on event; if present, the switch starts in discarding mode. It then resolves the off event. Runtime filtering has two phases: while discarding, all events are dropped until the on event appears; while accepting, events pass until the off event appears. The switch marker event itself is dropped unless `show_on_off_events` is set.

## State and Persistence Behavior

The mutable state is `evswitch->discarding` plus resolved `on`/`off` pointers. Names are borrowed option strings. No state is persisted to disk.

## Dependencies and Integration Points

It depends on evlists and evsels, especially `evlist__find_evsel_by_str`. The option surface is declared in the header and is intended for perf commands that support `--switch-on`, `--switch-off`, and `--show-on-off-events`.

## Risks and Edge Cases

Missing names fail initialization with `-ENOENT`. Duplicate event names depend on evlist lookup semantics. If only `off` is configured, collection starts enabled and turns off at the first off event. Marker visibility can surprise tests because switching events are suppressed by default.

## Test Signals

Tests should cover on-only, off-only, on/off pairs, missing event names, duplicate names, marker visibility, and streams where on/off events occur multiple times.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evswitch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evswitch.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/evswitch.h

## Purpose

`evswitch.h` declares the small state machine used to gate perf event output between named on/off events.

## Important APIs, Types, and Functions

`struct evswitch` stores resolved `on` and `off` evsels, option-provided names, current `discarding` state, and `show_on_off_events`. `evswitch__init` resolves names against an evlist. `evswitch__discard` evaluates and updates the filter state. `OPTS_EVSWITCH` expands to command-line options for `--switch-on`, `--switch-off`, and `--show-on-off-events`.

## Control Flow

Perf commands embed an `evswitch`, include `OPTS_EVSWITCH` in option parsing, call `evswitch__init` after evlist construction, and then call `evswitch__discard` for each event to decide whether to display/process it.

## State and Persistence Behavior

All state is in memory for one command invocation. The header does not define ownership transfer for the name strings; they are typical option-parser storage.

## Dependencies and Integration Points

It forward-declares `evsel` and `evlist`, includes boolean and stdio types, and relies on the perf option macro API being available where `OPTS_EVSWITCH` is used.

## Risks and Edge Cases

The option macro assumes `OPT_STRING` and `OPT_BOOLEAN` are visible at expansion sites. Tools must initialize the struct to zero before option parsing or stale pointers/state can affect filtering.

## Test Signals

Compile tests for option users and runtime switch filtering tests provide coverage. Zero-initialization tests are useful because the state machine has no separate constructor beyond `evswitch__init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/evswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/expr.c

## Purpose

`expr.c` backs perf metric expression parsing. It manages expression contexts, event ID maps, metric references, formula evaluation, ID discovery, literal reads, event-existence checks, and CPUID string comparisons.

## Important APIs, Types, and Functions

The hidden `struct expr_id_data` represents either a numeric event value, a referenced metric expression, or a resolved referenced metric value. Public APIs include `expr__ctx_new`, `expr__ctx_clear`, `expr__ctx_free`, `expr__add_id`, `expr__add_id_val`, `expr__add_id_val_source_count`, `expr__add_ref`, `expr__get_id`, `expr__resolve_id`, `expr__parse`, `expr__find_ids`, `expr__get_literal`, `expr__has_event`, and `expr__strcmp_cpuid_str`. Hashmap helpers implement string-keyed ID maps.

## Control Flow

Contexts hold an ID hashmap and scanner options. Evaluation calls `__expr__parse`, initializes the flex scanner with `ctx->sctx`, scans the expression string, invokes the bison parser in compute or evaluate mode, then destroys scanner buffers. ID resolution finds value entries directly or recursively parses referenced metric expressions, marking references as `REF_VALUE` to cache results. ID discovery parses with `compute_ids=true` and optionally removes one excluded ID.

## State and Persistence Behavior

Expression state is per `expr_parse_ctx`. The hashmap owns duplicated keys and allocated `expr_id_data` values. Metric references borrow `metric_ref` strings from PMU event metadata but store a duplicated hashmap key. Numeric duplicate inserts accumulate values and source counts. Scanner context stores runtime substitution, test mode, system-wide mode, and requested CPU list.

## Dependencies and Integration Points

It integrates with generated `expr-bison` and `expr-flex`, perf metric groups, evlist parsing, tool PMU events/literals, SMT/header helpers, PMU parsing, CPUID helpers, debug logging, and the generic hashmap. Metric code uses it to determine required events and compute final derived metric values.

## Risks and Edge Cases

Recursive metric references can fail if a referenced expression is invalid or cycles back before a value is available. Duplicate value insertion accumulates, which is intentional for aggregation but risky if callers expected replacement. `expr__has_event` creates a temporary evlist and rewrites `@` to `/`; malformed encodings return false or NAN. Literal reads can fail depending on platform/tool PMU support. Memory ownership differs between value IDs and borrowed metric expressions.

## Test Signals

Tests should cover arithmetic, conditionals, ID discovery, duplicate aggregation and `source_count`, referenced metrics, literal tool PMU reads, `has_event`, CPUID comparisons, runtime `?` substitutions, missing IDs, invalid expressions, and context clear/free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/expr.h

## Purpose

`expr.h` declares the public context and API for perf metric expression evaluation and ID discovery.

## Important APIs, Types, and Functions

`struct expr_scanner_ctx` carries scanner/runtime options: requested CPU list, runtime integer substitution, system-wide mode, and test mode. `struct expr_parse_ctx` contains the ID hashmap and scanner context. The header declares ID-map lifecycle, context lifecycle, ID insertion/deletion/value/reference APIs, subset checks, ID resolution, parsing, ID discovery, value/source-count accessors, literal evaluation, event-existence checks, and CPUID string comparisons.

## Control Flow

Metric callers create a context, add values or references, call `expr__find_ids` to discover needed events or `expr__parse` to compute a value, then clear or free the context. Scanner context fields must be set before parsing when expressions use runtime literals, system-wide tool PMUs, or test behavior.

## State and Persistence Behavior

The context owns its hashmap and `user_requested_cpu_list`. ID data is opaque to callers except through accessor functions. `ids__union` consumes and frees its input maps while returning the merged result, a notable ownership contract.

## Dependencies and Integration Points

It forward-declares `struct hashmap` and `struct metric_ref` to keep dependencies light. Implementations integrate with generated lexer/parser code and perf metric/event parsing.

## Risks and Edge Cases

Callers must not inspect opaque `expr_id_data` directly. Passing maps to `ids__union` transfers ownership. Context clear/free must match any inserted IDs or references to avoid leaks.

## Test Signals

Compile coverage for metric code, ownership tests around `ids__union`, context lifecycle tests, and parser golden tests for expressions using scanner context are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.l -->
# sources/distributed-fs/ceph-client/tools/perf/util/expr.l

## Purpose

`expr.l` is the flex scanner for perf metric expressions. It tokenizes numbers, event IDs, literals, keywords, operators, and punctuation for the bison parser.

## Important APIs, Types, and Functions

The scanner uses prefix `expr_`, reentrant mode, and bison bridge mode. Helpers include `value` for numeric conversion, `literal` for `#...` tool PMU literals, `nan_value`, `normalize`, and `str`. Tokens include `D_RATIO`, `MAX`, `MIN`, `IF`, `ELSE`, `SOURCE_COUNT`, `HAS_EVENT`, `STRCMP_CPUID_STR`, `NUMBER`, `ID`, `LITERAL`, and operator characters.

## Control Flow

For each token, the scanner writes semantic data to `YYSTYPE`: doubles for numbers/literals and normalized duplicated strings for IDs. `normalize` handles backslash escaping and replaces `?` with the runtime integer from `expr_scanner_ctx`. The ID pattern permits `@` so PMU event names can use `@` as a division-safe stand-in for `/`. Unknown characters are ignored by the `.` rule.

## State and Persistence Behavior

The scanner uses `expr_scanner_ctx` as extra state. ID strings are allocated and later freed by parser destructors or semantic handlers. Literal evaluation may read live tool PMU data unless test mode converts unrecognized literals to `1`.

## Dependencies and Integration Points

It includes `expr.h`, generated bison headers, Linux compiler annotations, errno, and math support. It is generated into `expr-flex` and called by `expr.c`.

## Risks and Edge Cases

`normalize` mutates strings in place; callers must pass owned storage. The number regex supports lowercase `e-` exponents but not `E` or explicit `e+`. The catch-all ignore rule can hide unexpected characters until the parser fails or produces surprising tokens. Literal failures are fatal outside test mode.

## Test Signals

Lexer tests should cover escaped symbols, `?` runtime substitution, PMU `@` names, keywords versus IDs, NaN, literals in normal/test mode, malformed numbers, and ignored punctuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.y -->
# sources/distributed-fs/ceph-client/tools/perf/util/expr.y

## Purpose

`expr.y` is the bison grammar and evaluator for perf metric expressions. It supports arithmetic, comparisons, boolean-like operators, ternary-style `if/else`, min/max, denominator-safe ratio, source-count queries, event existence checks, CPUID string checks, literals, and ID collection.

## Important APIs, Types, and Functions

The parser receives `double *final_val`, `struct expr_parse_ctx *ctx`, `bool compute_ids`, and the scanner. Semantic values include numbers, strings, and an `{ids, val}` pair. Helpers include `expr_error`, `is_const`, `union_expr`, `handle_id`, and the `BINARY_OP` macro. `BOTTOM` is represented by `NAN` during ID discovery to mean a value depends on runtime event data.

## Control Flow

In evaluation mode, IDs resolve to numeric values through `expr__resolve_id`; constants compute directly; missing values propagate `NAN`. In ID-discovery mode, constants are folded and non-constant branches union required ID sets. Conditional expressions can avoid collecting unused branches when the condition is constant, while non-constant conditions union condition and both branch IDs as needed. Division by zero yields `NAN`; `d_ratio` returns `0` for constant-zero denominators.

## State and Persistence Behavior

Parser reductions own and free ID strings and temporary ID hashmaps through bison destructors and explicit `ids__free` calls. At the `start` rule, discovered IDs are unioned into `ctx->ids`, transferring ownership. No persistent parser state remains after parsing.

## Dependencies and Integration Points

It depends on `expr.h`, generated scanner hooks, debug logging, math classification, and ID-map helpers. Metric-group code relies on the grammar both to compute values and to know which perf events must be scheduled.

## Risks and Edge Cases

Using `NAN` as both invalid value and bottom marker makes mode-specific logic delicate. Boolean operators intentionally fold constants and may not behave like C bitwise operators for nonzero doubles. Modulo casts operands to `long`. Division and modulo by zero differ: division returns `NAN`, modulo aborts parsing. ID-discovery correctness depends on freeing unused branch ID sets.

## Test Signals

Golden parser tests should cover precedence, ternary branches, constant folding in compute-IDs mode, boolean operators, `d_ratio`, division/modulo zero, min/max, `source_count`, `has_event`, CPUID checks, literals, and memory-checker runs for parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/expr.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/find-map.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/find-map.c

## Purpose

`find-map.c` provides a small helper to locate an executable private mapping for a named file in the current process. It is likely included directly by tests or JIT-related code rather than compiled as a standalone utility.

## Important APIs, Types, and Functions

The file defines `static int find_map(void **start, void **end, const char *name)`. It opens `/proc/self/maps`, scans fixed-size lines, parses mapping start/end addresses only for `r-xp` private executable mappings, and compares the pathname suffix area with the requested name.

## Control Flow

The function opens maps, reads until found or EOF, skips nonmatching permissions or malformed lines, uses `%n` to locate the pathname offset after parsed fields, and sets `found` when the name matches. It closes the file and returns `0` when found, `1` when not found, and `-1` when maps cannot be opened.

## State and Persistence Behavior

It has no persistent state. Results are returned through `start` and `end`, which hold the most recent parsed matching mapping on success.

## Dependencies and Integration Points

The source relies on libc I/O and `/proc/self/maps`. Because there are no includes in the file itself, it is probably included into another C file that supplies declarations for `FILE`, `PATH`, `fopen`, `fprintf`, `sscanf`, `strncmp`, and `strlen`.

## Risks and Edge Cases

The 128-byte line buffer can truncate long map paths. The name comparison uses `strncmp` with `strlen(name)`, so it matches prefixes rather than full path basenames. It only considers private executable mappings, not shared executable mappings. Return value `!found` is easy to misread.

## Test Signals

Tests should map or load a known executable object, verify returned bounds, cover missing names and inaccessible procfs, and include long path/prefix collision cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/find-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/fncache.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/fncache.c

## Purpose

`fncache.c` caches whether file names are readable to avoid repeated `access(R_OK)` calls in paths that may query the same files many times.

## Important APIs, Types, and Functions

The public API is `file_available(const char *name)`. Static helpers initialize a global hashmap once, hash and compare string keys, look up cached booleans, and update the cache with duplicated file-name keys.

## Control Flow

`file_available` checks the cache first. On miss, it calls `access(name, R_OK)`, stores the boolean result in the hashmap with `hashmap__set`, frees any replaced key, and returns the result. `pthread_once` lazily initializes the global map.

## State and Persistence Behavior

The global `fncache` persists for the process lifetime and has no eviction. It owns duplicated key strings but stores boolean values directly as long integers through the hashmap macros. The comment notes there is no LRU and callers should only use it when the input space is bounded.

## Dependencies and Integration Points

It depends on pthread once initialization, libc allocation/string/access, Linux compiler annotations, `fncache.h`, and the generic hashmap. It is a utility for perf code that probes many possible files or debug/source paths.

## Risks and Edge Cases

The underlying hashmap is documented as non-thread-safe. `pthread_once` protects initialization only, not concurrent lookups/updates. Results can become stale if files are created, removed, or permissions change after caching. Unbounded names can grow memory for the lifetime of perf.

## Test Signals

Tests should cover cache hits/misses, permission-readable versus missing files, replaced keys, stale-result behavior after file changes, and threaded callers if the intended use ever crosses threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/fncache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/fncache.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/fncache.h

## Purpose

`fncache.h` declares the filename availability cache API.

## Important APIs, Types, and Functions

It exposes `bool file_available(const char *name);` behind the `_FCACHE_H` include guard.

## Control Flow

Callers pass a path-like string and receive whether it was readable according to the cache-backed implementation.

## State and Persistence Behavior

The header has no state. The implementation maintains process-global cache state.

## Dependencies and Integration Points

The header assumes `bool` is available before inclusion or through surrounding build context, because it does not include `<stdbool.h>`. It is paired with `fncache.c`.

## Risks and Edge Cases

The missing direct `stdbool.h` include can make isolated inclusion fragile. The guard name uses `FCACHE`, not `FNCACHE`, which is harmless but inconsistent with the file name.

## Test Signals

Compile tests should include this header both after and before common perf headers to verify `bool` visibility assumptions. Runtime behavior is covered by `fncache.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/fncache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ftrace.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/ftrace.h

## Purpose

`ftrace.h` defines perf's ftrace command state and the optional BPF latency helper API used for function tracing and latency profiling.

## Important APIs, Types, and Functions

`struct perf_ftrace` stores the evlist, target, tracer name, filter/notrace/graph filter lists, event-pair list, profile hash, per-CPU buffer size, inherit/use-nsec options, histogram bucket settings, latency bounds, empty-bucket hiding, graph depth, stack/IRQ/args/retval/retaddr/nosleep/noirq/verbose/thresh/tail graph options, and BPF profile state. `struct filter_entry` stores flexible-array filter names. `NUM_BUCKET` defines the latency histogram bucket count. BPF helper prototypes are real when `HAVE_BPF_SKEL` is enabled and inline `-1` stubs otherwise.

## Control Flow

Perf ftrace code fills `perf_ftrace` from command options, configures kernel ftrace or BPF latency tracing, runs tracing, reads latency buckets/stats, then cleans up. The header itself only provides state layout and compile-time dispatch for BPF skeleton availability.

## State and Persistence Behavior

All struct fields are runtime command state. Lists hold filter entries and event pairs. `profile_hash` likely stores per-function profiling data. The fallback inline BPF functions do not mutate state and signal unsupported operation with `-1`.

## Dependencies and Integration Points

It depends on Linux list heads, perf target handling, evlists, hashmaps, stats, and optional BPF skeleton support. It is used by ftrace builtin/util implementation files.

## Risks and Edge Cases

There is a typo forward declaration `struct hashamp;` while the field uses `struct hashmap`; this is harmless if another declaration is visible but suspicious. Callers must initialize list heads and defaults before use. Builds without BPF skeletons must handle `-1` returns cleanly.

## Test Signals

Compile tests with and without `HAVE_BPF_SKEL`, option initialization tests, ftrace graph option smoke tests, latency histogram bucket tests, and BPF unsupported-path tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/genelf.c

## Purpose

`genelf.c` writes a synthetic ELF shared object for JITed code captured by perf jitdump support. The generated ELF contains executable code, symbol/string tables, a GNU build ID, optional unwind sections, and optional DWARF debug info.

## Important APIs, Types, and Functions

The public function is `jit_write_elf`. Static data includes the section-name string table, a two-entry symbol table, and a build-ID note. `jit_add_eh_frame_info` adds `.eh_frame` and `.eh_frame_hdr` sections. `blake2s_update_tagged` feeds tagged code/symbol/string inputs into the build-ID hash to avoid tuple ambiguity.

## Control Flow

`jit_write_elf` initializes libelf, starts an ELF write on the fd, creates ELF/program headers, writes a loadable `.text` section, hashes code, optionally adds unwind sections after aligned text, creates `.shstrtab`, `.symtab`, `.strtab`, computes and writes `.note.gnu.build-id`, and either delegates DWARF section creation to `jit_add_debug_info` or calls `elf_update` directly. Cleanup always calls `elf_end` and frees the symbol string table.

## State and Persistence Behavior

The output ELF persists on the provided fd. Most state is local, but `symtab[1]` and global `bnote` are mutated per call, making concurrent calls unsafe without external serialization. Build IDs are deterministic over code, symbol table, and symbol string data.

## Dependencies and Integration Points

It depends on libelf, BLAKE2s, `genelf.h` architecture macros, jitdump format definitions, optional libdw/DWARF support, and Linux alignment/compiler helpers. Perf uses the generated ELF so later symbolization/debug lookup can treat JIT code like a normal DSO.

## Risks and Edge Cases

Section indexes and `sh_link` values differ depending on optional unwind/debug sections and are easy to break. Pointer arithmetic on `void *` relies on compiler extensions. Build ID excludes unwind/debug data, so two files with same code/symbols but different debug data share a build ID. Global mutable `symtab`/`bnote` can race. Error paths use warnings but return only `-1`.

## Test Signals

Tests should generate ELF files with code only, with unwind data, with debug entries, and with both optional features; inspect them with `readelf`, verify executable `.text`, symbol table, build ID determinism, section links, unwind section addresses, and perf symbolization of JIT samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/genelf.h

## Purpose

`genelf.h` declares JIT ELF generation APIs and selects libelf type aliases/macros for the build architecture.

## Important APIs, Types, and Functions

It declares `jit_write_elf` and, when libdw support is enabled, `jit_add_debug_info`. It defines `GEN_ELF_ARCH`, `GEN_ELF_CLASS`, and `GEN_ELF_ENDIAN` based on compiler architecture/endian macros. It aliases libelf functions and types to 32-bit or 64-bit variants (`elf_newehdr`, `Elf_Ehdr`, `Elf_Sym`, etc.) and defines `GEN_ELF_TEXT_OFFSET` as the aligned location after ELF and program headers.

## Control Flow

Compilation selects one architecture branch or fails with `#error "unsupported architecture"`. The implementation then uses the normalized aliases so `genelf.c` can be mostly architecture-neutral.

## State and Persistence Behavior

The header stores no runtime state. It determines the class, machine type, endian encoding, and text offset of all generated JIT ELF files at compile time.

## Dependencies and Integration Points

It depends on libelf constants/types being visible, architecture compiler macros, and Linux `round_up`. It is included by `genelf.c` and `genelf_debug.c`.

## Risks and Edge Cases

Unsupported or newly added architectures fail the build until mapped. Cross-generation for a different target architecture is not supported; output follows the perf build host. `GEN_ELF_TEXT_OFFSET` depends on selected ELF type aliases.

## Test Signals

Build coverage across supported architectures, endian checks, generated ELF header inspection, and text-offset validation catch most regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf_debug.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/genelf_debug.c

## Purpose

`genelf_debug.c` adds minimal DWARF debug sections to generated JIT ELF files. It converts jitdump debug entries into `.debug_line`, `.debug_info`, and `.debug_abbrev` data.

## Important APIs, Types, and Functions

The public function is `jit_add_debug_info`. Static helpers implement a growable `buffer_ext`, LEB128 emission, DWARF opcode emission, line-table state transitions, compilation-unit creation, abbreviation creation, and debug-entry preprocessing. Key internal structures mirror DWARF line and compilation-unit headers.

## Control Flow

`jit_add_debug_info` initializes three dynamic buffers, calls `jit_process_debug_info`, then creates three libelf sections and assigns their buffers as ELF data before `elf_update`. `jit_process_debug_info` normalizes debug-entry addresses relative to the original code address, appends one compilation unit pointing at the current line-table offset, emits line-table rows from debug entries using special opcodes when possible, and emits a minimal compile-unit abbreviation.

## State and Persistence Behavior

The generated DWARF bytes persist in the ELF being written. Temporary buffers grow by doubling and are freed after `elf_update`. The function mutates incoming `debug_entry` addresses in place by subtracting `code_addr`, so callers should not expect the debug array to remain unchanged.

## Dependencies and Integration Points

It depends on libelf, DWARF constants, jitdump debug-entry layout, `genelf.h` section-name offsets/type aliases, Linux packed/compiler helpers, and zalloc. It is called from `genelf.c` when libdw support and debug entries are available.

## Risks and Edge Cases

In-place address normalization is a notable side effect. The implementation targets simple DWARF2 32-bit unit lengths and comments that >4GB debug data is unsupported. Several `buffer_ext_add` calls ignore allocation failures. Filename handling has a repeated-name marker convention, and line opcode range choices are static guesses. The `.debug_abbrev` section comment labels `sh_name = 76` as `.debug_info`, but the offset is `.debug_abbrev`.

## Test Signals

Tests should feed multiple files/lines, repeated-name markers, large buffers, and nonmonotonic addresses; validate with `readelf --debug-dump`, ensure perf resolves source lines for JIT samples, and run allocation-failure or sanitizer tests for buffer growth paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/genelf_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hashmap.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hashmap.c

## Purpose

`hashmap.c` implements a small generic, non-thread-safe hashmap used by perf/libbpf-derived utility code. It stores long-sized keys and values, including pointer values through wrapper macros in the header.

## Important APIs, Types, and Functions

It implements `hashmap__init`, `hashmap__new`, `hashmap__clear`, `hashmap__free`, `hashmap__size`, `hashmap__capacity`, `hashmap_insert`, `hashmap_find`, and `hashmap_delete`. Internal helpers manage chained entries, growth thresholds, rehashing, and bucket-chain search. It starts at 4 buckets and grows when the projected load exceeds roughly 75%.

## Control Flow

Insert computes a bucket using the current capacity bits, finds an existing key unless append mode is requested, performs add/set/update/append semantics, grows and rehashes as needed, then prepends a new entry. Set/update can return old key/value to callers for ownership cleanup. Find and delete compute the bucket and walk the chain. Clear frees entries and bucket storage.

## State and Persistence Behavior

The hashmap owns only entry nodes and bucket arrays. Key/value payload ownership stays with callers, which is why set/delete return old values. `hashmap__free` tolerates NULL and encoded error pointers. Bucket order changes on growth because entries are prepended into new chains.

## Dependencies and Integration Points

It depends on caller-provided hash/equality callbacks, Linux `ERR_PTR` helpers, errno values, and the iteration macros from `hashmap.h`. `#pragma GCC poison` prevents accidental use of kernel typedefs and `reallocarray`.

## Risks and Edge Cases

The implementation is not thread-safe. `hash_bits` with zero capacity bits maps all entries to bucket zero until growth; insert recalculates after growth. Pointer casting relies on long-sized pointers. Append mode creates multimaps where `find` returns the newest matching entry. Callers must free payloads before or after clear as appropriate.

## Test Signals

Tests should cover add/set/update/append semantics, old key/value return, delete, growth/rehash, iteration safe under deletion, multimap key iteration, NULL/error free, and pointer/integer macro usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hashmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hashmap.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hashmap.h

## Purpose

`hashmap.h` declares the generic hashmap API and iteration macros used by perf utility code. It originated from libbpf-style helpers and supports integer or pointer keys/values through long-sized storage.

## Important APIs, Types, and Functions

It defines `hash_bits`, `str_hash`, hash/equality callback typedefs, `struct hashmap_entry`, `struct hashmap`, `enum hashmap_insert_strategy`, lifecycle APIs, size/capacity queries, insert/set/add/update/append/delete/find wrappers, and iteration macros for all entries, safe deletion, and entries for one key. `hashmap_cast_ptr` uses `_Static_assert` to verify old-key/value pointer sizes.

## Control Flow

Callers initialize a map with callbacks, then use wrappers such as `hashmap__add`, `hashmap__set`, or `hashmap__find`. Iteration macros expand into nested bucket/chain loops. Key-specific iteration computes the bucket from the supplied key and filters by equality.

## State and Persistence Behavior

The map tracks callbacks, callback context, bucket array, capacity, capacity bits, and current size. Entry keys/values are stored as `long` or pointer unions; ownership of pointed-to data is external.

## Dependencies and Integration Points

The header depends on standard boolean/size/limits headers and is used by expression IDs, filename cache, evsel per-package masks, ftrace profile hashes, and other utility structures needing lightweight maps.

## Risks and Edge Cases

It is explicitly non-thread-safe. Pointer/integer polymorphism is convenient but can hide ownership and signedness mistakes. The comment typo `hasmap_entry` is documentation-only. `hashmap__for_each_key_entry` requires valid callbacks and handles an unallocated bucket array by starting at NULL.

## Test Signals

Compile tests should exercise integer and pointer keys/values with the static assertions. Runtime tests should cover C-string hash users, custom equality, all iteration macros, multimap append behavior, and empty-map key iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hashmap.h -->
