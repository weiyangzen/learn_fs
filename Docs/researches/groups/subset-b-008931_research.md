# subset-b-008931 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/jeprof.in -->
# sources/storage-engines/tikv/src/server/status_server/jeprof.in

## Purpose

`jeprof.in` is a vendored Perl profiling report generator derived from gperftools `pprof` and packaged as jemalloc `jeprof`. In TiKV it is not invoked as a standalone installed binary; `profile.rs` embeds it with `include_bytes!("jeprof.in")`, writes it to a spawned `perl /dev/stdin` process, and uses it to turn a dumped heap profile plus the current TiKV executable into SVG output for `/debug/pprof/heap?jeprof=true`. The script can also operate as a full command-line profile tool for local profiles, remote pprof-compatible endpoints, raw symbolized profiles, text/callgrind/dot/svg/pdf/gif reports, listings, disassembly, collapsed stacks, and interactive exploration.

## Important APIs, Types, And Functions

- Global options and tool maps: `%obj_tool_map`, `@DOT`, `@GV`, `@EVINCE`, `@KCACHEGRIND`, `@PS2PDF`, `@URL_FETCHER`, endpoint constants for `/pprof/*`, `$address_length`, `@prefix_list`, and temporary-file globals define the script's runtime environment.
- `Init()` initializes defaults, parses CLI flags with `Getopt::Long`, validates mutually exclusive modes/granularities, determines whether the first argument is a remote profile or a symbolized profile, configures object tools, and initializes library prefix search paths.
- `Main()` is the top-level driver: fetch dynamic profiles if needed, parse one or more profile files, optionally subtract a base profile, collect symbols via local object tools or remote symbol pages, then dispatch to `FilterAndPrint()`.
- `FilterAndPrint()` performs the central analysis pipeline: total calculation, uninteresting-frame removal, focus/ignore filtering, call extraction, granularity reduction, flat/cumulative aggregation, and renderer dispatch.
- Renderers include `PrintText`, `PrintCallgrind`, `PrintDot`, `RewriteSvg`, `PrintListing`, `PrintSource`, `PrintDisassembly`, `PrintDisassembledFunction`, `PrintSymbolizedProfile`, `PrintCollapsedStacks`, and interactive wrappers in `InteractiveMode` / `InteractiveCommand`.
- Profile manipulation helpers include `FlatProfile`, `CumulativeProfile`, `RemoveUninterestingFrames`, `ReduceProfile`, `FocusProfile`, `IgnoreProfile`, `FilterFrames`, `ExtractCalls`, `AddProfile`, `SubtractProfile`, `AddEntries`, and `TotalProfile`.
- Dynamic profile support includes `ParseProfileURL`, `FetchDynamicProfile`, `FetchDynamicProfiles`, `FetchDynamicProfilesRecurse`, `TryCollectProfile`, `CheckSymbolPage`, `FetchProgramName`, and `FetchSymbols`.
- Parsing support includes the `CpuProfileStream` package for streaming binary CPU profiles, `ReadProfileHeader`, `ReadProfile`, `ReadCPUProfile`, `ReadHeapProfile`, `ReadThreadedHeapProfile`, `ReadSynchProfile`, `ReadSymbols`, and `IsSymbolizedProfileFile`.
- Symbolization and address support includes `ParseLibraries`, `FindLibrary`, `DebuggingLibrary`, `ParseTextSectionHeader*`, `ExtractSymbols`, `MapToSymbols`, `MapSymbolsWithNM`, `GetProcedureBoundaries`, `GetProcedureBoundariesViaNm`, `ShortFunctionName`, `AddressAdd`, `AddressSub`, `AddressInc`, and `HexExtend`.
- Safety/utility helpers include `ConfigureObjTools`, `ConfigureTool`, `ShellEscape`, `TempName`, `cleanup`, `sighandler`, and `error`.

## Control Flow

Startup begins in `Main()`, which calls `Init()` immediately. `Init()` creates `/tmp/jeprof$$` temporary-name roots, installs an interrupt handler, sets all `main::opt_*` flags, parses command-line options, chooses a default output mode based on whether stdout is a TTY, handles `--test`, and determines whether symbol lookup should come from local binaries, a remote `/pprof/symbol` page, or a symbolized profile file. For local binaries, it runs `ConfigureObjTools()` before any profile parsing so later symbol extraction can call `nm`, `addr2line`, `objdump`, `c++filt`, `otool`, or Windows PDB helpers.

`Main()` then calls `FetchDynamicProfiles()`. Local profile arguments are returned unchanged; remote arguments are fetched with curl into `$JEPROF_TMPDIR` or `$HOME/jeprof`. Multiple remote profiles are fetched through a fork tree. The selected profile files are parsed by `ReadProfile()`, merged with `AddProfile()` and `AddPcs()`, and optionally adjusted by `SubtractProfile()` for `--base`.

