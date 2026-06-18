# subset-b-000191 Research

Grouped research for the mapped Moby daemon logging, network, container lifecycle, migration, and OCI spec files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/splunk/splunk_test.go -->
# sources/cloud-native/moby/daemon/logger/splunk/splunk_test.go

## Purpose
This file is the behavioral test suite for the Splunk HEC log driver. It validates configuration parsing, construction defaults, proxy handling, message formatting variants, compression, batching, retry buffering, connection verification, shutdown, and deadlock resistance.

## Important APIs, Types, And Functions
The tests exercise `ValidateLogOpt`, `New`, `logger.Logger.Log`, and `logger.Logger.Close` through concrete driver implementations such as `splunkLoggerInline`, `splunkLoggerJSON`, and `splunkLoggerRaw`. The test data uses `logger.Info` fields for container identity, labels, environment, and tag templates, and checks the resulting `splunkMessage` payloads recorded by the local HEC mock.

## Control Flow
Most tests start a `NewHTTPEventCollectorMock`, build `logger.Info`, call `New`, submit one or more `logger.Message` values, close the logger, and inspect mock HTTP state. The suite covers defaults, inline/json/raw formats, raw mode with labels and empty tags, batching by frequency and batch size, one-message-per-request compatibility, failed verification, skipped verification with later recovery, bounded buffers, permanently failing servers, log-after-close rejection, and blocked endpoint close completion.

## State, Persistence, And Dependencies
The state under test is in-memory driver state: URL path normalization, auth header, null/default Splunk message fields, gzip flags, stream channel capacity, batch settings from environment variables, retry buffers, and close markers. Dependencies include `net/http`, `compress/gzip`, `runtime`, `time`, `github.com/moby/moby/v2/daemon/logger`, and the package-local HEC mock.

## Integration Points
These tests define the contract between Docker's logger subsystem and Splunk HEC. They verify HEC endpoint path `/services/collector/event/1.0`, `Authorization: Splunk <token>`, optional proxy use through `HTTP_PROXY`, gzip request handling, log tag templating, Docker labels/env attribute inclusion, and fallback behavior when a HEC endpoint is unhealthy.

## Risks And Edge Cases
High-risk areas are asynchronous send loops, bounded buffers dropping old messages under sustained outage, flush-on-close behavior, and blocked HTTP requests causing `Close` to hang. Raw format explicitly drops whitespace-only events because HEC rejects empty events. Timing-sensitive frequency tests are relaxed on Windows due to slower scheduling.

## Test Signals
The suite is itself the primary signal. It asserts exact message counts, request counts, per-message timestamps, field values, event map/string content, gzip consistency, connection verification behavior, retry success, buffer eviction order, and a 60-second watchdog with stack dump for blocked close deadlocks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/splunk/splunk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/splunk/splunkhecmock_test.go -->
# sources/cloud-native/moby/daemon/logger/splunk/splunkhecmock_test.go

## Purpose
This file implements a local HTTP Event Collector test server used by Splunk logger tests. It records incoming HEC messages, simulates server failure or blocking, validates request headers and paths, and decodes optional gzip bodies.

## Important APIs, Types, And Functions
`HTTPEventCollectorMock` owns a TCP listener, token, request counters, connection verification flag, gzip mode, recorded `splunkMessage` slice, and failure/blocking controls. `NewHTTPEventCollectorMock`, `Serve`, `Close`, `ServeHTTP`, `simulateErr`, and `withBlock` are the main helpers. `splunkMessage.EventAsString` and `EventAsMap` give typed assertions for raw and structured events.

## Control Flow
The mock listens on localhost port 0. `ServeHTTP` increments request count, snapshots failure/blocking state under a mutex, optionally blocks until context cancellation, returns 500 when simulating errors, accepts one `OPTIONS` verification request, and handles `POST` by validating HEC path and authorization. It determines gzip use from `Content-Encoding`, decompresses when needed, reads the body, splits adjacent JSON objects, unmarshals each into `splunkMessage`, and responds 200.

## State, Persistence, And Dependencies
All state is in-memory and test-scoped. The mutex protects toggled error/block settings but message appends and counters are otherwise used in single-test request flows. Dependencies are standard `net`, `net/http`, `compress/gzip`, `encoding/json`, `io`, `sync`, `testing`, and `time`.

## Integration Points
The mock is tightly coupled to Splunk driver test expectations: exact HEC event path, Splunk auth token format, single verification request, stable gzip choice per logger, and concatenated JSON event bodies.

## Risks And Edge Cases
The body splitter assumes adjacent JSON objects can be separated at `}{`, which is sufficient for current driver output but not a general JSON stream parser. `ServeHTTP` reads `hec.blockingCtx` after unlocking instead of the local `ctx` variable, so future mutation could surprise blocked-request tests. `Close` only closes the listener and does not gracefully shut down the HTTP server.

## Test Signals
This helper enables strong assertions in `splunk_test.go`: captured `messages`, `numOfRequests`, `connectionVerified`, `gzipEnabled`, injected 500 responses, and blocked endpoint behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/splunk/splunkhecmock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/register.go -->
# sources/cloud-native/moby/daemon/logger/syslog/register.go

## Purpose
This file registers the syslog log driver with the daemon logging subsystem at package initialization time.

