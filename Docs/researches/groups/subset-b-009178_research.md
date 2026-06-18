# Research: subset-b-009178

This grouped report covers the assigned Syncthing infrastructure, discovery, relay, and command entrypoint files. Each section preserves the source path for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main.go

Purpose: implements `strelaypoolsrv`, the public relay pool HTTP service. It serves static UI assets, returns known relay endpoints, accepts relay registration POSTs, probes relays before admitting them, persists known relays to a flat file, and exposes Prometheus metrics.

Important APIs/types/functions: `location`, `relay`, `relayShort`, `stats`, `request`, `result`, `main`, `handleEndpointFull`, `handleEndpointShort`, `handleRegister`, `requestProcessor`, `handleRelayTest`, `evict`, `loadRelays`, `saveRelays`, `getLocation`, `errorTracker`, and `slimURL`. Global state includes `knownRelays`, `permanentRelays`, `evictionTimers`, `requests`, and `globalBlocklist`, protected primarily by `mut`.

Control flow: `main` parses flags, initializes GeoIP, loads permanent relays, creates a testing certificate, starts worker goroutines, asynchronously reloads cached relays, starts metrics if requested, then routes GET/HEAD/OPTIONS and POST traffic. `handleRegister` derives the client IP, enforces the LRU failure blocklist, decodes and canonicalizes the advertised relay URL, optionally validates the TLS peer certificate against the advertised `id`, rejects IP spoofing without a client cert, then enqueues a relay test. `handleRelayTest` uses `client.TestRelay`, fetches status, enriches with GeoIP, replaces any same-host relay, starts a new eviction timer, saves the relay cache, and replies with `evictionIn`.

State and persistence: in-memory relay slices and timers are the authoritative live state. `knownRelaysFile` stores one URL per line and is rewritten after successful dynamic registrations. Permanent relays are loaded from a separate file and never dynamically evicted. GeoIP lookups are runtime enrichment only.

Dependencies/integration: integrates with Syncthing relay client protocol, `protocol.DeviceID`, `tlsutil.NewCertificate`, generated UI assets, GeoIP, `hashicorp/golang-lru`, Prometheus, and the sibling `stats.go` metrics/status logic. It is consumed by `strelaysrv` pool joins.

Risks and test signals: relay registration is network-sensitive and intentionally rejects spoofed public IPs unless authenticated by cert. `append(permanentRelays, knownRelays...)` in the short endpoint can mutate backing arrays if capacity is shared; the full endpoint avoids that by copying. Queue saturation returns HTTP 429. Existing tests cover permanent relay preservation, URL query canonicalization, and slimming URLs, but not the network probe path, cert mismatch branch, cache writes, or blocklist threshold behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main_test.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main_test.go

Purpose: regression and utility tests for the relay pool server HTTP endpoint and URL handling.

Important APIs/tests: package-level `init` seeds `permanentRelays` and `knownRelays`; `TestHandleGetRequest` exercises `handleEndpointFull`; `TestCanonicalizeQueryValues` documents the `url.Parse` plus `Query().Encode()` canonicalization behavior; `TestSlimURL` verifies that relay URLs exposed by the short endpoint preserve only the `id` query parameter.

Control flow and state: the tests mutate package globals, so they assume single-package test execution and capacity-sensitive permanent relay setup. `TestHandleGetRequest` decodes the JSON response and then checks the global permanent relay slice for unchanged order and values.

Dependencies/integration: uses `httptest`, `encoding/json`, `net/url`, and the server package globals. It does not spin up listeners or exercise the relay testing queue.

Risks and test signals: the main regression signal is that full endpoint assembly must not corrupt `permanentRelays`. The URL canonicalization test is explanatory rather than directly invoking `handleRegister`. Gaps remain around `handleEndpointShort`, request queue backpressure, TLS certificate ID validation, IP header behavior, and error tracker blocking.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats.go

Purpose: Prometheus instrumentation and remote relay status scraping for `strelaypoolsrv`.

Important APIs/types/functions: metric constructors `makeGauge`, `makeSummary`, `makeCounter`; exported package metrics such as `apiRequestsTotal`, `relayTestsTotal`, `relayUptime`, and `relayBuildInfo`; `statsRefresher`, `refreshStats`, `fetchStats`, `updateMetrics`, `deleteMetrics`, `mergeStats`, and `mergeValue`. `statsFetchResult` carries scrape results back from concurrent workers.

Control flow: `statsRefresher` ticks forever and calls `refreshStats`. `refreshStats` snapshots permanent plus known relays, concurrently fetches `/status` for each relay, records scrape durations, then under `mut` updates relay structs and gauges. `fetchStats` derives the status address from the relay query string, defaults to `:22070`, fills an omitted host from the relay URL, and decodes JSON into the `stats` type defined in `main.go`.

State and persistence: metrics state lives in Prometheus collectors plus the `lastStats` map. `lastStats` lets `updateMetrics` smooth small backwards movements in counters to avoid Prometheus rate-reset spikes. There is no durable persistence in this file.

Dependencies/integration: depends on the relay status endpoint implemented by `strelaysrv/status.go`, `net/http`, and Prometheus. It assumes callers hold `mut` when necessary for consistency with relay list updates and metric scrapes.

Risks and test signals: `refreshStats` currently calls `fetchStats(rel)` twice per relay in the goroutine, which doubles remote traffic and can yield inconsistent duration/result data. `fetchStats` does not close `response.Body`, which can leak connections. Tests cover `mergeValue` only, leaving scraping, body lifecycle, label cleanup, and concurrent update behavior untested.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats_test.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats_test.go

Purpose: small unit test for the relay pool stats smoothing helper.

Important APIs/tests: `TestMerge` calls `mergeValue` with increasing, slightly decreasing, and sharply decreasing inputs.

Control flow and state: the test is stateless and directly validates the threshold policy: increases pass through, values within 1 percent below the old value are held at the old value, and large drops are treated as real resets.

Dependencies/integration: depends only on `testing` and the local helper in `stats.go`.

Risks and test signals: it documents the intended anti-spike behavior for Prometheus counters. It does not test `mergeStats`, per-field metric update behavior, or remote status scraping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stupgrades/main.go -->
# sources/sync-backup/syncthing/cmd/infra/stupgrades/main.go

Purpose: implements the upgrade metadata proxy service used by Syncthing clients. It periodically fetches GitHub release metadata, enriches releases with compatibility data, filters responses by client OS version, serves latest stable/prerelease metadata, and can forward configured auxiliary paths through a caching proxy.

Important APIs/types/functions: `cli`, `server`, `githubReleases`, `servePing`, `serveReleases`, `proxy.ServeHTTP`, `filterForLatest`, `filterForCompatibility`, `cachedReleases`, `cachedReleases.Update`, `fetchGithubReleases`, and `addReleaseCompatibility`.

