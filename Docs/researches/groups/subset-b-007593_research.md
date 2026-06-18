# Research: subset-b-007593

Grouped source research for Kubo command utilities, `ipfswatch`, core command plumbing, and configuration files. Each source section preserves the original path for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal_wasm.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal_wasm.go

Purpose: Provides the WASM-compatible interrupt handler implementation for the `cmd/ipfs/util` package. It avoids OS signal APIs and instead models interruption as a cancelable `context.Context`.

Important APIs/types/functions: `ctxCloser` adapts a `context.CancelFunc` to `io.Closer`. `SetupInterruptHandler(ctx)` returns that closer plus a derived context.

Control flow, state, and persistence: The only state is the derived context cancellation function. Calling `Close` cancels the context and returns nil. No persistent data, goroutines, or signal subscriptions are created in this WASM variant.

Dependencies and integration points: Depends only on `context` and `io`. It must match the non-WASM platform API so callers can call `SetupInterruptHandler` uniformly.

Risks and test signals: The main risk is behavioral drift from other platform implementations: WASM callers receive cancellation only when the returned closer is closed, not from OS signals. No direct tests in this subset cover it; compile/build-tag coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal_wasm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui.go

Purpose: Non-Windows GUI detection stub for CLI UI behavior.

Important APIs/types/functions: `InsideGUI() bool` always returns false on `!windows` builds.

Control flow, state, and persistence: No state and no side effects. The function is a platform split that lets shared code ask whether it likely runs from a GUI launcher.

Dependencies and integration points: No imports. The build tag excludes Windows so `ui_windows.go` supplies the Windows implementation.

Risks and test signals: Non-Windows platforms always report terminal-like behavior even when invoked from a graphical launcher. This is intentional but conservative. No direct tests are present; build-tag compilation is the relevant check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui_windows.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui_windows.go

Purpose: Windows-specific heuristic for determining whether the process was launched without an interactive terminal.

Important APIs/types/functions: `InsideGUI()` calls `windows.GetConsoleScreenBufferInfo(windows.Stdout, ...)` and returns true when the console cursor position is still `(0,0)`.

Control flow, state, and persistence: The function allocates a `ConsoleScreenBufferInfo`, queries stdout, returns false on API error, and otherwise treats an untouched cursor as a high-probability GUI launch. It has no persistent state.

Dependencies and integration points: Uses `golang.org/x/sys/windows`; pairs with `ui.go` for non-Windows builds. Callers can suppress terminal-oriented prompts or output behavior when it returns true.

Risks and test signals: The cursor-position heuristic can produce false positives if a terminal has not moved the cursor before Kubo starts, and false negatives if GUI launchers attach a console. No direct tests in this subset; behavior depends on Windows console API semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit.go

Purpose: Cross-platform entry point for raising the process file descriptor limit at startup.

Important APIs/types/functions: Package variables `supportsFDManagement`, `getLimit`, and `setLimit` are installed by platform files. `userMaxFDs()` parses `IPFS_FD_MAX`. `ManageFdLimit()` selects a target limit, compares current soft/hard limits, and attempts to raise them.

Control flow, state, and persistence: If platform support is disabled, `ManageFdLimit` is a no-op. Otherwise it defaults to `maxFds` (8192) unless `IPFS_FD_MAX` is a valid uint. It reads the current soft/hard limits, exits if the soft limit already satisfies the target, then tries to set soft and hard to target. On `syscall.EPERM`, it lowers the target to the hard limit if needed and tries setting only the soft limit, producing warnings when the result is below requested or below `minFds` (2048). No persistent state is written; only process resource limits and logs are affected.

Dependencies and integration points: Depends on `os`, `strconv`, `syscall`, and `go-log`. Platform implementations supply `getLimit`/`setLimit` in `ulimit_unix.go`, `ulimit_freebsd.go`, or no-op Windows behavior. Startup code can use the returned `changed`, `newLimit`, and `err` values for user-facing diagnostics.

Risks and test signals: Invalid `IPFS_FD_MAX` silently falls back to no user target after logging, which may surprise operators. Permission and hard-limit handling is subtle and OS-dependent. `ulimit_test.go` covers default value stability and invalid oversized env values on non-Windows/non-plan9.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_freebsd.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_freebsd.go

Purpose: FreeBSD-specific file descriptor limit implementation.

Important APIs/types/functions: `init()` enables FD management and binds `getLimit`/`setLimit`. `freebsdGetLimit()` wraps `unix.Getrlimit`. `freebsdSetLimit()` wraps `unix.Setrlimit`.

Control flow, state, and persistence: At package initialization, this file switches the generic ulimit logic on. It validates that returned FreeBSD `Rlimit` values are non-negative and that requested uint64 values fit into `int64` before converting to `unix.Rlimit`.

Dependencies and integration points: Uses `golang.org/x/sys/unix`, `errors`, and `math`. Integrated by package-level hooks consumed by `ManageFdLimit`.

Risks and test signals: Integer conversion is the main safety concern; explicit checks prevent wraparound. Runtime behavior still depends on FreeBSD privilege and resource limit policy. Covered indirectly by non-Windows/non-plan9 ulimit tests when run on FreeBSD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_test.go

Purpose: Non-Windows/non-plan9 tests for file descriptor limit management.

Important APIs/types/functions: `TestManageFdLimit` calls `ManageFdLimit` and locks `maxFds == 8192`. `TestManageInvalidNFds` sets `IPFS_FD_MAX` above the current maximum and expects an error path.

Control flow, state, and persistence: The tests mutate the process environment variable `IPFS_FD_MAX` and inspect kernel `RLIMIT_NOFILE` via `syscall.Getrlimit`. They do not persist files. Their behavior depends on the test process privileges and OS hard limit.

Dependencies and integration points: Uses `os`, `syscall`, `testing`, `fmt`, and string matching. It exercises the generic `ulimit.go` logic plus the active platform implementation.

Risks and test signals: The invalid-limit test can vary by platform if privileged processes can raise hard limits or if resource limits have unusual values. It provides useful regression coverage for default constants and error reporting, but not for all EPERM fallback combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_unix.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_unix.go

Purpose: Generic Unix file descriptor limit implementation for non-Windows, non-plan9, non-FreeBSD platforms.

Important APIs/types/functions: `init()` enables FD management and wires `getLimit`/`setLimit`. `unixGetLimit()` calls `syscall.Getrlimit`; `unixSetLimit()` calls `syscall.Setrlimit`.

Control flow, state, and persistence: The implementation directly converts syscall `Rlimit` values to and from `uint64`. No file or repository state is touched; it modifies only process resource limits through the kernel.

Dependencies and integration points: Uses the standard `syscall` package and the shared hooks consumed by `ManageFdLimit`.

Risks and test signals: Unlike FreeBSD, this path has no signed-range validation because common Unix `Rlimit` fields are unsigned in Go. Behavior is still constrained by OS hard limits and process privileges. Covered indirectly by `ulimit_test.go` on supported Unix platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_windows.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_windows.go

Purpose: Windows build placeholder for file descriptor limit management.

Important APIs/types/functions: The file contains only the `package util` declaration under a Windows build tag.

Control flow, state, and persistence: Because it does not install `getLimit`, `setLimit`, or set `supportsFDManagement`, the generic `ManageFdLimit` remains a no-op on Windows.

Dependencies and integration points: Pairs with `ulimit.go`; the package builds on Windows without Unix syscall code.

Risks and test signals: Windows processes do not benefit from Kubo's FD limit adjustment. Tests are explicitly excluded on Windows, so compile coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/ipfswatch_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/ipfswatch_test.go

Purpose: Unit coverage for hidden-directory detection in the `ipfswatch` helper command.

Important APIs/types/functions: `TestIsHidden` asserts that path components beginning with `.` are hidden except the current-directory marker `"."`.

