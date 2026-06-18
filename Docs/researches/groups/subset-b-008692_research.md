# subset-b-008692 Research

Grouped source research for RocksDB third-party build configuration, tool scripts, benchmark wrappers, blob inspection, and the Python Advisor rule/configuration optimization subsystem. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest_main.cc -->
# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest_main.cc

## Purpose

This is the fused GoogleTest default entry point used by RocksDB tests that link against `gtest_main`. It provides a tiny `main()` implementation so individual test binaries do not need to define their own test runner.

## Important APIs, Types, and Functions

The only function is `GTEST_API_ int main(int argc, char **argv)`. It includes `gtest/gtest.h`, prints the source file path with `printf`, calls `testing::InitGoogleTest(&argc, argv)`, and returns `RUN_ALL_TESTS()`.

## Control Flow

Process startup enters `main`, GoogleTest consumes/updates command-line arguments, then the GoogleTest registry executes all linked tests and returns the aggregate result as the process exit code.

## State and Persistence Behavior

The file owns no durable state. Its only state interaction is GoogleTest global registration and command-line flag initialization.

## Dependencies and Integration Points

It depends on the fused GoogleTest headers and C stdio. It integrates with every RocksDB test target that links this gtest main object rather than a custom runner.

## Risks and Test Signals

Risk is low, but changing it can affect every test binary's startup behavior, flag parsing, and exit status. A good signal is successful execution of any linked GoogleTest binary with normal flags such as filters and repeat counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest_main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/thirdparty.inc -->
# sources/storage-engines/rocksdb/thirdparty.inc

## Purpose

`thirdparty.inc` is a CMake include fragment for configuring optional third-party libraries, primarily for Windows/native package layouts rooted under `THIRDPARTY_HOME`. It wires compression, flags, and allocator dependencies into RocksDB build definitions.

## Important APIs, Types, and Functions

It sets `THIRDPARTY_LIBS`, `SYSTEM_LIBS`, and `ARTIFACT_SUFFIX`, and defines home/include/debug/release library variables for gflags, Snappy, LZ4, zlib, ZSTD, and jemalloc. Feature switches include legacy variables such as `GFLAGS`, `SNAPPY`, `LZ4`, `ZLIB`, `XPRESS`, and `JEMALLOC`, translated to `WITH_*` variables.

## Control Flow

CMake evaluates the file top to bottom. Each optional block checks whether the feature is enabled, lets environment variables override default include/library paths, adds compile definitions and include directories, and appends debug/optimized libraries to `THIRDPARTY_LIBS`. Disabled blocks emit status messages only.

## State and Persistence Behavior

There is no runtime persistence. Build state is persisted into the generated CMake configuration, compiler flags, link lines, and target names. Jemalloc changes `ARTIFACT_SUFFIX` to `_je`, affecting output artifact naming.

## Dependencies and Integration Points

The file integrates with top-level RocksDB CMake targets through `THIRDPARTY_LIBS`, `SYSTEM_LIBS`, include paths, and `add_definitions`. `XPRESS` links Windows `Cabinet.lib`; other features expect explicit `.lib` paths.

## Risks and Test Signals

Risks include stale hard-coded package paths, mismatched debug/release libraries, globally scoped include/definition leakage, and feature drift from modern `find_package` behavior. Test signals are configure-time status messages, successful Windows builds across enabled feature combinations, and link/runtime compression tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/thirdparty.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/CMakeLists.txt -->
# sources/storage-engines/rocksdb/tools/CMakeLists.txt

## Purpose

This CMake file defines RocksDB command-line tool targets built from `tools/` sources. It always builds core tools and conditionally builds additional utility/stress/dump tools when `WITH_TOOLS` is enabled.

## Important APIs, Types, and Functions

The main variables are `CORE_TOOLS`, `TOOLS`, `core_tool_deps`, and `tool_deps`. It creates executable targets from source basenames with optional `${ARTIFACT_SUFFIX}`, links core tools to `${ROCKSDB_LIB}`, links optional tools to `${ROCKSDB_LIB} ${THIRDPARTY_LIBS}`, and defines `ldb_tests` as a custom target running `ldb_tests.py`.

## Control Flow

CMake iterates over `sst_dump.cc` and `ldb.cc` unconditionally, then over optional sources such as `db_sanity_test.cc`, `write_stress.cc`, `db_repl_stress.cc`, `dump/rocksdb_dump.cc`, and `dump/rocksdb_undump.cc` inside `if(WITH_TOOLS)`.

## State and Persistence Behavior

There is no runtime state. Build graph state is persisted as generated executable targets and dependency lists.

## Dependencies and Integration Points

It depends on the parent CMake project defining `ROCKSDB_LIB`, `THIRDPARTY_LIBS`, `ARTIFACT_SUFFIX`, and `WITH_TOOLS`. The custom `ldb_tests` target integrates Python test execution with the `ldb` binary.

## Risks and Test Signals

Risks include target/list naming without suffix in dependency lists, missing third-party links for optional tools, and Python interpreter assumptions. Signals are successful CMake generation, tool linking, and `cmake --build . --target ldb_tests`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/Dockerfile -->
# sources/storage-engines/rocksdb/tools/Dockerfile

## Purpose

This Dockerfile creates a minimal container for running the RocksDB `ldb` command-line tool.

## Important APIs, Types, and Functions

It uses `FROM buildpack-deps:wheezy`, `ADD ./ldb /rocksdb/tools/ldb`, and `CMD /rocksdb/tools/ldb`.

## Control Flow

Image build starts from an old Debian Wheezy buildpack image, copies a local `ldb` binary into the image, and configures the container default command to execute that binary.

## State and Persistence Behavior

The copied `ldb` binary is the only meaningful image state. Runtime persistence depends on mounted volumes or paths accessed by `ldb`; the Dockerfile itself creates no database directories.

## Dependencies and Integration Points

It assumes a compatible `ldb` executable exists in the Docker build context and that its dynamic library needs are satisfied by the base image or static linking.

## Risks and Test Signals

Risks are the obsolete base image, ABI/library mismatch with the supplied binary, and a default command that prints usage unless arguments are supplied through Docker overrides. Signals are image build success and `docker run` behavior against a mounted RocksDB database.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/__init__.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/__init__.py

## Purpose

This empty package initializer marks `tools/advisor/advisor` as an importable Python package for the RocksDB Advisor subsystem.

## Important APIs, Types, and Functions

It exports no functions, classes, constants, or package-level side effects.

