# Research: subset-b-006748

This grouped report covers perf test sources under `sources/distributed-fs/ceph-client/tools/perf/tests`. Each section is wrapped with source-path markers for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/expand-cgroup.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/expand-cgroup.c

## Purpose
Tests that an existing `evlist` can be expanded across multiple cgroups without changing the original event ordering, names, or group membership semantics. It exercises default events, explicit grouped events, libpfm events when enabled, and metric-derived events.

## Important APIs, Types, and Functions
- `test_expand_events(struct evlist *evlist)` is the shared verifier. It snapshots original event names, original grouping state, and first-event `nr_members`, calls `evlist__expand_cgroup(evlist, "A,B,C", false)`, then checks expanded entries are grouped by cgroup and repeat the original event sequence.
- `expand_default_events()` builds `evlist__new_default(&target, false)`.
- `expand_group_events()` parses `{cycles,instructions}` after setting `symbol_conf.event_group = true`.
- `expand_libpfm_events()` calls `parse_libpfm_events_option()` with `"CYCLES"` and treats an empty evlist as libpfm unavailable.
- `expand_metric_events()` uses `find_core_metrics_table("testarch", "testcpu")` and `metricgroup__parse_groups_test()` for metric `CPI`.
- The test uses `struct evlist`, `struct evsel`, `struct cgroup`, `struct target`, `struct option`, and parse-event/metric/libpfm helper APIs.

## Control Flow
`test__expand_cgroup_events()` runs the four constructors in sequence. Each constructor creates an evlist, populates it, invokes `test_expand_events()`, then deletes the evlist. The core verifier first stores event names before expansion, records whether the original first event was a group and how many members it had, expands against cgroups `A`, `B`, and `C`, then walks the resulting evlist. It expects `original_event_count * 3` entries, with `ev_name[i % original_count]` and `cgrp_name[i / original_count]`. For the first event in each cgroup block it verifies group status and member count match the original.

## State and Persistence
State is in-memory only: the evlist is mutated by `evlist__expand_cgroup()`, temporary event-name strings are allocated and freed, and `symbol_conf.event_group` is set for grouped/libpfm cases. No files are written. The libpfm path depends on build/runtime support and can short-circuit before expansion if no event was created.

## Dependencies and Integration Points
The test integrates with perf event parsing (`parse_events()`), metric parsing (`metricgroup__parse_groups_test()`), libpfm parsing (`parse_libpfm_events_option()`), cgroup expansion, and the perf test suite registration via `DEFINE_SUITE("Event expansion for cgroups", expand_cgroup_events)`.

## Risks and Edge Cases
- `symbol_conf.event_group` is global state and is not restored locally; other tests must tolerate the suite environment or reset global symbol configuration.
- The verifier assumes expansion order is cgroup-major with event order preserved inside each cgroup.
- The libpfm branch treats an empty evlist as a non-fatal unavailable path, so a disabled libpfm build does not actually exercise expansion for that case.
- Only first-event group metadata is checked; deeper per-member leader relationships are indirectly covered by group member counts but not exhaustively validated.

## Test Signals
Failures report count, event-name, cgroup-name, group-flag, or group-member mismatches via `pr_debug()` and `TEST_ASSERT_*`. A passing suite signals that default, grouped, libpfm-enabled, and metric-generated evlists remain structurally coherent after cgroup expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/expand-cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/expr.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/expr.c

## Purpose
Validates perf's expression parser, ID discovery, topology constants, CPUID string matching, and ID-set union behavior used by metric expression evaluation.

## Important APIs, Types, and Functions
- `test_ids_union()` exercises `ids__new()`, `ids__insert()`, `ids__union()`, `ids__free()`, and `hashmap__size()` across empty, duplicate, and overlapping ID sets.
- `test(struct expr_parse_ctx *ctx, const char *e, double val2)` wraps `expr__parse()` and exact-value assertions for arithmetic and logical expressions.
- `test__expr()` builds an `expr_parse_ctx`, adds `FOO` and `BAR`, runs parse/evaluation checks, clears/reuses the context for `expr__find_ids()`, queries topology constants, tests CPUID matching via `strcmp_cpuid_str()`, and verifies `has_event()`.
- Key types include `struct expr_parse_ctx`, `struct expr_id_data`, `struct hashmap`, `struct perf_cpu`, and topology helpers from `cputopo`, `header`, and `smt`.

## Control Flow
The suite starts by obtaining a CPUID string, runs ID union checks, then evaluates arithmetic, modulo, unary minus, bitwise-style logical operators, `min`, `max`, nested ternaries, floating literals, ratios, and comparisons. It separately checks division by zero returns a parsed NaN while malformed syntax fails. It then repeatedly clears the context and tests ID extraction, including escaped event parameters using `ctx->sctx.runtime`, escaped dashes, conditional expressions involving `#smt_on` and `#core_wide`, and short-circuit cases that should not collect unused IDs. Finally it parses topology constants, validates ordering relationships, handles `#system_tsc_freq` architecture behavior, checks `source_count(EVENT1)`, escapes the real CPUID string for parser syntax, and tests `has_event(cycles)`.

## State and Persistence
All state is process-local. The expression context is allocated, mutated with IDs and scalar values, cleared several times, and freed. CPUID strings are dynamically allocated and transformed with `strreplace_chars()`. No persistent files are created.

## Dependencies and Integration Points
This file exercises `util/expr` and its support code, including hash maps, topology queries, SMT/core-wide helpers, CPUID environment override behavior, and test-suite registration through `DEFINE_SUITE("Simple expression parser", expr)`.

## Risks and Edge Cases
- Floating comparisons use exact equality for expected decimal results such as `3.2`; this relies on the parser and compiler producing stable double representations for these simple cases.
- `#system_tsc_freq` behavior is architecture-specific and Intel-specific; the test tolerates zero on non-Intel but asserts support on x86 if parsing fails.
- Short-circuit ID discovery is heavily semantically coupled to expression optimizer behavior.
- Global system topology affects some expected branches, though the assertions are framed as ordering constraints rather than fixed counts.