Control flow, state, and persistence: No filesystem state is created; it only calls `IsHidden` with string paths.

Dependencies and integration points: Uses `testify/require`. The behavior protects `addTree` from recursively watching hidden directories such as `.git`.

Risks and test signals: The test is narrow; it does not cover watcher behavior, symlinks, recursive traversal, or errors from `os.Stat`. It does lock the special-case behavior for `"."`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/ipfswatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/main.go -->
# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/main.go

Purpose: Implements the `ipfswatch` command, a filesystem watcher that imports changed files into an IPFS node and optionally exposes the HTTP API.

Important APIs/types/functions: CLI flags are `--http`, `--repo`, and `--path`. `loadDatastorePlugins` registers datastore plugin parsers. `run` owns watcher setup, repository opening, node construction, CoreAPI creation, optional HTTP serving, event processing, and shutdown. `addTree` recursively watches non-hidden directories. `IsDirectory`, `IsHidden`, and `cmdCtx` are small helpers.

Control flow, state, and persistence: `run` expands the repo path, builds an `fsnotify.Watcher`, recursively adds the initial watch tree, loads datastore plugins, opens the fsrepo, starts an online `core.IpfsNode`, and creates a CoreAPI. The event loop handles SIGINT/SIGTERM, watcher events, and watcher errors. Non-remove events spawn goroutines that open the changed path, wrap it as a Boxo `files.PathFile`, and call `api.Unixfs().Add`. Directory creates add watches recursively; directory removals remove watches. Persistent effects are repository writes from UnixFS imports.

Dependencies and integration points: Integrates `fsnotify`, Kubo config/fsrepo/core/coreapi/corehttp, datastore plugins, Boxo files, and OS signal handling. `cmdCtx` adapts the live node for HTTP command serving.

Risks and test signals: There is minimal synchronization around concurrent add goroutines, no debounce of repeated editor events, and the goroutine closes over event data after the select iteration. Remove events call `IsDirectory` after removal, which can fail and skip watcher removal. Optional HTTP server errors are ignored in the goroutine. Test coverage only checks `IsHidden`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/codecov.yml -->
# Research: sources/distributed-fs/ipfs-kubo/codecov.yml

Purpose: Codecov service configuration for Kubo coverage reporting.

Important APIs/types/functions: YAML config excludes legacy CI hosts, accepts GitHub CI, requires two builds before notification, sets coverage range to `50...100`, project threshold to `0.2%`, patch threshold to `2%`, and disables comments.

Control flow, state, and persistence: This file has no runtime control flow. It affects external Codecov status checks and notifications when coverage is uploaded.

Dependencies and integration points: Consumed by Codecov infrastructure, not Go code. It integrates with CI coverage upload jobs outside this subset.

Risks and test signals: Threshold changes can make CI noisier or too permissive. Because comments are off, coverage feedback depends on status checks or Codecov UI. No local tests apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/commands/context.go -->
# Research: sources/distributed-fs/ipfs-kubo/commands/context.go

Purpose: Defines command execution context for Kubo commands, including lazy node/API construction, request logging, gateway-specific API behavior, and cleanup.

Important APIs/types/functions: `Context` holds config root, request log, plugin loader, gateway mode, cached CoreAPI/node, and `ConstructNode`. `GetConfig`, `GetNode`, `ClearCachedNode`, `GetAPI`, `Context`, `LogRequest`, and `Close` are the key methods.

Control flow, state, and persistence: `GetNode` lazily calls `ConstructNode` once and caches the result. `ClearCachedNode` discards the cache to avoid daemon startup using an earlier offline node. `GetAPI` lazily builds a CoreAPI and disables block fetching when used by a gateway with `Gateway.NoFetch`. `LogRequest` adds an active `ReqLogEntry` and returns a closure that marks it finished. `Close` closes the cached node. Persistent repository state is accessed through `node.Repo.Config()` but not modified here.

Dependencies and integration points: Bridges `go-ipfs-cmds`, Kubo core/coreapi/config, plugin loader, and command request logging. Gateway and daemon startup paths depend on its node caching semantics.

Risks and test signals: The cached `api` is not cleared when `ClearCachedNode` is called, so callers must ensure stale API state cannot survive node replacement. No locking protects lazy fields, so concurrent command setup could race if shared unexpectedly. Tests are indirect through command integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/commands/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/commands/reqlog.go -->
# Research: sources/distributed-fs/ipfs-kubo/commands/reqlog.go

Purpose: In-memory request log used by the active requests command and command context.

Important APIs/types/functions: `ReqLogEntry` stores timing, command, options, args, active state, and ID. `Copy` strips the back pointer. `ReqLog` stores entries, next ID, mutex, and retention duration. Methods include `AddEntry`, `ClearInactive`, `SetKeepTime`, `Report`, and `Finish`.

Control flow, state, and persistence: All mutations lock `ReqLog.lock`. `AddEntry` assigns monotonically increasing IDs and appends entries. Finished entries are cleaned opportunistically every 10 entries and by `ClearInactive`; active entries are retained regardless of age. `Report` returns copies to prevent callers from mutating internal entries. State is process-local only and resets on daemon restart.

Dependencies and integration points: Used by `commands.Context.LogRequest` and `core/commands/active.go`. Depends only on `sync` and `time`.

Risks and test signals: Cleanup cadence is approximate; a small number of stale inactive requests can remain until the next cleanup or explicit clear. Large option/argument values are retained in memory while entries are kept. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/commands/reqlog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/addresses.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/addresses.go

Purpose: Defines the address-related configuration schema for a Kubo node.

Important APIs/types/functions: `Addresses` has `Swarm`, `Announce`, `AppendAnnounce`, `NoAnnounce`, `API`, and `Gateway` fields. `API` and `Gateway` use the custom `Strings` type so JSON can hold a single string or an array.

Control flow, state, and persistence: No functions. Values are persisted in the repo config and consumed by libp2p host, identify, API listener, and gateway listener setup.

Dependencies and integration points: Integrated into top-level `Config`, defaults from `addressesConfig`, and profiles such as `server`, `test`, and `default-networking`.

Risks and test signals: Invalid multiaddrs are not validated here; downstream listener/routing setup must reject them. Tests are indirect via config reflection/default profile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/addresses.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/api.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/api.go

Purpose: Defines RPC API HTTP header and authorization configuration plus helper conversion for stored auth secrets.

Important APIs/types/functions: Constants `APITag` and `AuthorizationTag`; `RPCAuthScope` with `AuthSecret` and `AllowedPaths`; `API` with `HTTPHeaders` and `Authorizations`; `ConvertAuthSecret(secret)`.

Control flow, state, and persistence: `ConvertAuthSecret` treats no-prefix secrets as bearer tokens, supports `bearer:<token>`, supports `basic:user:pass` by base64-encoding the user/password portion, and passes through `basic:<base64>` values. Unknown typed prefixes return an empty string. Secrets are persisted in repo config if configured.

Dependencies and integration points: Used by HTTP RPC server auth setup. Depends on `encoding/base64` and `strings`.

Risks and test signals: Unknown prefix returning `""` can turn configuration mistakes into failed auth matching; callers must handle empty converted values safely. Basic pre-encoded detection is heuristic: absence of a colon means "already base64". `api_test.go` covers the documented conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/api_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/api_test.go

Purpose: Tests API authorization secret conversion.

Important APIs/types/functions: `TestConvertAuthSecret` verifies empty input, implicit bearer, explicit bearer, `basic:user:pass`, and pre-encoded `basic:<base64>`.

Control flow, state, and persistence: Pure table test; no filesystem or environment state.

Dependencies and integration points: Uses `testify/assert` and locks behavior required by API HTTP auth setup.

