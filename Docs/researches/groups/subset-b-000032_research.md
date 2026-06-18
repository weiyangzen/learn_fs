# Research Report: subset-b-000032

This grouped report covers the BuildKit utility files assigned to `subset-b-000032`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display.go -->
# sources/cloud-native/buildkit/util/progress/progressui/display.go

Purpose: implements BuildKit solve progress rendering across quiet, plain text, TTY, and raw JSON modes. It owns the in-memory `trace` model that turns `client.SolveStatus` streams into terminal jobs, status rows, warning rows, terminal log panes, and final error log dumps.

Important APIs and types: `Display`, `DisplayMode`, `DisplayOpt`, `WithPhase`, `WithDesc`, and `NewDisplay` are the public construction surface. Internally `display` abstracts `init`, `update`, `refresh`, and `done`; concrete implementations are `discardDisplay`, `consoleDisplay`, `plainDisplay`, and `rawJSONDisplay`. The `trace`, `vertex`, `vertexGroup`, `interval`, `status`, `displayInfo`, `job`, and `ttyDisplay` types hold the accumulated solve state.

Control flow: `Display.UpdateFrom` initializes the chosen display, then selects on context cancellation, a refresh ticker, and solve status messages. TTY and plain displays rate-limit expensive rendering through `golang.org/x/time/rate`; raw JSON encodes every status immediately. `trace.update` ingests vertices, grouped vertices, statuses, warnings, and logs; it detects vertex transitions, merges progress-group state, updates virtual terminals, and records changed digests. `displayInfo` converts trace state into printable jobs, and `ttyDisplay.print` redraws the console using ANSI cursor movement.

State and persistence: all state is process-local. The trace caches vertices by digest, group state by progress group ID, merged time intervals, warning offsets, text log buffers, vt100 terminal buffers, and cached job projections. Environment variables affect behavior: `TTY_DISPLAY_RATE`, `PROGRESS_NO_TRUNC`, and terminal sizing state shared through package globals in `init.go`.

Dependencies and integration: integrates with BuildKit client solve status types, containerd console detection, vt100 terminal emulation, ANSI coloring, OCI digest keys, and BuildKit progress writers. It is the display sink used by `progresswriter.NewPrinter`.

Risks: terminal redraw correctness depends on terminal width/height and shared package globals (`termHeight`) mutated during rendering. Plain output suppresses frequent status changes, which is intentional but can hide very small progress deltas. Grouped vertices alias subvertex digests to the group vertex, so code that assumes one digest maps to one concrete vertex would be wrong. Log buffers are bounded only for text error printing; TTY trace keeps original logs for error dump.

Test signals: `display_test.go` covers `mergeIntervals`, including nil starts, adjacent intervals, overlaps, and open intervals. The rest of the rendering path is mostly untested here and relies on integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display_test.go -->
# sources/cloud-native/buildkit/util/progress/progressui/display_test.go

Purpose: table-driven unit tests for `mergeIntervals`, the time-interval normalization helper used by progress grouping and job duration display.

Important APIs and types: local helpers `mkinterval` and `mkOpenInterval` build `interval` values with concrete `time.Time` pointers. `TestMergeIntervals` exercises the unexported `mergeIntervals` function.

Control flow: each case passes a slice of intervals and asserts exact equality against the expected merged slice. Cases cover empty input, single intervals, nil-start filtering, duplicate/equal intervals, disjoint ranges, subsumed ranges, partial overlap chains, adjacent boundaries, open intervals, and a mixed complex case.

State and persistence: test-only in-memory data; no filesystem or environment state.

Dependencies and integration: uses `testing`, `time`, and `testify/require`. It directly validates the helper used by `vertexGroup.refresh`, `trace.displayInfo`, and text completion duration calculation.

Risks: tests do not exercise terminal rendering, progress-group aliasing, warning/log buffering, or rate limiting. They do protect a core invariant: open intervals consume later overlapping intervals and nil starts are omitted.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/init.go -->
# sources/cloud-native/buildkit/util/progress/progressui/init.go

Purpose: initializes package-level color and terminal log-height defaults for progress UI rendering.

Important APIs and types: package globals `colorRun`, `colorCancel`, `colorWarning`, `colorError`, `termHeightInitial`, and `termHeight` are consumed by `display.go` and `printer.go`. The `init` function configures them at process startup.

Control flow: if `NO_COLOR` is set, color globals remain nil so no ANSI color is applied. Windows defaults use cyan for completed/running rows; other platforms use blue. `BUILDKIT_COLORS` invokes `setUserDefinedTermColors` from the sibling color parser. `BUILDKIT_TTY_LOG_LINES` overrides the initial virtual terminal log pane height when it parses as a positive integer.

State and persistence: state is package-global and mutable. `termHeight` is later adjusted by TTY rendering as terminal dimensions change, so concurrent displays would share height state.

Dependencies and integration: depends on runtime GOOS, environment variables, and the package color map. It directly affects `ttyDisplay.print` color choices and vt100 sizing.

Risks: environment is read only once at package initialization. Invalid height input is silently ignored. Shared globals make behavior process-wide rather than display-instance-specific.

Test signals: no direct tests in this subset; behavior is exercised indirectly by display rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/printer.go -->
# sources/cloud-native/buildkit/util/progress/progressui/printer.go

Purpose: implements the plain text multiplexer used by progress UI plain mode. It serializes vertex transitions, status updates, warnings, logs, and completion markers into a stable human-readable stream.

Important APIs and types: `textMux.printVtx`, `textMux.print`, `sortCompleted`, `lastStatus`, `limitString`, and constants controlling anti-flicker and progress throttling. It operates on the `trace` and `vertex` types defined in `display.go`.

Control flow: `printVtx` assigns numeric vertex indexes, emits a header when switching active vertices, flushes pending events, prints status deltas only when progress/time thresholds warrant, emits new warnings, writes log lines with vertex prefixes, and prints terminal state (`DONE`, `CACHED`, `ERROR`, or `CANCELED`) when a vertex is complete and has no open status. `print` decides which changed/completed vertices to emit first and uses `sortCompleted` for deterministic completion ordering.

State and persistence: `textMux` tracks the current digest, last status progress by status ID, whether the initial description has been printed, and the next display index. Vertices retain log offsets, ring buffers for last logs, warning indexes, event lists, and counts.

Dependencies and integration: depends on OCI digest keys, `units.Bytes`, environment variable `PROGRESS_NO_TRUNC`, and the trace model from `display.go`. It is created by `newPlainDisplay`.

Risks: throttling can defer status lines until either enough time or enough progress has elapsed. Status IDs are tracked globally in `textMux.last`, so non-unique IDs across vertices could affect anti-flicker behavior. The log ring stores only recent log lines for error replay in plain mode.

Test signals: no direct tests for text formatting; `display_test.go` covers interval merging used by completion duration summaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/printer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go

Purpose: multiplexes multiple prefixed progress streams into a single underlying `Writer`, allowing parallel sub-operations to report into one solve status channel.

Important APIs and types: `MultiWriter`, `NewMultiWriter`, `WithPrefix`, `prefixed`, and helper `addPrefix`.

Control flow: `NewMultiWriter` wraps an existing writer and starts a goroutine that waits until at least one prefixed stream is ready, then waits for all prefix goroutines before closing the underlying status channel. `WithPrefix` creates an input channel; a goroutine reads statuses, optionally rewrites vertex names with `addPrefix`, and forwards to the underlying writer status channel until input closes or the main writer completes.

State and persistence: in-memory only. `errgroup.Group`, `sync.Once`, and `ready` coordinate lifecycle. `MultiWriter.Status` intentionally returns nil; callers use per-prefix writers instead.

Dependencies and integration: uses BuildKit `client.SolveStatus`, `errgroup`, and the `Writer` interface from this package. Prefix formatting preserves existing bracketed names by inserting the prefix after the opening bracket.

Risks: underlying status channel closure waits for `ready`; if no prefixed writer is ever created, the closure goroutine blocks. Forwarding mutates vertex names in the received status object when `force` is true, which affects any other consumer of the same pointers.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/multiwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/printer.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/printer.go

Purpose: adapts `progressui.Display` into the generic progress `Writer` interface and provides a tee wrapper for duplicating solve status streams.

Important APIs and types: `printer`, `tee`, `Tee`, and `NewPrinter`.

Control flow: `NewPrinter` creates a status channel and done channel, resolves `BUILDKIT_PROGRESS` when requested mode is `auto`, constructs a progress UI display, and runs `Display.UpdateFrom` in a goroutine. `Tee` forwards every incoming status to both the wrapped writer and an external channel, then closes both downstream channels when its own channel closes.