`ReadProfile()` first reads a textual or binary header. It recognizes symbolized profile sections, heap/growth profiles, threaded heap profiles, contention profiles, and binary CPU profiles. CPU profile parsing uses `CpuProfileStream` so large binary files are streamed in fixed-size windows rather than fully loaded. Heap readers parse stack entries and memory maps, adjust sampled allocations for older and v2 heap sampling algorithms, then map PCs to libraries. Contention parsing normalizes cycles to nanoseconds and handles sampling periods.

Symbol collection then branches by mode. Symbolized profiles call `FetchSymbols($pcs, $symbol_map)`. Remote profiles post PC addresses to `/pprof/symbol`. Local profiles call `ExtractSymbols()`, which maps each PC to a library range from `ParseLibraries()`, prefers debug symbol files when available, and calls `MapToSymbols()` with `addr2line`; `MapToSymbols()` falls back to `MapSymbolsWithNM()` when needed.

Finally `FilterAndPrint()` transforms and renders. It removes allocator/profiler-internal frames, applies focus and ignore regexes, reduces stack frames to the requested address/line/function/file granularity while avoiding recursion double-counting, computes flat and cumulative profiles, and dispatches to the selected renderer. Graph modes stream DOT into Graphviz or post-process generated SVG for browser pan/zoom. Interactive mode repeats a subset of those transformations per command.

## State And Persistence Behavior

The script is mostly process-local state in the `main::` namespace. Parsed options, temporary file paths, profile type, collected profile names, source-cache contents, address width, object-tool paths, and symbol disambiguation state are globals. The important persisted artifacts are:

- Temporary symbol/address files under `/tmp/jeprof$$.sym`.
- Temporary graph/listing files under `/tmp/jeprof$$.*`.
- Dynamically fetched profiles under `$JEPROF_TMPDIR` or `$HOME/jeprof`, intentionally left behind by `cleanup()` for later investigation.
- Renderer output on stdout or viewer-target temp files depending on selected mode.

`cleanup()` deletes only transient temp files and leaves fetched remote profiles. It runs on normal exit after `Main()`, on `SIGINT`, and inside `error()`. The script mutates no TiKV state directly, but when TiKV invokes it for heap SVG generation it consumes CPU, memory, temp files, the current executable, the heap profile file, and external tool processes.

## Dependencies

Runtime dependencies are Perl core modules `strict`, `warnings`, `Getopt::Long`, and `Cwd`; command-line tools include `perl`, `curl`, `nm`, `addr2line`, `objdump`, `c++filt`, optionally `dot`, `ps2pdf`, `gv`, `evince`, `kcachegrind`, `otool`, `eu-readelf`, `6nm`, and Windows PDB helpers. It assumes Unix-like process and file semantics, with limited Windows handling for `nul`, path separators, and PDB tools. For TiKV's embedded path, the critical dependencies are `perl`, object tools for the current executable, and Graphviz `dot` because `profile.rs` requests `--svg`.

## Integration Points

- `sources/storage-engines/tikv/src/server/status_server/profile.rs` uses `jeprof_heap_profile(path)` to spawn `perl`, pass this script on stdin, and run `/dev/stdin --show_bytes <current_exe> <heap_profile_path> --svg`.
- `sources/storage-engines/tikv/src/server/status_server/mod.rs` exposes heap profiling through `/debug/pprof/heap`; the query flag `jeprof=true` selects the SVG path that depends on this script.
- Remote pprof compatibility in the script expects `/pprof/profile`, `/pprof/heap`, `/pprof/symbol`, and `/pprof/cmdline`, while TiKV exposes analogous endpoints under `/debug/pprof/*`. The embedded TiKV use passes local files and does not rely on the script's remote fetch support.
- Symbolization depends on the same executable that produced the heap profile, so TiKV passes `std::env::current_exe()`.

## Risks And Edge Cases

- The embedded path blocks until the Perl process and Graphviz pipeline finish; large heap profiles or missing/slow symbol tools can make a status endpoint expensive.
- `ShellEscape()` uses a whitelist and single-quote escaping, but a few command strings are still composed manually for pipelines and redirections. Inputs are mostly local paths and tool names, but this script should not be treated as a hardened sandbox boundary.
- `jeprof_heap_profile()` unwraps when writing stdin in Rust; if the Perl child exits early, TiKV can panic in that path rather than returning a clean profiling error.
- The script relies on many external tools being available and compatible. Missing `addr2line` falls back to `nm`, but missing `dot` breaks SVG/graph output.
- Address arithmetic and parsing are hand-rolled for 32-bit and 64-bit profiles. Unit tests cover add/sub/inc, but parsing depends on profile format assumptions and Perl integer behavior.
- Dynamic remote profile fetching leaves collected profiles in `$HOME/jeprof`; this is intentional but can accumulate files outside TiKV's control if the script is used standalone.
- Heap sampling adjustment heuristics distinguish local heap-profiler output from remote heap pages; unusual profile headers can produce misleading adjusted counts.
- The script has broad legacy compatibility code. Changes that simplify one platform can silently break another profile format or output mode.