Risks and test signals: Does not cover unknown prefixes, malformed basic strings, or whitespace. It provides direct signal for the happy paths in `ConvertAuthSecret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/autoconf.go

Purpose: Defines AutoConf configuration and runtime expansion of `"auto"` placeholders for bootstrap peers, DNS resolvers, delegated routers, and delegated IPNS publishers.

Important APIs/types/functions: `AutoConf`, constants including `AutoPlaceholder`, `DefaultAutoConfURL`, and refresh/cache defaults. Helpers include `getNativeSystems`, `selectRandomResolver`, `expandAutoConfSlice`, `getAutoConf`, `DNSResolversWithAutoConf`, `BootstrapWithAutoConf`, `BootstrapPeersWithAutoConf`, `DelegatedRoutersWithAutoConf`, `DelegatedPublishersWithAutoConf`, `ExpandAutoConfValues`, and `ExpandConfigField`.

Control flow, state, and persistence: Runtime expansion is lazy and reads cached autoconf data only; it avoids network I/O during config access by using `client.GetCached()`. DNS expansion replaces configured `"auto"` values when matching autoconf data exists, preserves custom resolvers, and adds autoconf defaults for missing domains. Bootstrap expansion inserts autoconf peers once for each placeholder group. Delegated endpoint expansion delegates path filtering to Boxo autoconf. `ExpandAutoConfValues` clones only the top-level map before replacing supported fields, so nested maps are mutated when present.

Dependencies and integration points: Integrates `github.com/ipfs/boxo/autoconf`, Kubo `Config`, routing type, bootstrap parsing, and config-display paths. The daemon and config commands need these methods to agree on runtime expansion.

Risks and test signals: Random DNS resolver selection can make outputs non-deterministic. The shallow `maps.Clone` may surprise callers expecting a deep copy. Singleton client state in `autoconf_client.go` can make test/config changes sticky. `autoconf_test.go` covers defaults, profile wiring, and init placeholders but not expansion with real cached autoconf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf_client.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/autoconf_client.go

Purpose: Creates and validates the singleton AutoConf client used by configuration expansion.

Important APIs/types/functions: Package globals `clientOnce`, `clientCache`, and `clientErr`; `GetAutoConfClient`, `newAutoConfClient`, `ValidateAutoConfWithRepo`, and `validateAutoConfDisabled`.

Control flow, state, and persistence: `GetAutoConfClient` uses `sync.Once`, so the first config passed determines the process-wide client. `newAutoConfClient` builds a Boxo autoconf client with cache dir `$IPFS_PATH/autoconf`, user agent, cache size, timeout, refresh interval, fallback config, and configured URL. Validation rejects default mainnet AutoConf URL when a private swarm key exists. If AutoConf is disabled, it logs all lingering `"auto"` placeholders and returns a hard error only when Bootstrap is exactly `["auto"]`.

Dependencies and integration points: Depends on Boxo autoconf, Kubo version/user-agent, config path resolution, logging, and startup validation that knows whether a swarm key exists.

Risks and test signals: The singleton can ignore later config changes in the same process, which matters for tests or multi-repo tooling. `validateAutoConfDisabled` only hard-fails one bootstrap-only case; other auto placeholders may be silently skipped at runtime after logging. Tests cover profile/default behavior but not singleton reset or private-network validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/autoconf_test.go

Purpose: Unit tests for AutoConf defaults, the `autoconf-on` profile, and default init placeholder values.

Important APIs/types/functions: `TestAutoConfDefaults`, `TestAutoConfProfile`, and `TestInitWithAutoValues`.

Control flow, state, and persistence: Tests construct in-memory configs and call profile/init functions. They do not fetch remote autoconf or write repository state.

Dependencies and integration points: Uses `testify/assert` and `require`. It verifies `InitWithIdentity` and `Profiles["autoconf-on"]` set Bootstrap, DNS, Routing delegated routers, IPNS delegated publishers, and AutoConf enablement consistently.

Risks and test signals: Coverage does not exercise cache client behavior, placeholder expansion, private-network rejection, or disabled-auto validation. It is a strong signal that defaults and profile transforms continue to advertise `"auto"` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autoconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autonat.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/autonat.go

Purpose: Defines configuration for libp2p AutoNAT service mode and dialback throttling.

Important APIs/types/functions: `AutoNATServiceMode` enum values `Unset`, `Enabled`, `Disabled`, and `EnabledV1Only`; text marshal/unmarshal methods; `AutoNATConfig`; `AutoNATThrottleConfig`.

Control flow, state, and persistence: JSON/text decoding maps `""`, `"enabled"`, `"disabled"`, and `"legacy-v1"` to enum values. Unknown values error. Throttle config stores global/per-peer limits and an optional interval; semantics are applied by node construction, not this file.

Dependencies and integration points: Integrated into top-level `Config` and used by libp2p host/node setup. Low-power profile sets `ServiceMode` disabled.

Risks and test signals: `MarshalText` for unset returns nil bytes, which relies on encoding behavior for omitempty/defaults. Typoed modes fail during config decode. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autonat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autotls.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/autotls.go

Purpose: Defines AutoTLS/p2p-forge configuration for obtaining domain names and TLS certificates for browser-friendly connectivity.

Important APIs/types/functions: `AutoTLS` fields include `Enabled`, `AutoWSS`, `SkipDNSLookup`, `DomainSuffix`, registration endpoint/token/delay, CA endpoint, and `ShortAddrs`. Defaults are sourced from `p2p-forge` plus Kubo constants.

Control flow, state, and persistence: No functions. Values are persisted in config and resolved by node/network setup. Flags use the ternary `Flag` type so unset can mean "default".

Dependencies and integration points: Depends on `github.com/ipshipyard/p2p-forge/client` constants. Profiles `test` and `default-networking` adjust AutoTLS enablement.

Risks and test signals: AutoWSS, ShortAddrs, and DNS behavior depend on multiple flags and downstream address generation. Misconfigured private endpoints or tokens can break certificate registration. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/autotls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bitswap.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/bitswap.go

Purpose: Defines top-level Bitswap enablement configuration.

Important APIs/types/functions: `Bitswap` has `Libp2pEnabled` and `ServerEnabled` ternary flags. Defaults are `DefaultBitswapLibp2pEnabled` and `DefaultBitswapServerEnabled`, both true.

Control flow, state, and persistence: No functions. Flags are persisted in config and interpreted by node Bitswap setup.

Dependencies and integration points: Integrated with `HTTPRetrieval` and core node bitswap construction; `ServerEnabled` depends on libp2p bitswap being enabled.

Risks and test signals: Invalid combinations, such as server enabled while libp2p bitswap disabled, must be handled downstream. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bitswap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers.go

Purpose: Converts bootstrap peer configuration between serialized multiaddr strings and structured libp2p peer address info.

Important APIs/types/functions: `ErrInvalidPeerAddr`, `(*Config).BootstrapPeers`, `(*Config).SetBootstrapPeers`, `ParseBootstrapPeers`, and `BootstrapPeerStrings`.

Control flow, state, and persistence: `ParseBootstrapPeers` validates each string as a multiaddr and converts p2p multiaddrs to `peer.AddrInfo`. `SetBootstrapPeers` writes formatted strings back to `Config.Bootstrap`. `BootstrapPeerStrings` panics on `AddrInfoToP2pAddrs` errors, treating them as programmer errors.

Dependencies and integration points: Uses libp2p `peer` and multiaddr packages. `autoconf.go` uses parsing after expanding bootstrap placeholders. Repo config stores only strings.

Risks and test signals: All entries must be valid p2p multiaddrs; mixed invalid entries fail the entire parse. `ErrInvalidPeerAddr` is declared but not used in this file. `bootstrap_peers_test.go` covers round-trip formatting for autoconf fallback peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers_test.go

Purpose: Verifies bootstrap peer parse/format round-trip behavior.

Important APIs/types/functions: `TestBootstrapPeerStrings` parses `autoconf.FallbackBootstrapPeers`, formats the result, and checks element equality.

Control flow, state, and persistence: Pure in-memory test. It does not write config.

Dependencies and integration points: Uses Boxo autoconf fallback peer list and `testify` assertions. It protects compatibility between autoconf fallback peers and Kubo bootstrap serialization.

Risks and test signals: Uses `ElementsMatch`, so it does not enforce output ordering. It does not cover invalid multiaddrs or peers with multiple addresses beyond the fallback list shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/config.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/config.go

Purpose: Defines the root `Config` schema and core utilities for config path resolution, marshaling, map conversion, reflection-based shape inspection, cloning, and key validation.

Important APIs/types/functions: `Config` aggregates identity, datastore, addresses, routing, gateway, API, swarm, AutoConf, Provide, Import, internal settings, and more. Constants define default path names and `IPFS_PATH`. Functions include `PathRoot`, `Path`, `Filename`, `HumanOutput`, `Marshal`, `FromMap`, `ToMap`, `ReflectToMap`, `(*Config).Clone`, and `CheckKey`/validation helpers later in the file.

Control flow, state, and persistence: Path helpers resolve repo config locations without touching disk. JSON encode/decode is used for typed map conversion and deep-ish cloning. `ReflectToMap` recursively includes exported fields, including fields omitted by JSON, and adds `"*"` samples for maps so config-key validation can handle dynamic keys. Config persistence is handled elsewhere by `config/serialize`.

Dependencies and integration points: Central schema consumed by fsrepo, daemon, commands, profiles, and node construction. Uses `fsutil.ExpandHome`, JSON, reflection, and filepath utilities.

Risks and test signals: Reflection-based key validation can drift from JSON tags or special custom marshalers. `Clone` depends on JSON serialization and can lose unexported/custom runtime-only data. `config_test.go` covers clone isolation, reflected map shape, and important valid/invalid key paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/config_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/config_test.go

Purpose: Tests config cloning, reflection-to-map shape, and key validation.

Important APIs/types/functions: `TestClone`, `TestReflectToMap`, and `TestCheckKey`.

Control flow, state, and persistence: Tests use in-memory `Config` values. `TestClone` mutates the original after cloning to confirm map slices are not shared. `TestReflectToMap` checks representative struct, slice, map, pointer, string, int64, and bool conversions. `TestCheckKey` validates accepted nested/dynamic config paths and rejected unknown fields.

Dependencies and integration points: Directly exercises `Config.Clone`, `ReflectToMap`, and `CheckKey`, which support `ipfs config` command validation.

Risks and test signals: The reflection test checks selected fields, not the entire schema. It does not exercise all dynamic maps. It is useful for catching regressions in validation of `Provide.*`, gateway public gateway dynamic keys, and plugin config dynamic keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/datastore.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/datastore.go

Purpose: Defines datastore configuration and default datastore path helper.

Important APIs/types/functions: Constants for default datastore directory, block key cache size, and write-through behavior. `Datastore` stores storage limits, GC period, legacy fields, datastore `Spec`, hash/cache/write-through options. `DataStorePath(configroot)` resolves the default datastore path.

Control flow, state, and persistence: `DataStorePath` delegates to config path resolution. `Datastore.Spec` persists structured datastore plugin configuration; legacy fields remain for compatibility.

Dependencies and integration points: Integrated with fsrepo datastore setup and profiles/default init specs. Uses `encoding/json` for legacy raw params.

Risks and test signals: `Spec map[string]any` is flexible but weakly typed, so errors surface in datastore plugin parsing. Legacy fields can confuse migrations if both old and new fields are present. Default specs are tested indirectly through init/profile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/datastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/discovery.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/discovery.go

Purpose: Defines local discovery configuration.

Important APIs/types/functions: `Discovery` contains `MDNS`; `MDNS` has `Enabled bool`.

Control flow, state, and persistence: No functions. The boolean is persisted in config and consumed by node discovery setup.

Dependencies and integration points: Defaults are set in `InitWithIdentity`; profiles `server`, `local-discovery`, `test`, and `default-networking` mutate it.

Risks and test signals: There is no tri-state here, so explicit false and zero default are indistinguishable once omitted. Profile tests indirectly cover MDNS changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/discovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/dns.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/dns.go

Purpose: Defines custom DNS resolver configuration for Kubo.

Important APIs/types/functions: `DNS` has `Resolvers map[string]string` and `MaxCacheTTL *OptionalDuration`.

Control flow, state, and persistence: No functions here. Resolvers map FQDN suffixes such as `"."` or `"eth."` to resolver URLs, including DoH endpoints. AutoConf expansion in `autoconf.go` can replace `"auto"` resolver values.

Dependencies and integration points: Used by DNSLink/IPNS resolution, AutoTLS DNS behavior, and config profiles. Defaults are initialized with `"." : "auto"`.

Risks and test signals: Resolver URL validation is downstream. Random AutoConf resolver selection can change effective values between calls. Tests in `autoconf_test.go` and `config_test.go` indirectly cover default resolver presence and reflection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/dns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/experiments.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/experiments.go

Purpose: Holds experimental and legacy feature flags.

Important APIs/types/functions: `Experiments` includes filestore/urlstore/sharding/libp2p stream mounting/P2P HTTP proxy/optimistic provide/gateway-over-libp2p fields, plus removed-key sentinel fields `GraphsyncEnabled` and `AcceleratedDHTClient`.

Control flow, state, and persistence: No functions here, but custom sentinel types in `types.go` reject removed config keys during JSON decode while accepting limited empty/false values.

Dependencies and integration points: Consumed by daemon/node setup and config migration/validation. `AcceleratedDHTClient` moved to `Routing.AcceleratedDHTClient`.

Risks and test signals: Experimental flags can have unstable semantics. Deprecated fields remain for compatibility and may be ignored. Removed-key rejection is tested indirectly through `types.go` sentinel behavior but not by dedicated experiment tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/experiments.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/gateway.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/gateway.go

Purpose: Defines HTTP gateway behavior, including public gateway overrides, response modes, limits, and diagnostic links.

Important APIs/types/functions: Constants expose defaults from Boxo gateway and Kubo. `GatewaySpec` configures per-host paths, subdomain mode, DNSLink behavior, inline DNSLink, and deserialized responses. `Gateway` configures headers, root redirect, fetch behavior, DNSLink, response serialization, codec conversion, HTML errors, public gateways, routing API exposure, timeouts, concurrency, range limits, and diagnostic service URL.

Control flow, state, and persistence: No functions. Values persist in repo config and are interpreted by the gateway server. Several fields use `Flag`, `OptionalDuration`, `OptionalInteger`, or `OptionalBytes` so omitted values can defer to defaults.

Dependencies and integration points: Consumed by core HTTP gateway setup and `commands.Context.GetAPI` via `Gateway.NoFetch`. Public gateway dynamic keys are handled by config key validation.

Risks and test signals: Gateway behavior is security-sensitive: path/subdomain mixing, DNSLink, codec conversion, routing API exposure, and fetch/no-fetch all affect origin isolation and retrieval. Direct tests are not in this subset; `config_test.go` checks validation of dynamic `Gateway.PublicGateways.*.Paths`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/http_retrieval.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/http_retrieval.go

Purpose: Defines configuration for HTTP-based block retrieval.

Important APIs/types/functions: `HTTPRetrieval` fields include `Enabled`, allowlist, denylist, worker count, max block size, and TLS insecure skip verify. Defaults set HTTP retrieval enabled, 16 workers, `2MiB` max block size, and TLS verification enabled.

Control flow, state, and persistence: No functions. Values are persisted and consumed by core node bitswap/retrieval setup.

Dependencies and integration points: Related to Bitswap config because HTTP retrieval can supplement or replace libp2p block retrieval in some modes.

Risks and test signals: Allow/deny lists and TLS skip verification have security implications. Max block size must stay aligned with Bitswap protocol limits. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/http_retrieval.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/identity.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/identity.go

Purpose: Stores and decodes the local node identity.

Important APIs/types/functions: Constants identify config selectors. `Identity` stores `PeerID` and base64 private key. `DecodePrivateKey(passphrase)` decodes the base64 key and unmarshals a libp2p private key.

Control flow, state, and persistence: Private keys are persisted unencrypted in the config. `passphrase` is unused. Decode returns libp2p crypto errors for bad base64 or invalid key bytes.

Dependencies and integration points: `CreateIdentity` in `init.go` populates this struct. Node construction uses it for libp2p identity.

Risks and test signals: Plaintext private key storage is explicitly noted as a security TODO. `init_test.go` verifies RSA and Ed25519 identities can be decoded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/import.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/import.go

Purpose: Defines import defaults and validation for UnixFS ingestion behavior used by `ipfs add`, MFS writes, DAG/block import paths, and related commands.

Important APIs/types/functions: `Import` stores CID version, raw leaves, chunker, hash, max links, HAMT fanout/threshold/estimation, DAG layout, batch limits, and fast-provide flags. `ValidateImportConfig`, `isPowerOfTwo`, `isValidChunker`, `HAMTSizeEstimationMode`, `UnixFSSplitterFunc`, `MFSRootOptions`, and `UnixFSCidBuilder` are the core functions.

Control flow, state, and persistence: Validation only checks explicitly configured optional values. It restricts CID version to 0/1, positive file links and batch limits, non-negative directory max links, HAMT fanout power-of-two from 8 through 1024, recognized/allowed hash functions, valid chunker syntax, valid HAMT estimation modes, and valid DAG layouts. `UnixFSSplitterFunc` returns an optimized size splitter when possible and falls back to Boxo parsing/default splitter for invalid rare cases. `UnixFSCidBuilder` upgrades CIDv0 to CIDv1 when using non-default hash and always returns an explicit prefix. Values persist in config and alter resulting CIDs.

Dependencies and integration points: Uses Boxo chunker, UnixFS helpers, MFS, verifcid, go-cid, and multihash. `core/commands/add.go`, MFS, and profiles use these defaults.

Risks and test signals: Import settings directly affect CID determinism and interoperability. `UnixFSSplitterFunc` can silently fall back if invalid config bypasses validation. `import_test.go` extensively covers validation, chunkers, CID builders, defaults, HAMT estimation, and DAG layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/import_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/import_test.go

Purpose: Broad unit coverage for import configuration validation and derived UnixFS behavior.

Important APIs/types/functions: Tests cover `ValidateImportConfig` for HAMT fanout, CID version, file/directory max links, batch limits, chunkers, hash functions, defaults, HAMT size estimation, and DAG layout. It also tests `isValidChunker`, `isPowerOfTwo`, `UnixFSCidBuilder`, default CID builder behavior, and `HAMTSizeEstimationMode`.

Control flow, state, and persistence: Pure in-memory table tests. CID builder tests generate CIDs from `[]byte("test")` to inspect prefix version and multihash type.

Dependencies and integration points: Uses Boxo UnixFS size-estimation constants and multihash names. It protects config behavior consumed by `ipfs add` and MFS import.

Risks and test signals: Coverage is strong for validation edges and import defaults. It does not run full UnixFS imports, so actual DAG layout, batch writing, and chunk output compatibility are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/init.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/init.go

Purpose: Builds initial Kubo config defaults and creates new peer identities.

Important APIs/types/functions: `Init`, `InitWithIdentity`, connection manager/resource manager defaults, `addressesConfig`, `DefaultDatastoreConfig`, datastore spec helpers (`pebbleSpec`, `badgerSpec`, `flatfsSpec` and measure variants), and `CreateIdentity`.

Control flow, state, and persistence: `Init` generates an identity then delegates to `InitWithIdentity`. Initial config sets API/gateway headers, default swarm/API/gateway addresses, flatfs datastore, Bootstrap/DNS/delegated routing/IPNS publishers to `"auto"`, MDNS on, mount paths, gateway defaults, and empty remote pinning services. `CreateIdentity` validates key options, generates RSA or Ed25519 keys, stores the private key as base64, derives PeerID, and writes progress messages to the supplied writer.

Dependencies and integration points: Uses libp2p crypto/peer, Kubo options, Cockroach Pebble version constants, and config profiles. fsrepo init persists the returned config.

Risks and test signals: Identity private keys are stored unencrypted. Default `"auto"` values require AutoConf to remain enabled or replaced. Datastore specs are untyped maps and plugin-dependent. `init_test.go` covers RSA/Ed25519 identity generation and rejects Ed25519 size options; `autoconf_test.go` covers init auto placeholders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/init_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/init_test.go

Purpose: Tests identity creation behavior.

Important APIs/types/functions: `TestCreateIdentity` generates Ed25519 and RSA identities and decodes the private key type. `TestCreateIdentityOptions` verifies Ed25519 rejects an explicit bit size.

Control flow, state, and persistence: Tests use an in-memory `bytes.Buffer` for progress output. They generate real keys but write no files.

Dependencies and integration points: Uses Kubo key generation options and libp2p crypto protobuf key types. Protects `Init`/identity setup compatibility with node construction.

Risks and test signals: Key generation can consume entropy and is slower than pure unit tests. Tests do not verify PeerID/public key matching beyond successful decode/type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/init_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/internal.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/internal.go

Purpose: Defines unstable/internal configuration knobs for MFS, shutdown, diagnostics, and Bitswap internals.

Important APIs/types/functions: Defaults include MFS no-flush limit, shutdown timeout, CGNAT check, and dead-listener check. `Internal` holds optional fields for Bitswap, UnixFS sharding migration, reachability, backup bootstrap, MFS no-flush, shutdown timeout, and diagnostic flags. `InternalBitswap` and `BitswapBroadcastControl` hold detailed Bitswap worker/search/broadcast tuning. Broadcast defaults are declared later in the file.

Control flow, state, and persistence: No functions except constants/types. These values are persisted only when set and interpreted by lower-level node subsystems. Many are experimental and may change.

Dependencies and integration points: Uses `time` and custom optional/flag types. `core/builder.go` consumes shutdown timeout through build config derived from internal config.

Risks and test signals: Internal options can destabilize networking or resource behavior. Removed/moved options are partly handled in `types.go`. `internal_test.go` covers default-enabled diagnostic flags and JSON omission/false decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/internal_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/internal_test.go

Purpose: Locks default and JSON behavior for internal diagnostic flags.

Important APIs/types/functions: `TestInternalCheckFlagsDefaultEnabled` and `TestInternalCheckFlagsJSON`.

Control flow, state, and persistence: Pure JSON/in-memory tests. They verify zero-value flags resolve to enabled defaults, unset flags are omitted from JSON, and explicit false disables checks.

Dependencies and integration points: Exercises `Flag.WithDefault`, `json.Marshal`, and `json.Unmarshal` for `Internal`.

Risks and test signals: Narrow coverage, but important for operator-facing diagnostics because omitted config should not disable CGNAT/dead-listener checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/ipns.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/ipns.go

Purpose: Defines IPNS publishing/resolution configuration.

Important APIs/types/functions: `DefaultIpnsMaxCacheTTL`; `Ipns` fields include republish period, record lifetime, resolve cache size, max cache TTL, pubsub usage flag, and delegated publisher URLs.

Control flow, state, and persistence: No functions. Values are persisted in config and consumed by namesys/IPNS services. Delegated publishers can contain `"auto"` and are expanded in `autoconf.go`.

Dependencies and integration points: Uses `math` and `time` for maximum default TTL. Init defaults set resolve cache size and delegated publishers.

Risks and test signals: Republish period/lifetime are strings, so validation happens downstream. Delegated publisher auto expansion depends on AutoConf and routing type. Tests in `autoconf_test.go` cover init/profile placeholder behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/ipns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/migration.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/migration.go

Purpose: Retains deprecated configuration for legacy external repo migrations.

Important APIs/types/functions: `DefaultMigrationKeep`, `DefaultMigrationDownloadSources`, and `Migration` fields `DownloadSources` and `Keep`.

Control flow, state, and persistence: No functions. The comments state these settings apply only to repo versions below 16; modern repos use embedded migrations and ignore them.

Dependencies and integration points: Top-level `Config` includes `Migration`; migration code outside this subset reads it for old repositories.

Risks and test signals: Operators may assume these settings affect modern migrations when they do not. `migration_test.go` checks decoding preserves legacy config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/migration_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/migration_test.go

Purpose: Tests JSON decoding of migration configuration.

Important APIs/types/functions: `TestMigrationDecode` decodes `{"Migration":{"DownloadSources":["HTTPS"],"Keep":"cache"}}` into `Config`.

Control flow, state, and persistence: In-memory JSON decode only.

Dependencies and integration points: Exercises top-level config decoding for deprecated migration fields.

Risks and test signals: It only covers one valid legacy example; it does not validate deprecation behavior or modern ignored semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/mounts.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/mounts.go

Purpose: Defines FUSE mount path and metadata persistence configuration.

Important APIs/types/functions: Defaults for `FuseAllowOther`, `StoreMtime`, and `StoreMode`; `Mounts` fields `IPFS`, `IPNS`, `MFS`, `FuseAllowOther`, `StoreMtime`, and `StoreMode`.

Control flow, state, and persistence: No functions. Values are persisted in config and consumed by mount commands/FUSE integration. StoreMtime/StoreMode affect UnixFS metadata and therefore resulting CIDs for writable mounts.

Dependencies and integration points: Init sets `/ipfs`, `/ipns`, and `/mfs`. Uses the shared `Flag` type for optional booleans.

Risks and test signals: Enabling metadata persistence changes content addressing and interoperability expectations. `FuseAllowOther` has local security implications. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/mounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/peering.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/peering.go

Purpose: Defines persistent peers that the node should attempt to keep connected.

Important APIs/types/functions: `Peering` contains `Peers []peer.AddrInfo`.

Control flow, state, and persistence: No functions. Peer address info is serialized in config and consumed by the peering service.

Dependencies and integration points: Uses libp2p `peer.AddrInfo`. Profiles and command tooling may mutate it outside this subset.

Risks and test signals: Invalid or stale peer addresses can cause repeated dial attempts. Serialization shape depends on libp2p AddrInfo JSON behavior. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/peering.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/plugins.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/plugins.go

Purpose: Defines plugin configuration schema.

Important APIs/types/functions: `Plugins` holds a map of plugin name to `Plugin`; `Plugin` has `Disabled` and arbitrary `Config`.

Control flow, state, and persistence: No functions. Plugin config is persisted and interpreted by plugin loader implementations.

Dependencies and integration points: `commands.Context` holds a plugin loader. `config_test.go` verifies dynamic key validation for `Plugins.Plugins.peerlog.Config.Enabled`.

Risks and test signals: `Config any` intentionally allows arbitrary shape, so validation is limited and plugin-specific. Loader path is omitted for security. Tests cover dynamic key validation but not plugin runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/plugins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/profile.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/profile.go

Purpose: Defines named config profiles that transform initial or existing Kubo config for common deployment modes and import compatibility modes.

Important APIs/types/functions: `Transformer`, `Profile`, `defaultServerFilters`, `Profiles` map, helpers `getAvailablePort`, `appendSingle`, `deleteEntries`, `mapKeys`, and `applyUnixFSv02015`.

Control flow, state, and persistence: Each profile mutates a `*Config` in memory. Networking profiles add/remove address filters, disable MDNS/NAT port mapping, pick random swarm ports, or restore defaults. Datastore profiles replace `Datastore.Spec` and are marked init-only where needed. Lowpower reduces DHT/relay/connection manager settings. Announce profiles toggle `Provide`. UnixFS profiles pin import defaults for legacy CIDv0 or newer CIDv1 settings. AutoConf profiles set or clear `"auto"` fields and AutoConf enablement.

Dependencies and integration points: Profiles are used by `ipfs init --profile` and config profile commands. They coordinate with init defaults, datastore plugin specs, import config, AutoConf, routing, and provide config.

Risks and test signals: Profile transforms can overwrite operator settings. `randomports` has a TOCTOU race between finding and later binding a free port. `deleteEntries` returns map iteration order, so output order is nondeterministic. Tests in this subset cover AutoConf profile behavior; broader profile coverage is elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provide.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/provide.go

Purpose: Defines the unified provide/reprovide configuration and strategy validation for announcing local content to routing systems.

Important APIs/types/functions: Defaults for strategy, Bloom false-positive rate, DHT intervals/workers/sweep/resume/offline/timeout. `ProvideStrategy` bit flags include all, pinned, roots, MFS, unique, and entities. `Provide`, `ProvideDHT`, `ParseProvideStrategy`, `MustParseProvideStrategy`, `ValidateProvideConfig`, and `ShouldProvideForStrategy` are the key APIs.

Control flow, state, and persistence: Strategy parsing splits on `+`, maps `flat` to `all`, rejects unknown and empty tokens, prevents `all` from combining with selective strategies, and requires `+unique/+entities` to combine with pinned and/or MFS but not roots. Validation also enforces Bloom FP minimum, DHT interval bounds and the explicit `Provide.Enabled` requirement when interval is zero, positive worker/connection/batch/timeout settings, and non-negative dedicated workers/offline delay. State persists in config; sweep provider resume may persist runtime provider state downstream when enabled.

Dependencies and integration points: Uses libp2p Amino DHT provider validity. `core/commands/add.go` and provider subsystems use strategy and Bloom settings for fast provide and reprovides.

Risks and test signals: Strategy grammar is operator-facing and affects content discoverability. Bloom FP rates trade memory for skipped CID risk. Interval zero semantics changed and are guarded by validation. `provide_test.go` covers strategy parsing, validation edges, and `ShouldProvideForStrategy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provide.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provide_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/provide_test.go

