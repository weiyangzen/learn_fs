# subset-b-006745 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/intel_metrics.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/intel_metrics.py
Purpose: Generates Intel-specific perf metric JSON for one x86 model. It builds a hierarchy of low-power, branch, context-switch, FPU, ILP, L2/cache, load/store, and uncore memory/UPI metrics by composing the expression objects from `metric.py`. The command-line interface accepts `model`, `events_path`, and `-metricgroups`, loads model events from `events_path/x86/<model>/`, and prints either full metric JSON or metric-group descriptions.

Important APIs/types/functions: The public surface is a set of metric factory functions: `Idle`, `Rapl`, `Smi`, `Tsx`, `IntelBr`, `IntelCtxSw`, `IntelFpu`, `IntelIlp`, `IntelL2`, `IntelMissLat`, `IntelMlp`, `IntelPorts`, `IntelSwpf`, `IntelLdSt`, `UncoreCState`, `UncoreDir`, `UncoreMem`, `UncoreMemBw`, `UncoreMemSat`, and `UncoreUpiBw`. Each returns a `Metric`, `MetricGroup`, or `None` when prerequisite events are absent. It relies on `Event` fallback arguments, `Select`, `MetricRef`, `Literal`, `source_count`, `has_event`, `d_ratio`, `max`, and `MetricConstraint` to produce runtime-safe formulas.

Control flow: `main()` validates the event directory, calls `LoadEvents`, then constructs one root `MetricGroup` from `Cycles()` plus all Intel factories. Individual factories probe event availability through `Event(...)` inside `try/except` blocks and skip unsupported feature groups. Some functions inspect JSON files directly, such as `IntelPorts()` reading `pipeline.json` and `UncoreMemBw()` reading `uncore-memory.json`, to synthesize groups from matching event names.

State and persistence: State is process-local: `_args` holds parsed CLI options and `interval_sec` is the reusable `duration_time` event expression. No files are written; stdout is the generated artifact. The script mutates some `Event.name` fields to add filters or aliases after validation, which makes generated expressions model-specific.

Dependencies and integration points: This is part of perf's PMU event build pipeline and feeds JSON consumed by `jevents.py`. It depends on neighboring `common_metrics.py` and `metric.py`, plus model event JSON under `arch/x86`. Generated metrics integrate with perf's metric parser and runtime PMU event lookup.

Risks: Several broad `except:` blocks intentionally tolerate missing model events but can hide malformed JSON or expression errors. There are apparent typo hazards where code references `args.model` instead of `_args.model` in some branches, which would only surface when those branches execute. Duplicate metric names appear in some L2 groups, so downstream deduplication/order behavior matters. Event-name mutation after construction must preserve escaping expected by `metric.Event.ToPerfJson`.

Test signals: Main signals are `metric_test.py`, perf PMU event generation tests, and running this script against representative x86 model directories with and without `-metricgroups`. Useful regression checks include JSON validity, no missing event exceptions for supported models, and stable metric-group names expected by perf list/stat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/intel_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py
Purpose: Converts PMU event and metric JSON trees into compact generated C tables and lookup routines used by perf at runtime. It folds event strings into one large C string, emits per-PMU compact arrays, generates CPU/sys mapping tables, and writes C functions for event/metric iteration and lookup.

Important APIs/types/functions: `BigCString` collects, deduplicates, suffix-folds, and offsets string payloads. `JsonEvent` normalizes JSON dictionaries into event/metric fields, translates JSON units and constraints to perf enum encodings, resolves architecture-standard events, canonicalizes event codes, and builds compact C string records. Processing functions include `read_json_events`, `preprocess_arch_std_files`, `preprocess_one_file`, `process_one_file`, `print_pending_events`, `print_pending_metrics`, `print_mapping_table`, `print_system_mapping_table`, and `print_metricgroups`.

Control flow: `main()` parses `arch`, `model`, `starting_dir`, and optional output file. It chooses architecture directories, preloads architecture-standard events, walks the tree twice, computes the shared big string between passes, then emits generated C. The first walk gathers all strings and metric-group descriptions; the second walk accumulates events/metrics per leaf model directory and flushes tables when model leaves or sys leaves are encountered. Mapping generation reads each architecture `mapfile.csv` and connects cpuid regex rows to emitted event and metric table symbols.

State and persistence: Global lists and maps track generated event tables, sys event tables, metric tables, pending table rows, architecture-standard event aliases, metric-group descriptions, and the shared `BigCString`. Persistence is the generated C source written to stdout or the CLI output file. Runtime state in the generated C includes static caches in `map_for_cpu()` for the last CPU and cpuid lookup.

Dependencies and integration points: The script imports `metric.py` to parse and rewrite `MetricExpr` fields, consumes PMU JSON under `tools/perf/pmu-events/arch`, and emits C that includes `pmu-events/pmu-events.h`, `util/header.h`, and `util/pmu.h`. The generated code is linked into perf and implements `pmu_events_table__*`, `pmu_metrics_table__*`, `find_core_*`, `find_sys_events_table`, and metric-group description lookup.

Risks: The module is global-state-heavy; a failed run in a reused interpreter would need clean process state. Some helper exception clauses use `except e`, which is invalid if triggered, so malformed numeric fields could expose latent errors. String-length and escape handling is intentionally limited to the encodings expected by perf JSON. Binary search correctness depends on the sort keys used when emitting entries. Generated C embeds many assumptions about compact-string field order matching `pmu-events.h` structures.

Test signals: Validation should compile the generated C, run perf PMU event tests, and compare generated tables for known test architectures. Useful direct checks are running with `arch=test`, malformed JSON rejection, duplicate-event assertion coverage, metric expression round-trip coverage from `metric_test.py`, and verifying sys event/metric tables are discoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py
Purpose: Generates JSON event definitions for perf legacy hardware cache aliases. It expands known cache IDs, operations, and result names into `EventName`, `BriefDescription`, and `LegacyCacheCode` records.

Important APIs/types/functions: The data tables `hw_cache_id`, `hw_cache_op`, and `hw_cache_result` encode perf's legacy cache dimensions. `add_event()` is the only function; it filters names that would conflict with hardware events, adjusts descriptions and deprecation for L2 aliases, constructs the packed legacy cache code, and appends event dictionaries to `events`.

