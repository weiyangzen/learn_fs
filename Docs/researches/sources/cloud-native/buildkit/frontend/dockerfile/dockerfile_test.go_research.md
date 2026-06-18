# Research: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_test.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000014`: lines 1-10129, `Docs/researches/chunks/subset-b-000014_research.md`
- `subset-b-000015`: lines 10130-11727, `Docs/researches/chunks/subset-b-000015_research.md`

## Chunk Research

### subset-b-000014: lines 1-10129

# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_test.go chunk subset-b-000014

## Scope

This chunk covers `sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_test.go` lines 1-10129, the first and largest chunk of BuildKit's Dockerfile frontend integration test file. It starts at package imports and test registration and ends mid-function inside `testSBOMScannerArgs`; the remaining SBOM scanner argument assertions and helper frontend/security/network implementations are in the next chunk.

## Purpose

The chunk is a broad integration-test suite for the Dockerfile frontend. It validates Dockerfile parsing, build graph generation, local/remote context handling, image and tar/OCI exporters, cache import/export, platform matrix behavior, named contexts, reproducible timestamps, SBOM attestation wiring, and many Linux/Windows compatibility differences. The tests exercise the frontend through the common `frontend` abstraction so the same behavioral contract is applied to built-in, client, and gateway Dockerfile frontends.

`TestIntegration` is the main entry point. It runs `allTests`, lint/heredoc/outline/target tests declared elsewhere, non-Windows reproducibility tests, entitlement-specific security/network matrices, and provenance attestation tests. Initialization selects worker backends (`dockerd`, OCI, containerd) and frontend variants based on environment variables such as `FRONTEND_BUILTIN_ONLY`, `FRONTEND_CLIENT_ONLY`, and `FRONTEND_GATEWAY_ONLY`.

## Important APIs, Types, And Helpers

- `frontend` interface: abstracts `Solve`, `SolveGateway`, `DFCmdArgs`, and `RequiresBuildctl`. Concrete implementations are outside this chunk, but all tests depend on it for consistent invocation across frontend modes.
- `allTests`, `securityTests`, `networkTests`, `heredocTests`, `reproTests`: integration test registries. `allTests` includes most Dockerfile behavior tests; `reproTests` isolates `SOURCE_DATE_EPOCH` and reproducibility cases behind non-Windows and feature checks.
- `opts` and `securityOpts`: global integration runner options. `opts` installs mirrored images and a `"frontend"` matrix.
- `tarContextFile` and `makeTarContext`: build synthetic tar contexts with deterministic file contents and mtimes for HTTP/archive timestamp tests.
- `readOCIImage`, `readOCIImageCreated`, `readOCIManifest`, `readOCILayerMap`: parse OCI/tar exporter output with `testutil.ReadTarToMap`, OCI index/manifest/config JSON, and layer tar contents.
- Core external APIs used throughout: `client.New`, `client.SolveOpt`, `client.ExportEntry`, `client.CacheOptionsEntry`, `gateway.Client`, `gateway.SolveRequest`, `llb.State`, `contentutil.ProviderFromRef`, containerd image/content services, `integration.Tmpdir`, `fstest`, `httpserver.NewTestServer`, `uploadprovider.New`, and `filesync.NewFSSyncProvider`.

## Control Flow And Test Structure

Most tests follow a repeated pattern: create a temporary Dockerfile/context with `fstest`, open a BuildKit client to `sb.Address()`, call `f.Solve` or `c.Build` with `client.SolveOpt`, export to local/tar/OCI/image output, and assert either filesystem contents, image metadata, cache reuse, status stream vertices, or expected errors.

The early chunk establishes fundamental Dockerfile semantics:

