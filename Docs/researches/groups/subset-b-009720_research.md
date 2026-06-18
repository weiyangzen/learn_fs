<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/log_functions.c -->
# sources/user-network-fs/nfs-ganesha/src/log/log_functions.c

## Purpose
This is the central logging implementation for NFS-Ganesha. It owns log facility registration, active/default logger selection, log message formatting, component and conditional component log levels, file/syslog/stream output, in-process log rotation, crash backtrace emission, DBus log control surfaces, and parsing/committing of the `LOG` configuration block.

## Important APIs, Types, and Functions
Key global state includes `log_rwlock`, `cond_log_rwlock`, `log_rotate_rwlock`, `last_rotation_time`, `logfields`, `log_rotate_limits`, `facility_list`, `active_facility_list`, `default_facility`, `max_headers`, `component_log_level`, `conditional_component_log_level`, `default_log_level`, `original_log_level`, `rpc_debug_flags`, `global_export_id_list`, `global_client_ip_list`, `conditional_logging_configured`, and `cond_log_match_policy`. Thread-local logging context is carried in `thread_name`, `log_buffer`, and `clientip`.

Important structures are `struct logfields` for header/date/component display choices, `struct log_facility` for an output sink, `struct logger_config` for staged config parsing, `struct facility_config` for a pending facility block, and `struct conditional_config` for conditional log levels. `tabLogLevel`, `ConditionalLogPolicy`, `default_log_levels`, `default_conditional_log_levels`, and `LogComponents` map enum values to strings, short names, and syslog levels.

Public/externally important functions include `init_logging`, `Cleanup`, `RegisterCleanup`, `Fatal`, `ReturnLevelAscii`, `ReturnLevelInt`, `ReturnMatchPolicyAscii`, `SetNamePgm`, `SetNameHost`, `SetNameFunction`, `SetClientIP`, `SetComponentLogLevel`, `SetConditionalComponentLogLevel`, `DisplayLogComponentLevel`, `display_log_component_level`, `LogMallocFailure`, `rpc_warnx`, `read_log_config`, `gsh_log_backtrace`, `_ratelimit`, `conditional_logging_export_match`, and `conditional_logging_client_match`. Facility management is exposed through `create_log_facility`, `release_log_facility`, `enable_log_facility`, `disable_log_facility`, `set_log_destination`, and `set_log_level`; `set_default_log_facility` is internal.

## Control Flow
`init_logging()` initializes locks and lists, builds the default constant header fragment, creates `STDERR`, `STDOUT`, and `SYSLOG` facilities, chooses a default facility based on `-L`/`log_path`, optionally creates a `FILE` facility, and applies the startup debug level. If enriched libunwind is enabled, it also starts a watchdog thread that aborts if crash handling appears stuck.

Message emission enters through `DisplayLogComponentLevel()` or `display_log_component_level()`. The latter writes a timestamp/header prefix with `display_log_header()`, adds per-message component context through `display_log_component()`, appends the formatted user message, then takes `log_rwlock` for reading and sends the buffer to every active facility whose `lf_max_level` allows the message. Facility callbacks can output only the body, component-prefixed body, or full header depending on `lf_headers`. Fatal-level messages call `Fatal()` after dispatch, which logs a backtrace and exits.

Output callbacks are specialized. `log_to_syslog()` lazily calls `openlog()` and writes the component-formatted string at the syslog priority mapped from the Ganesha log level. `log_to_stream()` appends a temporary newline, chooses the substring requested by the header mode, writes/flushed a `FILE *`, then restores the buffer. `log_to_file()` opens the destination on each write with append/create, writes the full buffer plus newline, checks rotation, closes, and reports write/open/close failures to stderr.

Log rotation is controlled by `log_rotate_limits`. `should_rotate()` checks configured size and elapsed monotonic time. `rotate_if_should()` rechecks under `log_rotate_rwlock`, renames the active path to `<path>.old`, and updates `last_rotation_time` after successful rename.

Config parsing is staged. `read_log_config()` calls the config parser with `logging_param`. Nested init/commit handlers allocate temporary `logfields`, component-level arrays, facility configs, conditional-level arrays, and rotate limits. `log_conf_commit()` creates or updates facilities first, releases failed new facilities, then swaps validated global `logfields` and `log_rotate_limits`, applies default/component levels through `apply_logger_config_levels()`, updates conditional match policy, UTC timestamp selection, and nTI-RPC debug flags. On validation/resource errors, temporary objects are freed instead of becoming active.

Conditional logging input can arrive from config (`Conditional { Exports; Clients; ... }`) or DBus. Config adders call `add_export_id()` and `add_client()` and set `conditional_logging_configured` on success. Runtime match helpers delegate to `is_export_id_match()` and `client_match()`. DBus methods enable/disable exports and clients, list configured entries, and change/show match policy.

Crash backtraces choose libunwind if compiled, optionally followed by enriched `addr2line` output using `/proc/self/maps`. Otherwise `backtrace()`/`backtrace_symbols_fd()` are used. Backtrace code tries to write directly to an active file facility when available to reduce reliance on regular logging during failure handling.

## State and Persistence Behavior
Most logging state is in process memory and protected by read/write locks. Facility names and file paths are heap-owned; file facility paths are duplicated and freed on release/destination replacement. Configured `logfields` and rotate limits replace previous heap-backed objects after successful commit. Component level arrays are global pointers, but active component levels are ultimately copied into `component_log_level` and `conditional_component_log_level`; temporary arrays are freed after commit.

Output persistence is external: file logs append to configured paths, syslog persists through the platform logger, and stream logs go to process stdout/stderr. Rotation persists by renaming one generation to `.old`; there is no multi-generation retention in this file. `disp_utc_timestamp`, `date_time_fmt`, `const_log_str`, and the static log index counter affect formatting but are not persisted across process restart.

Thread context is transient and thread-local. `SetNameFunction()` resets `clientip`; callers must ensure the pointer passed to `SetClientIP()` remains valid for the duration of the thread. Conditional export/client lists persist only in memory unless specified in config and reread on restart.

## Dependencies and Integration Points
The file integrates with `log.h`, `log_common.h`, `display_buffer` helpers, Ganesha lists, memory wrappers, config parsing, core server state (`nfs_core.h`, `op_ctx`, `nfs_param` elsewhere), nTI-RPC debug control (`ntirpc_pp`, `tirpc_control`), SAL export/client helper functions, optional DBus (`gsh_dbus.h`), optional libunwind, optional fridgethr watchdog support, libc syslog, POSIX file APIs, and platform time APIs.

DBus integration exports `org.ganesha.nfsd.log.component` and, when conditional logging is enabled in the build, `org.ganesha.nfsd.log.conditional`. Config integration exposes the unique `LOG` block with nested `Facility`, `Format`, `Components`, `Rotate`, and `Conditional` blocks. Logging also feeds TI-RPC through `rpc_warnx()` and maps `COMPONENT_TIRPC` levels to `ntirpc_pp.debug_flags`.