## Test Signals
Pass signals include correct numeric parser behavior, correct ID extraction and short-circuiting, valid topology constants, CPUID comparison support for escaped strings, and event-presence helper behavior. Failures are emitted through `TEST_ASSERT_VAL`/`TEST_ASSERT_EQUAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/fdarray.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/fdarray.c

## Purpose
Tests the generic `fdarray` helper used by perf polling code, specifically filtering entries by `revents` masks and automatic growth when adding more descriptors than the initial allocation.

## Important APIs, Types, and Functions
- `fdarray__init_revents()` fills all allocated entries with descending fake fds and uniform `events`/`revents`, while setting `nr = nr_alloc`.
- `fdarray__fprintf_prefix()` prints debug state only when `verbose > 0`.
- `test__fdarray__filter()` verifies `fdarray__filter()` keeps all entries when the filter mask is absent, removes all entries when all match `POLLHUP`, and compacts partial survivors.
- `test__fdarray__add()` uses local `FDA_ADD` and `FDA_CHECK` macros to verify `fdarray__add()` preserves fd/event values and grows from an initial 2 slots to at least 4 entries.

## Control Flow
The filter test creates a 5-entry array with growth step 5, initializes synthetic `revents`, calls `fdarray__filter()` under several masks, and validates resulting `nr` counts. The add test creates a 2-entry array with growth step 2, adds two entries, then adds two more to force reallocation, checking each insertion and final entry values.

## State and Persistence
State is heap-local to `struct fdarray`; the tests allocate with `fdarray__new()` and always delete with `fdarray__delete()` on normal cleanup paths. Debug printing goes to stderr when verbose. No persistent state is produced.

## Dependencies and Integration Points
Integrates with `api/fd/array.h`, `poll.h`, perf debug output, and the tests framework via two `DEFINE_SUITE()` registrations: fdarray filtering and fdarray add/autogrow behavior.

## Risks and Edge Cases
- The tests use fake integer fds and do not interact with actual kernel descriptors.
- The filter callback arguments are `NULL`, so callback-assisted cleanup behavior is not covered.
- The add test checks `events` but its error message labels one path as `revents`; the functional assertion is still on the intended field.

## Test Signals
Passing requires correct compaction counts for all/none/partial filtering and correct order/value preservation across autogrow. Failures print detailed line-numbered diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/fdarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/genelf.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/genelf.c

## Purpose
Verifies the JIT dump ELF writer can emit an ELF image for a small code blob when JIT dump support is compiled in.

## Important APIs, Types, and Functions
- `test__jit_write_elf()` is compiled with two behaviors. With `HAVE_JITDUMP`, it creates a temporary file, writes a synthetic x86 code sequence using `jit_write_elf()`, closes and unlinks the file, and returns success based on the writer result. Without `HAVE_JITDUMP`, it returns `TEST_SKIP`.
- Uses `mkstemp()`, `close()`, `unlink()`, and `jit_write_elf(fd, 0, "main", code, size, NULL, ...)`.

## Control Flow
The test copies `/tmp/perf-test-XXXXXX` into a local buffer, creates the temp file, logs its path, writes one symbol named `main`, closes the fd, unlinks the temp path, then maps `jit_write_elf()` nonzero to `TEST_FAIL`.

## State and Persistence
The only external state is a temporary file under `/tmp`, removed before return in the normal write path. If `mkstemp()` fails there is no cleanup. No test artifact is intentionally retained.

## Dependencies and Integration Points
Depends on libelf and `../util/genelf.h` when `HAVE_JITDUMP` is available. Registered as `DEFINE_SUITE("Test jit_write_elf", jit_write_elf)`.

## Risks and Edge Cases
- The code blob is x86-specific even though the writer interface is generic; the test validates ELF generation mechanics, not executability on all architectures.
- Cleanup is straightforward after successful `mkstemp()`, but a failure inside `jit_write_elf()` still unlinks the file.
- Build configurations without JIT dump support skip the test, reducing coverage.

## Test Signals
`TEST_OK`/0 means `jit_write_elf()` accepted and wrote the synthetic symbol/code. `TEST_SKIP` indicates feature absence. `TEST_FAIL` indicates temp-file or ELF writer failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/genelf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.c

## Purpose
Provides shared synthetic machine, thread, mmap, DSO, and symbol fixtures plus histogram debug printers used by multiple histogram tests.

## Important APIs, Types, and Functions
- Static fixture arrays define fake threads (`perf` pids 100/200 and `bash` pid 300), fake mmap regions for executable/libc/kernel DSOs, and fake symbols for each DSO.
- `struct fake_sym` captures symbol start, length, and name.
- `setup_fake_machine(struct machines *machines)` creates or finds the host machine, creates threads, processes synthetic mmap events, marks DSOs loaded, and inserts symbols into each DSO symbol tree.
- `print_hists_in()` prints input or collapsed rb-tree entries, depending on `hists__has(hists, need_collapse)`.
- `print_hists_out()` prints output rb-tree entries with period and accumulated period.

## Control Flow
`setup_fake_machine()` first obtains the host machine. It then creates threads and sets their comm strings. Next it synthesizes mmap events for each pid and DSO using `machine__process_mmap_event()`. Finally it iterates DSO symbol definitions, obtains/creates each DSO, marks it loaded, allocates symbols with `symbol__new()`, and inserts them into the DSO's symbol collection. On allocation failure it deletes created threads and returns `NULL`.

## State and Persistence
The function mutates the supplied `struct machines` hierarchy by adding threads, maps, DSOs, and symbols. All state is in-memory and expected to be released by callers through `machines__exit()` and per-test map/thread puts. No files are read or written.

## Dependencies and Integration Points
This fixture is consumed by `hists_filter.c`, `hists_link.c`, `hists_cumulate.c`, and `hists_output.c`. It integrates with perf machine/thread/map/DSO/symbol processing and sort/hist data structures.

## Risks and Edge Cases
- Synthetic kernel mappings are represented via mmap events with `PERF_RECORD_MISC_USER` sample cpumode, which is adequate for tests but not a full kernel event simulation.
- Fixture correctness depends on address macros from `hists_common.h` remaining aligned with fake symbol offsets.
- The debug printers assume entries have valid maps and symbols.

## Test Signals
The file does not define a suite itself. Its signal is indirect: downstream histogram tests fail if synthetic resolution cannot find expected comm/DSO/symbol combinations or if the fixture cannot be allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.h -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.h

## Purpose
Declares the shared constants and helpers for perf histogram tests that operate on a synthetic machine with known pids, maps, IPs, and symbols.

## Important APIs, Types, and Functions
- Defines fake pids: `FAKE_PID_PERF1`, `FAKE_PID_PERF2`, and `FAKE_PID_BASH`.
- Defines fake map bases and length for perf, bash, libc, and kernel.
- Defines symbol offsets/length and derived fake IPs for all symbols used by histogram sample tables.
- Declares `setup_fake_machine(struct machines *machines)`, `print_hists_in(struct hists *hists)`, and `print_hists_out(struct hists *hists)`.

## Control Flow
This header has no executable control flow. Its embedded comment documents the expected synthetic process/DSO/symbol matrix that `setup_fake_machine()` implements.

## State and Persistence
No state is stored by the header. It establishes compile-time constants shared by multiple `.c` tests.

## Dependencies and Integration Points
Forward-declares `struct machine` and `struct machines`; consumers rely on perf histogram and machine headers for full types. It is included by the histogram tests and the shared implementation file.

## Risks and Edge Cases
- If a fake IP macro no longer matches the symbol ranges created in `hists_common.c`, downstream resolution tests will fail or validate the wrong entry.
- The header documents only one synthetic fixture shape; adding new histogram tests should preserve these constants or clearly extend them.

## Test Signals
No direct suite. Correctness is signaled by successful compilation and by downstream histogram tests resolving the declared fake IPs to the intended symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_cumulate.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_cumulate.c

## Purpose
Tests histogram accumulation of child periods and callchain rendering under four modes: no callchains/no children, callchains/no children, children/no callchains, and both callchains and children.

## Important APIs, Types, and Functions
- Static `fake_samples[]` defines ten samples across perf and bash processes.
- `fake_callchains[][10]` encodes synthetic `struct ip_callchain` payloads, including repeated/cyclic-looking xmalloc/malloc chains.
- `add_hist_entries()` resolves samples through `machine__resolve()` and adds them with either `hist_iter_normal` or `hist_iter_cumulative` based on `symbol_conf.cumulate_callchain`.
- `del_hist_entries()` erases output and input rb-tree nodes and deletes hist entries.
- `do_test()` collapses/resorts, output-resorts, then validates rb-tree order, self periods, accumulated child periods, and optional callchain nodes.
- `test1()` through `test4()` set `symbol_conf.use_callchain`, `symbol_conf.cumulate_callchain`, sample bits, sorting, and expected result tables.

## Control Flow
`test__hists_cumulate()` builds an evlist with `cpu-clock`, initializes machines and the fake machine fixture, obtains the first evsel, and runs the four mode-specific tests. Each mode configures global callchain/sorting state, adds hist entries from the same fake samples, validates expected output with `do_test()`, then deletes entries and resets output fields.

## State and Persistence
State is in-memory but includes global perf settings: `symbol_conf.use_callchain`, `symbol_conf.cumulate_callchain`, `callchain_param`, sample bits on the evsel, and output fields. Fake sample map/thread references are retained and later released by `put_fake_samples()`.

## Dependencies and Integration Points
Depends on the shared fake machine fixture, histogram iterators, callchain registration, sort setup, evsel/hists data structures, and rb-tree traversal. Registered as `DEFINE_SUITE("Cumulate child hist entries", hists_cumulate)`.

## Risks and Edge Cases
- The expected order is tightly coupled to perf's sort ordering and callchain accumulation rules.
- `do_test()` contains a TODO noting it only handles callchain validation for a single child node shape.
- Global callchain/symbol settings must be restored by surrounding test infrastructure or reset paths.
- The test expects exact accumulated periods such as 7000 for `perf/main`, so changes in duplicate folding or callchain propagation will surface as failures.

## Test Signals
Passing shows that histogram collapse/output resort preserves expected self periods, child accumulated periods, and callchain node sequences for synthetic perf/bash workloads. Failures identify the first mismatched hist entry or callchain node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_cumulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_filter.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_filter.c

## Purpose
Validates histogram filtering by thread, DSO, symbol, socket, and combined filters while ensuring total sample/entry/period statistics remain invariant and non-filtered statistics change correctly.

## Important APIs, Types, and Functions
- `struct sample` includes pid, IP, resolved thread/map/symbol, and socket.
- `fake_samples[]` supplies ten samples, with one duplicate `perf/perf/main` that collapses to produce nine hist entries.
- `add_hist_entries()` iterates every evsel, resolves samples, sets `al.socket`, and uses `hist_entry_iter__add()` with `hist_iter_normal`.
- `put_fake_samples()` releases stored map references.
- `test__hists_filter()` drives parsing, fake machine setup, sorting, histogram population, collapse/output resort, and filter assertions.

## Control Flow
The test creates an evlist with `cpu-clock` and `task-clock`, initializes the fake machine, calls `setup_sorting()`, and adds the same ten synthetic samples to each evsel. For each evsel it verifies baseline totals: 10 samples, 9 entries, total period 1000, all non-filtered stats equal totals. It then applies and removes filters: bash thread, kernel DSO, symbol string `main`, socket `2`, and a combined thread+DSO filter. After each filter it asserts total stats are unchanged and non-filtered samples/entries/periods match expected reduced counts.

## State and Persistence
The test mutates per-hists filter fields (`thread_filter`, `dso_filter`, `symbol_filter_str`, `socket_filter`) and histogram rb-trees. It also holds map references in static sample entries until cleanup. No persistent storage is used.

## Dependencies and Integration Points
Uses shared histogram fixture, parse-events, evlist/evsel hists, machine resolution, sorting, and `hists__filter_by_*` APIs. Registered as `DEFINE_SUITE("Filter hist entries", hists_filter)`.

## Risks and Edge Cases
- Expected counts depend on the duplicate main sample collapsing into one entry while still counting as three samples for symbol filtering.
- Static sample map references must be put after all evsels are processed to avoid leaks across repeated suite execution.
- Combined filter coverage is limited to thread+DSO, not all possible filter combinations.

## Test Signals
Passing indicates each filter updates `nr_non_filtered_*` and `total_non_filtered_period` correctly without corrupting raw totals. Verbose mode can print intermediate histograms for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_link.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_link.c

## Purpose
Tests matching and linking histograms from two evsels, including common entries, distinct entries, dummy paired entries, and collapsed duplicates.

## Important APIs, Types, and Functions
- `fake_common_samples[]` defines five entries expected to pair between the two hists.
- `fake_samples[2][5]` defines evsel-specific entries; the second evsel has a duplicate `bash/libc/malloc` that collapses.
- `add_hist_entries()` adds common and distinct samples to each evsel via `hists__add_entry()`.
- `find_sample()` matches a hist entry against known sample arrays by thread, map, and symbol.
- `validate_match()` checks `hists__match()` pairs only common entries.
- `validate_link()` checks `hists__link()` creates expected pair/dummy relationships.

## Control Flow
The suite creates an evlist with `cpu-clock` and `task-clock`, builds the fake machine, sets sorting, adds sample entries, and collapse-resorts each hists object. It then selects first and last evsel hists. First it calls `hists__match()` and validates only common samples have pairs. Next it calls `hists__link()` and validates the leader has dummy entries for other-only samples while the other hists entries all have pairs and no dummy entries.

## State and Persistence
All state is in-memory inside evlist/hists and static sample reference fields. Static map references are released at cleanup. The test mutates hist entry pair lists and may create dummy entries during linking.

## Dependencies and Integration Points
Integrates shared fake machine setup, sort setup/reset, evlist parsing, hist entry insertion, and hists match/link APIs. Registered as `DEFINE_SUITE("Match and link multiple hists", hists_link)`.

## Risks and Edge Cases
- Expected dummy count accounts for the collapsed duplicate in the second hists (`ARRAY_SIZE(fake_samples[1]) - 1`); changes in collapse semantics affect the test.
- Validation is based on thread/map/symbol identity, so reference-counting correctness in fixture setup matters.
- Only two hists are linked; multi-way linking behavior is not covered here.

## Test Signals
Passing confirms common entries are matched and distinct entries are linked through dummy pairs with expected counts. Failures print missing matched entries or invalid pair/dummy totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_output.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hists_output.c

## Purpose
Validates histogram output sorting and field selection for several combinations of `field_order` and `sort_order`.

## Important APIs, Types, and Functions
- `fake_samples[]` defines ten samples with cpu, pid, and IP data; duplicate perf main entries collapse depending on sort keys.
- `add_hist_entries()` resolves samples and adds normal hist entries with period 100.
- `del_hist_entries()` removes all output/input rb-tree entries after each case.
- `test1()` verifies default sort (`comm,dso,sym`).
- `test2()` verifies mixed fields `overhead,cpu` with sort key `pid`.
- `test3()` verifies fields-only output `comm,overhead,dso`.
- `test4()` verifies duplicate field handling with `dso,sym,comm,overhead,dso` and sort `sym`.
- `test5()` verifies full sort keys without overhead field using `cpu,pid,comm,dso,sym` and sort `dso,pid`.

## Control Flow
The suite creates a `cpu-clock` evlist, initializes the fake machine, obtains the first evsel, and runs five test functions. Each test sets global `field_order`/`sort_order`, calls `setup_sorting()`, adds hist entries, runs `hists__collapse_resort()` and `evsel__output_resort()`, then walks the output rb-tree in expected order and asserts selected fields and periods.

## State and Persistence
State is in-memory but uses global output/sort fields that are reset after each test with `reset_output_field()`. Static map references are held in `fake_samples[]` and released at suite cleanup.

## Dependencies and Integration Points
Depends on sort-key parsing, output field setup, histogram collapse and output resorting, fake machine resolution, and rb-tree traversal. Registered as `DEFINE_SUITE("Sort output of hist entries", hists_output)`.

## Risks and Edge Cases
- Expected rb-tree order is exact and will fail for legitimate sort-order changes.
- The tests check representative entries in `test2` but not the entire expected output, while other tests are more exhaustive.
- Global `field_order` and `sort_order` must be cleaned between cases to avoid cross-test contamination.

## Test Signals
Passing means selected field/sort combinations produce stable grouping, ordering, and period aggregation. Verbose mode prints formatted hist output for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hists_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hwmon_pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/hwmon_pmu.c

## Purpose
Tests perf's hwmon PMU filename parser and event parsing for simulated hwmon sysfs data, both with explicit PMU names and alias-only event names.

## Important APIs, Types, and Functions
- `test_events[]` defines two temperature events, aliases `temp1`/`temp2`, and expected `union hwmon_pmu_event_key` values.
- `test_pmu_get()` creates a temporary hwmon directory tree under `/tmp`, writes a `name` file plus `temp*_label` and `temp*_input` files, then registers it with `perf_pmus__add_test_hwmon_pmu()`.
- `test_pmu_put()` removes the temporary directory, unlinks the PMU from the global PMU list, and deletes it.
- `do_test()` parses either `hwmon_a_test_hwmon_pmu/<event>/` or the alias/name alone and verifies the resulting evsel uses the expected PMU and config.
- `test__parse_hwmon_filename()` table-tests filename decomposition into type, number, item, alarm flag, and parse success.

## Control Flow
The suite has three test cases. The filename parser case iterates fixed valid and invalid filenames and checks returned fields. The PMU parsing cases build the fake PMU, then for each event parse both canonical event name and alias, once without explicit PMU name and once with explicit PMU name. The parse result must include an evsel for `hwmon_a_test_hwmon_pmu` whose config equals the packed type/number key.

## State and Persistence
The test creates and deletes temporary directories/files under `/tmp/perf-hwmon-pmu-test-*`. It also mutates the process-global PMU list by adding a test PMU and removing it in cleanup. No persistent artifact is intended after `test_pmu_put()`.

## Dependencies and Integration Points
Integrates with `hwmon_pmu.h`, perf PMU registration/scanning, `parse_events()`, and the test suite table `suite__hwmon_pmu`.

## Risks and Edge Cases
- `test_pmu_put()` shells out through `system("rm -fr ...")`; the generated temp path is controlled by `mkdtemp()` but still makes cleanup dependent on shell behavior.
- The error path in `test_pmu_get()` calls `test_pmu_put(dir, hwm)` even when `hwm` can be `NULL`, which would be unsafe if reached as written.
- Alias-only parsing may match multiple events; the test allows `nr_entries >= 1` in that mode and scans for the target PMU.

## Test Signals
Passing proves hwmon filenames parse correctly and synthetic hwmon PMU events/aliases resolve to the expected config. Failures include parse-event error dumps and field mismatch diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/hwmon_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/is_printable_array.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/is_printable_array.c

## Purpose
Tests `is_printable_array()` classification for NUL-terminated printable byte arrays and non-printable or non-terminated inputs.

## Important APIs, Types, and Functions
- `test__is_printable_array()` defines a table of buffer pointer, length, and expected return value.
- Uses two explicit buffers containing control byte `4` in different positions.
- Calls `is_printable_array((char *)t[i].buf, t[i].len)` for each row.

## Control Flow
The test iterates the table and returns `TEST_FAIL` immediately on the first mismatch, logging the row index. Cases include a full `"krava"` array with NUL, the same string without NUL in the length, an empty string with and without NUL, a NULL pointer with length zero, and arrays containing non-printable bytes.

## State and Persistence
No mutable state escapes the stack-local buffers and table. No allocations or file operations occur.

## Dependencies and Integration Points
Depends on `print_binary.h` for `is_printable_array()`, Linux `ARRAY_SIZE`, perf debug output, and `DEFINE_SUITE("is_printable_array", is_printable_array)`.

## Risks and Edge Cases
- The table asserts that length must include the terminating NUL for a printable string to return true.
- It only covers a small ASCII-like input set and one control byte.

## Test Signals
Passing confirms expected truth values for printable, empty, NULL, unterminated, and non-printable buffer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/is_printable_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/kallsyms-split.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/kallsyms-split.c

## Purpose
Regression test ensuring a bad module symbol interleaved in `/proc/kallsyms` does not incorrectly split the main kernel kallsyms map.

## Important APIs, Types, and Functions
- Static fake proc files provide `version`, `modules`, and `kallsyms` content. The kallsyms stream includes main kernel symbols, a module, and a module `u bad_symbol` at an address inside the kernel range.
- `create_proc_dir()` builds `/tmp/perf-test.XXXXXX/proc` and writes the fake proc files.
- `remove_proc_dir()` removes those files/directories and is installed as a signal handler.
- `test__kallsyms_split()` initializes a `struct machine` rooted at the fake directory, creates kernel maps, forces kallsyms loading by setting `symbol_conf` flags, loads the kernel map, and validates map count and symbol ownership.

## Control Flow
The test creates the fake proc root, registers cleanup handlers, initializes the machine with that root, creates kernel maps, sets `ignore_vmlinux`, `ignore_vmlinux_buildid`, and `allow_aliases`, then loads the kernel map from fake kallsyms. It expects exactly two maps (main kernel plus module) and verifies `main_symbol3` resolves to `machine__kernel_map(&m)`, not a split or module map.

## State and Persistence
Creates temporary files under `/tmp` and removes them on normal exit or selected signals. Mutates global `symbol_conf` flags and a stack-local `struct machine`. No artifact should remain after cleanup.

## Dependencies and Integration Points
Exercises machine kernel map creation, DSO/map/symbol loading, fake root support, kallsyms parsing, module range handling, and test registration via `DEFINE_SUITE("split kallsyms", kallsyms_split)`.

## Risks and Edge Cases
- Signal-handler cleanup calls filesystem functions that are not strictly async-signal-safe, but this is test cleanup code.
- The temporary root uses a static template modified by `mkdtemp()`, so repeated invocations in the same process rely on cleanup resetting only `root_dir`, not the template string.
- Global `symbol_conf` mutations may affect later tests unless the broader suite resets them.

## Test Signals
Passing shows the fake mixed kallsyms/module input yields two maps and keeps `main_symbol3` in the main kernel map. Failure messages distinguish setup, load, map-count, and symbol-map mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/kallsyms-split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/keep-tracking.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/keep-tracking.c

## Purpose
Integration test for using a dummy software event to keep tracking records alive while another event is disabled.

## Important APIs, Types, and Functions
- `find_comm(struct evlist *evlist, const char *comm)` scans mmap buffers and counts `PERF_RECORD_COMM` events for the current pid/tid and requested comm.
- `test__keep_tracking()` creates thread/cpu maps, parses `dummy:u` and `cpu-cycles:u`, configures mmap recording, sets the dummy evsel to track comm events while initially disabled, opens/mmaps/enables/disables events, and uses `prctl(PR_SET_NAME, ...)` to generate comm records.
- Local `CHECK__` and `CHECK_NOT_NULL__` macros funnel failures to cleanup.

## Control Flow
The test creates maps for the current tid and online CPUs, builds an evlist with dummy and cycles events, configures record options, sets the first evsel (`dummy`) to record comm events with `disabled=1` and no `enable_on_exec`, then opens and mmaps. First it enables the whole evlist, changes comm to `"Test COMM 1"`, disables the evlist, and expects one comm record. Second it enables the evlist, disables only the last evsel (`cpu-cycles`), changes comm to `"Test COMM 2"`, disables the evlist, and again expects one comm record, proving dummy tracking remained active.

## State and Persistence
State is kernel perf event fds/mmap buffers plus the process comm name changed by `prctl()`. The evlist is disabled/deleted on cleanup, and maps are put. No files are written.

## Dependencies and Integration Points
Uses parse-events, evlist config/open/mmap/enable/disable, evsel disable, perf mmap read APIs, record options, and Linux `prctl`. Registered as `DEFINE_SUITE("Use a dummy software event to keep tracking", keep_tracking)`.

## Risks and Edge Cases
- Requires permission to open dummy and hardware cycle events; otherwise it skips.
- The test changes the current thread comm and does not restore the original name.
- It assumes exactly one comm record is present for each generated name in the mmap buffers.

## Test Signals
Passing confirms tracking events are emitted both when the whole group is enabled and when the non-dummy event is disabled. Failure indicates missing comm records or setup/open/mmap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/keep-tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/kmod-path.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/kmod-path.c

## Purpose
Tests kernel-module path parsing and `is_kernel_module()` classification for plain modules, compressed paths, bracketed kernel DSOs, and special pseudo-DSOs.

## Important APIs, Types, and Functions
- `test()` wraps `__kmod_path__parse()` and validates `struct kmod_path` fields `kmod`, `comp`, and optional allocated `name`.
- `test_is_kernel_module()` validates `is_kernel_module(path, cpumode)` for unknown/kernel/user cpumodes.
- Macros `T()` and `M()` make the test table compact.
- `test__kmod_path__parse()` contains the table for module and non-module path forms.

## Control Flow
The suite runs table rows for `.ko` paths, optional `.ko.gz` and `.gz` behavior under `HAVE_ZLIB_SUPPORT`, bracketed module names, dotted module names, vDSO/vsyscall variants, and `[kernel.kallsyms]`. For each parse row it checks whether the path is a module, whether it is compressed, and whether allocated names match normalized bracketed module names. For each classification row it checks cpumode-dependent kernel-module status.

## State and Persistence
Only stack-local `struct kmod_path` and optional heap-allocated `m.name` are used; `m.name` is freed per row. No persistent state exists.

## Dependencies and Integration Points
Exercises DSO path parsing from `dso.h`, cpumode constants from perf events, zlib-conditional compressed module behavior, and test registration via `DEFINE_SUITE("kmod_path__parse", kmod_path__parse)`.

## Risks and Edge Cases
- Coverage differs by build configuration because compressed-path cases are compiled only with zlib support.
- The same `.ko` and bracketed cases are repeated, likely to catch idempotence/regression but not adding new scenarios.
- Module classification intentionally returns false for user cpumode even if the path string resembles a module.

## Test Signals
Passing confirms normalized module names, compression flags, and cpumode-sensitive module detection match expectations across path styles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/kmod-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/maps.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/maps.c

## Purpose
Tests `struct maps` overlap handling for merging kcore maps around BPF program maps and for inserting maps that split or eclipse existing ranges.

## Important APIs, Types, and Functions
- `struct map_def` holds expected map name/start/end triples.
- `check_maps_cb()`, `failed_cb()`, and `check_maps()` compare actual map rb-tree order, ranges, DSO names, and refcounts against expected arrays.
- `test__maps__merge_in()` validates `maps__merge_in()`.
- `test__maps__fixup_overlap_and_insert()` validates `maps__fixup_overlap_and_insert()`.

## Control Flow
The merge test creates maps for three BPF programs, inserts them, then creates kcore maps. Merging `kcore1` across the whole range should split around BPF maps. Merging hidden `kcore2` should not alter the expected layout. Merging `kcore3` partly hidden by existing maps should add only the new tail range. The fixup test starts with target and next maps, inserts a split map inside target and expects target to be split into two ranges around it, then inserts an eclipse map covering `next_map` and expects `next_map` to be removed.

## State and Persistence
All state is heap-resident maps/DSOs and a `struct maps` object. Refcounts are part of validation; cleanup uses `maps__zput()` and `map__zput()`. No external state is touched.

## Dependencies and Integration Points
Exercises core map insertion, overlap fixup, range splitting, DSO-backed map creation, and test suite registration through `suite__maps` with two test cases.

## Risks and Edge Cases
- Exact refcount value `1` is asserted for each expected map, so ownership changes can fail this test even if ranges are correct.
- The tests use synthetic names/ranges and do not cover every overlap geometry.
- `check_maps()` assumes iteration order matches expected sorted order.

## Test Signals
Passing shows overlap merge and insert APIs preserve protected BPF ranges, split/eclipsed maps correctly, and maintain expected reference ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mem.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/mem.c

## Purpose
Tests human-readable formatting of memory data source snoop and level fields.

## Important APIs, Types, and Functions
- `check(union perf_mem_data_src data_src, const char *string)` allocates `mem_info`, stores the data source, formats snoop and level strings using `perf_mem__snp_scnprintf()` and `perf_mem__lvl_scnprintf()`, and compares against expected output.
- `test__mem()` constructs several `union perf_mem_data_src` cases for L4 hit, remote L4 hit, PMEM miss, remote PMEM miss, and forwarded remote RAM miss.

## Control Flow
The suite zeroes a data source, mutates fields across scenarios, and ORs together `check()` return values. Each `check()` creates a new mem_info object, formats into a fixed 100-byte buffer, releases the object, and asserts exact string equality.

## State and Persistence
No persistent state. Each scenario uses stack-local data and a short-lived `mem_info`.

## Dependencies and Integration Points
Exercises `util/mem-events.h`, `util/mem-info.h`, `union perf_mem_data_src`, and formatting helpers used by perf mem reports. Registered as `DEFINE_SUITE("Test data source output", mem)`.

## Risks and Edge Cases
- Expected strings are exact, so small display wording changes will fail the test.
- The same `src` object is mutated across cases; fields not explicitly reset can carry forward intentionally, such as snoop-forward on the final RAM case.
- Buffer size is sufficient for these cases but not a general formatter stress test.

## Test Signals
Passing means selected local/remote, hit/miss, PMEM/RAM, and snoop-forward combinations render as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mem2node.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/mem2node.c

## Purpose
Tests address-to-NUMA-node lookup built from perf environment memory-node metadata.

## Important APIs, Types, and Functions
- `test_nodes[]` describes node ids and CPU bitmap strings.
- `get_bitmap()` converts a CPU map string into a Linux bitmap via `perf_cpu_map__new()` and `__set_bit()`.
- `test__mem2node()` builds a `perf_env` with three `memory_node` entries and memory block size `0x100`, initializes `mem2node`, queries selected addresses, and tears down.

## Control Flow
For each synthetic node, the test sets node id, size `10`, and CPU bitmap. It initializes `mem2node__init(&map, &env)`, then checks addresses in block 0 map to node 0, blocks 1 and 2 to node 1, blocks 5 and 6 to node 3, and holes/out-of-range addresses return `-1`. It frees each bitmap and exits the map.

## State and Persistence
State is stack-local environment and `mem2node` map plus heap-allocated bitmaps. No files or global state are modified.

## Dependencies and Integration Points
Uses perf CPU maps, Linux bitmaps, `perf_env`, `memory_node`, and `mem2node` APIs. Registered as `DEFINE_SUITE("mem2node", mem2node)`.

## Risks and Edge Cases
- Node `size` is fixed to 10 for all entries, and the CPU bitmap positions are used as memory block indexes for the test.
- The test covers holes and one out-of-range high address but not overlapping node bitmaps.
- Allocation failure in `get_bitmap()` fails via test assertions before map initialization.

## Test Signals
Passing confirms `mem2node__node()` maps block-aligned addresses to expected node ids and returns `-1` for unmapped blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mem2node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mmap-basic.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/mmap-basic.c

## Purpose
Tests perf mmap sample delivery for syscall tracepoints and user-space counter reading through the perf event mmap page.

## Important APIs, Types, and Functions
- `test__basic_mmap()` opens tracepoint evsels for `sys_enter_getsid`, `sys_enter_getppid`, and `sys_enter_getpgid`, mmaps events, invokes syscalls random counts, reads samples, maps sample ids back to evsels, and checks counts.
- `enum user_read_state` and `set_user_read()` read/write PMU `rdpmc` sysfs controls when available.
- `test_stat_user_read(u64 event, enum user_read_state enabled)` scans core PMUs, opens a hardware event, mmaps it, validates `perf_event_mmap_page` user-read capabilities, reads counts, runs busy loops, and verifies monotonic count deltas.
- Four wrappers test instructions/cycles with user reading enabled or disabled.

## Control Flow
The basic mmap test binds the process to the first online CPU, creates per-thread tracepoint events with wakeup events and sample IDs, maps the evlist, generates syscalls, drains mmap records, parses samples, counts by evsel index, and compares observed counts to generated counts. The user-read tests create a dummy thread map, iterate core PMUs, optionally change rdpmc state, restrict affinity to PMU CPUs, open/mmap an evsel, validate mmap page flags/index/width against expected support, read initial and loop counts, then close/unmap and restore rdpmc and affinity.

## State and Persistence
State includes kernel perf event fds, mmap buffers, process CPU affinity, and optionally sysfs `rdpmc` settings that are restored per PMU. No repository files are changed. The basic test uses `rand()` for expected counts but records them before generating syscalls.

## Dependencies and Integration Points
Integrates tracepoint evsel creation, evlist mmap/read/sample parsing, id-to-evsel lookup, PMU scanning, libperf evsel mmap APIs, CPU affinity helpers, and architecture-specific user counter support. Registered as `suite__basic_mmap`.

## Risks and Edge Cases
- Requires tracepoint and perf_event permissions; many failure paths are reported as skips or failures depending on stage.
- Affinity changes can fail on constrained environments.
- User-read behavior depends on architecture, PMU sysfs, hybrid PMU semantics, and kernel support for `cap_user_rdpmc`.
- The busy-loop monotonic check is basic and does not assert exact event counts.

## Test Signals
Passing proves mmap sample delivery can be parsed and attributed to evsels, and user-space counter access flags/counts match enabled/disabled expectations for supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mmap-basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mmap-thread-lookup.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/mmap-thread-lookup.c

## Purpose
Tests that synthesized thread mmap events populate machine/thread maps sufficiently for `thread__find_map()` to locate per-thread anonymous executable mappings.

## Important APIs, Types, and Functions
- `struct thread_data` stores pthread id, Linux tid, mmap address, and a readiness pipe.
- `thread_init()` mmaps one page with read/write/exec permissions and records the thread tid.
- `thread_fn()` initializes a worker thread, signals readiness, waits for `go_away`, then unmaps.
- `threads_create()` initializes main thread data and creates worker threads.
- `synth_all()` uses `perf_event__synthesize_threads()`.
- `synth_process()` uses `thread_map__new_by_pid()` and `perf_event__synthesize_thread_map()`.
- `mmap_events()` creates threads, synthesizes events into a host machine, then verifies each thread's map can be resolved.

## Control Flow
The suite runs `mmap_events()` twice: once synthesizing all threads globally, once synthesizing a process thread map. For each run, it creates four total thread entries including main, initializes a host machine, invokes the synthesizer, destroys threads, then for each `thread_data` finds or creates the machine thread and calls `thread__find_map()` on `td->map + 1`. Each lookup must return a map.

## State and Persistence
The test creates pthreads, anonymous mmaps, readiness pipes, and in-memory machine state. `go_away` controls worker lifetime. All mmaps and threads are cleaned up; no persistent files are used.

## Dependencies and Integration Points
Exercises synthetic event generation, machine event processing, thread maps, map lookup, perf environment initialization, and pthread/syscall APIs. Registered as `DEFINE_SUITE("Lookup mmap thread", mmap_thread_lookup)`.

## Risks and Edge Cases
- Requires thread synchronization to ensure mappings exist before synthesis; readiness pipes handle worker initialization.
- Main thread mapping is initialized without a pthread and cleaned separately.
- `go_away` is a plain static int shared across threads; sufficient for this short test but not a robust synchronization primitive.

## Test Signals
Passing confirms both global and process-scoped synthesis paths allow every thread object to find its synthetic mmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/mmap-thread-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-all-cpus.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-all-cpus.c

## Purpose
Tests counting the `syscalls:sys_enter_openat` tracepoint across all online CPUs by pinning the process to each CPU and verifying per-CPU counts.

## Important APIs, Types, and Functions
- `test__openat_syscall_event_on_all_cpus()` creates a current-thread map, online CPU map, tracepoint evsel, opens it over all CPUs for the thread, generates `openat()` calls per CPU, reads counts per CPU, and validates expected values.
- Uses `perf_cpu_map__for_each_cpu()`, `sched_setaffinity()`, `evsel__open()`, `evsel__read_on_cpu()`, and `perf_counts()`.

## Control Flow
The test creates maps, opens `sys_enter_openat`, then iterates online CPUs. It skips CPUs outside `CPU_SETSIZE`, binds to each CPU, performs `111 + idx` openat calls on `/etc/passwd`, and clears the CPU from the affinity set. It assigns the cpumap to `evsel->core.cpus`, reads each CPU counter, and compares the count to the generated call count.

## State and Persistence
State includes process CPU affinity, perf event fds/counts, and transient file descriptors opened on `/etc/passwd`. FDs are closed immediately, and perf fds/maps are released. It does not restore the original affinity mask explicitly.

## Dependencies and Integration Points
Depends on tracing sysfs availability, perf_event permissions, CPU maps, thread maps, evsel counts, and test suite registration as `suite__openat_syscall_event_on_all_cpus`.

## Risks and Edge Cases
- CPUs above `CPU_SETSIZE` are ignored due to fixed `cpu_set_t`.
- Permission or tracepoint availability failures produce skips.
- Open failures for `/etc/passwd` are not checked before `close(fd)`, though the syscall still triggers the tracepoint.
- Original CPU affinity is not restored.

## Test Signals
Passing indicates per-CPU tracepoint counting attributes the generated openat calls to the CPU on which they were made.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-all-cpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-tp-fields.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-tp-fields.c

## Purpose
Tests raw tracepoint sample parsing for `syscalls:sys_enter_openat`, specifically extracting the `flags` field from the tracepoint payload.

## Important APIs, Types, and Functions
- `test__syscall_openat_tp_fields()` configures an evlist for mmap/raw samples, creates a tracepoint evsel, opens and mmaps it for the current pid, generates one `openat()`, reads samples, parses them, and extracts `flags` through `evsel__intval()`.
- Uses `record_opts`, `evlist__create_maps()`, `evsel__config()`, `evlist__open()`, `evlist__mmap()`, `evlist__enable()`, `perf_mmap__read_event()`, and `evsel__parse_sample()`.

## Control Flow
The test builds an evlist with `sys_enter_openat`, creates maps for a mmap-using target, configures raw samples/no buffering, sets the thread pid to the current process, opens and maps, enables events, calls `openat(AT_FDCWD, "/etc/passwd", O_RDONLY | O_DIRECTORY)`, then polls up to five times while draining mmap buffers. On a `PERF_RECORD_SAMPLE`, it parses the sample, extracts `flags`, compares it to the generated flags, and returns `TEST_OK`.

## State and Persistence
State is perf event fds, mmap buffers, and one attempted `openat()` syscall. The opened fd is not captured or closed because the chosen flags should fail for `/etc/passwd` as a directory, but the tracepoint is generated either way. All evlist resources are deleted.

## Dependencies and Integration Points
Integrates raw tracepoint sample parsing, tracepoint field lookup, mmap polling, current-thread target maps, and test registration as `suite__syscall_openat_tp_fields`.

## Risks and Edge Cases
- Requires tracepoint access and perf permissions.
- Relies on the `flags` field name and layout in the kernel tracepoint format.
- Poll count is bounded; slow systems may fail with "no events".

## Test Signals
Passing confirms a raw tracepoint sample can be parsed and its `flags` field matches the syscall argument.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-tp-fields.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall.c

## Purpose
Tests basic per-thread counting of the `syscalls:sys_enter_openat` tracepoint for the current process.

## Important APIs, Types, and Functions
- `test__openat_syscall_event()` creates a thread map for current pid, creates a tracepoint evsel, opens it per thread, performs 111 `openat()` calls, reads CPU 0/thread 0 count, and checks exact count.
- Uses `evsel__newtp()`, `evsel__open_per_thread()`, `evsel__read_on_cpu()`, `perf_counts()`, and perf tracing error helpers.

## Control Flow
The test creates a thread map, creates `syscalls:sys_enter_openat`, skips if the tracepoint cannot be opened, opens it for the thread, loops 111 times opening and closing `/etc/passwd`, reads the counter, compares it with 111, closes perf fds, deletes evsel, and releases the thread map.

## State and Persistence
State is kernel perf event fd/count storage and transient file descriptors for `/etc/passwd`. No persistent files are created or modified.

## Dependencies and Integration Points
Depends on tracing path availability, perf_event permissions, thread maps, evsel count storage, and suite registration as `suite__openat_syscall_event`.

## Risks and Edge Cases
- Permission/tracepoint failures are treated as skips.
- Open return values are not checked before `close(fd)`, but syscall entry counting does not require successful opens.
- It reads CPU index 0/thread index 0, assuming per-thread open maps counts there.

## Test Signals
Passing confirms the tracepoint counter observes exactly the generated number of `openat()` syscalls for the current thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/parse-events.c

## Purpose
Large table-driven and helper-driven suite validating perf event string parsing. It covers tracepoints, raw/numeric/symbolic events, cache events, breakpoints, modifiers, PMU-qualified events, groups, leader sampling, pinned/exclusive flags, named events, all tracepoints, sysfs PMU events, aliases, and event term parsing.

## Important APIs, Types, and Functions
- Assertion helpers `check_evlist()`/`TEST_ASSERT_EVLIST` and `check_evsel()`/`TEST_ASSERT_EVSEL` format evlists/evsels on failure.
- `num_core_entries()` accounts for wildcard expansion across hybrid/core PMUs.
- Many `test__checkevent_*()` functions validate specific parsed `perf_event_attr` fields: type/config/config1-4, sample type/period, exclude flags, precise IP, breakpoint type/length, pinned/exclusive, names, PMU ownership, group leader/index/member state, and `sample_read`.
- Group validators `test__group1()` through `test__group5()`, `test__group_gh1()` through `test__group_gh4()`, `test__leader_sample1()`, and `test__leader_sample2()` verify event grouping, group modifiers, host/guest modifiers, and sample-read behavior.
- `struct evlist_test` pairs an event string, optional validity predicate, and checker. `test__events[]` and `test__events_pmu[]` are the main matrices.
- `struct terms_test` and `test__checkterms_simple()` validate parsed config terms.
- `test_event()`, `test_events()`, `test_event_fake_pmu()`, `test_term()`, and `test_terms()` are generic drivers.
- `test__pmu_events()` scans sysfs PMU event files and attempts to parse each non-parameterized event.
- `test_alias()` and alias tests validate PMU alias equivalence.

## Control Flow
Suite cases in `tests__parse_events[]` run six lanes. `events2` iterates `test__events[]`, replacing `default_core` placeholders with the detected core PMU name, parses with `__parse_events(..., fake_tp=true)`, and dispatches to the checker. `pmu_events` scans real sysfs PMU event directories, skips special or parameterized entries, parses `pmu/event=name/u`, and for core PMUs also checks mixed legacy/PMU syntax. `pmu_events2` runs the explicit PMU-qualified matrix. `alias` finds a sysfs PMU alias and checks alias/event parse equivalence. `pmu_events_alias2` uses fake PMU parsing for hyphenated aliases. `terms2` parses a comma-separated term string and checks the resulting linked list of `parse_events_term` entries.

## State and Persistence
Most state is in-memory evlists/evsels and parse error objects. Some tests read sysfs and tracing directories, count available tracepoints, inspect PMU event files, and read PMU alias files. No files are written. The suite adapts to platform state through validity predicates such as Intel PT presence, ACR format support, s390 KVM tracepoint availability, and default core PMU format support.

## Dependencies and Integration Points
This is the central test consumer of `parse-events.h`, PMU scanning, tracefs/sysfs helpers, breakpoint constants, evsel formatting, evlist formatting, event term parsing, and fake PMU/fake tracepoint parse modes. Registered as `suite__parse_events` with multiple named test cases and permission/alias skip reasons.

## Risks and Edge Cases
- Many expectations depend on hybrid PMU expansion; `num_core_entries()` and `perf_pmus__num_core_pmus()` are used to avoid single-PMU assumptions.
- Some TODO comments document known behavior: software events are not always grouped with hardware events across multiple PMUs, and group modifiers are not always copied to split group leaders.
- Real sysfs PMU event scanning can skip or fail based on host PMU files, permissions, parameterized events, or event names containing special characters.
- Exact parser names and modifier semantics are tightly encoded; intentional parser changes require coordinated test updates.
- `combine_test_results()` preserves failures over skips and preserves skip if all non-OK results are skips, which affects suite-level status aggregation.

## Test Signals
Passing indicates broad event parser coverage: correct attr fields for individual events, correct group/leader topology, correct modifier semantics, valid term parsing, parseability of host PMU events, alias equivalence, and platform-conditional behavior. Failures include formatted evsel/evlist details and parse error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-metric.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/parse-metric.c

## Purpose
Tests parsing and evaluation of perf metric expressions from the test PMU metrics table using synthetic runtime counter values.

## Important APIs, Types, and Functions
- `struct value` maps event names to synthetic counts.
- `find_value()` returns a configured event count or zero.
- `load_runtime_stat()` allocates aggregate stats and fills each evsel's count, enabled, and running values.
- `compute_single()` locates a `metric_expr` by metric name in `evlist->metric_events` and evaluates it with `test_generic_metric()`.
- `__compute_metric()` is the common driver: creates evlist, binds CPU map `0`, parses metric groups from `find_core_metrics_table("testarch", "testcpu")`, allocates stats, loads runtime counts, evaluates one or two metric names, then cleans up.
- Test functions cover IPC, Frontend_Bound_SMT, cache miss cycles, DCache L2 hits/misses, recursion failure, memory bandwidth, and metric groups.

## Control Flow
Each test builds a small `struct value` array with event counts, calls `compute_metric()` or `compute_metric_group()`, and asserts expected ratios. The shared compute path prepares an evlist in stat mode on CPU 0, parses the named metric or group into metric events, allocates stats, injects synthetic counts, evaluates requested metric expressions, frees stats, releases CPU map, and deletes the evlist. `test__parse_metric()` runs all metric cases in sequence.

## State and Persistence
All state is in-memory: evlists, CPU maps, metric events, allocated stats, and synthetic counts. No sysfs or perf fds are opened for real measurement.

## Dependencies and Integration Points
Depends on metric group parsing, PMU events test tables, expression evaluation, stat count structures, evlist stat allocation, and PMU helpers. Registered as `DEFINE_SUITE("Parse and process metrics", parse_metric)`.

## Risks and Edge Cases
- Exact floating-point equality is used for expected ratios such as `1.5`, `0.45`, `0.3`, `0.7`, and `1.28`.
- Missing event names resolve to zero, which is useful for synthetic setup but can hide accidental omissions unless expected values expose them.
- Recursion tests expect `compute_metric()` to return `-1` for recursive metric definitions `M1` and `M3`.
- The test relies on `testarch/testcpu` metrics being present and stable in the bundled PMU metrics table.

## Test Signals
Passing demonstrates metric parser/evaluator correctness for arithmetic ratios, nested derived metrics, metric groups, bandwidth unit math, and recursion detection using controlled counter data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/parse-metric.c -->