## Important APIs, Types, And Functions
The `init` function calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`. The registered constructor and validator are defined in `syslog.go`.

## Control Flow
Registration happens during package import. After registration, the daemon logger factory can instantiate the syslog driver by name and validate syslog-specific `log-opts`.

## State, Persistence, And Dependencies
The only state mutation is global registration inside the logger package. There is no persistence or runtime data structure in this file.

## Integration Points
The file connects package-local syslog implementation to Docker daemon log-driver discovery. Without it, daemon config using `--log-driver=syslog` would not resolve.

## Risks And Edge Cases
The registration relies on the shared `name` constant matching user-facing driver names and validator/constructor signatures. Duplicate registration would be detected by the logger package rather than here.

## Test Signals
No direct test file targets registration; indirect coverage comes from syslog option tests and daemon log config validation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/syslog.go -->
# sources/cloud-native/moby/daemon/logger/syslog/syslog.go

## Purpose
This file implements Docker's syslog log driver, including option validation, address parsing, facility parsing, TLS config construction, message formatting/framing selection, and log writes.

## Important APIs, Types, And Functions
`New(info logger.Info)` constructs a `syslogger` around a `srslog.Writer`. `syslogger.Log`, `Close`, and `Name` satisfy the logger interface. Helper functions include `parseAddress`, `ValidateLogOpt`, `parseFacility`, `parseTLSConfig`, `parseLogFormat`, and RFC5424 formatter variants that set the app-name/tag field for rsyslog compatibility.

## Control Flow
`New` parses the Docker log tag template, validates/deduces protocol and address, parses facility, selects formatter and framer, dials syslog with optional TLS, configures the writer, and returns the logger. `Log` drops empty lines, sends stderr through `writer.Err`, sends other streams through `writer.Info`, and returns pooled logger messages only on successful writes.

## State, Persistence, And Dependencies
Runtime state is just the `*syslog.Writer`. No daemon state is persisted here. Dependencies include RackSec `srslog`, Docker TLS config helpers, logger utilities, standard `net/url`, `net`, `os`, `tls`, `time`, and configured TLS cert/key/CA paths.

## Integration Points
The file integrates Docker logger configuration keys (`syslog-address`, `syslog-facility`, `syslog-format`, TLS options, common tag/env/label attrs) with local or remote syslog endpoints. For `tcp+tls`, RFC5424 formats use RFC5425 length framing; for UDP/TCP they use default framing.

## Risks And Edge Cases
Unix socket addresses are validated by `os.Stat`, so missing sockets fail during validation. TCP/UDP addresses without ports default to 514. TLS skip verification is enabled by the presence of `syslog-tls-skip-verify`, regardless of its string value. `parseFacility` accepts named facilities and numeric 0-23 values shifted into syslog priority space. Empty log lines are silently ignored.

## Test Signals
`syslog_test.go` covers formatter/framer mapping, empty configs, malformed/unsupported addresses, default port behavior, invalid facilities, invalid formats, accepted common attributes, and unknown option rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/syslog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/syslog_test.go -->
# sources/cloud-native/moby/daemon/logger/syslog/syslog_test.go

## Purpose
This file tests syslog driver parsing and validation behavior.

## Important APIs, Types, And Functions
Tests target `parseLogFormat`, `ValidateLogOpt`, and `parseAddress`; `functionMatches` compares function pointers to verify selected formatter and framer implementations.

## Control Flow
`TestParseLogFormat` checks RFC5424, RFC5424 microsecond, RFC3164, default, TLS framing, and invalid format cases. `TestValidateSyslogAddress` creates a temporary socket path, substitutes it into unix URLs, and verifies unsupported schemes, missing sockets, tcp/udp defaults, and platform skips. Other tests assert empty config validity, default port 514, invalid facility/format errors, accepted full option sets, and rejection of unsupported options.

## State, Persistence, And Dependencies
The only filesystem state is a temporary file used as a stand-in unix socket path. Dependencies include `testing`, `runtime`, `reflect`, `net`, `os`, `filepath`, `strings`, `log`, RackSec `srslog`, and logger constants.

## Integration Points
The tests encode user-facing `--log-opt` behavior and protect syslog's compatibility with TLS framing and Docker's shared logger attributes.

## Risks And Edge Cases
The unix socket validation is skipped or has different messages on Windows. The function-pointer comparison is exact and can fail if wrapper functions are introduced. Address tests validate syntax and stat behavior, not actual network dialing.

## Test Signals
The test suite gives focused coverage for validation paths but does not instantiate a real syslog server or assert `Log` write behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/syslog/syslog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/templates/templates.go -->
# sources/cloud-native/moby/daemon/logger/templates/templates.go

## Purpose
This file provides reusable template helpers for logger tag formatting.

## Important APIs, Types, And Functions
`basicFunctions` exposes `json`, `split`, `join`, `title`, `lower`, `upper`, `pad`, and `truncate` to Go text templates. `NewParse(tag, format)` attaches those functions to a template and parses the format. `padWithSpace` and `truncateWithLength` implement the custom formatting helpers.

## Control Flow
Callers invoke `NewParse` with a template name and format string. The JSON helper encodes without HTML escaping and trims the encoder newline. `pad` returns the original empty string unchanged and otherwise adds requested leading/trailing spaces. `truncate` returns the original string when shorter than the requested length and byte-slices otherwise.

## State, Persistence, And Dependencies
There is no mutable state. Dependencies are standard `text/template`, `encoding/json`, `bytes`, and `strings`.

## Integration Points
Logger packages use these helpers to build configurable log tags and structured strings from container metadata.

## Risks And Edge Cases
`strings.Title` is deprecated and has Unicode boundary limitations; the code explicitly tolerates that for compatibility. `truncate` is byte-based, not rune-aware, so non-ASCII strings can be cut mid-rune. The JSON helper ignores encode errors by design.

## Test Signals
`templates_test.go` only verifies basic parse and execution; helper-specific edge cases are not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/templates/templates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/templates/templates_test.go -->
# sources/cloud-native/moby/daemon/logger/templates/templates_test.go

## Purpose
This file provides a minimal smoke test for logger template parsing and execution.

## Important APIs, Types, And Functions
`TestNewParse` calls `NewParse("foo", "this is a {{ . }}")`, executes the template with a string, and compares the rendered output.

## Control Flow
The test parses, executes into a `bytes.Buffer`, then asserts no parse/execute error and exact output `this is a string`.

## State, Persistence, And Dependencies
No persistent state. Dependencies include `bytes`, `testing`, and `gotest.tools/v3/assert`.

## Integration Points
The test verifies the template wrapper is usable by logger tag formatting code, but does not cover the custom function map.

## Risks And Edge Cases
Coverage is intentionally shallow; JSON, split/join, case conversion, padding, truncation, and malformed templates are not tested.

## Test Signals
The file confirms the happy path for `NewParse`; deeper behavior depends on consumers or future targeted tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/templates/templates_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logs.go -->
# sources/cloud-native/moby/daemon/logs.go

## Purpose
This file implements daemon-side container log retrieval and log config merging/validation.

## Important APIs, Types, And Functions
`Daemon.ContainerLogs` returns a channel of `backend.LogMessage` values and TTY status. `getLogger` retrieves the live container logger or starts a read-only logger for stopped containers. `mergeAndVerifyLogConfig` and `defaultLogConfig` merge daemon defaults and validate driver-specific options.

## Control Flow
`ContainerLogs` starts a trace span, validates stdout/stderr selection, resolves the container, rejects removal/dead state and `none` driver reads, obtains a logger, verifies it implements `logger.LogReader`, parses tail, and calls `ReadLogs`. It then launches a goroutine that forwards log messages or errors to a buffered channel until log streams close or context is canceled, while closing temporary loggers and marking `ConsumerGone`.

## State, Persistence, And Dependencies
The function reads container state under existing daemon/container abstractions and may create a temporary logger. It does not directly persist state. `mergeAndVerifyLogConfig` mutates the provided `LogConfig`, filling default type/config and merging cache-related defaults before validation.

## Integration Points
The file bridges API log requests (`backend.ContainerLogsOptions`) to logger drivers, container state, tracing, daemon default log config, and `logger.ValidateLogOpts`.

## Risks And Edge Cases
Follow mode is disabled when a new logger is created for a stopped container. Error forwarding copies only the error to avoid partial data. Channel sends are guarded by context cancellation to avoid blocking forever. If `StartLogger` returns an error after creating resources, the code marks `created=true` and notes a possible resource leak TODO.

## Test Signals
`logs_test.go` only covers nil per-container log config map merging. Broader behavior relies on integration tests around log streaming and individual driver tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logs_test.go -->
# sources/cloud-native/moby/daemon/logs_test.go

## Purpose
This file tests one regression path in daemon log configuration merging.

## Important APIs, Types, And Functions
`TestMergeAndVerifyLogConfigNilConfig` constructs a daemon with default `json-file` log config and calls `mergeAndVerifyLogConfig`.

## Control Flow
The test passes a `LogConfig` with the default type but nil `Config` map, expecting the method to allocate/merge defaults and validate successfully.

## State, Persistence, And Dependencies
No persistent state. It mutates the local `cfg` and uses Docker container API types.

## Integration Points
This protects container create/update paths where the caller supplies a log driver type but omits an option map.

## Risks And Edge Cases
The test is narrow; it does not inspect the final map contents or cover non-default drivers, invalid options, or logcache-specific defaults.

## Test Signals
Passing the test proves `mergeAndVerifyLogConfig` no longer panics or errors for nil `Config` when daemon defaults contain options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/migration.go -->
# sources/cloud-native/moby/daemon/migration.go

## Purpose
This file migrates older persisted container platform/OS metadata into `Container.ImagePlatform`, using image manifests, content store config blobs, image service metadata, and host defaults as fallbacks.

## Important APIs, Types, And Functions
`migrateContainerOS` updates a container in place. `deduceContainerPlatform` returns the best platform or an aggregated error. `platformReader` abstracts platform lookup. `daemonPlatformReader` implements it with `ImageService` and containerd `content.Provider`.

## Control Flow
For pre-OS containers with no deprecated `OS` and no `ImageManifest`, the default host platform is returned. If `ImageManifest.Platform` is set, it wins. Otherwise the manifest blob is read, its config descriptor is read, and the config is unmarshaled as an OCI platform. If that fails or is malformed, the image service is queried by `ImageID`. If all paths fail, errors are joined and wrapped. `migrateContainerOS` logs a warning and preserves the deprecated OS value as `ImagePlatform.OS` on failure.

## State, Persistence, And Dependencies
The function mutates only the in-memory container; persistence occurs later through normal container checkpointing. Dependencies include containerd content reads, OCI image descriptors/manifests, Docker image service, `platforms.DefaultSpec`, and internal multierror aggregation.

## Integration Points
This migration supports daemon restore across image store formats, graphdriver/containerd image store differences, and legacy containers created before platform metadata existed.

## Risks And Edge Cases
If an image ID points to a multi-platform image index rather than a platform-specific manifest, fallback lookup may choose a host-preferred platform rather than the original platform. Missing content store support returns an error for manifest-based deduction. Malformed config with missing OS or architecture is treated as invalid.

## Test Signals
`migration_test.go` covers graphdriver nil manifests, pre-OS defaulting, Linux/Windows image IDs, missing images, containerd manifest lookup, fallback to image ID, and priority of `ImageManifest` over `ImageID`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/migration_test.go -->
# sources/cloud-native/moby/daemon/migration_test.go

## Purpose
This file tests container platform migration logic using a mock platform reader.

## Important APIs, Types, And Functions
`mockPlatformReader` implements `ReadPlatformFromImage` and `ReadPlatformFromConfigByImageManifest`, mapping synthetic image IDs/digests to platforms or errors. `TestContainerMigrateOS` invokes `migrateContainerOS` for table-driven cases.

## Control Flow
Each case creates a container with combinations of deprecated `OS`, `ImageID`, and `ImageManifest`. The migration is run and `ctr.ImagePlatform` is compared to the expected platform.

## State, Persistence, And Dependencies
Only local container structs are mutated. Dependencies include `container.Container`, internal `image.ID`, OCI platform types, containerd platform defaults, and gotest assertions.

## Integration Points
The test captures migration compatibility across graphdriver and containerd image stores, including malformed/missing platform paths.

## Risks And Edge Cases
The mock abstracts away actual manifest JSON/content-store behavior, so it tests decision order rather than blob parsing. The test intentionally tolerates fallback to host default for a multi-platform image ID.

## Test Signals
Coverage includes pre-OS fallback, successful platform reads, missing images preserving OS-only information, ImageManifest priority, and fallback from missing manifest to image lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/monitor.go -->
# sources/cloud-native/moby/daemon/monitor.go

## Purpose
This file handles containerd lifecycle events for containers and exec processes, updates Docker container state, checkpoints state, emits events, restarts containers, and handles auto-removal.

## Important APIs, Types, And Functions
Key methods are `setStateCounter`, `handleContainerExit`, `ProcessEvent`, `autoRemove`, and `shouldIgnoreExitEventWithLock`. It uses container state, restart manager, containerd task/process APIs, health monitor hooks, metrics, backend removal config, and event logging.

## Control Flow
`ProcessEvent` resolves the container and switches on event type. OOM marks `OOMKilled` and checkpoints. Main process exit delegates to `handleContainerExit`; exec exit updates `ExecConfig`, closes streams, deletes the process asynchronously, and emits `exec_die`. Start/pause/resume external events update state, health, metrics, checkpoints, and Docker events. `handleContainerExit` ignores networking setup failures and duplicate exits, deletes the task, waits briefly for streams, resets state, chooses restart behavior, cleans up resources, checkpoints, emits `die`, and optionally schedules restart after the restart-manager wait channel.

## State, Persistence, And Dependencies
The file mutates `container.State`, `RestartCount`, exec command stores, health monitor state, metrics counters, stream state, and container checkpoints through `CheckpointTo`. It also calls daemon cleanup, container removal, and container start paths. Dependencies include containerd client/error/status types, Docker event/action constants, restartmanager, and daemon config.

## Integration Points
This is a central integration point between containerd events and Docker's persisted container model, API-visible state, event stream, metrics, restart policy, health checks, and auto-remove behavior.

## Risks And Edge Cases
Duplicate exit events are hard to classify; the code checks current state and live task status instead of timestamps because system time can move backward. Restart processing uses goroutines and must handle daemon startup completion, shutdown, manual stops/restarts, and failed restarts. Lock ordering is important: `autoRemove` is deferred until after unlocking. External starts may race with non-Docker task deletion and handle NotFound specially.

## Test Signals
No direct tests are in this work item. Behavior is likely covered by daemon lifecycle integration tests. The code has explicit logging around duplicate exits, cleanup failures, and restart errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/mounts.go -->
# sources/cloud-native/moby/daemon/mounts.go

## Purpose
This file prepares persisted mount-point state before container use and releases/removes volume and image mounts during cleanup.

## Important APIs, Types, And Functions
`Daemon.prepareMountPoints` lazy-initializes volumes, restores image mount layers, and live-restores volumes for running containers. `Daemon.removeMountPoints` releases volume references, removes anonymous volumes when requested, unmounts image layers, and releases image layers.

## Control Flow
Preparation iterates all mount points, initializes each volume, restores missing image layers from `imageService.GetLayerByID`, skips non-volume mount points, and calls `LiveRestore` for volumes on already-running containers. Removal iterates mount points, releases volume refs, optionally removes anonymous volumes while ignoring in-use errors, then unmounts and releases image layers or records a missing-layer error.

## State, Persistence, And Dependencies
The code mutates mount point runtime references (`Layer`, live-restored volume state) and affects volume/image-layer reference counts through volume service and image service. Errors are aggregated as strings and returned as one formatted error.

## Integration Points
This file connects container restore/removal paths with daemon volume service, image service, mount API types, and live-restore behavior.

## Risks And Edge Cases
Named volumes are never removed even when `rm` is true. Anonymous volume removal ignores in-use errors to avoid noisy failure when shared with other containers. Missing image layer references become cleanup errors. Live restore only runs for containers whose state says running.

## Test Signals
No direct tests in this item. Indirect coverage comes from container restore/removal and volume/image mount integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/mounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/names.go -->
# sources/cloud-native/moby/daemon/names.go

## Purpose
This file manages container name generation, validation, reservation, conflict handling, and release.

## Important APIs, Types, And Functions
Methods include `registerName`, `generateIDAndName`, `reserveName`, `releaseName`, and `generateAndReserveName`. It uses `containersReplica.ReserveName`, `ReleaseName`, `Snapshot().GetID`, `stringid.GenerateRandomID`, `stringid.TruncateID`, and `namesgenerator.GetRandomName`.

## Control Flow
`registerName` rejects empty IDs and already-loaded containers, generates a name if missing, or reserves the persisted name. `generateIDAndName` creates an ID and either generates/reserves a random name or reserves the requested name. `reserveName` validates name characters after trimming a leading slash, ensures a leading slash, reserves it, and converts conflicts into `nameConflictError` with the existing container ID. `generateAndReserveName` tries six generated names before falling back to the truncated container ID.

## State, Persistence, And Dependencies
Name state is maintained in the daemon's `containersReplica` reservation index and later persisted by container metadata. There is no direct disk write here. Dependencies include containerd conflict detection, name regex from `daemon/names`, random Docker name generator, and errdefs invalid parameter errors.

## Integration Points
This file is used by container create and restore paths to preserve globally unique container names across daemon state.

## Risks And Edge Cases
Name validation allows a single-character alphanumeric name and subsequent alphanumeric/underscore/dot/hyphen characters. Conflict handling does an extra lookup that can itself fail. Fallback to truncated ID can still conflict if replica state is corrupt.

## Test Signals
No direct tests in this item. Behavior is historically covered by container create/name conflict integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/names/names.go -->
# sources/cloud-native/moby/daemon/names/names.go

## Purpose
This small package defines the shared restricted-name pattern for container and volume names.

## Important APIs, Types, And Functions
`RestrictedNameChars` is the regex fragment `[a-zA-Z0-9][a-zA-Z0-9_.-]`. `RestrictedNamePattern` lazily compiles `^` + fragment + `+$`.

## Control Flow
Consumers call `RestrictedNamePattern.MatchString` to validate names. Lazy compilation defers regex construction until first use.

## State, Persistence, And Dependencies
The only state is the lazy compiled regex. Dependency is Docker's internal `lazyregexp`.

## Integration Points
`daemon/names.go` imports this package for container name validation, and comments indicate volume naming also uses the same rules.

## Risks And Edge Cases
The fragment plus trailing `+` means at least one initial alphanumeric char and zero or more allowed continuation chars. Names must be trimmed of any leading slash by callers before matching.

## Test Signals
No direct tests in this item; validation is exercised by name reservation/create tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/names/names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network.go -->
# sources/cloud-native/moby/daemon/network.go

## Purpose
This file implements daemon network management: lookup, create/delete, swarm ingress handling, plugin refcounting, IPAM validation/conversion, network listing/inspection projection, attachable cleanup, endpoint option construction, port mapping extraction, endpoint info persistence, and join options.

## Important APIs, Types, And Functions
Major APIs include `NetworkController`, `FindNetwork`, `GetNetworkByID`, `GetNetworkByName`, `CreateNetwork`, `createNetwork`, `DeleteNetwork`, `GetNetworks`, `GetNetworkSummaries`, `buildNetworkResource`, `buildCreateEndpointOptions`, `buildPortsRelatedCreateEndpointOptions`, `buildEndpointInfo`, and `buildJoinOptions`. `PredefinedNetworkError` is a forbidden error for attempts to create predefined networks. `ingressJob` and global ingress worker variables serialize ingress network operations.

## Control Flow
Network lookup scans libnetwork state by full ID, full name, or unambiguous partial ID. Creation runs in the network namespace, rejects predefined networks, resolves default driver, forbids non-manager overlay creation unless agent-driven, merges default driver options, resolves IPv4/IPv6 flags, validates and converts IPAM, appends internal/agent/config options, optionally attaches LB endpoint IPs, calls `libnetwork.NewNetwork`, acquires plugin refs, and emits create events. Deletion validates predefined/dynamic rules, calls `nw.Delete`, releases plugin refs, and emits destroy events. Listing filters networks and builds API resources including containers, services, peers, IPAM, and optional status.

## State, Persistence, And Dependencies
Persistent network state is owned by libnetwork. This file mutates plugin refcounts, cluster attachment store usage, container network settings, and daemon/network events. Dependencies include libnetwork controller/network/endpoint APIs, swarm cluster provider, networkdb peer info, driver/IPAM plugin endpoints, Docker API network/container types, filters, netip utilities, and OpenTelemetry baggage for ingress setup.

## Integration Points
This is the main integration boundary between Docker daemon API methods, swarm-managed networks, libnetwork, plugin management, network filters, container network settings, port mappings, endpoint driver info, and daemon events.

## Risks And Edge Cases
IPAM validation rejects host bits, out-of-subnet gateways/aux addresses, mismatched address families, and IP ranges larger than their subnet, but agent-created existing swarm networks log and continue for upgrade compatibility. `FindNetwork` must preserve libnetwork `ErrNoSuchNetwork` wrapping for controller retry behavior. Port mapping options are skipped for internal networks or sandboxes already carrying port map info. Build functions tolerate missing endpoint info. Ingress operations rely on global worker state and stale ID cleanup.

## Test Signals
`network_test.go` directly covers IPAM validation edge cases. `network/filter_test.go` covers filtering used by list/prune paths. Broader create/delete/endpoint behavior depends on daemon integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/filter.go -->
# sources/cloud-native/moby/daemon/network/filter.go

## Purpose
This file defines network list and prune filtering logic.

## Important APIs, Types, And Functions
`Filter` wraps `filters.Args` plus derived fields for dangling/use and until time. `FilterNetwork` abstracts the network data required for matching. Constructors are `NewFilter` and `NewPruneFilter`; matching helpers are `Matches`, `matchesUse`, `validateNetworkTypeFilter`, and `matchesType`.

## Control Flow
Constructors validate accepted filter keys, parse the optional single `dangling` boolean, validate `type` values, and parse a single `until` timestamp. Prune filters implicitly require dangling-only results. `Matches` applies driver, name, id, label, negative label, scope, use/dangling, type, and until checks in sequence.

## State, Persistence, And Dependencies
The filter is immutable after construction except for the exported `IDAlsoMatchesName` compatibility flag. There is no persistence. Dependencies include internal `filters`, timestamp parsing, errdefs, and predefined network detection.

## Integration Points
Daemon network list and prune flows pass libnetwork-backed values through this filter. The interface keeps filter matching decoupled from concrete libnetwork types.

## Risks And Edge Cases
`dangling` and `until` allow only one value. Network `type=builtin` maps to predefined names, while `custom` means not predefined. The `IDAlsoMatchesName` flag lets id filters also match names for compatibility and can broaden results substantially.

## Test Signals
`filter_test.go` exercises accepted/rejected filters, dangling semantics, label and negative label behavior, type/scope/name/id matching, prune restrictions, ID/name overlap, and until timestamp cutoffs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/filter_test.go -->
# sources/cloud-native/moby/daemon/network/filter_test.go

## Purpose
This file tests daemon network filter behavior on non-Windows platforms.

## Important APIs, Types, And Functions
`mockFilterNetwork` implements `FilterNetwork`. `TestFilter` drives `NewFilter`, `NewPruneFilter`, and `Filter.Matches` through a table of built-in, custom, attached, labeled, and dated mock networks.

## Control Flow
Each case constructs filter args, chooses list or prune filter construction, optionally enables `IDAlsoMatchesName`, asserts expected construction errors, then collects matched network names and compares them to expected results.

## State, Persistence, And Dependencies
All state is local test data. Dependencies include Docker API network constants, internal filters, `time`, and gotest assertions.

## Integration Points
The tests encode API-visible behavior for `docker network ls --filter` and network prune filtering.

## Risks And Edge Cases
The test is build-tagged `!windows`, matching platform differences in predefined network semantics. The mock data intentionally uses ROT13-like IDs and overlapping names to expose `id` matching behavior.

## Test Signals
Coverage includes empty filters, exact driver/scope, builtin/custom type, invalid type, dangling true/false values and duplicates, labels and negative labels, invalid unsupported prune keys, relative/absolute until values, ID matching with/without name fallback, and prune's implicit dangling behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode.go -->
# sources/cloud-native/moby/daemon/network/network_mode.go

## Purpose
This file exposes platform-independent network mode constants and predefined-network checks for the daemon network package.

## Important APIs, Types, And Functions
`DefaultNetwork` aliases the platform-specific `defaultNetwork`. `IsPredefined(network string)` delegates to the platform-specific `isPreDefined`.

## Control Flow
At compile time, Unix or Windows companion files provide the default network name and predefined logic. Consumers call this file's stable API regardless of platform.

## State, Persistence, And Dependencies
No mutable state or persistence. It depends only on the platform-specific files in the same package.

## Integration Points
Daemon network creation, deletion, filtering, and use/dangling checks rely on `IsPredefined` and `DefaultNetwork`.

## Risks And Edge Cases
The TODO notes predefined checks are not fully aligned across platforms, so callers must expect Windows and Unix differences.

## Test Signals
Platform behavior is indirectly covered by network filter and daemon network tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode_unix.go -->
# sources/cloud-native/moby/daemon/network/network_mode_unix.go

## Purpose
This non-Windows file defines Docker's Unix default network and predefined network detection.

## Important APIs, Types, And Functions
`defaultNetwork` is `network.NetworkBridge`. `isPreDefined` converts the name to `container.NetworkMode` and returns true for bridge, host, none, or default.

## Control Flow
The function is a simple predicate used through `IsPredefined`.

## State, Persistence, And Dependencies
No state or persistence. Dependencies are Docker API container and network type constants.

## Integration Points
Unix daemon network create/delete/filter behavior uses this definition to protect built-in networks and classify filters.

## Risks And Edge Cases
`NetworkMode.IsDefault()` is treated as predefined along with explicit bridge/host/none. User-defined networks that share unexpected aliases could be affected by `NetworkMode` semantics.

## Test Signals
`filter_test.go` relies on host/bridge/none being builtin on non-Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode_windows.go -->
# sources/cloud-native/moby/daemon/network/network_mode_windows.go

## Purpose
This Windows file defines Docker's Windows default network and predefined network detection.

## Important APIs, Types, And Functions
`defaultNetwork` is `network.NetworkNat`. `isPreDefined` returns true for any `container.NetworkMode` that is not user-defined.

## Control Flow
The predicate delegates to `container.NetworkMode(network).IsUserDefined()`, negating the result.

## State, Persistence, And Dependencies
No mutable state or persistence. Dependencies are Docker API container and network type constants.

## Integration Points
Windows daemon network create/delete/filter behavior uses this broader predefined definition.

## Risks And Edge Cases
The Windows predicate is broader than Unix and may classify more modes as predefined. The shared wrapper notes a TODO to align platform behavior.

## Test Signals
No tests in this subset target the Windows implementation directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/network_mode_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/settings.go -->
# sources/cloud-native/moby/daemon/network/settings.go

## Purpose
This file defines daemon-persisted network settings for containers and an attachment store for swarm load-balancer IPs.

## Important APIs, Types, And Functions
`Settings` stores sandbox IDs/keys, endpoint settings, service config, ports, and swarm endpoint state. `EndpointSettings` wraps API endpoint settings with internal fields `IPAMOperational` and `DesiredMacAddress`. `AttachmentStore` maps network IDs to LB IPs with methods `ResetAttachments`, `ClearAttachments`, `clearAttachments`, and `GetIPForNetwork`.

## Control Flow
`ResetAttachments` locks the store, clears existing state, parses each CIDR string, stores parsed IPs by network ID, and resets to an empty map on parse failure. `ClearAttachments` and `GetIPForNetwork` are mutex-protected. `clearAttachments` initializes the map.

## State, Persistence, And Dependencies
`Settings` is persisted as part of container network state; `AttachmentStore` is in-memory daemon/cluster state. Dependencies include API network types, cluster service config, `net`, `sync`, and errors wrapping.

## Integration Points
`network.go` uses `AttachmentStore.GetIPForNetwork` when creating agent overlay networks with load-balancer endpoints. Container networking code uses `Settings.Networks` to build endpoint options and persist endpoint info.

## Risks And Edge Cases
On any CIDR parse error, `ResetAttachments` discards all attachment mappings. `GetIPForNetwork` returns the stored `net.IP` slice directly, so callers should not mutate it. The comment notes Windows-specific factoring is incomplete.

## Test Signals
No direct tests in this item; behavior is covered indirectly by swarm networking paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network/settings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network_test.go -->
# sources/cloud-native/moby/daemon/network_test.go

## Purpose
This file tests validation of network IPAM configuration.

## Important APIs, Types, And Functions
`TestValidateIPAM` calls unexported `validateIpamConfig` with table-driven `network.IPAMConfig` inputs and expected error substrings.

## Control Flow
Each subtest runs in parallel, calls validation with IPv6 enabled/disabled flags, expects nil for valid cases, or asserts the joined error contains `invalid network config` and each detailed expected error.

## State, Persistence, And Dependencies
No persistent state. Dependencies include `net/netip`, Docker API network types, and gotest assertions.

## Integration Points
The tests protect `CreateNetwork` validation behavior for IPv4/IPv6 IPAM input supplied through Docker API/CLI.

## Risks And Edge Cases
Tests include IPv6 subnet ignored when IPv6 is disabled for upgrade compatibility, mismatched address families, IP ranges larger than subnets, host bits in subnet/IP range, out-of-range gateways/aux addresses, empty IPAM, and a valid case.

## Test Signals
Strong focused signal for IPAM validation error messages and multierror aggregation; it does not cover conversion into libnetwork IPAM config.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/network_windows.go -->
# sources/cloud-native/moby/daemon/network_windows.go

## Purpose
This Windows-specific daemon file resolves a container endpoint within a libnetwork network.

## Important APIs, Types, And Functions
`getEndpointInNetwork(name string, n *libnetwork.Network)` trims a leading slash from the container name and calls `n.EndpointByName`.

## Control Flow
The function normalizes Docker's slash-prefixed container names to endpoint names, then delegates lookup to libnetwork.

## State, Persistence, And Dependencies
No state or persistence. Dependencies are `strings` and daemon `libnetwork`.

## Integration Points
`oci_windows.go` uses this helper while building Windows OCI network endpoint lists from container network settings.

## Risks And Edge Cases
If endpoint names diverge from trimmed container names, spec generation silently skips endpoints at the caller. Errors are propagated to the immediate caller there but often continued over.

## Test Signals
No direct tests in this item.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/network_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_linux.go -->
# sources/cloud-native/moby/daemon/oci_linux.go

## Purpose
This file assembles Linux OCI runtime specs for containers by composing containerd OCI `SpecOpts` for identity, rootfs, mounts, namespaces, resources, devices, security labels, capabilities, cgroups, sysctls, init, rootless mode, and snapshotter metadata.

## Important APIs, Types, And Functions
Major spec options include `withRlimits`, `withRootless`, `withRootfulInRootless`, `WithOOMScore`, `WithSelinux`, `WithApparmor`, `WithCapabilities`, `WithNamespaces`, `withMounts`, `withCommonOptions`, `withCgroups`, `WithDevices`, `WithResources`, `WithSysctls`, and `WithUser`. Helpers include `getUser`, `setNamespace`, `specMapping`, `getSourceMount`, `ensureShared`, `ensureSharedOrSlave`, `sysctlExists`, `clearReadOnly`, and `mergeUlimits`. `Daemon.createSpec` orchestrates the option list.

## Control Flow
`createSpec` starts from `oci.DefaultSpec`, appends spec options in a deliberate order, conditionally adds no-new-privileges, console size, masked/readonly path overrides, rootless/rootful-in-rootless conversion, and snapshotter identifiers, then applies options. `withCommonOptions` sets root path, working directory, args/init, env, terminal, hostname/domain sysctl, and safe network sysctls. `WithNamespaces` configures user, network, IPC, PID, UTS, time, and cgroup namespaces based on host config and daemon support. `withMounts` filters default mounts overridden by user mounts, adds tmpfs/bind mounts, verifies propagation, handles recursive read-only support, userns mount flags, read-only rootfs propagation, privileged `/sys` behavior, and writable cgroup rules.

## State, Persistence, And Dependencies
The file mutates only the in-memory OCI spec and occasionally container working-directory filesystem state. It reads daemon config, container host config, rootless/userns state, sysctls under `/proc/sys`, mountinfo, cgroup mode, AppArmor state, CDI/device drivers, and image snapshotter information. Persistence of the spec is handled by containerd, not this file.

## Integration Points
This is a central Linux integration layer between Docker container config and containerd/runc OCI specs. It touches daemon config defaults, rootless conversion, AppArmor/SELinux/seccomp, cgroups, resource conversion helpers, device handling, CDI injection, mount parsing, volume mount output, user/group lookup inside rootfs, and containerd snapshots.

## Risks And Edge Cases
Namespace sharing with a container while user namespaces are enabled can overwrite an earlier user namespace path, as noted by FIXME. Mount propagation must match source mount state; daemon-root fallback preserves backward compatibility only for implicit propagation. Recursive read-only support can downgrade to plain `ro` unless forced. Writable cgroups conflict with rootless/userns. Default sysctls are conditional on network mode, userns, current kernel files, and explicit user sysctls. Privileged mode clears readonly/masked paths and cgroup restrictions.

## Test Signals
`oci_linux_test.go` covers CDI additional GID preservation, `/dev/shm` tmpfs duplication, private IPC with read-only rootfs, sysctl override precedence and host network suppression, source mount lookup, and default resources being unset/empty.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_linux_test.go -->
# sources/cloud-native/moby/daemon/oci_linux_test.go

## Purpose
This file tests selected Linux OCI spec assembly regressions and helper behavior.

## Important APIs, Types, And Functions
`setupFakeDaemon` creates a temporary rootfs, libnetwork controller, and fake image service. Tests exercise `Daemon.createSpec`, `getSourceMount`, `sysctlExists`-conditioned sysctls, and resource defaults. `fakeImageService.StorageDriver` supports snapshotter-related paths.

## Control Flow
Tests construct minimal containers/daemon state, call `createSpec`, and inspect the resulting spec. Root-only tests are skipped for non-root users. Cleanup detaches leaked `/dev/shm` mounts. CDI test registers a temporary CDI device definition and verifies additional GIDs are preserved after user setup and device injection.

## State, Persistence, And Dependencies
The tests create temp directories, libnetwork data dirs, optional mounts, and mutate package-level `deviceDrivers` around CDI registration. Dependencies include libnetwork, config store, container API types, OCI specs, Unix unmount, and gotest assertions/skips.

## Integration Points
These tests protect OCI spec interactions among CDI, tmpfs, IPC, read-only rootfs, sysctls, user namespace settings, mountinfo, and default resource structs.

## Risks And Edge Cases
Several tests require root because spec assembly can mount or inspect privileged paths. The cleanup loop repeatedly detaches `ShmPath` to handle over-mounts. Sysctl assertions depend on kernel support files existing.

## Test Signals
Coverage is regression-focused: CDI supplementary group preservation, no duplicate `/dev/shm`, `/dev/shm` not made read-only under read-only rootfs, explicit sysctls overriding implicit ones, host network suppressing implicit network sysctls, `getSourceMount("/")`, and empty/default resource structures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_opts.go -->
# sources/cloud-native/moby/daemon/oci_opts.go

## Purpose
This file defines a small OCI spec option for initial TTY console sizing.

## Important APIs, Types, And Functions
`WithConsoleSize(c *container.Container)` returns a containerd OCI `SpecOpts` closure.

## Control Flow
When either configured console dimension is greater than zero, the closure ensures `s.Process` exists and sets `s.Process.ConsoleSize` from `HostConfig.ConsoleSize[0]` height and `[1]` width.

## State, Persistence, And Dependencies
It mutates only the in-memory OCI spec. Dependencies include containerd OCI option types, container model, and runtime-spec `specs.Box`.

## Integration Points
`oci_linux.go` appends this option when `c.Config.Tty` is true, so terminal containers can receive an initial size.

## Risks And Edge Cases
Zero dimensions are ignored. The function assumes the host config array indexes follow Docker's height/width convention.

## Test Signals
No direct tests in this item; behavior is covered indirectly by OCI spec creation tests or TTY integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_utils.go -->
# sources/cloud-native/moby/daemon/oci_utils.go

## Purpose
This file maps Docker's Linux domainname configuration into an OCI-compatible sysctl.

## Important APIs, Types, And Functions
`setLinuxDomainname(c *container.Container, s *specs.Spec)` ensures `s.Linux.Sysctl` exists and sets `kernel.domainname` when `c.Config.Domainname` is non-empty.

## Control Flow
The function lazily initializes `s.Linux` and `s.Linux.Sysctl`, then writes the sysctl. It is called by `withCommonOptions`.

## State, Persistence, And Dependencies
Only the in-memory OCI spec is mutated. Dependencies are Docker container config and runtime-spec types.

## Integration Points
OCI has no explicit NIS domainname field, so Linux daemon spec generation relies on this sysctl to match `setdomainname(2)` behavior.

## Risks And Edge Cases
Explicit host config sysctls are merged later by `WithSysctls` and intentionally override this implicit value. The helper is Linux-specific.

## Test Signals
`oci_linux_test.go` verifies implicit domainname sysctl creation and explicit override behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_windows.go -->
# sources/cloud-native/moby/daemon/oci_windows.go

## Purpose
This file assembles Windows OCI runtime specs and handles Windows-specific container directories, Hyper-V isolation, HNS endpoint lists, credential specs, resource limits, backing device paths, and device assignments.

## Important APIs, Types, And Functions
Key methods/functions include `setupContainerDirs`, `isHyperV`, `createSpec`, `createSpecWindowsFields`, `escapeArgs`, `getBackingDeviceForContainerdMount`, `setWindowsCredentialSpec`, `setResourcesInSpec`, `readCredentialSpecRegistry`, `readCredentialSpecFile`, `setupWindowsDevices`, and no-op Windows `getUser`/`mergeUlimits`.

## Control Flow
`setupContainerDirs` prepares secret/config dirs, mounts Hyper-V rootfs only when needed for first-start symlink creation, and returns secret/config mounts. `createSpec` validates image OS, starts from default Windows spec, applies annotations and mounts, sets process env/CWD/TTY/user, computes layer folders, gathers HNS endpoint IDs and gateway endpoint IDs from libnetwork driver info, handles shared network containers, sets DNS search, then delegates Windows fields. `createSpecWindowsFields` sets hostname, default CWD, command line vs args, root path/backing device for process-isolated snapshotter containers, boot optimization, resources, credential spec, and Windows devices.

## State, Persistence, And Dependencies
The file mutates only the spec and prepares container filesystem symlinks for secrets/configs. It reads daemon root, image service, dependency store configs, Windows registry, credential spec files under daemon root, alternate data streams from containerd mounts, hcsshim layer paths, runtime CPU count, and HNS driver metadata.

## Integration Points
This is the Windows counterpart to Linux OCI creation, integrating Docker container config with containerd/HCS, image layers, libnetwork/HNS, Swarm config-backed credential specs, registry/file/raw credential specs, Windows resource controls, and Windows device syntax.

## Risks And Edge Cases
Credential spec parsing silently lets the last valid `credentialspec` option win but rejects unknown malformed options. `file://` credential specs must be relative and remain under the daemon credential spec directory. `config://` is accepted only for swarm-managed containers with a dependency store. Backing device extraction depends on containerd's Windows alternate data stream implementation. Endpoint gathering skips networks/endpoints/driver info that cannot be found. Windows rootfs cannot be read-only.