Control flow: `main` parses Kong flags and calls `server`. `server` starts an optional metrics listener, performs an initial cache update, starts periodic refreshes, registers `/ping` and `/meta.json`, then attaches any `path->url` forwards with `httpcache.SinglePath`. `serveReleases` reads cached releases, optionally filters them based on `User-Agent` and `Syncthing-Os-Version`, keeps only the latest relevant releases, sets cache/CORS/Vary headers, and returns JSON.

State and persistence: release cache is in memory under `cachedReleases.mut`. `latestRel` and `latestPre` are mirrored into a gauge. There is no durable local storage; refresh failures retain the last successful cache.

Dependencies/integration: uses GitHub releases JSON shaped as `upgrade.Release`, Syncthing upgrade compatibility semantics, Prometheus, `httpcache`, Kong, and optional HTTP forwarding targets.

Risks and test signals: `fetchGithubReleases` accepts a context parameter but creates the initial request with `context.TODO()`, so cancellation does not cover the releases fetch. HTTP status codes from GitHub are not checked before JSON decode. Compatibility files are limited to 10 KiB. Metrics identify filter outcomes. No tests are listed in this subset for filtering or proxy behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stupgrades/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stupgrades/metrics.go -->
# sources/sync-backup/syncthing/cmd/infra/stupgrades/metrics.go

Purpose: centralizes Prometheus collectors for the upgrade metadata service.

Important APIs/state: `metricUpgradeChecks`, `metricFilterCalls`, `metricHTTPRequests`, and `metricLatestReleaseInfo` are registered with `promauto` under namespace `syncthing` and subsystem `upgrade`.

Control flow: collectors are initialized at package load. Runtime updates come from `serveReleases`, compatibility filtering, GitHub/compat/proxy HTTP fetches, and `cachedReleases.Update`.

State and persistence: all state is in-process Prometheus collector state; `metricLatestReleaseInfo` uses labels for latest stable and prerelease versions and is explicitly deleted/replaced on cache changes.

Dependencies/integration: depends on Prometheus client packages and the functions in `main.go`.

Risks and test signals: label cardinality is bounded by configured forward names and release version labels. There are no tests here; correctness is observed indirectly via metrics endpoint and service behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stupgrades/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/main.go -->
# sources/sync-backup/syncthing/cmd/infra/ursrv/main.go

Purpose: top-level command entrypoint for the usage reporting server `ursrv`.

Important APIs/types/functions: `CLI` contains a default `Serve serve.CLI` subcommand. `main` configures text `slog`, logs build version information, parses commands with Kong, and runs the selected command.

Control flow: startup is intentionally thin: logging setup, version log, parse, run, fatal log on command failure. All server behavior is delegated to `cmd/infra/ursrv/serve`.

State and persistence: no direct state or persistence; it passes through to the `serve` package.

Dependencies/integration: depends on Kong, `slog`, Syncthing `build`, and the local `serve` package.

Risks and test signals: failure handling uses `log.Fatalf`, which exits immediately. There are no direct tests; coverage lives in the serve package tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/compiler_test.go -->
# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/compiler_test.go

Purpose: validates parsing of compiler and builder identity from Syncthing long version strings used in usage report enrichment.

Important APIs/tests: `TestCompilerRe` applies package regex `compilerRe` to historical version string examples and asserts captured compiler and builder values.

Control flow and state: table-driven test iterates three samples, verifies match count, then compares capture groups.

Dependencies/integration: depends on `compilerRe` from `serve.go` and `testing`.

Risks and test signals: gives regression coverage for release string formats from older Syncthing versions. It does not cover distribution classification, version transformation, or report validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/compiler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/metrics.go -->
# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/metrics.go

Purpose: defines operational Prometheus metrics for the usage reporting server itself.

Important APIs/state: counters and gauges include `metricReportsTotal`, `metricsCollectsTotal`, `metricsCollectSecondsTotal`, `metricsCollectSecondsLast`, `metricsRecalcsTotal`, `metricsRecalcSecondsTotal`, `metricsRecalcSecondsLast`, and `metricsWriteSecondsLast`.

Control flow: package initialization creates collectors with namespace `syncthing` and subsystem `ursrv_v2`. `init` prewarms `incoming_reports_total` labels `fail`, `replace`, and `accept`.

State and persistence: metrics are process-local. They summarize incoming report outcomes, custom collector recalculation/collection timing, and dump-file write timing.

Dependencies/integration: used by `serve.go` request handling and dump writes, and by `prometheus.go` custom collector recalculation/collection paths.

Risks and test signals: prewarming avoids missing series for dashboards. No direct unit tests are present for collector registration or label use.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/prometheus.go -->
# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/prometheus.go

Purpose: builds a dynamic Prometheus collector from `contract.Report` struct tags, aggregating usage report data into gauges, gauge vectors, and custom summaries.

Important APIs/types/functions: `metricsSet`, `newMetricsSet`, `fieldNameTypeLabel`, `nameConstLabels`, `Serve`, `recalc`, `addReport`, `addReportStruct`, `Describe`, `Collect`, and `metricSummary` with `Observe`, `Collect`, and `Reset`.

Control flow: `newMetricsSet` reflects over `contract.Report` fields recursively and creates collectors based on `metric` tags. `Serve` triggers recalculation on a five-minute boundary. `recalc` resets collectors, deletes stale reports older than the negative cutoff, and re-adds all remaining reports. `Collect` exposes the current calculated values under a read lock while updating collection timing metrics.

State and persistence: state is in memory in maps of Prometheus collectors and summary accumulators. Source data lives in `server.reports`; stale report pruning mutates that map. Custom summaries retain value slices until each recalculation resets them.

Dependencies/integration: depends heavily on `lib/ur/contract` metric tags, Prometheus collector interfaces, `xsync` report storage via `server`, reflection, sorting, and `serve.go` report enrichment.

Risks and test signals: reflection tag mistakes can silently create empty metric names or missing labels. In the `map[string]int` gaugeVec branch, `field.SetInt` is attempted on a map-valued reflect field, which looks suspicious and could panic if hit. `metricSummary.Collect` returns from the whole method when it sees an empty value slice, potentially skipping later labels. No direct tests cover these collector edge cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/prometheus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/serve.go -->
# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/serve.go

Purpose: implements the usage reporting server that accepts Syncthing client reports, enriches them, serves aggregate Prometheus metrics, and periodically persists report dumps locally and optionally to S3-compatible blob storage.

Important APIs/types/functions: `CLI`, `knownDistributions`, `distributionMatch`, `CLI.Run`, `downloadDumpFile`, `saveDumpFile`, `server`, `handleNewData`, `addReport`, `save`, `load`, and `transformVersion`.

Control flow: `Run` opens external and internal listeners, optionally starts GeoIP, optionally opens S3 storage and downloads the latest dump, loads a gzip JSON-lines dump into an `xsync` map, starts periodic dump writes/uploads, exposes internal process metrics on `/metrics`, registers a custom usage metrics registry on the external `/metrics`, and handles `/newdata` and `/ping`. `handleNewData` accepts only POST, derives IP from `X-Forwarded-For` or `RemoteAddr`, limits body reads to 40 KiB, validates a `contract.Report`, stamps received/date/address fields, and stores it by unique ID. `addReport` enriches country, major version, OS/arch, compiler, builder, distribution, and database backend flags.

