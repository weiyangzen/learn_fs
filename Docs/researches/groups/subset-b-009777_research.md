# subset-b-009777 Research

Grouped research for the rclone RC, WebGUI, registry, size suffix, and sync files in `sources/user-network-fs/rclone`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/main.go -->
# sources/user-network-fs/rclone/fs/rc/js/main.go

## Purpose
This Go source is the browser/WebAssembly entry point for exposing selected rclone remote-control functionality to JavaScript. It is built only for the `js` target and imports the RC registry plus a small set of rclone capabilities: operations, sync, and the memory backend.

## Important APIs, Types, and Functions
- `main` validates the browser environment, captures `document` and `JSON`, installs `globalThis.rc` as a `js.FuncOf(rcCallback)`, resolves `rcValidResolve`, and then blocks forever.
- `rcCallback(this js.Value, args []js.Value) interface{}` is the exported JavaScript call bridge. It expects exactly two arguments: method name and null/object input.
- `errorValue(method string, in js.Value, err error) js.Value` maps Go errors into a JS object with `status`, `error`, `input`, and `path`, using RC/FS error classification.
- `getElementById`, `time`, and `paramToValue` are local helpers; `paramToValue` is currently a stub returning an empty `js.Value`.

## Control Flow
Startup checks `js.Global`, `document`, and `JSON`; failures are fatal because the module is browser-oriented. Calls enter through `rcCallback`, stringify JS object input with `JSON.stringify`, unmarshal into `rc.Params`, look up `rc.Calls.Get(method)`, invoke the registered Go RC function synchronously with `context.Background`, then reshape the returned `rc.Params` into `map[string]interface{}` for `js.ValueOf`.

## State and Persistence
The file keeps browser globals in package variables `document` and `jsJSON`. It does not persist data directly; invoked RC functions may mutate state, files, or remotes depending on what has been registered. The installed `globalThis.rc` function remains live for the lifetime of the WASM process.

## Dependencies and Integration Points
It depends on `syscall/js`, `encoding/json`, `fs/rc`, and implicitly on imported packages that register RC calls in `init`. The build imports only the memory backend, so browser use is constrained unless more backends are uncommented or added. It integrates with `wasm_exec.js` and host JavaScript through `rcValidResolve`.

## Risks and Edge Cases
The RC call is synchronous and uses `context.Background`, so cancellation, deadlines, and request-scoped auth are absent. Input objects must survive JSON stringification; functions, cyclic structures, and unsupported JS values fail or lose information. `call.NoAuth` and HTTP auth checks are not enforced here, so the browser embedding must treat the exposed `rc` function as privileged.

## Test Signals
No dedicated tests are present for this file in the subset. Behavior is indirectly coupled to RC registry and parameter tests, but browser/WASM integration needs manual or browser-driven validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/serve.go -->
# sources/user-network-fs/rclone/fs/rc/js/serve.go

## Purpose
This is a development-only helper server for serving the WASM demo/current directory over HTTP. The `//go:build none` tag prevents it from participating in normal builds.

## Important APIs, Types, and Functions
- `main` registers MIME types for `.wasm` and `.js`, serves the current directory with `http.FileServer(http.Dir("."))`, and listens on `:3000`.

## Control Flow
The helper process creates a default mux, attaches static file serving at `/`, prints the local URL, and blocks in `http.ListenAndServe`.

## State and Persistence
No persistent state is managed. It exposes files from the current working directory at runtime.

## Dependencies and Integration Points
It uses only Go standard-library packages: `fmt`, `log`, `mime`, and `net/http`. It pairs with `main.go` and `wasm_exec.js` during local browser testing.

## Risks and Edge Cases
Serving `.` can expose any local files in the working directory. The fixed port `3000` may conflict with other services. It lacks auth, TLS, directory restrictions beyond the process CWD, and production hardening, which is acceptable for a build-excluded development utility.

## Test Signals
No automated tests are present. The build tag itself is the primary safety signal that this does not enter normal binaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/wasm_exec.js -->
# sources/user-network-fs/rclone/fs/rc/js/wasm_exec.js

## Purpose
This is the Go WebAssembly JavaScript support runtime, adapted from the Go project. It defines `globalThis.Go`, polyfills minimum Node/browser-like `fs` and `process` behavior when absent, and implements the import functions required by Go's `runtime` and `syscall/js` packages.

## Important APIs, Types, and Functions
- `globalThis.Go` class encapsulates argv/env setup, WebAssembly import object construction, JS value reference tables, timeout scheduling, and program execution.
- `run(instance)` validates the `WebAssembly.Instance`, initializes memory/value tables, writes argv/env strings into linear memory, calls the Go `run` export, and waits for program exit.
- `_resume` and `_makeFuncWrapper` support Go callbacks invoked from JavaScript.
- Import handlers cover runtime time functions, random data, writes, JS property access, calls, construction, `instanceof`, and byte copies between Go and JS.

## Control Flow
The IIFE first installs minimal `fs` and `process` shims if needed, then validates required browser primitives (`crypto`, `performance`, `TextEncoder`, `TextDecoder`). The constructor builds `importObject.go` with many functions that interpret the Go stack pointer and read/write WASM memory. Runtime events use `_scheduledTimeouts` and `_pendingEvent` to resume Go from JS callbacks.

## State and Persistence
State is entirely in-memory: `_values`, `_goRefCounts`, `_ids`, `_idPool`, timeout maps, instance references, and the buffered stdout line accumulator. There is no filesystem persistence beyond writes delegated to an existing or shimmed `fs`.

## Dependencies and Integration Points
The file is required by Go-compiled WASM modules using `syscall/js`. `main.go` depends on this runtime to expose JavaScript globals and function callbacks. Host pages must instantiate WASM with `go.importObject` and call `go.run(instance)`.

## Risks and Edge Cases
The fallback `fs` implementation only supports writes and returns ENOSYS for most operations, so Go code doing real filesystem calls will fail. Reference counting bugs or failing to finalize Go refs can leak JS values. The runtime assumes layout contracts with the Go compiler/linker; version mismatch with a differently generated `.wasm` can break imports. Host environments must provide secure `crypto.getRandomValues`.