## Test Signals
`oci_windows_test.go` covers credential spec no-op cases, file/registry/config/raw success, path traversal/absolute path rejection, missing file/registry errors, case-insensitive option names, unsupported option/scheme rejection, empty values, registry mocking, and Windows device mapping validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_windows_test.go -->
# sources/cloud-native/moby/daemon/oci_windows_test.go

## Purpose
This file tests Windows credential spec handling and Windows device mapping conversion.

## Important APIs, Types, And Functions
`TestSetWindowsCredentialSpecInSpec` targets `Daemon.setWindowsCredentialSpec`. `dummyRegistryKey` and `setRegistryOpenKeyFunc` mock registry access. `TestSetupWindowsDevices` targets `setupWindowsDevices`.

## Control Flow
Credential spec tests create a temporary daemon root, define a container factory for security options, create a credential spec file, and run subtests for no options, file, registry, swarm config, raw, malformed, unsupported, and empty values. Registry tests replace the package-level opener and restore it afterward. Device tests feed valid and invalid `DeviceMapping.PathOnHost` syntaxes and compare generated `specs.WindowsDevice` entries.

## State, Persistence, And Dependencies
The tests create temporary files under a fake daemon root and mutate the package-level `registryOpenKeyFunc` within cleanup. Swarm dependency manager state is created for `config://` tests. Dependencies include Windows registry package, swarmkit agent/API, gotest filesystem/assertions, and runtime-spec types.

