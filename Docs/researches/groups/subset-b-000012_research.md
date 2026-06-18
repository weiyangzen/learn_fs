# subset-b-000012 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export.go -->
# sources/cloud-native/buildkit/exporter/local/export.go

Purpose: implements the `local` exporter, which streams build result files from BuildKit back to a client-side directory through the active session. The exporter handles single-result refs, multi-platform refs, optional platform directory splitting, local exporter modes, attestation files, and reproducible timestamps via `SOURCE_DATE_EPOCH`.

Important APIs and functions: `Opt` carries the `session.Manager`; `New` returns an `exporter.Exporter`; `Resolve` validates `CreateFSOpts`; `localExporterInstance` implements exporter metadata and `Export`; `NewProgressHandler` emits throttled progress updates and returns an explicit closer. `Export` resolves session caller access, parses platform metadata with `exptypes.ParsePlatforms`, builds filtered `fsutil.FS` values through `CreateFS`, and calls `filesync.CopyToCaller`.

Control flow: export options are loaded before runtime. During export, epoch is inherited from source metadata when not explicitly configured. Multi-platform inputs must include exporter platform mapping; without `platform-split`, duplicate output paths across platforms are rejected. Delete mode merges all output filesystems and transfers with `WithExporterMultiPlatformTransfer`; copy mode runs one transfer per platform using `errgroup`.

State and persistence: no durable server-side state is created, but mounted refs require cleanup; temporary progress state is in the progress writer. Shared `visitedPath` is protected by a mutex to detect collisions. Output persistence happens on the client through the filesync session.

Dependencies and integration: integrates cache refs, exporter source metadata, session/filesync, `CreateFS`, `staticfs.MergeFS`, epoch utilities, and BuildKit client exporter modes. Platform IDs are converted to safe directory names by replacing `/` with `_`.

Risks and test signals: main risks are missing platform mappings, platform path collisions when split is disabled, session lookup timeouts, cleanup leaks, and progress writer leaks. The progress closer comment signals a prior cleanup concern. Behavior is exercised indirectly by local/tar exporter integration tests and by epoch parsing tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export_unix.go -->
# sources/cloud-native/buildkit/exporter/local/export_unix.go

Purpose: provides the non-Windows implementation of local exporter filesystem walking.

Important API: `fsWalk(ctx, fs, s, walkFn)` is the platform abstraction used by `export.go` while checking duplicate paths before transfer.

Control flow: the Unix build simply delegates to `fsutil.FS.Walk` with the given context, start path, and callback. It has no special privilege elevation, filtering, or retry behavior.

State and persistence: no state is stored; it is a thin call-through over the output `fsutil.FS`.

Dependencies and integration: selected by `//go:build !windows`; shares the same package and signature as the Windows implementation so `export.go` can remain platform-neutral.

Risks and test signals: risk is limited to whatever the underlying filesystem walk returns. Platform-specific coverage is normally via exporter integration tests on Unix runners.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export_windows.go -->
# sources/cloud-native/buildkit/exporter/local/export_windows.go

Purpose: provides the Windows implementation of local exporter filesystem walking.

Important API: `fsWalk(ctx, fs, s, walkFn)` matches the Unix signature but wraps the walk in `winio.RunWithPrivilege(winio.SeBackupPrivilege, ...)`.

Control flow: caller-supplied filesystem walking is executed while holding backup privilege so Windows rootfs or metadata files that require elevated read semantics can be traversed.

State and persistence: no persistent state; privilege scope is bounded to the callback executed by `go-winio`.

Dependencies and integration: used only on Windows through build tags. It integrates with the same duplicate-path validation path in `local/export.go`.

Risks and test signals: failures depend on process privilege availability and special Windows files. The in-code reference to issue 4994 explains the special-file motivation. Windows exporter and tar tests are the main regression signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/export_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/fs.go -->
# sources/cloud-native/buildkit/exporter/local/fs.go

Purpose: constructs the exported filesystem view shared by local and tar exporters. It mounts cache refs, applies idmap and epoch metadata normalization, filters attestations to inline-only data, unbundles attestations, creates in-toto statements over exported subjects, and merges statement files into the output filesystem.

Important APIs and types: `CreateFSOpts` holds `Epoch`, `AttestationPrefix`, and `PlatformSplit`; `UsePlatformSplit` defaults split behavior to multi-ref exports; `Load` parses exporter attrs including `source-date-epoch`, `platform-split`, `attestation-prefix`, and `mode`; `CreateFS` returns an `fsutil.FS`, cleanup function, and error.

Control flow: `CreateFS` either creates a temporary empty directory for nil refs or mounts an immutable ref with a session group. It wraps the root in `fsutil.NewFilterFS`, optionally remapping host ids into container ids and overriding `ModTime`. Attestations are filtered/unbundled, regular files are hashed as in-toto subjects, statements are marshaled to deterministic JSON, and a `staticfs` overlay is merged into the output.

State and persistence: temporary directories and mounted refs require caller cleanup. Attestation output exists only in the exported FS unless the caller transfers it. Duplicate statement filenames are rejected per export.

Dependencies and integration: used by local and tar exporters; integrates cache mounting, snapshot `LocalMounter`, session groups, `attestation.MakeInTotoStatements`, `result` metadata, `fsutil`, `staticfs`, and OCI digest helpers.

Risks and test signals: risks include cleanup leaks, idmap exclusion of unmappable files, duplicate attestation basenames, platform filename ambiguity when split is disabled, and expensive whole-tree hashing. Indirect coverage comes from local/tar export and attestation integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/local/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/oci/export.go -->
# sources/cloud-native/buildkit/exporter/oci/export.go

Purpose: implements OCI and Docker image archive exporters. It commits image metadata and layers via `containerimage.ImageWriter`, builds an archive content provider, then either streams a tarball to the caller or copies content into a caller content store.

Important APIs and types: `ExporterVariant` distinguishes `client.ExporterOCI` and `client.ExporterDocker`; `Opt` carries session, image writer, variant, and lease manager; `Resolve` parses image commit opts and `tar`; `imageExporterInstance.Export` performs commit and transfer; `normalizedNames` parses and tag-normalizes comma-separated names.

