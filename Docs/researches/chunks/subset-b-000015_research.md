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