Purpose: Tests provide strategy parsing, config validation, and selection logic.

Important APIs/types/functions: Tests cover `ParseProvideStrategy`, `MustParseProvideStrategy`, `ValidateProvideConfig` strategy/interval/Bloom/worker cases, and `ShouldProvideForStrategy`.

Control flow, state, and persistence: Pure in-memory tests. Table cases verify valid combinations, typo rejection, delimiter errors, `all` combination rejection, unique/entities constraints, interval zero migration guard, interval upper bound, Bloom minimum, positive workers, and OR behavior for combined strategies.

Dependencies and integration points: Uses `testify/assert` and `require`. Protects behavior consumed by provider setup and `ipfs add` fast-provide logic.

Risks and test signals: Strong for parser and basic validation. It does not exercise actual DHT providing, Bloom implementation, or persisted sweep resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provide_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provider.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/provider.go

Purpose: Deprecated legacy provider configuration kept for compatibility.

Important APIs/types/functions: `Provider` has deprecated `Enabled`, `Strategy`, and `WorkerCount` fields, with comments pointing to `Provide`.

Control flow, state, and persistence: No functions. Fields may still decode from old config but should be migrated or ignored in favor of `Provide`.

Dependencies and integration points: Top-level `Config` includes both legacy `Provider` and new `Provide`. Migration/compatibility code outside this file handles mapping.