Control flow: Module top-level loops over cache IDs, aliases, supported operations, and results to emit base, operation, operation-result, and result-only names. The script prints the final JSON array to stdout.

State and persistence: All state is process-local in `events`; no input files are read and no output files are written except stdout. Deprecation flags are stored in generated JSON records.

Dependencies and integration points: Depends only on `json`. The output feeds the same PMU event JSON pipeline that `jevents.py` compiles into perf C tables.

Risks: The mapping is manually encoded and must stay synchronized with perf's `PERF_COUNT_HW_CACHE_*` constants. Alias generation intentionally deprecates many names, so user-facing compatibility depends on preserving those flags. `branch-misses` and `branches` are skipped to avoid priority conflicts.

Test signals: Compare generated JSON against expected legacy event names/codes, validate with `jevents.py`, and exercise `perf list`/`perf stat` legacy cache aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/make_legacy_cache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py
Purpose: Provides the Python expression and metric model used to generate perf metric JSON. It validates event names against loaded PMU JSON, builds an expression tree with operator overloading, serializes/deserializes perf metric expressions, and emits `Metric`/`MetricGroup` dictionaries.

Important APIs/types/functions: `LoadEvents`, `CheckPmu`, `CheckEvent`, `CheckEveryEvent`, and `IsExperimentalEvent` maintain global validation sets. `MetricConstraint` mirrors perf grouping constraints. The expression hierarchy is `Expression`, `Operator`, `Select`, `Function`, `Event`, `MetricRef`, `Constant`, and `Literal`, with helpers `min`, `max`, `d_ratio`, `source_count`, `has_event`, and `strcmp_cpuid_str`. `Metric` and `MetricGroup` represent output records and group descriptions. `ParsePerfJson` parses perf metric expressions into the Python AST model, and `RewriteMetricsInTermsOfOthers` substitutes same-PMU metrics to shorten formulas.

Control flow: Generator scripts create `Event` and expression objects through overloaded arithmetic and comparison operators. Each expression can simplify itself, serialize to perf JSON, serialize to Python reconstructors, test equality, and substitute subexpressions. `ParsePerfJson` rewrites token-like strings into `Event(...)` calls, fixes literals/keywords, transforms Python ternary syntax into `Select`, then evaluates the restricted expression using this module's constructors.

State and persistence: Validation state is held in module globals: `all_pmus`, `all_events`, `experimental_events`, and `all_events_all_models`. The module reads JSON files but writes no files. `Metric` construction mutates descriptions to mark experimental-event use and normalizes scale units.

Dependencies and integration points: Used by `intel_metrics.py`, `jevents.py`, and tests. It depends on Python `ast`, `decimal`, `json`, `os`, and `re`. Its serialized dictionaries become the PMU metric JSON that perf's C parser consumes.

Risks: `ParsePerfJson` uses `eval` after regex rewriting; it is intended for trusted repository JSON, not untrusted input. Simplification uses arithmetic on `Constant` string objects in paths that rely on `__str__` coercion, so operator coverage should be tested carefully. Global validation changes behavior depending on whether `LoadEvents` was called. Escaping around commas, equals signs, slashes, and metric literals is delicate.

Test signals: `metric_test.py` covers operator serialization, bracket precedence, JSON parsing, ternary rewriting, Python round-tripping, simplification, and metric-expression substitution. Additional signals are successful PMU event generation and perf metric parsing in compiled perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py
Purpose: Unit tests for `metric.py` expression behavior. It documents the expected string forms and rewrite semantics that PMU metric generators rely on.

Important APIs/types/functions: `TestMetricExpressions` tests `Event`, `MetricRef`, `Constant`, `Select`, `d_ratio`, `min`, `max`, `source_count`, `has_event`, `JsonEncodeMetric`, `ParsePerfJson`, `ToPython`, `Simplify`, and `RewriteMetricsInTermsOfOthers`.

Control flow: Each test builds expressions, compares `str()`/`ToPerfJson()` output, parses perf JSON strings back into expression objects, and validates simplified or substituted expressions. The substitution test creates same-PMU metric tuples and checks that expressions can be shortened using earlier metric definitions.

State and persistence: Tests run in process and depend on `metric` globals being permissive when no event JSON was loaded. No files are read or written by the tests themselves.

Dependencies and integration points: Uses Python `unittest` and the local `metric` module. It is a guard for `intel_metrics.py` and `jevents.py` because both depend on expression serialization and parsing.

Risks: Coverage is focused on expression mechanics, not full PMU model JSON. It does not exercise every escaping corner or event validation path with loaded event files.

Test signals: Passing this test suite is a direct signal that metric AST precedence, ternary conversion, Python reconstruction, constant simplification, and cross-metric rewrite behavior remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py
Purpose: Maps CPU identifiers to PMU event model directory names by reading architecture `mapfile.csv` files. It is a small CLI helper for selecting model subsets used by PMU event generation.

Important APIs/types/functions: `main()` defines helpers `dir_path`, `find_archs`, `find_mapfiles`, and `find_cpuids`. `find_cpuids` converts `[[:xdigit:]]` regex syntax from mapfiles into Python-compatible `[0-9a-fA-F]` and returns model paths whose cpuid regex matches the requested cpuid list.

Control flow: The CLI accepts `arch`, `cpuid`, and `starting_dir`; chooses matching architecture directories; finds their `mapfile.csv`; scans non-comment rows; matches each requested cpuid against row 0; and prints comma-separated model names from row 2.

State and persistence: Stateless aside from local lists. It reads mapfiles and writes only stdout.

Dependencies and integration points: Depends on `argparse`, `csv`, `os`, and `re`. It integrates with the PMU events build process and can feed the `model` argument of `jevents.py`/`intel_metrics.py`.

Risks: The first-row skipping variable is named confusingly and must preserve mapfile header behavior. Matching is only as accurate as mapfile regexes, and the script supports comma-separated cpuid input without trimming spaces.

Test signals: Run against known architecture mapfiles and cpuid strings; compare model output to expected mapfile row selections and confirm `arch=all` scans all architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h
Purpose: Declares perf's generated PMU event and metric table interface. It is the C contract consumed by generated code from `jevents.py` and by perf runtime callers.

Important APIs/types/functions: Defines `enum aggr_mode_class`, `enum metric_event_groups`, `struct pmu_event`, `struct pmu_metric`, opaque table structs, iterator callback typedefs, lookup-not-found constants, event/metric iteration and find APIs, table lookup APIs for current/default/core/sys PMUs, and `describe_metricgroup`.

