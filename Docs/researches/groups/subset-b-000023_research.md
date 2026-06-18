# subset-b-000023 Research

Grouped research report for BuildKit solver and llbsolver files. Each section is delimited for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go -->
## sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go

Purpose: generated vtprotobuf support for the `solver/errdefs` protobuf messages used as typed gRPC error payloads. It gives BuildKit's error details fast deep clone, equality, marshal, size, and unmarshal paths without reflection-heavy generic protobuf handling.

Important APIs and types: methods are generated on `Vertex`, `Source`, `Frontend`, `FrontendCap`, `CompatibilityFeature`, `Subrequest`, `Solve`, `FileAction`, `ContentCache`, `ProvenanceMaterialsIncomplete`, and `ProvenanceMaterialIncomplete`. The key method families are `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT`. Oneof wrappers `Solve_File` and `Solve_Cache` also receive clone/equality/marshal/size handling.

Control flow: marshal methods compute exact size, fill buffers backward with field tags and varints, and preserve `unknownFields`. Unmarshal methods scan wire fields, validate wire types and tags, append repeated fields, instantiate nested protobuf values, and preserve unknown wire segments via `protohelpers.Skip`.

State and dependencies: the file has no durable state; it mutates receiver fields during unmarshal and allocates cloned slices/maps for deep-copy safety. It depends on `solver/pb` vtproto helpers for nested `pb.Op`, `pb.SourceInfo`, and `pb.Range`, plus `google.golang.org/protobuf` and Planetscale `protohelpers`.

Integration points: wrapper files such as `frontend.go`, `source.go`, `solve.go`, and `provenance.go` rely on `CloneVT` when extracting error chains and on vt marshaling when typed details cross gRPC.

Risks and test signals: because this is generated code, manual edits are high risk and should be regenerated from `errdefs.proto`. Main risks are schema drift, oneof handling regressions, and unknown-field loss. Direct tests are elsewhere, especially provenance round-trip tests through `grpcerrors`, which exercise generated serialization indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontend.go -->
## sources/cloud-native/buildkit/solver/errdefs/frontend.go

Purpose: defines typed frontend failure details that can wrap ordinary errors and survive gRPC conversion.

Important APIs and types: `FrontendError` embeds `*Frontend` plus an underlying `error`, implements `Error`, `Unwrap`, and `ToProto`, and is created through `(*Frontend).WrapError`. `Frontends(err)` walks nested `FrontendError` wrappers and returns cloned `Frontend` details in unwrap order. `init` registers the `Frontend` type with `typeurl`.

Control flow: `Error` deliberately avoids expanding message detail when an inner error exists, preventing deeply nested frontend wrappers from producing unwieldy strings. `Frontends` uses `errors.As`, recurses into `Unwrap`, then appends `CloneVT` of the current detail.

State and dependencies: no persistence; each wrapper stores the protobuf detail and underlying error. It depends on `containerd/typeurl` and BuildKit `grpcerrors` for typed error transport.

Integration points: used by frontends/gateway paths that need to label errors with frontend name/source and by gRPC conversion code that recognizes `TypedErrorProto`.

Risks and test signals: risks are mostly error-chain ordering and message bloat if `Error` changes. There is no direct test in this subset; generated vtproto and grpcerrors round-trip coverage for related errdefs provide indirect confidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontendcap.go -->
## sources/cloud-native/buildkit/solver/errdefs/frontendcap.go

Purpose: represents an unsupported frontend capability as a typed error payload.

Important APIs and types: `UnsupportedFrontendCapError` wraps `*FrontendCap` and an optional cause. It implements `Error`, `Unwrap`, and `ToProto`; `NewUnsupportedFrontendCapError(name)` creates a cause-free error; `(*FrontendCap).WrapError` attaches a cause. `init` registers the proto detail type.

Control flow: `Error` starts with `unsupported frontend capability <name>` and appends the wrapped error text when present. gRPC detail export is through `ToProto`.

State and dependencies: no persistent state. The wrapper owns only the `FrontendCap` detail and error chain. Dependencies are `typeurl` registration and BuildKit `grpcerrors`.

Integration points: consumed by frontend capability validation and clients that need to distinguish unsupported capability failures from generic solve failures.

Risks and test signals: risks are string compatibility for clients that inspect messages and preservation of typed detail across gRPC. No direct test appears in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontendcap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/jobs.go -->
## sources/cloud-native/buildkit/solver/errdefs/jobs.go

Purpose: provides a solver-level typed error for missing jobs.

Important APIs and types: `UnknownJobError` stores a job id, implements `Code() codes.Code` returning `codes.NotFound`, and formats `no such job <id>`. `NewUnknownJobError(id)` is the public constructor.

Control flow: there is no complex flow; the solver job registry constructs this error from `Solver.Get` after waiting for a job id and timing out.

State and dependencies: only the missing id is stored. The dependency on `google.golang.org/grpc/codes` lets BuildKit's error conversion map the error to `NotFound`.

Integration points: `solver/jobs.go` uses this in `Solver.Get` when a requested job never appears within the bounded wait.

Risks and test signals: behavior is simple, but the gRPC code is semantically important for clients. No direct unit test in this subset; job lifecycle integration tests exercise jobs broadly, not this exact timeout path.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/jobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/op.go -->
## sources/cloud-native/buildkit/solver/errdefs/op.go

Purpose: attaches the protobuf operation and human-readable operation description to errors so later solve-level wrappers can include op context.

Important APIs and types: `OpError` stores an underlying `error`, `*pb.Op`, and description map. `WithOp(err, anyOp, opDesc)` wraps only when `err` is non-nil and `anyOp` is actually `*pb.Op`.

Control flow: callers defer wrapping around cache map, exec, or slow-cache paths. `WithSolveError` later uses `errors.As` to recover `OpError` details and put them into the `Solve` typed detail.

State and dependencies: no persistence; the wrapper retains the original op pointer and map. It depends on `solver/pb`.

Integration points: `solver/jobs.go` calls `errdefs.WithOp` in shared op error paths, and `solve.go` consumes the result.

Risks and test signals: because the op pointer is retained, mutation after wrapping could affect details. Passing a non-`*pb.Op` silently returns the original error, which is intentional but can hide context if callers use the wrong value.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/op.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance.go -->
## sources/cloud-native/buildkit/solver/errdefs/provenance.go

Purpose: carries structured details when provenance material capture is incomplete.

Important APIs and types: `ProvenanceMaterialsIncompleteError` embeds `*ProvenanceMaterialsIncomplete` and an underlying error, implements `Unwrap` and `ToProto`, and is produced by `(*ProvenanceMaterialsIncomplete).WrapError`, `WithProvenanceMaterialsIncomplete`, and `NewProvenanceMaterialsIncomplete`.

