# Research Group subset-b-008395

This grouped report covers FoundationDB contrib utilities and vendored helper libraries under `sources/storage-engines/foundationdb/contrib`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/plot.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/plot.py

## Purpose
`plot.py` visualizes the GRV proxy simulation results produced by `proxy_model.py`. It turns per-priority request, queue, latency, limiter rate, limiter budget, and release-time series into a fixed 3x3 matplotlib dashboard.

## Important APIs, Types, And Functions
The central API is `Plotter(results)`, where `results` is expected to be a `ProxyModel.Results` instance with dictionaries such as `started`, `queued`, `latencies`, `unprocessed_queue_sizes`, `rate`, `released`, `limit`, `limit_and_budget`, and `budget`. `Plotter.add_plot(data, time_resolution, label, use_avg=False)` buckets numeric values by `t // time_resolution * time_resolution`; `Plotter.add_plot_with_times(data, label)` plots raw ordered key/value series; `display(time_resolution=0.1)` lays out the dashboard.

## Control Flow
`display` creates a large figure, draws request starts, queued requests, and maximum unprocessed queue sizes in the first row, then allocates one subplot per priority for latency percentiles and one subplot per priority for limiter/rate/budget diagnostics. Latencies are derived by selecting median, 90th percentile, and max values from per-second latency lists before plotting. The function ends with `plt.show()`.

## State And Persistence Behavior
The module does not persist data. It reads the supplied result object, aggregates values in local dictionaries, and mutates only matplotlib global plotting state. It assumes latency vectors are already ordered by append order and uses integer-second keys present in `ProxyModel.Results`.

## Dependencies And Integration Points
It depends on `matplotlib.pyplot` and the shape of `ProxyModel.Results`. It integrates with `priority.Priority` only indirectly through dictionary keys, whose `__str__` labels appear in legends and y-axis text.

## Risks And Edge Cases
`add_plot` and `add_plot_with_times` are defined without `self`, so they must be called as class functions as this file does. Latency percentile lookup does not sort samples and can fail to represent real percentiles if completion latencies are not appended in sorted order. The fixed 3x3 grid can overflow if more priorities or limiter series are added. Empty dicts produce empty plots, but latency lists are guarded.

## Test Signals
Useful tests would construct synthetic `ProxyModel.Results`, call `display` under a noninteractive matplotlib backend, and assert expected subplot/line counts and bucketed values. Current signals are mostly manual: rendered charts should show queued/started rates, queue sizes, latency curves, and limiter budgets per priority.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/plot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/priority.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/priority.py

## Purpose
`priority.py` defines the priority ordering used by the GRV proxy simulator. It gives system, default, and batch traffic comparable objects with stable labels.

## Important APIs, Types, And Functions
`Priority(priority_value, label)` stores a numeric ordering and display label. `functools.total_ordering` derives the remaining comparisons from `__lt__`; `__str__` returns the label and `__repr__` returns the quoted label. Module constants `Priority.SYSTEM`, `Priority.DEFAULT`, and `Priority.BATCH` are assigned values 0, 1, and 2.

## Control Flow
There is no runtime control flow beyond object construction. Priority objects are consumed as dictionary keys and compared in queue processing and budget calculations.

## State And Persistence Behavior
The file creates three singleton-like class attributes. These objects are mutable by convention but not mutated by the simulator after initialization. Nothing is persisted.

## Dependencies And Integration Points
It depends only on `functools`. `workload_model.Request.__lt__`, `proxy_model.ProxyModel.process_requests`, and predefined workload/ratekeeper maps rely on this ordering to process lower numeric priorities first and to sum traffic at or above a priority threshold.

## Risks And Edge Cases
`__eq__` is not explicitly implemented even though `total_ordering` normally expects it; object identity equality is therefore retained. This is acceptable while singleton constants are reused everywhere, but separately constructed `Priority(1, "Default")` objects would compare with `<` but not compare equal. The class has no hash override, so identity hashing matches identity equality.

## Test Signals
Tests should assert `SYSTEM < DEFAULT < BATCH`, string labels, repr labels, and dictionary-key behavior with the predefined singleton objects. A regression would show up as changed request-queue ordering or limiter budget attribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/priority.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/proxy_model.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/proxy_model.py

## Purpose
`proxy_model.py` implements a discrete-event model of FoundationDB GRV proxy request admission. It simulates request arrival, priority ordering, queueing, ratekeeper limits, limiter budget behavior, and resulting latency/throughput metrics.

## Important APIs, Types, And Functions
`Task(time, fxn)` is heap-ordered by time and represents scheduled simulation events. `Limiter` defines parameter carrier classes (`UpdateRateParams`, `UpdateLimitParams`, `CanStartParams`, `UpdateBudgetParams`) and the abstract limiter interface.

Limiter implementations model different admission policies: `OriginalLimiter` uses ratekeeper rate and a small bounded token budget; `PositiveBudgetLimiter` lets budget accumulate positively; `ClampedBudgetLimiter` caps negative debt; `TimeLimiter` and `TimePositiveBudgetLimiter` add `locked_until` throttling after overshoot; `SmoothingLimiter` uses `Smoother` to compare smoothed rate limits with smoothed releases; `SmoothingBudgetLimiter` adds a positive budget and records rich diagnostics.

`ProxyModel.Results` initializes per-priority per-second maps for starts, queues, latencies, and outstanding queue sizes plus sparse limiter diagnostic maps. `ProxyModel(duration, ratekeeper_model, workload_model, Limiter)` wires one limiter per workload priority. `run`, `update_rate`, `receive_request`, and `process_requests` drive the simulation.

## Control Flow
`run` initializes limiter rates, schedules the first request for each priority, then repeatedly pops the earliest `Task` from a heap until simulated time reaches `duration`. `update_rate` refreshes every limiter from the ratekeeper and schedules itself 0.01 seconds later. `receive_request` pushes a request into the priority heap, records queued count, and schedules the next request for that priority if the workload can produce one.

`process_requests(last_time)` computes elapsed time, updates limiter limits, then consumes queued requests while the head request's limiter permits starting it. Completing a request can re-enable a workload that was blocked by `max_outstanding`. After admission, budget updates run for all priorities using total started work, started-at-or-above-priority counts, the minimum priority admitted in the batch, last batch size, queue-empty information, and elapsed time. The method records outstanding sizes and schedules itself again after 0.001 seconds.

## State And Persistence Behavior
All state is in memory: simulated time, log time, task heap, request heap, request-scheduled flags, limiter state, workload outstanding counts, and results dictionaries. Limiter state can include rates, limits, budgets, smoothed totals, released deltas, and lockout timestamps. There is no file or database persistence.

## Dependencies And Integration Points
The model imports `Priority` for ordering and priority thresholds and `Smoother` for exponentially smoothed limiter variants. It expects `ratekeeper_model.get_limit(time, priority)`, `workload_model.priorities()`, `workload_model.next_request(time, priority)`, and `workload_model.request_completed(request)` to match the interfaces from sibling modules. `plot.py` consumes `ProxyModel.Results`.

## Risks And Edge Cases
`Task.__lt__` compares only time, so same-time event ordering is heap implementation dependent. `request_queue` is a heap of `Request` objects ordered only by priority, not arrival time within priority. `ProxyModel.Results.init_result` uses `copy.copy(starting_value)` so list values are distinct shallow copies, which works for lists but would not deeply copy nested defaults. Several limiter formulas divide by `self.rate`; a zero rate can cause failures in time-based limiter overshoot paths. Assertions require each workload to produce an initial request.

## Test Signals
Tests should run deterministic workloads/ratekeepers and assert queued counts, started counts, latency buckets, lockout behavior, and budget diagnostics. Good regression signals include starvation behavior for batch traffic, max outstanding backpressure, zero-rate workloads, fixed-rate throughput, and deterministic output under seeded request distributions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/proxy_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/rate_model.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/rate_model.py