Control flow: This header has no executable control flow; it establishes function signatures that generated C implements. Iterator callbacks return 0 to continue or non-zero to terminate, while special not-found constants allow table-local misses to continue across other tables.

State and persistence: No state is stored here. The struct field layout is persistent ABI-like build contract between generated compact records and C decompression routines.

Dependencies and integration points: Includes `stdbool.h` and `stddef.h` and forward-declares `struct perf_pmu`. The generated C includes this header and fills these structures; perf list/stat/metric code calls the declared functions.

Risks: Field-order drift between `struct pmu_event`/`struct pmu_metric` and `jevents.py`'s `_json_event_attributes`/`_json_metric_attributes` would corrupt decompression. Enum value changes must stay synchronized with JSON conversion in `jevents.py` and grouping behavior in perf.

Test signals: Build failures catch signature mismatches; runtime PMU event tests and `perf list`/`perf stat -M` catch lookup and decompression mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/counting.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/counting.py
Purpose: Minimal example of using perf's Python binding to count events. It opens an event list, performs a small CPU-bound loop, reads counts per CPU/thread, and prints raw value/enabled/running fields.

Important APIs/types/functions: `main(event)` calls `perf.parse_events`, modifies each evsel `read_format` to include total enabled/running time, then uses `open`, `enable`, `disable`, `read`, and `close` on perf binding objects.

Control flow: CLI option `-e/--event` defaults to `cpu-clock,task-clock`. The script opens all parsed events, counts down from 100000, disables counting, iterates evsels, CPUs, and threads, then prints one line per read.

State and persistence: State is only the live perf event list and loop counter. No persistent output exists besides stdout.

Dependencies and integration points: Depends on local perf Python extension and kernel perf permissions. It is an example/diagnostic rather than library code.

Risks: Fails if event parsing or perf_event_open permissions fail. The measured workload is intentionally trivial and not a benchmark.

Test signals: Successful execution with default events and sensible nonzero read fields indicates basic counting bindings work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/counting.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/ilist.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/ilist.py
Purpose: Textual TUI for browsing PMUs, events, and metrics interactively and displaying live counts/sparklines for a selected item. It is an interactive replacement/demo for `perf list` plus quick counter reads.

Important APIs/types/functions: `TreeValue` abstracts tree entries with `name`, `description`, `matches`, `parse`, and `value`. `Metric` resolves metric descriptions with `perf.metrics()`, parses via `perf.parse_metrics`, and computes values via `evlist.compute_metric`. `PmuEvent` resolves PMU event descriptions through `perf.pmus()` and parses event strings. UI classes include `ErrorScreen`, `SearchScreen`, `Counter`, `CounterSparkline`, and `IListApp`.

Control flow: `IListApp.compose()` builds a PMU tree and a metric-group tree. Search actions collect matching nodes and navigate through them. Selecting a leaf closes any old evlist, opens the new event/metric, adds counters and sparklines for total and each CPU, and periodic `update_counts()` disables the evlist, reads per-CPU/thread values, updates labels/sparklines, and reenables counting.

State and persistence: UI state includes `selected`, `evlist`, search result nodes, and current search cursor. Counter samples are kept in each sparkline's in-memory data list and trimmed by visible width. No persistent files are written.

Dependencies and integration points: Depends on perf Python bindings and the `textual` framework. Integrates with perf's PMU/event/metric discovery and event opening APIs.

Risks: It broadly catches exceptions around metric computation and event opening, so failures can appear as zero values or modal errors. Runtime depends on Textual API compatibility and perf permissions. Tree construction repeatedly calls `perf.metrics()` and `perf.pmus()`, which may be expensive on systems with many PMUs.

Test signals: Manual TUI smoke tests should verify tree population, search, event selection, counter updates, metric computation, and clean close/reopen behavior across PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/ilist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py
Purpose: Example perf Python binding consumer for tracepoint samples, focused on `sched:sched_switch`. It streams context-switch records and prints decoded fields.

Important APIs/types/functions: `change_proctitle()` optionally uses `setproctitle`. `main()` creates `perf.cpu_map`, `perf.thread_map(-1)`, parses `sched:sched_switch`, disables tracking events, configures sample formats, mmaps the evlist, polls forever, and reads `perf.sample_event` instances.

Control flow: After setup, an infinite poll loop reads one event per CPU when available, ignores non-sample records, and prints timestamp plus previous/next task information.

State and persistence: Maintains live mmap buffers and perf event configuration only. Output is an unbounded stdout stream.

Dependencies and integration points: Requires perf Python bindings and sched tracepoint availability. Optional `setproctitle` only improves process listing.

Risks: Infinite runtime, permission requirements, and potential output volume are the main operational risks. It assumes sched_switch sample fields are exposed as Python attributes.

Test signals: Running under suitable privileges should print sched switch lines; failures isolate tracepoint decoding or mmap/poll binding issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/tracepoint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/twatch.py -->
# sources/distributed-fs/ceph-client/tools/perf/python/twatch.py
Purpose: Experimental thread lifetime/context-switch watcher using the perf Python interface. It demonstrates software dummy events with task/comm/context-switch records instead of sampling real hardware events.

Important APIs/types/functions: `main(context_switch=0, thread=-1)` builds `perf.cpu_map`, `perf.thread_map`, one `perf.evsel` with `TYPE_SOFTWARE` and `COUNT_SW_DUMMY`, opens it, wraps it in `perf.evlist`, mmaps, polls, and prints events.

Control flow: The function configures the evsel to record task and comm lifetime events, then loops forever reading events per CPU after each poll. The bottom comment documents using `context_switch=1` and a target pid to test switch records.

State and persistence: State is live perf maps and mmap buffers; no files are persisted. Output is stdout.

Dependencies and integration points: Depends on perf Python bindings and kernel perf record support for software dummy and task/context-switch records.

Risks: It has no CLI parser despite documented possible options. Infinite output and perf permissions are expected concerns.

Test signals: Launching the script should print task lifetime or switch records; selecting a target thread can validate switch-in/switch-out decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/python/twatch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c
Purpose: Generated Perl XS bridge exposing selected perf scripting context fields to Perl perf scripts. It wraps libtraceevent helpers for common preempt count, common flags, and common lock depth.