State and persistence: `printer.err` captures the display loop result after the goroutine exits; callers observe completion via `Done`. No persistent storage.

Dependencies and integration: depends on `containerd/console.File`, BuildKit client status types, and `progressui.NewDisplay`. Used by CLI and solve paths that need terminal progress.

Risks: `Tee` writes sequentially to both outputs and can block if either receiver stalls. `NewPrinter` does not use a separate context; it passes the supplied context into display update so cancellation ends the display loop.

Test signals: no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/printer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/progress.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/progress.go

Purpose: offers a lightweight logger facade that turns arbitrary nested operations and log bytes into BuildKit `client.SolveStatus` messages.

Important APIs and types: `Logger`, `SubLogger`, `Wrap`, `subLogger.Wrap`, and `subLogger.Log`.

Control flow: top-level `Wrap` emits a new vertex with a generated digest and start time, invokes the callback with a `SubLogger`, then defers a completion vertex containing any error string. Nested `subLogger.Wrap` emits `VertexStatus` start/completion pairs under the parent digest. `Log` emits a `VertexLog` with stream, bytes, and timestamp.

State and persistence: no shared state; each wrapped operation gets an identity-derived digest and local timestamps.

Dependencies and integration: uses BuildKit client status structs, `identity.NewID`, OCI digests, and `time.Now`. It feeds any `Logger` function, including writers that send to progress UI.

Risks: if the logger is nil, `Wrap` returns nil without invoking the supplied callback, which is a subtle behavior and likely intentional for disabled progress but surprising to generic callers. The function does not recover panics.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/reset.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/reset.go

Purpose: wraps a progress writer and shifts incoming timestamps so the first observed vertex start aligns with wrapper creation time.

Important APIs and types: `ResetTime` and internal `pw`.

Control flow: `ResetTime` creates a wrapper status channel and goroutine. The first status containing a started vertex establishes `diff = firstStarted - wrapperCreationTime`. Subsequent vertex, status, and log timestamps are copied and shifted backward by that diff before forwarding to the underlying writer. Closing the wrapper status channel closes the underlying status channel.

State and persistence: in-memory diff state only. The wrapper embeds the underlying writer and overrides `Status`.

Dependencies and integration: uses BuildKit client status structs and the package `Writer` interface.

Risks: until a vertex with `Started` appears, statuses pass through unchanged. The wrapper copies top-level status slices but preserves warning pointers as-is. The goroutine exits on underlying `Done` without closing wrapper status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/reset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/writer.go -->
# sources/cloud-native/buildkit/util/progress/progresswriter/writer.go

Purpose: defines the common progress writer contract and a helper for emitting a one-step vertex around a function.

Important APIs and types: `Writer` interface with `Done`, `Err`, and `Status`; helper `Write`.

Control flow: `Write` generates a digest, sends a started vertex, invokes the optional function, then sends a completed vertex with any error message captured from the function.

State and persistence: no persistent state; writes directly to the writer status channel.

Dependencies and integration: depends on BuildKit client types, identity IDs, OCI digests, and `time.Now`. Used by code that needs simple progress spans without full logger nesting.

Risks: `Write` ignores the writer `Done` channel and can block forever if the status receiver is not reading. It discards the callback error after embedding it in progress status.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progresswriter/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pull.go -->
# sources/cloud-native/buildkit/util/pull/pull.go

Purpose: resolves and pulls image manifests and non-layer metadata while deliberately skipping layer blob downloads so lazy layer providers can fetch layer content later.

Important APIs and types: `SessionResolver`, `Puller`, `PulledManifests`, `Puller.PullManifests`, provider `ReaderAt`, `filterLayerBlobs`, and `getLayers`.

Control flow: `Puller.resolve` flightcontrols remote/local resolution and caches the descriptor or error. `tryLocalResolve` resolves digest-pinned content from the content store when it has matching distribution source labels. `PullManifests` resolves the reference, constructs platform-filtered image handlers, fetches only metadata/config/nonlayer descriptors through `images.Dispatch`, rejects Docker schema1 manifests, derives layer descriptors and diffID annotations through `getLayers`, and returns a session-aware content provider for later fetches.

State and persistence: `Puller` caches resolution state, descriptors, layer and nonlayer lists, and errors in memory. Content persistence happens through the provided containerd content store, distribution source labels, and fetch handlers.

Dependencies and integration: integrates with containerd content/images/remotes/docker, BuildKit sessions, flightcontrol, image media detection, resolver concurrency limiting, retry handler, and progress logging. The returned provider calls session-specific resolvers to fetch blobs.

Risks: `resolveErr` is cached except for context cancellation; transient non-cancel errors can poison a `Puller` instance. Metadata map is protected because containerd dispatch handlers may run in parallel. Lazy layer semantics depend on `filterLayerBlobs` recognizing all layer media types.

Test signals: no direct tests in this subset; behavior is typically covered by image pull/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pullprogress/progress.go -->
# sources/cloud-native/buildkit/util/pull/pullprogress/progress.go

Purpose: wraps content providers and remote fetchers so reads/fetches emit progress based on content ingest or stored content status.

Important APIs and types: `PullManager`, `ProviderWithProgress`, `FetcherWithProgress`, `readerAtWithCancel`, `readerWithCancel`, and `trackProgress`.

Control flow: `ReaderAt` and `Fetch` delegate to the underlying provider/fetcher, then start `trackProgress` in a context detached from caller cancellation but canceled when the returned reader is closed. `trackProgress` ticks every 150ms, checks active ingest status with `remotes.MakeRefKey`, writes progress via `progress.NewFromContext`, and falls back to content `Info` to emit a final completed status when the blob is present.

State and persistence: progress goroutines are bound to reader lifetimes. Content state is read from the provided manager; no new persistent state is created beyond progress messages.

Dependencies and integration: uses containerd content/remotes, BuildKit progress context, BuildKit logging, and errdefs for not-found detection.

Risks: `Close` waits up to one second for the progress goroutine before warning, so leaked readers can leak progress goroutines. `context.WithoutCancel` intentionally keeps progress alive past caller cancellation until reader close.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pullprogress/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image.go -->
# sources/cloud-native/buildkit/util/purl/image.go

Purpose: converts Docker/OCI image references with optional platform information to and from package-url (`purl`) strings.

Important APIs and types: `RefToPURL` and `PURLToRef`.

Control flow: `RefToPURL` parses and normalizes an image reference, records digest as a `digest` qualifier for canonical refs, extracts tag as package version when present, collapses familiar Docker names into namespace/name fields, and appends normalized platform as a qualifier. `PURLToRef` parses purl strings, requires type `docker`, rebuilds a reference from namespace/name/version/digest qualifiers, parses a platform qualifier while clearing OSVersion/OSFeatures that containerd may infer, defaults tag to `latest` when neither version nor digest exists, then validates through distribution reference parsing.

State and persistence: pure conversion; no process or filesystem state.

Dependencies and integration: uses distribution/reference, containerd/platforms, OCI digest and platform specs, and packageurl-go. Intended for SBOM/package identity and image reference interchange.

Risks: digest can be represented either as a version that parses as a digest or as a qualifier; mismatches are rejected. Only Docker purl type is accepted in reverse conversion. Platform string parsing may still normalize OS/architecture according to containerd behavior.

Test signals: `image_test.go` covers default tags, Docker Hub familiar names, registry namespaces, canonical digests, digest qualifier/version interactions, platforms, and invalid types/refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image_test.go -->
# sources/cloud-native/buildkit/util/purl/image_test.go

Purpose: validates image reference to package-url conversion and package-url back to normalized image reference conversion.

Important APIs and types: `TestRefToPURL` and `TestPURLToRef` exercise `RefToPURL` and `PURLToRef` with `packageurl.TypeDocker`, OCI platform specs, and generated digests.

Control flow: tests run table cases for plain names, tags, Docker Hub familiar forms, canonical refs, registry names, platform qualifiers, invalid refs, invalid purl types, and digest-bearing purls.

State and persistence: pure table tests with no external state.

Dependencies and integration: uses `net/url` for expected escaped platform strings, containerd platform normalization, OCI specs, packageurl-go, and `testify/require`.

Risks: tests intentionally normalize platform OSVersion to empty before comparison because purl platform strings cannot carry all platform fields. No fuzzing of arbitrary purl qualifier ordering or malformed digest/version combinations beyond listed cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/push/push.go -->
# sources/cloud-native/buildkit/util/push/push.go

Purpose: pushes image content and manifests to a registry with BuildKit resolver/auth integration, deduplication, retries, concurrency limiting, and distribution source label updates.