## Risks and Edge Cases
The logging file deliberately undefines tracing variants of `PTHREAD_RWLOCK_*` to avoid recursive logging, but any future lock/log interaction inside this file can still deadlock if it calls regular logging while holding incompatible locks. `DisplayLogComponentLevel()` holds `log_rwlock` while invoking facility callbacks; callbacks that block on slow disks, stderr, syslog, or close/write stalls delay all concurrent logging.

`log_to_file()` opens and closes the file per message, which avoids shared descriptor lifecycle issues but adds per-log syscall overhead. Rotation is single-generation and races are only partially mitigated; writes that already opened the old path can continue around rename. `rotate_if_should()` opens the current path read-only to recheck size/time, so failure to open suppresses rotation.

`display_timeval()` and `display_timespec()` call `display_printf(dspbuf, tbuf, tv->tv_usec/ts->tv_nsec)` when user-controlled date/time formats select microsecond output. Because `tbuf` is used as a format string, only trusted/admin-controlled format strings should reach `user_date_fmt`/`user_time_fmt`; malformed `%` sequences can behave like format strings.

Conditional DBus handlers generally return a success boolean even when `errormsg` reports an argument or validation failure, so clients must inspect the status reply text/fields rather than only method return. `dbus_conditional_log_export_disable()` calls `gsh_free(&export_entry->export_id_glist)`, which is suspicious because the list member address may not be the allocation base unless `struct export_id_list` embeds it at offset zero.

`get_code_location()` builds an `addr2line` shell command with `popen()`, which is not signal-safe and is intentionally best-effort under the crash watchdog. Enriched backtraces depend on Linux `/proc/self/maps`; portability is limited. `strip_new_line_from_string_end()` assumes a non-empty string.

The default/component level logic uses `NB_LOG_LEVEL` as a sentinel; incorrect initialization of arrays would make normal log levels look unset. Compile-time `CT_ASSERT`s protect enum-array size drift for the main component tables. `SetNamePgm()` and `SetNameHost()` call fatal logging on truncation, which can terminate during early startup.

## Test Signals
Relevant signals include unit or integration tests for `ReturnLevelAscii()` accepting full, shortened, and `NIV_`-less names; config tests covering `LOG` block commit/rollback, `Facility` create/update/default/active states, `Format` validation for user-defined date/time formats, `Components { ALL }` precedence, `Default_Log_Level`, `Rotate`, and `Conditional` lists; DBus tests for component and conditional property get/set plus export/client enable/disable/list/match policy methods; and runtime tests that verify fatal logs emit backtraces.

Operational tests should verify simultaneous logging from many threads, slow or missing log files, invalid file destinations, rotation by size/time, syslog open-on-first-use, stdout/stderr header modes, UTC/local timestamp selection, nTI-RPC debug flag updates when `COMPONENT_TIRPC` changes, and conditional matching by export and client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/log_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/maketest.conf -->
# sources/user-network-fs/nfs-ganesha/src/log/maketest.conf

## Purpose
This is a legacy test-harness configuration for the log library. It declares two tests, `Test_liblog_Standard` and `Test_liblog_Multithread`, that run shell scripts intended to validate static log library behavior.

## Important APIs, Types, and Functions
The file is declarative rather than code. It uses a harness grammar with `Test`, `Product`, `Command`, `Comment`, `Failure`, `Success`, `STATUS`, `STDOUT`, regex matching with `=~`, and boolean `AND`. The commands are `./test_liblog_STD.sh` and `./test_liblog_MT.sh`.

## Control Flow
The harness executes each `Command`, then evaluates failure and success clauses. The standard test fails when `STATUS != 0` and succeeds when stdout contains `PASSED` and status is zero. The multithread test fails on nonzero status and succeeds on zero status.

## State and Persistence Behavior
No persistent application state is managed here. Any state is produced by the invoked shell scripts and the external harness. The top comments preserve historical CVS metadata and indicate the multithread test was added in an old revision.

## Dependencies and Integration Points
This file depends on a test runner that understands the custom `maketest.conf` syntax and on the two shell scripts being present/executable in the working directory. It integrates with the old log test suite, not directly with CMake in the files reviewed here.

## Risks and Edge Cases
The configuration is likely stale relative to current build/test infrastructure. It validates only exit status and a `PASSED` marker for the standard test, so detailed regressions can pass if the script hides them. The multithread test has no stdout assertion. Missing scripts, changed working directories, or a harness that no longer supports this grammar make the file inert.

## Test Signals
Passing signals are explicit: standard script exits zero and prints `PASSED`; multithread script exits zero. Useful modernization signals would be a CTest wrapper or CI job that still runs these scripts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/maketest.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/test_display.c -->
# sources/user-network-fs/nfs-ganesha/src/log/test_display.c

## Purpose
This is a small display-buffer exerciser for the logging/display utility layer. It manually drives `display_printf()`, `display_reset_buffer()`, and `display_opaque_value()` against buffers of different sizes to observe truncation, concatenation, and opaque-byte formatting behavior.

## Important APIs, Types, and Functions
`show_display_buffer()` prints a comment, buffer size, current string length, and buffer contents. `main()` constructs three `struct display_buffer` instances backed by local arrays of 10, 200, and 14 bytes. It calls `display_printf()` repeatedly with strings and integers, resets buffers, and calls `display_opaque_value()` on printable and non-printable byte sequences.

The opaque inputs include a printable string, short binary strings with embedded NUL bytes, and data ending around newline/NUL combinations. Some calls intentionally pass `strlen(opaque3) + 3` to include bytes after the first NUL.

## Control Flow
Execution is linear. Each scenario writes to a display buffer, calls `show_display_buffer()` with a label, then resets before the next scenario. The early tests fill a small buffer with repeated `foo` strings and integer formatting to exercise boundary behavior. Later tests compare opaque formatting in a small buffer, large buffer, and 14-byte buffer.

## State and Persistence Behavior
All state is stack-local. Output is written to stdout for manual or script-based comparison. The test does not persist artifacts by itself and does not assert internally.

## Dependencies and Integration Points
The file depends on `display.h` and the display-buffer implementation elsewhere in the log/support code. It integrates with old log tests by producing deterministic stdout that a harness can inspect. It does not include `log_functions.c`, but it validates lower-level formatting helpers used by logging.

## Risks and Edge Cases
Because the test only prints observations, failures require an external golden-output comparison or manual inspection. Embedded NUL strings mean `strlen()` intentionally stops early in some cases; the one `strlen() + 3` case is designed to include hidden bytes but is easy to misunderstand. The `%z` length format in `show_display_buffer()` assumes the local platform/compiler accepts that length modifier as used here.

## Test Signals
Useful signals are stable stdout lines showing expected truncation and NUL-termination for small buffers, correct reset behavior after repeated calls, integer formatting consistency between small and large buffers, and readable/escaped output for opaque binary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/test_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt

## Purpose
This CMake file builds the `ganesha_monitoring` shared library from the Prometheus exposer and dynamic metrics implementation.

## Important APIs, Types, and Functions
It sets `CMAKE_CXX_STANDARD 17`, defines `ganesha_monitoring_SRCS` as `prometheus_exposer.cc` and `dynamic_metrics.cc`, creates `add_library(ganesha_monitoring SHARED ...)`, optionally links `procps` and defines `HAVE_PROCPS` on Linux, applies sanitizers, sets `-fPIC`, adds the prometheus-cpp-lite include directory, appends strict C++ flags, and installs the library to `${LIB_INSTALL_DIR}`.

## Control Flow
Configuration is platform-dependent. On Linux it calls `find_library(PROCPS_LIB procps)` and either links/defines procps support or emits a warning. On non-Linux platforms it skips procps checks with a status message. The rest of the target setup is unconditional for this directory.

## State and Persistence Behavior
The file persists build-system state through target definitions, compile flags, include paths, linked libraries, and install rules in the generated build tree. It does not manage runtime state.

## Dependencies and Integration Points
It depends on the top-level CMake variables/functions `LINUX`, `add_sanitizers`, `PROJECT_SOURCE_DIR`, and `LIB_INSTALL_DIR`. It integrates with embedded ntirpc monitoring headers under `libntirpc/src/monitoring/prometheus-cpp-lite/core/include` and with platform procps when resource metrics are available.

## Risks and Edge Cases
`add_definitions(-DHAVE_PROCPS)` is directory-wide rather than target-scoped, which can leak into other targets configured from this directory context. Strict `-pedantic-errors -Werror -Wall -Wextra` can break builds on compiler/library warning drift. If procps is unavailable, memory/CPU metrics silently compile out after a warning. The include path is private but hard-coded to the source tree layout.

## Test Signals
Build tests should cover Linux with and without `procps`, and non-Linux configuration. Packaging tests should confirm `libganesha_monitoring` is installed when monitoring is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc

## Purpose
This file implements runtime-created Prometheus metrics for NFS-Ganesha when `USE_MONITORING` is enabled. It records per-operation, per-export, per-client, cache hit/miss, memory, swap, and CPU utilization metrics.

## Important APIs, Types, and Functions
The internal `DynamicMetrics` class owns Prometheus family references for counters, gauges, and histograms. Counter families include `mdcache_cache_hits_total`, `mdcache_cache_misses_total`, `rpcs_received_total`, `rpcs_completed_total`, `nfs_errors_total`, client request/byte totals, operation totals, and export-scoped totals. Gauge families include `last_client_update`, `nfs_memory_resident_ram_size`, `nfs_virtual_ram_size`, `nfs_memory_swap_size`, and `nfs_cpu_utilization`. Histogram families include request/response size and latency, both by operation and by operation/export/path.

`requestSizeBuckets` cover 2 bytes through 16 MiB by powers of two. `latencyBuckets` cover roughly 0.1 ms through 12.783 s. `SimpleMap` is a small shared-mutex-protected cache used to turn `export_id_t` into stable strings like `export_id=123`. Utility functions include `trimIPv6Prefix()`, `GetExportLabel()`, and `toLowerCase()`.

Extern "C" entry points are `dynamic_metrics__init()`, `dynamic_metrics__observe_nfs_request()`, `dynamic_metrics__observe_nfs_io()`, `dynamic_metrics__mdcache_cache_hit()`, `dynamic_metrics__mdcache_cache_miss()`, and, with `HAVE_PROCPS`, `dynamic_metrics__mem_info()`.

## Control Flow
`dynamic_metrics__init()` is idempotent via a static boolean. It obtains the global monitoring registry handle from `monitoring__get_registry_handle()`, casts it to `prometheus::Registry *`, and constructs the single `dynamic_metrics` object.

`dynamic_metrics__observe_nfs_request()` returns immediately until initialized. It converts request time from nanoseconds to milliseconds, lowercases the operation label, optionally updates per-client request count and last-update epoch after trimming IPv4-mapped IPv6 prefixes, increments `nfs_errors_total` for every status label, increments total requests by operation, and observes latency by operation. If `export_id` is nonzero, it also updates request count and latency by operation/export/path.

`dynamic_metrics__observe_nfs_io()` maps `is_write` to an operation label and divides bytes into received/sent. It updates optional per-client byte counters, operation-level byte counters and request/response size histograms, then, for nonzero exports, export/path-scoped byte counters and size histograms.

MDCache hit/miss functions increment operation totals and optional export totals. `dynamic_metrics__mem_info()` converts procps `proc_t` memory fields into gauge values and computes process CPU utilization from proc utime/stime, system uptime, process start time, clock ticks, and online CPU count.

## State and Persistence Behavior
Metric families and label children persist in the in-process Prometheus registry for the life of the process. The global `dynamic_metrics` unique pointer is initialized once and is never reset. Label cardinality is dynamic: every new client, operation, status, export, and path combination can create a persistent child metric. `SimpleMap` caches export labels and grows monotonically.

## Dependencies and Integration Points
The file depends on `dynamic_metrics.h`, `monitoring.h`, prometheus-cpp-lite counter/gauge/histogram APIs, C++ STL containers/locks/strings, `nsecs_elapsed_t`, `NS_PER_MSEC`, and optional procps plus Linux `sysinfo()`. Callers are in server statistics and MDCACHE helper paths; the Prometheus exposer scrapes the registry and calls resource updates after scrapes when dynamic metrics are enabled.

## Risks and Edge Cases
Dynamic labels can create high cardinality, especially `client` and `path`. The header warns that dynamic metrics affect performance, and this implementation confirms that risk by retaining all label children for process lifetime. `operation` is lowercased with `::tolower` on `char`; non-ASCII signed char values would be undefined, though NFS operation strings are expected to be ASCII.

`path` is passed directly into export-scoped labels without a null check in the nonzero-export path. `status_label`, `version`, and `operation` are also assumed non-null. `dynamic_metrics__init()` is not protected by a mutex, so concurrent first calls could race on `initialized` and `dynamic_metrics`. Procps resource gauges are compiled under `HAVE_PROCPS`, but `dynamic_metrics__mem_info()` does not check `dynamic_metrics` before dereferencing it; it relies on initialization order.

The counter `errorsByVersionOperationStatus` is incremented for every status, not only failures, despite its metric name/help saying errors. `rpcsReceivedTotal`, `rpcsCompletedTotal`, and `rpcsInFlight` are declared/registered but not updated in this file.

## Test Signals
Tests should verify idempotent initialization, no-op behavior before initialization for most functions, expected metric names/help/labels, operation lowercasing, IPv4-mapped IPv6 client normalization, export id zero suppression, path label creation for nonzero exports, bucket boundaries, cache hit/miss counters, and procps CPU/memory gauge calculations. Stress tests should measure cardinality and lock overhead under many clients/exports/paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h