## Control Flow

Importing `advisor` executes no code from this file. Submodules such as `advisor.rule_parser`, `advisor.db_options_parser`, and `advisor.db_bench_runner` hold the actual behavior.

## State and Persistence Behavior

There is no runtime state or persistence.

## Dependencies and Integration Points

It integrates with Python package import resolution, especially command lines using `python3 -m advisor.config_optimizer_example` or tests importing `advisor.*`.

## Risks and Test Signals

Risk is minimal. Removing it can break package imports in environments that do not rely on namespace package behavior. A useful signal is successful import of all advisor submodules from the expected working directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/bench_runner.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/bench_runner.py

## Purpose

`bench_runner.py` defines the abstract benchmark-runner contract used by the Advisor optimizer. It lets the optimizer compare experiment metrics and request data sources without knowing the benchmark backend.

## Important APIs, Types, and Functions

`BenchmarkRunner` is an `ABC` with abstract `is_metric_better(new_metric, old_metric)` and `run_experiment()`. The concrete helper `get_info_log_file_name(log_dir, db_path)` reproduces RocksDB info-log prefix naming when `db_log_dir` redirects logs away from the database path.

## Control Flow

Subclasses implement execution and metric comparison. The static log-name helper strips the leading slash from `db_path`, replaces non `[0-9a-zA-Z-_\.]` characters with underscores, appends a trailing underscore when needed, and finally appends `LOG`; if no log directory is configured, it returns `LOG`.

## State and Persistence Behavior

The base class has no instance state. The helper computes names for persisted RocksDB LOG files but does not access the filesystem.

## Dependencies and Integration Points

It depends on `abc` and `re`. `DBBenchRunner` subclasses it, and tests assert the log filename contract used by RocksDB's `GetInfoLogPrefix()`.

## Risks and Test Signals

Risks are mismatch with RocksDB's real log naming rules and the abstract `run_experiment` signature differing from subclass arguments. Signals include `test_get_info_log_file_name`, successful subclass instantiation, and optimizer operation against redirected log directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/bench_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/config_optimizer_example.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/config_optimizer_example.py

## Purpose

This is the command-line entry point for running the Advisor configuration optimizer. It wires rules, a benchmark runner class, initial RocksDB OPTIONS, optional miscellaneous settings, optional ODS access, and a base DB path into `ConfigOptimizer`.

## Important APIs, Types, and Functions

`main(args)` constructs `RulesSpec`, dynamically imports `args.benchrunner_module`, instantiates `args.benchrunner_class`, builds `DatabaseOptions`, forces `DBOptions.stats_dump_period_sec`, runs `ConfigOptimizer`, and prints the generated final OPTIONS file plus miscellaneous options. The module-level parser defines required flags for rules, options, base DB, stats period, benchmark module/class, and benchmark positional args.

## Control Flow

Execution parses arguments, optionally creates an `ods_args` dictionary, constructs the selected benchmark runner, loads the starting options, updates stats-dump settings, invokes the iterative optimizer, and emits final configuration output.

## State and Persistence Behavior

The script writes final and temporary OPTIONS files through `DatabaseOptions.generate_options_config`. It mutates in-memory options during optimization and relies on benchmark runs to create/delete database contents.

## Dependencies and Integration Points

It depends on `argparse`, Advisor parser/optimizer modules, and dynamic imports. It integrates with `DBBenchRunner`, ODS/rapido fetchers, `advisor/rules.ini`, and RocksDB `db_bench`.

## Risks and Test Signals