Risks and test signals: Dual legacy/new config can confuse operators. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/pubsub.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/pubsub.go

Purpose: Defines pubsub configuration and duplicate-message tracking strategy names.

Important APIs/types/functions: Strategy constants `last-seen`, `first-seen`, and default. `PubsubConfig` fields include router, signing, enabled flag, seen-message TTL, and seen-message strategy.

Control flow, state, and persistence: No functions. Values persist in config and are consumed by pubsub/namesys setup.

Dependencies and integration points: `Ipns.UsePubsub` and daemon flags interact with this config. Optional types allow defaults to be omitted.

Risks and test signals: Strategy string validation is not in this file, so typos must be handled downstream. Disabling signing changes message authenticity semantics. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/remotepin.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/remotepin.go

Purpose: Defines remote pinning service configuration and selectors for concealing API keys.

Important APIs/types/functions: `RemoteServicesPath`, `PinningConcealSelector`, `Pinning`, `RemotePinningService`, `RemotePinningServiceAPI`, `RemotePinningServicePolicies`, and `RemotePinningServiceMFSPolicy`.

Control flow, state, and persistence: No functions. Service endpoints and API keys persist in config; conceal selector identifies `Pinning.RemoteServices.*.API.Key` as sensitive for display.

Dependencies and integration points: Used by pin remote commands/services and MFS remote pin policy logic. Init creates an empty `RemoteServices` map.