- ARG/ENV expansion and empty values: `testEmptyStringArgInEnv`, `testDefaultEnvWithArgs`, `testEnvEmptyFormatting`, `testQuotedMetaArgs`, `testGlobalArgErrors`, `testArgDefaultExpansion`, `testMultiArgs`, `testBuiltinArgs`, and `testTargetStageNameArg`.
- Context filtering and Dockerfile selection: `.dockerignore`, per-Dockerfile ignore overrides, invalid ignore files with timeout guard, lower-case `dockerfile`, symlinked Dockerfile, external Dockerfile with tar context, HTTP/Git contexts, and `dockerfilekey`/`contextsubdir`.
- COPY/ADD semantics: empty destination strings, trailing slash preservation, `COPY --link`, wildcards, symlink traversal, sockets converted to regular files, relative copy destinations, `COPY --from` restrictions, archive unpacking, URL ADD, `--chown`, `--chmod`, and invalid chmod errors.
- Multi-stage and ONBUILD behavior: implicit `COPY --from=image`, case-insensitive stage names, out-of-order stage errors, ONBUILD clearing, child-stage inheritance, named context use in ONBUILD, new graph dependencies introduced by ONBUILD, and ONBUILD cache mounts.
- Export behavior: local, tar, OCI, and image exporters; multi-platform local and OCI export; image labels, exposed ports, history, default shell/PATH, scratch config, and containerd-backed image inspection.

The middle and later parts focus on caching, platform routing, named contexts, and frontend gateway behavior:

- Cache tests cover local and registry cache import/export, inline multi-platform cache reuse, image-manifest cache media types, reproducible image IDs with and without cache import, full and stage-specific `no-cache`, and cache mount behavior under no-cache.
- Platform tests cover implicit and explicit `TARGETOS`, `TARGETARCH`, `TARGETPLATFORM`, `BUILDPLATFORM`, platform-specific export folder names, manifest-list contents, and platform selection for named image contexts.
- Gateway/frontend tests cover forwarded solve results, `Evaluate` error surfacing, `FrontendInputs`, subrequest/capability errors, and status stream step names.
- Named-context tests cover `docker-image://`, `local:`, `oci-layout:`, `input:` contexts, custom local session IDs, per-platform input contexts, scratch replacement, timestamp behavior for overridden image contexts, OCI layout export preservation, and filtered transfer of named local contexts.

The tail of this chunk covers reproducibility and SBOM:

- `SOURCE_DATE_EPOCH` tests validate Dockerfile defaults, frontend overrides, exporter reset, invalid values, context-derived timestamps from Git/HTTP archive/HTTP `Last-Modified`, local context unset behavior, stage-derived timestamps, named-context-derived timestamps, image `Created` fields, history timestamps, layer rewrite annotations, and the value visible inside build steps.
- `testSBOMScannerImage` builds a scanner image that emits an in-toto/SPDX statement, then uses `attest:sbom=generator=...` to verify an attestation appears as an `unknown/unknown` image with the expected statement while the normal image keeps its layer content.
- `testSBOMScannerArgs` starts by building a scanner image that emits a core SPDX statement and optional extra statements from `BUILDKIT_SCAN_SOURCE_EXTRAS`, then begins the first target-image solve. Its complete assertions continue in chunk `subset-b-000015`.

## State And Persistence Behavior

The tests intentionally create and inspect persistent BuildKit-side state:

- Cache state is exported to local directories or registries, pruned with `ensurePruneAll`, then re-imported to prove stable outputs and cache hits. Tests compare random/unique files before and after prune to distinguish cached from re-executed steps.
- Image state is exported to containerd or pushed to ephemeral registries and then re-read with containerd content services or `contentutil.ProviderFromRef`.
- OCI layout state is materialized by extracting OCI tar output to a temporary directory, opening it as a `local.Store`, and using `context:<name>=oci-layout:<store>@sha256:<digest>` in later solves.
- Session state is exercised through upload providers, frontend inputs, local custom session IDs, and file sync providers.
- Reproducibility state is encoded in OCI image config timestamps, history entries, layer annotations, and layer tar contents.

All filesystem writes are test-local (`t.TempDir`, `integration.Tmpdir`) except deliberate inspection of host cgroup v2 files in `testCgroupParent`/`testLinuxResources`, which skip on Windows/rootless/missing cgroup v2.