Risks include unsafe dynamic import/class selection, missing `benchrunner_pos_args`, path assumptions for temp OPTIONS output, and real benchmark side effects. Signals are argument parsing, successful module import, a complete optimizer run, and generation of `OPTIONS_final.tmp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/config_optimizer_example.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_bench_runner.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_bench_runner.py

## Purpose

`db_bench_runner.py` implements the Advisor `BenchmarkRunner` contract for RocksDB's `db_bench`. It prepares a database, executes one benchmark, parses throughput and perf context output, and returns Advisor data sources for rules.

## Important APIs, Types, and Functions

`DBBenchRunner` defines `OUTPUT_FILE`, `ERROR_FILE`, `DB_PATH`, `THROUGHPUT`, and `PERF_CON`. Key methods are `is_metric_better`, `get_opt_args_str`, `_parse_output`, `get_log_options`, `_get_options_command_line_args_str`, `_setup_db_before_experiment`, `_build_experiment_command`, `_run_command`, and `run_experiment`.

## Control Flow

Construction stores the `db_bench` binary, benchmark name, optional db_bench args, and optional ODS args. `run_experiment` removes/reloads the DB with `fillrandom`, builds the benchmark command with `--statistics --perf_level=3`, records start/end time, runs it through `subprocess.call(shell=True)`, parses output, constructs `DatabaseLogs`, `LogStatsParser`, `DatabasePerfContext`, and optional `OdsStatsFetcher`, then returns data sources and throughput.

## State and Persistence Behavior

It overwrites `temp/dbbench_out.tmp` and `temp/dbbench_err.tmp`, removes the target DB path before setup, generates temporary OPTIONS files, and reads RocksDB LOG files. Perf context is converted into a timestamped in-memory time series.

## Dependencies and Integration Points

It depends on `shutil`, `subprocess`, `time`, `BenchmarkRunner`, `DatabaseOptions`, log/stat fetchers, and the external `db_bench` binary.

## Risks and Test Signals

Risks include shell command injection through option strings, fixed temp filenames, non-thread-safety, assumptions about `db_bench` output format, and destructive DB path cleanup. Tests cover setup, log filename/path selection, optional argument string construction, experiment command building, and a live experiment when `db_bench` is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_bench_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_config_optimizer.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_config_optimizer.py

## Purpose

This module contains the Advisor optimization loop that applies rule suggestions to RocksDB OPTIONS, benchmarks each candidate configuration, and backtracks when throughput does not improve.

## Important APIs, Types, and Functions

`ConfigOptimizer` exposes static helpers `apply_action_on_value`, `improve_db_config`, `pick_rule_to_apply`, `apply_suggestions`, and `get_backtrack_config`, plus the instance method `run`. Constants `SCOPE` and `SUGG_VAL` name output concepts.

## Control Flow

`run` deep-copies the initial options, bootstraps a benchmark, loads and validates rules, triggers rules from returned data sources, applies one selected rule, updates options, reruns the benchmark, compares metrics through `bench_runner.is_metric_better`, and either backtracks or reloads/retriggers rules for the next iteration. Selection prefers a still-triggered previous rule after improvement, otherwise the first untried rule.

## State and Persistence Behavior

State is held in mutable `DatabaseOptions`, current/updated option dictionaries, triggered rules, and a `rules_tried` set. Persistent side effects are delegated to benchmark runs and generated OPTIONS files.

## Dependencies and Integration Points

It depends on `DatabaseOptions`, `NO_COL_FAMILY`, and `Suggestion.Action`. It integrates rule parser output with benchmark data sources and the db_bench runner.

## Risks and Test Signals

Risks include random choice among suggested values, `assert`-based validation, integer-only 30 percent option changes, recursion when diffs are empty, and narrow throughput-only optimization. Signals include unit tests around option diffs/actions plus end-to-end optimizer runs that show rule application, backtracking, and final option generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_config_optimizer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_log_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_log_parser.py

## Purpose

`db_log_parser.py` models RocksDB LOG files as Advisor data sources. It parses log records, associates them with column families, and triggers log-based rule conditions using regular expressions.

## Important APIs, Types, and Functions

It defines `NO_COL_FAMILY = "DB_WIDE"`, abstract `DataSource` with enum `Type` (`LOG`, `DB_OPTIONS`, `TIME_SERIES`), `Log`, and `DatabaseLogs`. `Log` provides `is_new_log`, timestamp/context/message/column-family accessors, `append_message`, `get_timestamp`, and `__repr__`.

## Control Flow

`DatabaseLogs.check_and_trigger_conditions` globs files by prefix, skips filenames containing `old`, groups multiline log entries by detecting timestamp prefixes, constructs `Log` objects, and sends each completed log to `trigger_conditions_for_log`. That method applies each condition regex to the log message and appends matching logs under the detected column family key.

## State and Persistence Behavior

The parser reads LOG files but does not write them. Condition objects accumulate trigger dictionaries of column-family name to `Log` list.

## Dependencies and Integration Points

It depends on `glob`, `re`, `time`, `calendar.timegm`, and Advisor rule conditions. It feeds `RulesSpec.get_triggered_rules` and `LogStatsParser`.

## Risks and Test Signals

Risks include timestamp format assumptions, old-file filtering by substring, `new_log.append_message` before a first timestamp on malformed files, and GMT timestamp interpretation. Tests cover column-family detection, multiline records, timestamp conversion, new-record detection, skipped nonmatching regexes, and trigger map contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_log_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_options_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_options_parser.py

## Purpose

This module parses RocksDB OPTIONS files into Advisor data-source objects, retrieves and updates scoped option values, generates temporary OPTIONS configs, and triggers option-based conditions.

## Important APIs, Types, and Functions

`OptionsSpecParser` extends INI helpers with section/option parsing and string generation. `DatabaseOptions` implements `DataSource.Type.DB_OPTIONS` and exposes `is_misc_option`, `get_options_diff`, `setup_misc_options`, `load_from_source`, `get_misc_options`, `get_column_families`, `get_all_options`, `get_options`, `update_options`, `generate_options_config`, and `check_and_trigger_conditions`.

## Control Flow

Loading strips trailing comments, recognizes section headers, maps section paths such as `TableOptions/BlockBasedTable` to dotted names, records column families from `CFOptions`, and stores key/value pairs. Condition checks fetch required options, build an `options` list for database-wide or per-column-family scopes, evaluate the condition expression, and set triggers for database-wide or matching column families.

## State and Persistence Behavior

State is `options_dict`, `misc_options`, and `column_families`. `generate_options_config` writes `../temp/OPTIONS_<nonce>.tmp` relative to the module directory.

## Dependencies and Integration Points

It depends on `copy`, `os`, `IniParser`, `DataSource`, and `NO_COL_FAMILY`. It integrates with `DBBenchRunner`, `ConfigOptimizer`, option rules, and tests using fixture OPTIONS files.

## Risks and Test Signals

Risks include use of `eval`, weak parsing of malformed misc options, `curr_sec_type` reliance on previous section state, and temp-directory assumptions. Tests cover option diffing, misc option handling, setup, retrieval, updates, generated file creation, and condition triggering across database-wide and column-family scopes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_options_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_stats_fetcher.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_stats_fetcher.py

## Purpose

`db_stats_fetcher.py` adapts RocksDB LOG statistics, db_bench perf context, and external ODS/rapido time series into the common Advisor `TimeSeriesData` interface.

## Important APIs, Types, and Functions

Classes are `LogStatsParser`, `DatabasePerfContext`, and `OdsStatsFetcher`. Important methods include `LogStatsParser.parse_log_line_for_stats`, `add_to_timeseries`, `fetch_timeseries`; `DatabasePerfContext.unaccumulate_metrics`; and ODS helpers `_get_string_in_quotes`, `_get_time_value_pair`, `_get_ods_cli_stime`, `execute_script`, `parse_rapido_output`, `parse_ods_output`, `fetch_timeseries`, `get_keys_from_conditions`, and `fetch_rate_url`.

## Control Flow

Log stats parsing scans LOG files by prefix, skips old files, groups log records, identifies `STATISTICS:` records, parses metric lines into lowercased keys, and populates `keys_ts`. Perf context wraps a provided metric timestamp map and optionally converts cumulative samples to deltas. ODS fetchers build shell commands, execute client tools, then parse tabular output into entity/key/timestamp maps.

## State and Persistence Behavior

State is in-memory `keys_ts`, `stats_freq_sec`, and duration windows. ODS execution overwrites `temp/stats_out.tmp` and `temp/stats_err.tmp`.

## Dependencies and Integration Points

It depends on Advisor log/time-series parsers, `subprocess`, `glob`, `re`, and external ODS/rapido clients. It feeds time-series rule conditions.

## Risks and Test Signals

Risks include shell execution, fixed temp files, fragile output parsing, numeric conversions, old-log filtering, and division issues in rate calculations. Tests cover burst detection, aggregate and per-epoch expression triggers, mocked fetches, and cumulative perf-context conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_stats_fetcher.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_timeseries_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/db_timeseries_parser.py

## Purpose

This module defines the common time-series data-source abstraction used by Advisor rules. It evaluates bursty behavior and boolean expressions over fetched metrics.

## Important APIs, Types, and Functions

It defines `NO_ENTITY`, `TimeSeriesData`, enum `Behavior` (`bursty`, `evaluate_expression`), enum `AggregationOperator` (`avg`, `max`, `min`, `latest`, `oldest`), abstract `get_keys_from_conditions` and `fetch_timeseries`, plus concrete `fetch_burst_epochs`, `fetch_aggregated_values`, `check_and_trigger_conditions`, and `handle_evaluate_expression`.

## Control Flow

`check_and_trigger_conditions` asks the subclass for required keys, fetches them, filters entities that have all keys for each condition, and dispatches by behavior. Bursty conditions compute windowed rate changes. Expression conditions either aggregate each key once per entity or evaluate at each timestamp, then set trigger maps when the expression is true.

## State and Persistence Behavior

`keys_ts` stores entity -> key -> timestamp -> value. Condition triggers persist on condition objects until reset/reparsed.

## Dependencies and Integration Points

It depends on `math`, `DataSource`, and rule parser condition fields. Subclasses include `LogStatsParser`, `DatabasePerfContext`, and `OdsStatsFetcher`.

## Risks and Test Signals

Risks include `eval`, division by zero for percent rates, assuming aligned timestamps for multi-key expressions, and missing-key handling. Tests exercise burst windows, latest aggregation, non-aggregate expression evaluation, and cumulative perf metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/db_timeseries_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/ini_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/ini_parser.py

## Purpose

`ini_parser.py` provides lightweight parsing helpers for the Advisor rules/spec syntax and is reused by the OPTIONS parser for simple key/value handling.

## Important APIs, Types, and Functions

`IniParser.Element` classifies `rule`, `cond`, `sugg`, `key_val`, and `comment`. Static helpers are `remove_trailing_comment`, `is_section_header`, `get_section_name`, `get_element`, `get_key_value_pair`, and `get_list_from_value`.

## Control Flow

Each line has trailing comments stripped, then is classified as empty/comment, section header, or key/value. Section headers are identified by square brackets and by a section type prefix. Key/value parsing splits at the first `=`, preserves embedded `=`, returns `None` for empty values, and converts colon-separated values to lists only when more than one token is present.

## State and Persistence Behavior

The parser is stateless and performs no I/O itself.

## Dependencies and Integration Points

It depends only on `Enum`. `RulesSpec` uses it for rule sections; `OptionsSpecParser` inherits its comment and key/value utilities.

## Risks and Test Signals

Risks include treating `#` inside values as a comment, no escaping/quoting semantics for lists, strict section-name quoting, and no duplicate detection. Tests cover missing section names, missing values, list parsing indirectly through rules/options, and parse errors for unrecognized lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/ini_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser.py