Risks and test signals: API keys are stored in config and must be concealed in output. Repin intervals are strings and require downstream validation. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/remotepin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/reprovider.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/reprovider.go

Purpose: Deprecated legacy reprovider configuration kept for compatibility.

Important APIs/types/functions: `Reprovider` has deprecated `Interval` and `Strategy` fields pointing to `Provide.DHT.Interval` and `Provide.Strategy`.

Control flow, state, and persistence: No functions. Fields may decode old configs but should not be the primary source of truth in new configs.

Dependencies and integration points: Top-level `Config` keeps `Reprovider` alongside unified `Provide`.

Risks and test signals: Legacy/new duplication can produce migration ambiguity. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/reprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/routing.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/routing.go

Purpose: Defines routing mode, delegated router configuration, advanced custom router composition, method validation, environment-derived filters, and HTTP-provider detection.

Important APIs/types/functions: Routing defaults and env keys; `Routing`, `Router`, `Routers`, `Methods`, `RouterParser`, router types, DHT modes, method names/list, `HTTPRouterParams.FillDefaults`, `DHTRouterParams`, `ComposableRouterParams`, `ConfigRouter`, `Method`, `getEnvOrDefault`, `(*Config).HasHTTPProviderConfigured`, and `routerSupportsHTTPProviding`.