State and persistence: live reports are held in `xsync.MapOf[string,*contract.Report]`. Persistence is gzip-compressed JSON-lines in `DumpFile`, atomically written via `.tmp` rename, with optional daily S3 object upload. On startup, an absent local dump can be restored from latest blob key.

Dependencies/integration: depends on `contract.Report` validation, GeoIP, `blob`/S3, Prometheus, Suture supervisor for metrics recalculation, `slog`, and Syncthing build/version conventions.

Risks and test signals: reports are keyed by `UniqueID`, so repeat reports replace older ones. Body truncation can cause decode failure for oversized reports. `metricsWriteSecondsLast.Set(float64(time.Since(t0)))` records nanoseconds as a float despite the metric name saying seconds. `handlePing` intentionally returns an empty 200. Tests in this subset cover only `compilerRe`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/ursrv/serve/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/amqp.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/amqp.go

Purpose: provides optional AMQP fanout replication for the discovery server database.

Important APIs/types/functions: `amqpReplicator`, `newAMQPReplicator`, `amqpSender`, `amqpReceiver`, `amqpSender.Serve`, `amqpSender.send`, `amqpReceiver.Serve`, `amqpChannel`, and `amqpConsume`.

Control flow: `newAMQPReplicator` creates a Suture service containing a sender and receiver. The sender consumes buffered replication records, marshals protobuf messages, and publishes them to the `discovery` fanout exchange with `AppId` set to the local client ID. The receiver declares/binds an exclusive transient queue, ignores messages whose `AppId` is local, unmarshals records, parses the device ID from bytes or legacy string form, and merges records into the database.

State and persistence: the sender has a buffered outbox. Replication itself is transient AMQP fanout; durable state remains in the discovery database. Sender drops messages rather than blocking if the outbox is full.

Dependencies/integration: depends on RabbitMQ AMQP 0-9-1, generated `discosrv` protobufs, `protoutil`, Syncthing `protocol.DeviceID`, the local `database` interface, Suture, and replication Prometheus counters.

Risks and test signals: the exchange and queue are non-durable, so replication does not survive broker restart and relies on the local database flush/S3 backup for persistence. Receiver returns on malformed protobuf or database merge errors, relying on supervisor restart. No direct AMQP tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/amqp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv.go

Purpose: implements the discovery API server used by Syncthing clients to announce addresses and look up other devices.

Important APIs/types/functions: `announcement`, `apiSrv`, `replicator`, `newAPISrv`, `Serve`, `handler`, `handleGET`, `handlePOST`, `handleAnnounce`, `certificateBytes`, `fixupAddresses`, `loggingResponseWriter`, `addressStrs`, retry header helpers, and `retryAfterTracker`.

Control flow: `Serve` listens with either TLS client-certificate support or plain HTTP for reverse-proxy deployments, registers `/` and `/ping`, and shuts down on context cancellation. `handler` records metrics and dispatches GET/POST. GET parses a `device` query parameter, loads the database record, returns addresses if active, or returns 404 with adaptive `Retry-After` depending on whether the device was ever seen. POST extracts a client certificate from TLS or proxy headers, derives the device ID, decodes announced addresses, normalizes unspecified hosts/ports with the remote address, and merges sorted compacted addresses into the database, optionally sending replication.

State and persistence: live state is in the database implementation. `retryAfterTracker` maintains per-category counters and dynamically adjusts not-found retry delays to target a desired rate. Gzip writers are pooled for compressed lookup responses.

Dependencies/integration: integrates with the `database` interface, AMQP `replicator`, generated discovery protobuf address records, Syncthing device IDs, reverse-proxy certificate header formats for nginx/Caddy/Traefik, and Prometheus metrics.

Risks and test signals: certificate header parsing is security-sensitive in HTTP proxy mode and assumes a trusted proxy boundary. `fixupAddresses` rejects loopback/multicast and enforces scheme/IP-family compatibility, but it calls methods on `ip` after `net.ParseIP(host)` without an explicit nil check; Go IP methods handle nil safely, but this behavior is subtle. Tests cover address fixups, adaptive retry distribution, and API benchmarks, but not certificate header variants or full HTTP TLS flows.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv_test.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv_test.go

Purpose: validates discovery API address normalization and retry-after behavior, plus a request benchmark.

Important APIs/tests: `TestFixupAddresses`, helper `addr`, `TestRetryAfterSHistogram`, and `BenchmarkAPIRequests`.

Control flow and state: fixup tests supply announced addresses with unspecified, loopback, multicast, IPv4/IPv6, and zero-port cases against synthetic remote addresses. Retry tests exercise `retryAfterTracker.retryAfterS` enough times to validate generated delays stay within configured bounds and cluster around the desired delay. The benchmark drives API request handling against an in-memory setup.

Dependencies/integration: uses `net`, `testing`, and local API helpers. It indirectly documents reverse-proxy derived remote IP/port semantics.

Risks and test signals: strong signal for address sanitation and deduplication, especially replacing `0.0.0.0`/`[::]` with the remote IP. Missing coverage remains for parsing proxy certificate headers, compression response behavior, database merge side effects, and GET not-found status classes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/database.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/database.go

Purpose: provides the discovery server's in-memory database with periodic protobuf persistence, expiry, statistics, and optional blob-store backup/restore.

Important APIs/types/functions: `clock`, `database`, `inMemoryStore`, `newInMemoryStore`, `put`, `merge`, `get`, `Serve`, `expireAndCalculateStatistics`, `write`, `read`, `merge`, `expire`, `Cmp`, and `Equal`.

Control flow: construction reads `records.db`, falls back to downloading the latest blob object if configured and the local file is missing, logs record count, then expires records and calculates metrics. `Serve` periodically runs statistics and `write`, and writes one final time on shutdown. `get` expires returned addresses lazily. `merge` combines new and old sorted address lists using latest expiry and latest seen timestamp. `write` serializes length-prefixed protobuf `ReplicationRecord` entries to a temp file, renames atomically, and uploads to blob storage when configured.

State and persistence: live state is an `xsync.MapOf[protocol.DeviceID,*DatabaseRecord]`. Durable state is `records.db` in the configured database directory, with records older than one week omitted. Optional S3/blob upload uses a hostname-derived object key.

Dependencies/integration: uses generated `discosrv` protobufs, Syncthing device IDs, `protoutil`, `blob.Store`, Prometheus database metrics, and the API/AMQP layers.

Risks and test signals: `merge` assumes both address slices are sorted; API and read paths sort before merge, but direct callers must preserve that contract. The insertion path allocates when `b` has new earlier addresses; benchmark tracks equal-list allocations. Old records are deleted by statistics/write filtering. Tests cover put/get, expiry filtering, merge symmetry, and benchmark allocation behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/database.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/database_test.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/database_test.go