Important APIs/types/functions: XS functions `XS_Perf__Trace__Context_common_pc`, `XS_Perf__Trace__Context_common_flags`, and `XS_Perf__Trace__Context_common_lock_depth` convert a Perl scalar integer back to `struct scripting_context *`, call `common_pc`, `common_flags`, or `common_lock_depth`, and return integer values. `boot_Perf__Trace__Context` registers these functions in the Perl module.

Control flow: Perl loads this extension through `Context.pm`. Each exported function validates a single argument, unwraps the pointer, calls the perf helper, pushes the result, and returns one value.

State and persistence: No persistent state; it operates on the live perf script context pointer passed for each event.

Dependencies and integration points: Depends on Perl XS headers and perf `util/trace-event.h`. It is generated from `Context.xs`, so edits should happen in the XS source, not here.

Risks: Pointer conversion trusts perf's generated script harness. ABI drift in `struct scripting_context` or helper availability would break runtime. The header warns that manual edits are overwritten.

Test signals: Perl `check-perf-trace.pl` exercises these functions via `common_pc`, `common_flags`, and `common_lock_depth`. Successful perf script execution validates the XS bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/Context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm
Purpose: Perl module loader/exporter for the perf trace context XS extension.

Important APIs/types/functions: Exports `common_pc`, `common_flags`, and `common_lock_depth`. Uses `XSLoader::load('Perf::Trace::Context', $VERSION)` to load the compiled extension.

Control flow: Loading the module sets exporter metadata, loads XS symbols, and returns true. Perf scripts then call exported functions inside event handlers.

State and persistence: Only module metadata and exports are initialized. No persistent data is stored.

Dependencies and integration points: Depends on Perl 5.10, `Exporter`, `XSLoader`, and the compiled `Perf::Trace::Context` XS object. Used by Perl perf scripts that need fields not provided as handler arguments.

Risks: Missing or mismatched XS library prevents scripts from loading. Exported names must match the XS registration in `Context.c`.

Test signals: `check-perf-trace.pl` imports this module and prints uncommon context fields from real trace events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Context.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm
Purpose: Perl utility module for perf script field formatting. It stores symbolic and flag field definitions and formats numeric trace flags into readable strings.

Important APIs/types/functions: Exports `define_flag_field`, `define_flag_value`, `flag_str`, `dump_flag_fields`, `define_symbolic_field`, `define_symbolic_value`, `symbol_str`, `dump_symbolic_fields`, and `trace_flag_str`. Internal hashes `%flag_fields` and `%symbolic_fields` hold event/field mappings.

Control flow: Perf's script generator or scripts populate mappings with define functions. Event handlers call `flag_str` or `symbol_str` to translate integer values. `trace_flag_str` formats common flags using `%trace_flags`.

State and persistence: Mapping state is global to the Perl interpreter process and lasts for the perf script run. Nothing is persisted to disk.

Dependencies and integration points: Used by Perl scripts under `scripts/perl`. It mirrors the Python `Core.py` behavior for cross-language script support.

Risks: Undefined mappings return empty/undef strings, so missing generated definitions can silently reduce output quality. All state is global and unnamespaced beyond event/field keys.

Test signals: `check-perf-trace.pl` exercises `symbol_str`, `flag_str`, `trace_flag_str`, and unhandled-event reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Core.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm
Purpose: Miscellaneous Perl helpers for perf trace scripts, primarily time conversion and terminal clearing.

Important APIs/types/functions: Exports `avg`, `nsecs`, `nsecs_secs`, `nsecs_nsecs`, `nsecs_usecs`, `print_nsecs`, and `clear_term`; implemented functions include average, nanosecond composition/decomposition, `nsecs_str`, and ANSI clear-screen output.

Control flow: Scripts call helpers while processing events or printing summaries. There is no top-level runtime beyond exports.

State and persistence: Stateless except for the constant `$NSECS_PER_SEC`. No persistence.

Dependencies and integration points: Used by Perl scripts such as wakeup latency and rwtop. It parallels Python `Util.py`.

Risks: Export list includes names not implemented in this file (`nsecs_usecs`, `print_nsecs`), which can surprise callers if they rely on them. Time division returns Perl numeric values and formatting is caller-dependent.

Test signals: Wakeup latency and rwtop scripts indirectly exercise `avg`, `nsecs`, and `clear_term`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/Perf-Trace-Util/lib/Perf/Trace/Util.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/check-perf-trace-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/check-perf-trace-record
Purpose: Shell launcher for a perf script record phase. It records `kmem:kmalloc`, `irq:softirq_entry`, and `kmem:kfree` system-wide for Perl scripting self-tests.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/check-perf-trace-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-record
Purpose: Shell launcher for a perf script record phase. It records syscall exit events, preferring `raw_syscalls:sys_exit` and falling back to `syscalls:sys_exit`.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-report
Purpose: Perl failed syscall report wrapper. It parses optional `comm`, shifts perf options, and invokes `scripts/perl/failed-syscalls.pl`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/failed-syscalls-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-record
Purpose: Shell launcher for a perf script record phase. It records syscall read/write enter events for later fd-level requested-byte reporting.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-report
Purpose: Perl rw-by-file report wrapper. It requires `<comm>` and invokes `scripts/perl/rw-by-file.pl` with that command filter.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-file-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-record
Purpose: Shell launcher for a perf script record phase. It records read/write enter and exit syscall tracepoints for pid-level byte and error reporting.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-report
Purpose: Perl rw-by-pid report wrapper. It invokes `scripts/perl/rw-by-pid.pl` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rw-by-pid-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-record
Purpose: Shell launcher for a perf script record phase. It records the same read/write enter and exit tracepoints used by the interval top report.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-report
Purpose: Perl rwtop report wrapper. It parses optional interval before perf options and invokes `scripts/perl/rwtop.pl`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/rwtop-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-record
Purpose: Shell launcher for a perf script record phase. It records `sched:sched_switch` and `sched:sched_wakeup` for wakeup latency calculation.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-report
Purpose: Perl wakeup latency report wrapper. It invokes `scripts/perl/wakeup-latency.pl` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/bin/wakeup-latency-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl
Purpose: Perl perf-script self-test handler that validates generated event handlers, common context access, symbolic/flag formatting, begin/end callbacks, and unhandled-event accounting.