Control flow: Docker variant rejects manifest lists. Metadata is cloned and augmented, annotations are parsed, OCI type defaults are set, and commit opts are validated. A temporary lease protects committed content until a `DescriptorReference` owns cleanup. Export response includes image digest, optional config digest, descriptor JSON as base64, and normalized image names. Refs are un-lazied concurrently, descriptors are added to a multiprovider, and archive export streams through `filesync.CopyFileWriter` when `tar=true`; otherwise a session content store receives the descriptor chain.

State and persistence: content is retained through leases and descriptor references. The caller receives either an archive stream or content-store blobs. Descriptor annotations may be mutated to expose response fields.

Dependencies and integration: integrates containerd archive exporter, BuildKit image writer, cache remotes, compression config, session/filesync/content, progress reporting, and gRPC error handling for `AlreadyExists`.

Risks and test signals: risks include Docker manifest-list incompatibility, lease cleanup on error, name parsing failures, lazy remote materialization failures, and incomplete stream close handling. Existing image exporter integration tests and normalized name behavior cover this surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/oci/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export.go -->
# sources/cloud-native/buildkit/exporter/tar/export.go

Purpose: implements the `tar` exporter, reusing local export filesystem construction and sending the resulting filesystem as a tar stream to the client.

Important APIs and functions: `Opt` carries `session.Manager`; `New` and `Resolve` create `localExporterInstance`; `Export` orchestrates `local.CreateFS`, platform subdirectory assembly, session lookup, writer creation, and `writeTar`.

Control flow: options are parsed with `local.CreateFSOpts.Load`. Export resolves epoch from source metadata when needed, validates multi-ref platform mapping, builds per-platform `fsutil.Dir` entries, wraps multi-platform map exports with `fsutil.SubDirFS`, then obtains a filesync writer and streams a tar archive. Cleanup functions are stored and invoked in reverse order.

State and persistence: no server-side durable state; mounted refs and temp dirs are released by deferred cleanup. Output persists only as the client-received tar stream.

Dependencies and integration: depends on `exporter/local` for filesystem and attestation preparation, `exptypes` for platform mapping, session/filesync for transport, and platform-specific `writeTar` implementations.

Risks and test signals: risks include missing platform mappings, cleanup order, `CopyFileWriter`/tar close errors, and platform-split differences from local exporter delete/copy modes. It shares most behavior with local exporter tests and platform-specific tar tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export_unix.go -->
# sources/cloud-native/buildkit/exporter/tar/export_unix.go

Purpose: provides the non-Windows tar writer implementation.

Important API: `writeTar(ctx, fs, w)` is the abstraction called by `tar/export.go`.

Control flow: directly delegates to `fsutil.WriteTar`, passing through the context, filesystem, and write closer.

State and persistence: no state beyond bytes written to the caller-provided stream.

Dependencies and integration: selected by `//go:build !windows` and shares a signature with the Windows privileged variant.

Risks and test signals: risks are limited to archive traversal/write failures from `fsutil.WriteTar`. Unix tar exporter integration is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export_windows.go -->
# sources/cloud-native/buildkit/exporter/tar/export_windows.go

Purpose: provides the Windows tar writer implementation, allowing tar export of special Windows rootfs metadata files.

Important API: `writeTar(ctx, fs, w)` wraps `fsutil.WriteTar` in `winio.RunWithPrivileges`.

Control flow: enables `SeBackupPrivilege` for the duration of archive writing so privileged metadata files can be read.

State and persistence: no persistent state; privilege scope is bound to the callback.

Dependencies and integration: selected on Windows and used transparently by `tar/export.go`.

Risks and test signals: behavior depends on Windows privilege availability. Regressions surface in Windows tar exporter tests and builds involving Windows container layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/tar/export_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/util/epoch/parse.go -->
# sources/cloud-native/buildkit/exporter/util/epoch/parse.go

Purpose: centralizes parsing of `SOURCE_DATE_EPOCH` values for exporters and frontend forwarding.

Important APIs: `Epoch` wraps `*time.Time`; `ParseBuildArgs` detects numeric frontend build args that should be forwarded; `ParseExporterAttrs` consumes exporter `source-date-epoch`; `ParseSource` reads source metadata globally or per-platform; `parseTime` parses Unix seconds.

Control flow: empty values intentionally parse to nil without error, enabling explicit clearing/override semantics. Build args are forwarded only when syntactically numeric. Exporter attrs are split into epoch and rest map. Source metadata checks per-platform keys before global keys and wraps frontend-origin errors with context.

State and persistence: no persistence; returned time values are UTC and later used to normalize filesystem mtimes or image created annotations.

Dependencies and integration: used by local, tar, and container image exporter option flows, and by frontend metadata handoff through exporter metadata keys.

Risks and test signals: risks include accepting empty values as nil, parse errors for non-numeric frontend metadata, and precedence between per-platform and global epochs. `parse_test.go` covers build-arg forwarding semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/util/epoch/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/util/epoch/parse_test.go -->
# sources/cloud-native/buildkit/exporter/util/epoch/parse_test.go

Purpose: unit-tests `ParseBuildArgs` behavior for frontend build-arg forwarding of `SOURCE_DATE_EPOCH`.

Important test cases: numeric strings are accepted and returned; symbolic value `context` is rejected from exporter forwarding; empty string is accepted as a valid exporter override.

Control flow and state: the test is table-like but explicit, runs in parallel, and calls only pure parser logic with in-memory maps.

Dependencies and integration: validates the contract between the Dockerfile frontend, which may support symbolic `SOURCE_DATE_EPOCH` sources, and exporters, which should only receive numeric or empty values.

Risks and test signals: protects against accidentally forwarding symbolic frontend-only values into exporter parsers, and against breaking empty override behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/util/epoch/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/verifier/opts.go -->
# sources/cloud-native/buildkit/exporter/verifier/opts.go

Purpose: captures frontend request options into solver result metadata so exporter verification can compare requested platforms/labels/request id against produced results.

Important APIs: `RequestOpts` stores `Platforms`, `Labels`, and `Request`; `CaptureFrontendOpts` serializes request options under `verifier.requestopts`; `getRequestOpts` deserializes them.

Control flow: platform request defaults to the normalized default platform when not provided. Label options are extracted from `label:` prefixed keys. Request id is copied from `requestid`. JSON is stored in `result.Result` metadata.

State and persistence: metadata persists with the in-memory solver result and is later consumed by verifier code; no disk state.