Important APIs and types: `Pusher`, `Push`, `skipNonDistributableBlobs`, `annotateDistributionSourceHandler`, `childrenHandler`, `updateDistributionSourceHandler`, and `dedupeHandler`.

Control flow: `Push` normalizes target references, handles by-digest mode, builds an insecure registry host callback when requested, gets a pooled resolver, creates a masked pusher wrapper, traverses image children, pushes layers/configs with retry and concurrency limiting, records manifest descriptors separately, and finally pushes manifests in reverse stack order. Child traversal adds distribution-source annotations from explicit annotations and content labels.

State and persistence: persistent side effects are registry uploads and content-store distribution source label updates after successful layer pushes. In-memory state includes a manifest stack, dedupe cache, and flightcontrol group.

Dependencies and integration: uses containerd content/images/remotes/docker, BuildKit sessions, progress, logs, resolver pool/config, limited concurrency, retry handler, image media detection, and in-toto payload type handling.

Risks: comments note a race in distribution source label updates when concurrent pull/push jobs consume the same layer. `childrenHandler` assumes OCI manifest/index shape even for Docker mediatypes. By-digest mode rejects tagged refs to avoid ambiguous push targets.

Test signals: no direct tests in this subset; image push behavior is integration-heavy.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/push/push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/registrar/registrar.go -->
# sources/cloud-native/buildkit/util/registrar/registrar.go

Purpose: generic concurrent registrar that lets callers register a value by key and lets other callers wait briefly for that value to appear.

Important APIs and types: `Registrar[K,V]`, `New`, `Register`, `Get`, `Discard`, `getOrCreateRegistrar`, and internal `registrarValue`.

Control flow: `Get` creates or retrieves a keyed `registrarValue`, starts a three-second discard timer only for newly created missing registrations, then waits for context cancellation or `notifyCh` closure. `Register` stores a value and closes the notification channel once. `Discard` removes the entry and signals waiters with `context.Canceled`.

State and persistence: process-local map protected by a mutex; per-value state has its own mutex and closed channel. Values persist until explicitly discarded.

Dependencies and integration: depends only on context, sync, and time. Useful for bridging asynchronous component registration.

Risks: `getOrCreateRegistrar` invokes `onCreate` while holding the registrar mutex, but in a goroutine; the timer can race with real registration and will call `Discard` after three seconds if still pending. Once a registrar value is set, subsequent registrations are ignored.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/registrar/registrar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf.go -->
# sources/cloud-native/buildkit/util/resolvconf/resolvconf.go

Purpose: parses, modifies, transforms, and regenerates container `resolv.conf` content for host, legacy network, and internal DNS resolver scenarios.

Important APIs and types: `ResolvConf`, `ExtDNSEntry`, `Load`, `Parse`, `SetHeader`, `NameServers`, `OverrideNameServers`, `Search`, `OverrideSearch`, `Options`, `Option`, `OverrideOptions`, `AddOption`, `TransformForLegacyNw`, `TransformForIntNS`, and `Generate`.

Control flow: parsing scans recognized directives, keeping valid nameservers, last search/domain directive, accumulated options, unknown directives, invalid nameserver metadata, and ndots origin. Legacy transform removes host loopback and IPv6 nameservers as needed unless nameservers were overridden, then adds Google fallback resolvers if empty. Internal resolver transform stashes existing nameservers as external DNS entries, marks host-loopback ownership based on overrides, replaces visible nameserver with internalNS, and ensures required options exist while replacing invalid `ndots` values.

State and persistence: all state is held in `ResolvConf` fields and metadata until `Generate` writes bytes. Metadata controls generated debug comments, override tracking, transform labels, invalid nameserver lists, and external server comments.

Dependencies and integration: uses `net/netip`, BuildKit errdefs and logging. Integrated by networking code that needs container DNS config and by internal resolver setup that consumes returned external DNS entries.

Risks: comments can expose source path and external resolver addresses. `OverrideSearch` filters `"."`, but other search validation is minimal. `TransformForLegacyNw` does nothing when nameservers are overridden, even if loopback addresses are unusable in a target network. Internal resolver transform warns but does not inject fallback external servers when no external entries exist.

Test signals: `resolvconf_test.go` thoroughly covers option lookup, overrides, legacy transforms, internal resolver transforms, invalid ndots replacement, load/path behavior, invalid nameserver reporting, headers, unknown directives, and generation benchmark.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go -->
# sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go

Purpose: comprehensive unit coverage for the resolv.conf parser, mutators, transforms, generator comments, invalid input handling, and benchmark performance.

Important APIs and types: `TestRCOption`, `TestRCModify`, `TestRCTransformForLegacyNw`, `TestRCTransformForIntNS`, `TestRCTransformForIntNSInvalidNdots`, `TestRCRead`, `TestRCInvalidNS`, `TestRCSetHeader`, `TestRCUnknownDirectives`, `BenchmarkGenerate`, and helper `sliceutilMapper`.

Control flow: tests construct input files with strings or temp files, call parse/load/mutator/transform methods, then assert generated content and exposed slices. Internal resolver tests also compare returned `ExtDNSEntry` values including `HostLoopback` semantics.

State and persistence: temporary filesystem use is limited to `TestRCRead`; all other tests are in memory.

Dependencies and integration: uses `net/netip`, `os`, `filepath`, string builders, and `testify` assertions. Test data documents intended generated comment format.

Risks: expected output strings are exact, so harmless formatting changes require coordinated updates. Tests cover many DNS paths but do not exercise concurrent use; `ResolvConf` is mutable and not designed as thread-safe.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer.go -->
# sources/cloud-native/buildkit/util/resolver/authorizer.go

Purpose: implements Docker registry request authorization for BuildKit resolvers, including Basic auth, Bearer token flow, BuildKit session credential lookup, delegated token authority, token caching, and scope normalization.

Important APIs and types: `authHandlerNS`, `dockerAuthorizer`, `authFetcher`, `authResult`, `parseScopes`, `scopes.normalize`, `scopes.contains`, `invalidAuthorization`, and `sameRequest`.

Control flow: `Authorize` finds a cached `authFetcher` for the request host/session and sets an Authorization header. `AddResponses` parses registry auth challenges from a 401 response, invalidates handlers on repeated invalid auth, obtains token authority or credentials from BuildKit sessions, creates a fetcher for Bearer or Basic auth, and merges old scopes. Bearer authorization normalizes token scopes from context, flightcontrols token fetches by scope string, reuses unexpired scoped tokens, and fetches via session token authority, OAuth, token GET, or anonymous token flow.

State and persistence: `authHandlerNS` maintains host/session keyed fetchers and host configs. `authFetcher` caches scoped bearer tokens with expiry at 90 percent of server lifetime and records `lastUsed` for pool GC. State is process-local and guarded by mutexes/flightcontrol.

Dependencies and integration: integrates with containerd docker auth/challenge handling, BuildKit session auth provider, resolver pool, BuildKit logging/version user-agent, and containerd remotes error types.

Risks: credential and token cache keys are security-sensitive; push scopes are isolated by session in `pool.go`, while pull-only scopes are shared. Insufficient-scope handling only treats repeated same-request errors as fatal. Anonymous token fallback is intentional when no active session exists. Scope parsing returns nil for empty scope input, so callers must tolerate nil maps.

Test signals: `authorizer_test.go` covers scope parsing and anonymous bearer token fallback without a session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer_test.go -->
# sources/cloud-native/buildkit/util/resolver/authorizer_test.go

Purpose: verifies resolver auth helper behavior for scope parsing and no-session anonymous bearer token acquisition.

Important APIs and types: `TestParseScopes` and `TestBearerAuthFallsBackToAnonymousTokenWithoutSession`.

Control flow: scope tests compare parsed map structures for invalid empty scopes, separate scope strings, and combined space-delimited scope strings. The bearer test starts an HTTP token server, synthesizes a registry 401 Bearer challenge, calls `AddResponses`, then verifies `Authorize` fetches and applies an anonymous bearer token with no Authorization header on the token request.

State and persistence: in-memory test HTTP server and session manager only.

Dependencies and integration: uses `httptest`, BuildKit `session.Manager`, `testify/require`, and the unexported authorizer constructors.

Risks: tests do not cover Basic auth, token caching expiry, delegated token authority, invalid authorization retries, OAuth fallback, or session-specific cache linking.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/authorizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/config/config.go -->
# sources/cloud-native/buildkit/util/resolver/config/config.go

Purpose: defines the TOML-facing registry configuration shape consumed by resolver construction.