Control flow, state, and persistence: `Methods.Check` requires all supported methods and rejects unknown ones. `RouterParser.UnmarshalJSON` first decodes the router type then decodes `Parameters` into type-specific structs for HTTP, DHT, sequential, or parallel routers. HTTP params fill default batch/concurrency values when zero. `getEnvOrDefault` accepts comma/space-separated env overrides. HTTP-provider detection walks custom router composition recursively from the provide method.

Dependencies and integration points: Integrates config with routing subsystem, delegated routing HTTP clients, DHT mode setup, autoconf delegated endpoint expansion, and provide capability decisions.

Risks and test signals: Recursive router detection can loop indefinitely on cyclic custom router configs. Unknown router types leave parameters as generic nil/empty without explicit validation here. Env-based defaults are process-global and can change tests. `routing_test.go` covers typed JSON parameter round-trip and method completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/routing_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/routing_test.go

Purpose: Tests routing custom-router JSON parameter decoding and method validation.

Important APIs/types/functions: `TestRouterParameters` builds a custom routing config with DHT, parallel, and sequential routers and checks decoded parameter concrete types. `TestMethods` validates complete and missing method maps.

Control flow, state, and persistence: Pure JSON marshal/unmarshal and in-memory validation. It uses durations and optional duration fields inside composable routers.

Dependencies and integration points: Uses `testify/require`. Protects `RouterParser.UnmarshalJSON` and `Methods.Check`, both required for advanced custom routing configs.

Risks and test signals: Does not test HTTP router params, unknown methods, unsupported router types, cyclic router graphs, or environment filter parsing. It is strong for preserving typed parameters across JSON round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/routing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/serialize/serialize.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/serialize/serialize.go

Purpose: Reads and writes Kubo config files for fsrepo.

Important APIs/types/functions: `ErrNotInitialized`, `ReadConfigFile`, `WriteConfigFile`, `encode`, and `Load`.

Control flow, state, and persistence: `ReadConfigFile` opens and JSON-decodes a config file, mapping missing files to `ErrNotInitialized`. `WriteConfigFile` creates parent directories, opens an atomic file with mode `0600`, writes pretty JSON via `config.Marshal`, and relies on atomicfile close semantics. `Load` reads into `config.Config`.

Dependencies and integration points: Package name is `fsrepo` despite living under `config/serialize`; it is part of repository config persistence. Uses `facebookgo/atomicfile` to avoid partial writes.

Risks and test signals: Decode errors wrap with context but do not include filename. Atomic write close errors depend on deferred close behavior from atomicfile. `serialize_test.go` verifies round-trip and permissions on non-Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/serialize/serialize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/serialize/serialize_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/serialize/serialize_test.go

Purpose: Tests config file write/read round-trip and file permissions.

Important APIs/types/functions: `TestConfig` writes `.ipfsconfig`, loads it, compares `Identity.PeerID`, stats the file, and checks permissions on non-Windows.

Control flow, state, and persistence: Creates a local `.ipfsconfig` file in the test working directory. It verifies the file is not executable or world-accessible on Unix-like platforms.

Dependencies and integration points: Uses `config.Config`, `WriteConfigFile`, and `Load`. Permission check is skipped on Windows due to Go/os mode differences.

Risks and test signals: The test writes a fixed relative filename and does not clean it up in the snippet, so test isolation depends on working directory conventions. It does not test missing file mapping or atomic failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/serialize/serialize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/swarm.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/swarm.go

Purpose: Defines libp2p swarm, relay, transport, connection manager, and resource manager configuration.

Important APIs/types/functions: `SwarmConfig`, `RelayClient`, `RelayService`, `Transports`, `ConnMgr`, `ResourceMgr`, and resource scope prefix constants.

Control flow, state, and persistence: No functions. The schema stores address filters, bandwidth/NAT settings, relay client/service settings, hole punching, transport enablement and priorities, connection manager watermarks/durations, and resource manager memory/fd/allowlist options. Values persist in config and are consumed by node/libp2p construction.

Dependencies and integration points: Profiles modify `Swarm.AddrFilters`, NAT port mapping, relay service, and connection manager fields. Removed `ResourceMgr.Limits` is guarded by a sentinel in `types.go`.

Risks and test signals: Misconfigured filters can block listeners or peer dials. Transport/security priority values can disable essential transports. Resource manager settings affect process stability. No direct tests here; `internal.go` defaults and profile behavior are indirect signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/types.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/types.go

Purpose: Provides custom JSON helper types used throughout config for flexible strings, ternary flags, priorities, optional durations/integers/strings/bytes, and removed-key sentinels.

Important APIs/types/functions: `Strings`, `Flag`, `ResolveBoolFromConfig`, `Priority`, `OptionalDuration`, `Duration`, `OptionalInteger`, `OptionalString`, `OptionalBytes`, and sentinel types `swarmLimits`, `experimentalAcceleratedDHTClient`, and `graphsyncEnabled`.

Control flow, state, and persistence: `Strings` decodes either a string or array and encodes nil/single/array shapes. `Flag` maps false/default/true to JSON false/null/true. `Priority` maps disabled/default/positive priorities and rejects invalid values. Optional types preserve omitted/default as nil and provide `WithDefault`. `OptionalBytes` validates/parses human byte strings and numeric values. Sentinel unmarshaler types accept limited empty/false forms and reject removed config keys with migration guidance.