## Integration Points
The tests protect API behavior for `--security-opt credentialspec=...` and `--device` on Windows containers.

## Risks And Edge Cases
Tests assert `config://` is hidden from non-swarm containers by returning the generic invalid-credential-spec error. File path validation covers absolute paths and breakout attempts. Multiple security options behavior is noted in production code but not deeply tested here.

## Test Signals
Coverage is strong for credential spec parsing/storage sources and device syntax. It does not instantiate full Windows OCI specs or HCS.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/oci_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pause.go -->
# sources/cloud-native/moby/daemon/pause.go

## Purpose
This file implements container pause operations for the daemon.

## Important APIs, Types, And Functions
`ContainerPause(name string)` resolves a container and calls `containerPause`. `containerPause` checks running task state, paused/restarting conflicts, invokes containerd task `Pause`, updates Docker state, metrics, health monitor, event log, and checkpoint.

## Control Flow
The public method gets the container by name/ID. The internal method locks the container, obtains a running task, rejects already paused or restarting containers, calls `tsk.Pause`, sets `State.Paused`, updates counters and health monitor, emits a pause event, and checkpoints state using `context.WithoutCancel`.

## State, Persistence, And Dependencies
The method mutates `container.State.Paused`, metrics, health monitor state, daemon event stream, and persisted container metadata through `CheckpointTo`. Dependencies include containerd task pause, Docker events, errdefs conflict errors, and daemon container lookup.