Important APIs and types: `RegistryConfig` and `TLSKeyPair`.

Control flow: no functions; struct tags map mirrors, plain HTTP, insecure TLS, CA files, client keypairs, and TLS config directories to BuildKit daemon config.

State and persistence: values are loaded by configuration code elsewhere and passed to `resolver.NewRegistryConfig`.

Dependencies and integration: imported by `util/resolver/resolver.go` and likely by daemon config conversion. The optional bool pointers distinguish unset values from explicit false.

Risks: because fields are simple paths and booleans, validation happens downstream while loading TLS config or constructing registry hosts.

Test signals: `resolver_test.go` indirectly exercises mirror configuration behavior from daemon config.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/limited/group.go -->
# sources/cloud-native/buildkit/util/resolver/limited/group.go

Purpose: limits concurrent registry fetch and push operations per registry domain, while giving JSON metadata requests one extra high-priority slot.

Important APIs and types: `Group`, `Default`, `DefaultMaxConcurrency`, `SetMaxConcurrency`, `WrapFetcher`, `PushHandler`, package-level `FetchHandler` and `PushHandler`, and internal `req`/`readCloser`.

Control flow: `req.acquire` skips limiting if the context already has the package marker, derives high priority from media type suffix `+json`, acquires semaphores, and returns a release function. Fetch wrappers hold slots until the returned reader closes and attach a finalizer warning/release path if not closed. Push wrappers acquire around each descriptor handler call.

State and persistence: `Group` stores per-domain semaphore pairs in memory. The default group is replaceable via `SetMaxConcurrency`.

Dependencies and integration: wraps containerd remotes fetch/push handlers, content providers/ingesters, OCI descriptors, BuildKit logging, and distribution reference parsing for domain extraction.

Risks: leaked readers delay semaphore release until finalizer execution and log a warning. The default group is mutable global state. High-priority JSON requests still acquire the total semaphore, allowing at most one extra metadata connection per domain.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/limited/group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/pool.go -->
# sources/cloud-native/buildkit/util/resolver/pool.go

Purpose: provides a shared resolver/auth-handler pool with local image-store fallback modes and session-aware resolver cloning.

Important APIs and types: `DefaultPool`, `Pool`, `NewPool`, `Clear`, `GetResolver`, `Resolver`, `ScopeType`, `ResolveMode`, `ParseImageResolveMode`, `WithSession`, `WithImageStore`, `ResolveLocal`, `Resolve`, and `Fetcher`.

Control flow: `GetResolver` normalizes the reference name, builds a cache key from image name and scope, includes session IDs for push scopes, creates or reuses an auth handler namespace, and returns a new resolver wrapper. `Pool.gc` runs every five minutes, removing stale auth fetchers that have not been used for ten minutes or whose sessions are gone. `Resolver.HostsFunc` flightcontrols registry host lookup and attaches a fresh authorizer to copied host entries. Resolve modes prefer remote, force remote, or prefer local image store.

State and persistence: process-local pool map keyed by scope/name, auth fetcher caches, host config caches, image-store pointer, and resolve mode. No disk persistence.

Dependencies and integration: uses containerd docker resolver, images store, BuildKit sessions, protobuf resolve mode constants, BuildKit logging, and `authorizer.go`.

Risks: pull-only auth handlers are intentionally shared across sessions; push handlers include session IDs to avoid leaking write-capable credentials. `Fetcher` calls `Resolve` first when the auth counter is zero to populate auth challenge state. GC runs forever via `time.AfterFunc`.

Test signals: no direct pool tests in this subset; resolver tests focus on mirror host parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver.go -->
# sources/cloud-native/buildkit/util/resolver/resolver.go

Purpose: converts BuildKit registry config into containerd Docker registry hosts, configures TLS/HTTP clients, supports mirrors, and provides HTTPS-to-HTTP fallback for insecure localhost/plain HTTP behavior.

Important APIs and types: `NewRegistryConfig`, `fillInsecureOpts`, `loadTLSConfig`, `newMirrorRegistryHost`, `newDefaultClient`, `newDefaultTransport`, `httpFallback`, `isTLSError`, and `isPortError`.

Control flow: `NewRegistryConfig` returns a `docker.RegistryHosts` callback that emits configured mirrors first, then the canonical registry host, rewriting `docker.io` to `registry-1.docker.io`. TLS config loading reads CA files, client cert/key pairs, and `.crt`/`.cert` files from TLS config directories. Insecure config sets `InsecureSkipVerify`; plain HTTP config switches scheme or wraps HTTPS transport with fallback. `httpFallback` tries HTTPS first per host, then retries HTTP on TLS/port errors and remembers the host.

State and persistence: TLS config is built from filesystem certificate paths at resolver creation time. `httpFallback` stores one host string protected by a mutex.

Dependencies and integration: uses containerd docker remotes, BuildKit resolver config, tracing transport wrapper, Go TLS/x509/http transports, and OS filesystem APIs.

Risks: insecure mode disables certificate verification. HTTP fallback only retries without a specified port for connection-refused/timeouts, preventing unexpected port changes. Directory scanning ignores missing/permission-denied TLS directories but fails on other read errors.

Test signals: `resolver_test.go` validates mirror host/path parsing and `/v2` path joining for configured mirrors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver_test.go -->
# sources/cloud-native/buildkit/util/resolver/resolver_test.go

Purpose: validates construction of mirror registry host entries from daemon registry mirror config strings.

Important APIs and types: `TestNewMirrorRegistryHost` exercises `newMirrorRegistryHost` using config loaded by `cmd/buildkitd/config`.

Control flow: test parses a TOML registry config with mirrors with and without schemes and paths. For each mirror it asserts parsed host and resulting registry path, including joining mirror path under default `/v2`.

State and persistence: in-memory config parsing only.

Dependencies and integration: uses daemon config loader, `path.Join`, and `testify/require`.

Risks: coverage is narrow: no TLS config, insecure/plain HTTP, fallback, resolver pool, or auth host callback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go -->
# sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go

Purpose: wraps image descriptor handlers with exponential retry for transient registry/network failures.

Important APIs and types: package variable `MaxRetryBackoff`, `New`, and `retryError`.

Control flow: the wrapper calls the underlying handler, returns immediately on success or non-retryable error, logs errors/retry delays when logger is supplied, sleeps with exponential backoff starting at one second, and stops once backoff reaches `MaxRetryBackoff`. Context cancellation short-circuits with the current error.

State and persistence: no persistence; `MaxRetryBackoff` is mutable global configuration for embedders.

Dependencies and integration: used by pull and push handlers around limited fetch/push operations. Recognizes containerd unexpected 5xx statuses, `io.EOF`, connection reset/pipe/closed errors, and temporary net errors.

Risks: uses `time.Sleep` rather than a context-aware timer, so cancellation during sleep is not observed until after sleep returns. Retry budget is time/backoff based, not attempt-count based.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/utils.go -->
# sources/cloud-native/buildkit/util/resolver/utils.go

Purpose: parses registry mirror strings into host and optional path components.

Important APIs and types: `extractMirrorHostAndPath`.

Control flow: attempts to parse the mirror as a URL; if no host is present, retries by prepending `//` so bare `host/path` strings parse as authority plus path. Returns the original string and empty path if parsing still fails. Path is trimmed of trailing slash.

State and persistence: pure string transformation.

Dependencies and integration: used by `newMirrorRegistryHost` to build mirror `docker.RegistryHost` values.

Risks: malformed but URL-parseable input may produce surprising host/path splits; validation is left to subsequent registry client behavior.