Purpose: unit and benchmark coverage for discovery database records, expiry, and merge behavior.

Important APIs/tests: `TestDatabaseGetSet`, `TestFilter`, `TestMerge`, `BenchmarkMergeEqual`, and `testClock`.

Control flow and state: tests use temporary stores and a controllable clock to validate reads, lazy expiry, statistics-era pruning, and merge ordering. Merge cases cover nil inputs, duplicate addresses with newer expiry, disjoint ordered inputs, reverse merge symmetry, and preserving maximum expiry per address.

Dependencies/integration: depends on generated discovery protobuf address records and local database helpers.

Risks and test signals: tests document the sorted-address precondition and expected union semantics. Benchmark asserts the equal-address merge path remains allocation-free. Tests do not cover file serialization round trips with corrupt records, blob fallback, or concurrent `xsync` access.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/database_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/etc/linux-systemd/stdiscosrv.service -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/etc/linux-systemd/stdiscosrv.service

Purpose: systemd unit for running the Syncthing discovery server as a hardened service.

Important directives: `WorkingDirectory=/var/lib/syncthing-discosrv`, `EnvironmentFile=/etc/default/syncthing-discosrv`, `ExecStart=/usr/bin/stdiscosrv $DISCOSRV_OPTS`, `User=syncthing-discosrv`, `Group=syncthing`, `ReadWritePaths=/var/lib/syncthing-discosrv`, and install alias `syncthing-discosrv.service`.

Control flow: systemd starts after `network.target` and launches the binary with options supplied by the environment file. The service participates in `multi-user.target`.

State and persistence: runtime data and database writes are confined to `/var/lib/syncthing-discosrv`; config is injected through `/etc/default/syncthing-discosrv`.

Dependencies/integration: integrates Linux packaging with the `stdiscosrv` binary and `scripts/preinst` user/group provisioning.

Risks and test signals: `ProtectSystem=strict`, `NoNewPrivileges`, private temp/devices, home protection, native syscall architecture, and W^X hardening reduce service attack surface. Operational risk is that missing environment file or incorrect writable path prevents startup. No automated tests target this unit file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/etc/linux-systemd/stdiscosrv.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/main.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/main.go

Purpose: main entrypoint and service wiring for the discovery server.

Important APIs/types/functions: constants for expiry, retry, HTTP timeouts, and replication outbox size; global `debug`; `CLI` flags/env bindings; and `main`.

Control flow: `main` parses Kong options, configures log level, handles `--version`, loads or generates TLS certificates unless HTTP proxy mode is enabled, creates the root Suture supervisor, optionally configures S3 blob storage, starts the in-memory database service, optionally starts AMQP replication, starts the API service, optionally starts a Prometheus metrics listener, and cancels the supervisor on SIGINT/SIGTERM after an optional shutdown delay.

State and persistence: delegates database persistence to `inMemoryStore`, certificates to configured cert/key files, optional S3 backups to blob storage, and optional AMQP replication to `amqp.go`.

Dependencies/integration: uses Kong, Suture, Syncthing build/tlsutil/protocol/rand helpers, Prometheus `promhttp`, S3 blob storage, and the API/database/metrics files in this package.

Risks and test signals: certificate auto-generation changes first-run behavior and device identity. HTTP mode trusts proxy-provided certificate and remote address headers. Metrics listener errors call `os.Exit(1)` from a goroutine. Tests are indirect through API and database test files.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/scripts/preinst -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/scripts/preinst

Purpose: Debian-style package pre-install script for the discovery server service account.

Important commands: `addgroup --system syncthing` and `adduser --system --home /var/lib/syncthing-discosrv --ingroup syncthing syncthing-discosrv`.

Control flow and state: the script creates the shared `syncthing` system group and a dedicated `syncthing-discosrv` system user with home/state directory `/var/lib/syncthing-discosrv`.

Dependencies/integration: supports the systemd unit's `User`, `Group`, and `WorkingDirectory` assumptions.

Risks and test signals: no shell strict mode is set, and behavior depends on platform-specific `addgroup`/`adduser` tools. It is packaging glue rather than Go runtime code; no tests are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/scripts/preinst -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/stats.go -->
# sources/sync-backup/syncthing/cmd/stdiscosrv/stats.go

Purpose: defines Prometheus metrics for discovery server API, replication, database operations, database writes, and adaptive retry delays.

Important APIs/state: counters/summaries/gauges include `apiRequestsTotal`, `apiRequestsSeconds`, `lookupRequestsTotal`, `announceRequestsTotal`, `replicationSendsTotal`, `replicationRecvsTotal`, `databaseKeys`, `databaseStatisticsSeconds`, `databaseOperations`, `databaseOperationSeconds`, `databaseWriteSeconds`, `databaseLastWritten`, and `retryAfterLevel`.

Control flow: `init` registers all collectors and prewarms key labels for common API, lookup, announcement, and replication results.

State and persistence: metrics are process-local. Database and API code update these collectors as side effects of requests, flushes, expiry, and replication.

Dependencies/integration: depends on Prometheus and standard HTTP method constants. Used by `apisrv.go`, `database.go`, and `amqp.go`.

Risks and test signals: prewarmed label sets improve dashboard continuity, but some error label values used in code are not prewarmed. No direct tests validate metric names or registration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/stdiscosrv/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/etc/linux-systemd/strelaysrv.service -->
# sources/sync-backup/syncthing/cmd/strelaysrv/etc/linux-systemd/strelaysrv.service

Purpose: systemd unit for running the Syncthing relay server as a hardened service.

Important directives: `WorkingDirectory=/var/lib/syncthing-relaysrv`, `EnvironmentFile=/etc/default/syncthing-relaysrv`, `ExecStart=/usr/bin/strelaysrv -nat=${NAT} $RELAYSRV_OPTS`, `User=syncthing-relaysrv`, `Group=syncthing`, `ReadWritePaths=/var/lib/syncthing-relaysrv`, and alias `syncthing-relaysrv.service`.

Control flow: systemd starts the relay after network target and installs it under multi-user target.

State and persistence: relay keys and runtime files are expected under `/var/lib/syncthing-relaysrv`.

Dependencies/integration: matches the packaging preinstall script and `strelaysrv` flags, including NAT enablement via environment.

Risks and test signals: hardened sandboxing limits filesystem/device exposure. Startup depends on `/etc/default/syncthing-relaysrv` and writable state directory. No direct automated tests cover this unit.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/etc/linux-systemd/strelaysrv.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/listener.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/listener.go

Purpose: accepts relay protocol and session data connections, manages joined clients, and brokers session invitations.

Important APIs/state/functions: global `outboxes`, `outboxesMut`, `numConnections`; `listener`, `protocolConnectionHandler`, `sessionConnectionHandler`, and `messageReader`.