Important APIs/types/functions: Defines `trace_begin`, `trace_end`, handlers `irq::softirq_entry` and `kmem::kmalloc`, helper `print_uncommon`, `print_unhandled`, `trace_unhandled`, and `print_header`. It imports `Perf::Trace::Core`, `Context`, and `Util`.

Control flow: When perf script replays matching events, handler functions print a common header, context fields from XS, and decoded symbolic/flag fields. Unmatched events increment `%unhandled`; `trace_end` prints a final summary.

State and persistence: `%unhandled` accumulates counts during the run. Output is stdout only.

Dependencies and integration points: Designed to pair with `bin/check-perf-trace-record`, which records kmem and irq tracepoints. It validates the Perl trace utility stack.

Risks: It assumes generated definitions exist for `irq::softirq_entry` symbols and `kmem::kmalloc` flags. Missing tracepoints or permissions prevent meaningful output.

Test signals: If this script runs and displays expected decoded values and end output, Perl perf scripting support is operational.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl
Purpose: Perl report script that counts failed system calls by command name.

Important APIs/types/functions: Handles `raw_syscalls::sys_exit` and aliases `syscalls::sys_exit` to it. `trace_end` prints counts sorted by descending errors. Optional first argument filters to one `comm`.

Control flow: Each syscall exit with negative `ret` increments `%failed_syscalls` keyed by `common_comm`. At trace end, rows are sorted and printed, skipping nonmatching comm values when a filter is provided.

State and persistence: `%failed_syscalls` is the only run state. Output is stdout; no files are written.

Dependencies and integration points: Paired with `bin/failed-syscalls-record` and `bin/failed-syscalls-report`. Uses perf's Perl event handler naming convention.

Risks: Counts by command name, not pid or syscall number, so processes sharing `comm` are aggregated. Raw vs typed syscall tracepoint availability varies by kernel.

Test signals: Recording failed syscalls then reporting should show nonzero rows for workloads that return negative syscall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/failed-syscalls.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl
Purpose: Perl report script that summarizes read/write syscall requests by file descriptor for a selected command name.

Important APIs/types/functions: Handlers `syscalls::sys_enter_read` and `syscalls::sys_enter_write` update `%reads` and `%writes`; `trace_end` prints sorted summaries; `trace_unhandled` tracks unrelated events.

Control flow: The script requires a `<comm>` argument. During replay, it only records syscalls whose `common_comm` equals that argument, accumulating read counts/bytes requested and write counts/bytes requested by fd. At the end it prints read and write tables.

State and persistence: `%reads`, `%writes`, and `%unhandled` are in-memory accumulators. No file path resolution is performed despite the name; fd numbers are reported.

Dependencies and integration points: Paired with `bin/rw-by-file-record` and report wrapper. Uses Perl perf script handler signatures for syscall enter events.

Risks: It records requested byte counts, not necessarily successful bytes. FD reuse across time is not disambiguated. Filtering by `comm` can miss renamed processes or aggregate unrelated processes.

Test signals: Run against a known command doing reads/writes and verify fd rows and counts appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-file.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl
Purpose: Perl report script that summarizes read/write activity and errors by pid.

Important APIs/types/functions: Handles syscall enter/exit for read and write. `%reads` tracks requested bytes, successful bytes read, errors, count, and comm. `%writes` tracks requested write bytes, write counts, errors, and comm. `trace_end` prints four tables: reads, failed reads, writes, failed writes.

Control flow: Enter handlers increment request totals. Exit handlers add successful read return values or error counts for failed reads/writes. End processing sorts by bytes read/written and by error count.

State and persistence: All state is in `%reads`, `%writes`, and `%unhandled`; output is stdout only.

Dependencies and integration points: Paired with `bin/rw-by-pid-record` and report wrapper. Uses syscall tracepoints produced by perf record.

Risks: Writes count requested bytes, not successful positive write return values. Long-running pid reuse can combine data if trace spans reuse. Some hash dereferences assume nested `errors` hashes exist and may warn for pids without errors.

Test signals: Replay a perf.data containing read/write syscalls and verify sorted pid tables and error tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rw-by-pid.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl
Purpose: Perl live-style report that periodically displays top read/write syscall activity by pid.

Important APIs/types/functions: Read/write enter/exit handlers update `%reads` and `%writes`; `trace_begin` installs a `SIGALRM` handler; `set_print_pending`, `print_check`, and `print_totals` implement interval refresh; `clear_term` refreshes the terminal.

Control flow: Optional argument sets the refresh interval, defaulting to 3 seconds. A signal marks output pending, event handlers check and print totals when safe, then reset accumulated read/write hashes after each display. `trace_end` prints any unhandled summary and final totals.

State and persistence: Uses `%reads`, `%writes`, `%unhandled`, `$print_pending`, and signal timer state. It intentionally resets totals after each interval and writes only to stdout.

Dependencies and integration points: Paired with `bin/rwtop-record` and report wrapper. Depends on POSIX signal handling and perf syscall tracepoints.

Risks: Signal-driven printing can be timing-sensitive. Counts are interval-local, not cumulative. Write byte totals are requested bytes. Output assumes a terminal for clear-screen behavior.

Test signals: Running the record/report pair while generating I/O should refresh top read/write rows at the selected interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/rwtop.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl
Purpose: Perl report script computing scheduler wakeup-to-switch latency statistics.

Important APIs/types/functions: `sched::sched_wakeup` records wakeup timestamp by target CPU; `sched::sched_switch` computes latency for the CPU's last wakeup; `trace_begin` initializes min/max; `trace_end` prints total, average, min, and max latency.

Control flow: Wakeup events store `nsecs(common_secs, common_nsecs)` in `%last_wakeup` keyed by target CPU. Switch events use the current CPU's stored timestamp, update total/min/max, increment wakeup count, and clear the timestamp. End processing prints stats and unhandled events.

State and persistence: `%last_wakeup`, min/max, total latency, wakeup count, and `%unhandled` live for one replay. No persistence beyond stdout.

Dependencies and integration points: Paired with `bin/wakeup-latency-record` and report wrapper. Uses `Perf::Trace::Util` for nanosecond arithmetic and average.

Risks: Matching wakeup by CPU only is approximate and can be overwritten by multiple wakeups before a switch. Initial min value is fixed at 1s and will print even if no wakeups occur. Requires sched tracepoint availability.