Test signals: covered indirectly by `resolver_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go -->
# sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go

Purpose: preserves kernel-locked unprivileged mount flags on bind mounts in rootless/user-namespace scenarios.

Important APIs and types: `UnprivilegedMountFlags`, `FixUp`, and `FixUpOCI`.

Control flow: `UnprivilegedMountFlags` calls `unix.Statfs` and maps locked filesystem flags to mount option strings such as `ro`, `nodev`, `noexec`, and `nosuid`. `FixUp` and `FixUpOCI` scan mount option lists for `bind`/`rbind`, fetch unprivileged flags for the mount source, append and dedupe them, and write the updated mount back.

State and persistence: no persistent state; reads kernel mount flags for the supplied path.

Dependencies and integration: uses containerd mount types, OCI runtime spec mounts, BuildKit slice dedupe helper, and `x/sys/unix`. Integrated where BuildKit prepares mounts for rootless execution.

Risks: `Statfs` errors fail the entire fixup. Only bind/rbind mounts are modified. Option order after dedupe depends on append/dedupe behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go -->
# sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go

Purpose: non-Linux stub implementation for rootless mount option fixup.

Important APIs and types: `UnprivilegedMountFlags`, `FixUp`, and `FixUpOCI` mirror the Linux API.

Control flow: returns an empty flag list and leaves mount slices unchanged.

State and persistence: none.

Dependencies and integration: keeps cross-platform callers compiling for containerd and OCI mount types.

Risks: rootless mount flag preservation is only meaningful on Linux; non-Linux behavior is explicitly a no-op.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go -->
# sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go

Purpose: mutates an OCI runtime spec to be usable with rootless runc on Linux.

Important APIs and types: `ToRootless`.

Control flow: filters out mounts whose destination starts with `/sys`, then clears Linux resource settings and cgroup path to avoid cgroup operations that rootless runc cannot perform.

State and persistence: in-place mutation of the supplied `*specs.Spec`; no external state.

Dependencies and integration: depends on OCI runtime spec types. Integrated where BuildKit configures rootless executors.

Risks: assumes `spec.Linux` is non-nil; a nil Linux section would panic. Removing all `/sys*` mounts may affect workloads that expect sysfs, but comments document this as an intentional rootless workaround.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go -->
# sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go

Purpose: non-Linux stub for rootless OCI spec conversion.

Important APIs and types: `ToRootless`.

Control flow: always returns an error stating rootless conversion is not implemented on the current GOOS.

State and persistence: none.

Dependencies and integration: uses runtime GOOS and `pkg/errors`; preserves API compatibility for cross-platform builds.

Risks: callers must handle the error on non-Linux platforms.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/keyscan.go -->
# sources/cloud-native/buildkit/util/sshutil/keyscan.go

Purpose: retrieves an SSH server host key in authorized-keys style for a hostname or host:port string.

Important APIs and types: `SSHKeyScan`, `addDefaultPort`, constants `defaultPort`, and sentinel `errCallbackDone`.

Control flow: `SSHKeyScan` creates an SSH client config with a custom host key callback. The callback records `hostname public-key` and returns the sentinel error to stop the handshake after key capture. The function adds port 22 when missing, dials TCP SSH, suppresses the expected sentinel error when a key was captured, closes any connection, and returns key/error.

State and persistence: local variable only; no known-hosts persistence.

Dependencies and integration: uses `golang.org/x/crypto/ssh`, `net`, and string formatting. Useful for Git/SSH source handling or diagnostics.

Risks: the config intentionally has no normal host-key verification because the goal is scanning. Network calls can block according to SSH dial behavior. The returned hostname strips the port.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/keyscan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl.go -->
# sources/cloud-native/buildkit/util/sshutil/scpurl.go

Purpose: detects and parses implicit SCP-style Git SSH URLs such as `git@github.com:moby/buildkit.git`.

Important APIs and types: `IsImplicitSSHTransport`, `SCPStyleURL`, `ParseSCPStyleURL`, and `SCPStyleURL.String`.

Control flow: a regex accepts username, hostname, path, optional query, and optional fragment. Parse builds `url.Userinfo`, host, path, parsed query values, and fragment. String reconstructs the SCP-style URL and appends encoded query and fragment.

State and persistence: pure parsing/formatting.

Dependencies and integration: uses `regexp`, `net/url`, and `pkg/errors`. Integrated by Git source URL handling that distinguishes implicit SSH from explicit transports.

Risks: regex is intentionally narrower than all possible SSH syntaxes; for example explicit `ssh://` URLs are not implicit. Query encoding may reorder query keys through `url.Values.Encode`.

Test signals: `scpurl_test.go` covers accepted/rejected implicit forms and parsing of fragment fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl_test.go -->
# sources/cloud-native/buildkit/util/sshutil/scpurl_test.go

Purpose: validates implicit SCP-style SSH URL detection and parsing.

Important APIs and types: `TestIsImplicitSSHTransport` and `TestParseSCPStyleURL`.

Control flow: detection tests assert false for HTTP, plain host/path, malformed, and explicit SSH URLs, and true for common and unusual username/path SCP forms. Parse tests assert failure for non-SCP inputs and field extraction for simple and fragment-bearing SCP URLs.

State and persistence: pure table tests.

Dependencies and integration: uses `testify/require`.

Risks: tests do not cover query parsing or `SCPStyleURL.String` round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress.go -->
# sources/cloud-native/buildkit/util/stack/compress.go

Purpose: reduces redundant stack traces by removing duplicate or shared suffix frames.

Important APIs and types: `compressStacks`, `subFrames`, and `Frame.Equal`.

Control flow: stack traces are sorted longest-first. Each later stack is compared against already-kept stacks from the bottom frame upward. Full duplicate stacks from the same pid/version/cmdline are skipped. Partial shared suffixes are trimmed before appending.

State and persistence: mutates `Frames` slices of stack objects passed in; no external state.

Dependencies and integration: used by `Traces` in `stack.go` before formatting or serializing stack traces.

Risks: input order is not preserved because stacks are sorted by frame length. Partial trimming mutates the original stack object, which may surprise callers holding references.

Test signals: `compress_test.go` validates full duplicate removal and partial suffix trimming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress_test.go -->
# sources/cloud-native/buildkit/util/stack/compress_test.go

Purpose: tests stack compression behavior using nested errors with multiple stack traces.

Important APIs and types: helper functions `testcall1`, `testcall2`, `testcall3`, `TestCompressStacks`, and `TestCompressMultiStacks`.

Control flow: helpers create errors with stack wrapping at controlled call sites. Tests call `Traces`, assert number and length of resulting stack traces, check expected function names in leading frames, and verify shared suffix trimming.

State and persistence: no external state.

Dependencies and integration: uses `pkg/errors` for stack-bearing errors and `testify/require`.

Risks: assertions depend on function names and relative frame layout; compiler/runtime changes can affect exact stack depth but tests use greater-or-equal where needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.go -->
# sources/cloud-native/buildkit/util/stack/stack.go

Purpose: captures, wraps, extracts, compresses, and formats BuildKit stack traces, including conversion from `pkg/errors` stack frames into protobuf `Stack` objects.

Important APIs and types: `SetVersionInfo`, `Helper`, `Traces`, `Enable`, `Wrap`, `Formatter`, `convertStack`, `withStackError`, and package-level helper registry.

Control flow: `Enable` records its caller as a helper and adds a stack only if the error chain lacks a local `pkg/errors` stack trace. `Traces` recursively unwraps single or multi-error chains, extracts `pkg/errors.StackTrace` and BuildKit `*Stack` traces, then compresses them. `Formatter` prints normal error text, or with `%+v`, includes pid, version, command line, and frames.

State and persistence: package globals track version/revision and helper function names protected by a mutex. Stack objects record command line and pid at conversion time.

Dependencies and integration: registers `Stack` with containerd `typeurl`, uses `pkg/errors`, runtime frame APIs, process args, and generated protobuf types.

Risks: helper filtering relies on function names recorded by `Helper`; misuse can hide frames. `hasLocalStackTrace` checks only single unwrap chains, not multi-error chains. Formatting may expose command-line arguments.

Test signals: compression tests exercise `Traces` and stack frame conversion indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.pb.go -->
# sources/cloud-native/buildkit/util/stack/stack.pb.go

Purpose: generated Go protobuf bindings for `stack.proto`.

Important APIs and types: messages `Stack` and `Frame`, getters, `ProtoReflect`, descriptors, and initialization function `file_github_com_moby_buildkit_util_stack_stack_proto_init`.

Control flow: standard `protoc-gen-go` output builds a file descriptor with two messages. Message getters return zero values on nil receivers. Reset and ProtoReflect wire messages into the protobuf runtime.

State and persistence: protobuf message state, unknown fields, and size cache are embedded per object. Descriptor raw data is compressed once through `sync.Once`.

Dependencies and integration: used by `stack.go`, vtprotobuf generated helpers, typeurl registration, and any protobuf serialization/deserialization of BuildKit stack traces.

Risks: generated file should not be hand-edited; schema changes must flow from `stack.proto` regeneration. Field names for `Frame` are capitalized in proto, which is reflected in generated JSON/protobuf names.

Test signals: no direct generated-code tests; exercised indirectly by stack consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.proto -->
# sources/cloud-native/buildkit/util/stack/stack.proto

Purpose: protobuf schema for serializable BuildKit stack trace data.

Important APIs and types: `Stack` message with repeated `Frame`, repeated command line, pid, version, and revision; `Frame` message with name, file, and line.

Control flow: declarative schema only; generated Go code is in `stack.pb.go` and vtproto helpers in `stack_vtproto.pb.go`.