## Test Signals
There are no repository-local tests for this vendored/runtime file. Compatibility should be validated by running the browser WASM build under the same Go toolchain version that provided this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/wasm_exec.js -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/params.go -->
# sources/user-network-fs/rclone/fs/rc/params.go

## Purpose
This file defines `rc.Params`, the common input/output map used by rclone remote-control calls, plus typed getters and standard error response construction.

## Important APIs, Types, and Functions
- `type Params map[string]any` is the canonical RC payload shape.
- `ErrParamNotFound` and `ErrParamInvalid` distinguish missing parameters from malformed parameters; these are later translated to HTTP 400.
- `Reshape(out, in any) error` converts arbitrary structured values through JSON marshal/unmarshal.
- Getter methods include `Get`, `GetString`, `GetInt64`, `GetFloat64`, `GetBool`, `GetStruct`, `GetStructMissingOK`, `GetDuration`, `GetFsDuration`, `GetHTTPRequest`, and `GetHTTPResponseWriter`.
- `Error(path, in, err, status)` creates the standard RC JSON error body and adjusts status for not-found and parameter errors.

## Control Flow
Most getters call `Get`, type-switch the result, and return either a typed value or `ErrParamInvalid`. Numeric and boolean getters accept strings and selected numeric types. `GetStruct` first uses `Reshape`; if the raw value is a string and reshape fails, it tries to unmarshal the string as JSON. `Error` prioritizes filesystem not-found errors and RC parameter errors over the supplied status code.

## State and Persistence
The code is stateless except for shallow copying a `Params` map with `Copy`. `GetHTTPRequest` and `GetHTTPResponseWriter` rely on server-injected reserved keys `_request` and `_response`.

## Dependencies and Integration Points
It is used by RC functions, the HTTP server, WebGUI plugin RC methods, sync RC methods, and the WASM bridge. It depends on `encoding/json`, `net/http`, `strconv`, `time`, and `fs.ParseDuration`.

## Risks and Edge Cases
`Params.Copy` is shallow, so nested maps/slices remain shared. `GetInt64` converts `float64` by truncation after only range checking, which matches JSON number handling but may surprise callers expecting integral validation. `Reshape` is convenient but can be expensive and may silently apply JSON type coercions. Reserved keys can carry raw HTTP interfaces into RC handlers and must not be serialized back accidentally in error input; the server copies the original input before injecting them.

## Test Signals
`params_test.go` covers missing/invalid errors, reshape failures, shallow copy behavior, string/int/float/bool/duration parsing, struct extraction including JSON strings, optional struct reads, and reserved HTTP request/response retrieval.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/params_test.go -->
# sources/user-network-fs/rclone/fs/rc/params_test.go

## Purpose
This file verifies the typed RC parameter helpers and error classifiers defined in `params.go`.

## Important APIs, Types, and Functions
- Tests cover `ErrParamNotFound.Error`, `IsErrParamNotFound`, `NotErrParamNotFound`, `IsErrParamInvalid`, `Reshape`, `Params.Copy`, all core getters, and reserved HTTP request/response getters.
- Table-driven tests exercise accepted and rejected inputs for numeric, boolean, and duration parsing.

## Control Flow
Each test constructs small `Params` maps, calls the relevant helper, and asserts both value and error type/message. Duration tests rely on rclone `fs.ParseDuration` semantics, including `off`, years, days, months, and negative durations.

## State and Persistence
The tests are stateless except for local `httptest.NewRecorder` values used to validate `http.ResponseWriter` extraction.

## Dependencies and Integration Points
The tests use `testify/assert` and `testify/require`, the standard `net/http` test helpers, and `fs.Duration` parsing behavior. They document the contract consumed by RC server handlers and RC method implementations.

## Risks and Edge Cases
The tests intentionally allow float-to-int64 truncation and broad bool conversions, so future stricter behavior would need test changes. They verify error classification but do not exercise HTTP serialization directly; that appears in `rcserver` tests.

## Test Signals
Coverage is strong for parameter coercion and error typing. The main gaps are nested `Params.Copy` aliasing behavior and pathological JSON reshape cases beyond basic marshal/unmarshal failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/params_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rc.go -->
# sources/user-network-fs/rclone/fs/rc/rc.go

## Purpose
This file declares the remote-control global option schema, the runtime `Options` struct, and JSON response writer helper for the RC subsystem.

## Important APIs, Types, and Functions
- `OptionsInfo` is an `fs.Options` block containing RC, WebGUI, metrics, job expiry, auth, HTTP, and template options.
- `type Options` stores RC server, auth, WebGUI, metrics, and job expiration settings with `config` tags.
- `var Opt Options` holds global defaults loaded by the fs global option registry.
- `WriteJSON(w io.Writer, out Params) error` writes indented JSON responses.

## Control Flow
At init time, `fs.RegisterGlobalOptions` registers the `rc` option block and points it at `Opt`. `OptionsInfo` composes RC-specific options with prefixed HTTP/auth/template option groups, then sets defaults such as `localhost:5572` for RC and an empty metrics listener.

## State and Persistence
`Opt` is process-global mutable configuration populated through rclone's option machinery. This file itself does not persist to disk; persistence comes from config/env/flags handled by the broader fs config system.

## Dependencies and Integration Points
The file depends on `fs.Options`, `fs.Duration`, and `lib/http` configuration blocks. `rcserver.Start`, `MetricsStart`, `webgui`, and `jobs` consume `Options` at runtime.

## Risks and Edge Cases
Because `Opt` is global, tests and initialization code that mutate it can affect later behavior unless isolated. `WriteJSON` uses tab-indented JSON, which tests assert and clients may observe.

## Test Signals
`rc_test.go` directly verifies `WriteJSON` formatting. Option registration is exercised indirectly across server, flags, and integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rc_test.go -->
# sources/user-network-fs/rclone/fs/rc/rc_test.go

## Purpose
This file validates the RC JSON response writer.

## Important APIs, Types, and Functions
- `TestWriteJSON` writes a small `Params` map to a buffer and asserts the exact tab-indented JSON output.

## Control Flow
The test calls `WriteJSON`, requires no error, and compares the resulting buffer to a golden string.

## State and Persistence
No persistent state is touched.