## Purpose
`rate_model.py` provides simple rate sources for the GRV proxy simulator. These models supply request rates or ratekeeper limits as functions of simulated time.

## Important APIs, Types, And Functions
`RateModel.get_rate(time)` is the base interface. `FixedRateModel(rate)` returns a constant; `UnlimitedRateModel` intends to represent an effectively unbounded rate of `1e9`; `IntervalRateModel(intervals)` stores sorted `(start_time, rate)` pairs and returns the active interval; `SawtoothRateModel(low, high, frequency)` alternates between low and high rates; `DistributionRateModel(distribution, frequency)` samples a rate from a callable and holds it for a frequency window.

## Control Flow
Consumers call `get_rate` at simulated times. Fixed and unlimited models return stored values. Interval lookup returns zero before the first interval, scans for the interval preceding the requested time, truncates older intervals from `self.intervals`, and returns the current rate. Sawtooth uses `int(2 * time / frequency) % 2` to alternate. Distribution refreshes when no prior sample exists or when the time has moved to a new frequency bucket.

## State And Persistence Behavior
Rates are in-memory only. `IntervalRateModel` mutates `self.intervals` by discarding prior intervals, so it assumes monotonic time. `DistributionRateModel` stores `last_change` and `rate`, making it stateful and also monotonic-time-oriented. Nothing is persisted.

## Dependencies And Integration Points
The module imports `numpy` for random distribution call sites, though only `DistributionRateModel` receives callables. `ratekeeper_model.py` and `workload_model.py` instantiate these classes in predefined scenarios.

## Risks And Edge Cases
`UnlimitedRateModel.__init__` sets `self.rate` without calling `FixedRateModel.__init__`, but the effect is equivalent for current fields. `IntervalRateModel` gives incorrect answers for non-monotonic time after truncating previous intervals. `SawtoothRateModel` divides by `frequency`; zero frequency is not guarded. `DistributionRateModel` uses a bucket comparison that is sensitive to the meaning of `last_change`, not just absolute bucket number.

## Test Signals
Tests should cover fixed and unlimited returns, interval boundaries, pre-first-interval zero behavior, monotonic interval truncation, sawtooth phase changes, zero-rate handling, and seeded distribution refresh cadence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/rate_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/ratekeeper_model.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/ratekeeper_model.py

## Purpose
`ratekeeper_model.py` maps traffic priorities to rate limit models. It represents the ratekeeper side of the GRV proxy simulation.

## Important APIs, Types, And Functions
`RatekeeperModel(limit_models)` stores a dictionary keyed by `Priority` objects. `get_limit(time, priority)` delegates to the selected rate model's `get_rate(time)`. `predefined_ratekeeper` contains named scenarios: `default200_batch100`, `default_sawtooth`, `default_uniform_random`, `default_trickle`, and `default1000`.

## Control Flow
Runtime control flow is simple delegation. Predefined scenarios are built at import time from `rate_model.UnlimitedRateModel`, `FixedRateModel`, `SawtoothRateModel`, and `DistributionRateModel`.

## State And Persistence Behavior
State is in-memory and mostly delegated to the underlying rate models. Random and interval models can mutate internal rate state during calls. No state is persisted.

## Dependencies And Integration Points
It imports `numpy`, `rate_model`, and `Priority`. `proxy_model.Limiter.update_rate` calls `RatekeeperModel.get_limit` for each priority. Scenario names are likely selected by driver scripts outside this subset.

## Risks And Edge Cases
Missing priority keys raise `KeyError`. Random ratekeeper scenarios are nondeterministic unless numpy's random seed is controlled. Some scenarios set batch rate to zero, which can expose divide-by-zero risks in limiter implementations that use rate as a divisor.

## Test Signals
Tests should verify every predefined model has expected priority keys, fixed limits return expected values, sawtooth/random scenarios remain in valid ranges, and missing priorities fail clearly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/ratekeeper_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/smoother.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/smoother.py

## Purpose
`smoother.py` implements an exponential smoother used by smoothed GRV proxy limiter policies. It tracks a total and a lagging estimate, then derives smoothed totals and rates.

## Important APIs, Types, And Functions
`Smoother(folding_time)` initializes smoothing with a time constant. `reset(value)` resets time, total, and estimate. `set_total(time, total)` converts an absolute total to a delta. `add_delta(time, delta)` first advances the estimate, then increments total. `smooth_total(time)` updates and returns the estimate. `smooth_rate(time)` updates and returns `(total - estimate) / folding_time`. `update(time)` advances the estimate by `1 - exp(-elapsed / folding_time)` when elapsed is positive.

## Control Flow
The class is call-driven. Every public read/write method funnels through `update`, which is a no-op for non-positive elapsed time and an exponential interpolation toward `total` for positive elapsed time.

## State And Persistence Behavior
The object stores `folding_time`, `time`, `total`, and `estimate` in memory. There is no persistence or external state.

## Dependencies And Integration Points
It depends on Python's `math.exp`. `proxy_model.SmoothingLimiter` uses two instances to smooth rate limits and released request counts, and `SmoothingBudgetLimiter` records smoothed values into results.

## Risks And Edge Cases
`folding_time` is not validated; zero causes division by zero and negative values invert the smoothing behavior. Non-monotonic time is ignored because negative elapsed does not update, which can leave `self.time` ahead of future calculations. Large elapsed values effectively snap the estimate to total.

## Test Signals
Tests should assert reset behavior, monotonic convergence, rate calculation after deltas, no update on same/earlier time, and error/guard behavior for zero folding time if validation is added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/smoother.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/workload_model.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/workload_model.py

## Purpose
`workload_model.py` generates request streams for the GRV proxy simulator. It models per-priority arrivals, batch sizes, inter-arrival distributions, and outstanding-request backpressure.

## Important APIs, Types, And Functions
`Request(time, count, priority)` is heap-ordered by priority. `PriorityWorkloadModel` combines a priority, rate model, batch generator, request interval generator, and `max_outstanding`. `next_request(time)` returns a future `Request` or `None` when outstanding work is capped; `request_completed(request)` decrements outstanding count and reports whether generation should resume.

`WorkloadModel` wraps a priority-to-model map. `Distribution` provides `exponential`, `uniform`, and `fixed` callables. `DistributionBatchGenerator.next_batch()` returns `ceil(distribution(size))`. `DistributionRequestGenerator.next_request_interval(rate)` returns a sampled interval based on `1/rate` or `1e9` for zero rate. `predefined_workloads` defines named scenarios including `slow_exponential`, `fixed_uniform`, `batch_starvation`, `default_low_high_low`, and several fixed default rates.

## Control Flow
The simulator asks a priority workload for its next request. If outstanding work is at or above the cap, generation pauses. Otherwise a batch size is sampled, outstanding count increases immediately, an interval is sampled from the current rate, and a request at `time + interval` is returned. When the proxy admits a request, `request_completed` reduces outstanding work and returns true only when the workload was previously full and has dropped below the cap.

## State And Persistence Behavior
Outstanding counts live in each `PriorityWorkloadModel`. Distribution and interval rate models may hold their own state. The wrapper and predefined workload dictionaries are in memory only; no persistence occurs.

## Dependencies And Integration Points
The module imports `numpy`, `math`, sibling `rate_model`, and `Priority`. `proxy_model.ProxyModel` uses the `WorkloadModel` interface for scheduling and backpressure. `plot.py` later reads outstanding sizes captured by `ProxyModel`.

## Risks And Edge Cases
`Request.__lt__` ignores time and count, so queued request heap order is strictly priority-based with unspecified same-priority ordering. `DistributionBatchGenerator` can return zero for uniform distributions near zero, creating requests with no work but still affecting outstanding logic. Negative or nonsensical distribution results are not guarded. Zero request rate maps to a very large delay instead of no request.