## Purpose

`rule_parser.py` implements the Advisor rule DSL: rules combine conditions and suggestions, conditions bind to log/options/time-series sources, and `RulesSpec` loads a rules file and determines which rules are triggered.

## Important APIs, Types, and Functions

Core classes are `Section`, `Rule`, `Suggestion`, `Condition`, `LogCondition`, `OptionCondition`, `TimeSeriesCondition`, and `RulesSpec`. `Suggestion.Action` supports `set`, `increase`, and `decrease`. Important methods include `perform_checks`, `set_parameter`, `Rule.is_triggered`, `Rule.get_overlap_timestamps`, `RulesSpec.load_rules_from_spec`, `trigger_conditions`, `get_triggered_rules`, and `print_rules`.

## Control Flow

`RulesSpec.load_rules_from_spec` scans an INI-like file, creates section objects, converts base `Condition` objects to source-specific subclasses when it sees `source`, and assigns parameters. `perform_section_checks` validates all sections. Triggering first asks each data source to set condition triggers, then tests each rule as a conjunction. Rules with `overlap_time_period` require two time-series conditions with nearby trigger epochs.

## State and Persistence Behavior

State lives in dictionaries of rule, condition, and suggestion objects. Trigger state is mutable on conditions and rules and is reset only by reparsing/recreating objects.

## Dependencies and Integration Points

It depends on `re`, `abc`, `Enum`, `DataSource`, `NO_COL_FAMILY`, `TimeSeriesData`, and `IniParser`. It is central to the Advisor CLI, optimizer, fixtures, and tests.

## Risks and Test Signals

Risks include source needing to be the first condition parameter, `Enum` key errors for bad action/behavior names, trigger state reuse, unchecked references to unknown condition/suggestion names, and an index-order bug risk in overlap scanning. Tests cover all triggered sample rules, conjunction behavior, missing required fields, missing source/action, and section header parse errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser_example.py -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser_example.py

## Purpose

This command-line example runs the Advisor rule parser against existing RocksDB OPTIONS, LOG files, and optional ODS data to print triggered rules and their suggestions.

## Important APIs, Types, and Functions

`main(args)` creates `RulesSpec`, `DatabaseOptions`, `DatabaseLogs`, `LogStatsParser`, optional `OdsStatsFetcher`, and a `data_sources` map keyed by `DataSource.Type`. The argument parser requires rules spec, OPTIONS path, LOG prefix, and stats dump period, and accepts ODS client/entity/key-prefix/time bounds.

## Control Flow

Execution parses arguments, loads and validates rules, loads options, builds log and statistics data sources, appends ODS time-series source if requested, evaluates triggered rules, and prints details through `RulesSpec.print_rules`.

## State and Persistence Behavior

The script reads options/logs and may write ODS fetcher temp output files indirectly. Trigger state is held in memory on parsed rules and conditions.

## Dependencies and Integration Points

It integrates the parser modules as a standalone advisor diagnostic flow without running `db_bench` or optimizer iterations.

## Risks and Test Signals

Risks include missing files, ODS argument combinations that are not fully validated, parser side effects from external clients, and direct printing rather than structured output. Signals are successful CLI invocation on fixture options/logs and expected triggered rule names.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser_example.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rules.ini -->
# sources/storage-engines/rocksdb/tools/advisor/advisor/rules.ini

## Purpose

`rules.ini` is the default expert-rule specification for the RocksDB Advisor. It describes symptoms, conditions, and configuration suggestions for write stalls, L0/compaction pressure, Bloom filter usefulness, latency spikes, and decompression overhead.

## Important APIs, Types, and Functions

The file defines `[Rule]`, `[Condition]`, and `[Suggestion]` sections consumed by `RulesSpec`. Conditions use `source=LOG`, `source=OPTIONS`, or `source=TIME_SERIES`; suggestions use `option`, `action`, optional `suggested_values`, and sometimes freeform `description`.

## Control Flow