## Integration Points
This file is used by the Docker API pause endpoint and ties runtime pause to Docker-visible state and persistence.

## Risks And Edge Cases
The code holds the container lock while calling `tsk.Pause`, which serializes state mutation but can prolong lock duration. Checkpoint failure is logged as a warning after runtime pause has already succeeded. Already paused and restarting states are rejected before runtime call.

## Test Signals
No direct tests in this subset. Pause behavior is likely covered by integration tests around API state transitions and containerd events.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/defaults.go -->
# sources/cloud-native/moby/daemon/pkg/oci/caps/defaults.go

## Purpose
This file defines Docker's default Linux capability set for non-privileged containers.

## Important APIs, Types, And Functions
`DefaultCapabilities()` returns a new slice containing capabilities such as `CAP_CHOWN`, `CAP_DAC_OVERRIDE`, `CAP_MKNOD`, `CAP_NET_RAW`, `CAP_NET_BIND_SERVICE`, `CAP_SYS_CHROOT`, `CAP_KILL`, and `CAP_AUDIT_WRITE`.

## Control Flow
The function simply returns a literal slice each call.

## State, Persistence, And Dependencies
There is no state, persistence, or external dependency.

## Integration Points
`oci/defaults.go` uses this set in the default Linux spec, and `oci_linux.go` passes it through `TweakCapabilities` with container `CapAdd`, `CapDrop`, and privileged settings.