## Dependencies And Integration Points

This chunk integrates Dockerfile frontend code with the BuildKit client, gateway frontend protocol, LLB, session/file sync/upload mechanisms, containerd image/content APIs, OCI image-spec structures, BuildKit cache exporters/importers, temporary registries, HTTP test servers, Git command-line repositories, and test worker feature gates.

Feature checks are important integration gates. Tests require capabilities such as image exporter, OCI exporter, direct push, cache export/import backends, OCI layout support, multi-platform builds, SBOM, and `SOURCE_DATE_EPOCH`. Platform checks split Linux/Windows behavior heavily; many UID/GID, symlink, cgroup, socket, git-source, cache-mount, SBOM, and reproducibility tests are Linux-only, while Windows variants use nanoserver, `cmd.exe`, CRLF normalization, and different path/layer expectations.

## Risks And Edge Cases Covered

- Cache invalidation and reuse can silently regress; tests compare random outputs, digests, stage-specific no-cache behavior, wildcard rename invalidation, and multi-platform inline cache reuse.
- Context handling is security-sensitive; tests cover `.dockerignore`, named local filtering, symlink traversal, Git/HTTP sources, Dockerfile-specific ignores, custom session IDs, and large-file transfer boundaries.
- Metadata correctness is broad: labels, exposed ports, history, default shell/PATH, `Config.User`, scratch image config, rootfs diff IDs, platform fields, mtimes, and provenance/SBOM attachment paths.
- UID/GID and chmod behavior can diverge between source files, directories, existing destinations, archives, and variable expansion; Linux-only tests verify those details explicitly.
- Multi-platform results can mix refs or metadata; tests assert per-platform layer contents, env propagation, manifest ordering, and platform-specific input contexts.
- Reproducibility depends on multiple timestamp sources; tests assert Dockerfile ARG precedence, context/stage/named-context derivation, exporter reset behavior, invalid input errors, and layer annotation rewriting.
- Gateway/frontend integration can hide errors; tests exercise `Evaluate`, forwarded results, unsupported subrequests/caps, and status vertex names.

## Test Signals

Positive signals are `require.NoError` solves plus concrete assertions on exported files, tar maps, OCI image structs, registry-read image contents, containerd image configs, and status streams. Negative signals include expected Dockerfile parse/build errors for invalid instructions, invalid JSON command suffixes, invalid chmod values, out-of-order stage references, unsupported variable expansion in `COPY --from`, empty-stage Dockerfiles, invalid `.dockerignore`, invalid `SOURCE_DATE_EPOCH`, and invalid source-only stage use for timestamp derivation.

This chunk is itself a test file, so it does not define production APIs. Its value is as a comprehensive behavioral contract for the Dockerfile frontend and its integration with workers, exporters, caches, remote sources, sessions, and image metadata.

### subset-b-000015: lines 10130-11727

# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_test.go lines 10130-11727

## Purpose

This chunk is the tail of BuildKit's Dockerfile frontend integration test suite. It validates late-stage behavior around SBOM attestations, OCI/image exporters, reproducible timestamps, gateway input validation, Unicode paths, named contexts and source policy, linter warnings for platform mismatches, build history persistence, OSVersion-aware platform selection, target-name typo suggestions, cleanup helpers, and frontend adapter implementations used by the broader test file.

The code is test-focused but covers real integration contracts among the Dockerfile frontend, `client.Solve`, gateway builds, local/registry/OCI exporters, content stores, build history APIs, and worker feature gates.

## Important APIs, Types, and Functions