Control flow: constructors preserve nil-error behavior, build a `ProvenanceMaterialsIncomplete` detail containing individual `ProvenanceMaterialIncomplete` entries, and rely on grpcerrors/typeurl to serialize the detail.

State and dependencies: no persistent state. It depends on `typeurl`, BuildKit `grpcerrors`, generated vtproto methods, and `pkg/errors` for the default message.

Integration points: provenance capture code can report which source materials could not be verified, including operation, request name, method, URI/final URI, and reason.

Risks and test signals: the primary risk is losing detailed incomplete-material entries during error transport. `provenance_test.go` directly round-trips this error through gRPC and asserts the URI/reason and message survive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance_test.go -->
## sources/cloud-native/buildkit/solver/errdefs/provenance_test.go

Purpose: verifies that provenance-incomplete typed errors survive BuildKit's gRPC error conversion path.

Important APIs and types: `TestProvenanceMaterialsIncompleteRoundTrip` constructs `NewProvenanceMaterialsIncomplete`, converts with `grpcerrors.ToGRPC` and `grpcerrors.FromGRPC`, then uses `require.ErrorAs` for `*ProvenanceMaterialsIncompleteError`.

Control flow: the test creates one incomplete material with operation digest, command-like name, method, URI, and reason. After round-trip, it validates the entry count, selected fields, and human message.

State and dependencies: test-only, no persistence. It depends on `testing`, BuildKit `grpcerrors`, and testify `require`.

Integration points: protects the contract used by provenance reporting, clients, and any middle layer that forwards BuildKit errors through gRPC status details.

Risks and test signals: strong signal for typeurl registration and vtproto serialization of this specific detail. It does not cover multiple entries, `FinalUri`, or nested wrapping depth.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/solve.go -->
## sources/cloud-native/buildkit/solver/errdefs/solve.go

Purpose: wraps solve-time errors with structured information about the failing op, subject, input ids, mount ids, and operation description.

Important APIs and types: `SolveError` embeds `*Solve` and `Err`, implements `Error`, `Unwrap`, and `ToProto`. `WithSolveError(err, subject, inputIDs, mountIDs)` builds the detail and pulls `Op`/`Description` from any nested `OpError`. `(*Solve).WrapError` recreates a wrapper from decoded proto details. `MarshalJSON` and `UnmarshalJSON` use `protojson`.

Control flow: caller-provided subject is an alias to generated oneof interface `IsSolve_Subject`, commonly `Solve_File` or `Solve_Cache`. Nil input error returns nil to preserve Go wrapping conventions.

State and dependencies: no persistence; the wrapper keeps protobuf fields and an error chain. Dependencies include `typeurl`, `solver/pb`, `grpcerrors`, and protobuf JSON.

Integration points: `SlowCacheError` and file action errors expose `ToSubject` so upper layers can attach precise solve subjects. gRPC transport uses `ToProto`.

Risks and test signals: risks include missing op context if `WithOp` was not applied, and JSON compatibility for oneof details. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/solve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/source.go -->
## sources/cloud-native/buildkit/solver/errdefs/source.go

Purpose: attaches source-location details to errors and can print highlighted source excerpts.

Important APIs and types: `WithSource`, `SourceError`, `Sources(err)`, `(*Source).WrapError`, and `(*Source).Print`. Helpers `containsLine` and `getStartEndLine` inspect protobuf ranges.

Control flow: `Sources` recursively unwraps `SourceError` chains and appends cloned details. `Print` splits embedded source data into lines, finds the min/max range, pads surrounding context, and writes a filename header plus marked `>>>` lines.

State and dependencies: no persistence; `Print` only writes to an `io.Writer`. Dependencies include `solver/pb` source/range messages, `grpcerrors`, and `pkg/errors`.

Integration points: used by frontend/source parsing paths to surface precise Dockerfile or LLB source locations in error details and client diagnostics.

Risks and test signals: `Print` ignores nil/malformed ranges and out-of-bounds starts, which is safe but may hide context. Multi-range printing highlights all contained lines but computes a single padded span. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/subrequest.go -->
## sources/cloud-native/buildkit/solver/errdefs/subrequest.go

Purpose: represents unsupported frontend/gateway subrequests as typed errors.

Important APIs and types: `UnsupportedSubrequestError` embeds `*Subrequest` and an optional cause. It implements `Error`, `Unwrap`, and `ToProto`; `NewUnsupportedSubrequestError(name)` and `(*Subrequest).WrapError` are constructors. `init` registers the detail type with `typeurl`.

Control flow: message construction mirrors frontend capability errors, with a base `unsupported request <name>` string plus optional cause text.

State and dependencies: no persistent state. It depends on BuildKit `grpcerrors` and containerd `typeurl`.

Integration points: gateway frontend request handling can return this when a client requests an unsupported subrequest, while preserving machine-readable request name.

Risks and test signals: low algorithmic risk; main contract is gRPC detail preservation. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/subrequest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/vertex.go -->
## sources/cloud-native/buildkit/solver/errdefs/vertex.go

Purpose: associates errors with the LLB vertex digest that produced them and registers vertex/source error details.

Important APIs and types: `VertexError` wraps `*Vertex` and an underlying error, implements `Unwrap` and `ToProto`. `WrapVertex(err, dgst)` builds a `Vertex{Digest: dgst.String()}` detail; `(*Vertex).WrapError` rebuilds from decoded details. `init` registers both `Vertex` and `Source`.

Control flow: nil errors pass through. Shared op code defers `WrapVertex` so cache/exec failures consistently include the original LLB digest.

State and dependencies: no persistence. Dependencies include `typeurl`, BuildKit `grpcerrors`, and OCI `digest`.

Integration points: solver execution, cache, and slow-cache paths use this to link failures back to graph vertices and progress UI entries.

Risks and test signals: the file stores digest as string, so invalid or empty digests are not validated here. Direct tests are absent; scheduler/solve tests indirectly depend on error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/vertex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter.go -->
## sources/cloud-native/buildkit/solver/exporter.go

Purpose: exports solver cache records and dependency links to a `CacheExporterTarget`, including remote result metadata, backlinks, secondary exporters, and merged exporters.

Important APIs and types: `exporter.ExportTo`, `addBacklinks`, `getBestResult`, `compareCacheRecord`, and `mergedExporter.ExportTo`. The `exporter` carries a cache key, preferred records, optional single record, context option injector, secondary edge context, and override flag.

Control flow: `ExportTo` initializes per-call context maps for backlink memoization and recursion cycle prevention. It clones and sorts records by newest `CreatedAt` then lower `Priority`, loads result remotes, optionally resolves local refs into remotes, recursively exports dependency cache keys, adds secondary exporters from merged edges, exports backlinks unless disabled, validates all dependency slots have records, and finally calls `t.Add` for the root cache key. `addBacklinks` recursively walks backend backlink metadata and suppresses incomplete link sets.