## Test Signals

- Built-in `--test` runs `RunUnitTests()`, covering `AddressAdd`, `AddressSub`, and `AddressInc` for 32-bit and 64-bit canonical hex values.
- TiKV status-server tests in adjacent Rust modules exercise `/debug/pprof/heap`, CPU pprof, and symbol endpoints; those tests are integration signals for the profile subsystem, though they may not always execute the `jeprof=true` SVG path.
- Useful manual checks are `perl jeprof.in --test`, an embedded heap SVG request with `jeprof=true`, and a failure-mode check with missing Graphviz/object tools to confirm error propagation through `profile.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/jeprof.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/lite.rs -->
# sources/storage-engines/tikv/src/server/status_server/lite.rs

## Purpose

`lite.rs` implements a stripped-down TiKV status server intended for short-lived or batch `tikv-ctl` tasks that need observability without a fully bootstrapped TiKV server. It exports metrics, CPU profiling, heap profiling, and async task tracing while intentionally omitting operational endpoints such as config reloads and region metadata dumps.

## Important APIs, Types, And Functions

- `type Svc = StatusServer<()>` aliases the full generic status server with an empty router so this file can call existing static handler methods.
- `Server` owns an `Arc<SecurityConfig>` and is the builder/launcher for the lite HTTP server.
- `Handle` stores the bound `SocketAddr`; `Handle::address()` exposes it to callers and tests.
- `Server::new(sec)` constructs the lite server from shared security configuration.
- `Server::start(status_addr)` parses and binds the requested address, selects TLS or plain Hyper accepting based on whether cert/key/CA paths are all configured, spawns the serving future, and returns the local address.
- `Server::start_serve()` is generic over Hyper acceptors and TiKV's `ServerConnection`, builds per-connection services, captures optional client certificates, and runs `LiteService`.
- `LiteService` is a copyable request dispatcher with `call(RequestCtx)`.
- `RequestCtx` bundles the Hyper request, optional peer `X509` certificate, and shared security config.

## Control Flow

Callers construct `Server::new(Arc<SecurityConfig>)` and call `start()`. `start()` parses `status_addr` into `SocketAddr`, binds `AddrIncoming`, stores `incoming.local_addr()` in the returned handle, and chooses between `tls_incoming(self.security_config.clone(), incoming)` and the raw incoming socket. It then delegates to `start_serve()` and returns immediately after spawning the Hyper server on the current Tokio runtime.

`start_serve()` creates a mutable `LiteService` and passes a service factory to Hyper. For each accepted connection it extracts `conn.get_x509()`, clones the security config, and returns a `service_fn` that clones those per request. Each request is wrapped into `RequestCtx` and passed to `svc.call()`. Server-level Hyper errors are logged with `warn!`.

`LiteService::call()` copies the request path and method, decides whether certificate authorization is required, optionally rejects the request with `403 FORBIDDEN`, and dispatches the accepted subset:

- `GET /metrics` -> `StatusServer::metrics_to_resp(req, true)`.
- `GET /debug/pprof/profile` -> `StatusServer::dump_cpu_prof_to_resp(req).await`.
- `GET /async_tasks` -> `StatusServer::dump_async_trace()`.
- `GET /debug/pprof/heap` -> `StatusServer::dump_heap_prof_to_resp(req)`.
- Anything else -> `404 NOT_FOUND`.

The certificate bypass list is intentionally smaller than the full status server: only `GET /metrics` and `GET /debug/pprof/profile` are unauthenticated when TLS security is configured.

## State And Persistence Behavior

The lite server does not own TiKV data state. It persists only the bound socket listener inside the spawned Hyper server and returns the address through `Handle`. The server task is detached with `tokio::spawn`; there is no explicit stop handle in this file. Request state is per-call and cloned from connection/request context. Profiling handlers can allocate buffers, spawn profiling work, or read heap profile files through the shared `StatusServer` static methods, but this module itself does not persist those artifacts.

## Dependencies

This module depends on Hyper for HTTP serving, Tokio for async runtime and spawning, OpenSSL `X509` for client certificates, `security::SecurityConfig` for TLS/authz configuration, and status-server helpers from the parent module: `StatusServer`, `make_response`, `tls_incoming`, `check_cert`, `make_service_fn`, and the `ServerConnection` trait. It also relies on full status-server profiling/metrics implementations and the Prometheus registry through `metrics_to_resp`.

## Integration Points

- Reuses full status-server handler methods instead of duplicating metrics/profiling logic.
- Shares TLS/client-certificate plumbing with the full status server through `tls_incoming`, `ServerConnection::get_x509`, and `check_cert`.
- Intended for `tikv-ctl` or similar short-term tasks where the full `StatusServer<R>` dependencies, router, config controller, and resource managers are unavailable.
- `GET /debug/pprof/heap` can transitively use `profile.rs` and `jeprof.in` when the request selects the jeprof heap SVG path.

## Risks And Edge Cases

- `Server::start()` panics if called outside a Tokio runtime because `start_serve()` uses `tokio::spawn`.
- The returned `Handle` has no shutdown channel, so lifecycle control is limited once spawned.
- TLS is enabled only when cert, key, and CA paths are all non-empty. Partial security configuration silently falls back to plaintext serving.
- `LiteService` bypasses certificate checks for CPU profile and metrics, matching the local policy in this file. CPU profiling can be expensive, so exposure should be considered when binding non-loopback addresses.
- Unlike the full status server, this lite dispatcher does not record `STATUS_REQUEST_DURATION`, so request latency metrics may be absent for lite-only status traffic.
- `let mut svc = LiteService` is captured by the service factory. `LiteService` is zero-sized and `Copy`, so this is safe, but future stateful additions to `LiteService` would need care around sharing and mutation.

## Test Signals

- `test_server_start_insecure` verifies binding on `127.0.0.1:0` and that the returned address is IPv4.
- `test_lite_service_call_metrics` registers a test Prometheus counter, calls `GET /metrics`, and asserts a successful response containing the series.
- `test_lite_service_call_profile` calls `GET /debug/pprof/profile?seconds=1` without a certificate and expects `200 OK` plus SVG content type.
- `test_lite_service_call_not_found` verifies unknown paths return `404 NOT_FOUND`.
- Missing direct tests include TLS startup, certificate-required routes such as heap and async task tracing, and lifecycle/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/lite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/metrics.rs -->
# sources/storage-engines/tikv/src/server/status_server/metrics.rs

## Purpose

`metrics.rs` defines the Prometheus metric used by TiKV's full status server to observe status HTTP request latency by method and normalized path. It is intentionally small and centralizes the metric registration for the status-server module.

## Important APIs, Types, And Functions

- `STATUS_REQUEST_DURATION: HistogramVec` is a `lazy_static!` global registered with Prometheus.
- The metric name is `tikv_status_server_request_duration_seconds`.
- The help string is `Bucketed histogram of TiKV status server request duration`.
- Labels are `method` and `path`.
- Buckets are generated by `exponential_buckets(0.0001, 2.0, 24).unwrap()`, covering roughly 0.1 ms through 1677.7 seconds.

## Control Flow

There is no runtime control flow in this file beyond lazy initialization. The first access to `STATUS_REQUEST_DURATION` registers the histogram vector in the default Prometheus registry. The full status server observes it after dispatching each HTTP request: it measures elapsed time, normalizes unknown paths to `"unknown"` to avoid unbounded path-cardinality, then calls `with_label_values(&[method.as_str(), &path_label]).observe(...)`.

## State And Persistence Behavior

The histogram is process-global Prometheus state. It accumulates bucket counts, sums, and sample counts for the process lifetime and is exported through the normal metrics endpoint. It is not persisted to disk. Registration uses `.unwrap()`, so duplicate registration or invalid bucket construction would panic at first initialization, but the static is intended to be registered once.

## Dependencies

The file depends on `prometheus::{HistogramVec, exponential_buckets, register_histogram_vec}` and `lazy_static`. Its consumers are in `status_server/mod.rs`, which imports `metrics::STATUS_REQUEST_DURATION`.

## Integration Points

- Full status-server request handling in `mod.rs` observes this histogram around route dispatch.
- `/metrics` output includes this metric alongside the rest of TiKV's Prometheus registry.
- The lite status server in `lite.rs` reuses metrics output but does not currently observe this histogram for its own request handling.

## Risks And Edge Cases

- Known-path labels include the raw route path. Dynamic routes must be normalized by the caller to avoid high-cardinality labels; the full server already maps unknown paths to `"unknown"`, but any new dynamic matched routes should follow the same discipline.
- Bucket range is broad, which is useful for slow profiling/debug endpoints but gives relatively coarse resolution at high latencies.
- `.unwrap()` on registration is conventional in TiKV metrics code but still means duplicate metric names fail at runtime initialization.

## Test Signals

- There is no unit test in this file.
- Indirect signals come from full status-server tests that call endpoints and `/metrics`, plus any Prometheus registry tests that would fail on duplicate metric names.
- A focused test could make a known and unknown status request, scrape `/metrics`, and assert that `tikv_status_server_request_duration_seconds_bucket` appears with expected `method` and normalized `path` labels.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/status_server/metrics.rs -->