## Test Signals
Tests should cover outstanding cap behavior, resume-on-completion logic, deterministic fixed distributions, random distributions under seeded numpy, zero rate behavior, batch rounding, and priority ordering in the request heap.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/workload_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/inline_fdb_backtraces.py -->
# sources/storage-engines/foundationdb/contrib/inline_fdb_backtraces.py

## Purpose
`inline_fdb_backtraces.py` post-processes FoundationDB trace output. It echoes each input line and, when it finds an embedded `addr2line` command with hexadecimal addresses, runs `llvm-addr2line` against a debug binary to inline symbolicated stack frames.

## Important APIs, Types, And Functions
`main()` defines CLI arguments: optional input `file`, `--addr2line`, `--debug-binary`, and `--dry-run`. The compiled regex matches `addr2line -e <binary> -p -C -f -i` followed by one or more `0x...` addresses. Symbolication uses `subprocess.run(cmd, capture_output=True, text=True, timeout=30)`.

## Control Flow
The script opens the requested file or reads stdin. For each line, it writes the original line to stdout, scans for matching address lists, builds a command from the configured addr2line binary and debug binary, and either prints the command in dry-run mode or executes it. Output is wrapped between `BACKTRACE BEGIN` and `BACKTRACE END` markers. Missing addr2line exits with status 1; timeouts are reported and processing continues.

## State And Persistence Behavior
The script has no persistent state. It streams input and output line by line, only holding regex matches and subprocess output for each backtrace.

## Dependencies And Integration Points
It depends on Python stdlib modules `argparse`, `re`, `subprocess`, and `sys`, plus an external addr2line-compatible binary and matching FoundationDB debug executable. It integrates with trace lines that already contain addr2line command text.

## Risks And Edge Cases
The default debug binary name is version-specific. The regex accepts lowercase hex only and ignores uppercase `0X` forms. It discards the binary path from the matched trace and always uses `--debug-binary`, which is intentional but can surprise users. It does not use a context manager for the optional input file. Subprocess stderr is printed only for nonzero exits.

## Test Signals
Tests can feed synthetic lines via stdin, run `--dry-run`, and assert original lines plus wrapper markers. Mocked subprocess tests should cover successful output, nonzero stderr, timeout, missing binary, multiple matches on one line, and no-match pass-through.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/inline_fdb_backtraces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/joshua_logtool.py -->
# sources/storage-engines/foundationdb/contrib/joshua_logtool.py

## Purpose
`joshua_logtool.py` uploads and downloads FoundationDB simulation trace logs through the Joshua test cluster. It packages trace XML/JSON and optional app logs into an xz-compressed tar archive stored in a Joshua/FDB blob subspace keyed by ensemble ID and test UID.

## Important APIs, Types, And Functions
Constants define RocksDB trace event names and regexes for ensemble IDs and test UIDs. `console_log` prints status to stderr. `_execute_grep`, `_is_rocksdb_test`, `_extract_ensemble_id`, `_get_log_subspace`, `_tar_logs`, and `_tar_extract` provide helpers. `report_error(work_directory, log_directory, ensemble_id, test_uid)` implements upload. `download_logs(ensemble_id, test_uid)` reads and extracts an uploaded archive. `list_commands(ensemble_id)` prints download commands for tests found by `joshua.tail_results`. `_setup_args` creates subcommands `upload`, `download`, and `list`; `_main` opens Joshua and dispatches.

## Control Flow
Upload validates the log directory, finds `trace*.xml` and `trace*.json` recursively, optionally includes `app_log.txt` and `python_app_std*` when `TH_INCLUDE_APP_LOGS` is truthy, filters out filenames containing `core`, derives the ensemble ID from the argument or work-directory path, creates a temporary `.tar.xz`, uploads it via `joshua._insert_blob`, unlinks the archive, and reports success. Download creates a temporary file, reads a blob with `joshua._read_blob`, checks archive size, and extracts it into the current directory. List iterates Joshua results and extracts `TestUID` values from test harness output.

## State And Persistence Behavior
Persistent state is the compressed archive written into FoundationDB under `dir_ensemble_results_application/simulation_logs/<ensemble_id>/<test_uid>`. Temporary archives are created on local disk and normally removed after upload. Download writes extracted archive contents to the current working directory through `tar xf`. Logging and stderr console messages report progress.

## Dependencies And Integration Points
It depends on external `grep` and `tar`, the Python `fdb` bindings, and `joshua.joshua_model`. It integrates with Joshua ensemble result directories, FoundationDB subspaces, trace file naming conventions, and environment variable `TH_INCLUDE_APP_LOGS`.

## Risks And Edge Cases
`_is_rocksdb_test` is currently unused. `_tar_extract` extracts archives without target-directory isolation, so callers must trust archive contents and run from an intended directory. Temporary archive cleanup is skipped on some error returns before `unlink`. The ensemble regex expects work directories ending in `ensembles/<id>`. The upload path catches broad exceptions and returns without a nonzero code from `report_error`; `_main` exits nonzero only for exceptions escaping dispatch.

## Test Signals
Tests should mock Joshua blob APIs and subprocess calls to verify file discovery, core-file filtering, app-log inclusion, ensemble extraction, archive command formation, empty archive handling, download empty-blob behavior, and list command generation from harness output. Integration tests require a Joshua/FDB test database.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/joshua_logtool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/joshua_stats/stats.py -->
# sources/storage-engines/foundationdb/contrib/joshua_stats/stats.py

## Purpose
`stats.py` analyzes Joshua XML result logs and generates summary statistics and histograms for simulation physical time, simulated time, peak memory, speedup for long simulations, and per-test runtime distributions.

## Important APIs, Types, And Functions
Parsing helpers are `get_realtime`, `get_simtime`, `get_test_stats`, `get_speedup_long_simulation_time`, and `get_peakMemory`. `print_stats(data)` prints P90, P50, mean, count, and total. Plotters `draw_realtime`, `draw_simtime`, `draw_memory`, and `draw_speedup_long_physical_time` save histogram PNGs. `main()` reads `sys.argv[1]`, derives a figure label, computes all metrics, writes histograms, and writes `simulatin-test-internal-stats.txt`.

## Control Flow
Each parser loads the XML with `ElementTree.parse`, iterates root children, filters entries with `Command`, `SimElapsedTime`, and `RealElapsedTime`, skips `noSim` commands for most aggregate metrics, and extracts selected numeric attributes. `main` runs parsers sequentially, prints stats, draws figures with log scaling for most histograms, computes speedups for simulated time at least 600 seconds, then groups runtime data by the fifth token of the `Command` string.

## State And Persistence Behavior
Persistent outputs are PNG files named from the input path with dots removed plus metric suffixes, and `simulatin-test-internal-stats.txt` in the current directory. No input data is modified. The module mutates matplotlib global plotting state and redirects `sys.stdout` temporarily while writing per-test stats.

## Dependencies And Integration Points
It depends on `xml.etree.ElementTree`, `numpy`, `matplotlib.pyplot`, `io` (imported but unused), and `sys`. It integrates with Joshua result XML attribute conventions and with local filesystem output for reports.

## Risks And Edge Cases
There is no argparse or input validation; missing `sys.argv[1]` raises. Empty datasets cause numpy percentile/mean warnings or errors and speedup plotting calls `min`/`max` on empty lists. `get_test_stats` assumes the command has at least five space-separated tokens. The output text filename appears misspelled as `simulatin-test-internal-stats.txt`. Repeated `ET.parse` calls reread the same file for every metric.

## Test Signals
Tests should use small XML fixtures covering valid simulation entries, `noSim` filtering, missing attributes, malformed command strings, empty datasets, and deterministic PNG/text output naming under a temporary directory with a noninteractive matplotlib backend.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/joshua_stats/stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/libb64/CMakeLists.txt

## Purpose
This CMake file builds the vendored libb64 base64 helper library for FoundationDB.

## Important APIs, Types, And Functions
It declares `add_library(libb64 STATIC cdecode.c cencode.c)`, disables clang-tidy for the target with `C_CLANG_TIDY ""`, and publishes the local `include` directory with `target_include_directories(libb64 PUBLIC ...)`.