State and dependencies: no durable state here; it reads cache manager backend/results and writes to exporter target. Context stores memo maps for one export traversal. Dependencies include cache manager internals, OCI digests, and containerd errdefs.

Integration points: remote cache export, inline cache export, scheduler cache exporting, and llbsolver exporter code all route through this machinery via `ExportableCacheKey.Exporter`.

Risks and test signals: recursive graph export must avoid cycles and incomplete dependency records. Error handling intentionally continues on dependency export failures in some loops, which may omit cache links. `exporter_test.go` covers record ordering only; broader scheduler cache export tests outside this subset cover integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter_test.go -->
## sources/cloud-native/buildkit/solver/exporter_test.go

Purpose: validates deterministic cache record ranking used by cache export selection.

Important APIs and types: `TestCompareCacheRecord` constructs records with equal, newer, older timestamps and different priorities, includes nil entries, then sorts with `compareCacheRecord`.

Control flow: the expected order is newest first, then lower priority for equal timestamps, then older records, with nil records last.

State and dependencies: test-only; depends on `slices`, `testing`, and `time`.

Integration points: protects `getBestResult` and the first record selected by `exporter.ExportTo` when multiple cache records are available.

Risks and test signals: useful but narrow. It does not exercise backlink recursion, remote resolution, compression variants, dependency validation, or target `Add` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index.go -->
## sources/cloud-native/buildkit/solver/index.go

Purpose: maintains an in-memory synchronous index of active solver edges so equivalent cache keys share work and merged edges can be discovered.

Important APIs and types: `edgeIndex`, `indexItem`, `newEdgeIndex`, `LoadOrStore`, `Release`, `releaseEdge`, `releaseLink`, `enforceLinked`, `enforceIndexID`, `getAllMatches`, and `isIgnoreCache`.

Control flow: `LoadOrStore` computes all matching IDs for a `CacheKey`; if an existing edge should win, it links the new key and returns the old edge. Otherwise it assigns an identity or matching ID, links dependencies, records the edge, and back-references it for release. Dependency matching intersects candidate IDs across input indexes and selectors. Release clears edge owners and recursively removes link-only items no longer referenced.

State and dependencies: state is fully in-memory under `mu`: ID-to-item map and edge-to-ID backrefs. `CacheKey.indexIDs` is mutated to cache index identities. Dependencies are BuildKit cache key/link types and `identity.NewID`.

Integration points: scheduler and solver state create edges through this index to deduplicate concurrent or repeated graph work.

Risks and test signals: correctness depends on recursive link cleanup and `IgnoreCache` asymmetry. `index_test.go` covers simple, multi-level, three-level, selector, dependency mutation, and release cleanup scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index_test.go -->
## sources/cloud-native/buildkit/solver/index_test.go

Purpose: exercises edge index matching and cleanup across root and dependency-linked cache keys.

Important APIs and types: helper `checkEmpty` asserts both internal maps are empty. Tests create `edge` placeholders and cache keys using `NewCacheKey`, `testCacheKeyWithDeps`, and selectors.

Control flow: `TestIndexSimple` checks root-key collision and release cleanup. `TestIndexMultiLevelSimple` verifies dependency equivalence, selector changes, alternate dependency sets, merged key behavior, and that a later edge remains after the original is released. `TestIndexThreeLevels` verifies nested dependencies and low-level dependency mutation still match through linked IDs.

State and dependencies: test-only state is an in-memory `edgeIndex`. It depends on test helpers defined elsewhere in the solver package.

Integration points: gives confidence that scheduler deduplication can merge equivalent active graph edges without leaking index entries after job release.

Risks and test signals: solid coverage for index graph behavior, but no race test here; synchronization is covered by mutex use and broader scheduler tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe.go -->
## sources/cloud-native/buildkit/solver/internal/pipe/pipe.go

Purpose: implements a small generic request/status pipe between scheduler senders and receivers, including cancellation propagation to function-backed work.

Important APIs and types: `Pipe`, `Request`, `Sender`, `Receiver`, `Status`, `New`, and `NewWithFunction`. Internal `channel` uses `atomic.Pointer` to publish the latest value and detect whether a receiver has already consumed it.

Control flow: `New` wires a sender status channel and receiver cancel channel, with optional completion callbacks. `Sender.Update` publishes intermediate status; `Finalize` marks completion, stores error/value, and sets `Canceled` when the sender observed a canceled request and the error is `context.Canceled`. `Receiver.Cancel` sends a canceled request back to the sender. `NewWithFunction` wraps a function with a cancelable context and finalizes the pipe when the function returns.

State and dependencies: state is in-memory; sender protects request mutation with a mutex, receiver stores last status locally, and atomic channels hold most recent messages. Dependencies are `context`, `sync`, `sync/atomic`, and `pkg/errors`.

Integration points: scheduler request dispatch uses pipes to communicate edge requests, function requests, status updates, and cancellation.

Risks and test signals: the channel is latest-value rather than queueing, so intermediate updates may be coalesced. `pipe_test.go` covers normal completion and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go -->
## sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go

Purpose: validates function-backed pipe completion and cancellation.

Important APIs and types: `TestPipe` and `TestPipeCancel` exercise `NewWithFunction`, receiver polling, callbacks, status fields, and cancellation.

Control flow: both tests use a blocking function that either returns `res0` after a channel is closed or returns `context.Cause(ctx)` after cancellation. They assert no status is available before completion, then verify `Completed`, `Canceled`, `Err`, and `Value`.

State and dependencies: test-only channels coordinate execution. Dependencies are `context`, `testing`, and testify `require`.

Integration points: protects scheduler pipe assumptions that no status appears before send completion, completion callbacks fire, and cancellation is represented both as an error and as `Status.Canceled`.

Risks and test signals: tests cover two core paths but not multiple updates, duplicate cancel, or concurrent receiver polling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs.go -->
## sources/cloud-native/buildkit/solver/jobs.go

Purpose: defines BuildKit's solver job orchestration layer: active vertex graph sharing, job lifecycle, progress/tracing fanout, cache manager composition, operation deduplication, sub-build support, and provenance walking.

Important APIs and types: public surface includes `ResolveOpFunc`, `Builder`, `Solver`, `SolverOpt`, `NewSolver`, `Solver.NewJob`, `Solver.Get`, `Solver.Close`, `Job.Build`, `Job.Discard`, `Job.InContext`, `Job.Session`, `Job.Cleanup`, `Job.SetValue`, `Job.EachValue`, and `Job.CompatibilityVersion`. Internal types include `state`, `sessionGroup`, `subBuilder`, `sharedOp`, `activeOp`, `cacheWithCacheOpts`, `withProvenance`, `vertexWithMetadata`, `vertexWithCacheOptions`, and `SlowCacheError`.