## Risks And Edge Cases
Changing this list directly changes the security posture of default containers. Returning a new slice avoids caller mutation of package-level state.

## Test Signals
No direct tests in this subset; capability behavior is indirectly covered by OCI and container security tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils.go -->
# sources/cloud-native/moby/daemon/pkg/oci/caps/utils.go

## Purpose
This file normalizes, validates, enumerates, and tweaks Linux capabilities for container OCI specs.

## Important APIs, Types, And Functions
`GetAllCapabilities` returns current-environment capabilities. `NormalizeLegacyCapabilities` uppercases names, adds `CAP_`, validates against known/current capabilities, and accepts magic `ALL`. `TweakCapabilities` computes the final capability set from defaults, additions, drops, and privileged mode. `knownCapabilities` and globals `allCaps`/`knownCaps` are initialized by platform-specific `initCaps`.

## Control Flow
Normalization loops over requested capabilities, handles `ALL`, prefixes missing `CAP_`, rejects unknown names, and rejects known but unavailable names. Tweaking returns all capabilities for privileged containers, returns defaults when no changes are requested, otherwise normalizes add/drop lists and applies one of three rules: add all except drops, drop all and use adds, or remove drops from defaults then append adds.

## State, Persistence, And Dependencies
State is cached in package-level `allCaps` and `knownCaps`, initialized once by platform code. There is no persistence. Dependencies include slices/string helpers and errdefs invalid-parameter errors.