## Control Flow
CMake configures a static library target from the C encoder and decoder sources. Consumers linking to `libb64` inherit the public include path.

## State And Persistence Behavior
The file affects build graph state only. It creates no runtime persistence.

## Dependencies And Integration Points
It integrates with the parent FoundationDB CMake build and with headers under `include/libb64`. Disabling clang-tidy acknowledges vendored/public-domain C style that may not meet project lint rules.

## Risks And Edge Cases
Only C sources are compiled into the static library; C++ wrapper headers are header-only consumers. Build failures would likely come from include-path changes or parent target policy changes.

## Test Signals
Build-system tests should verify the `libb64` target compiles, exports headers, and links into any FDB components that include `libb64/cencode.h`, `libb64/cdecode.h`, or the C++ wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/cdecode.c -->
# sources/storage-engines/foundationdb/contrib/libb64/cdecode.c

## Purpose
`cdecode.c` implements streaming base64 decoding from the public-domain libb64 project.

## Important APIs, Types, And Functions
`base64_decode_value(int value_in)` maps ASCII characters in the `+` through `z` range to six-bit values, `-1` for ignored invalid characters, and `-2` for `=` padding. `base64_init_decodestate(base64_decodestate*)` resets a decoder to `step_a`. `base64_decode_block(code_in, length_in, plaintext_out, state_in)` decodes a chunk while preserving partial quartet state across calls.

## Control Flow
The decoder uses a switch with intentional fallthrough inside an infinite loop. At each step it reads input until a nonnegative decoded fragment appears or the input chunk ends. Steps `a` through `d` assemble output bytes by shifting and OR-ing fragments. On chunk exhaustion, the current step and partially built plaintext byte are saved into `state_in`.

## State And Persistence Behavior
Streaming state is stored in `base64_decodestate.step` and `plainchar`; callers own input and output buffers. No heap allocation or persistence occurs.

## Dependencies And Integration Points
It includes `libb64/cdecode.h` and is compiled into the `libb64` static target. The C++ `decode.h` wrapper delegates to this C API.

## Risks And Edge Cases
Invalid characters are skipped, which is permissive and may hide malformed input. Padding maps to `-2`, which is also skipped by the `fragment < 0` loops, so strict padding validation is not performed. Output buffer sizing is the caller's responsibility. The fallthrough style requires compiler warnings to tolerate implicit fallthrough.

## Test Signals
Tests should decode RFC 4648 vectors, chunked inputs split at every possible boundary, input with newlines/whitespace, padding cases, malformed characters, empty input, and output length correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/cdecode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/cencode.c -->
# sources/storage-engines/foundationdb/contrib/libb64/cencode.c

## Purpose
`cencode.c` implements streaming base64 encoding from libb64.

## Important APIs, Types, And Functions
`CHARS_PER_LINE` is 72. `base64_init_encodestate` initializes `step_A`, `result`, and `stepcount`. `base64_encode_value(char)` maps six-bit values to the base64 alphabet or returns `=` for values above 63. `base64_encode_block` encodes an input chunk while preserving partial triples. `base64_encode_blockend` emits final padding and a trailing newline.

## Control Flow
Like the decoder, encoding uses a switch with intentional fallthrough. Steps A, B, and C consume one byte at a time, emit base64 characters from accumulated fragments, and save `result` and `step` when a chunk ends mid-triple. After every 18 four-character groups, it emits a newline. The block-end function emits `==`, `=`, or no padding depending on the saved step, then appends a newline.

## State And Persistence Behavior
Streaming state lives in `base64_encodestate`. The encoder writes into caller-provided output buffers and performs no allocation or persistence.

## Dependencies And Integration Points
It includes `libb64/cencode.h`, builds into `libb64`, and is wrapped by the header-only C++ `base64::encoder`.

## Risks And Edge Cases
The output buffer must be large enough for expansion, inserted newlines, padding, and final newline. `char` signedness can be surprising, but masks are applied before alphabet lookup. Consumers expecting unwrapped base64 must account for 72-character line wrapping and terminal newline.