Test signals: Replaying sched wakeup/switch events should produce nonzero total wakeups and reasonable min/avg/max values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/wakeup-latency.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c
Purpose: Python C extension module `perf_trace_context` exposing selected perf script context helpers to Python scripts. It provides common trace fields, instruction bytes, itrace option parsing, source line/source code lookup, and perf config access.

Important APIs/types/functions: Helper `get_args` unwraps the Python capsule holding `struct scripting_context`. Exported methods include `common_pc`, `common_flags`, `common_lock_depth` when libtraceevent is available, `perf_sample_insn`, `perf_set_itrace_options`, `perf_sample_srcline`, `perf_sample_srccode`, and `perf_config_get`. `PyInit_perf_trace_context` registers the module and a placeholder `perf_script_context` attribute.

Control flow: Python scripts pass the current perf script context capsule. Each function validates arguments, accesses fields such as sample/al/session/map, calls perf utility helpers, converts results to Python objects, and returns them. Source lookup uses DSO/map address translation and optionally fetches a source line.

State and persistence: No module-level mutable state beyond module initialization. It reads live perf session/sample context and perf config; no files are written, but source lookup may read debug/source files through perf helpers.

Dependencies and integration points: Depends on Python C API and many perf internals: config, trace-event, event, symbol, thread, map, maps, auxtrace, session, srcline, and srccode. Used by Python perf scripts such as `check-perf-trace.py`, `arm-cs-trace-disasm.py`, and `event_analyzing_sample.py`.

Risks: Strongly coupled to perf internal structs and Python C API. `perf_set_itrace_options` refuses changes after synth opts are already set. Source and instruction lookup can return `None` when maps or debug data are missing.

Test signals: Python trace script self-tests, CoreSight disassembly/source printing, and PEBS sample analysis exercise the exported methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/Context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py
Purpose: Python utility module for perf script field formatting. It mirrors the Perl Core module by storing flag/symbol mappings and formatting common trace flags.

Important APIs/types/functions: `autodict` creates recursive defaultdicts. Global `flag_fields` and `symbolic_fields` store definitions. Public functions are `define_flag_field`, `define_flag_value`, `define_symbolic_field`, `define_symbolic_value`, `flag_str`, `symbol_str`, `trace_flag_str`, and `taskState`. `EventHeaders` wraps common event header fields with nanosecond timestamp helpers.

Control flow: Generated script prologues or scripts populate mapping dictionaries. Event handlers call `flag_str`/`symbol_str` to translate numeric fields. `trace_flag_str` scans the fixed trace flag map and joins matched bits.

State and persistence: Mapping dictionaries are process-global for one script replay. `EventHeaders` instances are per-event objects. No disk persistence.

Dependencies and integration points: Depends only on `collections.defaultdict`. Imported by Python perf scripts, especially `check-perf-trace.py`.

Risks: Missing mappings produce empty strings. `taskState` only covers a small subset of states. Global mutable maps can be overwritten if scripts define the same event/field keys differently.

Test signals: `check-perf-trace.py` validates symbolic and flag formatting against real tracepoint fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Core.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py
Purpose: Defines simple Python classes for grouping raw perf samples into generic and Intel PEBS event objects.

Important APIs/types/functions: Constants `EVTYPE_GENERIC`, `EVTYPE_PEBS`, `EVTYPE_PEBS_LL`, and `EVTYPE_IBS` identify event categories. `create_event()` selects `PebsEvent`, `PebsNHM`, or `PerfEvent` by raw buffer length. `PerfEvent` stores generic metadata. `PebsEvent` unpacks base PEBS register fields. `PebsNHM` unpacks Nehalem/Westmere load-latency fields.

Control flow: Consumers pass event metadata and `raw_buf`. The factory checks raw size, constructs the appropriate class, and constructors unpack fixed 64-bit fields with `struct.unpack` before calling base initialization.

State and persistence: Class counters track total created events by type. Each object stores raw buffer and decoded fields. No disk persistence.

Dependencies and integration points: Used by `event_analyzing_sample.py` to classify samples before SQLite insertion. Depends on Python `struct` and assumes x86 PEBS record layouts.

Risks: Raw-buffer-size detection is heuristic and architecture/layout-specific. Unexpected buffer lengths fall back to generic events. PEBS parsing assumes native data is little-endian 64-bit words in the expected order.

Test signals: Feeding known 144-byte and 176-byte raw buffers should produce `PebsEvent` and `PebsNHM` with decoded fields; `event_analyzing_sample.py` exercises this path during perf script replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/EventClass.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py
Purpose: wxPython GUI frame for visualizing scheduler trace rectangles and summaries. It is support code for scheduler visualization scripts.

Important APIs/types/functions: `RootFrame` owns window dimensions, zoom, scroll settings, and the scheduler tracer adapter. Methods convert time to pixels, track scroll origin, paint rectangle zones, request visible data from `sched_tracer.fill_zone`, map mouse coordinates to rectangles, update summary text, zoom, and handle key/mouse events.

Control flow: Construction initializes wx frame/panels/scrollbars, binds paint/key/mouse events, asks the tracer for interval and rectangle count, and shows the frame. Paint events compute visible time range and call into the tracer. Mouse clicks identify a rectangle and timestamp and dispatch to `sched_tracer.mouse_down`. Keyboard events zoom or scroll.

State and persistence: Maintains GUI state such as `zoom`, virtual width/height, screen dimensions, current `wx.PaintDC`, and optional summary text widget. No persistent files.

Dependencies and integration points: Requires `wx`/wxPython and a `sched_tracer` object implementing `set_root_win`, `interval`, `nr_rectangles`, `fill_zone`, and `mouse_down`.

Risks: Uses older wx APIs such as `GetPositionTuple`, and Python 2-era division may produce floats where wx expects ints. Missing wxPython raises ImportError. Rendering depends on tracer callbacks being efficient.

Test signals: Manual GUI test with a scheduler tracer should show rectangles, respond to mouse selection, and zoom/scroll with keyboard controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py
Purpose: Miscellaneous Python utilities for perf trace scripts: time conversion, running stats, terminal clearing, syscall name lookup, and errno formatting.

Important APIs/types/functions: Defines futex constants, `NSECS_PER_SEC`, `avg`, `nsecs`, `nsecs_secs`, `nsecs_nsecs`, `nsecs_str`, `add_stats`, `clear_term`, `syscall_name`, and `strerror`. Optional audit integration maps machine names to audit architecture ids.