Control flow: `listener` accepts TCP with `tlsutil.DowngradingListener`, sets TCP options, and dispatches TLS protocol connections to `protocolConnectionHandler` and non-TLS session joins to `sessionConnectionHandler`. Protocol connections TLS-handshake with client certificates, derive device IDs, read relay protocol messages, handle joins, connect requests, pings, idle timeouts, over-limit refusal, duplicate IDs, and outbox invitations. Session connections read `JoinSessionRequest`, find a pending session by key, attach the connection, and return protocol responses.

State and persistence: joined clients are represented by per-device outbox channels in the global map. Sessions live in globals from `session.go`. No durable persistence exists.

Dependencies/integration: uses Syncthing relay protocol messages, Syncthing device IDs, TLS config from `main.go`, timeout globals, session creation, and limit monitoring.

Risks and test signals: connection handling is highly concurrent and relies on map locks and channel lifetimes. Closing outboxes during shutdown can interact with protocol handler sends. Over-limit handling drops idle joined clients with no active sessions. No direct tests in this subset cover protocol negotiation or session attach races.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/listener.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/main.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/main.go

Purpose: main entrypoint for the Syncthing relay server, including flags, certificates, NAT mapping, relay pool registration, status service, limits, and graceful shutdown.

Important APIs/state/functions: numerous global flag variables, `httpClient`/`httpTransport`, `main`, `monitorLimits`, `mapping`, and `mapping.Address`.

Control flow: `main` parses flags, validates advertised/provided values, binds outgoing HTTP to the listen IP when specific, raises file descriptor limits, loads or generates the relay certificate, configures outbound and inbound TLS, initializes NAT service/mapping, waits briefly for mapping if enabled, creates rate limiters, starts status service, builds the advertised relay URL with query metadata, starts pool join loops unless token mode disables pools, starts the listener, then waits for shutdown signals and closes sessions/outboxes.

State and persistence: certificate/key files persist identity in the keys directory. Live state is global in sessions/outboxes/counters. NAT mappings are runtime. Pool membership is maintained by periodic registration with pools.

Dependencies/integration: uses Syncthing config wrapper, NAT/PMP/UPnP packages, relay protocol, TLS helpers, status and pool files, rate limiting, and OS file descriptor limits.

Risks and test signals: `sessionAddress = addr.IP[:]` assumes resolved advertised IP is non-nil. `InsecureSkipVerify` is set for relay protocol TLS because identity is derived from presented certificates, but this is security-sensitive. Pool joins are disabled when token auth is configured. No direct tests cover startup; behavior is observed through protocol clients/status.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/pool.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/pool.go

Purpose: periodically registers a running relay server with one relay pool endpoint.

Important APIs/functions: `httpStatusEnhanceYourCalm` and `poolHandler`.

Control flow: each loop copies the relay URL, refreshes its host from the current NAT mapping, POSTs `{"url": ...}` to the pool, reads the response, and reacts by status code. On success it parses `evictionIn` and sleeps for 80 percent of that duration before rejoining. Server errors, bad requests, rate limiting, and unexpected statuses sleep one minute. Unauthorized logs and aborts permanently.

State and persistence: no durable state; membership is maintained by periodic HTTP registration. It uses the package `httpClient`, which may have TLS client cert and local address binding configured by `main.go`.

Dependencies/integration: integrates with `strelaypoolsrv` registration API and NAT mapping state.

Risks and test signals: URL host is recalculated each registration, which handles changing external NAT addresses. Unexpected success response JSON falls through to a one-hour sleep, which may delay rejoin. No tests cover retry/backoff behavior or response parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/scripts/preinst -->
# sources/sync-backup/syncthing/cmd/strelaysrv/scripts/preinst

Purpose: package pre-install script for relay server service identity.

Important commands: creates the shared system group `syncthing` and system user `syncthing-relaysrv` with home `/var/lib/syncthing-relaysrv`.

Control flow and state: runs before package install to ensure the systemd unit's user/group and working directory ownership assumptions can be satisfied.

Dependencies/integration: supports `strelaysrv.service`.

Risks and test signals: no strict shell options and platform-specific account tools. No tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/scripts/preinst -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/session.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/session.go

Purpose: manages relay sessions between two devices and proxies bytes between their joined TCP connections.

Important APIs/state/functions: global `sessionMut`, `activeSessions`, `pendingSessions`, `numProxies`, `bytesProxied`; `newSession`, `findSession`, `dropSessions`, `hasSessions`, `session`, `AddConnection`, `Serve`, invitation builders, `CloseConns`, `proxy`, `makeRateLimitFunc`, and `take`.

Control flow: `newSession` generates two random 32-byte keys, creates optional per-session and global rate limiting behavior, and registers both keys as pending. `Serve` waits for two joined connections or times out, starts two proxy goroutines, records itself active, waits for either direction to finish, then removes pending/active entries and closes connections. `proxy` repeatedly reads with deadlines, increments byte counters, applies rate limiting, and writes to the peer with deadlines.

State and persistence: all session state is in memory. Pending sessions are keyed by raw key string, active sessions by slice membership, and counters are atomics.

Dependencies/integration: used by `listener.go` for connect and join flow, by `status.go` for reporting, and by rate limiter globals from `main.go`.

Risks and test signals: session keys are binary strings, which is valid for map keys but opaque in logs. `AddConnection` uses an unbuffered channel and fails if `Serve` is not actively selecting. Rate limiting reserves tokens on all limiters and sleeps the maximum delay. No direct tests here cover timeouts, cleanup, or proxy error races.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/status.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/status.go

Purpose: exposes the relay server status HTTP endpoint and calculates throughput rates.

Important APIs/types/functions: global `rc`, `statusService`, `getStatus`, `rateCalculator`, `newRateCalculator`, `updateRates`, and `rate`.

Control flow: `statusService` creates a 360-interval rate calculator at 10-second resolution, registers `/status`, optionally exposes pprof, and serves HTTP with keepalives disabled. `getStatus` gathers build/runtime data, pending and active session counts under lock, connection/proxy/byte atomics, rate windows, and current relay options, then emits indented JSON with CORS.

State and persistence: rate history is an in-memory ring-like slice shifted every interval. Status is computed live from globals and atomics.

Dependencies/integration: consumed by relay pool stats scraping, depends on build metadata, runtime package, session globals, and option globals.

Risks and test signals: `rate(periods)` assumes enough history length for the requested period. Locking around sessions prevents map/slice races for counts. No direct tests cover status JSON or rate calculation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/testutil/main.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/testutil/main.go

Purpose: manual command-line utility for testing relay join/connect/test flows against a relay server.

Important APIs/functions: `main`, `stdinReader`, and `connectToStdio`.

Control flow: loads a TLS keypair, derives the device ID, parses relay URL, reads stdin asynchronously, and runs one of three modes. `-join` creates a relay client, serves it, receives session invitations, joins sessions, and bridges to stdio. `-connect` requests an invitation for a target device and joins it. `-test` uses `client.TestRelay`.

State and persistence: uses certificate/key files for identity; otherwise no persistence. Runtime state is relay client connection/invitation channels.

Dependencies/integration: depends on relay client and relay protocol packages. It is intended to exercise `strelaysrv` behavior externally.