State and persistence: defines the wire contract for persisted or transported stack traces.

Dependencies and integration: `go_package` targets `github.com/moby/buildkit/util/stack`; `stack.go` registers this type with containerd typeurl.

Risks: field numbers are persistent wire compatibility commitments. Changing or reusing field numbers would break serialized stack data.

Test signals: generated code is not directly tested; stack extraction/formatting tests cover usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack_vtproto.pb.go -->
# sources/cloud-native/buildkit/util/stack/stack_vtproto.pb.go

Purpose: generated vtprotobuf optimized helpers for cloning, equality, sizing, marshaling, and unmarshaling `Stack` and `Frame`.

Important APIs and types: `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for both messages.

Control flow: marshal writes fields into a sized buffer from the end backwards. unmarshal loops over wire fields, decodes known fields, appends unknown fields, and returns protobuf helper errors for invalid length, overflow, wrong wire type, or unexpected EOF. Clone/equality handle nil nested frames and unknown fields.

State and persistence: operates on protobuf object fields and unknown fields. No package-level mutable state beyond generated version constants.

Dependencies and integration: generated by `protoc-gen-go-vtproto` and depends on Planetscale vtprotobuf helpers plus protobuf runtime interfaces.

Risks: generated file should not be edited by hand. Unmarshal appends to existing repeated fields instead of clearing, matching common protobuf behavior but important for reuse of message instances.

Test signals: no direct tests in this subset; protobuf serialization use is indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge.go -->
# sources/cloud-native/buildkit/util/staticfs/merge.go

Purpose: overlays two `fsutil.FS` instances with upper filesystem entries taking precedence over lower entries during walk and open.

Important APIs and types: `MergeFS`, `NewMergeFS`, `record`, `MergeFS.Walk`, and `MergeFS.Open`.

Control flow: `Walk` starts lower and upper walks concurrently, streams sorted records through channels, and merges them by path key. When the same key exists in both, upper is emitted and lower is skipped. `Open` tries upper first, falls back to lower only on not-exist errors.

State and persistence: no persistent state beyond references to lower/upper filesystems. Walk channels buffer records during traversal.

Dependencies and integration: implements `fsutil.FS`, uses `errgroup`, Go `io/fs`, and `staticfs` path-key helpers. Useful for layering generated/static filesystem inputs.

Risks: merge correctness assumes both underlying walks emit paths in sorted order by the same key function. A callback error stops the merge goroutine and propagates through errgroup.

Test signals: `merge_test.go` covers upper precedence, lower fallback, sorted walk, nested merge, and not-exist fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge_test.go -->
# sources/cloud-native/buildkit/util/staticfs/merge_test.go

Purpose: validates overlay semantics of `MergeFS`.

Important APIs and types: `TestMerge`.

Control flow: the test builds lower and upper `FS` instances, verifies `Open` chooses upper content for duplicate path `foo` and lower for `bar`, walks merged output and asserts sizes/modes/order, then layers an additional filesystem and checks fallback/open/not-found behavior.

State and persistence: in-memory filesystems only.

Dependencies and integration: uses `context`, `io`, `os`, `io/fs`, `testify/require`, and `fsutil/types`.

Risks: tests assume deterministic path ordering from static FS and merge logic. They do not simulate walk callback errors or context cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static.go -->
# sources/cloud-native/buildkit/util/staticfs/static.go

Purpose: provides an in-memory implementation of `fsutil.FS`.

Important APIs and types: `File`, `FS`, `NewFS`, `Add`, `Walk`, `Open`, `convertPathToKey`, and `convertKeyToPath`.

Control flow: `Add` normalizes leading slash, updates stat size/mode/path, and stores data by path. `Walk` filters keys by target prefix, sorts them using a slash-to-NUL key transform so parent/child order is stable, and calls the callback with `fsutil.DirEntryInfo`. `Open` returns a new reader over stored bytes or `os.ErrNotExist`.

State and persistence: in-memory map from normalized path to stat/data. `Add` mutates the caller-provided stat pointer.

Dependencies and integration: implements `fsutil.FS` for tests and static content injection.

Risks: `Walk` prefix matching is string-based and does not enforce path component boundaries. No directories are synthesized; only added files are walked. Not concurrency-safe.

Test signals: `static_test.go` covers add/open/read/not-found/walk order and metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static_test.go -->
# sources/cloud-native/buildkit/util/staticfs/static_test.go

Purpose: unit tests for the in-memory static filesystem.

Important APIs and types: `TestStatic`.

Control flow: test adds files with modes/data, opens and reads content, verifies not-found behavior, walks all files checking size/mode/order, then adds a third file and verifies all open/read paths.

State and persistence: in-memory only.

Dependencies and integration: uses `context`, `io`, `os`, `io/fs`, `testify/require`, and `fsutil/types`.

Risks: no tests for target-prefixed walks, leading slash normalization, or directory-like paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/suggest/error.go -->
# sources/cloud-native/buildkit/util/suggest/error.go

Purpose: attaches “did you mean” suggestions to errors based on Levenshtein distance against allowed options.

Important APIs and types: `Search`, `WrapError`, `WrapErrorMaybe`, `suggestError`, and `matchCase`.

Control flow: `Search` optionally lowercases the input/options, rejects exact matches as unrelated errors, selects the closest option under distance threshold 3, and preserves broad input casing. `WrapErrorMaybe` returns `(true, wrappedError)` only when a suggestion exists; otherwise it leaves the original error unchanged.

State and persistence: pure string/error transformation.

Dependencies and integration: uses `github.com/agext/levenshtein`. Useful for config/CLI validation.

Risks: fixed distance threshold can miss longer near-matches or suggest short accidental matches. Case restoration only handles all-lower and all-upper input specially.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/suggest/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go -->
# sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go

Purpose: Windows reexec helper that resolves a username or group to a SID and prints it as JSON.

Important APIs and types: `getUserInfoCmd`, `init`, and `userInfoMain`.

Control flow: `init` registers the `get-user-info` command with `moby/sys/reexec`. `userInfoMain` validates a single argument, calls `windows.LookupSID`, marshals `{SID: ...}` to JSON, writes stdout, and exits with distinct nonzero codes on usage, lookup, or marshal errors.

State and persistence: no persistent state; process exits directly after command handling.

Dependencies and integration: Windows-only file using `x/sys/windows` and BuildKit/Moby reexec. Used when Windows-specific user/group SID lookup is needed from a helper process.

Risks: prints errors to stdout rather than stderr. Hard exits make it unsuitable for direct library use outside reexec.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/getuserinfo/userinfo_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path.go -->
# sources/cloud-native/buildkit/util/system/path.go

Purpose: normalizes Dockerfile/build paths across Linux and Windows semantics, especially WORKDIR/COPY-like paths rooted in container filesystems.

Important APIs and types: `DefaultPathEnv`, `NormalizePath`, `ToSlash`, `FromSlash`, `NormalizeWorkdir`, `IsAbs`, `CheckSystemDriveAndRemoveDriveLetter`, and `cleanPath`.

Control flow: `NormalizePath` converts to slash form, defaults parent to root, removes/validates Windows drive letters, absolutizes relative paths against parent, optionally preserves trailing slash or `/.`, and returns slash form. `NormalizeWorkdir` then converts slash form to platform separators. Windows drive handling rejects non-system drives, bare drive letters, and UNC paths, while stripping `C:` from valid paths.

State and persistence: pure string processing.

Dependencies and integration: used by frontend/build path handling to normalize user-provided container paths. Uses `path` rather than `filepath` to make slash-form handling independent of host OS.

Risks: Windows semantics are intentionally container-root-specific and differ from `filepath.IsAbs`. UNC paths are not supported. `keepSlash` behavior preserves selected trailing syntax and can produce `/.` suffixes.

Test signals: `path_test.go` covers Linux and Windows workdir normalization, drive-letter removal, slash preservation, and Windows absolute detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_test.go -->
# sources/cloud-native/buildkit/util/system/path_test.go

Purpose: validates platform path normalization and Windows drive handling.

Important APIs and types: `TestNormalizeWorkdir`, `TestCheckSystemDriveAndRemoveDriveLetter`, `TestNormalizeWorkdirWindows`, `TestNormalizeWorkdirUnix`, and `TestIsAbs`.

Control flow: table tests cover relative/absolute workdirs, empty current/new workdir, parent-directory cleanup, Windows mixed slashes, C-drive stripping, non-C drive errors, bare drive errors, `C:relative` behavior, UNC rejection, and Windows absolute path detection.

State and persistence: pure string tests.

Dependencies and integration: uses `testify/require`.

Risks: tests are extensive for exposed behavior but do not cover `NormalizePath` keepSlash directly outside drive-removal helper cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_unix.go -->
# sources/cloud-native/buildkit/util/system/path_unix.go

Purpose: non-Windows helpers for host absolute path handling.

Important APIs and types: `IsAbsolutePath` and `GetAbsolutePath`.

Control flow: `IsAbsolutePath` delegates to `filepath.IsAbs`; `GetAbsolutePath` returns the input unchanged.

State and persistence: pure path helpers.

Dependencies and integration: keeps API symmetry with Windows implementation for host path code.

Risks: unlike Windows, `GetAbsolutePath` does not enforce absolutization; callers must know this helper’s platform-specific contract.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_windows.go -->
# sources/cloud-native/buildkit/util/system/path_windows.go

Purpose: Windows host path helpers that account for default system volume prefixing.

Important APIs and types: `DefaultSystemVolumeName`, `IsAbsolutePath`, and `GetAbsolutePath`.

Control flow: `IsAbsolutePath` cleans a path, prepends `C:` when it starts with a separator, then calls `filepath.IsAbs`. `GetAbsolutePath` cleans the path, returns it unchanged if it already starts with `C:` case-insensitively, otherwise prefixes `C:`.

State and persistence: pure path helpers.

Dependencies and integration: used in Windows-specific path handling outside the container-root normalization in `path.go`.

Risks: assumes default system volume is `C:`. Network/UNC and alternate drive semantics are not preserved by `GetAbsolutePath`.

Test signals: Windows-specific direct tests are not included in this subset; `path_test.go` tests cross-platform path logic in `path.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/containerd/containerd.go -->
# sources/cloud-native/buildkit/util/testutil/containerd/containerd.go