Control flow: `Solver.load` recursively canonicalizes vertices and inputs, handles `IgnoreCache` by using a derived digest when necessary, creates or reuses active `state`, merges cache sources and metadata, records parent/child graph links, and connects progress writers. `Job.Build` loads the graph and delegates scheduling. `sharedOp` lazily resolves the concrete `Op`, deduplicates cache map, slow-cache, and exec work with `flightcontrol`, wraps errors with op and vertex details, and records progress/tracing. `Job.Discard` removes job references, releases unreferenced active states recursively, delays job map deletion for late status readers, and runs cleanup hooks.

State and persistence: state is in-memory only. Solver maps jobs by id and active states by digest; `state` tracks jobs, parents, children, releasers, cache managers, progress writer set, spans, op, and edges. `Job` tracks progress reader/writer, values, session id, unique provenance id, resolver cache, and releasers. No durable storage is written here.

Dependencies and integration: integrates with scheduler, edge index, cache managers, session groups, progress controller, tracing, compatibility values, resolver cache, errdefs, and provenance providers. `llbsolver/bridge.go` uses the `Builder` and `JobContext` contracts.

Risks and test signals: concurrency and lifecycle are the main risks: lock ordering, edge merge propagation, ignored-cache digest shifts, delayed deletion, cleanup release, and incomplete cancellation caching. `jobs_test.go` covers worker parallelism at integration level; scheduler tests outside this subset cover many shared-op behaviors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs_test.go -->
## sources/cloud-native/buildkit/solver/jobs_test.go

Purpose: integration-test job scheduling parallelism against real workers.

Important APIs and types: `TestJobsIntegration`, `testParallelism`, and config updaters `parallelismSetterSingle` / `parallelismSetterUnlimited`. It initializes OCI and containerd workers and runs an integration matrix.

Control flow: two independent busybox LLB runs share a persistent cache mount and each waits for the other to write a signal file. With max parallelism set to one, elapsed time should exceed ten seconds; with unlimited parallelism it should be below ten seconds.

State and dependencies: uses BuildKit integration sandbox, client solve API, LLB marshal, temporary local mounts, and errgroup. The cache mount is persistent within the worker to coordinate the two commands.

Integration points: validates that solver/job scheduling respects worker `max-parallelism` configuration while allowing true concurrency when unrestricted.

Risks and test signals: this is a high-value integration signal but platform-sensitive; it skips Windows and depends on worker images/mirrors. It does not directly test job deletion, provenance, or error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/bridge.go -->
## sources/cloud-native/buildkit/solver/llbsolver/bridge.go

Purpose: implements the LLB frontend bridge over solver jobs, workers, source policy, cache importers, entitlements, executor access, source metadata resolution, and lazy cache importer resolution.

Important APIs and types: `llbBridge` fields hold builder, frontends, worker resolvers, cache importer functions, cache manager memo, session manager, provenance store, proxy-network mode, and lazily loaded executor. Methods include `Warn`, `loadResult`, `policy`, `validateEntitlements`, `Run`, `Exec`, `loadExecutor`, `ResolveSourceMetadata`, `resolveSourceMetadata`, `cmKey`, and `newLazyCacheManager`. `lazyCacheManager` implements the solver cache manager interface by waiting for async importer construction.

Control flow: `loadResult` resolves a worker, loads entitlements/source policy, validates request policies, builds a source policy engine, memoizes cache importers by stable key, loads LLB with policy/entitlement/cap/resource options, prunes detected pruned cache ids, then calls `builder.Build`. Execution methods validate entitlements, attach proxy policy, lazily load worker executor once, and delegate. Source metadata resolution applies policy before calling worker metadata resolution inside progress context.

State and persistence: cache importer managers are memoized in `cms` under `cmsMu`; executor is cached with `sync.Once`. Lazy cache managers start goroutines and close `waitCh` when ready. No durable state.

Dependencies and integration: central bridge between frontend gateway, solver, worker controller, remotecache, sourcepolicy, entitlements, sessions, executor, and provenance/proxy helpers.

Risks and test signals: risks include lazy importer goroutine errors surfacing late, cache importer key collisions, policy bypass when `withPolicy` is false, and proxy network netmode rewriting. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/bridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml

Purpose: CDI test fixture defining one concrete `vendor1.com/device=foo` device.

Important fields: `cdiVersion: "0.6.0"`, `kind: "vendor1.com/device"`, one `devices` entry named `foo`, and a container edit that injects `FOO=injected`.

Control flow and state: static YAML loaded by `cdi.NewCache(cdi.WithSpecDirs("./fixtures"))` in tests. It does not execute code or persist runtime state.

Dependencies and integration: consumed by the CDI library and `cdidevices.Manager` tests to validate exact device-name matching and annotation-derived auto-allow behavior.

Risks and test signals: fixture correctness depends on CDI schema compatibility. Its spec-level `org.mobyproject.buildkit.device.autoallow: true` annotation exercises manager annotation merging and auto-allow detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-device.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml

Purpose: CDI fixture for device class annotation lookup.

Important fields: declares `kind: "vendor1.com/deviceclass"`, a spec annotation `foo.bar.baz: FOO`, auto-allow annotation, and four devices. `foo` and `bar` carry `org.mobyproject.buildkit.device.class: class1`, `baz` carries `class2`, and `qux` has no BuildKit class annotation.

Control flow and state: static test data read into the CDI cache. It contributes both spec-level and device-level annotations that `deviceAnnotations` merges.

Dependencies and integration: `manager_test.go` expects class lookup for `class1` to find `vendor1.com/deviceclass=foo` and `vendor1.com/deviceclass=bar` from this file.

Risks and test signals: changing names or annotations will alter class-based device resolution tests. It also helps cover that unrelated spec annotations do not interfere with BuildKit-specific annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-deviceclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml

Purpose: CDI fixture for first-device, wildcard, class, and auto-allow behavior on a multi-device kind.

Important fields: `kind: "vendor1.com/devicemulti"` with devices `foo`, `bar`, `baz`, and `qux`; each injects a distinct env var. Device `baz` is annotated with BuildKit class `class1`; the spec has auto-allow enabled.

Control flow and state: static YAML used by CDI cache tests. Device order matters for the manager's "first device of kind" resolution path.

Dependencies and integration: `manager_test.go` expects `vendor1.com/devicemulti` with no name to resolve to the first matching device, wildcard to return all four devices, and class lookup to include `baz`.

Risks and test signals: reordering devices changes first-device expectations. The fixture covers dedup and class fallback combined with qualified CDI names.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/fixtures/vendor1-devicemulti.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go

Purpose: manages Container Device Interface devices for BuildKit, including listing, auto-allow evaluation, name/class resolution, OCI spec injection, cache refresh, and on-demand device installers.

