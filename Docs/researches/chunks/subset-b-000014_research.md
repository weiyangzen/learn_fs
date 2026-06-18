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