Dependencies and integration: used with `solver/result`, containerd `platforms`, and `platforms.go` verification.

Risks and test signals: malformed metadata JSON can abort verification; default platform assumptions affect warning behavior for single-platform builds. Coverage is mainly through exporter verifier integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/verifier/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/verifier/platforms.go -->
# sources/cloud-native/buildkit/exporter/verifier/platforms.go

Purpose: validates that the platforms requested by the frontend match the platforms actually represented in an export result, returning BuildKit vertex warnings rather than mutating results.

Important APIs: `CheckInvalidPlatforms` is the verifier entry point; `platformsString` formats deterministic sorted platform lists.

Control flow: request options are loaded from result metadata. A result with multiple refs must have platform metadata; empty results are ignored. Requested platforms are parsed, normalized, and checked for invalid or duplicate entries. Single requested/single produced platform gets special OSVersion tolerance. Multi-platform mismatches compare normalized sets and warn on cardinality or value differences; multiple requested platforms with a non-map result warn separately.

State and persistence: no mutation except local warning construction.

Dependencies and integration: depends on `exptypes.ParsePlatforms`, `client.VertexWarning`, and request metadata from `opts.go`.

Risks and test signals: risks include nil request metadata assumptions, OSVersion comparison edge cases, and warnings after invalid parse still appending a zero platform. Exporter/platform integration tests should exercise this.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/exporter/verifier/platforms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/parse.go -->
# sources/cloud-native/buildkit/frontend/attestations/parse.go

Purpose: parses frontend attestation options from `attest:` keys and legacy `build-arg:BUILDKIT_ATTEST_` keys into typed attribute maps.

Important APIs: constants define supported types `sbom` and `provenance`; `Filter` extracts attestation-related options; `Validate` rejects unknown types; `Parse` lowercases type names, applies defaults, parses CSV-style key/value attributes, and validates output.

Control flow: each attestation value is parsed as CSV fields so commas can be escaped/quoted. Fields without `=` become empty-valued attributes. SBOM defaults `generator` to BuildKit Syft scanner; provenance defaults `version` to SLSA v1. Unknown attestation type errors early.

State and persistence: no persistence; parsed maps are consumed by dockerui/build frontend configuration.

Dependencies and integration: integrates provenance type constants and `go-csvvalue` for robust attribute parsing.

Risks and test signals: risks include duplicate attribute overwrite, unknown type rejection, and lowercasing type names while preserving attribute keys. `parse_test.go` covers simple and quoted-comma forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/parse_test.go -->
# sources/cloud-native/buildkit/frontend/attestations/parse_test.go

Purpose: tests attestation option parsing.

Important test cases: simple SBOM/provenance parsing with default provenance version, extra SBOM parameters, and quoted CSV fields containing commas.

Control flow and state: table-driven subtests call `Parse`, require no error, and compare complete nested maps.

Dependencies and integration: uses `testify` assertions and intentionally compares provenance default version as literal `v1` to catch contract drift.

Risks and test signals: protects CSV parsing and default injection. It does not cover unknown type errors, legacy build-arg key parsing, or duplicate attributes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/sbom/sbom.go -->
# sources/cloud-native/buildkit/frontend/attestations/sbom/sbom.go

Purpose: builds a reusable SBOM scanner closure that runs a scanner image against an LLB state and returns a BuildKit attestation.

Important APIs: `Scanner` function type; `CreateSBOMScanner` resolves scanner image config and returns a closure; `HasSBOM` checks result attestations for SPDX predicate type. Constants define core and extra mount names plus source/output directories.

Control flow: the scanner image is resolved, entrypoint and cmd are combined, and empty command is rejected. The returned closure builds scanner environment, includes scanner params as `BUILDKIT_SCAN_*`, mounts the core target and optional extra states read-only, runs scanner image with `/tmp` tmpfs, and returns a bundle attestation pointing at `/run/out/`.

State and persistence: scan output exists as an LLB state until solved; attestation metadata identifies SBOM reason and core name. No local persistence.

Dependencies and integration: integrates sourceresolver, LLB image/run/mount primitives, gateway attestation kinds, in-toto SPDX predicate type, and builder SBOM flow.

Risks and test signals: risks include scanner image config lacking command, environment key collisions, missing scanner policy enforcement, and extra mount naming. Coverage is mostly integration through Dockerfile builder SBOM paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/attestations/sbom/sbom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/build.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/builder/build.go

Purpose: gateway frontend entry point for Dockerfile builds. It reads Dockerfile input, optionally forwards to another syntax frontend, handles subrequests, converts Dockerfile to LLB per platform, solves it, attaches SBOM attestations, and finalizes `dockerui` build results.

Important APIs: `Build(ctx, c)` is invoked by the frontend binary; `forwardGateway` invokes gateway frontend forwarding; `warnOpts` maps parser ranges to gateway warnings; `wrapSource` attaches source maps to errors.

Control flow: wraps the gateway client in `withResolveCache`, loads dockerui config, validates frontend caps, reads the Dockerfile, and honors syntax directives or `BUILDKIT_SYNTAX` by forwarding unless already in forwarded mode. Subrequests delegate to outline, target list, lint, or convertllb handlers. Normal build prepares `dockerfile2llb.ConvertOpt`, creates optional SBOM scanner, and calls `bc.Build` for each platform. Each platform converts Dockerfile, marshals and solves LLB, records scan targets, then `rb.Finalize` returns the result. SBOM scanning solves scanner states and attaches attestations per platform.

State and persistence: per-platform `scanTargets` map tracks conversion results. Build result refs and attestations persist in gateway result objects, not disk.

Dependencies and integration: central integration point for dockerui, dockerfile2llb, linter warnings, gateway client, platform handling, SBOM scanner, errdefs source mapping, and solver results.

Risks and test signals: risks include forwarding cap handling, source-location wrapping, stale resolve cache errors, multi-platform warning suppression after first platform, SBOM target mismatch, and subrequest behavior. Integration tests across Dockerfile frontend cover this file heavily.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/caps.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/builder/caps.go

Purpose: validates requested Dockerfile frontend capabilities and decides whether unsupported caps should allow syntax forwarding.

Important APIs: `enabledCaps` lists supported capability strings; `validateCaps(req)` returns `(forward bool, err error)`.