Important APIs and types: `Setup`, global `Register`, `Device`, `Manager`, `NewManager`, `ListDevices`, `GetDevice`, `Refresh`, `InjectDevices`, `FindDevices`, `OnDemandInstaller`, plus helpers `parseDevice`, `isAutoAllowed`, `hasDevice`, `deviceAnnotations`, and `dedupSlice`.

Control flow: `FindDevices` lists current CDI devices, parses each requested `pb.CDIDevice`, resolves qualified names by exact/first/wildcard kind, falls back to BuildKit class annotations when the qualifier is invalid or no device matched, and errors for missing non-optional devices. `InjectDevices` resolves then delegates to CDI cache injection. `ListDevices` annotates registered devices and adds validated on-demand installer kinds not already present. `OnDemandInstaller` serializes setup by kind with a locker, validates preconditions, runs installer, refreshes cache, and auto-allows the kind.

State and persistence: manager keeps a CDI cache pointer, per-kind locker, and in-memory `autoAllowed` set. On-demand auto-allow is not persisted and has a TODO to encode it as annotation.

Dependencies and integration: integrates with `tags.cncf.io/container-device-interface`, BuildKit protobuf CDI requests, OCI runtime specs, and worker entitlement checks.

Risks and test signals: risks include global installer mutation, non-persistent auto-allow, class annotation collisions, and optional device warning-only behavior. `manager_test.go` covers exact, first, wildcard, class, and missing required devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go

Purpose: validates CDI device resolution semantics against fixture specs.

Important APIs and types: `TestFindDevices` table-drives requests through `NewManager(cache, nil).FindDevices`.

Control flow: cases cover exact qualified device, first device of a kind when no name is supplied, wildcard all devices of a kind, class lookup across different CDI kinds, and erroring for a missing required device.

State and dependencies: each case creates a fresh CDI cache from `./fixtures`; no shared persistent state. Dependencies are BuildKit `pb.CDIDevice`, testify, and the CDI cache package.

Integration points: protects `Manager.parseDevice` behavior used by LLB execution device requests and entitlement validation.

Risks and test signals: tests use `ElementsMatch` for unordered multi-device results except the first-device case expects one exact device. They do not test optional missing devices, on-demand installers, auto-allow output, or OCI spec injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go -->
## sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go

Purpose: defines supported BuildKit LLB compatibility versions and validation logic.

Important APIs and types: constants `CompatibilityVersion013`, `CompatibilityVersion015`, `CompatibilityVersion031`, `CompatibilityVersionCurrent`, `JobValueKey`, `SupportedCompatibilityVersions`, and `ValidateCompatibilityVersion`.

Control flow: supported versions are stored in a slice and returned as a clone to prevent caller mutation. Validation accepts known versions, reports a special "upgrade buildkit" error for versions newer than current, and reports supported values for older unsupported versions.

State and dependencies: static in-memory constants only. Dependency on `slices` and `pkg/errors`.

Integration points: solver jobs store compatibility with `Job.SetValue` under `JobValueKey`; exporter code reads `Job.CompatibilityVersion` and passes it to exporters.

Risks and test signals: forgetting to update `CompatibilityVersionCurrent` or tests when adding a version would reject newer clients. `compat_test.go` covers current list, valid versions, unsupported old-ish version, and future-version message.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go

Purpose: verifies the compatibility version constants and validation messages.

Important APIs and types: `TestSupportedCompatibilityVersions` and `TestValidateCompatibilityVersion` exercise `SupportedCompatibilityVersions`, `CompatibilityVersionCurrent`, and `ValidateCompatibilityVersion`.

Control flow: tests assert the exact supported slice `[10, 20, 30]`, current `30`, no error for version 13/current constants, an unsupported message for `11`, and an upgrade hint for `40`.

State and dependencies: test-only; depends on testify `require`.

Integration points: protects client/server compatibility negotiation and exporter metadata that depends on job compatibility.

Risks and test signals: exact slice assertion intentionally forces test updates when compatibility versions change.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/entitlements.go -->
## sources/cloud-native/buildkit/solver/llbsolver/entitlements.go

Purpose: loads and filters LLB entitlements stored on solver jobs/builders.

Important APIs and types: `keyEntitlements`, `supportedEntitlements(ents []string)`, and `loadEntitlements(b solver.Builder)`.

Control flow: `supportedEntitlements` maps string names to known BuildKit entitlement constants for network host, security insecure, and devices. `loadEntitlements` iterates all builder values under `keyEntitlements`, requires each to be an `entitlements.Set`, and merges configs into one set, merging when a previous non-nil config exists.

State and dependencies: no persistence; values are stored in solver job value maps elsewhere. Dependencies are `solver.Builder`, BuildKit `entitlements`, and `pkg/errors`.

Integration points: `llbBridge.loadResult`, `validateEntitlements`, and LLB loading use these values to permit or reject network/security/device behavior.

Risks and test signals: type assertions mean incorrect job value wiring fails the build. Merge behavior distinguishes nil config from non-nil config. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/entitlements.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go -->
## sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go

Purpose: wraps execution errors with references to input and mount results, ensuring borrowed refs can be released if the error is dropped.

Important APIs and types: `ExecError`, `WithExecError`, `WithExecErrorWithContext`, `EachRef`, and `Release`.

Control flow: constructor returns nil for nil errors, stores inputs/mounts, and installs a finalizer that warns and releases unreleased refs if ownership was not borrowed. `EachRef` deduplicates result pointers across inputs and mounts before invoking a callback. `Release` releases all refs once and marks `OwnerBorrowed`.

State and dependencies: holds in-memory result references and an ownership flag. It depends on solver `Result`, `context`, `runtime.SetFinalizer`, and BuildKit logging.

Integration points: exec op code can wrap errors so higher layers can include input/mount context and safely transfer result ownership.

Risks and test signals: finalizers are nondeterministic and should be a leak backstop, not normal control flow. Callers must call `Release` or intentionally borrow ownership. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go -->
## sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go

Purpose: annotates file-operation errors with the index of the failing file action.

Important APIs and types: `FileActionError`, `WithFileActionError`, and `ToSubject`.

Control flow: `WithFileActionError` returns nil for nil errors and otherwise wraps the cause with an action index. `ToSubject` converts the index into solver errdefs `Solve_File` subject detail so solve errors can identify the failing action.

State and dependencies: no persistence; only stores index and error. Depends on top-level solver errdefs package.

Integration points: file op solver/backend paths can wrap action failures and then `WithSolveError` can serialize the subject into typed gRPC details.

Risks and test signals: correctness depends on callers using the same action index as the LLB `FileAction` list. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/errdefs/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/export.go -->
## sources/cloud-native/buildkit/solver/llbsolver/export.go