Risks and test signals: useful for interactive/manual verification, but not automated. `connectToStdio` polls reads with millisecond deadlines and writes stdin lines, which is simple but not throughput-oriented.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/testutil/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/utils.go -->
# sources/sync-backup/syncthing/cmd/strelaysrv/utils.go

Purpose: applies TCP socket options for accepted relay connections.

Important APIs/functions: `setTCPOptions`.

Control flow: asserts the connection is a `*net.TCPConn`, then sets linger to zero, disables Nagle with `SetNoDelay(true)`, sets keepalive period to `networkTimeout`, and enables keepalive.

State and persistence: no persistent state; uses global `networkTimeout`.

Dependencies/integration: called by `listener` immediately after accepting TCP connections.

Risks and test signals: non-TCP connections return an error, but the caller ignores the result, so failed socket tuning does not reject clients. No direct tests cover socket option failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/strelaysrv/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/blockprof.go -->
# sources/sync-backup/syncthing/cmd/syncthing/blockprof.go

Purpose: optional debug support for periodically writing Go block profiles from the Syncthing process.

Important APIs/functions: `startBlockProfiler` and `saveBlockingProfiles`.

Control flow: `startBlockProfiler` looks up the `block` profile, enables a goroutine, and panics if profile saving returns. `saveBlockingProfiles` sets block profile rate to 1 and every 20 seconds writes `block-<pid>-<ms>.pprof` based on elapsed runtime.

State and persistence: writes profile files to the current working directory. It changes global runtime block profiling rate.

Dependencies/integration: enabled from `serveCmd.syncthingMain` when `--debug-profile-block`/`STBLOCKPROFILE` is set.

Risks and test signals: aggressive block profiling can affect performance and produce unbounded files. No tests cover profile writing failure or cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/blockprof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/client.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/client.go

Purpose: provides the REST API client used by `syncthing cli` subcommands.

Important APIs/types/functions: `APIClient`, `apiClient`, `apiClientFactory`, `getClient`, `loadGUIConfig`, `Endpoint`, `Do`, `Request`, `RequestString`, `RequestJSON`, `Get`, `Post`, `PutJSON`, `errNotFound`, and `checkResponse`.

Control flow: `getClient` either uses explicit GUI address/API key or loads local cert/config to discover GUI settings. It builds an HTTP client with a custom dialer that dials the configured GUI network/address and disables TLS verification for local GUI certs. Requests are built under `Endpoint()+"rest/"`, `X-Api-Key` is injected in `Do`, and `checkResponse` maps 404/401/non-200 statuses into errors with body text.

State and persistence: reads config and cert/key from Syncthing locations; no writes.

Dependencies/integration: depends on Syncthing config, locations, protocol device IDs, and standard HTTP/TLS.

Risks and test signals: `InsecureSkipVerify` is acceptable for local pinned API-key access but must not be treated as generic remote trust. `checkResponse` only treats HTTP 200 as success, so endpoints returning other 2xx codes would be flagged. No tests in this subset cover API client behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/config.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/config.go

Purpose: implements `syncthing cli config`, a reflection-driven configuration editor backed by the REST API.

Important APIs/types/functions: custom urfave/cli help templates, `configHandler`, `configCommand`, `configCommand.Run`, `configBefore`, and `configAfter`.

Control flow: `Run` builds a urfave CLI app to mimic Kong help, obtains an API client and current config, copies the original config, uses `recli` to construct commands over `config.Configuration`, and runs the nested app. `configBefore` permits help without requiring API connectivity. `configAfter` compares modified config to the original and POSTs `system/config` with indented JSON when changed.

State and persistence: reads current config via REST and persists changes through Syncthing's `system/config` endpoint.

Dependencies/integration: bridges Kong, urfave/cli, `recli`, Syncthing config structs, and the API client.

Risks and test signals: reflection exposes config surface based on struct tags, so tag changes can alter CLI behavior. Errors before command execution are deferred to allow help. No direct tests cover command construction or POST diffing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/debug.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/debug.go

Purpose: implements `syncthing cli debug` subcommands for inspecting file index data and saving runtime profiles.

Important APIs/types/functions: `fileCommand`, `fileCommand.Run`, `profileCommand`, `profileCommand.Run`, and `debugCommand`.

Control flow: file debug normalizes the path, builds `debug/file?folder=...&file=...`, and pretty-prints the REST response. Profile debug accepts only `cpu` or `heap` and saves `debug/cpuprof` or `debug/heapprof` response content to the filename from `Content-Disposition`.

State and persistence: file command is read-only. Profile command writes the profile file supplied by the server response.

Dependencies/integration: uses REST API helpers in `utils.go`.

Risks and test signals: invalid profile type returns a local error. `saveToFile` trusts server-provided filename. No direct tests for command routing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/errors.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/errors.go

Purpose: implements CLI access to Syncthing pending GUI/system errors.

Important APIs/types/functions: `errorsCommand`, `errorsPushCommand`, `errorsPushCommand.Run`, and `errorsCommand.Run`.

Control flow: `push` posts a trimmed message to `system/error` and emits detailed status/body errors on non-200 responses. Parent `Run` dispatches `show` to `system/error` and `clear` to `system/error/clear`.

State and persistence: modifies or reads runtime error state in the running Syncthing instance via REST.

Dependencies/integration: depends on Kong selected command metadata and API helpers.

Risks and test signals: response body is included in command errors for operator diagnostics. No direct tests; relies on REST endpoint behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/main.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/main.go

Purpose: defines the top-level `syncthing cli` command tree and stdin command loop.

Important APIs/types/functions: `CLI`, `Context`, `CLI.AfterApply`, `stdinCommand`, and `stdinCommand.Run`.

Control flow: `AfterApply` creates an `apiClientFactory` from global `--gui-address` and `--gui-apikey` flags and binds it into the Kong context. `stdinCommand` reads shell-quoted command lines from stdin, parses each into a fresh CLI parser, runs it, prints per-command errors, and continues.

State and persistence: no direct state beyond context binding. Stdin mode repeatedly invokes command handlers that may read/write the Syncthing REST API.

Dependencies/integration: ties together `show`, `debug`, `operations`, `errors`, `config`, and stdin subcommands with Kong and shellquote parsing.

Risks and test signals: stdin mode ignores the original top-level `cli -` prefix and parses input directly as CLI subcommands. It prints errors instead of aborting per command. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/operations.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/operations.go

Purpose: implements operational REST commands for restart, shutdown, upgrade, folder override, and default ignore updates.

Important APIs/types/functions: `folderOverrideCommand`, `defaultIgnoresCommand`, `operationCommand`, parent `Run`, `folderOverrideCommand.Run`, and `defaultIgnoresCommand.Run`.

Control flow: parent `Run` maps restart/shutdown/upgrade to empty POSTs. Folder override loads config, verifies the folder ID exists, then POSTs `db/override`. Default ignores opens the supplied file through Syncthing filesystem abstraction, reads all lines, and PUTs `config/defaults/ignores`.