## Dependencies and Integration Points
It depends on `bytes.Buffer` and `testify`. It protects HTTP API response formatting used by `rcserver.writeError` and successful RC POST responses.

## Risks and Edge Cases
The exact string assertion makes formatting changes deliberate but may be brittle if Go's JSON map ordering behavior or encoder formatting changes. It does not cover write failures.

## Test Signals
The test is narrow but useful: it documents that RC responses are pretty-printed with tabs and include a trailing newline.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcflags/rcflags.go -->
# sources/user-network-fs/rclone/fs/rc/rcflags/rcflags.go

## Purpose
This small package wires RC options into a `pflag.FlagSet` for command-line use.

## Important APIs, Types, and Functions
- `const FlagPrefix = "rc-"` names the flag namespace.
- `AddFlags(flagSet *pflag.FlagSet)` delegates to `flags.AddFlagsFromOptions` using `rc.OptionsInfo`.

## Control Flow
Callers provide a flag set; the helper adds every RC option described in `rc.OptionsInfo`, relying on the fs/config flag system for type conversion and option metadata.

## State and Persistence
No state is held in this file. Added flags later populate RC global options through the larger configuration pipeline.

## Dependencies and Integration Points
It depends on `fs/config/flags`, `fs/rc`, and `spf13/pflag`. It is an integration adapter between RC option metadata and the CLI.

## Risks and Edge Cases
The exported `FlagPrefix` is not used in `AddFlags`; the actual prefixing comes from option names already present in `OptionsInfo`. If RC option metadata changes, this helper inherits it automatically.

## Test Signals
No dedicated tests are in this subset. CLI flag behavior is indirectly covered where global option registration and flag parsing are tested elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcflags/rcflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/metrics.go -->
# sources/user-network-fs/rclone/fs/rc/rcserver/metrics.go

## Purpose
This file implements the standalone Prometheus metrics HTTP server for rclone RC.

## Important APIs, Types, and Functions
- `MetricsStart(ctx, opt)` starts a metrics server only when `opt.MetricsHTTP.ListenAddr` is non-empty.
- `MetricsServer` wraps context, `libhttp.Server`, Prometheus handler, and RC options.
- `newMetricsServer` creates the HTTP server with metrics-specific config/auth/template options and registers `GET /metrics`.
- `Serve`, `Wait`, and `Shutdown` mirror the RC server lifecycle.

## Control Flow
Package init registers an accounting collector and fs HTTP metrics collectors with the default Prometheus registry, assigns `fshttp.DefaultMetrics`, and stores the default promhttp handler. `MetricsStart` updates job options, builds the server, and starts background serving.

## State and Persistence
Prometheus collectors are registered globally at init time. Runtime metrics are held in process memory via accounting and fshttp metrics. No filesystem persistence is used.

## Dependencies and Integration Points
It integrates `prometheus/client_golang`, `fs/accounting`, `fs/fshttp`, `rc.Options`, `jobs`, and `lib/http`. Metrics can also be served by the main RC server when `--rc-enable-metrics` is enabled; this file handles the separate metrics listener.

## Risks and Edge Cases
Global collector registration can panic if duplicate collectors are registered in the same process through unusual test/plugin loading. Metrics exposure depends on the configured metrics auth; an empty listener disables this server completely.

## Test Signals
`metrics_test.go` starts a metrics server on `localhost:0`, fetches `/metrics`, and asserts key rclone metric lines reflect `accounting.GlobalStats`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/metrics_test.go -->
# sources/user-network-fs/rclone/fs/rc/rcserver/metrics_test.go

## Purpose
This file tests the Prometheus metrics endpoint exposed by the RC metrics server.

## Important APIs, Types, and Functions
- `testMetricsServer` creates a metrics server and reuses `emulateCalls` from RC server tests.
- `newMetricsTestOpt` enables metrics listening on the test bind address.
- `TestMetrics` asserts baseline metrics, mutates global accounting stats, and asserts changed metrics.
- `makeMetricsTestCases` builds regex expectations for byte, check, error, delete, and transfer counters.

## Control Flow
The test installs a config file environment, constructs the server without binding a real external port, calls the chi router with synthetic HTTP requests, and checks status/body regexes.

## State and Persistence
It mutates `accounting.GlobalStats`, so it relies on test isolation and may be sensitive to other tests changing global stats in the same process. No disk persistence is intentional beyond config setup.

## Dependencies and Integration Points
It imports the local backend for filesystem availability, `configfile.Install`, `accounting`, `rc.Options`, and the `testRun` harness from `rcserver_test.go`.

## Risks and Edge Cases
Because metrics are global, test ordering or parallel execution with other accounting tests could change expected values. The tests assert selected metric lines rather than full Prometheus output.

## Test Signals
The file provides direct evidence that the metrics route returns HTTP 200 and exposes current accounting counters in Prometheus text format.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/rcserver.go -->
# sources/user-network-fs/rclone/fs/rc/rcserver/rcserver.go

## Purpose
This file implements the main HTTP remote-control server, including RC POST dispatch, local/WebGUI file serving, remote file serving, metrics routing, pprof routing, auth gating, and server lifecycle.

## Important APIs, Types, and Functions
- `Start(ctx, opt)` starts the RC server only when enabled.
- `Server` holds context, `libhttp.Server`, static file/plugin handlers, options, and a startup snapshot of `NoAuth`.
- `newServer` prepares MIME types, WebGUI/static handlers, default WebGUI credentials, `libhttp.Server`, middleware, pprof, and route handlers.
- `handler`, `handlePost`, `handleGet`, and `handleOptions` implement request dispatch.
- `checkServeRemote` enforces security rules before instantiating remotes from request paths.
- `serveRemote` and `serveRoot` implement remote object/directory browsing.
- `Serve`, `URLs`, `Wait`, and `Shutdown` manage lifecycle.

## Control Flow
POST requests parse URL/form/JSON input into `rc.Params`, honor `Prefer: respond-async` by setting `_async`, look up `rc.Calls`, enforce auth unless the call is `NoAuth` or `--rc-no-auth` was set at startup, inject `_request`/`_response` for calls that need them, then execute via `jobs.NewJob` and write JSON. GET/HEAD requests route to remote serving for `/[fs]/path`, `/metrics` when enabled, remote listing, WebGUI plugins, static files, or 404.