## Purpose
This header defines the C ABI used by the rest of NFS-Ganesha to initialize and update dynamic monitoring metrics, while compiling to inline no-ops when monitoring is disabled.

## Important APIs, Types, and Functions
It defines `export_id_t` as `uint16_t`. Under `USE_MONITORING`, it declares `dynamic_metrics__init()`, `dynamic_metrics__observe_nfs_request()`, `dynamic_metrics__observe_nfs_io()`, `dynamic_metrics__mdcache_cache_hit()`, `dynamic_metrics__mdcache_cache_miss()`, and optional `dynamic_metrics__mem_info(proc_t proc_info)` when `HAVE_PROCPS` is defined. Request observation accepts operation, elapsed nanoseconds, NFS version, status label, export id, path, and client IP. IO observation accepts requested/transferred byte counts, read/write direction, export id, path, and client IP.

When `USE_MONITORING` is not defined, the same API is provided as static inline no-op functions with unused-argument annotations.

## Control Flow
The header itself has no runtime control flow beyond compile-time selection. C and C++ callers share the declarations through `extern "C"`. Disabled-monitoring builds compile callers without `#ifdef` blocks because every function returns immediately.

## State and Persistence Behavior
No state is stored in the header. Runtime metric state belongs to `dynamic_metrics.cc` and the monitoring registry. Disabled builds persist no metrics.

## Dependencies and Integration Points
The header depends on `config.h`, `gsh_types.h`, `monitoring.h`, standard integer/size/bool headers, and optional procps `proc/readproc.h`. It is included from C and C++ code paths such as request stats and MDCACHE helpers.

## Risks and Edge Cases
The disabled inline `dynamic_metrics__mem_info` signature takes `proc_t *` while the enabled declaration takes `proc_t` by value. That mismatch can matter for code compiled with `HAVE_PROCPS` but without `USE_MONITORING`, depending on caller expectations. The fallback defines an `UNUSED` macro if missing, which can collide with other local conventions. Callers must still pass valid pointers in enabled builds; the API does not encode nullability.

## Test Signals
Build matrix tests should compile with monitoring on/off and procps on/off. ABI tests should ensure C callers link against the C++ implementation when enabled and compile cleanly to no-ops when disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h

## Purpose
This header declares the Prometheus HTTP exposer API and, for C++ builds with monitoring enabled, the `ganesha_monitoring::PrometheusExposer` class.

## Important APIs, Types, and Functions
It aliases `sockaddr_t` to `struct sockaddr_storage`. Under `USE_MONITORING`, C callers see `prometheus_exposer__start(const sockaddr_t *addr, uint16_t port, prometheus_registry_handle_t registry_handle)` and `prometheus_exposer__stop(prometheus_registry_handle_t registry_handle)`. C++ callers additionally see `update_mem_info()` and the `PrometheusExposer` class.

`PrometheusExposer` owns a Prometheus registry reference, a scrape-latency histogram family, success/failure scrape histograms, a server socket fd, a running flag, a server thread, and a mutex. Copy and move are deleted.

When monitoring is disabled, the start/stop functions are static inline no-ops.

## Control Flow
Compile-time `USE_MONITORING` and `__cplusplus` select either C declarations, C++ class declarations, or no-op stubs. Runtime behavior is implemented in `prometheus_exposer.cc`.

## State and Persistence Behavior
The header defines the shape of runtime state but does not instantiate it. The class is intended to start and stop a background socket server for the lifetime of monitoring.

## Dependencies and Integration Points
It depends on `monitoring.h` for the registry handle and, in C++ mode, prometheus histogram/text serializer/registry headers plus `<thread>`. It is used by C startup/shutdown paths and by the C++ implementation.

## Risks and Edge Cases
The API accepts a generic `sockaddr_storage` pointer and port; callers must initialize the family and address fields correctly. Disabled-monitoring stubs hide all effects, so integration tests must explicitly include enabled builds. The header exposes `update_mem_info()` in C++ only, but that function depends on procps in the implementation.

## Test Signals
Build tests should cover C and C++ inclusion with monitoring enabled and disabled. API tests should verify start/stop linkage from C and class construction/destruction from C++ when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc

## Purpose
This file implements a minimal Prometheus HTTP scrape endpoint for the Ganesha monitoring registry. It listens on an IPv4 or IPv6 socket, serializes collected Prometheus metric families, compacts empty metrics, tracks scrape latency success/failure, and optionally updates procps-backed memory/CPU gauges after scrapes.

## Important APIs, Types, and Functions
`SocketStreambuf` adapts a socket fd to `std::ostream` with a 4096-byte output buffer, blocking `send()` loops, abort tracking, and a mutex-protected `safe_close()`. `is_metric_empty()` and `compact_family()` remove zero-value counter, empty summary, and empty histogram children while retaining at least one child per family. `getBoundries()` returns scrape-latency histogram buckets.

`PrometheusExposer::start()` creates the server socket, sets `SO_REUSEADDR`, binds IPv4 or IPv6, listens, marks `running_`, and starts `server_thread`. `stop()` clears `running_`, shuts down the server fd to wake `accept4()`, joins the thread, closes the socket, and resets the fd. `server_thread()` accepts clients, reads one request buffer, collects/compacts registry families, writes an HTTP 200 text response, serializes metrics, closes the client, observes scrape latency, and calls `update_mem_info()` when procps and dynamic metrics are enabled.

Extern "C" wrappers are `prometheus_exposer__start()`, `prometheus_exposer__stop()`, and optional `update_mem_info()`.

## Control Flow
The server loop runs while `running_` is true. Each accepted connection is handled synchronously in the server thread; there is no per-client worker pool. HTTP parsing is intentionally minimal: it reads up to 1024 bytes and responds with metrics regardless of path or method. Serialization is through `prometheus::TextSerializer::Serialize()`.

`prometheus_exposer__start()` is idempotent with a static `initialized` flag. It casts the registry handle to a Prometheus registry pointer, constructs a static exposer, starts it, then marks initialized. `prometheus_exposer__stop()` has its own static `stopped` flag and constructs another static exposer before calling `stop()`.

## State and Persistence Behavior
Runtime state is in the `PrometheusExposer` instance: socket fd, running flag, thread object, and scrape latency histograms registered in the registry. Metrics persist in the registry; the HTTP endpoint itself persists only while the process is running. `SocketStreambuf` owns no fd but closes the accepted client through `safe_close()`.

## Dependencies and Integration Points
The implementation depends on POSIX sockets (`socket`, `setsockopt`, `bind`, `listen`, `accept4`, `recv`, `send`, `shutdown`, `close`), C++ stream and mutex primitives, `prometheus_exposer.h`, `dynamic_metrics.h`, `gsh_config.h`, prometheus-cpp-lite registry and serializer APIs, global `nfs_param.core_param.enable_dynamic_metrics`, and optional procps (`openproc`, `readproc`) for process resource metrics.