State and persistence: sends commands that can restart/shut down/upgrade the running daemon, override folder state, or change config defaults. Folder override is explicitly destructive.

Dependencies/integration: depends on REST API client, config structures, and filesystem abstraction.

Risks and test signals: the folder override implementation verifies the folder exists but posts `db/override` without including the folder ID in this file, so endpoint semantics must infer or this may be a bug depending on API expectations. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/pending.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/pending.go

Purpose: implements `syncthing cli show pending` subcommands.

Important APIs/types/functions: `pendingCommand` and `pendingCommand.Run`.

Control flow: dispatches `devices` to `cluster/pending/devices`; dispatches `folders` to `cluster/pending/folders`, optionally adding a `device` query parameter.

State and persistence: read-only REST access to pending cluster state.

Dependencies/integration: nested under `showCommand` and uses `indexDumpOutputWrapper`.

Risks and test signals: command depends on Kong selected-name matching. No direct tests cover query encoding.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/pending.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/show.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/show.go

Purpose: implements read-only `syncthing cli show` commands.

Important APIs/types/functions: `showCommand` and `showCommand.Run`.

Control flow: selected subcommands call REST endpoints for version, config restart-required status, system status, connections, discovery cache, usage report, and nested pending commands.

State and persistence: read-only; pretty-prints JSON responses.

Dependencies/integration: depends on the API helper wrapper and Kong selected command names.

Risks and test signals: endpoint mappings are simple and therefore sensitive to REST path changes. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/utils.go -->
# sources/sync-backup/syncthing/cmd/syncthing/cli/utils.go

Purpose: shared helpers for `syncthing cli` HTTP responses, pretty printing, file saves, config loading, and path normalization.

Important APIs/functions: `responseToBArray`, `emptyPost`, `indexDumpOutputWrapper`, `indexDumpOutput`, `saveToFile`, `getConfig`, `prettyPrintJSON`, `prettyPrintResponse`, and `normalizePath`.

Control flow: response helpers read and close bodies. Dump helpers fetch REST responses and pretty-print JSON or save raw response bytes to a server-provided filename. `getConfig` fetches `system/config` and unmarshals into `config.Configuration`. `normalizePath` cleans and converts paths to slash-separated form.

State and persistence: `saveToFile` writes local files; `getConfig` and pretty print are read-only; empty posts trigger API side effects.

Dependencies/integration: used by most CLI subcommands and depends on JSON, MIME `Content-Disposition`, filesystem paths, and Syncthing config.

Risks and test signals: pretty printing requires valid JSON, so non-JSON REST responses will error. `saveToFile` uses the server's filename without additional path sanitation. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/cli/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/crash_reporting.go -->
# sources/sync-backup/syncthing/cmd/syncthing/crash_reporting.go

Purpose: uploads panic logs to the configured crash-reporting server and sanitizes log content before upload.

Important APIs/functions: `uploadPanicLogs`, `uploadPanicLog`, and `filterLogLines`; constants `headRequestTimeout` and `putRequestTimeout`.

Control flow: `uploadPanicLogs` globs `panic-*.log`, sorts newest-first, skips already reported files, uploads each, and renames successful uploads to `.reported.log`. `uploadPanicLog` reads a file, filters log lines for privacy, hashes the filtered content as the panic ID, checks if the crash is already known with HEAD, and uploads with PUT on miss. `filterLogLines` keeps the first line and the panic trace starting at a `Panic ` line while stripping device ID prefixes.

State and persistence: reads panic logs and renames reported ones. Network state is remote crash server objects keyed by SHA-256 of filtered content.

Dependencies/integration: called by monitor crash-reporting flow when config enables crash reporting.

Risks and test signals: filtering is privacy-sensitive and pattern-based; stack traces not beginning with `Panic ` may retain only the first line. HTTP responses must be closed and non-200 PUT returns errors. Unit test covers device-prefix stripping and log-line removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/crash_reporting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/crash_reporting_test.go -->
# sources/sync-backup/syncthing/cmd/syncthing/crash_reporting_test.go

Purpose: unit test for panic log filtering.

Important APIs/tests: `TestFilterLogLines`.

Control flow and state: constructs sample log data with a device ID prefix, arbitrary log lines, and a panic marker. It verifies `filterLogLines` returns the first line without device prefix plus the panic section, excluding intervening logs.

Dependencies/integration: depends on `bytes.Equal` and the local filter function.

Risks and test signals: provides regression coverage for privacy filtering. It does not test HEAD/PUT upload behavior, rename-on-success, already-reported skipping, or nonstandard panic prefixes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/crash_reporting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/debug.go -->
# sources/sync-backup/syncthing/cmd/syncthing/debug.go

Purpose: registers the main package with Syncthing's structured logging package registry.

Important APIs/functions: package `init` calls `slogutil.RegisterPackage("Main package")`.

Control flow and state: registration happens at package initialization and contributes to log package descriptions shown in extended help and STTRACE handling.

Dependencies/integration: used by `logPackages` in `main.go` and the logging subsystem.

Risks and test signals: tiny initialization file with no direct tests. Behavior depends on package init ordering only for registry population.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/decrypt/decrypt.go -->
# sources/sync-backup/syncthing/cmd/syncthing/decrypt/decrypt.go

Purpose: implements `syncthing decrypt`, which decrypts or verifies files from an encrypted folder using the folder password and encrypted metadata trailers.

Important APIs/types/functions: `CLI`, `storedEncryptionToken`, `Run`, `walk`, `withContinue`, `getFolderID`, `process`, `decryptFile`, and `loadEncryptedFileInfo`.

Control flow: `Run` validates mode, sets the default token path, discovers folder ID from token when needed, derives the folder key, and walks the encrypted folder. `process` skips non-regular/internal files, loads encrypted `FileInfo` trailer, decrypts metadata, creates destination directories/files when decrypting, decrypts each block, verifies size and hash, writes plaintext blocks, applies permissions and modtime, and deletes partial output on failure. `--verify-only` passes a nil writer and validates without writing.

State and persistence: reads encrypted folder files and token JSON. In decrypt mode, writes plaintext files under `--to`, preserves selected permission bits, and sets modification times.

Dependencies/integration: depends on generated BEP protobufs, Syncthing config constants, filesystem abstraction, OS filename normalization, protocol encryption helpers, and scanner hash validation.

Risks and test signals: wrong password/folder ID causes metadata or block decryption failure. `--continue` logs and continues, but partial outputs are removed on file errors. Large files allocate per encrypted block. No tests in this subset cover decrypt paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/decrypt/decrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/generate/generate.go -->
# sources/sync-backup/syncthing/cmd/syncthing/generate/generate.go

Purpose: implements `syncthing generate`, creating or updating keys and config without starting the daemon.

Important APIs/types/functions: `CLI`, `CLI.Run`, `Generate`, and `updateGUIAuthentication`.