Purpose: coordinates result exporters, session-provided exporters, remote cache exporters, inline cache creation, exporter progress, verification warnings, and descriptor/result metadata.

Important APIs and types: `Solver.getSessionExporters`, `runCacheExporters`, `runInlineCacheExporter`, `exporterVertexID`, `Solver.runExporters`, `splitCacheExporters`, `inlineCacheExporter`, `asInlineCache`, `inlineCache`, and `withDescHandlerCacheOpts`.

Control flow: session exporters are discovered via session gRPC and resolved through the default worker. Remote cache exporters run concurrently in builder contexts, export the first cache key chain, finalize, and merge responses while respecting `IgnoreError`. Main exporters run concurrently, emit invalid-platform warnings, serialize inline cache generation with a mutex, pass job compatibility version, collect finalize functions/descriptors, and merge response maps. Inline cache extracts remote layer digests from a worker ref, exports cache in min mode with compression variants, then asks the inline exporter for per-layer data.

State and dependencies: mostly transient; no durable state except external exporter side effects. Uses session groups, progress, tracing, errgroup, worker refs, compression config, and cache descriptor handlers attached through solver cache options.

Integration points: called from llbsolver solve completion to produce image/local outputs and cache metadata.

Risks and test signals: concurrent closures must use correct loop variables; inline cache is serialized because exporters may share target state. Session exporter discovery tolerates unavailable/unimplemented. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend.go

Purpose: implements the platform-neutral file operation backend for mkdir, mkfile, symlink, rm, copy, user ownership mapping, wildcard handling, timestamps, and docker-compatible archive unpack.

Important APIs and types: helpers `timestampToTime`, `mkdir`, `symlink`, `mkfile`, `rm`, `rmPath`, `docopy`, `cleanPath`; public `NewFileOpBackend`, `ReadUserCallback`, and `Backend` methods `Mkdir`, `Mkfile`, `Symlink`, `Rm`, `Copy`, `readUserWrapper`.

Control flow: backend methods validate mount types, locally mount snapshot mountables, read owner info from optional user/group mounts, then call helpers. Helpers resolve paths with `fs.RootPath`, trim host-root prefixes from `os.PathError`, apply chown/utime, support wildcard removal/copy, optionally create destination paths, and attempt archive unpack before normal copy when requested.

State and persistence: mutates mounted snapshot filesystems; no separate persistent metadata. Mutable/immutable ref lifecycle is handled by `RefManager`, not this file. Dependencies include continuity fs, BuildKit snapshot/fileoptypes/pb, fsutil copy, user identity mapping, and OS filesystem calls.

Integration points: file op solver invokes this backend to apply LLB file actions to cache refs.

Risks and test signals: path escaping prevention relies on `fs.RootPath`; wildcard and archive behavior can be subtle; xattr errors are logged and ignored during copy. `backend_test.go` covers `rmPath` allow-not-found behavior, while Windows-specific copy behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_test.go

Purpose: verifies `rmPath` semantics for missing and existing paths.

Important APIs and types: `TestRmPathNonExistentFileAllowNotFoundFalse`, `TestRmPathNonExistentFileAllowNotFoundTrue`, and `TestRmPathFileExists`.

Control flow: tests create temporary roots, call `rmPath` with `allowNotFound` true/false, assert `os.ErrNotExist` behavior, create a real file, remove it, and confirm it is gone.

State and dependencies: uses temporary directories/files only. Depends on `os`, `filepath`, `pkg/errors`, and testify.

Integration points: protects file action remove behavior used by LLB file operations.

Risks and test signals: narrow coverage. It does not cover directory removal, wildcard removal, root/path traversal edge cases, or mounted snapshot behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go

Purpose: provides Unix-specific ownership mapping and copy behavior for the file backend.

Important APIs and types: `mapUserToChowner` and `platformCopy`.

Control flow: when no user is specified, the chowner preserves existing ownership, except nil ownership under an idmap maps root to host ids. When a user is specified, it copies the user and maps UID/GID to host ids if an identity mapping exists. `platformCopy` directly delegates to fsutil `copy.Copy`.

State and dependencies: no persistent state; returns callback functions used by copy/chown operations. Depends on BuildKit/user identity mapping and fsutil copy.

Integration points: compiled on non-Windows builds and used by backend mkdir/mkfile/symlink/copy operations.

Risks and test signals: idmap conversion errors fail file actions. The nil-user behavior is subtle because non-nil old ownership is assumed already mapped. No direct Unix-only test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go

Purpose: provides Windows-specific ownership defaults and copy filtering for protected snapshot-root folders.

Important APIs and types: `mapUserToChowner` and `platformCopy`.

Control flow: if no SID is supplied, ownership defaults to `ContainerAdministratorSidString`; otherwise the supplied user is returned. `platformCopy` appends exclude patterns for `System Volume Information` and `WcSandboxState` only when copying from the mount root, then delegates to fsutil `copy.Copy`.

State and dependencies: no durable state. Depends on BuildKit Windows utilities and fsutil copy.

Integration points: compiled on Windows and used by file backend copy/chown paths for container snapshots.

Risks and test signals: excluding protected folders only at root avoids access-denied failures without hiding nested user files with the same names. `backend_windows_test.go` covers this root-only behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go

Purpose: validates Windows `platformCopy` excludes protected folders only when copying from snapshot root.

Important APIs and types: `TestPlatformCopy_RootOnlyProtectedExcludes`.

Control flow: the test creates a source root with a normal folder plus `System Volume Information` and `WcSandboxState`, copies `/`, asserts normal file copied and protected folders absent, then creates a nested protected-named folder under `foo`, copies `/foo`, and asserts the nested folder is copied.

State and dependencies: Windows-only test using temporary directories and files. Depends on `context`, `os`, `filepath`, and testify.

Integration points: protects Windows file-op behavior on container snapshot mounts.

Risks and test signals: good coverage for the intended filter boundary, but it does not simulate actual Windows ACL denial behavior; it verifies path filtering semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go

Purpose: adapts BuildKit cache refs into file operation mounts and commits mutable file-op results.

Important APIs and types: `NewRefManager`, `RefManager`, `Prepare`, `Commit`, and `Mount` methods `Mountable`, `Release`, `IsFileOpMount`, `Readonly`.

Control flow: `Prepare` accepts an immutable ref or nil. For readonly immutable refs it returns a readonly mount directly. Otherwise it creates a mutable ref from the input with retain policy and description, mounts it, and rolls back cache policy/release on failure. `Commit` requires a `Mount` with an active mutable ref, commits it to an immutable ref, releases on commit failure, and clears `mr`.

State and persistence: creates and commits cache mutable refs through `cache.Manager`, which persists snapshot/cache state externally. `Mount` holds current mountable, mutable ref, and readonly flag.