## Risks and Edge Cases
The start and stop C wrappers each declare a separate function-local static `PrometheusExposer exposer(*registry_ptr)`. That means `prometheus_exposer__stop()` does not obviously stop the instance created by `prometheus_exposer__start()`; it constructs/stops a distinct static object. This is a lifecycle risk and could leave the actual server running until process teardown.

Error handling uses `PFATAL`, `PEXIT`, and `abort()/exit(1)` inside a library component. Bind/listen/socket failures can terminate the whole daemon rather than returning an error to startup code. `server_thread()` handles clients serially, so a slow send can block all scrapes. `recv()` return values are ignored; malformed or empty requests still get a response. `accept4()` and `SOCK_CLOEXEC` are Linux-specific unless compat is provided elsewhere. `SocketStreambuf::sync()` treats `send()` returning 0 as progress of zero bytes and could loop indefinitely on unusual socket behavior.

`compact_family()` copies metrics by value in the lambda and removes empty metrics from a collected copy, which is safe for output reduction, but keeping the first empty child may still expose misleading labels. `update_mem_info()` calls `openproc()` but does not close the `PROCTAB`, which can leak per scrape if procps requires `closeproc()`.

## Test Signals
Tests should start the exposer on IPv4 and IPv6 loopback, scrape `/metrics`, verify content type and Prometheus text output, verify compacting retains one empty metric but removes additional empty children, observe success/failure scrape latency updates, and confirm stop actually closes the listening socket. Fault tests should cover bind failures, slow/disconnected clients, procps metric updates, and repeated start/stop calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake

## Purpose
This is the CMake-templated RPM spec for packaging NFS-Ganesha and its optional FSALs, utilities, monitoring module, tracing library, embedded ntirpc, SELinux policy, service units, configs, and admin tooling.

## Important APIs, Types, and Functions
Important RPM/CMake constructs include `%define`, `%global`, `%bcond` placeholders such as `@BCOND_GPFS@`, the `on_off_switch()` macro, CMake-substituted versions (`@GANESHA_BASE_VERSION@`, `@GANESHA_EXTRA_VERSION@`, `@NTIRPC_VERSION_EMBED@`, `@CPACK_SOURCE_PACKAGE_FILE_NAME@`), `%package`, `%description`, `%prep`, `%build`, `%install`, scriptlets (`%pre`, `%post`, `%preun`, `%postun`, `%posttrans`), and many `%files` sections.

The spec defines feature toggles for FSALs (`nullfs`, `mem`, `gpfs`, `xfs`, `lustre`, `ceph`, `rgw`, `gluster`, `kvsfs`), protocols/features (`rdma`, `9P`, `nfs_rdma`, `rpc_rdma`, `qos`, `monitoring`, `nfsidmap`, `rpcbind`, unwind/enriched backtrace, LTTng, RADOS features, admin tools, GUI tools, man pages, sanitizers, allocators, legacy Python install, system ntirpc, and MSPAC).

## Control Flow
At RPM parse time, distro conditionals select BuildRequires/Requires for SUSE, Fedora, RHEL, Python, SELinux, rpcbind/portmap, system ntirpc, and optional packages. `%build` runs `cmake3` with feature toggles translated into `-DUSE_*` and related options, then retries `make` up to three times. SELinux policy is built for Fedora/RHEL platforms that support it.

`%install` creates config, dbus, sysconfig, logrotate, binary, library, log, libexec, and systemd directories; installs sample configs and service files conditionally; runs `make DESTDIR=%{buildroot} install`; installs SELinux policy artifacts; and removes unwanted Python site-package files. Scriptlets create the `ganesha` user/group, register systemd services, set SELinux log fcontexts, reload dbus, and handle service uninstall/restart macros.

`%files` sections assign installed artifacts to the base package and subpackages, including optional FSAL shared objects, configs, man pages, utilities, monitoring libraries, LTTng libraries, SELinux policy, and embedded libntirpc packages when not using system ntirpc.

## State and Persistence Behavior
The spec persists build choices into the RPM build output and installed system state. Installed persistent paths include `/etc/ganesha`, dbus policy, sysconfig, logrotate config, systemd units/drop-ins, `/var/log/ganesha`, FSAL shared libraries under `%{_libdir}/ganesha`, libraries under `%{_libdir}`, libexec scripts, and optional Python/admin tools. Scriptlets persist the `ganesha` system user/group and SELinux fcontext/module state.

## Dependencies and Integration Points
It integrates CMake build options with RPM subpackage topology. It depends on distro RPM macros, systemd macros, optional SUSE service macros, SELinux macros, compiler/build tools, dbus, libcap, blkid, uuid, userspace RCU, Kerberos, nfs-utils, libattr/libacl, optional backend libraries, optional Python/Sphinx/PyQt tooling, optional proc/monitoring libraries via build outputs, and optional embedded ntirpc packaging.

The monitoring toggle creates an `nfs-ganesha-monitoring` package requiring/providing monitoring libraries. The base package depends on that subpackage when `%{with monitoring}`. Service integration installs `nfs-ganesha.service`, `nfs-ganesha-lock.service`, and `nfs-ganesha-config.service`.

## Risks and Edge Cases
The spec is highly conditional and sensitive to distro macro differences. Some conditionals reference features that are not visibly declared in the reviewed top section, such as `%{with pt}`, so template generation must supply all expected bconds. `%define _unpackaged_files_terminate_build 0` can hide packaging omissions. Retrying `make` can mask flaky parallel build dependencies instead of failing deterministically.

The base package requires `nfs-ganesha-selinux` on Fedora >= 30/RHEL >= 8, so SELinux package build failures affect base installability. Python cleanup removes broad site-package paths and must stay aligned with tool installation layouts. Monitoring `%files` includes `libntirpcmonitoring*`; packaging must ensure this artifact exists only when expected. Scriptlets call `killall -SIGHUP dbus-daemon` and SELinux tools opportunistically, which can behave differently across minimal systems.

## Test Signals
Packaging tests should build RPMs across supported distro macro sets and representative feature combinations: default, monitoring, system vs embedded ntirpc, each FSAL family, utils/gui utils, SELinux platforms, and man-page builds. Install/upgrade/remove tests should verify user/group creation, systemd macro behavior, dbus reload, log directory ownership, config marked `noreplace`, and that every installed file is in the intended subpackage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt

## Purpose
This CMake file selects platform-specific OS abstraction sources and builds them into the `gos` object library.

## Important APIs, Types, and Functions
It sets `gos_STAT_SRCS` based on platform flags. FreeBSD uses `freebsd/atsyscalls.c`, `freebsd/mntent_compat.c`, `freebsd/subr.c`, and `freebsd/xattr.c`. Darwin uses `darwin/sys_resource.c`. Linux uses `linux/acl.c` and `linux/subr.c`. It then calls `add_library(gos OBJECT ...)`, applies sanitizers, sets `-fPIC`, and adds LTTng generated-header dependencies when `USE_LTTNG` is enabled.