Control flow: `Run` optionally reads GUI password from stdin when `--gui-password=-`, then calls `Generate` for the config base directory. `Generate` expands the directory, ensures it exists, sets locations, loads or creates certificate/key files, calculates device ID, loads existing config or creates default config, starts config wrapper service, optionally updates GUI username/password, waits for modification, and saves config.

State and persistence: creates or reuses cert/key files, creates config directory, creates or modifies `config.xml`, and writes password hashes through config GUI helpers.

Dependencies/integration: uses Syncthing config, events, filesystem, locations, protocol device IDs, and `lib/syncthing` certificate/default config helpers.

Risks and test signals: existing keys are intentionally not overwritten. Password read from stdin reads one line only. Config wrapper is transient but required for safe modification. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/generate/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/heapprof.go -->
# sources/sync-backup/syncthing/cmd/syncthing/heapprof.go

Purpose: optional debug heap profiler for the Syncthing process.

Important APIs/functions: `startHeapProfiler` and `saveHeapProfiles`.

Control flow: `startHeapProfiler` starts a goroutine and panics if profile saving fails. `saveHeapProfiles` sets `runtime.MemProfileRate`, periodically reads memory stats, and when `HeapInuse` increases writes a heap profile to `heap-<pid>.pprof.tmp`, closes it, removes the old target, and renames atomically.

State and persistence: writes one rolling heap profile file in the working directory and mutates runtime memory profiling rate.

Dependencies/integration: enabled by `serveCmd.syncthingMain` debug flags/env.

Risks and test signals: high-frequency polling and low profile rate can affect performance. Errors abort via panic. No tests cover profiler file lifecycle.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/heapprof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/hideconsole_others.go -->
# sources/sync-backup/syncthing/cmd/syncthing/hideconsole_others.go

Purpose: non-Windows build-specific CLI option definition.

Important APIs/types: `buildSpecificOptions` with hidden `HideConsole`.

Control flow and state: build tags select this file on non-Windows, keeping the `serveCmd` field portable while hiding the no-console option.

Dependencies/integration: embedded in `serveCmd` in `main.go`.

Risks and test signals: no runtime behavior on non-Windows. Build tag correctness is the main signal; no tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/hideconsole_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/hideconsole_windows.go -->
# sources/sync-backup/syncthing/cmd/syncthing/hideconsole_windows.go

Purpose: Windows build-specific CLI option definition for hiding the console.

Important APIs/types: `buildSpecificOptions` with `HideConsole` exposed as `--no-console` and environment `STHIDECONSOLE`.

Control flow and state: when selected by Windows builds, `serveCmd.Run` can call `osutil.HideConsole()` if this flag is set.

Dependencies/integration: embedded in `serveCmd` in `main.go` and tied to Windows console behavior.

Risks and test signals: option text notes Windows 11 24H2 behavior. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/hideconsole_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/main.go -->
# sources/sync-backup/syncthing/cmd/syncthing/main.go

Purpose: primary Syncthing command entrypoint, command tree, serving lifecycle, upgrade logic, debug commands, and startup/shutdown orchestration.

Important APIs/types/functions: top-level `CLI`, `serveCmd`, `defaultVars`, `main`, `helpHandler`, `serveCmd.Run`, `openGUI`, `checkUpgrade`, `upgradeViaRest`, `syncthingMain`, `setupSignalHandling`, `loadOrDefaultConfig`, `auditWriter`, `autoUpgrade`, `initialAutoUpgradeCheck`, `cleanConfigDirectory`, `setPauseState`, command structs for version/device-id/paths/upgrade/browser/debug, database debug commands, `setConfigDataLocationsFromFlags`, and `migratingAPI`.

Control flow: `main` builds a Kong parser, handles shell completion and version flag, then runs the selected command. `serveCmd.Run` applies GUI override env vars, console hiding, logging format/level, log and GUI asset locations, ensures config/data directories, and either runs the monitored child or inner Syncthing process. `syncthingMain` starts debug profilers, loads/generates certs, locks the instance, starts early services and config, performs database migration/open, optionally performs initial auto-upgrade, adjusts pause state, creates the Syncthing app with audit/profiler options, starts auto-upgrade and signal handlers, starts the app, cleans old config/data artifacts, optionally opens browser, waits for app exit, stops CPU profiling, unlocks, and exits with service status.

State and persistence: manages config/data locations, cert/key files, lock file, database, audit logs, cleanup of old panic/audit/config/support files, upgrade metadata in misc DB, and optional profile files. Direct debug commands can remove the database or inspect SQLite statistics/files.

Dependencies/integration: central integration point for `cli`, `decrypt`, `generate`, database/sqlite, config/events/locations, `lib/syncthing`, upgrade, Suture services, flock, OS signals, logging, and monitor mode.

Risks and test signals: startup has many exit paths with process termination rather than returned errors. Upgrade timing gates prevent repeated early upgrade attempts. `loadOrDefaultConfig` creates a temporary wrapper on any load error, not only missing files, which is acceptable for some commands but risky if callers expect strict config validation. `setConfigDataLocationsFromFlags` enforces `--config` and `--data` together. No tests in this subset directly cover main lifecycle.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/monitor.go -->
# sources/sync-backup/syncthing/cmd/syncthing/monitor.go

Purpose: outer monitor process for Syncthing, handling child restarts, log rotation/autoclose, panic log capture/reporting, and monitor self-restart after upgrades.

Important APIs/types/functions: stdout line buffers, restart/log/panic constants, `serveCmd.monitorMain`, `getBinary`, `copyStderr`, `copyStdout`, `restartMonitor`, platform restart helpers, `rotatedFile`, `newRotatedFile`, `Write`, `rotate`, `numberedFile`, `autoclosedFile`, `newAutoclosedFile`, `Write`, `Close`, `ensureOpenLocked`, `closerLoop`, `childEnv`, and `maybeReportPanics`.

Control flow: `monitorMain` configures stdout plus optional file logging with rotation and autoclosed files, resolves the executable, filters child env and adds `STMONITORED=yes`, reports existing panics, enforces restart-loop protection, starts the inner process, copies stdout/stderr concurrently, forwards INT/TERM/SIGHUP as stop/restart signals, interprets child exit codes, self-execs on upgrade on Unix, and restarts on crashes unless disabled. `copyStderr` detects panic/fatal/runtime prefixes, creates timestamped panic logs, includes early and recent stdout context, and triggers crash reporting after close.

State and persistence: writes log files with rotation, panic logs, and reported panic renames through `crash_reporting.go`. Keeps first 10 and last 50 stdout lines in memory for panic context.

Dependencies/integration: tightly coupled with `serveCmd.Run`, `svcutil` exit codes, locations, build OS checks, crash reporting config, and platform-specific restart behavior.

Risks and test signals: restart-loop threshold protects against rapid crash cycles. Log rotation errors are printed to stdout rather than fatal. Autoclosed files reduce long-held descriptors. Existing monitor tests are outside this work item, but not mapped here; this file's assigned scope has no direct mapped test doc.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/monitor.go -->