Control flow: comma-separated requested capabilities are split, optional `+forward` suffix is recognized, and unsupported caps produce an unsupported frontend cap error wrapped as gRPC `Unimplemented`. If unsupported with `+forward`, the function records that forwarding is allowed and continues; otherwise it returns immediately.

State and persistence: no state beyond the static capability map.

Dependencies and integration: used early by `Build` before syntax forwarding. Depends on BuildKit errdefs, grpc error wrappers, stack enabling, and gRPC codes.

Risks and test signals: risks include capability list drift with Dockerfile image labels/docs and parsing whitespace. Build forwarding integration tests are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/resolvecache.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/builder/resolvecache.go

Purpose: caches and deduplicates image config resolution calls made through the gateway client during Dockerfile build conversion.

Important APIs: `withResolveCache` embeds `client.Client`; `ResolveImageConfig` hashes `sourceresolver.Opt`, keys by `ref,optHash`, and uses `flightcontrol.CachedGroup`; `resolveResult` stores mutable ref, digest, and config bytes.

Control flow: every call enables `CacheError`, hashes the resolver option structurally, runs or joins the cached flight, delegates to the embedded client on cache miss, and returns stored values.

State and persistence: in-memory cached group state lives for the wrapper lifetime. Errors are cached intentionally, which can avoid duplicate failing resolver requests but may preserve transient failures inside one build.

Dependencies and integration: wraps the gateway client in `Build`; uses `hashstructure/v2`, BuildKit sourceresolver, flightcontrol, and OCI digest.

Risks and test signals: risks include hash instability for new option fields, cached transient errors, and memory growth in long-lived clients. Integration signal is reduced duplicate metadata loads and consistent behavior across repeated base image references.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/builder/resolvecache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/Dockerfile -->
# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/Dockerfile

Purpose: defines the container build for the external Dockerfile frontend binary.

Important stages: `xx` supplies cross-compilation helper tools; `base` installs Go, git, bash, and vendored module mode; `version` validates release tags and writes ldflags/build tags; `build` compiles a static `dockerfile-frontend`; `release` packages the binary in scratch with capability labels and network-none label.

Control flow: version stage reads release channel tag file, compares exact Dockerfile tag against built-in frontend version, records git revision including dirty suffix, and writes `/tmp/.ldflags` and `/tmp/.buildtags`. Build stage uses `xx-go build` with static/netgo/osusergo tags and verifies the binary. Release stage copies binary and sets entrypoint.

State and persistence: only image layers and temporary build artifacts inside stages. Build labels persist in the final frontend image and influence BuildKit capability negotiation.

Dependencies and integration: integrates Dockerfile frontend release metadata, tonistiigi/xx, Go toolchain, and BuildKit frontend labels.

Risks and test signals: risks include release tag/version mismatch, channel tag file drift, cross-compilation failures, static verification failures, and capability label drift with `caps.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/main.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/main.go

Purpose: executable entry point for the external Dockerfile frontend.

Important APIs: `init` sets stack version info from linked variables; `main` handles `-version` and otherwise runs `dockerfile.Build` via `grpcclient.RunFromEnvironment`.

Control flow: command-line parsing is minimal. Version mode prints binary name, package, version, and revision then exits. Normal mode creates an app context, runs gateway gRPC environment plumbing, logs fatal error, and panics on failure.

State and persistence: no durable state. Version variables come from `version.go` defaults or Dockerfile ldflags.

Dependencies and integration: connects the packaged frontend binary to the builder package and BuildKit gateway gRPC protocol. Imports proto encoding for registration.

Risks and test signals: risks include panic-style fatal path and stale version ldflags. Smoke tests of external frontend image and `-version` output cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/version.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/version.go

Purpose: holds link-time-overridden metadata for the Dockerfile frontend binary.

Important variables: `Package`, `Version`, and `Revision` default to package path, `0.0.0+unknown`, and empty revision.

Control flow and state: no functions; values are read by `main.go` and `stack.SetVersionInfo`. The packaging Dockerfile overrides them through `-ldflags`.

Dependencies and integration: tied to release Dockerfile version stage and CLI `-version` output.

Risks and test signals: if ldflags are missing, published frontend binaries report unknown metadata. Release build checks and version smoke tests are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/command/command.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/command/command.go

Purpose: enumerates Dockerfile command keywords in one package.

Important APIs: constants for `add`, `arg`, `cmd`, `copy`, `entrypoint`, `env`, `expose`, `from`, `healthcheck`, `label`, `maintainer`, `onbuild`, `run`, `shell`, `stopsignal`, `user`, `volume`, and `workdir`; `Commands` set contains all supported keys.

Control flow and state: static declarations only; no runtime behavior.

Dependencies and integration: consumed by parser/instruction or validation code elsewhere as the canonical command set.

Risks and test signals: risk is drift when adding Dockerfile instructions or labs-only features. Parser tests and command recognition tests provide signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/command/command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref.go

Purpose: parses Dockerfile-specific Git references used by ADD and Git build contexts, including fragment syntax and query-string options.

Important APIs and types: `GitRef` captures remote, short name, ref, checksum, subdir, flags for local-ambiguous and unencrypted refs, keep-git-dir, submodules, mtime, and fetch-by-commit. `ParseGitRef` parses and validates URLs. `loadQuery` applies query parameters. `FragmentFormat` converts query-form refs to fragment-form display.

Control flow: local `./` and `../` refs are invalid. `github.com/...` legacy refs are accepted as ambiguous local-like refs. HTTP(S) refs must end in `.git`; git/http mark unencrypted TCP. Query processing rejects missing values except boolean flags, rejects duplicate values, normalizes `tag` to `refs/tags/` and `branch` to `refs/heads/`, detects ref/subdir conflicts, parses booleans, and limits mtime values to `checkout` or `commit`.

State and persistence: pure parsing; returned flags control later LLB Git source options.

Dependencies and integration: used by ADD/COPY detection and `SOURCE_DATE_EPOCH` source resolution. Relies on BuildKit `gitutil` and containerd errdefs.

Risks and test signals: risks include ambiguous local refs, query conflict handling, boolean valueless handling, and security warnings not yet emitted for unencrypted TCP. `git_ref_test.go` has extensive coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref_test.go

Purpose: validates Dockerfile Git URL parsing and fragment formatting.

Important test cases: HTTP(S) `.git` enforcement, legacy `github.com/` ambiguity, SSH-style refs, fragment ref/subdir parsing, query `ref`, `tag`, `branch`, `subdir`, `checksum`/`commit`, `keep-git-dir`, `submodules`, `mtime`, and `fetch-by-commit`, plus conflict and invalid parameter errors.

Control flow and state: table-driven tests call `ParseGitRef` and compare full `GitRef` structs or expected error substrings. Separate tests call `FragmentFormat` with and without subdir.

Dependencies and integration: guards behavior consumed by Dockerfile ADD Git and Git build context integration tests.

Risks and test signals: strong regression coverage for parser rules; does not execute remote Git resolution, which is covered by `dockerfile_addgit_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dfgitutil/git_ref_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile.go