## Control Flow
Only one platform block should populate `gos_STAT_SRCS` in a normal build. After source selection, target setup is unconditional. LTTng-specific generated file properties are included only under `USE_LTTNG`.

## State and Persistence Behavior
The file persists build graph state: selected source list, object target, compile flags, sanitizer instrumentation, and optional generated header dependency. It has no runtime state.

## Dependencies and Integration Points
It depends on top-level CMake variables `FREEBSD`, `DARWIN`, `LINUX`, `USE_LTTNG`, `CMAKE_BINARY_DIR`, `add_sanitizers`, and the generated file `gsh_lttng_generation_file_properties.cmake`. The `gos` object library provides OS abstraction functions used by FSAL and support code.

## Risks and Edge Cases
If no platform variable is set, `gos_STAT_SRCS` will be empty or undefined and target creation can fail or produce an empty object library. If multiple platform variables are true, later `SET()` calls overwrite earlier selections. Platform-specific source coverage must stay synchronized with headers under `include/os`.

## Test Signals
Configure/build tests on Linux, FreeBSD, and Darwin should confirm the intended source list and successful `gos` object creation. LTTng-enabled builds should verify generated-header ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c -->
# sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c

## Purpose
This Darwin-specific file wraps open-file resource limit discovery and normalizes macOS `RLIMIT_NOFILE` semantics for Ganesha.

## Important APIs, Types, and Functions
It implements `get_open_file_limit(struct rlimit *rlim)`. The function calls `getrlimit(RLIMIT_NOFILE, rlim)` and clamps `rlim->rlim_max` to `OPEN_MAX` when the reported hard limit exceeds `OPEN_MAX`.

## Control Flow
The function returns `-1` if `getrlimit()` fails. On success it applies the macOS compatibility clamp and returns zero.

## State and Persistence Behavior
No persistent state is modified. The caller-provided `struct rlimit` is filled and possibly adjusted.

## Dependencies and Integration Points
It depends on `sys_resource.h`, `getrlimit()`, `RLIMIT_NOFILE`, and Darwin `OPEN_MAX` from `sys/syslimits.h`. It integrates with code that sizes file descriptor resources during startup.

## Risks and Edge Cases
The clamp is Darwin-specific and intentionally deviates from raw `getrlimit()` output. If callers expect the kernel-reported hard limit rather than a usable maximum, they may see a lower value. Failure handling leaves `errno` from `getrlimit()`.

## Test Signals
Darwin tests should verify success on normal systems, error propagation for invalid calls if mockable, and clamping when a hard limit greater than `OPEN_MAX` is reported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/darwin/sys_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c

## Purpose
This FreeBSD compatibility file provides wrappers for `*at` syscalls and Panasas/NFS file-handle syscalls on FreeBSD versions or kernels where libc/kernel support is incomplete.

## Important APIs, Types, and Functions
For newer FreeBSD compiler versions, it defines module-discovered wrappers `getfhat()`, `fhlink()`, and `fhreadlink()` that find syscall modules named `sys/getfhat`, `sys/fhlink`, and `sys/fhreadlink`, read their syscall numbers with `modstat()`, and invoke `syscall()`.

When `SYS_openat` is not defined, it defines hard-coded syscall numbers matching a modified FreeBSD 10.1 environment and implements wrappers for `openat`, `mkdirat`, `mknodat`, `fchownat`, `futimesat`, `fstatat`, `unlinkat`, `renameat`, `linkat`, `symlinkat`, `readlinkat`, `fchmodat`, `faccessat`, `getfhat`, `fhlink`, and `fhreadlink`.

## Control Flow
Module-discovered file-handle wrappers initialize `module_stat`, call `modfind()`, call `modstat()`, extract `stat.data.intval`, then dispatch through `syscall()`. Fallback `*at` wrappers directly call `syscall(SYS_..., args...)`.

## State and Persistence Behavior
No state is stored. Calls rely on kernel syscall/module state at runtime.

## Dependencies and Integration Points
The file depends on FreeBSD syscall headers, `sys/module.h`, `syscalls.h`, and libc `syscall()`. It supports higher-level FSAL/VFS code that expects Linux-like `*at` APIs and Ganesha-specific file-handle operations.

## Risks and Edge Cases
Returning `errno` directly on `modfind()`/`modstat()` failure is inconsistent with normal syscall wrappers that return `-1` and set `errno`. Hard-coded syscall numbers are explicitly tied to a modified FreeBSD 10.1 and are unsafe for arbitrary kernels if compiled in. The fallback only compiles when `SYS_openat` is absent, which may not align with partial syscall availability.

## Test Signals
FreeBSD build tests should cover systems with native `SYS_openat` and without it. Runtime tests need kernels/modules exposing `getfhat`, `fhlink`, and `fhreadlink`, plus basic `*at` operations through the wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/atsyscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c

## Purpose
This file implements `open_memstream()` on FreeBSD using `funopen()`, providing a GNU-like memory stream API where unavailable.

## Important APIs, Types, and Functions
`struct memstream` stores pointers to the caller's buffer pointer and length, plus the current stream offset. `memstream_grow()` reallocates the caller buffer with one extra byte and zero-fills newly exposed memory. `memstream_read()`, `memstream_write()`, `memstream_seek()`, and `memstream_close()` implement the `funopen()` callbacks. `open_memstream(char **cp, size_t *lenp)` initializes outputs, allocates the cookie, and returns a `FILE *`.

## Control Flow
Opening initializes `*cp = NULL`, `*lenp = 0`, allocates a cookie, and calls `funopen()`. Reads and writes grow the backing buffer to cover the requested range, copy bytes, and advance `offset`. Seek updates `offset` based on `SEEK_SET`, `SEEK_CUR`, or `SEEK_END`. Close frees only the cookie; the caller retains ownership of `*cp`.

## State and Persistence Behavior
The buffer and length are caller-visible and persist after `fclose()` until the caller frees the buffer. Internal offset lives in the stream cookie and disappears on close.

## Dependencies and Integration Points
It depends on FreeBSD `funopen()`, stdio, and Ganesha memory wrappers (`gsh_malloc`, `gsh_realloc`, `gsh_free`). It provides compatibility for code expecting `open_memstream()`.

## Risks and Edge Cases
`memstream_grow()` does not handle allocation failure from `gsh_realloc()` locally. The zero-fill starts at `buf + *lenp + 1`, leaving the byte at old length untouched until write behavior sets it; NUL-termination semantics should be verified. `memstream_seek()` does not reject invalid `whence` or negative positions that wrap in `size_t`. Callback signatures use `int len`, which can truncate very large sizes.

## Test Signals
Tests should write strings and binary data, seek forward/backward, read from sparse regions, close and inspect `*cp`/`*lenp`, verify NUL termination, and simulate allocation failure if the memory wrapper supports it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c