Dependencies and integration: integrates file op solver with BuildKit cache, sessions, snapshot mountables, and logging.

Risks and test signals: failure cleanup is important to avoid orphan mutable refs; committing a readonly mount is invalid. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go

Purpose: implements docker-compatible archive detection and unpacking for file copy actions that request archive extraction.

Important APIs and types: `unpack` and `isArchivePath`.

Control flow: `unpack` resolves source/destination safely under their roots, returns false for non-archive sources, creates destination directory with requested ownership/timestamp, opens the source, builds tar options with best-effort xattrs, optional idmap and chown, then calls `chrootarchive.Untar`. `isArchivePath` rejects non-regular files, opens the source, creates a decompression stream, and checks whether a tar reader can read the first entry.

State and persistence: mutates destination filesystem by creating directories and extracting archive contents. Dependencies include Go tar, BuildKit archive/chrootarchive/compression packages, continuity fs, user idmap, and fsutil copy chowner.

Integration points: called from `docopy` before normal copy when `AttemptUnpackDockerCompatibility` is set.

Risks and test signals: archive sniffing opens/decompresses the source and treats any readable first tar entry as archive. Extraction correctness and security rely on chrootarchive and root path resolution. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/unpack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history.go

Purpose: records build history around a solve, including frontend/exporter metadata, logs, result descriptors, provenance attestations, resource usage, errors, traces, and metrics.

Important APIs and types: `Solver.recordBuildHistory` returns a finalizer function. It builds `controlapi.BuildHistoryRecord`, calls history queue `Update` with STARTED/COMPLETE events, imports status/error blobs, opens blob writers, creates SLSA provenance with `NewProvenanceCreator`, manages trace recording through `detect.Recorder`, and records build metrics.

Control flow: initial call starts trace recording and emits a STARTED event. The returned finalizer closes job progress, copies exporter response metadata, bounds finalization to 300 seconds, concurrently creates provenance for default and named refs, imports job status from a channel, records descriptors, imports errors when present, acquires history finalizer for trace saving, records metrics, emits COMPLETE, and asynchronously saves OTLP trace blobs if available.

State and persistence: persists records and blobs through `s.history` queue; temporary releasers hold leases until record update completes. The history record is mutated through finalization with timestamps, counts, descriptors, errors, and trace metadata.

Dependencies and integration: integrates solver jobs, resources sampler, exporter descriptors, provenance, in-toto media type, tracing recorder, BuildKit history queue, and OTEL metrics.

Risks and test signals: finalization has many concurrent writers guarded by a mutex; errors in history export are converted to internal only if the build error was nil. Trace saving is asynchronous and coordinated with `AcquireFinalizer`. No direct tests in this subset, but metrics tests cover the `recordBuildCompletion` call target.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go

Purpose: implements the build history queue: active/completed record storage, garbage collection, blob import/export, leases, status replay, deletion, finalization, and event listening.

Important APIs and types: `QueueOpt`, `Queue`, `StatusImportResult`, `NewQueue`, `gc`, `clearOrphans`, `delete`, `UpdateRef`, `Status`, `Update`, `Delete`, `OpenBlobWriter`, `Writer`, `ImportError`, `ImportStatus`, `AcquireFinalizer`, `Finalize`, and `Listen`.

Control flow: `NewQueue` configures defaults, creates a separate `_history` containerd namespace, migrates v1 data if needed, starts orphan cleanup/GC loops, and closes pubsub after graceful stop when no active finalizers remain. `Update` tracks active records for STARTED and persists COMPLETE records. `update` writes the protobuf record into Bolt and attaches all referenced blobs to a per-record lease. `ImportStatus` serializes streamed solve statuses as length-prefixed protobuf messages and counts cached/completed/total/warnings. `Listen` returns active, completed, filtered/limited, and live pubsub events while respecting ref deletion deferral.

State and persistence: active records, finalizers, listener ref counts, and deleted refs are in memory under `mu`. Completed records live in Bolt bucket `_records`; blob content and leases live in isolated containerd history namespace.

Dependencies and integration: used by llbsolver build history finalizer and control API history endpoints. Integrates with content store, lease manager, Bolt transactor, grpc error conversion, filters, and pubsub.

Risks and test signals: risks include lease/blob consistency, GC criteria, deletion while listeners hold refs, indefinite goroutines, and status stream framing. Tests in this subset cover filters and pubsub, not full queue persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/filter.go

Purpose: parses and applies build history filters for refs, status, repository, timestamps, durations, and result limits.

Important APIs and types: `filterHistoryEvents`, `parseFilters`, `parseFilter`, `timeBasedFilter`, `adaptHistoryRecord`, and `cutAny`; status constants `running`, `completed`, `error`, and `canceled`.

Control flow: events are first nil-filtered. Multiple filter strings are ORed, while comma-separated fields inside one filter string are ANDed. Time filters support `startedAt`, `completedAt`, and `duration` with `>`, `>=`, `<`, `<=`; timestamp values can be durations relative to now or RFC3339 times. Static filters use containerd filter parsing over an adaptor exposing `ref`, `status`, and `repository`. Limits sort newest-first by `CreatedAt` and reject negative limits.

State and dependencies: no persistence; pure filtering over event slices. Depends on containerd filters, BuildKit git URL parsing, csvvalue parsing, and time.

Integration points: `Queue.Listen` uses this before returning completed history records.

Risks and test signals: duration comparisons convert `time.Duration` to int64 nanoseconds while timestamp comparisons use Unix seconds. Repository extraction falls back from `vcs:source` to parsed `context`. `filter_test.go` covers ref/repository/status-like time/limit/or/and/error cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go

Purpose: validates build history filtering and limiting.

Important APIs and types: `TestHistoryFilters` creates three `BuildHistoryEvent` records with refs, frontend attrs, created/completed timestamps, then table-drives `filterHistoryEvents`.

Control flow: cases cover no match, ref prefix, repository inequality, repository parsed from git context, limit newest-first, invalid filter parsing, multi-field AND, relative completed/started time, duration, OR across filter strings, and no-filter limiting.

State and dependencies: test-only events based around `time.Now().Add(-24h)`. Dependencies include control API protobufs, testify, and timestamppb.

Integration points: protects `Queue.Listen` filtering behavior for CLI/API history requests.

Risks and test signals: good behavioral coverage for supported syntax. It does not cover `status` filters explicitly or RFC3339 absolute timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go

Purpose: migrates build history blobs and leases from the main containerd namespace to the isolated history namespace used by Queue v2.

Important APIs and types: `Queue.migrateV2`, `blobRefs`, and `migrateBlobV2`.