## Integration Points
Linux OCI spec generation calls `TweakCapabilities` before applying capabilities with containerd OCI helpers. API `CapAdd`/`CapDrop` compatibility relies on legacy normalization.

## Risks And Edge Cases
Duplicate capabilities are not de-duplicated in the default add-after-drop path. The `ALL` magic value in `CapDrop` causes output to be exactly normalized `CapAdd`, so callers must not pass `ALL` through to OCI. Environment-restricted capabilities produce invalid-parameter errors before runtime invocation.

## Test Signals
No direct tests in this subset; behavior depends on capability utility tests elsewhere and OCI integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils_linux.go -->
# sources/cloud-native/moby/daemon/pkg/oci/caps/utils_linux.go

## Purpose
This Linux-specific file initializes known and currently available kernel capabilities.

## Important APIs, Types, And Functions
`initCaps` uses `sync.Once` to populate `allCaps` and `knownCaps` using containerd capability helpers `cap.Known()` and `cap.Current()`.

## Control Flow
On first call, it reads all known capability names, attempts to read current effective capabilities, logs an error and falls back to known capabilities when current cannot be read, then builds a map where unavailable current capabilities are stored with nil values and available capabilities point to a sentinel struct.

## State, Persistence, And Dependencies
The function mutates package-level cached capability slices/maps once per process. Dependencies include containerd capability package, containerd logging, `context.TODO`, `slices`, and `sync`.