At runtime the parser loads each section into objects. Log rules match stall regexes, option rules evaluate Python expressions over `options`, and time-series rules evaluate bursty or expression behavior over `keys`. Triggered rules cause suggestions such as increasing background flushes/compactions, write buffer size, L0 triggers, pending compaction byte limits, Bloom bits, cache size, or changing compression type.

## State and Persistence Behavior

The file is static configuration. It drives in-memory rule objects and later option updates; it does not persist results.

## Dependencies and Integration Points

It depends on exact parser keywords and RocksDB option names. It integrates with `rule_parser_example.py`, `config_optimizer_example.py`, and `ConfigOptimizer`.

## Risks and Test Signals

Risks include a likely typo `[Rules "tuning-iostat-burst"]` that is not a recognized `Rule` header, use of Python `eval`, option names that may drift from RocksDB, and thresholds that are workload-specific. Tests use reduced fixture rule files, so the full default file needs separate smoke coverage with representative logs/options/time-series data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/advisor/rules.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/__init__.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/__init__.py

## Purpose

This empty file marks `tools/advisor/test` as a Python package for Advisor unit tests.

## Important APIs, Types, and Functions

It defines no runtime API.

## Control Flow

Importing the package has no side effects.

## State and Persistence Behavior

There is no state or persistence.

## Dependencies and Integration Points

It integrates with Python test discovery/import behavior for tests under `tools/advisor/test`.

## Risks and Test Signals

Risk is minimal. A test signal is successful `unittest` discovery/import of the Advisor test modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err1.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err1.ini

## Purpose

This fixture contains intentionally invalid Advisor rules used to verify section validation failures after parsing succeeds.

## Important APIs, Types, and Functions

It defines rules missing suggestions or conditions, conditions missing options, expressions, or regexes, and suggestions missing option/description fields. It is consumed by `TestSanityChecker` in `test_rule_parser.py`.

## Control Flow

Tests parse the file with `RulesSpec.load_rules_from_spec`, fetch the dictionaries, and call `perform_checks()` on selected rules, conditions, and suggestions expecting `ValueError` messages.

## State and Persistence Behavior

It is static test input and has no runtime persistence.

## Dependencies and Integration Points

It depends on exact section names such as `missing-suggestions`, `missing-conditions`, `missing-regex`, `missing-options`, `missing-expression`, `missing-option`, and `missing-description`.

## Risks and Test Signals

Risks are fixture drift from parser error messages and accidentally making an invalid section valid. Signals are the `assertRaisesRegex` checks in `TestSanityChecker`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err1.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err2.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err2.ini

## Purpose

This fixture verifies parse-time failure when a condition has `source=` with no source type but then receives a source-specific parameter.

## Important APIs, Types, and Functions

It defines a normal rule referencing `missing-source`, a condition with empty `source`, and normal suggestions.

## Control Flow

`RulesSpec.load_rules_from_spec` creates a base `Condition`, sees the empty source value, does not convert it to `LogCondition`, then calls the base `Condition.set_parameter` for `regex`, which raises `NotImplementedError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_condition_missing_source`.

## Risks and Test Signals

The fixture depends on source being required before source-specific keys and on the base class raising the expected message. A passing test confirms malformed source handling still fails early.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err2.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err3.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err3.ini

## Purpose

This fixture verifies parse-time failure for a suggestion that names an option but leaves `action` empty.

## Important APIs, Types, and Functions

It defines `Suggestion "missing-action"` with `option=DBOptions.max_background_flushes` and `action=`, plus a normal rule/condition/suggestion.

## Control Flow

During `RulesSpec.load_rules_from_spec`, `Suggestion.set_parameter("action", None)` detects that an option is already present and raises `ValueError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_suggestion_missing_action`.

## Risks and Test Signals

The signal is an expected parse-time `ValueError`. If parser ordering changes to allow late validation only, this fixture/test contract would need adjustment.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err3.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err4.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err4.ini

## Purpose

This fixture verifies section-header validation when a section type lacks a quoted section name.

## Important APIs, Types, and Functions

It ends with `[Suggestion]` followed by valid-looking suggestion keys.

## Control Flow

`RulesSpec.load_rules_from_spec` classifies `[Suggestion]` as a suggestion section, then `IniParser.get_section_name` fails because there is no quoted name token and raises `ValueError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_section_no_name`.

## Risks and Test Signals

The test protects the DSL requirement that every Rule, Condition, and Suggestion section has a stable quoted identifier.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err4.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/test_rules.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/test_rules.ini

## Purpose

This fixture defines a small rule set for verifying conjunction semantics in the Advisor rule parser.

## Important APIs, Types, and Functions

It includes `single-condition-false`, `multiple-conds-true`, and `multiple-conds-one-false`, with four LOG conditions and three suggestions. `l0-l1-ratio-health-check` uses a description-only suggestion.

## Control Flow

Tests load the file, trigger conditions from fixture LOG data, and assert that only the rule whose full condition list is true becomes triggered.

## State and Persistence Behavior

Static fixture only. Runtime trigger state accumulates on parsed condition/rule objects during tests.

## Dependencies and Integration Points

It is used by `TestConditionsConjunctions` with `LOG-1` and `OPTIONS-000005`.

## Risks and Test Signals

The signal is exact triggered/not-triggered rule membership. Risks are regex drift from fixture logs or names changing without updating tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/test_rules.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/triggered_rules.ini -->
# sources/storage-engines/rocksdb/tools/advisor/test/input_files/triggered_rules.ini

## Purpose

This fixture defines a rule set expected to fully trigger against Advisor test LOG and OPTIONS fixtures.

## Important APIs, Types, and Functions

It mirrors core stall and compaction rules from `advisor/rules.ini`: memtable stalls, L0 stalls/stops, pending compaction byte stalls, and a level0-level1 option ratio health rule. Suggestions include background flush/compaction, write buffer, subcompaction, L0 trigger, and pending-byte-limit changes.

## Control Flow

`TestAllRulesTriggered` loads this file, builds log/options data sources, asserts conditions are initially unset, runs `get_triggered_rules`, and verifies every non-time-series condition and every rule is triggered with the expected suggestion names.

## State and Persistence Behavior

Static fixture only. It drives in-memory trigger dictionaries during tests.

## Dependencies and Integration Points

It depends on matching regexes in `LOG-0` and option values in `OPTIONS-000005`.

## Risks and Test Signals