## State and Persistence
The server keeps static handler references and a `noAuth` snapshot to prevent runtime option mutation from changing auth semantics. WebGUI mode may download/extract files under the cache directory and mutate auth defaults with generated credentials. Remote serving uses `cache.Get` and may create backend instances.

## Dependencies and Integration Points
It integrates chi middleware through `libhttp.Server`, rclone config/cache/fspath/list/serve packages, RC registry/jobs, WebGUI helpers, pprof on the default mux, and browser opening via `open-golang/open`.

## Risks and Edge Cases
`checkServeRemote` is a key security boundary: unauthenticated servers may serve only configured named remotes, while inline remotes, bare local paths, and connection-string overrides are rejected; `global.*` is rejected even for authenticated requests. POST parsing merges query/form/JSON values with last value wins for repeated query values and JSON overwriting/augmenting the map. RC calls that receive `_response` can write directly, so response ownership must be handled carefully. Browser auto-open embeds basic credentials and a login token in a URL, which should be treated as sensitive.

## Test Signals
`rcserver_test.go` covers static files, range/head requests, remote serving, security rejection for unauthenticated inline/local/global remotes, authenticated serving, RC input parsing, auth/no-auth behavior, async jobs, pprof, directory modtime display, and JSON content type. Metrics route behavior is also covered in `metrics_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/rcserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/rcserver_test.go -->
# sources/user-network-fs/rclone/fs/rc/rcserver/rcserver_test.go

## Purpose
This large test file validates the HTTP behavior, auth behavior, file/remote serving, RC POST dispatch, async handling, pprof exposure, and security restrictions of the RC server.

## Important APIs, Types, and Functions
- `testRun` describes synthetic HTTP cases.
- `testServer` and `emulateCalls` create a server/router and execute table-driven requests.
- `newTestOpt` builds enabled RC options on `localhost:0`.
- Focused tests include `TestFileServing`, `TestRemoteServing`, `TestCheckServeRemote`, `TestServeRemoteUnauthenticated`, `TestServeRemoteWithAuth`, `TestServeRemoteMarksRCRequest`, `TestRC`, `TestRCWithAuth`, `TestRCAsync`, `TestRCDebug`, `TestServeModTime`, and `TestContentTypeJSON`.

## Control Flow
Tests synthesize requests directly against the chi router or start a real listener for the basic liveness check. Assertions compare exact bodies or regex matches and selected headers. `TestMain` fakes `rclone version` and an unknown command for `core/command` RC tests.

## State and Persistence
Tests install temporary config state, mutate filesystem modtimes in `testdata/files/modtime`, and add cache entries indirectly through local backend use. They rely on static test fixtures under `testdata`.

## Dependencies and Integration Points
The test imports the local backend, `configfile`, `fs`, RC registry, `httptest`, and the server's router. It verifies integration with `core/command`, jobs, pprof, static serving, remote listing, and auth middleware.

## Risks and Edge Cases
The exact response-body assertions are valuable but can be brittle across template or JSON formatting changes. The security tests are especially important because remote serving can instantiate backends from URL-derived strings.

## Test Signals
Coverage is strong for HTTP status/body/header behavior, content-type parsing, JSON charset validation, form parsing failures, async `Prefer` behavior, auth enforcement, no-auth overrides, and the RC-request marker that prevents `global.*` config mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/rcserver/rcserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/registry.go -->
# sources/user-network-fs/rclone/fs/rc/registry.go

## Purpose
This file defines the registry for remote-control calls and the metadata used to expose them.

## Important APIs, Types, and Functions
- `type Func func(ctx context.Context, in Params) (out Params, err error)` is the RC handler signature.
- `type Call` stores path, function, title, auth metadata, help text, and whether the handler needs raw request/response interfaces.
- `Registry` stores path-to-call mappings under an RW mutex.
- `NewRegistry`, `(*Registry).Add`, `Get`, and `List` manage entries.
- `var Calls` is the global registry; `Add` is its package-level registration helper.

## Control Flow
Packages register calls in `init` via `rc.Add`. `Add` trims path slashes and help whitespace before storing the call. `List` snapshots keys, sorts them alphabetically, and returns calls in stable order.

## State and Persistence
The global `Calls` registry is process-wide mutable state. There is no disk persistence. Registered functions are stored as function pointers and omitted from JSON through the struct tag.

## Dependencies and Integration Points
The registry is used by `rcserver.handlePost`, `rc/js/main.go`, sync RC registration, WebGUI plugin registration, and other rclone packages that expose RC endpoints.

## Risks and Edge Cases
Duplicate paths overwrite previous calls without warning. Path normalization only trims leading/trailing slashes; internal path conventions are caller-owned. Global registration order can affect duplicate conflicts, though `List` output is deterministic.

## Test Signals
No dedicated tests in this subset target the registry directly, but server, sync RC, WebGUI RC, and WASM behavior all depend on `rc.Calls.Get`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/plugins.go -->
# sources/user-network-fs/rclone/fs/rc/webgui/plugins.go

## Purpose
This file implements WebGUI plugin metadata storage, plugin filtering, GitHub URL parsing, and plugin serving/proxy helpers.

## Important APIs, Types, and Functions
- `PackageJSON` and `RcloneConfig` model plugin `package.json` metadata and rclone-specific fields.
- `Plugins` stores loaded plugin metadata plus a mutex and config filename.
- `initPluginsOrError` initializes cache paths and loads `availablePlugins.json` when WebUI is enabled.
- `readFromFile`, `writeToFile`, `addPlugin`, `removePlugin`, and `GetPluginByName` persist and query plugin state.
- `getAuthorRepoBranchGitHub` parses supported GitHub repository URLs.
- `filterPlugins` selects plugin subsets.
- `ServePluginOK` reverse-proxies test plugins.
- `ServePluginWithReferrerOK` redirects absolute asset requests back under a plugin path when configured.

## Control Flow
Initialization is guarded by `initMutex` and `initSuccess`. Plugin metadata is read from or created under `PluginsPath/config/availablePlugins.json`. Test-plugin serving matches `/plugins/{author}/{name}/...`, looks up plugin metadata, and proxies to `TestURL` when `Rclone.Test` is true. Referrer-based serving inspects `Referer`, finds the plugin that emitted the request, and redirects when `RedirectReferrer` is set.

## State and Persistence
Plugin metadata persists as JSON under the WebGUI cache plugin config directory. Package globals hold paths, the loaded plugin set, a reverse proxy, regexes, and init flags. Writes use file mode `0755` even for JSON metadata.

## Dependencies and Integration Points
It depends on `config.GetCacheDir`, `fs` logging, `rc.Opt.WebUI`, and `net/http/httputil`. `rcserver.handleGet` uses `PluginsMatch`, `PluginsPath`, `ServePluginOK`, and `ServePluginWithReferrerOK`.

## Risks and Edge Cases
The global `pluginsProxy.Director` is mutated per request, which could race under concurrent test-plugin proxy requests. GitHub URL parsing is narrow and defaults to `master`. Persisted plugin config is process-global and can be affected by tests or multiple RC servers. Referrer parsing assumes a host:port-style URL and may miss valid referrers.

## Test Signals
`webgui/rc_test.go` indirectly exercises plugin metadata loading, add/list/remove/filter RC paths, but it relies on live network downloads for `TestAddPlugin` unless skipped on bad HTTP status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/plugins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/rc.go -->
# sources/user-network-fs/rclone/fs/rc/webgui/rc.go

## Purpose
This file registers RC endpoints for managing WebGUI plugins.

## Important APIs, Types, and Functions
- Registered paths: `pluginsctl/listTestPlugins`, `pluginsctl/removeTestPlugin`, `pluginsctl/addPlugin`, `pluginsctl/listPlugins`, `pluginsctl/removePlugin`, and `pluginsctl/getPluginsForType`.
- Handler functions include `rcListTestPlugins`, `rcRemoveTestPlugin`, `rcAddPlugin`, `rcGetPlugins`, `rcRemovePlugin`, and `rcGetPluginsForType`.

## Control Flow
Each `init` block registers one call in the global RC registry. Handlers first call `initPluginsOrError`. `rcAddPlugin` parses the repository URL, chooses branch/version defaults, creates plugin directories, downloads `package.json`, resolves the GitHub release asset, downloads and unzips it under `plugins/{author}/{repo}/app`, and records metadata. Listing/filtering handlers reload or filter `loadedPlugins`.

## State and Persistence
The handlers mutate the WebGUI plugin directory tree and `availablePlugins.json`. `rcAddPlugin` removes any previous extract path before unzipping. Output is usually `nil` for mutating operations and maps for listing operations.

## Dependencies and Integration Points
It depends on `rc.Params` typed getters, the plugin helpers in `plugins.go`, and release/download/unzip helpers in `webgui.go`. The endpoints become available to HTTP RC, WASM RC if imported, and CLI `rclone rc`.

## Risks and Edge Cases
Plugin installation performs unauthenticated network downloads from GitHub URLs and extracts archives into the cache, so integrity and zip path safety depend on `GetLatestReleaseURL`, `DownloadFile`, and `Unzip`. Optional `branch` and `version` ignore missing-parameter errors and use defaults. Remove operations fail if the plugin is not loaded but do not remove extracted files from disk.

## Test Signals
`webgui/rc_test.go` verifies registration and behavior for add/list/remove/filter, though add/remove depends on network availability and may skip only selected HTTP failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/rc_test.go -->
# sources/user-network-fs/rclone/fs/rc/webgui/rc_test.go

## Purpose
This file tests the WebGUI plugin RC endpoints and plugin metadata operations.

## Important APIs, Types, and Functions
- `setCacheDir` points plugin paths at a temporary directory and initializes `loadedPlugins`.
- `addPlugin` invokes `pluginsctl/addPlugin` with a test GitHub URL and skips on selected bad HTTP status failures.
- `removePlugin` verifies removal of a missing plugin produces an error.
- Tests cover add, list, remove, and filtering by type/plugin type.

## Control Flow
An `init` function sets `rc.Opt.WebUI = true` so plugin initialization succeeds. Tests fetch handlers from `rc.Calls`, call them directly with `context.Background`, and inspect `loadedPlugins` or returned `rc.Params`.

## State and Persistence
Tests write plugin config and downloaded/unzipped plugin content under temporary cache directories. The global `rc.Opt.WebUI`, `PluginsPath`, `pluginsConfigPath`, and `loadedPlugins` are mutated.

## Dependencies and Integration Points
The tests exercise the global RC registry, WebGUI plugin helpers, filesystem cache paths, and live GitHub release/package downloads for adding the test plugin.

## Risks and Edge Cases
Network-dependent tests can be flaky and only skip a subset of download failures. Global state mutation can leak if tests are reordered or run with other WebGUI tests. Commented-out tests indicate test-plugin removal/listing coverage is currently disabled.

## Test Signals
The file confirms handlers are registered and basic plugin lifecycle paths work in the happy path. It has weaker coverage for proxy/referrer serving, failed unzip/download cleanup, and file removal on plugin deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/webgui.go -->
# sources/user-network-fs/rclone/fs/rc/webgui/webgui.go

## Purpose
This file provides WebGUI release download, update, unzip, path creation, and GitHub release JSON helpers.

## Important APIs, Types, and Functions
- `GetLatestReleaseURL(fetchURL)` fetches GitHub release metadata and returns first asset download URL, tag, and size.
- `CheckAndDownloadWebGUIRelease(checkUpdate, forceUpdate, fetchURL, cacheDir)` manages cached WebGUI installation and updates.
- `DownloadFile(filepath, url)` streams an HTTP 200 response to a local file.
- `Unzip(src, dest)` extracts a zip archive while checking for Zip Slip paths.
- `exists` and `CreatePathIfNotExist` are filesystem helpers.
- `gitHubRequest` models the GitHub releases API payload fields used here.

## Control Flow
Update flow computes `cacheDir/webgui`, `tag`, and `current` paths, validates directories, fetches latest release metadata, compares the cached tag file, and downloads/extracts when missing, update requested, or forced. Zip files are removed after extraction and the tag file is written.

## State and Persistence
The WebGUI cache persists under `cacheDir/webgui`, including `current`, release tag file, and temporary release zip. Downloads and extraction mutate local filesystem state.

## Dependencies and Integration Points
It depends on standard `archive/zip`, `net/http`, and filesystem packages plus rclone `fs` logging and `lib/file`. `rcserver.newServer` calls `CheckAndDownloadWebGUIRelease` when `--rc-web-gui` is enabled; plugin install code reuses `DownloadFile`, `Unzip`, and `CreatePathIfNotExist`.

## Risks and Edge Cases
`GetLatestReleaseURL` blindly selects the first asset, so release asset ordering matters. There is no hash/signature verification despite a TODO. `DownloadFile` overwrites/creates the target path directly. `Unzip` protects against paths outside `dest`, but archive size and file count are not bounded here. Update checks require live network access even when an existing install is present.

## Test Signals
No direct tests for this file are listed in the subset. WebGUI plugin RC tests exercise `DownloadFile` and `Unzip` indirectly through plugin installation; RC server WebGUI paths are not deeply tested here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/webgui/webgui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/registry.go -->
# sources/user-network-fs/rclone/fs/registry.go

## Purpose
This file implements rclone's filesystem backend registry and option metadata system used by backends, global options, config, flags, environment variables, and RC option reporting.

## Important APIs, Types, and Functions
- `RegInfo` describes a backend: name, description, prefix, constructors, config callback, options, aliases, command help, visibility, and metadata.
- `Options` is a slice of `Option` with helpers `Add`, `AddPrefix`, `setValues`, `Get`, `SetDefault`, `Overridden`, `NonDefault`, `NonDefaultRC`, and `HasAdvanced`.
- `Option` describes a config/flag/API option and implements pflag-style methods: `String`, `Set`, `Type`.
- `OptionExample` and `OptionExamples` model selectable examples.
- `Register`, `Find`, and `MustFind` manage backend registration and lookup.
- `OptionsInfo`, `OptionsRegistry`, `RegisterGlobalOptions`, `GlobalOptionsInit`, and `OptionsInfo.Check/load` manage global option blocks.
- `Type`, `addReverse`, and `FindFromFs` support reverse lookup from an `fs.Fs` instance to its registration.

## Control Flow
Backends call `Register` from init functions. Registration fills default option values, sets a default prefix, appends the common `description` option, and creates hidden alias registrations. Global option registration validates option metadata against struct `config` tags, loads defaults/env values immediately, and can call reload hooks. `GlobalOptionsInit` reloads all option blocks in deterministic order with `main` first.

## State and Persistence
`Registry`, `OptionsRegistry`, and `typeToRegInfo` are process-global mutable registries. The file itself does not write config files, but it reads through configmap/configstruct layers and environment/config getters elsewhere.

## Dependencies and Integration Points
It depends on `configmap`, `configstruct`, `errcount`, reflection, sorting, and string normalization. It is foundational for all backend packages, RC option declaration, command-line flags, environment variable mapping, and config UI/API output.

## Risks and Edge Cases
`Registry` is not protected by a mutex, assuming init-time registration. `Register` mutates `RegInfo.Options` by appending `description`, so callers should not assume their original slice remains unchanged. `Option.Set` for string arrays relies on reflect pointer behavior and assumes defaults are slice-like. `OptionsInfo.Check` logs type mismatches without adding them to the returned errcount, so some metadata issues may be non-fatal.

## Test Signals
`registry_test.go` covers option string/type/set behavior, defaults, overridden/non-default detection, JSON marshaling, flag/env names, environment/config getter priority, and `NonDefaultRC` success/error cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/registry_test.go -->
# sources/user-network-fs/rclone/fs/registry_test.go

## Purpose
This file tests filesystem option metadata and configuration getter behavior.

## Important APIs, Types, and Functions
- Tests cover `Option` as a `pflag.Value`, `Options.setValues`, `Get`, `Overridden`, `NonDefault`, JSON marshaling, `GetValue`, `String`, `Set`, `Type`, `FlagName`, `EnvVarName`, config/environment getters, and `Options.NonDefaultRC`.
- Shared fixtures define `nouncOption`, `copyLinksOption`, `caseInsensitiveOption`, and `testOptions`.

## Control Flow
Tests construct options and config maps, set/unset environment variables, monkey-patch `ConfigFileGet`, and assert getter priority and returned values. `NonDefaultRC` tests use small tagged structs to verify field-name output and missing-key errors.

## State and Persistence
The test temporarily mutates process environment variables and the package-level `ConfigFileGet` function, restoring them with defers. It does not persist files.

## Dependencies and Integration Points
It uses `configmap`, `pflag`, `testify`, and option parsing through `configstruct.StringToInterface`. It protects behavior consumed by CLI flags, env/config loading, RC option output, and backend registration.

## Risks and Edge Cases
Environment and global function mutation mean tests should not be parallelized casually. The tests assert JSON text for option marshaling and therefore encode field ordering/format expectations.

## Test Signals
Coverage is good for user-visible option stringification/parsing and config priority behavior. It does not directly cover backend alias registration or reverse `FindFromFs` lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sizesuffix.go -->
# sources/user-network-fs/rclone/fs/sizesuffix.go

## Purpose
This file defines `SizeSuffix`, an int64-backed size flag type that parses and formats binary size suffixes for rclone options and JSON.

## Important APIs, Types, and Functions
- `type SizeSuffix int64` and constants `Kibi` through `Exbi` define binary units.
- `String`, `ByteUnit`, `ByteRateUnit`, `BitUnit`, and `BitRateUnit` format values.
- `Set(s string) error` parses strings such as `1K`, `1MiB`, `102B`, bare numbers, and `off`.
- `Type` identifies the flag type as `SizeSuffix`.
- `Scan` implements `fmt.Scanner`.
- `SizeSuffixList` implements sorting.
- `UnmarshalJSONFlag` and `(*SizeSuffix).UnmarshalJSON` parse JSON strings or integers.

## Control Flow
Formatting chooses the largest binary unit below the value and emits either integer or three-decimal precision; negative values render as `off`. Parsing treats bare numeric values as KiB, `B`/`b` as bytes, `K/M/G/T/P/E` and `Ki`/`KiB` forms as binary units, rejects unknown suffixes and negative numeric values, and maps `off` to `-1`.

## State and Persistence
The type is pure value state with no global mutation or persistence.

## Dependencies and Integration Points
It depends on `encoding/json`, `fmt`, `math`, `sort`, `strconv`, and `strings`. `Option.String` and option parsing use it for size configuration values, and JSON config/RC paths can unmarshal it.

## Risks and Edge Cases
Bare numbers default to KiB rather than bytes, which is intentional but easy to misuse. `MB` decimal-style suffixes are rejected. Very large parsed floats are converted to `SizeSuffix` without explicit overflow checks in `Set`, despite max/min constants being declared.

## Test Signals
`sizesuffix_test.go` covers string/unit formatting through EiB, parser accepted/rejected suffixes, scanning, and JSON string/integer unmarshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sizesuffix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sizesuffix_test.go -->
# sources/user-network-fs/rclone/fs/sizesuffix_test.go

## Purpose
This file verifies parsing, formatting, scanning, and JSON behavior for `SizeSuffix`.

## Important APIs, Types, and Functions
- Interface assertions verify `SizeSuffix` satisfies rclone flag interfaces.
- `TestSizeSuffixString`, `TestSizeSuffixByteUnit`, and `TestSizeSuffixBitRateUnit` check formatting.
- `TestSizeSuffixSet` checks accepted and rejected string syntax.
- `TestSizeSuffixScan` verifies `fmt.Sscan` integration.
- `TestSizeSuffixUnmarshalJSON` checks string and integer JSON inputs.

## Control Flow
The tests use table-driven cases, instantiate a fresh `SizeSuffix`, call the target method, assert expected error presence, and compare int64/string results.

## State and Persistence
No persistent or global state is touched.

## Dependencies and Integration Points
It uses `encoding/json`, `fmt`, and `testify`. The tests document behavior relied on by config, flags, and RC JSON option handling.

## Risks and Edge Cases
The tests explicitly reject `1MB` while accepting `1M` and `1MiB`, preserving the binary-only suffix contract. They do not cover overflow or NaN/Inf float parsing.

## Test Signals
Coverage is strong for normal values, off/negative rendering, invalid suffixes, empty strings, negative inputs, and JSON numeric fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sizesuffix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/pipe.go -->
# sources/user-network-fs/rclone/fs/sync/pipe.go

## Purpose
This file implements an internal unbounded object-pair queue for sync/copy/move pipelines, with optional heap ordering and queue-size accounting.

## Important APIs, Types, and Functions
- `pipe` stores a mutex-protected queue, a signaling channel, total queued size, stats callback, ordering comparator, and mixed-order fraction.
- `newPipe(orderBy, stats, maxBacklog)` constructs the pipe and parses ordering.
- `Put`, `Get`, `GetMax`, `Stats`, and `Close` provide queue operations.
- Heap methods `Len`, `Less`, `Swap`, `Push`, and `Pop` support ordered queues through `deheap`.
- `newLess(orderBy)` parses order strings by name/size/modtime and ascending/descending/mixed direction.

## Control Flow
`Put` locks, appends or heap-pushes, updates total size for non-delete pairs, calls stats, unlocks, then sends a token to the buffered channel. `GetMax` waits for a token, locks, pops FIFO or heap min/max depending on order and fraction, updates stats, and returns the pair. `Close` closes the signaling channel; subsequent writes panic via send on closed channel semantics.

## State and Persistence
State is in-memory only. The queue holds `fs.ObjectPair` references and deliberately clears removed entries to avoid retaining objects. `totalSize` tracks queued source sizes excluding `Src == Dst` delete signals.

## Dependencies and Integration Points
It depends on `fs.ObjectPair`, `fserrors.FatalError`, `math/bits`, and `github.com/aalpar/deheap`. `sync.go` uses pipes for checker, transfer, and rename queues, feeding accounting queue stats callbacks.

## Risks and Edge Cases
The pipe is not strictly ordered without `--order-by`; it approximates unbounded channel behavior with separate queue and token channel. `maxBacklog < 0` uses the largest positive int, which can allocate a very large buffered channel. Modtime ordering calls `ModTime(context.Background())`, which may be expensive or unsupported. `Close` is not idempotent and write-after-close panics by design.

## Test Signals
`pipe_test.go` covers basic put/get/close/cancel behavior, concurrent producers/consumers, order-by variants, mixed fractions, and invalid order strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/pipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/pipe_test.go -->
# sources/user-network-fs/rclone/fs/sync/pipe_test.go

## Purpose
This file tests the sync pipeline queue implementation.

## Important APIs, Types, and Functions
- Interface assertion verifies `pipe` satisfies `heap.Interface`.
- `TestPipe` checks stats, delete-signal size accounting, close/read behavior, write-after-close panic, and cancellation.
- `TestPipeConcurrent` stresses concurrent put/get pairs.
- `TestPipeOrderBy` checks queue ordering for name, size, modtime, ascending, descending, and mixed modes.
- `TestNewLess` validates parsing errors and comparator behavior.

## Control Flow
Tests create mock objects with content, enqueue object pairs, read them back, and assert queue stats and object order. Concurrent tests run paired reader/writer goroutines and use an atomic counter to verify balance.

## State and Persistence
All state is in memory and uses mock objects. No filesystem persistence is touched.

## Dependencies and Integration Points
It uses `mockobject`, `fs.ObjectPair`, `container/heap`, `sync`, `atomic`, and `testify`. It protects the behavior consumed by the high-concurrency sync engine in `sync.go`.

## Risks and Edge Cases
Concurrent assertions inside goroutines can produce multiple failures but are still useful for race detection when run with `-race`. Modtime comparator tests use mock object defaults, so they mainly protect parser/comparator wiring rather than backend-specific modtime costs.

## Test Signals
The tests give good evidence for queue correctness, stats callbacks, cancellation, and order parsing. They should be paired with race testing for stronger concurrency confidence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/pipe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/rc.go -->
# sources/user-network-fs/rclone/fs/sync/rc.go

## Purpose
This file registers RC endpoints for sync, copy, and move directory operations.

## Important APIs, Types, and Functions
- Init registers `sync/sync`, `sync/copy`, and `sync/move`.
- `rcSyncCopyMove(ctx, in, name)` resolves source/destination filesystems and dispatches to `Sync`, `CopyDir`, or `MoveDir`.

## Control Flow
For each operation name, an RC call is added with help text. At call time, `srcFs` and `dstFs` are required through `rc.GetFsNamed`. Optional `createEmptySrcDirs` is parsed if present. For move, optional `deleteEmptySrcDirs` is also parsed. Missing optional bools default false; invalid bools return parameter errors.

## State and Persistence
The file registers global RC calls at package initialization. The operation handlers can mutate source and destination remotes by copying, deleting, moving, and creating directories according to the chosen operation.

## Dependencies and Integration Points
It depends on `fs/rc` and the sync engine in `sync.go`. It integrates RC clients with rclone's core sync/copy/move behavior and filesystem cache/config resolution.

## Risks and Edge Cases
These endpoints are destructive for `sync` and `move`; server auth policy must protect them unless explicitly disabled. The closure over `name` relies on Go's per-iteration range variable semantics in the targeted Go version. Missing optional booleans are accepted, but malformed values fail.

## Test Signals
`sync/rc_test.go` exercises all three registered endpoints against local test remotes and verifies resulting source/destination contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/rc_test.go -->
# sources/user-network-fs/rclone/fs/sync/rc_test.go

## Purpose
This file tests the RC wrappers for sync, copy, and move directory operations.

## Important APIs, Types, and Functions
- `rcNewRun` creates a local fstest run, obtains the registered RC call, and inserts local/remote filesystems into `cache`.
- `TestRcCopy`, `TestRcMove`, and `TestRcSync` each prepare source/destination file sets, call the RC method, and assert final contents.

## Control Flow
Tests skip non-local remote test configurations, create source/destination files, call `call.Fn` with `srcFs` and `dstFs`, require no error, and verify copy/move/sync semantics: copy preserves extra destination files, move empties source, sync deletes destination-only files.

## State and Persistence
Tests create temporary local filesystem state via `fstest.Run` and mutate the global fs cache with `cache.Put` so RC filesystem resolution can find the test remotes.

## Dependencies and Integration Points
They depend on `fstest`, `fs/cache`, `rc.Calls`, and the actual sync engine. This is an integration-level test rather than a pure unit test.

## Risks and Edge Cases
The tests do not cover optional RC flags, invalid params, auth behavior, or remote backends with different capabilities. Cache mutation should remain test-isolated.

## Test Signals
The file confirms end-to-end RC registration and dispatch for the three primary directory operations on local backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync.go -->
# sources/user-network-fs/rclone/fs/sync/sync.go

## Purpose
This file is the core implementation of rclone directory sync, copy, move, and in-place transform operations. It coordinates listing/marching, checking, transfer queues, deletion modes, rename tracking, directory metadata/modtime handling, backup/compare/copy destinations, error aggregation, and duration cutoffs.

## Important APIs, Types, and Functions
- `syncCopyMove` is the central operation state object, storing source/destination filesystems, config/filter state, queues, maps, wait groups, error fields, rename tracking, backup/copy-dest state, directory metadata state, and overlap policy.
- Public entry points: `Sync`, `CopyDir`, `MoveDir`, and `Transform`.
- Internal orchestration: `newSyncCopyMove`, `runSyncCopyMove`, and `(*syncCopyMove).run`.
- Pipeline workers: `pairChecker`, `pairRenamer`, `pairCopyOrMove`, plus `start/stopCheckers`, `start/stopTransfers`, `start/stopRenamers`, `start/stopTrackRenames`, and `start/stopDeleters`.
- March callbacks: `SrcOnly`, `DstOnly`, and `Match`.
- Rename helpers: `parseTrackRenamesStrategy`, `renameID`, `makeRenameMap`, `tryRename`, `pushRenameMap`, and `popRenameMap`.
- Directory helpers: `markParentNotEmpty`, `markDirModified`, `copyDirMetadata`, `setDelayedDirModTimes`, and `deleteEmptyDirectories`.
- Error helpers: `processError`, `currentError`, and `aborting`.

## Control Flow
`runSyncCopyMove` validates incompatible delete/move combinations and runs a delete-only pass for `DeleteModeBefore`. `newSyncCopyMove` snapshots global config/filter settings, validates overlap and option combinations, creates checker/transfer/rename pipes, configures max-duration contexts, resolves backup/copy destinations, and disables unsupported track-renames modes. `run` starts worker goroutines, runs `march.March` over source and destination, optionally builds a rename map from remaining destination files, drains queues, applies delete-after and directory cleanup/modtime updates, processes context/deadline errors, cancels contexts, and returns the highest-priority error.

## State and Persistence
Runtime state is held in maps/channels/slices on `syncCopyMove`: destination/source file maps, empty-directory maps, rename candidates, delayed directory modtimes, modified directories, and queued object pairs. Persistent effects occur on the source/destination/backup filesystems: object copies, moves, deletes, directory creation, metadata updates, and backup-dir moves.

## Dependencies and Integration Points
It integrates with `fs.ConfigInfo`, filters, accounting stats, `march`, `operations`, backend feature flags, hash/modtime support, logger options, error classification, transform path rewriting, and the `pipe` queue implementation. RC wrappers and CLI commands ultimately call these entry points.

## Risks and Edge Cases
This is high-risk destructive code. Incorrect option interactions can delete or move wrong objects, so overlap checks, `SkipDestructive`, delete modes, backup-dir handling, and auth/RC exposure matter. Concurrency spans multiple worker pools and maps protected by mutexes; queue close order and context cancellation are critical. Track-renames depends on hash/modtime/leaf strategies and destination maps, and may be disabled based on backend capabilities. Directory modtime updates are delayed and level-ordered to avoid parent/child timestamp churn. Max-duration handling differs between hard, soft, and graceful cutoff modes.

## Test Signals
This subset includes RC integration tests and pipe tests, but not the main sync engine's broader test suite. Existing signals here prove basic RC copy/move/sync outcomes and queue behavior; full confidence requires running the repository's sync/operations/fstest tests because this file touches destructive and backend-dependent behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/sync/sync.go -->