Purpose: test helper for retrieving the version of a running containerd daemon.

Important APIs and types: `GetVersion`.

Control flow: creates a containerd client with a 60-second timeout, calls `Version`, fails the test immediately on client or version errors, and returns the version string.

State and persistence: opens a client connection and closes it with defer; no persistence.

Dependencies and integration: uses containerd v2 client and `testing.T`. Intended for integration tests.

Risks: uses `t.Fatal`, so it is not usable outside tests. Uses `context.TODO` with the client timeout option.

Test signals: helper itself has no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/containerd/containerd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go

Purpose: minimal Docker API client for BuildKit integration tests, with local socket/npipe support and raw connection dialing.

Important APIs and types: `Client`, constants `DummyHost` and `DefaultVersion`, `CheckRedirect`, `NewClientWithOpts`, `Close`, `ParseHostURL`, `dialerFromTransport`, and `Dialer`.

Control flow: `NewClientWithOpts` parses the platform default host, creates a default HTTP client/transport, applies functional options, records base transport, and defaults request scheme based on TLS config. `ParseHostURL` validates `proto://addr` style hosts and extracts TCP base paths. `Dialer` returns a raw connection function using configured transport dialer, unix socket, npipe, TLS dialer, or plain net dialer.

State and persistence: holds connection configuration, API version, HTTP client, and base transport. `Close` closes idle connections.

Dependencies and integration: integrates with socket configuration files in the same package, test dockerd daemon helpers, and Docker API request/hijack helpers.

Risks: intentionally minimal compared to full Docker client. `DummyHost` is used to satisfy Go HTTP requirements for local transports. Redirect policy rejects non-GET redirects to avoid method rewrite surprises.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go

Purpose: non-Windows default Docker host constant for the test client.

Important APIs and types: `DefaultDockerHost`.

Control flow: no runtime logic; sets default host to `unix:///var/run/docker.sock`.

State and persistence: constant only.

Dependencies and integration: consumed by `NewClientWithOpts`.

Risks: platform build tag controls inclusion; tests using defaults depend on a local Docker socket existing.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go

Purpose: Windows default Docker host constant for the test client.

Important APIs and types: `DefaultDockerHost`.

Control flow: no runtime logic; sets default host to `npipe:////./pipe/docker_engine`.

State and persistence: constant only.

Dependencies and integration: consumed by `NewClientWithOpts`.

Risks: depends on Windows named pipe availability and permissions.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go

Purpose: formats user-facing Docker daemon connection failure errors for the test client.

Important APIs and types: `ErrorConnectionFailed`.

Control flow: returns a generic daemon-running message when host is empty, otherwise includes the target host.

State and persistence: pure error construction.

Dependencies and integration: used by request connection error handling.

Risks: message is modeled for Docker-style diagnostics; it wraps no underlying cause.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go

Purpose: implements Docker-style HTTP connection hijacking/upgrade for test client raw streams.

Important APIs and types: `DialHijack`, `setupHijackConn`, `CloseWriter`, `hijackedConn`, and `hijackedConnCloseWriter`.

Control flow: builds a POST request with `Connection: Upgrade` and `Upgrade: proto`, dials the daemon, enables TCP keepalive when applicable, writes the request through a lightweight round tripper, requires `101 Switching Protocols`, and returns the raw connection. If HTTP buffered data remains, wraps the connection so reads drain the buffered reader, preserving `CloseWrite` when supported.

State and persistence: transient network connection only.

Dependencies and integration: uses the client `Dialer`, Go HTTP read/write primitives, and is intended for Docker API endpoints that hijack connections.

Risks: caller owns returned connection lifecycle. The `meta` parameter is unused. Non-101 responses close their body and return an error.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go

Purpose: functional option support for configuring the test Docker client.

Important APIs and types: `Opt` and `WithHost`.

Control flow: `WithHost` parses the supplied host, updates client host/proto/addr/basePath, and reconfigures the existing HTTP transport for the selected protocol.

State and persistence: mutates a `Client` during construction.

Dependencies and integration: uses `ParseHostURL` and `configureTransport`.

Risks: fails if the client transport is not `*http.Transport`; options must be applied before tracing/wrapping changes the transport type.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go

Purpose: implements Docker daemon ping for the test client.

Important APIs and types: `PingResponse` and `Client.Ping`.

Control flow: builds a HEAD request to non-versioned `/_ping`, sends it, drains/closes the response body, and converts non-2xx/3xx responses through `checkResponseErr`.

State and persistence: no state beyond network request.

Dependencies and integration: uses `buildRequest`, `doRequest`, and response error helpers in the same package.

Risks: does not perform API version negotiation; intentionally hits base ping endpoint.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go

Purpose: central request construction, execution, response error conversion, and response body cleanup for the test Docker client.

Important APIs and types: `buildRequest`, `doRequest`, `checkResponseErr`, `addHeaders`, and `ensureReaderClosed`.

Control flow: `buildRequest` creates a context request, adds headers, sets scheme/host, uses `DummyHost` for unix/npipe Host headers, and defaults body content type. `doRequest` executes the HTTP request and decorates common connection/TLS/permission/npipe errors while preserving context cancellation/deadline sentinels. `checkResponseErr` accepts 2xx/3xx, reads at most 1 MiB of error body, decodes JSON daemon errors when content type is exactly `application/json`, and wraps the message.

State and persistence: no persistent state; drains up to 512 bytes in `ensureReaderClosed` for connection reuse.

Dependencies and integration: used by `Ping` and other client operations. Integrates with local socket/npipe behavior and Docker-style daemon errors.

Risks: JSON detection is strict on content type and misses charset variants. Large error bodies are replaced by a generic message. Windows privilege probing opens `\\.\PHYSICALDRIVE0`.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go

Purpose: protocol-dispatch transport configuration for the test Docker client.

Important APIs and types: `defaultTimeout` and `configureTransport`.

Control flow: dispatches to unix or npipe platform-specific configuration. For other protocols, sets proxy, enables compression, and installs a net dialer with default timeout.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: used by default client construction and `WithHost`.

Risks: subsequent calls overwrite transport dial settings. Compression is disabled only for local transports.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go

Purpose: non-Windows unix socket transport support for the test Docker client.

Important APIs and types: `configureUnixTransport`, `configureNpipeTransport`, `DialPipe`, and `maxUnixSocketPathSize`.

Control flow: validates unix socket path length, disables compression, and installs a dialer that ignores request network/address and dials the configured unix socket. npipe configuration and pipe dialing return unsupported errors on non-Windows.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: uses `syscall.RawSockaddrUnix` for max path size and Go net dialers.

Risks: path length validation is platform-derived; overly long generated sockets fail early.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go

Purpose: Windows named-pipe transport support for the test Docker client.

Important APIs and types: `configureUnixTransport`, `configureNpipeTransport`, and `DialPipe`.