The fixture is a strong smoke test for log/option rule integration but does not cover time-series sections. Main signal is exact rule-to-suggestion membership in `RuleToSuggestions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/input_files/triggered_rules.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_bench_runner.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/test_db_bench_runner.py

## Purpose

This test module verifies `DBBenchRunner` setup, command construction, log-path derivation, and live experiment data-source assembly.

## Important APIs, Types, and Functions

It imports `DBBenchRunner`, `DatabaseOptions`, `DataSource`, and `NO_COL_FAMILY`. Tests cover constructor state, `get_info_log_file_name`, `get_opt_args_str`, `get_log_options`, `_build_experiment_command`, and `run_experiment`.

## Control Flow

Setup builds a runner with `./../../db_bench`, `overwrite`, and db_bench arguments, then loads fixture OPTIONS. Unit tests mutate options and compare expected strings/paths. The integration-style test updates misc options, runs a real db_bench experiment on `/dev/shm`, and checks returned data-source types.

## State and Persistence Behavior

Tests may generate `OPTIONS_12345.tmp`, create/remove RocksDB data under `/dev/shm`, and rely on `temp/dbbench_out.tmp`/`temp/dbbench_err.tmp`.

## Dependencies and Integration Points

It depends on the `db_bench` binary being present relative to the test directory for the live experiment. It integrates the benchmark runner with options and data-source creation.

## Risks and Test Signals

Risk is environment sensitivity: missing binary, insufficient `/dev/shm`, or command output changes can fail the live test. Signals are exact command strings, log prefix paths, optional arg filtering, and returned DB_OPTIONS/LOG/TIME_SERIES data sources.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_bench_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_log_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/test_db_log_parser.py

## Purpose

This module tests the Advisor LOG parser and log-condition triggering behavior.

## Important APIs, Types, and Functions

Tests use `Log`, `DatabaseLogs`, `NO_COL_FAMILY`, `Condition`, and `LogCondition`. `TestLog` validates field accessors, timestamp conversion, multiline appends, column-family detection, and `is_new_log`. `TestDatabaseLogs` validates trigger maps from fixture logs.

## Control Flow

Tests construct synthetic log lines for direct `Log` assertions, then create `DatabaseLogs` over `input_files/LOG-0`, build three conditions, run `check_and_trigger_conditions`, and assert matching and nonmatching trigger contents.

## State and Persistence Behavior

The module reads fixture LOG files only. Trigger dictionaries are stored on condition objects.

## Dependencies and Integration Points

It depends on fixed fixture log paths and expected column-family tokens. It covers the log side of `RulesSpec` data-source integration.

## Risks and Test Signals

Signals include exact timestamps, column family fallback to `DB_WIDE`, multiline message preservation, and matched log counts per column family. Risks are fixture format drift and the parser's assumption that logs begin with a timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_log_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_options_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/test_db_options_parser.py

## Purpose

This test module verifies parsing, querying, updating, diffing, config generation, and option-condition triggering for `DatabaseOptions`.

## Important APIs, Types, and Functions

It tests `DatabaseOptions.get_options_diff`, `is_misc_option`, constructor/setup, `get_all_options`, `get_misc_options`, `get_column_families`, `get_options`, `update_options`, `generate_options_config`, and `check_and_trigger_conditions` with `OptionCondition`.

## Control Flow

Setup loads `OPTIONS-000005` with misc options and removes a previously generated test OPTIONS file. Tests construct expected dictionaries, apply updates to DB-wide, column-family, table, and misc options, generate a temp config, and evaluate option conditions over database-wide, column-family-only, and mixed scopes.

## State and Persistence Behavior

It reads fixture OPTIONS and writes/removes `../temp/OPTIONS_testing.tmp`. It mutates one `DatabaseOptions` instance per test setup.

## Dependencies and Integration Points

It covers the options parser used by `DBBenchRunner`, `RulesSpec` option conditions, and `ConfigOptimizer`.

## Risks and Test Signals

Signals are exact option maps, diff tuples, generated file existence, column families `default` and `col_fam_A`, and trigger maps. Risks are order/format assumptions and use of `eval` expressions in conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_options_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_stats_fetcher.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/test_db_stats_fetcher.py

## Purpose

This module tests time-series condition evaluation for LOG-derived statistics and cumulative perf-context conversion.

## Important APIs, Types, and Functions

It imports `LogStatsParser`, `DatabasePerfContext`, `NO_ENTITY`, `Condition`, and `TimeSeriesCondition`. Tests cover bursty triggers, evaluate-expression triggers with `latest` aggregation, evaluate-expression triggers per epoch, and `DatabasePerfContext.unaccumulate_metrics`.

## Control Flow

Setup reads a fixture `log_stats_parser_keys_ts` into `LogStatsParser.keys_ts`, then mocks `fetch_timeseries` so condition evaluation uses deterministic data. Conditions are built dynamically by converting base `Condition` objects into `TimeSeriesCondition` and setting keys, behavior, thresholds, windows, expressions, and aggregation operations.

## State and Persistence Behavior

The tests are in-memory except for reading the fixture stats file. Condition triggers are mutable per test.

## Dependencies and Integration Points

They cover `TimeSeriesData` behavior used by `LogStatsParser`, `DatabasePerfContext`, and ODS-backed stats.

## Risks and Test Signals

Signals are exact trigger dictionaries and unaccumulated metric maps. Risks include timestamp alignment assumptions, floating-point exactness, and lack of direct ODS parser coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_db_stats_fetcher.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_rule_parser.py -->
# sources/storage-engines/rocksdb/tools/advisor/test/test_rule_parser.py

## Purpose

This is the main test suite for Advisor rule loading, validation, triggering, conjunction semantics, and parsing errors.

## Important APIs, Types, and Functions

It imports `RulesSpec`, `DatabaseOptions`, `DatabaseLogs`, and `DataSource`. Test classes are `TestAllRulesTriggered`, `TestConditionsConjunctions`, `TestSanityChecker`, and `TestParsingErrors`. The `RuleToSuggestions` map defines exact expected suggestions for triggered fixture rules.

## Control Flow

The first two classes load rules/options/log fixtures and build data-source maps, assert initial untriggered state, run triggering, and check conditions/rules. The sanity checker loads invalid rules and calls `perform_checks` expecting `ValueError`. Parsing-error tests load individual malformed INI files expecting parse-time exceptions.

## State and Persistence Behavior

The module reads fixture INI, LOG, and OPTIONS files. Runtime trigger state is held in parsed rule/condition objects.

## Dependencies and Integration Points

It exercises the interaction among `RulesSpec`, `DatabaseLogs`, `DatabaseOptions`, and the parser fixtures.

## Risks and Test Signals

Signals are exact triggered rule membership, expected suggestion names, condition truth values, and error regexes. The suite covers LOG and OPTIONS rules strongly, but time-series rule parsing/validation is mostly covered elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/advisor/test/test_rule_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/analyze_txn_stress_test.sh -->
# sources/storage-engines/rocksdb/tools/analyze_txn_stress_test.sh

## Purpose

This debugging script analyzes RocksDB transaction stress-test LOG output around a failed `RandomTransactionVerify` snapshot. It reconstructs committed transactions and expected key values between two snapshots.

## Important APIs, Types, and Functions

It uses environment variables `LOG`, `vn`, `vn_1`, and optional `SET`. It writes intermediate files `/tmp/txn.txt`, `/tmp/names.txt`, `/tmp/changes.txt`, `/tmp/va.txt`, `/tmp/vb.txt`, `/tmp/keys.txt`, and `/tmp/adds.txt`. The implementation is shell pipelines around `grep`, `awk`, `cut`, `sort`, `uniq`, and arithmetic expansion.

## Control Flow

The script prints inputs, extracts transactions committed between snapshots, maps transaction IDs to names, gathers all change lines, computes total inserts, compares read values between prior and failing snapshots, checks missing keys, and validates that per-key inserted deltas reconcile from first to last change.

## State and Persistence Behavior

It reads only the specified LOG but overwrites fixed `/tmp` scratch files. It returns `1` from the sourced shell context on detected inconsistency in the final loop.

## Dependencies and Integration Points

It is meant to be sourced after running a specific `transaction_test` gtest with detailed logging enabled.

## Risks and Test Signals

Risks include fixed temp filenames, brittle field positions, unquoted variables, sourcing assumptions, and log-format dependence. Test signals are manually inspected mismatched keys, missing-key lines, and `inconsistent txn` output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/analyze_txn_stress_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/auto_sanity_test.sh -->
# sources/storage-engines/rocksdb/tools/auto_sanity_test.sh

## Purpose

This script performs forward/backward RocksDB format compatibility checks between two git commits using `db_sanity_test`.

## Important APIs, Types, and Functions

It accepts `[new_commit] [old_commit]`, defaults to the newest and tenth newest commits, uses `TMPDIR`/`/tmp` for `rocksdb-sanity-test`, and defines `makestuff` to run `make clean` and `make db_sanity_test -j32`.

## Control Flow

The script checks out the new commit, builds `db_sanity_test`, creates a DB, stores tool sources in the temp DB directory, checks out the old commit, restores the tool sources, builds again, creates an old DB, then verifies the old DB with the new binary and the new DB with the old binary. It cleans binaries and temp DBs on success.

## State and Persistence Behavior

It mutates the git working tree via `git checkout`, runs builds, creates temp DB directories, and temporarily renames built binaries. It does not restore the original branch/commit.

## Dependencies and Integration Points

It depends on git history, Makefile targets, `db_sanity_test`, and RocksDB compatibility semantics.

## Risks and Test Signals

Risks are destructive checkout/build side effects, dirty worktree hazards, unquoted paths, and no trap cleanup. Signals are successful create/verify steps and explicit exit code `2` on compatibility failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/auto_sanity_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/backup_db.sh -->
# sources/storage-engines/rocksdb/tools/backup_db.sh

## Purpose

This shell wrapper invokes `ldb backup` to create a RocksDB backup from a database path to a backup directory.

## Important APIs, Types, and Functions

It expects two arguments, `<DB Path>` and `<Backup Dir>`, assigns them to `db_dir` and `backup_dir`, and runs `./ldb backup --db="$db_dir" --backup_dir="$backup_dir"`.

## Control Flow

If fewer than two arguments are supplied, it prints usage and exits `1`; otherwise it prints the operation and delegates to `ldb`.

## State and Persistence Behavior

It reads the source DB and writes backup files through `ldb`. The script itself keeps no state.

## Dependencies and Integration Points

It depends on an executable `./ldb` in the current directory and RocksDB backup support compiled into that tool.

## Risks and Test Signals

Risks are no preflight validation of paths, no propagation handling beyond the command exit status, and dependence on current working directory. Signals are `ldb backup` exit status and the presence of backup metadata/files in the target directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/backup_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark.sh -->
# sources/storage-engines/rocksdb/tools/benchmark.sh

## Purpose

`benchmark.sh` is the main RocksDB performance benchmark wrapper around `db_bench`. It provides named benchmark jobs, environment-driven configuration, stats collection, and normalized TSV reporting.

## Important APIs, Types, and Functions

It defines many environment knobs: DB/WAL/output paths, key/value sizes, cache, compression, compaction style, blob settings, O_DIRECT, sync, threads, durations, and write limits. Important functions are `display_usage`, `get_cmd`, `start_stats`, `stop_stats`, `units_as_gb`, `summarize_result`, `run_bulkload`, `run_manual_compaction_worker`, `run_univ_compaction`, `run_fillseq`, `run_lsm`, `run_change`, `run_filluniquerandom`, read/range helpers, and `run_randomtransaction`.

## Control Flow

The script validates arguments and required `./db_bench`, builds common db_bench argument strings based on compaction style, dispatches comma-separated jobs, records schedule start/end entries, runs db_bench under `/usr/bin/time` and optional `timeout`/`numactl`, starts background `iostat`, `vmstat`, process, and size samplers for most jobs, summarizes db_bench output, and appends one TSV report row per benchmark.

## State and Persistence Behavior

It creates output logs, `.time`, `.stats.*`, compressed iostat/vmstat files, `schedule.txt`, and `report.tsv`. It mutates the RocksDB database and WAL directories according to each benchmark.

## Dependencies and Integration Points

It depends on `db_bench`, Bash, GNU-ish core utilities, `awk`, `bc`, `gzip`, `iostat`, `vmstat`, `ps`, and RocksDB db_bench output formats. `benchmark_compare.sh` and CI wrappers call it.

## Risks and Test Signals

Risks include unquoted variables, `eval`, fragile grep/awk parsing, background process cleanup via broad `killall`, output format drift, and destructive DB reuse. Signals are completed jobs, report header/rows, schedule entries, compressed stats files, and nonfailed TSV metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_ci.py -->
# sources/storage-engines/rocksdb/tools/benchmark_ci.py

## Purpose

This Python wrapper runs `benchmark_compare.sh` for the current RocksDB build/version in CI, using the just-built `db_bench` binary and copying the resulting report to a stable output path.

## Important APIs, Types, and Functions

`Config` stores version, data, result, script, and cwd paths plus `benchmark_env_keys`. Functions are `read_version`, `prepare`, `results`, `cleanup`, `get_benchmark_env`, and `main`.

## Control Flow

`main` parses directories and key count, reads `include/rocksdb/version.h`, builds a version string, removes stale result contents for that version, symlinks `tools/db_bench.<version>` to the current `db_bench`, collects allowed environment variables, runs `benchmark_compare.sh db_dir results_dir version`, copies `<version>/report.tsv` to `results_dir/report.tsv`, and removes the symlink in `finally`.

## State and Persistence Behavior

It deletes old files/directories under the versioned results directory, creates/removes a symlink in `tools`, and writes/copies benchmark reports.

## Dependencies and Integration Points

It depends on Python stdlib, RocksDB version headers, built `db_bench`, and `tools/benchmark_compare.sh`.

## Risks and Test Signals

Risks include recursive cleanup with plain `os.rmdir`, symlink collisions, no `check=True` on `subprocess.run`, and environment truncation to whitelisted keys. Signals are logged version, successful symlink lifecycle, benchmark_compare output, and copied `report.tsv`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_ci.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_compare.sh -->
# sources/storage-engines/rocksdb/tools/benchmark_compare.sh

## Purpose

This script compares performance across one or more RocksDB `db_bench.<version>` binaries by running a fixed benchmark sequence and generating per-version reports plus a cross-version summary.

## Important APIs, Types, and Functions

It accepts `db_dir output_dir version+`, collects environment knobs for benchmark shape and RocksDB options, builds arrays `base_args`, `args_common`, `args_load`, `args_nolim`, and `args_lim`, and defines `usage` and `dump_env`.

## Control Flow

After validation, it loops over each version, creates a version output directory, symlinks `db_bench` to `db_bench.<version>`, clears database files, runs load, read-only, read-mostly, and write-only jobs through `benchmark.sh`, copies/gzips LOG files, then builds `summary.tsv` by grouping corresponding report rows across versions.

## State and Persistence Behavior

It creates output directories, args files, symlinks, reports, summary TSV, RocksDB database contents, and compressed logs. It deletes files under `dbdir` between versions.

## Dependencies and Integration Points

It depends on Bash arrays, `benchmark.sh`, versioned db_bench binaries, coreutils, gzip, and `awk`. `benchmark_ci.py` calls it for a single current version.

## Risks and Test Signals

Risks include destructive `find "$dbdir" -type f -exec rm`, symlink replacement, output directory refusal if preexisting, unquoted conditionals in places, and variability from compaction debt. Signals are per-version `report.tsv`, copied/gzipped LOG files, `args`, and final `summary.tsv` grouping.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_compare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_leveldb.sh -->
# sources/storage-engines/rocksdb/tools/benchmark_leveldb.sh

## Purpose

This legacy wrapper runs LevelDB fork benchmarks using a db_bench-compatible binary and emits a small report for comparison with RocksDB-style workloads.

## Important APIs, Types, and Functions

It accepts one comma-separated job argument among `fillseq`, `overwrite`, `readrandom`, `readwhilewriting`, and `debug`. Environment knobs include `DB_DIR`, `OUTPUT_DIR`, `DB_BENCH_NO_SYNC`, `NUM_THREADS`, `WRITES_PER_SECOND`, `CACHE_SIZE`, `NUM_KEYS`, and `VALUE_SIZE`. Functions include `summarize_result`, `run_fillseq`, `run_change`, `run_readrandom`, `run_readwhile`, and `now`.

## Control Flow

The script validates a single argument and `DB_DIR`, builds common db_bench flags, dispatches jobs, logs schedule entries, executes commands through `eval`/`tee`, parses output metrics, appends `report.txt`, and prints the latest row.

## State and Persistence Behavior

It writes logs, `report.txt`, and `schedule.txt` under `OUTPUT_DIR`, and mutates the database under `DB_DIR`.

## Dependencies and Integration Points

It depends on a LevelDB fork's `db_bench` binary with expected options and output format, plus shell utilities and `bc`.

## Risks and Test Signals

Risks include legacy output parsing, no support for many modern RocksDB settings, unquoted variables, and `eval`. Signals are benchmark logs, report rows with ops/sec/latency, and schedule timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/benchmark_leveldb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/blob_dump.cc -->
# sources/storage-engines/rocksdb/tools/blob_dump.cc

## Purpose

`blob_dump.cc` is the command-line entry point for inspecting RocksDB BlobDB/blob files through `BlobDumpTool`.

## Important APIs, Types, and Functions

It includes `utilities/blob_db/blob_dump_tool.h`, maps display strings `none`, `raw`, `hex`, and `detail` to `BlobDumpTool::DisplayType`, defines long options `--help`, `--file`, `--show_key`, `--show_blob`, `--show_uncompressed_blob`, and `--show_summary`, and calls `BlobDumpTool::Run`.

## Control Flow

`main` parses options with `getopt_long`. Help prints usage and exits. Optional display options without explicit values default blob/uncompressed blob display to hex, while keys default to raw. Invalid display types or unknown options return `-1`. After parsing, `BlobDumpTool tool; tool.Run(...)` performs the actual dump and returns success/failure.

## State and Persistence Behavior

The program reads the specified blob file and writes output to stdout/stderr. It does not mutate database state.

## Dependencies and Integration Points

It depends on libc `getopt`, C++ containers/strings, RocksDB `Status`, and `BlobDumpTool`. It integrates with RocksDB's tool build targets when included.

## Risks and Test Signals

Risks include not requiring `--file` before running, optional argument parsing quirks for short options, and returning `-1` instead of conventional positive exit codes. Signals are help output, invalid display-type errors, successful summary/detail/raw/hex dumps, and failure status for missing/corrupt files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/blob_dump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/__init__.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/__init__.py

## Purpose

This package initializer marks `tools/block_cache_analyzer` as an executable/importable Python package area and carries the script header/copyright.

## Important APIs, Types, and Functions

It defines no Python symbols beyond file metadata comments.

## Control Flow

Importing the package executes no substantive code.

## State and Persistence Behavior

There is no state or persistence.

## Dependencies and Integration Points

It integrates with Python import/discovery for the block cache analyzer tooling.

## Risks and Test Signals

Risk is minimal. A useful signal is successful import of the package and neighboring analyzer modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/__init__.py -->