## Purpose
This file provides Linux-style mount-entry helpers on FreeBSD, adapting `getmntinfo()`/`statfs` data to `struct mntent` and implementing `hasmntopt()`.

## Important APIs, Types, and Functions
Global static state includes `pos`, `mntsize`, `_mntbuf`, and `_mntent`. `mntoptions[]` maps FreeBSD mount flags to option strings. `hasmntopt()` searches a mount option string for a named option. `catopt()` appends an option to a buffer. `flags2opts()` converts mount flags to `ro`/`rw` plus named options. `statfs_to_mntent()` fills the static `_mntent`. `getmntent(FILE *fp)` iterates mounted filesystems from `getmntinfo()`.

## Control Flow
`getmntent()` lazily calls `getmntinfo()` when iteration is reset, logs all mount source names at full debug, increments `pos`, returns `NULL` and resets when all entries are consumed, otherwise returns a static `struct mntent` view for the current `statfs`. `hasmntopt()` duplicates the options string, tokenizes by spaces, and returns a pointer into the original string when a match is found.

## State and Persistence Behavior
Iteration state is global and not thread-safe. Returned `struct mntent` and option buffer are static and overwritten by subsequent calls. No persistent files are modified.

## Dependencies and Integration Points
The file depends on `os/freebsd/mntent.h`, FreeBSD `getmntinfo()`/`statfs`, mount flag constants, Ganesha memory wrappers, and logging. It supports FSAL code that includes the generic `os/mntent.h`.

## Risks and Edge Cases
`flags2opts()` initializes `char *res = NULL` and passes it to `catopt()` instead of the provided `buf`; this appears to dereference a null pointer when options are appended. `hasmntopt()` tokenizes with `strtok()`, which is not thread-safe. The `FILE *fp` argument to `getmntent()` is ignored. The static iteration state prevents concurrent or nested mount iteration.

## Test Signals
FreeBSD tests should call `getmntent()` through a full mount table, verify option strings for representative flags, call `hasmntopt()` for present/absent options, and run under sanitizers to catch the apparent null-buffer bug in `flags2opts()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/mntent_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c

## Purpose
This file implements FreeBSD-specific OS abstraction routines for directory entry reading, generic directory entry conversion, timestamp updates, and per-thread credential changes.

## Important APIs, Types, and Functions
`vfs_readents()` wraps `getdirentries()`. `to_vfs_dirent()` converts a FreeBSD `struct dirent` in a raw buffer to `struct vfs_dirent`. `vfs_utimesat()` and `vfs_utimes()` adapt `struct timespec` arrays to FreeBSD `futimesat()`/`futimes()` timeval APIs while handling `UTIME_OMIT` and `UTIME_NOW`. Private helpers `setthreaduid()`, `setthreadgid()`, and `setthreadgroups()` discover custom syscall modules and invoke them. Public wrappers `setuser()`, `setgroup()`, and `set_threadgroups()` expose credential switching.

## Control Flow
Directory reads call the kernel and leave offset update to `getdirentries()`. Directory conversion fills inode, record length, type, offset, and name, using `d_off` when `HAS_DOFF` exists or computing offset from base/bpos/reclen otherwise. Time update wrappers return immediately for any `UTIME_OMIT`, pass `NULL` timeval arrays for any `UTIME_NOW`, or convert both timespecs to timevals. Credential helpers discover syscall numbers through `modfind()`/`modstat()` each call.

## State and Persistence Behavior
No module-level state is stored. Calls mutate kernel-visible file timestamps, directory offsets, and thread credential state.

## Dependencies and Integration Points
It depends on FreeBSD directory APIs, custom syscall modules named `sys/setthreaduid`, `sys/setthreadgid`, `sys/setthreadgroups`, Ganesha `os/subr.h`, `syscalls.h`, and logging. FSAL code uses these functions for VFS operations under caller credentials.

## Risks and Edge Cases
The `UTIME_OMIT` handling returns without changing either timestamp when either entry is omit; POSIX semantics allow updating one timestamp while omitting the other, so this loses partial updates. Similarly, any `UTIME_NOW` causes both timestamps to become current. The custom setthread syscall wrappers return `errno` on module lookup failures, while `setuser()`/`setgroup()` log `errno`; if the wrapper did not set `errno` consistently, logs can be misleading.

## Test Signals
FreeBSD tests should verify directory iteration offsets, conversion of empty inode entries, timestamp behavior for normal times, both `UTIME_OMIT`, one `UTIME_OMIT`, both `UTIME_NOW`, one `UTIME_NOW`, and credential changes with and without required syscall modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c

## Purpose
This file maps Linux-style file-descriptor extended attribute APIs onto FreeBSD `extattr_*_fd()` calls for the VFS FSAL.

## Important APIs, Types, and Functions
It implements `fgetxattr()`, `fsetxattr()`, `flistxattr()`, and `fremovexattr()`. All operations use `EXTATTR_NAMESPACE_SYSTEM`. `fsetxattr()` probes existing attribute state with `extattr_get_fd()` and honors Linux-like `XATTR_REPLACE` and `XATTR_CREATE` flags before calling `extattr_set_fd()`.

## Control Flow
Get/list/remove directly call the corresponding FreeBSD extattr function. Set clears `errno`, attempts to get the existing attribute into a stack buffer, returns an error for replace-if-missing or create-if-existing cases, and otherwise sets the value.

## State and Persistence Behavior
The functions persist extended attribute changes on the target file descriptor. No process-global state is stored.

## Dependencies and Integration Points
It depends on `os/freebsd/xattr.h`, FreeBSD `<sys/extattr.h>`, `errno`, and xattr flag definitions. FSAL code can call Linux-compatible xattr names while building on FreeBSD.

## Risks and Edge Cases
`fsetxattr()` returns positive `ENOATTR`/`EEXIST` values instead of `-1` with `errno` set, unlike normal POSIX-style APIs. The existence probe passes the caller's value `size` with a fixed `EXTATTR_MAXNAMELEN` stack buffer; if `size` exceeds 255, this can overflow `buff`. It compares `attr_size != size` to infer missing attributes, which confuses existing attributes whose size differs from the new value. Namespace choice is fixed to system and may not match user xattr expectations.

## Test Signals
FreeBSD xattr tests should cover get/set/list/remove, create-only existing, replace-only missing, attributes larger than 255 bytes, replacing with different-sized values, and errno/return-value compatibility with Linux callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c -->
# sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c

## Purpose
This Linux file supplies non-standard POSIX ACL file-descriptor helpers when the platform lacks `acl_get_fd_np()` or `acl_set_fd_np()`, especially for default ACLs.

## Important APIs, Types, and Functions
Under `#ifndef HAVE_ACL_GET_FD_NP`, `acl_get_fd_np(int fd, acl_type_t type)` returns `acl_get_fd(fd)` for `ACL_TYPE_ACCESS`, otherwise builds `/proc/self/fd/<fd>` and calls `acl_get_file(path, type)`. Under `#ifndef HAVE_ACL_SET_FD_NP`, `acl_set_fd_np(int fd, acl_t acl, acl_type_t type)` similarly uses `acl_set_fd()` for access ACLs and `/proc/self/fd/<fd>` plus `acl_set_file()` for other types.