Purpose: declares the `dockerfile` package at the frontend root.

Important APIs: none; the file only contains `package dockerfile`.

Control flow, state, and dependencies: no executable behavior or imports.

Integration: serves as a package anchor for sibling Dockerfile frontend integration tests that use `package dockerfile`.

Risks and test signals: no direct runtime risk. Removing it could affect package layout when only test files exist in the directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert.go

Purpose: core Dockerfile-to-LLB converter. It parses Dockerfile syntax, resolves stages, platforms, build args, base images, dependencies, lints, dispatches instructions into LLB/image config mutations, tracks context path usage, and returns build, outline, lint, target-list, or convert-LLB results.

Important APIs and types: `ConvertOpt`, `Result`, `SBOMTargets`, `Dockerfile2LLB`, `Dockerfile2Outline`, `DockerfileConvertLLB`, `DockerfileLint`, `ListTargets`, `dispatchContext`, `dispatchState`, `dispatchStates`, `command`, and many `dispatch*` helpers for Dockerfile instructions. Utility functions handle env mutation, history, platform labels, context path filters, proxy env, source locations, ARG meta processing, and command names.

Control flow: `toDispatchState` validates input, initializes linter and caps, parses stages/ARGs, builds platform defaults, validates base image defaults, resolves `SOURCE_DATE_EPOCH`, builds dispatch states, resolves target and dependency graph, resolves reachable base images concurrently, initializes ONBUILD triggers, dispatches reachable stages, and finalizes image/state metadata. Instruction dispatch expands variables, reports lint warnings, and routes to specialized handlers for RUN, COPY/ADD, metadata instructions, ARG, and platform-related behavior.

State and persistence: converter state is in-memory in `dispatchState`: LLB state, Docker OCI image config/history, base image snapshot, context paths, stage dependencies, outline data, no-cache flags, command counters, epoch, and SBOM scan flags. Result persistence happens when the builder solves returned LLB.

Dependencies and integration: integrates parser/instructions, linter, dockerui config/client, image metadata resolver, containerd platforms/reference, BuildKit LLB, solver caps, source maps, and helper files in this package.

Risks and test signals: high-risk areas include stage dependency cycles, ARG/platform expansion, path filtering, ONBUILD dependency injection, implicit target platform detection, COPY from unregistered states, no-cache propagation, and image config mutation aliasing. `convert_test.go`, platform/image/expose tests, and many frontend integration tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_copy.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_copy.go

Purpose: implements ADD and COPY dispatch into LLB file operations, including local context copies, stage copies, remote HTTP ADD, Git ADD, heredoc source contents, checksums, chmod/chown, exclude patterns, parents mode, link mode, and unpack behavior.

Important APIs: `copyConfig` carries instruction-specific settings; `dispatchCopy` performs conversion; `isHTTPSource`, `isGitSource`, and `containsWildcards` classify sources.

Control flow: destination is normalized relative to workdir. Copy options are assembled for chown, chmod, and exclude patterns. Chmod accepts octal up to `07777` or symbolic modes via `dchapes-mode`. Checksums are restricted to ADD with exactly one HTTP(S) or Git source. Each source is handled as Git, HTTP, local path, or inline content. Git sources map query/flags to `llb.GitOption`; HTTP sources use `llb.HTTP` with optional digest and no default unpack; local copies normalize source paths, validate `.dockerignore` warnings, and configure wildcard/required path behavior. Link mode can use merge op when caps permit.

State and persistence: mutates `dispatchState.state` and image history. Context path usage is recorded by caller in `convert.go`.

Dependencies and integration: uses `dfgitutil`, Dockerfile instructions, LLB copy/http/git, system path helpers, pattern matcher, identity progress groups, and solver caps.

Risks and test signals: risks include checksum/ref conflict handling, COPY accidentally accepting remote refs, Windows path normalization, symbolic chmod compatibility, link-mode command indexing, and wildcard required paths. Covered by ADD checksum/Git/chmod integration tests and exclude pattern tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose.go

Purpose: converts Dockerfile `EXPOSE` instructions into image `ExposedPorts` metadata with validation and linting for protocol casing and unsupported host/IP formats.

Important APIs: `dispatchExpose`, `portSpecs`, options `withLocation`/`withLint`, and methods `parsePorts`, `parsePort`, `parsePortRange`, `parsePortNumber`, `splitProtoPort`, `splitParts`.

Control flow: variables are expanded into port words, parsed specs may include legacy `[ip:]host:container/proto` forms, protocol defaults to tcp and accepts tcp/udp/sctp, port ranges expand into individual `port/proto` strings, IPv6 forms are handled, and image config map is initialized/filled. Lints warn on non-lowercase protocol and host/IP/host-port format even while preserving legacy parsing.

State and persistence: mutates only image config and history; no filesystem layer.

Dependencies and integration: used by `dispatch` in `convert.go`; relies on shell env expansion, linter, parser ranges, and Go `net` parsing.

Risks and test signals: risks include IPv6 colon splitting, range mismatch semantics, allowing host mappings for backward compatibility, and out-of-range diagnostics. `convert_expose_test.go` covers empty ports, full forms, IPv6, protocol variants, and ranges.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose_test.go

Purpose: unit-tests EXPOSE port parsing.

Important test cases: empty spec errors, full IP/host/container ranges, bracketed and unbracketed IPv6 forms, tcp/udp/sctp protocols, host mapping forms, invalid hostname-as-IP, and multi-port range expansion.

Control flow and state: tests use package-level `ps := newPortSpecs()` and call parser methods directly; no LLB or image state is solved.