Control flow: At import time it tries to import `audit`, chooses `machine_id` from `os.uname()[4]`, and prints one warning if audit is unavailable. `syscall_name` uses audit when possible and otherwise returns the numeric id as a string.

State and persistence: `audit_package_warned` and `machine_id` are module-level state. `add_stats` mutates a caller-provided dictionary. No persistence.

Dependencies and integration points: Used by Python perf scripts that need syscall names, errno names, or nanosecond formatting. Optional dependency on python-audit affects output quality.

Risks: Import-time warning can affect script output. `nsecs_str` creates a one-element tuple due to a trailing comma, which may be a latent formatting bug. `add_stats` uses a simple average update rather than a mathematically exact running average over all values.

Test signals: Scripts that format syscall counts or futex errors exercise audit/errno helpers; unit checks should cover `nsecs_str` and `add_stats` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/Util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py
Purpose: Perf script handler for ARM CoreSight traces that prints source lines and optional disassembly for traced instruction ranges. It supports filtering by sample/time ranges and kernel/user DSO resolution.

Important APIs/types/functions: CLI parsing configures vmlinux path, objdump command, verbosity, start/stop time, and start/stop sample. Helpers include `default_objdump`, `find_vmlinux`, `get_dso_file_path`, `read_disam`, `print_disam`, `print_sample`, `common_start_str`, `print_srccode`, and `process_event`. It imports `perf_sample_srccode` and `perf_config_get` from `perf_trace_context`.

Control flow: Perf calls `trace_begin`, `process_event` for each sample, and `trace_end`. `process_event` increments a global sample index, applies filters, stores previous branch target by CPU, ignores non-branch/non-instruction samples as appropriate, computes an address range from consecutive branch samples, validates DSO map bounds, optionally runs objdump for that range, and prints source/symbol context.

State and persistence: Global caches include `disasm_cache`, `cpu_data`, sample index, and last printed source/DSO fields to suppress repeated output. No persistent output; it reads vmlinux/build-id files and invokes external objdump.

Dependencies and integration points: Depends on perf Python script context, `PERF_BUILDID_DIR`, vmlinux/debug files, objdump/llvm-objdump, and CoreSight branch/instruction sample fields. Integrates with perf script `-s`.

Risks: Assumes `PERF_BUILDID_DIR` exists for non-kernel DSOs. Disassembly cache can be cleared wholesale after 64K entries. Address calculations depend on DSO start and map offset conventions. Missing kcore/debug info affects accuracy and source availability.

Test signals: Replay CoreSight perf.data with and without `-d`; verify sample filtering, source output, DSO resolution, and objdump ranges for kernel and user DSOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/arm-cs-trace-disasm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-record
Purpose: Shell launcher for a perf script record phase. It records memory compaction begin/end/migrate/isolate tracepoints.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-report
Purpose: Python compaction report wrapper. It passes perf script arguments to `scripts/python/compaction-times.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/compaction-times-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-record
Purpose: Shell launcher for a perf script record phase. It runs generic `perf record` so arbitrary samples can be analyzed by the Python sample analyzer.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-report
Purpose: Python sample analyzer wrapper. It invokes `scripts/python/event_analyzing_sample.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/event_analyzing_sample-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-record
Purpose: Shell launcher for a perf script record phase. It runs generic `perf record` for later export to PostgreSQL; tracepoints are noted as excluded by the report family.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-report
Purpose: PostgreSQL export wrapper. It parses up to three positional arguments: database name, columns, and calls, then invokes `export-to-postgresql.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-postgresql-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-record
Purpose: Shell launcher for a perf script record phase. It runs generic `perf record` for later export to SQLite; tracepoints are noted as excluded by the report family.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-report
Purpose: SQLite export wrapper. It parses up to three positional arguments: database name, columns, and calls, then invokes `export-to-sqlite.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/export-to-sqlite-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-record
Purpose: Shell launcher for a perf script record phase. It records syscall exit events, preferring raw tracepoints and falling back to typed syscalls.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report
Purpose: Python failed-syscalls-by-pid wrapper. It parses optional `comm` and invokes `failed-syscalls-by-pid.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-record
Purpose: Shell launcher for a perf script record phase. It runs `perf record -g` to capture call graphs for flamegraph generation.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-report
Purpose: Python flamegraph wrapper. It invokes `flamegraph.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/flamegraph-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-record
Purpose: Shell launcher for a perf script record phase. It records futex enter and exit syscall tracepoints.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-report
Purpose: Python futex contention wrapper. It invokes `futex-contention.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/futex-contention-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-record
Purpose: Shell launcher for a perf script record phase. It runs `perf record -F 99 -g` for Firefox Gecko profile export.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-report
Purpose: Python Gecko profile wrapper. It special-cases `-i -` streaming input and otherwise passes arguments after `--` to `gecko.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/gecko-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-record
Purpose: Shell launcher for a perf script record phase. It validates that arguments include an `intel_pt` event, then runs `perf record`.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-report
Purpose: Intel PT events report wrapper. It invokes `intel-pt-events.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/intel-pt-events-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-record
Purpose: Shell launcher for a perf script record phase. It discovers a retired-load event from `perf list` and records physical address samples with `--phys-data`.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-report
Purpose: Physical address report wrapper. It invokes `mem-phys-addr.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/mem-phys-addr-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-record
Purpose: Shell launcher for a perf script record phase. It records `skb:kfree_skb` drop events.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-report
Purpose: Network drop monitor wrapper. It invokes `net_dropmonitor.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/net_dropmonitor-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-record
Purpose: Shell launcher for a perf script record phase. It records net, skb, napi, irq, and softirq tracepoints for packet timing analysis.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-report
Purpose: Network device timing wrapper. It invokes `netdev-times.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/netdev-times-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-record
Purpose: Shell launcher for a perf script record phase. It records grouped PowerPC hcall entry/exit tracepoints.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-report
Purpose: PowerPC hcalls wrapper. It invokes `powerpc-hcalls.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/powerpc-hcalls-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record
Purpose: Shell launcher for a perf script record phase. It records sched wakeup, wakeup_new, switch, and migrate_task events with a larger mmap buffer.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-report
Purpose: Scheduler migration wrapper. It invokes `sched-migration.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sched-migration-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-record
Purpose: Shell launcher for a perf script record phase. It records syscall enter events, preferring raw tracepoints and falling back to typed syscalls.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-report
Purpose: Syscall top wrapper. It parses optional `comm` and interval before invoking `sctop.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/sctop-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-record
Purpose: Shell launcher for a perf script record phase. It runs generic `perf record` for later stack-collapse output.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-report
Purpose: Stackcollapse wrapper. It invokes `stackcollapse.py` through `perf script`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/stackcollapse-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-record
Purpose: Shell launcher for a perf script record phase. It records syscall enter events for pid-level syscall counting.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-report
Purpose: Syscall counts by pid wrapper. It parses optional `comm` and invokes `syscall-counts-by-pid.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-by-pid-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-record
Purpose: Shell launcher for a perf script record phase. It records syscall enter events for system-wide syscall counting.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-report
Purpose: Syscall counts wrapper. It parses optional `comm` and invokes `syscall-counts.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/syscall-counts-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-record -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-record
Purpose: Shell launcher for a perf script record phase. It records sched switch and migrate_task events for task timing analysis.

Important APIs/types/functions: The only API is the executable script itself. It delegates to the external `perf record` command and forwards user arguments with `$@`.

Control flow: The script is straight-line shell. Some variants include fallback logic with `||`, argument validation, or event discovery before invoking `perf record`. There are no reusable shell functions.

State and persistence: It creates or appends perf's normal recording output, typically `perf.data`, through `perf record`. The wrapper itself stores no state.

Dependencies and integration points: Depends on a working `perf` binary, kernel tracepoint/PMU availability, and permissions for the selected events. It is paired with the corresponding `*-report` wrapper and script under `scripts/perl` or `scripts/python`.

Risks: Tracepoint names vary by kernel, and permission failures are common outside privileged environments. Wrappers using fallback with stderr redirected to `/dev/null` can hide the reason the preferred event failed. Event-discovery wrappers depend on `perf list` output format.

Test signals: A successful run exits with `perf record` status and produces a readable `perf.data` for the paired report wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-record -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-report
Purpose: Task analyzer wrapper. It passes arguments after `--` to `task-analyzer.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/task-analyzer-report -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py
Purpose: Python perf-script self-test handler analogous to the Perl version. It verifies generated event handlers, common context access, flag/symbol formatting, and unhandled-event reporting.