## Test Signals
Tests should cover RFC vectors, chunk boundaries, empty input, one- and two-byte tails, line wrapping at 72 characters, and round trips through `cdecode.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/cencode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cdecode.h -->
# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cdecode.h

## Purpose
`cdecode.h` declares the C streaming base64 decoder API and state type.

## Important APIs, Types, And Functions
`base64_decodestep` enumerates `step_a` through `step_d`. `base64_decodestate` stores the current step and a partially assembled plaintext character. Declared functions are `base64_init_decodestate`, `base64_decode_value`, and `base64_decode_block`.

## Control Flow
The header itself has no control flow. It defines the ABI contract consumed by `cdecode.c` and wrappers.

## State And Persistence Behavior
The state struct lets callers preserve decode progress across chunks. It is caller-owned and contains no allocated resources.

## Dependencies And Integration Points
It is included by `cdecode.c` and by the C++ wrapper in `decode.h` inside an `extern "C"` block. The include guard is `BASE64_CDECODE_H`.

## Risks And Edge Cases
The API does not expose required output-buffer sizing or strict validation semantics. `char plainchar` may hold partial binary data, so callers should treat it as opaque state.

## Test Signals
ABI tests should compile C and C++ consumers, initialize state, decode split inputs, and ensure repeated calls preserve state correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cdecode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cencode.h -->
# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cencode.h

## Purpose
`cencode.h` declares the C streaming base64 encoder API and state type.

## Important APIs, Types, And Functions
`base64_encodestep` enumerates `step_A`, `step_B`, and `step_C`. `base64_encodestate` stores the current step, pending result bits, and line-wrapping step count. Declared functions are `base64_init_encodestate`, `base64_encode_value`, `base64_encode_block`, and `base64_encode_blockend`.

## Control Flow
The header contains declarations only. Runtime flow is implemented in `cencode.c`.

## State And Persistence Behavior
The caller owns `base64_encodestate` and output buffers. State enables chunked encoding and tracks line wrap cadence.

## Dependencies And Integration Points
It is included by `cencode.c` and by the C++ wrapper `encode.h` inside `extern "C"`. The include guard is `BASE64_CENCODE_H`.

## Risks And Edge Cases
The API requires callers to invoke `base64_encode_blockend` to flush padding. Output sizing is not encoded in the type system. Line wrapping is implicit through `stepcount`.

## Test Signals
Compile tests and chunked encoding tests should verify state initialization, finalization, padding, line wrapping, and C++ linkage compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cencode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/decode.h -->
# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/decode.h

## Purpose
`decode.h` provides a C++ stream/string wrapper around the C libb64 decoder.

## Important APIs, Types, And Functions
Inside namespace `base64`, `struct decoder` owns a `base64_decodestate` and buffer size. Methods include `decode(char)`, `decode(const char*, int, char*)`, `decode(std::istream&, std::ostream&)`, and static `from_string(std::string)`.

## Control Flow
Stream decoding initializes C decode state, allocates code and plaintext buffers, reads chunks from the input stream, decodes each chunk, writes decoded bytes to the output stream, resets state, and frees buffers. `from_string` wraps stringstreams around this stream API.

## State And Persistence Behavior
Decoder state is per object and reset around stream calls. Heap buffers are allocated per stream decode call and freed before return. No persistent storage is touched.

## Dependencies And Integration Points
It includes `<iostream>` and `libb64/encode.h`; the latter supplies `BUFFERSIZE` and includes `<sstream>`, which `from_string` relies on. It includes `cdecode.h` in an `extern "C"` block. C++ users can include this header without linking a separate wrapper source, but still need the C decoder object code.

## Risks And Edge Cases
Including `encode.h` only to obtain `BUFFERSIZE` couples decode to encode. Manual `new[]`/`delete[]` lacks RAII if stream operations throw exceptions. Strict base64 validation is inherited from the permissive C decoder. The decoder state is uninitialized until stream decode or caller-managed direct decode initializes it.

## Test Signals
Tests should cover `from_string`, stream decoding with chunked inputs, binary output, empty input, invalid characters, and exception-safety expectations if streams are configured to throw.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/encode.h -->
# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/encode.h

## Purpose
`encode.h` provides a C++ stream/string wrapper around the C libb64 encoder.

## Important APIs, Types, And Functions
It defines `BUFFERSIZE 8192`. Inside namespace `base64`, `struct encoder` owns a `base64_encodestate` and buffer size. Methods include `encode(char)`, `encode(const char*, int, char*)`, `encode_end(char*)`, `encode(std::istream&, std::ostream&)`, and static `from_string(std::string)`.

## Control Flow
Stream encoding initializes C encode state, allocates plaintext and expanded code buffers, reads chunks from the input stream, writes encoded chunks to the output stream, then calls `encode_end` to flush padding and final newline. State is reset and buffers are freed before return.

## State And Persistence Behavior
Encoder state is per object and reset around stream calls. Heap buffers are local to stream encoding. No external persistence occurs.

## Dependencies And Integration Points
It includes `<iostream>`, `<sstream>`, and `cencode.h` under `extern "C"`. C++ consumers get a header-only convenience layer over the C object files in `libb64`.

## Risks And Edge Cases
Manual buffer management is not exception-safe. Output includes line wrapping and a trailing newline from the C encoder. Direct low-level `encode` calls require explicit state initialization and finalization by the caller.

## Test Signals
Tests should cover string and stream encoding, padding tails, empty input, line wrapping, binary input, and round trips through `decode.h`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/libb64/include/libb64/encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/linenoise/CMakeLists.txt

## Purpose
This CMake file builds the vendored `linenoise` terminal line-editing library.

## Important APIs, Types, And Functions
It declares `add_library(linenoise STATIC linenoise.c)`, exposes the local `include` directory publicly, and disables clang-tidy for the target.

## Control Flow
CMake creates a static library from `linenoise.c`. Any target linking to `linenoise` receives `include/linenoise` headers.

## State And Persistence Behavior
Only build graph state is affected. Runtime terminal and history state live in `linenoise.c`.

## Dependencies And Integration Points
The target integrates vendored BSD-licensed source with the parent FoundationDB CMake build. Disabling clang-tidy avoids enforcing project style on third-party code.

## Risks And Edge Cases
The target is Unix-oriented because `linenoise.c` uses termios and POSIX APIs. Build portability depends on parent platform guards.

## Test Signals
Build tests should verify the static target compiles and headers can be included by FoundationDB CLI components that need line editing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/include/linenoise/linenoise.h -->
# sources/storage-engines/foundationdb/contrib/linenoise/include/linenoise/linenoise.h

## Purpose
`linenoise.h` declares the public C API for the vendored linenoise line editor used by interactive command-line tools.

## Important APIs, Types, And Functions
`linenoiseCompletions` stores completion strings. Callback types are `linenoiseCompletionCallback`, `linenoiseHintsCallback`, and `linenoiseFreeHintsCallback`. Public functions configure callbacks, add completions, read a line with `linenoise(prompt)`, free returned memory, manage history, clear the screen, enable multiline mode, and print key codes.

## Control Flow
The header has declarations only. Runtime behavior is implemented in `linenoise.c`.

## State And Persistence Behavior
The API exposes global editor configuration and history behavior. Returned lines and completions use heap allocation and must be freed by the caller or by linenoise completion cleanup.

## Dependencies And Integration Points
It includes `<stddef.h>` and is C++ compatible through `extern "C"`. It is the public include path for the `linenoise` CMake target.

## Risks And Edge Cases
The API is global rather than context-based, so callbacks, multiline mode, and history are process-wide. Callers must use `linenoiseFree` or compatible `free` for returned buffers. Callback contracts are not strongly typed beyond raw pointers.

## Test Signals
Compile tests should include the header from C and C++. Behavioral tests should exercise completion callback registration, hint callback/free callback, history save/load, and non-TTY line reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/include/linenoise/linenoise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/linenoise.c -->
# sources/storage-engines/foundationdb/contrib/linenoise/linenoise.c

## Purpose
`linenoise.c` implements a compact POSIX terminal line editor with history, tab completion, hints, single-line and multiline refresh, raw terminal mode, and a non-TTY fallback.

## Important APIs, Types, And Functions
Global configuration includes unsupported terminal names, completion/hint/free callbacks, original termios, raw-mode flags, multiline mode, and history storage. `struct linenoiseState` tracks the current edit buffer, cursor, prompt, terminal columns, multiline rows, and history index. Public APIs include `linenoise`, `linenoiseFree`, `linenoiseSetCompletionCallback`, `linenoiseSetHintsCallback`, `linenoiseSetFreeHintsCallback`, `linenoiseAddCompletion`, `linenoiseHistoryAdd`, `linenoiseHistorySetMaxLen`, `linenoiseHistorySave`, `linenoiseHistoryLoad`, `linenoiseClearScreen`, `linenoiseSetMultiLine`, and `linenoisePrintKeyCodes`.

Internal helpers cover raw mode (`enableRawMode`, `disableRawMode`, `linenoiseAtExit`), terminal sizing (`getCursorPosition`, `getColumns`), completion (`completeLine`, `freeCompletions`), screen refresh (`abuf`, `refreshShowHints`, `refreshSingleLine`, `refreshMultiLine`, `refreshLine`), edit actions (`linenoiseEditInsert`, movement, delete, history navigation), raw input (`linenoiseEdit`, `linenoiseRaw`), and non-TTY input (`linenoiseNoTTY`).

## Control Flow
`linenoise(prompt)` chooses among three modes: unlimited line reading for non-TTY stdin, plain `fgets` for unsupported terminals, or raw interactive editing. Raw editing enables termios raw mode, writes the prompt, adds a temporary empty history entry, reads one byte at a time, dispatches control keys and escape sequences, refreshes the terminal as needed, removes the temporary history entry on enter/EOF, restores terminal mode, prints a newline, and returns a heap copy of the buffer.

Completion invokes the registered callback, cycles through completion candidates on repeated tab, accepts a candidate on other input, or restores the original buffer on escape. History navigation updates the temporary latest history entry before replacing the buffer. Refresh builds ANSI escape sequences in an append buffer to reduce flicker.

## State And Persistence Behavior
Most editor configuration is global process state: callbacks, raw-mode status, multiline mode, history max length, history length, and history entries. `linenoiseHistorySave` persists history to a user-readable/writeable file after temporarily tightening the umask; `linenoiseHistoryLoad` reads lines from a file into memory. `atexit` restores terminal mode and frees history.

## Dependencies And Integration Points
The file depends on POSIX headers and APIs: termios, unistd, ioctl `TIOCGWINSZ`, stat/chmod/umask, read/write, isatty, and stdio allocation functions. It implements the declarations from `linenoise/linenoise.h` and is compiled into the `linenoise` static target for interactive FoundationDB tools.

## Risks And Edge Cases
Global state makes the library non-reentrant and not thread-safe. Raw mode checks `STDIN_FILENO` even when passed a file descriptor. Terminal escape parsing handles a limited set of sequences and reads only a few bytes. Many write errors are ignored because recovery is difficult. Manual allocation and callback ownership require care. History load returns `-1` for missing files despite a comment saying missing files return zero. The library is Unix-specific and lacks Win32 support.

## Test Signals
Unit tests can cover non-TTY input, history add/dedup/max length/save/load, completion list allocation, and edit helper behavior with synthetic `linenoiseState`. Integration tests need pseudo-terminal coverage for raw mode, cursor movement, multiline refresh, hints, ctrl-key handling, unsupported `TERM`, and terminal restoration after errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/linenoise/linenoise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/lint.py -->
# sources/storage-engines/foundationdb/contrib/lint.py

## Purpose
`lint.py` checks FoundationDB Flow/C++-like source files for `wait` calls inside `when` clauses, a pattern that can block a `choose` loop from reacting to other events.

## Important APIs, Types, And Functions
CLI setup is in `_setup_args`; logging in `_setup_logger`. `LinterIssue` formats findings. `Token` normalizes clang token location, kind, and spelling. `tokenizer(source_file_path, clang_args)` parses a file with libclang and yields tokens. `_ScopeLinter` maintains scope state and detects violations. `lint(source_file_path, clang_args)` returns issues. `_main` validates file paths and prints findings.

## Control Flow
The tokenizer yields tokens from clang's translation-unit cursor. `_ScopeLinter.accept` pushes scoping keywords (`loop`, `when`, `choose`) and braces onto a stack, increments `_inside_when_clause` on `when`, pops scopes on `}`, and reports a violation when a `wait` identifier is seen while inside a `when` clause and the current top of stack is `{`. `finalize` reports unclosed scope stack depth.

## State And Persistence Behavior
Linter state is in memory: a stack of tokens/`None` and a count of active `when` clauses. It prints findings to stdout and logs to stderr/stdout handlers. It does not modify source files.

## Dependencies And Integration Points
It depends on Python `clang.cindex` and a working libclang installation, plus clang arguments sufficient to parse the target files. It integrates with FoundationDB's actor/Flow code patterns through token spelling rather than full AST semantics.

## Risks And Edge Cases
The scope heuristic is lexical and can misclassify unrelated identifiers named `when`, `choose`, `loop`, or `wait`. `_exit_scope` sometimes returns `None` implicitly after successful pops. `_main` passes `args.clang_args` directly and may pass `None` where a list is annotated. `logger.warn` is deprecated. The rule only catches waits directly inside the current when-body brace level, not necessarily nested semantics users may care about.

## Test Signals
Tests should feed token fixtures or small source files with valid/invalid `when(wait(...))` patterns, nested scopes, unmatched braces, identifiers in non-scope contexts, missing files, and clang argument handling. Expected output is one issue per forbidden wait.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/lint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/binding_test.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/binding_test.py

## Purpose
`binding_test.py` runs FoundationDB binding tester suites against a temporary local FoundationDB cluster. It is a harness for cycling API, concurrency, directory, HCA, and scripted binding tests across multiple language bindings.

## Important APIs, Types, And Functions
Constants derive default paths for `fdbserver`, `fdbcli`, `libfdb`, the binding tester script, and Python bindings. `_setup_logs`, `_setup_args`, and `_check_file` handle CLI setup. `TestSet` stores binding tester configuration and environment, sets the active cluster file, and exposes `run_scripted_test`, `run_api_test`, `run_api_concurrency_test`, `run_directory_test`, and `run_directory_hca_test`. `API_LANGUAGES` lists `python3`, `java`, `java_async`, `go`, `flow`, and `swift`. `_generate_test_list` builds callable test closures. `run_binding_tests` starts a local cluster and runs cycles. `main` validates paths, configures executable paths, constructs `TestSet`, and exits based on failure count.

## Control Flow
`main` parses args, configures logs and binary paths, creates a `TestSet`, then calls `asyncio.run(run_binding_tests(...))`. `run_binding_tests` creates a one-process `FDBServerLocalCluster`, sets the generated cluster file on the test set, runs all generated tests or one random test per cycle, counts failures, optionally stops after a configured threshold, and finally logs severity 40 and 30 cluster trace lines. Each test launches the binding tester as an async subprocess, waits with a per-test timeout, then drains and logs stdout/stderr.

## State And Persistence Behavior
Persistent external state is limited to the local cluster work directory, fdbserver data/log files, and any side effects from binding tests in the temporary database. The process environment for tester subprocesses is copied from `os.environ` and prepended with `LD_LIBRARY_PATH` and `PYTHONPATH`. Failure counts and cluster file path are in memory.

## Dependencies And Integration Points
It depends on sibling `lib.fdb_process`, `lib.local_cluster`, and `lib.process`, plus FoundationDB binaries, binding tester scripts, language runtimes, and libfdb shared libraries. It uses the local-cluster async context manager to provide a configured memory database.

## Risks And Edge Cases
`stop_at_failure` handling treats `-1` as truthy, so the default can trigger early-stop logic once failures exceed -1. `_test_coroutine` logs subprocess output but does not inspect process return code, so a failing binding tester can be reported successful if it exits before timeout. `_update_path_from_env` logs `LD_LIBRARY_PATH` even when updating `PYTHONPATH`. The local cluster is always one process. Random mode uses unseeded randomness.

## Test Signals
Tests should mock `lib.process.Process` and `FDBServerLocalCluster` to assert command arguments, environment setup, timeout handling, return-code handling if fixed, failure thresholds, random selection, and severity log extraction. Integration tests require packaged FDB binaries and binding tester runtimes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/binding_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/__init__.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/__init__.py

## Purpose
`lib/__init__.py` initializes logging for the local-cluster helper package.

## Important APIs, Types, And Functions
`_setup_logs()` obtains the package logger, clears handlers, constructs a timestamped formatter, attaches a stderr stream handler, and runs immediately at import time.

## Control Flow
Importing `lib` executes `_setup_logs`, which mutates the logger configuration for the package module name.

## State And Persistence Behavior
The only state change is process-local logging handler configuration. No files or cluster state are touched.

## Dependencies And Integration Points
It depends on `logging` and `sys`. Other modules under `lib` get named loggers and can inherit or coexist with this handler setup; top-level scripts sometimes add their own handlers to the `"lib"` logger.

## Risks And Edge Cases
Running logging setup at import time can surprise embedding applications and may interact with handlers added later by `binding_test.py` or `local_cluster.py`. It configures only `__name__`, not necessarily all child loggers.

## Test Signals
Tests can import the package and assert stderr handler presence and formatter shape, while checking repeated imports do not duplicate handlers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/cluster_file.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/cluster_file.py

## Purpose
`cluster_file.py` generates a minimal `fdb.cluster` file for a local FoundationDB cluster.

## Important APIs, Types, And Functions
`generate_fdb_cluster_file(base_directory, description=None, ip_address=None, port=None)` writes `fdb.cluster` under the base directory. Defaults are a random token hex description, `127.0.0.1`, and port `4000`.

## Control Flow
The function computes the file path, fills default values, formats cluster content as `<description>:<description>@<ip>:<port>`, writes it to disk, logs the content at debug level, and returns the file path.

## State And Persistence Behavior
It persists the cluster connection string to `base_directory/fdb.cluster`. It does not create the base directory itself.

## Dependencies And Integration Points
It depends on `ipaddress`, `os.path`, `secrets`, and logging. `lib.local_cluster.FDBServerLocalCluster.run` uses it when the user did not provide a cluster file.

## Risks And Edge Cases
The function overwrites any existing `fdb.cluster` at the target path. It logs the full cluster content, which is usually local-only but still sensitive operational metadata. Port and address are not validated beyond formatting defaults.

## Test Signals
Tests should create a temporary directory, call with defaults and explicit values, assert file content and returned path, and verify generated descriptions differ when omitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/cluster_file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/fdb_process.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/fdb_process.py

## Purpose
`fdb_process.py` wraps `fdbserver` and `fdbcli` subprocess execution for the local-cluster helpers and provides wait loops for server readiness and database availability.

## Important APIs, Types, And Functions
`FileNotFoundError` is a local `OSError` subclass. `_ExecutablePath` resolves and validates executable paths via override or `shutil.which`; module globals `_fdbserver_path` and `_fdbcli_path` store current paths. Public setters/getters are `set_fdbserver_path`, `get_fdbserver_path`, `set_fdbcli_path`, and `get_fdbcli_path`.

`FDBServerProcess` extends `lib.process.Process` and builds `fdbserver` args for cluster file, public address, optional class, data path, and log path. It can iterate XML log files and return lines matching a severity. `FDBCLIProcess` extends `Process` and builds `fdbcli -C <cluster> --exec <commands>`. Async helpers `get_server_status`, `wait_fdbserver_up`, and `wait_fdbserver_available` poll `status json`.

## Control Flow
At import time, the module tries to discover `fdbserver` and `fdbcli`, logging warnings if absent. Running an `FDBServerProcess` constructs args and delegates to the base async process launcher. Status polling launches `fdbcli`, reads stdout with a timeout, waits for process exit, parses JSON, and retries every second until either any response is available or `client.database_status.available` is true.

## State And Persistence Behavior
Executable paths are process-global. `FDBServerProcess` causes fdbserver to persist data and XML logs under provided paths. Severity log reading opens those persisted XML files. No database state is written directly in this module beyond subprocess commands.

## Dependencies And Integration Points
It depends on `asyncio`, `glob`, `ipaddress`, `json`, `shutil`, sibling `lib.process`, and external `fdbserver`/`fdbcli` binaries. `lib.local_cluster` uses it to spawn and configure servers; `binding_test.py` uses setters to point at packaged binaries.

## Risks And Edge Cases
The custom `FileNotFoundError.filename` property returns `_strerror`, likely a bug. `get_server_status` catches builtin `TimeoutError`, not necessarily `asyncio.TimeoutError` in all contexts. It does not inspect fdbcli stderr or return code before JSON parsing. Import-time executable discovery logs warnings before top-level scripts finish configuring log handlers. `get_log_with_severity` string-matches XML lines rather than parsing XML.

## Test Signals
Tests should mock `shutil.which`, subprocess creation, fdbcli output, timeouts, JSON parse failures, severity log files, command argument construction, and executable override validation. Integration tests require real FDB binaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/fdb_process.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/local_cluster.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/local_cluster.py

## Purpose
`local_cluster.py` orchestrates a temporary local FoundationDB cluster from generated work directories, spawned `fdbserver` processes, and `fdbcli` configuration.

## Important APIs, Types, And Functions
`FDB_DEFAULT_PORT` is 4000. `configure_fdbserver(cluster_file)` waits for server response, runs `configure new single memory`, and waits for database availability. `spawn_fdbservers(num_processes, directory, cluster_file, port=None)` creates per-process data/log directories and starts `FDBServerProcess` instances. `FDBServerLocalCluster` is an async context manager exposing `work_directory`, `cluster_file`, `processes`, `handlers`, `run`, and `terminate`.

## Control Flow
`FDBServerLocalCluster.run` creates and sets up a `WorkDirectory`, generates a cluster file if needed, spawns the requested number of fdbservers on sequential ports, configures the database, logs readiness, and returns process handles. `__aenter__` calls `run`; `__aexit__` calls `terminate`. `terminate` sends SIGTERM and then SIGKILL to every process without waiting between them.

## State And Persistence Behavior
The cluster persists data and logs under the work directory during its lifetime. If no work directory is supplied, `WorkDirectory` creates a temp directory and, with default `auto_cleanup=False`, does not remove it on exit. The class stores process handles and handler objects in memory.

## Dependencies And Integration Points
It depends on sibling `cluster_file`, `fdb_process`, and `work_directory`. Top-level `local_cluster.py` and `binding_test.py` use `FDBServerLocalCluster` to provide a database.

## Risks And Edge Cases
Multi-process clusters still run `configure new single memory`, which may not match requested fault tolerance. `terminate` immediately sends kill after terminate and does not await process exit or reap handles. Work directories are not auto-cleaned by default. Existing cluster files must match the chosen port/process setup. Exceptions during spawn/configure can leave started processes running unless the caller handles cleanup.

## Test Signals
Tests should mock work directory setup, cluster file generation, process spawning, configure commands, wait helpers, context-manager cleanup, port increments, and failure paths during partial startup. Integration tests can verify a real local cluster reaches available status.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/local_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/process.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/process.py

## Purpose
`process.py` is a small asyncio subprocess wrapper used by local-cluster and binding-test utilities.

## Important APIs, Types, And Functions
`Process(executable, arguments=None, env=None)` stores command metadata and an optional environment. `run()` launches `asyncio.subprocess.create_subprocess_exec` with stdin/stdout/stderr pipes and returns the underlying process. Properties/methods `pid`, `kill`, `terminate`, `return_code`, and `is_running` expose process status and control.

## Control Flow
Callers construct a `Process`, await `run`, then interact with the returned `asyncio.subprocess.Process` or wrapper methods. `kill` and `terminate` raise if called before `run`.

## State And Persistence Behavior
State is the executable, args, env, and the process handle. Persistence and side effects are determined by the child process, not this wrapper.

## Dependencies And Integration Points
It depends on `asyncio`, `logging`, and typing helpers. `FDBServerProcess`, `FDBCLIProcess`, and `binding_test.TestSet` use it as their process-launch primitive.

## Risks And Edge Cases
The wrapper does not wait after kill/terminate, does not drain pipes automatically, and can deadlock callers that wait on processes producing large output without reading. `is_running` returns true if a pid exists and return code is `None`, but the return code may not update until waited/polled by asyncio. It logs command arguments, which may reveal sensitive values.

## Test Signals
Tests should launch short-lived commands, verify stdout/stderr pipes, pid/return code transitions, custom environment propagation, and pre-run kill/terminate errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/process.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/work_directory.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/lib/work_directory.py

## Purpose
`work_directory.py` manages filesystem directories used by local FoundationDB clusters for data and logs.

## Important APIs, Types, And Functions
`WorkDirectory(base_directory=None, data_directory="data/", log_directory="log/", auto_cleanup=False)` stores configuration. Properties expose `base_directory`, `data_directory`, and `log_directory`. `setup()` creates a temp base directory if needed, creates data and log subdirectories, and changes the process current working directory to the base. `teardown()` removes the base directory. Context manager methods call setup and optionally teardown.

## Control Flow
Entering the context or calling setup materializes directories and changes cwd. Exiting restores the original cwd and removes the directory only when `auto_cleanup` is true.

## State And Persistence Behavior
The class persists directories on local disk. With default `auto_cleanup=False`, temp work directories remain after use. It stores the original cwd at construction time for restoration.

## Dependencies And Integration Points
It depends on `tempfile`, `os`, `shutil`, and logging. `lib.local_cluster.FDBServerLocalCluster` creates a `WorkDirectory` directly and calls `setup` without using its context manager.

## Risks And Edge Cases
Changing process-wide cwd is surprising and not thread-safe. `teardown` deletes the full base directory recursively. If `setup` is called without the context manager, cwd is not automatically restored. Relative `data_directory` and `log_directory` values are joined to the base without normalization.

## Test Signals
Tests should verify temp and explicit base-directory setup, data/log creation, cwd restoration in context manager use, auto-cleanup behavior, and safe handling of repeated setup/teardown calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/lib/work_directory.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/local_cluster.py -->
# sources/storage-engines/foundationdb/contrib/local_cluster/local_cluster.py

## Purpose
The top-level `local_cluster.py` script starts a local FoundationDB cluster and keeps it running until interrupted.

## Important APIs, Types, And Functions
`_setup_logs` configures stderr logging. `_setup_args` parses `--num-processes`, `--work-dir`, `--debug`, `--cluster-file`, `--fdbserver-path`, `--fdbcli-path`, and `--port`. `run_fdbservers` opens an async `FDBServerLocalCluster` context and sleeps forever. `main` validates process count, sets executable paths, and runs the async loop.

## Control Flow
CLI execution parses args and logging, rejects fewer than one process, configures binary paths through `lib.fdb_process`, then runs `run_fdbservers`. The async function starts the cluster and then loops with one-second sleeps, relying on context-manager exit during cancellation or exceptions for cleanup.

## State And Persistence Behavior
Runtime state and persistence are delegated to `lib.local_cluster.FDBServerLocalCluster`: work directories, cluster file, fdbserver data, and logs. The script itself persists nothing else.

## Dependencies And Integration Points
It depends on sibling `lib.local_cluster` and `lib.fdb_process`, `asyncio`, and external FoundationDB binaries. It is the operator-facing entry point for manually starting a local cluster from this contrib package.

## Risks And Edge Cases
The infinite loop has no explicit signal handling in this file. Work directories remain by default. It uses `asyncio.get_event_loop().run_until_complete`, which is older style compared with `asyncio.run`. The error message says "more than 1 process" even though one process is accepted.

## Test Signals
Tests should mock `FDBServerLocalCluster` and path setters, assert argument parsing and process-count validation, and verify the async context is entered. Integration tests can run with real binaries and confirm the cluster remains available until terminated.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/local_cluster/local_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/md5/CMakeLists.txt

## Purpose
This CMake file builds the vendored MD5 implementation used by FoundationDB when OpenSSL MD5 is not selected.

## Important APIs, Types, And Functions
It declares `add_library(md5 STATIC md5.c)`, disables clang-tidy, and publishes `include` as a public target include directory.

## Control Flow
CMake compiles `md5.c` into a static library and exposes `include/md5/md5.h` to consumers.

## State And Persistence Behavior
Only build graph state is affected. Runtime digest state is in `MD5_CTX`.

## Dependencies And Integration Points
It integrates a public-domain MD5 implementation into the parent build. Consumers link the `md5` target and include `md5/md5.h`.

## Risks And Edge Cases
MD5 is cryptographically broken and should only be used for compatibility/non-security checksums. Build selection with `HAVE_OPENSSL` affects whether this implementation or OpenSSL declarations are used.

## Test Signals
Build tests should verify the target compiles with and without OpenSSL configuration and that known MD5 vectors link and pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/include/md5/md5.h -->
# sources/storage-engines/foundationdb/contrib/md5/include/md5/md5.h

## Purpose
`md5.h` declares an OpenSSL-compatible MD5 API, either by including OpenSSL's header when `HAVE_OPENSSL` is defined or by declaring the bundled implementation's types and functions.

## Important APIs, Types, And Functions
When OpenSSL is unavailable, it defines `MD5_u32plus`, `MD5_CTX` with counters, hash state words, a 64-byte buffer, and a 16-word block buffer. It declares `MD5_Init`, `MD5_Update`, and `MD5_Final` with `MULTIPLY_DEFINED_SYMBOL` from `flow/Platform.h`.

## Control Flow
The header is controlled by preprocessor branches. With `HAVE_OPENSSL`, it delegates to `<openssl/md5.h>`; otherwise it exposes bundled declarations behind `_MD5_H`.

## State And Persistence Behavior
`MD5_CTX` is caller-owned incremental digest state. No persistence is involved.

## Dependencies And Integration Points
It depends on OpenSSL when configured, otherwise on `flow/Platform.h` for symbol annotation. `md5.c` implements the non-OpenSSL declarations. The function names intentionally match OpenSSL for compatibility.

## Risks And Edge Cases
The header name guard `_MD5_H` can overlap with other MD5 headers. `MD5_u32plus` is `unsigned int`, assuming it is at least 32 bits. MD5 should not be used for security-sensitive integrity. Symbol compatibility depends on `MULTIPLY_DEFINED_SYMBOL`.

## Test Signals
Compile tests should cover both `HAVE_OPENSSL` and bundled paths. Functional tests should hash standard vectors through init/update/final and compare with known digests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/include/md5/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/md5.c -->
# sources/storage-engines/foundationdb/contrib/md5/md5.c

## Purpose
`md5.c` implements the bundled OpenSSL-compatible MD5 message-digest algorithm when `HAVE_OPENSSL` is not defined.

## Important APIs, Types, And Functions
The file defines MD5 round functions `F`, `G`, `H`, `H2`, `I`, the `STEP` macro, endian-aware `SET`/`GET` macros, static `body(MD5_CTX*, const void*, unsigned long)` for 64-byte block transforms, and public `MD5_Init`, `MD5_Update`, and `MD5_Final`.

## Control Flow
`MD5_Init` sets the four standard initial state words and zeroes bit counters. `MD5_Update` updates byte counters, fills any partial buffer, processes full 64-byte blocks with `body`, and stores remaining bytes. `MD5_Final` appends `0x80`, zero padding, the bit length, processes the final block, writes the 16-byte little-endian digest, and zeroes the context. `body` applies all four MD5 rounds to one or more 64-byte blocks.

## State And Persistence Behavior
Digest state lives entirely in caller-provided `MD5_CTX`. Finalization clears the context with `memset`. No external persistence occurs.

## Dependencies And Integration Points
It includes `<string.h>` and `md5.h`, and is excluded at compile time when `HAVE_OPENSSL` is defined. The CMake target builds it into the `md5` static library.

## Risks And Edge Cases
MD5 is not collision-resistant and must not be used for security decisions. The x86/vax `SET` macro reads unaligned words by casting, which is fast but can violate strict aliasing expectations on some compilers. The counter uses a 29-bit low byte count plus high count scheme matching the original implementation; very large inputs should be covered by tests.

## Test Signals
Tests should run RFC 1321 vectors, incremental updates with all chunk sizes, large input crossing many blocks, empty input, finalization clearing behavior if observable, and parity with OpenSSL when available.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/md5/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/backup_metadata.py -->
# sources/storage-engines/foundationdb/contrib/metadata_audit/backup_metadata.py

## Purpose
`backup_metadata.py` backs up selected FoundationDB system metadata ranges (`serverList`, `keyServers`, and `serverKeys`) to JSON files and verifies that the backup is readable and matches live data at sampled keys.

## Important APIs, Types, And Functions
The script imports metadata prefixes and range ends plus `set_read_transaction_options` from `fdb_metadata_utils`. `backup_range(db, prefix, end, name, batch_size=10000)` reads a metadata range in batches and returns `{'key': hex, 'value': hex}` entries. `main()` parses `--cluster-file` and `--output-dir`, connects to FDB, backs up three ranges, writes JSON files and `backup_manifest.json`, then verifies JSON structure and live spot checks. Nested transactional `verify_entry` reads system keys with lock-aware and timeout options.

## Control Flow
`main` creates a timestamped output directory, opens the requested or default FDB cluster, calls `backup_range` for each metadata range, writes each result list to JSON, writes a manifest with timestamp/counts/files, then verifies. `backup_range` repeatedly opens read transactions, sets read options, scans from `start` to `end` with a limit, appends hex-encoded entries, and advances `start` to the last key plus `\x00` until a short batch or no batch is returned.

## State And Persistence Behavior
The script persists a backup directory named `<output-dir>_<timestamp>` containing `serverList.json`, `keyServers.json`, `serverKeys.json`, and `backup_manifest.json`. It reads live FoundationDB system keys but does not write to the database. Verification reopens the written JSON and spot-checks sampled entries against current live values.

## Dependencies And Integration Points
It depends on Python `fdb` bindings, `fdb_metadata_utils`, JSON/filesystem modules, and FoundationDB system-key read options. It is intended to pair with a restore script mentioned in usage and final output.

## Risks And Edge Cases
The backup is not guaranteed to be a single consistent snapshot across all batches and all three ranges unless transaction/version behavior in `set_read_transaction_options` enforces that elsewhere. Advancing with `last_key + b'\x00'` is a common exclusive-start trick but should be checked for arbitrary system key encodings. Verification spot-checks only first/middle/last-style samples and can fail if metadata changes between backup and verification. Output directories are timestamped by local time and can collide within a second if reused.

## Test Signals
Tests should mock FDB transactions and metadata utilities to verify batched range scanning, hex encoding, output file/manifest structure, malformed JSON detection, entry structure validation, spot-check success/failure, empty ranges, and non-default cluster-file handling. Integration tests require a controlled FDB cluster and stable metadata during backup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/metadata_audit/backup_metadata.py -->