Control flow: `migrateV2` scans Bolt records, lists old per-record lease resources, migrates content resources recursively, creates matching leases in the history namespace, attaches migrated resources, deletes old leases, and records version `2`. `blobRefs` reads content labels and optionally inspects OCI manifests to avoid treating skipped layers as references. `migrateBlobV2` copies content by digest to the history store with reconstructed GC labels and recursively migrates referenced blobs, tolerating missing source blobs by returning false.

State and persistence: mutates Bolt `_version`, old/new lease managers, and old/new content stores. Temporary migration leases guard content during copy.

Dependencies and integration: called from `NewQueue` when the stored version is absent or not greater than one.

Risks and test signals: migration deliberately allows missing blobs in some paths, which can later cause record deletion as orphaned. Recursive copy ignores errors for nested refs in one place. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go

Purpose: small generic pubsub implementation for live build history events.

Important APIs and types: `pubsub[T]`, `channel[T]`, `Subscribe`, `Send`, `Close`, `channel.send`, and `channel.close`.

Control flow: subscribing creates a buffered channel and done channel, adds it to the subscriber map under lock, and returns it. Sending snapshots current subscribers under lock by launching a goroutine per subscriber send; each send either writes to the buffered channel or exits if closed. Close iterates current subscribers and closes each idempotently. Channel close removes itself from the parent map and closes `done` via `sync.Once`.

State and dependencies: in-memory subscriber map under mutex; each subscriber has a buffered `ch` of size 32. Depends only on `sync`.

Integration points: `history.Queue` uses it to broadcast STARTED, COMPLETE, DELETED, and graceful-close events to listeners.

Risks and test signals: send starts goroutines while holding the pubsub lock, which avoids blocking on full subscribers but can create many goroutines under high fanout. Tests cover send/receive, close, idempotent close, and concurrent send/receive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go

Purpose: verifies pubsub delivery, closure, idempotency, and basic concurrency.

Important APIs and types: `TestPubsubSendReceive`, `TestPubsubClose`, `TestPubsubCloseIdempotent`, and `TestPubsubConcurrent`.

Control flow: tests subscribe one or more channels, send values, assert delivery, close one subscriber and verify it no longer receives, close all subscribers, and use a wait group to send/receive 100 messages across 10 subscribers.

State and dependencies: test-only in-memory pubsub. Depends on `sync`, `testing`, and testify.

Integration points: protects live history event delivery used by `Queue.Listen`.

Risks and test signals: concurrency test assumes all subscriber buffers/readers keep up. It does not test slow subscribers filling buffers or `pubsub.Close` during active sends.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/pubsub_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go -->
## sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go

Purpose: merges Linux resource metadata from shared vertices so a vertex reused by multiple jobs is not constrained by the strictest sibling.

Important APIs and types: `Metadata` implementing `solver.VertexMetadata.Merge`, `mergeRelaxed`, `relaxedMemory`, `relaxedMemorySwap`, `relaxedCPUShares`, `relaxedCPUBandwidth`, and `relaxedCpuset`.

Control flow: metadata merge returns self for nil/unknown metadata and otherwise returns a new `Metadata` with relaxed `pb.LinuxResources`. Memory treats `0` as unlimited; memory swap treats `0` as unset and `-1` as unlimited; CPU shares treats `0` as unset; CPU bandwidth chooses the quota/period pair with higher effective cap and shorter period on ties; cpuset empty string is most relaxed, otherwise parsed sets are unioned and formatted.

State and dependencies: no persistence; clones nil-side resources to avoid pointer aliasing. Depends on solver metadata, BuildKit protobuf Linux resources, and `util/cpuset`.

Integration points: `WithLinuxResourcesMetadata` in LLB loading attaches this metadata, and `solver/jobs.go` merges metadata when shared active states are reused.

Risks and test signals: CPU quota cross multiplication can overflow for extreme values, though typical cgroup values are bounded. Parse errors fall back to the side that parsed cleanly or the first invalid value. `merge_test.go` covers many relaxation cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go

Purpose: validates relaxed merging semantics for Linux resource metadata.

Important APIs and types: `TestMergeRelaxed` table of subtests over `mergeRelaxed`.

Control flow: tests cover nil handling and clone/no-alias behavior, memory unlimited and max behavior, memory-swap unset/unlimited/max semantics, CPU shares unset/max semantics, CPU quota unlimited and pairwise cap comparison, equal quota shorter period, cpuset unset/union/canonical range formatting, and all-fields merge together.

State and dependencies: test-only protobuf resources. Depends on testify.

Integration points: protects shared-vertex resource metadata merging in solver state.

Risks and test signals: coverage is broad for documented semantics. It does not cover invalid cpuset parse fallback or extremely large quota/period values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics.go -->
## sources/cloud-native/buildkit/solver/llbsolver/metrics.go

Purpose: defines OpenTelemetry build completion metrics emitted by llbsolver when build history finalization completes.

Important APIs and types: constants for instrumentation name and attribute keys/values, `buildMetrics`, `newBuildMetrics`, and `(*buildMetrics).recordBuildCompletion`.

Control flow: `newBuildMetrics` uses a no-op meter provider when nil, creates counters `buildkit.builds` and `buildkit.builds.steps`, and histogram `buildkit.build.duration`. `recordBuildCompletion` no-ops for nil receiver/record, records one build with bounded `status` and optional `error_code`, records completed/cached/total/warning step counters by `kind`, and records duration in seconds when both timestamps are present.

State and dependencies: instruments are shared and concurrency-safe through OTEL. No custom persistence. Dependencies are control API records, OTEL metric API, noop provider, and gRPC codes.

Integration points: called from `recordBuildHistory` immediately before emitting the COMPLETE history event.

Risks and test signals: labels intentionally avoid frontend and error message to control cardinality. Missing timestamps skip duration only. `metrics_test.go` covers success, failure codes, step counters, nil safety, and nil provider behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go

Purpose: verifies OTEL build metric registration and observations.

Important APIs and types: helpers `newTestMetrics`, `collect`, `findCounterPoint`, `attrsContain`, and tests `TestRecordBuildCompletion_Success`, `TestRecordBuildCompletion_FailureGRPCCodes`, `TestRecordBuildCompletion_StepCounters`, `TestRecordBuildCompletion_NilSafe`, and `TestNewBuildMetrics_NilProviderUsesNoop`.

Control flow: tests use an SDK manual reader to synchronously collect metric data, then assert build counters by attributes, absence of `error_code` on success, histogram count/sum/status, failure code labels for several gRPC codes, step counter values by kind, nil receiver/record no panic, and nil provider creates usable noop metrics.

State and dependencies: test-only meter provider/manual reader. Depends on OTEL SDK metricdata, testify, control API records, gRPC status codes, and timestamppb.

Integration points: protects metrics emitted from build history completion finalizer.

Risks and test signals: strong coverage for bounded labels and values. It does not test concurrent metric recording, relying on OTEL API guarantees.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/metrics_test.go -->