Dependencies and integration: validates helper behavior used by `dispatchExpose`.

Risks and test signals: strong parser coverage; lint warning behavior and image config mutation are not directly asserted here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_expose_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_norundevice.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_norundevice.go

Purpose: default build-tag implementation for Dockerfile RUN device support when labs device feature is not enabled.

Important API: `dispatchRunDevices(c)` returns an error if the parsed RUN command contains devices.

Control flow: selected by `//go:build !dfrundevice`. It checks `instructions.GetDevices(c)` and rejects any device usage with a message requiring Dockerfile frontend 1.14.0-labs or later.

State and persistence: none.

Dependencies and integration: called from `dispatchRun` only when LLB CDI cap support is available. Paired with `convert_rundevice.go`.

Risks and test signals: risk is build-tag/configuration mismatch where device syntax parses but should be unavailable. Labs frontend tests cover the positive variant.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_norundevice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_rundevice.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_rundevice.go

Purpose: labs build-tag implementation for Dockerfile RUN CDI device mounts.

Important API: `dispatchRunDevices(c)` converts parsed device specs into `llb.AddCDIDevice` run options.

Control flow: selected by `//go:build dfrundevice`. For each device, it sets `llb.CDIDeviceName` and appends `llb.CDIDeviceOptional` when not required.

State and persistence: no persistent state; options affect the LLB exec op.

Dependencies and integration: called from `dispatchRun` and depends on instruction parser support plus LLB CDI support.

Risks and test signals: risks include feature-gate drift and optional/required inversion. Device integration tests under labs builds are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_rundevice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runmount.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runmount.go

Purpose: converts `RUN --mount` options into LLB run mount options and records mount source dependencies/paths.

Important APIs: `detectRunMount` records dependency states for mounts; `setCacheUIDGID` prepares cache mount ownership/mode; `dispatchRunMounts` returns `[]llb.RunOption`.

Control flow: mount sources are resolved to existing stages or unregistered external sources; cache mounts without `from` use scratch/empty image source. Tmpfs, secret, and SSH mounts dispatch to special handlers. Bind mounts can be readonly or forced no-output for rw bind without cap support. Cache mounts map sharing mode and persistent cache ID with namespace. Relative targets are resolved under current workdir; `/` target is rejected. Source paths are recorded against build context or source stage for path filtering.

State and persistence: persistent cache mounts use `AsPersistentCacheDir`; stage/context path maps mutate `dispatchState` for later local filtering. Secret/SSH outline state is mutated by sub-handlers.

Dependencies and integration: used by RUN dispatch; integrates Dockerfile mount parser, LLB mount options, solver caps, system path helpers, and secret/SSH handlers.

Risks and test signals: risks include dependency ordering, relative target resolution, source path accounting, cache permission setup, and cap-dependent bind behavior. RUN mount integration tests cover this surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runnetwork.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runnetwork.go

Purpose: converts Dockerfile `RUN --network` mode into an LLB run option.

Important API: `dispatchRunNetwork(c)` maps parsed network mode to `llb.Network`.

Control flow: default mode returns nil, `none` maps to `pb.NetMode_NONE`, `host` maps to `pb.NetMode_HOST`, and unknown modes error.

State and persistence: none; network mode is encoded in the exec op.

Dependencies and integration: called by `dispatchRun`; depends on instruction parser and solver `pb` net modes.

Risks and test signals: risk is parser/dispatcher mode drift. RUN network frontend tests cover supported and unsupported modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runnetwork.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runsecurity.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runsecurity.go

Purpose: converts Dockerfile `RUN --security` mode into an LLB run option.

Important API: `dispatchRunSecurity(c)` maps insecure/sandbox modes to solver security enums.

Control flow: insecure returns `llb.Security(pb.SecurityMode_INSECURE)`, sandbox returns `llb.Security(pb.SecurityMode_SANDBOX)`, and unknown modes error.

State and persistence: none; security mode is stored in the exec op.

Dependencies and integration: called by `dispatchRun`; depends on instruction parser and solver `pb` security modes.

Risks and test signals: risk is feature-gating/security entitlement mismatch outside this function. RUN security integration tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_runsecurity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_secrets.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_secrets.go

Purpose: converts secret mounts for RUN and masks secret environment values in progress command names.

Important APIs: `dispatchSecret`, `withSecretEnvMask`, and `secretEnv` implementing `shell.EnvGetter`.

Control flow: secret id comes from cache ID, source, target basename, or errors if none exists. Target is derived from mount target or `/run/secrets/<id>` unless mounted as env. Outline metadata records id, location, and required flag. LLB secret options include ID, optional flag, env name, and file uid/gid/mode with default `0400` when metadata is specified. `withSecretEnvMask` overlays env-mounted secrets with `****` for command rendering.

State and persistence: records outline secret metadata on `dispatchState`; secret contents are never persisted in Dockerfile conversion.

Dependencies and integration: used by `dispatchRunMounts` and `dispatchRun` command name formatting; integrates LLB secret options and parser ranges.

Risks and test signals: risks include id derivation surprises, target/env interactions, required flag accuracy, and accidentally exposing secret values in custom names. Secret mount tests and outline tests cover this.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_ssh.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_ssh.go

Purpose: converts SSH mounts for RUN into LLB SSH socket options and records outline metadata.

Important API: `dispatchSSH(d, m, loc)` returns `llb.AddSSHSocket(...)`.

Control flow: SSH mounts reject `source`. ID defaults to `default` for outline, while options use `m.CacheID`. Target, optional flag, and socket uid/gid/mode are appended when configured; default mode is `0600` if any file metadata is set.

State and persistence: records SSH id, required flag, and location in `dispatchState.outline.ssh`. No secret material is persisted.

Dependencies and integration: called by RUN mount dispatch and represented in outline subrequests.

Risks and test signals: possible risk is the option ID using `m.CacheID` instead of the local defaulted `id`; empty id likely means default to LLB, but this contract matters. SSH mount and outline tests are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_test.go

Purpose: unit-tests core Dockerfile conversion helpers and selected end-to-end conversion paths without running full BuildKit integration.