## Integration Points
`utils.go` relies on this initializer for Linux validation and privileged capability enumeration.

## Risks And Edge Cases
If current capability detection fails, all known capabilities are treated as available for backward compatibility; runtime/kernel may still reject unavailable caps later. The nil marker in `knownCaps` is semantically important to distinguish unknown from known-but-unavailable.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils_other.go -->
# sources/cloud-native/moby/daemon/pkg/oci/caps/utils_other.go

## Purpose
This non-Linux file provides a no-op capability initializer for platforms without Linux capabilities.

## Important APIs, Types, And Functions
`initCaps()` is defined under build tag `!linux` and intentionally does nothing.

## Control Flow
Calls to shared capability APIs on non-Linux platforms leave `allCaps` and `knownCaps` at zero values.

## State, Persistence, And Dependencies
No state is initialized and there are no dependencies.

## Integration Points
This allows the shared caps package to compile on Windows and other non-Linux targets while Linux-only callers are build constrained elsewhere.

## Risks And Edge Cases
If shared capability APIs are used unexpectedly on non-Linux, empty/nil capability state may lead to empty results or nil map behavior. Current usage expects Linux-specific capability manipulation.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/caps/utils_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/defaults.go -->
# sources/cloud-native/moby/daemon/pkg/oci/defaults.go

## Purpose
This file defines Docker's default OCI specs and default PATH environment values for Linux and Windows containers.

## Important APIs, Types, And Functions
`DefaultPathEnv`, `DefaultSpec`, `DefaultWindowsSpec`, and `DefaultLinuxSpec` are the public constructors. `iPtr` creates int64 pointers for device cgroup entries. `defaultLinuxMaskedPaths` computes and caches default masked paths.

## Control Flow
`DefaultSpec` dispatches by `runtime.GOOS`. Windows specs contain version, Windows, process, and root structs. Linux specs include default process capabilities, root, standard mounts (`/proc`, `/dev`, `/dev/pts`, `/sys`, cgroup, mqueue, `/dev/shm`), Linux namespaces, masked/readonly paths, empty device list, and default device cgroup allow/deny rules. `defaultLinuxMaskedPaths` starts with sensitive proc/sys paths and appends CPU thermal throttle paths that exist on the host.

## State, Persistence, And Dependencies
The only cached state is `defaultLinuxMaskedPaths` via `sync.OnceValue`. The function reads host CPU topology and filesystem path existence. Dependencies include runtime-spec types, default capability set, internal platform CPU helpers, standard `os/runtime/sync/fmt`.

## Integration Points
Linux and Windows daemon `createSpec` functions start from this default before applying container-specific mutations. Default masked paths include security-advisory-driven protections.

## Risks And Edge Cases
Default Linux mount and device cgroup rules are security-sensitive. Cached masked paths do not change until daemon restart. Windows returns an empty default PATH because Docker cannot infer it outside the image/container context.

## Test Signals
No direct tests in this subset. OCI Linux tests inspect downstream effects of these defaults, especially mounts and resources.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/devices_linux.go -->
# sources/cloud-native/moby/daemon/pkg/oci/devices_linux.go

## Purpose
This file converts Linux host device paths into OCI device entries and device-cgroup permissions for container specs.

## Important APIs, Types, And Functions
`deviceCgroup` builds a `specs.LinuxDeviceCgroup` from a device and permission string. `DevicesFromPath(pathOnHost, pathInContainer, cgroupPermissions)` resolves devices, symlinks, and directories into `[]specs.LinuxDevice` and matching cgroup rules.

## Control Flow
`DevicesFromPath` resolves symlinks when possible, calls containerd `DeviceFromPath`, and on success rewrites the device path to the container path. If the path is not a device but is a directory, it walks the directory recursively, ignores non-device entries, converts found devices, and maps child paths from host directory prefix to container directory prefix. If no devices are found, it returns a contextual error.

## State, Persistence, And Dependencies
There is no persistent state. The function reads filesystem metadata and device nodes. Dependencies include containerd OCI device detection, runtime-spec types, `os`, `filepath`, `strings`, `errors`, and `fmt`.

## Integration Points
`oci_linux.go` calls this for `HostConfig.Devices` in privileged and non-privileged containers, feeding results into spec devices and cgroup permissions.

## Risks And Edge Cases
Directory walking ignores errors and non-device entries, which is permissive but can hide inaccessible devices. Symlink resolution failure falls back to the original path. String prefix replacement maps host child paths to container paths and assumes the walked path is under the resolved host directory.

## Test Signals
No direct tests in this subset; device mapping behavior is covered by OCI/device integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/devices_linux.go -->