- `testOCILayoutMultiname`: verifies `client.ExporterOCI` supports a comma-separated `name` attribute and records multiple OCI index manifest entries pointing at the same manifest digest but with distinct image-name/ref-name annotations.
- `testReproSourceDateEpoch`: validates `SOURCE_DATE_EPOCH` plus image exporter `rewrite-timestamp=true` produces deterministic image digests, annotates rewritten non-base layers, leaves base image history immutable, avoids mutating registry cache export layer annotations, and remains stable after cache pruning.
- `testMultiNilRefsOCIExporter`: confirms a multi-platform `FROM scratch` build with nil refs exports an OCI layout containing a top-level index with one manifest-list descriptor and a nested index containing the two requested platforms.
- `timeMustParse`: small test helper that parses fixed timestamps and fails the test on parse errors.
- `readImage`: reads an image reference through `contentutil.ProviderFromRef`, parses the manifest and config, and verifies every layer blob digest is readable and matches its descriptor. It is used by reproducibility checks and image metadata assertions.
- `testNilContextInSolveGateway`: uses `c.Build` and `f.SolveGateway` with nil frontend input definitions to assert the daemon returns `"invalid nil input definition to definition op"` instead of panicking.
- `testMultiNilRefsInSolveGateway`: builds a Dockerfile LLB definition directly with `llb.Scratch().File(...).Marshal(ctx)`, passes it as the Dockerfile frontend input, and verifies multi-platform gateway solve succeeds without explicit context input.
- `testCopyUnicodePath`: verifies `COPY` handles literal UTF-8 names, percent-encoded-looking names, and plus signs as distinct local filesystem paths on both Unix and Windows Dockerfile variants.
- `testSourcePolicyWithNamedContext`: combines `FrontendAttrs["context:replace"]`, a local mount named `test`, and `spb.PolicyAction_CONVERT` to redirect an image named context to `local://test`.
- `testEagerNamedContextLookup`: asserts unused named contexts are not resolved eagerly, even when their configured image references are invalid.
- `testBaseImagePlatformMismatch`: pushes an image for a different platform, then checks the Dockerfile linter emits `InvalidBaseImagePlatform`; Unix expects structured warning data, while Windows matches a regex because the platform string includes an OS version.
- `testHistoryError`: verifies a failed build record persists an external serialized gRPC status in the content store, can be reconstructed as a typed BuildKit error with stack traces, contains vertex metadata, and retains Dockerfile source info.
- `testHistoryFinalizeTrace`: finalizes build history for a successful build and verifies persisted trace metadata contains a digest.
- `testPlatformWithOSVersion`: builds and pushes a synthetic multi-platform image whose platform OS is `windows` with two OSVersion values, then checks later pulls choose the manifest matching the requested OSVersion and expose `TARGETOSVERSION`/`TARGETPLATFORM` correctly.
- `testMaintainBaseOSVersion`: verifies an image exported with a Windows OSVersion keeps that OSVersion when used as a base for another image, even when the later requested platform omits OSVersion.
- `testTargetMistype`: checks a misspelled target (`bulid`) reports a helpful suggestion for the available stage (`build`).
- `runShell`: test utility for running shell commands cross-platform (`powershell -command` on Windows, `sh -c` otherwise) in a given directory.
- `ensurePruneAll`: retrying cache cleanup helper that calls `c.Prune(..., client.PruneAll)` and polls `c.DiskUsage` to handle async cache release.
- `checkAllReleasable`: deletes build history records, waits for no in-use disk usage records, prunes all cache, and optionally checks containerd snapshots/content are empty in the `buildkit` namespace.
- `newContainerd`: opens a containerd client with a 60 second timeout.
- `dfCmdArgs`: builds a `buildctl build --progress=plain ... --trace=<tempfile>` command string and returns the trace path.
- `builtinFrontend`, `clientFrontend`, `gatewayFrontend`: implementations of the test-local `frontend` interface. They route solves through the built-in `dockerfile.v0`, the in-process `builder.Build`, or the `gateway.v0` frontend with `source=<gw>`.
- `getFrontend`: fetches the active frontend adapter from `integration.Sandbox.Value("frontend")`.
- `secModeSandbox`, `secModeInsecure`, `networkModeHost`, `networkModeSandbox`: `integration.ConfigUpdater` helpers that grant or deny insecure entitlements in generated BuildKit config.
- `fixedWriteCloser`: adapts an `io.WriteCloser` to `filesync.FileOutputFunc` for exporter tests that stream tar output into a provided writer.