Important test coverage: simple parsing, stage target case-insensitivity, missing targets, ADD URL vs COPY URL, blank FROM errors, LLB marshaling, preserving base labels across sibling stage copy, env helpers, proxy env deterministic order, circular dependencies, base image config immutability, healthcheck history formatting, numeric and symbolic `SOURCE_DATE_EPOCH`, valid/invalid source epoch stages, extracting source ops from wrapped copy states, and rewriting source states.

Control flow and state: tests call `Dockerfile2LLB` for in-memory Dockerfiles and lower-level helpers directly. Some tests resolve real image metadata for busybox base image config, so they are more integration-like.

Dependencies and integration: validates interactions across parser, dispatch, image metadata, epoch helper, LLB marshal, and linter-adjacent behavior.

Risks and test signals: strong signals for dependency cycles, mutation aliasing, proxy reproducibility, and epoch behavior. Does not cover every instruction, so integration tests complete coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convertllb.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convertllb.go

Purpose: implements the Dockerfile frontend `convertllb` subrequest by serializing a dispatch state's LLB graph into digest-addressed protobuf ops.

Important API: `(*dispatchState).ConvertLLB(ctx)` returns `*convertllb.Result`.

Control flow: marshals `ds.state`, initializes result maps and metadata/source fields, unmarshals each definition byte slice into `pb.Op`, computes its digest from bytes, and stores op by digest.

State and persistence: reads final dispatch state only; result is returned through gateway subrequest response.

Dependencies and integration: used by `DockerfileConvertLLB` in `convert.go` and by builder subrequest handling.

Risks and test signals: risks include marshal failures and protobuf unmarshal incompatibility. Subrequest tests and clients inspecting LLB output provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convertllb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/defaultshell.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/defaultshell.go

Purpose: returns the default shell used for shell-form RUN/CMD/ENTRYPOINT when the image config does not define one.

Important API: `defaultShell(os string) []string`.

Control flow: Windows returns `cmd /S /C`; all other OS values return `/bin/sh -c`.

State and persistence: none.

Dependencies and integration: called by `withShell` in `convert.go`, which influences command args and image config history.

Risks and test signals: risk is platform-specific shell behavior drift, especially Windows escaping. Covered by Dockerfile command integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/defaultshell.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/epoch.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/epoch.go

Purpose: resolves Dockerfile `SOURCE_DATE_EPOCH` values into timestamps, including numeric values, main/named contexts, or a restricted source-only stage that points at an HTTP/Git remote.

Important APIs: `resolveSourceDateEpochValue`, `formatSourceDateEpochValue`, `resolveSourceDateEpochState`, `sourceDateEpochStageSource`, `applySourceDateEpochStageArgs`, `sourceDateEpochAddSource`, `resolveSourceDateEpochFromState`, `sourceOpFromState`, `sourceDateEpochFromMetadata`, and `archiveMaxTimeFromRef`.

Control flow: numeric values become UTC Unix seconds. `context` loads main context; named contexts are checked through dockerui; stage names must resolve to `FROM scratch` stages containing only ARG and exactly one remote ADD. Remote ADD sources become HTTP or Git LLB sources with checksum/subdir/submodule flags. Metadata resolution prefers Git commit object committer time or HTTP Last-Modified. For HTTP archives without metadata, it solves and scans archive members for max mtime.

State and persistence: no durable state; resolved epoch is stored in `dispatchState` and build args, then exported as metadata/history timestamps.

Dependencies and integration: bridges Dockerfile conversion, dockerui gateway client, sourceresolver metadata, git object parsing, archive decompression, and source op protobuf extraction.

Risks and test signals: risks include ambiguous states with multiple source ops, archive decompression fallback, symbolic value behavior without client, stage restriction enforcement, and Git checksum parity. `convert_test.go` covers numeric/context/stage/source-op paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/epoch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/exclude_patterns_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/exclude_patterns_test.go

Purpose: verifies parser/converter acceptance of `--exclude` patterns for COPY and ADD.

Important tests: `TestDockerfileCopyExcludePatterns` and `TestDockerfileAddExcludePatterns` call `Dockerfile2LLB` on scratch Dockerfiles with two exclude patterns.

Control flow and state: tests only assert no conversion error; they do not solve the LLB or inspect filtered copy options.

Dependencies and integration: covers `convert_copy.go` option plumbing from parsed instruction fields to conversion.

Risks and test signals: minimal smoke coverage; deeper behavior requires integration tests that verify copied files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/exclude_patterns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image.go

Purpose: provides image config helpers for safe mutation during stage inheritance and scratch image initialization.

Important APIs: `clone`, `cloneX`, and `emptyImage`.

Control flow: `clone` shallow-copies the OCI image then deep-copies mutable slices/maps in Docker image config, healthcheck test slice, shell/onbuild, exposed ports, volumes, labels, and history. `cloneX` handles nil pointers. `emptyImage` initializes platform fields, rootfs type, working dir, and non-Windows PATH.

State and persistence: prevents child stages mutating base stage image metadata by aliasing shared maps/slices.

Dependencies and integration: used when resolving base stages and scratch images in `convert.go`; uses system default PATH.

Risks and test signals: omissions in deep copy can leak metadata mutations across stages. `image_test.go` specifically guards mutable field isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image_test.go

Purpose: verifies that `clone` deep-copies mutable image config fields.

Important test coverage: exposed ports, env, cmd, entrypoint, volumes, labels, onbuild, shell, healthcheck test slice, and history are mutated in the clone and asserted unchanged in the source.

Control flow and state: constructs an in-memory `DockerOCIImage`, clones it, mutates nested values, and asserts original values.

Dependencies and integration: protects stage inheritance semantics in `convert.go`.

Risks and test signals: strong signal for currently known mutable fields. Future image config fields need test updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/outline.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/outline.go

Purpose: captures and renders outline subrequest information: build args, secrets, SSH mounts, target name/description, source bytes, and source locations.

Important APIs and types: `outlineCapture`, `argInfo`, `secretInfo`, `sshInfo`, `newOutlineCapture`, `clone`, `markAllUsed`, dispatch-state methods `args`, `secrets`, `ssh`, `Outline`, plus location helpers.

Control flow: captures are cloned per stage to inherit global ARG knowledge. Used args recursively mark dependencies. Rendering walks current stage, base stages, and dependency stages, deduplicates by visited maps, sorts by source location, and emits `outline.Outline`.

State and persistence: outline data is in-memory during conversion and returned through subrequest response.