Control flow: unix transport returns unsupported. npipe transport disables compression and installs a `go-winio` pipe dialer. `DialPipe` delegates to `winio.DialPipe` with timeout.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: uses Microsoft `go-winio` and platform build tags.

Risks: named pipe dialing depends on Windows privileges and daemon availability.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/config.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/config.go

Purpose: JSON config structs for test dockerd daemon configuration.

Important APIs and types: `Config`, `BuilderConfig`, and `BuilderEntitlements`.

Control flow: no functions; struct tags define JSON output for features, registry mirrors, and builder entitlements.

State and persistence: values are marshaled by test setup elsewhere.

Dependencies and integration: used by dockerd integration helpers and BuildKit builder tests.

Risks: `BuilderConfig.Entitlements` has no explicit json tag, so default field name is used unless Go JSON lowercasing is acceptable for the target config.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go

Purpose: starts and stops isolated dockerd instances for BuildKit integration tests.

Important APIs and types: `Daemon`, `Option`, `NewDaemon`, `WithBinary`, `WithExtraEnv`, `Sock`, `StartWithError`, `StopWithError`, and `lockingWriter`.

Control flow: `NewDaemon` creates unique working/root/exec/socket paths and applies options. `StartWithError` resolves the dockerd binary, builds data-root/exec-root/pid/containerd namespace/host args, adds debug defaults and storage driver/userns options, starts the process with test env vars, captures logs into synchronized buffers, and exposes a wait channel. `StopWithError` sends interrupt, waits up to 20 seconds, retries interrupts up to five times, then kills the process if needed.

State and persistence: creates temp directories, daemon root, pid file, exec root, socket path, process handle, log buffers, and wait channel. Removes pid file on clean stop but does not remove daemon root in this file.

Dependencies and integration: uses BuildKit identity for unique IDs, platform socket helpers, test log interfaces, and integration tests that need real Docker daemon behavior.

Risks: process lifecycle is timing-sensitive. `exec.CommandContext(context.TODO())` has no cancellation context. Stop logic can return `errDaemonNotStarted` for already finished processes. Socket path length constraints are handled by shortened exec-root and platform socket helpers.

Test signals: no direct tests in this subset; used by integration suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go

Purpose: non-Windows socket scheme/path helper for test dockerd daemon.

Important APIs and types: `socketScheme` and `getDockerdSockPath`.

Control flow: returns `unix://` scheme and creates a socket path under the supplied root using `<id>.sock`.

State and persistence: pure path construction.

Dependencies and integration: used by `Daemon.Sock` and daemon startup args.

Risks: generated path must fit unix socket length limits; parent code uses short IDs and temp root to help.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go

Purpose: Windows named-pipe scheme/path helper for test dockerd daemon.

Important APIs and types: `socketScheme` and `getDockerdSockPath`.

Control flow: returns `npipe://` scheme and a pipe path `//./pipe/dockerd-<id>`.

State and persistence: pure string construction.

Dependencies and integration: used by `Daemon.Sock` on Windows.

Risks: pipe name uniqueness depends on generated daemon ID.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/echoserver/server.go -->
# sources/cloud-native/buildkit/util/testutil/echoserver/server.go

Purpose: tiny TCP test server that writes a fixed response to every accepted connection.

Important APIs and types: `TestServer`, `NewTestServer`, and `handleConnection`.

Control flow: listens on an ephemeral TCP port, accepts connections in a goroutine until accept fails, and handles each connection by writing the response then closing.

State and persistence: listener remains open until caller closes it through the returned `io.Closer`.

Dependencies and integration: useful for low-level network tests needing deterministic socket response.

Risks: write errors are ignored. The accept loop exits silently on listener close or accept error.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/echoserver/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/azurite.go -->
# sources/cloud-native/buildkit/util/testutil/helpers/azurite.go

Purpose: starts an Azurite blob service for integration tests that need Azure Blob Storage behavior.

Important APIs and types: `AzuriteOpts`, `NewAzuriteServer`, and `waitAzurite`.

Control flow: verifies `azurite-blob` exists, reserves an ephemeral localhost port, starts Azurite with account env vars and temp location, waits up to 15 seconds by issuing blob list requests, registers cleanup in a `MultiCloser`, and returns account-scoped service URL and cleanup function.

State and persistence: creates a temp Azurite data directory and child process; cleanup stops the process through integration helpers.

Dependencies and integration: depends on external `azurite-blob` binary, BuildKit integration sandbox logs/context, HTTP readiness checks, and account credentials.

Risks: port is selected by opening then closing a listener before process start, so another process could theoretically claim it. Missing binary skips via returned error to caller. Readiness accepts any successful HTTP response.

Test signals: helper itself has no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/azurite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/minio.go -->
# sources/cloud-native/buildkit/util/testutil/helpers/minio.go

Purpose: starts a MinIO server and creates a bucket for S3-compatible integration tests.

Important APIs and types: `MinioOpts`, `NewMinioServer`, `waitMinio`, and `randomString`.

Control flow: verifies `minio` and `mc` binaries, chooses an ephemeral address, starts MinIO with root credentials, waits for live health endpoint, configures an `mc` alias, creates a random bucket with requested region, starts `mc admin trace`, and returns server address, bucket, and cleanup function.

State and persistence: creates temp server data, external processes, `mc` alias state, bucket, and trace process. Cleanup removes alias and stops processes via `MultiCloser`.

Dependencies and integration: depends on external MinIO tools and BuildKit integration sandbox command/log helpers.

Risks: same close-open port race as Azurite helper. Random string ignores `rand.Read` errors and maps bytes modulo alphabet length, which is fine for test identifiers but not cryptographic selection. External command availability controls test viability.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/minio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/httpserver/server.go -->
# sources/cloud-native/buildkit/util/testutil/httpserver/server.go

Purpose: configurable HTTP test server with route responses and request statistics.

Important APIs and types: `TestServer`, `NewTestServer`, `SetRoute`, `ServeHTTP`, `Stats`, `Response`, `Stat`, and `Request`.

Control flow: server looks up a route by path, records request stats, sets response headers for last-modified/content-encoding/content-disposition/etag, handles matching `If-None-Match` with 304 and cached count, then writes status 200 and content. `Stats` returns a snapshot copy of the stat struct.

State and persistence: in-memory route map and stats map protected by mutex. Request headers are cloned per recorded request.

Dependencies and integration: uses `httptest.Server`; useful for source fetching/cache tests.

Risks: `Stats` returns a shallow copy; the `Requests` slice backing array is shared. Route map provided to constructor is retained, so external mutation is possible unless callers avoid it. `io.Copy` write errors are ignored.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/httpserver/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/imageinfo.go -->
# sources/cloud-native/buildkit/util/testutil/imageinfo.go

Purpose: reads OCI image/index descriptors from a content provider into convenient test structures including parsed config and layer tar contents.

Important APIs and types: `ImageInfo`, `ImagesInfo`, `Find`, `Filter`, `FindAttestation`, `ReadImages`, and `ReadImage`.

Control flow: `ReadImages` reads the root descriptor as an index; if it is not an index media type, reads a single image and derives platform from image config. For indexes, it reads each manifest descriptor and stores platform from descriptor platform. `ReadImage` reads manifest, validates media type, reads image config, then reads every layer; layer media types are decompressed/parsed via `ReadTarToMap`.

State and persistence: builds in-memory structures and raw layer byte slices from content provider blobs.

Dependencies and integration: uses containerd content/images helpers, OCI specs, platform formatting, and test tar helpers. Used by image-output integration tests.

Risks: assumes index manifests have non-nil `Platform`; nil would panic. Attestation lookup assumes `Desc.Annotations` is non-nil before indexing. Reads all layer blobs into memory.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/imageinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/frombinary.go -->
# sources/cloud-native/buildkit/util/testutil/integration/frombinary.go

Purpose: imports an OCI/Docker image archive from a binary file into a temporary local content store for integration tests.

Important APIs and types: `providerFromBinary`.

Control flow: creates a temp content-store directory, opens the archive file, imports the index with `archive.ImportIndex`, reads and unmarshals the resulting index descriptor, and returns the first manifest descriptor, the content provider/store, and a cleanup function. On any error, the temp directory is removed.

State and persistence: creates a temporary BuildKit state directory and local containerd content store; caller-owned cleanup removes it after success.

Dependencies and integration: uses containerd local content store and image archive importer, OCI specs, JSON, and filesystem temp APIs.

Risks: assumes imported index contains at least one manifest. Cleanup is returned as a bare function and must be called by tests to avoid temp directory leaks.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/frombinary.go -->