## Control Flow
Both functions validate `fd >= 0`, format the procfs fd path with `snprintf()`, reject truncation by setting `errno = EINVAL`, and delegate to libacl functions. Get returns `NULL` on error; set returns `-1` on local validation errors or the libacl return code.

## State and Persistence Behavior
Get has no persistent side effect. Set persists ACL changes to the file referenced by the descriptor. No module-global state is kept.

## Dependencies and Integration Points
It depends on `os/acl.h`, libacl APIs, `PATH_MAX`, `/proc/self/fd`, `errno`, and `snprintf()`. It supports FSAL ACL code that wants descriptor-based ACL operations even when libacl lacks the `_np` variants.

## Risks and Edge Cases
The default ACL path fallback depends on procfs being mounted and accessible. Path-based `/proc/self/fd/<fd>` operations can behave differently for some special descriptors or deleted files. The source includes `<stdio.h>` but relies on `PATH_MAX` from headers pulled indirectly through `os/acl.h`; portability depends on that include chain.

## Test Signals
Linux tests should compile with and without native `_np` functions, get/set access ACLs directly, get/set default ACLs through `/proc/self/fd`, handle invalid fds, and run in environments with procfs unavailable or restricted if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c

## Purpose
This file implements Linux-specific OS abstraction routines for raw directory reads, directory entry conversion, timestamp updates, and thread/process credential changes.

## Important APIs, Types, and Functions
`vfs_readents()` invokes `syscall(SYS_getdents64, fd, buf, bcount)` and advances `*basepp` by the returned byte count. `to_vfs_dirent()` converts a raw `struct dirent64` entry into `struct vfs_dirent`. `vfs_utimesat()` wraps `utimensat()`, and `vfs_utimes()` wraps `futimens()`. `setuser()` calls `SYS_setresuid`, `setgroup()` calls `SYS_setresgid`, and `set_threadgroups()` calls `__NR_setgroups`.

## Control Flow
Directory reads return the syscall result and update base offset only on nonnegative results. Conversion copies inode, record length, type, offset, and name; it derives `d_type` from the last byte of the record. Timestamp and credential functions are thin wrappers with logging on setresuid/setresgid failure.

## State and Persistence Behavior
The functions mutate caller-provided offsets, file timestamps, and Linux credential/group state. No module-level state is stored.

## Dependencies and Integration Points
It depends on Linux syscalls, `fsal.h`, `os/subr.h`, `struct dirent64` layout, `utimensat`, `futimens`, and Ganesha logging. It is the Linux implementation selected by `src/os/CMakeLists.txt` for the `gos` object library.

## Risks and Edge Cases
The comment for `to_vfs_dirent()` mentions FreeBSD but the code is Linux-specific. Deriving `d_type` as `buf[dp->d_reclen - 1]` assumes the Linux `getdents64` record layout and ignores `bpos`; it should still point at the current record only because `dp` starts at `buf + bpos`, but the expression reads from the start of `buf`, which is suspicious unless `bpos` is zero. Credential changes use raw syscalls and log errors but do not propagate them from `setuser()`/`setgroup()`.

## Test Signals
Linux tests should verify raw directory iteration over multiple entries with nonzero `bpos`, correct file types, timestamp wrapper behavior including `UTIME_NOW`/`UTIME_OMIT`, and credential/group changes under privileged and unprivileged conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt

## Purpose
This CMake file conditionally includes admin-tool script subdirectories in the build.

## Important APIs, Types, and Functions
It checks `USE_ADMIN_TOOLS` and, when enabled, calls `add_subdirectory(ganeshactl)`, `add_subdirectory(gpfs-epoch)`, and `add_subdirectory(ganesha-top)`.

## Control Flow
The whole file is a single build-time conditional. If admin tools are disabled, no script subdirectories are added from here.

## State and Persistence Behavior
It affects generated build-system state and install targets from child directories. It has no runtime state.

## Dependencies and Integration Points
It depends on the top-level `USE_ADMIN_TOOLS` CMake option and the presence of the three child directories. Packaging in the RPM spec uses the same admin-tools concept through `%{with utils}`/`-DUSE_ADMIN_TOOLS`.

## Risks and Edge Cases
All three tools are tied to one option; there is no per-tool selection here. Missing child directories or child CMake errors break admin-tool builds. Packaging must stay aligned with what these subdirectories install.

## Test Signals
Configure/build tests should run with `USE_ADMIN_TOOLS=ON` and `OFF`, verifying child targets and installed scripts are present only when expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf -->
# sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf

## Purpose
This file configures Linux `checkpatch.pl` for the NFS-Ganesha codebase, disabling kernel-specific checks and adjusting style policy to match a user-space NFS server rather than the Linux kernel tree.

## Important APIs, Types, and Functions
The file is a list of checkpatch flags. `--no-tree` tells checkpatch this is not a kernel tree. Many `--ignore` entries disable kernel-only errors/warnings (`MODIFIED_INCLUDE_ASM`, `UAPI_INCLUDE`, `LOCKDEP`, `EXPORT_SYMBOL`, `PRINTK_*`, etc.), project-accepted style deviations (`CAMELCASE`, `UNNECESSARY_ELSE`, `BRACES`, `SPLIT_STRING`, `SYMBOLIC_PERMS`, `FUNCTION_ARGUMENTS`, `COMPLEX_MACRO`, `MACRO_WITH_FLOW_CONTROL`, `POINTER_LOCATION`, `SPACING`, `INDENTED_LABEL`), and metadata checks (`GERRIT_CHANGE_ID`, `FSF_MAILING_ADDRESS`, `GIT_COMMIT_ID`). It sets `--max-line-length=80`.

## Control Flow
There is no runtime control flow. Checkpatch reads these options and suppresses matching diagnostics when run by project scripts such as `runcp.sh`.

## State and Persistence Behavior
It persists style policy in the repository. It does not modify source files by itself.

## Dependencies and Integration Points
It depends on Linux `checkpatch.pl` option names remaining stable. It integrates with developer/CI style checks and the scripts directory tooling.

## Risks and Edge Cases
The broad ignore list can hide real maintainability issues, especially around complex macros, spacing, pointer location, and date/time usage. One line has a leading space before `--max-line-length=80`; parsers generally tolerate whitespace, but exact tooling should be checked. Duplicate ignores such as `DATE_TIME` are harmless but indicate drift. Misspellings in comments do not affect behavior.

## Test Signals
Style-check tests should run checkpatch with this config on known-good and known-bad patches, verifying that intended project exceptions are suppressed while important non-ignored errors still fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf -->