Dependencies and integration: populated by ARG dispatch, secret/SSH mount dispatch, and `Dockerfile2Outline`; maps parser ranges to solver protobuf locations.

Risks and test signals: risks include missing dependency args, nil location comparison assumptions, duplicate suppression hiding redefinitions, and SSH slice preallocation typo using secrets length. Outline subrequest tests are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/outline.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform.go

Purpose: computes build/target platform defaults and injects automatic platform build args.

Important APIs: `platformOpt`, `buildPlatformOpt`, and `defaultArgs`.

Control flow: if target is set but build platforms are absent, build platforms default to the target. If build platforms are absent entirely, default spec is used. If target is absent, target becomes the first build platform and `implicitTarget` is true. `defaultArgs` creates `BUILD*`, `TARGET*`, and `TARGETSTAGE` env entries, applying build arg overrides.

State and persistence: platform opt is in-memory conversion state; default args feed ARG expansion and stage platform resolution.

Dependencies and integration: used early in `convert.go`; depends on containerd platform formatting and LLB env lists.

Risks and test signals: risks include implicit platform behavior, overrides producing inconsistent auto args, and OSVersion/variant formatting. `platform_test.go` covers selection rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform_test.go

Purpose: unit-tests platform option resolution.

Important tests: `TestResolveBuildPlatforms`, `TestResolveTargetPlatform`, and `TestImplicitTargetPlatform`.

Control flow and state: constructs `ConvertOpt` combinations with/without `TargetPlatform` and `BuildPlatforms`, then asserts derived build platforms, target platform, and implicit target flag.

Dependencies and integration: protects platform defaults used by Dockerfile stage resolution and automatic build args.

Risks and test signals: covers selection logic but not `defaultArgs` values or platform auto-detection from base image config.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/validations.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/validations.go

Purpose: houses Dockerfile conversion validation and lint helpers for copy ignored files, dependency cycles, instruction casing, stage names, undefined variables/args, platform rules, duplicate singleton instructions, base image platform mismatch, and secret-looking ARG/ENV keys.

Important APIs: `validateCopySourcePath`, `validateCircularDependency`, `validateCommandCasing`, `validateStageNames`, `reportUnmatchedVariables`, `reportUnusedFromArgs`, `reportRedundantTargetPlatform`, `reportConstPlatformDisallowed`, `validateUsedOnce`, `validateBaseImagePlatform`, `validateNoSecretKey`, and `validateBaseImagesWithDefaultArgs`.

Control flow: validation mostly reports linter warnings rather than hard errors, except circular dependency detection. Dependency cycles use DFS with current path and attach command locations. Copy ignored-file warnings only run when dockerignore has no exclusions. Secret regexes are lazily initialized. Default-ARG base image validation processes ARGs without build overrides to warn about invalid defaults.

State and persistence: no durable state. `instructionTracker` records first CMD/ENTRYPOINT/HEALTHCHECK locations per stage.

Dependencies and integration: called from `convert.go` and `convert_copy.go`; uses linter rule catalog, suggest helper, parser locations, platform/reference parsers, and pattern matcher.

Risks and test signals: risks include false positives for secret names, reserved stage name case sensitivity, cycle path reporting, and dockerignore validation limits. Covered by conversion tests plus broader linter integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/validations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addchecksum_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addchecksum_test.go

Purpose: integration-tests `ADD --checksum` for HTTP sources.

Important test cases: valid digest, digest and URL from env expansion, digest mismatch, unsupported known algorithm, unknown algorithm, missing algorithm, and checksum on local non-HTTP source.

Control flow and state: creates an HTTP test server with deterministic content, builds Dockerfiles through the frontend in an integration sandbox, and expects success or specific errors. Uses scratch/nanoserver base depending on platform.

Dependencies and integration: exercises parser, `convert_copy.go` checksum validation, LLB HTTP source checksum behavior, frontend solve, local mounts, and BuildKit client.

Risks and test signals: strong signal for HTTP checksum contract and error messages. Git checksum behavior is covered separately in ADD Git tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addchecksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addgit_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addgit_test.go

Purpose: integration-tests Dockerfile ADD and build context Git URL behavior, including SHA-1/SHA-256 repos, query-string syntax, checksums, subdirs, submodules, keep-git-dir, and cache behavior.

Important tests: `testAddGitSHA1`, `testAddGitSHA256`, shared `testAddGit`, `testAddGitChecksumCache`, and `testGitQueryString`. Helper `applyTemplate` renders Dockerfile templates.

Control flow: tests create local Git repositories, commits/tags/branches/submodules, serve them over HTTP, then run frontend solves with local mounts or Git context URLs. Cases verify file contents, git metadata presence/absence, chown behavior, checksum success/mismatch/invalid errors, cache reuse when checksum is added, query `ref`/`branch`/`tag`/`commit`/`subdir`/`keep-git-dir`/`submodules` behavior for both build context and ADD.

State and persistence: uses temp Git repos, HTTP servers, BuildKit cache, and local exporter output dirs. Windows skips reflect Git source handler limitations.

Dependencies and integration: exercises `dfgitutil`, `convert_copy.go`, Git source resolver, local exporter, frontend attrs, and BuildKit client.

Risks and test signals: very high-value regression coverage for Git semantics and cache keys. Risks include dependency on local git command, HTTP dumb Git serving, platform skips, and exact error text.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_addgit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_chmod_non_octal_test.go -->
# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_chmod_non_octal_test.go

Purpose: integration-tests symbolic, non-octal `COPY --chmod` behavior.

Important test cases: file and directory copies with modes `go-w`, `u=rw,g=r,o=r`, `a+X`, and compound symbolic forms. Windows is skipped.

Control flow and state: builds a Dockerfile that creates base input files/dirs, independently computes expected permissions with shell `chmod`, copies using `COPY --chmod` into a scratch result stage, then compares `stat -c %A` between actual and expected in a final stage.

Dependencies and integration: exercises `convert_copy.go` symbolic mode parsing through `dchapes-mode`, LLB copy chmod handling, multi-stage COPY, and frontend integration sandbox.

Risks and test signals: protects symbolic chmod compatibility and directory execute-bit behavior. It does not cover invalid symbolic expressions; parser/unit tests should cover failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_chmod_non_octal_test.go -->