Important APIs/types/functions: Defines `trace_begin`, `trace_end`, handlers `irq__softirq_entry` and `kmem__kmalloc`, `trace_unhandled`, `print_header`, `print_uncommon`, and `print_unhandled`. Imports `Core` helpers and all symbols from `perf_trace_context`.

Control flow: On matching trace events, handlers print common event header fields, extra context fields from the C extension, and decoded symbolic/flag values. Unhandled events increment an `autodict` counter and are printed at trace end.

State and persistence: `unhandled` is the only accumulator. Output is stdout.

Dependencies and integration points: Requires `PERF_EXEC_PATH` to locate Python trace utilities and the compiled `perf_trace_context` extension. Paired with record scripts capturing kmem and irq tracepoints.

Risks: Broad imports and generated definitions can hide missing names until runtime. Missing tracepoint format definitions reduce symbol/flag formatting quality.

Test signals: Running with matching perf.data should print `trace_begin`, decoded softirq/kmalloc fields, common context values, and a final unhandled summary if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py
Purpose: Python perf-script report that measures time and scanner/migration work for Linux memory compaction events.

Important APIs/types/functions: Option classes `popt` and `topt` define display modes. `comm_filter` and `pid_filter` implement filtering. `pair` stores paired counters, `cnode` stores one compaction interval, and `chead` manages per-pid heads plus global totals. Event handlers cover `mm_compaction_begin`, `end`, `migratepages`, `isolate_freepages`, and `isolate_migratepages`.

Control flow: CLI options are parsed at import time after `--`. Begin events create a pending `cnode` for the pid unless filtered. Intermediate events increment pending migration/free/migrate scanner stats. End events complete the pending interval, add elapsed time to global and optional per-process totals, and store verbose interval entries when requested. `trace_end` prints global totals and optional per-process details.

State and persistence: Global option variables, `chead.heads`, `chead.val`, and each head's pending/list state persist for one replay. Output is stdout; no files are written.

Dependencies and integration points: Paired with `bin/compaction-times-record` and report wrapper. Depends on compaction tracepoints and perf script Python handler naming.

Risks: Missing begin/end ordering produces stderr warnings. Filtering is decided when a head is first created, so later command-name changes for a pid are not reconsidered. Time formatting rounds microseconds when `-u` is selected.

Test signals: Force compaction via `/proc/sys/vm/compact_memory`, record the listed tracepoints, and verify total/per-process compaction time and scanner/migration counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/compaction-times.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py
Purpose: Example general perf sample analyzer that stores sample metadata in SQLite and prints grouped histograms for generic events and PEBS load-latency events.

Important APIs/types/functions: `trace_begin` creates `gen_events` and `pebs_ll` tables in `/dev/shm/perf.db`. `process_event` extracts sample attributes, raw buffer, comm, event name, DSO, and symbol; `create_event` from `EventClass.py` classifies raw buffers; `insert_db` writes rows. `trace_end` calls `show_general_events` and `show_pebs_ll`. `num2sym` renders logarithmic histograms.

Control flow: At import time the script opens SQLite in autocommit mode. During replay, every sample is classified and inserted. At the end, SQL group-by queries summarize generic events by comm/symbol/dso and PEBS LL events by comm/symbol/dse/latency.

State and persistence: Persists analysis data to `/dev/shm/perf.db` for the duration of the run and possibly after if not removed by the environment. `PerfEvent` class counters also accumulate in memory.

Dependencies and integration points: Depends on perf Python script context, SQLite, `/dev/shm`, and `EventClass.py`. Paired with record/report wrappers that allow arbitrary perf samples.

Risks: Fixed database path can collide with concurrent runs or stale data because tables are `create if not exists` and inserts do not clear old rows. Autocommit row-by-row insertion can be slow for large data despite tmpfs. Raw PEBS detection is heuristic.

Test signals: Record a known sample workload, run the report, and verify table counts and histograms reflect the sample mix; remove or isolate `/dev/shm/perf.db` to avoid stale-data false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/event_analyzing_sample.py -->