Dependencies and integration points: Used by nearly every config section and by command code resolving config-vs-flag precedence. Depends on JSON, time, and `go-humanize`.

Risks and test signals: Several `WithDefault` methods tolerate nil receivers, which is intentional but easy to overlook. `OptionalBytes.WithDefault` panics if invalid values are manually constructed. Sentinel errors are important migration UX. `types_test.go` covers all major helper types and invalid cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/types_test.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/types_test.go

Purpose: Comprehensive unit coverage for custom config JSON helper types.

Important APIs/types/functions: Tests cover `OptionalDuration`, `Strings`, `Flag`, `Priority`, `OptionalInteger`, `OptionalString`, and `OptionalBytes`.

Control flow, state, and persistence: Pure in-memory JSON marshal/unmarshal and default-resolution tests. It verifies omitempty behavior, valid round trips, invalid input rejection, byte-size parsing, nil/default semantics, and `OptionalBytes` panic on manually corrupted state.

Dependencies and integration points: Uses `testify` assertions and standard JSON/time. These helper contracts affect all config files that use optional/flag types.

Risks and test signals: Strong coverage for serialization semantics. It does not test every sentinel removed-key type in the visible snippet, but it covers the common helper types that most config sections rely on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/version.go -->
# Research: sources/distributed-fs/ipfs-kubo/config/version.go

Purpose: Defines version/user-agent related configuration and swarm update-check thresholds.

Important APIs/types/functions: `DefaultSwarmCheckPercentThreshold`; `Version` with `AgentSuffix`, `SwarmCheckEnabled`, and `SwarmCheckPercentThreshold`.

Control flow, state, and persistence: No functions. Values persist in config and are consumed by identify/version-check code outside this subset.

Dependencies and integration points: Uses optional string, flag, and optional integer helper types. `autoconf_client.go` uses Kubo version code for user-agent separately.

Risks and test signals: Agent suffix changes externally visible libp2p identify data. Update-check thresholds can affect warning noise. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/config/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/builder.go -->
# Research: sources/distributed-fs/ipfs-kubo/core/builder.go

Purpose: Constructs `IpfsNode` instances using Uber FX, supports global FX option injection, coordinates lifecycle shutdown, and normalizes FX errors.

Important APIs/types/functions: `FXNodeInfo`, `fxOptFunc`, `RegisterFXOptionFunc`, `valueContext`, `BuildCfg` alias, `NewNode`, and `logAndUnwrapFxError`.

Control flow, state, and persistence: `NewNode` saves the caller lifetime context, creates a cancelable context that keeps values but ignores parent cancellation, adds metrics scope, builds FX options from `node.IPFS`, global option funcs, `fx.NopLogger`, and `fx.Extract(n)`, then starts the app. It installs `n.stop` with `sync.Once`, bounded by `cfg.ShutdownTimeout` unless zero, stopping FX before canceling node context. A goroutine stops the node when the lifetime context is canceled. Online nodes run bootstrap after start; offline nodes return immediately. No direct persistence happens here, but dependencies initialize repo-backed subsystems.

Dependencies and integration points: Uses Boxo bootstrap, Kubo core/node, metrics, Uber FX/Dig. Plugin/extension code can globally register option functions affecting all node construction sites.

Risks and test signals: `fxOptionFuncs` is global mutable state without locking; registration order and test isolation matter. Ignoring lifetime cancellation in the working context is subtle but intentional. Shutdown hooks can still run until timeout. Error unwrapping depends on dig private error behavior. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/active.go -->
# Research: sources/distributed-fs/ipfs-kubo/core/commands/active.go

Purpose: Implements `ipfs commands`/active request listing and request-log maintenance subcommands.

Important APIs/types/functions: `ActiveReqsCmd`, `clearInactiveCmd`, and `setRequestClearCmd`; option `--verbose`.

Control flow, state, and persistence: The main command emits `ctx.ReqLog.Report()`. Text encoding writes a tabular report with command, active state, start time, runtime, and optionally ID/args/options sorted by option key. `clear` calls `ReqLog.ClearInactive`. `set-time` parses a duration and updates request-log retention. State is in-memory request log only.

Dependencies and integration points: Uses old command `Context` from `commands` package, `go-ipfs-cmds`, tabwriter, and `ReqLogEntry` types. Exposed as a `NoLocal` command for RPC context.

Risks and test signals: Verbose output may expose command arguments/options with sensitive values if such options are logged. Runtime for active requests is computed at encode time and can vary. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/active.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/add.go -->
# Research: sources/distributed-fs/ipfs-kubo/core/commands/add.go

Purpose: Implements the user-facing `ipfs add` command, translating CLI/config import settings into CoreAPI UnixFS add options, emitting progress/events, optional MFS linking, pinning, and fast provide behavior.

Important APIs/types/functions: `ErrDepthLimitExceeded`, `AddEvent`, many option-name constants, `AddCmd` with `PreRun`, `Run`, and CLI `PostRun`. The command uses `options.Unixfs.*`, `cmdenv.ExecuteFastProvideRoot`, and `cmdenv.ExecuteFastProvideDAG`.

Control flow, state, and persistence: `PreRun` defaults progress to terminal stderr unless quiet/silent. `Run` obtains CoreAPI, node, and repo config; resolves each CLI option with config defaults from `Import`; validates inline limit, pin name, incompatible flags, hash function, metadata/raw-leaf conflicts, and MFS constraints. It wraps input files when requested, builds UnixFS add options, and iterates entries. For each entry it starts an add goroutine, streams CoreAPI add events into emitted `AddEvent`s with encoded CIDs, names, byte counts, mode, and mtime, then waits for the add error. Optional `--to-files` validates MFS destination, fetches the added DAG node, and writes it into MFS. After all entries, it optionally fast-provides the DAG or root CID unless only-hash disabled storage. Persistent effects include blockstore writes, pin records, MFS updates, and provider announcements.

Dependencies and integration points: Integrates config import/provide defaults, command environment, Boxo files/UnixFS/MFS/path, multihash, CID encoding, verifcid, progress bar, CoreAPI, blockstore/provider, and routing/provider subsystems.

Risks and test signals: This command has many CID-affecting options; config or default changes can break deterministic CIDs. `lastRootCid` and `fileAddedToMFS` are mutated by goroutines, though each add goroutine is drained before the next entry. MFS `toFilesStr` is mutated when empty. Fast-provide depends on provider availability and may be skipped/async. Progress size discovery races with output by design. Direct tests are not in this subset, so integration tests elsewhere are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bitswap.go -->
# Research: sources/distributed-fs/ipfs-kubo/core/commands/bitswap.go

Purpose: Implements Bitswap diagnostic and compatibility commands.

Important APIs/types/functions: `BitswapCmd` with subcommands `stat`, `wantlist`, `ledger`, and deprecated `reprovide`. `showWantlistCmd`, `bitswapStatCmd`, and `ledgerCmd` are the active implementations.

Control flow, state, and persistence: Wantlist command requires an online node, optionally decodes a peer ID, emits that peer's wantlist or the local wantlist, and text-encodes sorted CIDs. Stat command requires online node, gets `nd.Bitswap.Stat()`, and text-encodes block/data counters, duplicate data, wantlist, and optionally peers with human-readable sizes. Ledger decodes a peer ID and emits Bitswap ledger receipt for that peer. Deprecated reprovide aliases routing reprovide. No persistent state is modified except the aliased reprovide command may announce providers.

Dependencies and integration points: Uses command environment node access, Boxo Bitswap/stat/server receipt, CID encoder/sorting, humanize, and libp2p peer decode. Tied to online node Bitswap service.

Risks and test signals: Commands fail offline. Wantlist for self vs peer depends on peer ID equality. Verbose stat may expose peer IDs. No direct tests in this subset; behavior depends on Bitswap implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bitswap.go -->