## Control Flow and Test Behavior

The SBOM section at the start of the chunk continues a preceding test. It builds and pushes images with `attest:sbom=generator=<scannerTarget>` and `BUILDKIT_SBOM_SCAN_CONTEXT` / `BUILDKIT_SBOM_SCAN_STAGE` build args, then reads the pushed image back and inspects the `unknown/unknown` attestation image. It expects one core attestation when scanning is constrained, four layers when extra SBOMs are enabled across context/stages, and only the core attestation when scan args are set to false.

Most tests follow the same integration pattern: create a temporary Dockerfile/context using `integration.Tmpdir` and `fstest.CreateFile`, create a `client.Client` from `sb.Address()`, select `f := getFrontend(t, sb)`, call `f.Solve` or `f.SolveGateway`, and assert either exported filesystem content, OCI layout/index metadata, pushed registry image metadata, lint output, or build history records.

Exporter tests use both output-directory and streaming-output paths. `testOCILayoutMultiname` writes an unpacked OCI layout with `tar=false`, then repeats as a tar stream into a `bytes.Buffer` through `fixedWriteCloser`; both paths must produce equivalent `index.json` annotations. `testMultiNilRefsOCIExporter` writes a tar file, parses it with `testutil.ReadTarToMap`, then descends from top-level `index.json` into the blob holding the nested image index.

Reproducibility flow is deliberately multi-pass. Each test case builds and pushes with `SOURCE_DATE_EPOCH`, OCI media types, timestamp rewriting, and registry cache export. It reads image and cache manifests, asserts an exact digest, checks layer annotations, prunes all cache with `ensurePruneAll`, rebuilds to confirm digest stability, and finally rebuilds without `rewrite-timestamp` to prove rewritten timestamp annotations are gated by exporter attrs.

Gateway tests exercise error and nil-input paths that are easy to miss in regular CLI flows. One intentionally passes nil `pb.Definition` values for context and Dockerfile inputs and expects a controlled error. The other passes only a Dockerfile LLB definition with a multi-platform frontend option and expects success.

Build history tests use explicit `Ref` values from `identity.NewID()` to locate records. On error, `ListenBuildHistory` should emit a record with inline error summary and an external serialized status blob, stored in BuildKit content. On finalize, `UpdateBuildHistory(Finalize: true)` should materialize trace metadata visible through `ListenBuildHistory`.

The final adapter section defines how the same suite can run through different frontend paths. `builtinFrontend` sets `opt.Frontend = "dockerfile.v0"` before `c.Solve`; `clientFrontend` calls `c.Build(..., builder.Build, ...)`; `gatewayFrontend` sets `gateway.v0` and injects `source`. This is central to interpreting failures because the same test logic may run against different frontend execution modes.

## State and Persistence Behavior

Persistent state is mostly external to the test process:

- Temporary filesystem contexts and local exporter outputs are created under test-managed temp directories.
- Registry-backed tests push images and cache manifests to `sb.NewRegistry()` references, then re-open them via `contentutil.ProviderFromRef`.
- Image verification reads OCI manifests, configs, layers, and raw attestation layers from content providers. `readImage` additionally validates blob digest integrity for every layer.
- Build cache state is pruned by `ensurePruneAll`, which accounts for delayed release by retrying prune and polling disk usage.
- Build history is persisted in the daemon and read via `ControlClient().ListenBuildHistory`; external error and trace artifacts are stored as content blobs referenced by digest/size/media type.
- `checkAllReleasable` can delete build history records, prune cache, and inspect containerd snapshot/content stores to assert no residual state remains.

## Dependencies and Integration Points

This chunk depends heavily on BuildKit integration harness packages and container image APIs:

- `integration.Sandbox` supplies context, BuildKit address, optional registry, snapshotter name, containerd address, frontend adapter value, and platform-specific helpers.
- `client.SolveOpt` carries `LocalMounts`, `FrontendAttrs`, `Exports`, `CacheExports`, `SourcePolicy`, and `Ref`.
- `dockerui.DefaultLocalNameDockerfile` and `dockerui.DefaultLocalNameContext` are the canonical local mount names for Dockerfile frontend input.
- Exporters include `client.ExporterImage`, `client.ExporterOCI`, and `client.ExporterLocal`; tests rely on attrs such as `name`, `push`, `tar`, `oci-mediatypes`, and `rewrite-timestamp`.
- OCI/image inspection uses `ocispecs.Index`, `ocispecs.Manifest`, `ocispecs.Image`, `platforms.Format/FormatAll/Normalize`, `digest.Digest`, and `content.ReadBlob`.
- Gateway paths use `gateway.Client`, `gateway.SolveRequest`, `pb.Definition`, and `llb` marshaling.
- Policy conversion uses `spb.Policy`, `spb.Rule`, `spb.PolicyAction_CONVERT`, selector identifiers, and update identifiers.
- Build history and error reconstruction use `controlapi.BuildHistoryRequest`, `controlapi.UpdateBuildHistoryRequest`, `statuspb.Status`, `anypb.Any`, `status.FromProto`, `grpcerrors.FromGRPC`, `stack.Traces`, `errdefs.VertexError`, and `errdefs.Sources`.
- Containerd cleanup inspection uses `ctd.Client`, `namespaces.WithNamespace`, snapshot walking, and content-store walking.

## Risks and Edge Cases

- Exact digest assertions in `testReproSourceDateEpoch` are sensitive to BuildKit version, base image content, snapshotter behavior, hardlink handling, and exporter serialization. The test skips the native snapshotter and logs that digests may change with environment.
- Several tests require feature gates (`FeatureOCIExporter`, `FeatureSourceDateEpoch`, `FeatureMultiPlatform`, `FeatureDirectPush`) and/or an available test registry. Missing capabilities skip or fail before reaching behavioral assertions.
- Windows handling is special throughout: some tests skip Windows, some choose `nanoserver` Dockerfiles, and linter platform output needs regex matching because OSVersion appears in formatted platform strings.
- `testEagerNamedContextLookup` relies on invalid remote references not being pulled unless used; any future eager validation could break this contract even if the final build output would not need those contexts.
- `testSourcePolicyWithNamedContext` is sensitive to exact source identifier schemes (`docker-image://...` selector versus frontend attr `docker-image:...`) and local named mount `test`.
- `testHistoryError` intentionally expects `resp.Record.Error.Details` to be empty while the external status blob carries reconstructable typed details; changing where error details are stored would affect this assertion.
- Cleanup helpers contain polling loops and time sleeps; slow cache release, containerd state lag, or namespace/snapshotter differences can create flakes.
- `clientFrontend.RequiresBuildctl` skips buildctl-dependent scenarios, so test coverage differs by frontend adapter.

## Test Signals

The chunk's assertions provide signals for:

- SBOM attestations are attached as an `unknown/unknown` image, contain expected intoto statement predicates, and respect scan enable/disable build args.
- OCI layout multiname export creates multiple descriptor annotations for one manifest digest in both unpacked and tar modes.
- `SOURCE_DATE_EPOCH` timestamp rewriting is confined to exported image layers beyond base layers, does not mutate cache export layers, and remains reproducible after pruning.
- Multi-platform empty/scratch builds preserve a nested image index even when refs are nil.
- Gateway nil input definitions return a controlled error instead of daemon panic.
- Unicode and URL-looking filenames are copied literally.
- Source policy can redirect a Docker image named context to a local context.
- Unused named contexts are lazy and do not force failing pulls.
- Linter reports platform mismatches with the correct rule name, level, and line information.
- Build history records retain external error blobs, typed error metadata, Dockerfile source locations, and finalized traces.
- OSVersion-aware platform selection and OSVersion preservation work for Windows platform metadata even when tests run on non-Windows hosts with synthetic platform values.
- Misspelled target names produce a suggestion.
