# subset-b-000223 Research

Grouped research report for the requested Nydus `nydusify` source subset. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest_test.go

Purpose: tests `ManifestRule`, the checker rule responsible for validating OCI and Nydus image manifest/config consistency. The file focuses on observable rule behavior: rule naming, ignored deprecated OCI config fields, Nydus target layer layout, OCI diff ID checks, and special model-artifact handling.

Important APIs and flow: `TestManifestName` asserts `ManifestRule.Name()` returns `manifest`. `TestManifestRuleValidate_IgnoreDeprecatedField` builds source and target `parser.Parsed` values with differing `ocispec.ImageConfig.ArgsEscaped` and expects `Validate` to ignore that deprecated field. `TestManifestRuleValidate_TargetLayer` mutates a target Nydus manifest through invalid and valid layer arrangements, checking blob media type, bootstrap annotation, bootstrap reference annotations, and diff ID count. `TestManifestRuleValidateOCI` and `TestManifestRuleValidateNydus` call unexported validation helpers from package-local tests.

State and persistence: tests are pure in-memory construction of OCI descriptors and parser models. No filesystem or registry state is used.

Dependencies and integration: uses `parser.Parsed`, `remote.Remote`, `utils` Nydus media/annotation constants, OCI digest/descriptors, and CloudNativeAI model-spec constants. It verifies that model manifests relax standard rootfs layer count validation and require matching Nydus artifact annotations.

Risks and test signals: coverage is strong for layer classification and model-artifact exceptions, but it uses synthetic descriptors and does not exercise parser-produced real manifests or reference blob annotation parsing beyond string presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/rule.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/rule.go

Purpose: defines the minimal checker rule contract used by the `checker/rule` package.

Important APIs and flow: `type Rule interface` requires `Validate() error` and `Name() string`. Implementations such as `ManifestRule` and filesystem rules can be registered or run polymorphically by the checker without exposing implementation-specific fields.

State and persistence: none. This file contains only an interface and has no side effects.

Dependencies and integration: no imports. The integration point is package-level: any validation rule in `nydusify` must return a human-readable name and signal failure with an error.

Risks and test signals: the contract is intentionally narrow, so compatibility risk is low. It does not model context, logging, or severity, so callers must handle cancellation and reporting outside the interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/rule/rule.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder.go

Purpose: wraps the external `nydus-image` binary for checker bootstrap inspection.

Important APIs and flow: `BuilderOption` carries `BootstrapPath` and `DebugOutputPath`. `NewBuilder(binaryPath)` initializes stdout/stderr to process stdout/stderr. `(*Builder).Check` executes `nydus-image check --log-level warn --output-json <debug> --bootstrap <bootstrap>` using `os/exec`, wiring configured output streams and returning the process error.

State and persistence: no internal persistence. External side effects are entirely delegated to `nydus-image`, which reads the bootstrap and writes the JSON debug output path.

Dependencies and integration: used by checker flows that need parsed bootstrap diagnostics. Depends only on `io`, `os`, and `os/exec`, making it easy to test with fake scripts.

Risks and test signals: command construction is deterministic but no validation is performed for empty paths. Failure mode is the raw `cmd.Run` error, so stderr context depends on configured `stderr`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder_test.go

Purpose: validates `Builder` initialization and `Check` command construction.

Important APIs and flow: `TestNewBuilder` checks binary path and default streams. `TestBuilderCheck/success` creates a temporary shell script that records its arguments, injects buffer streams, invokes `Check`, and asserts exact argument order. `TestBuilderCheck/command failed` uses a script that exits nonzero and expects an error.

State and persistence: uses temporary directories and writes fake executable scripts plus an argument log. No external Nydus binary is required.

Dependencies and integration: depends on `testify/require`, `bytes`, `os`, and `filepath`. It tests the wrapper boundary rather than real bootstrap parsing.

Risks and test signals: strong signal for CLI argument regression. It does not assert stdout/stderr content propagation beyond stream assignability and does not cover missing binary behavior separately from nonzero exit.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image.go

Purpose: provides helper logic for identifying parsed image type and mounting/unmounting OCI image root filesystems from extracted layer directories.

Important APIs and flow: `mkMounts` returns nil for no layers, a read-only recursive bind mount for one layer, and an overlay mount with `lowerdir=<layers joined by colon>` for multiple layers. `CheckImageType` returns `nydus`, `oci`, or `unknown` by inspecting `parser.Parsed`. `Image.Mount` creates the rootfs directory, builds layer directory names in reverse manifest order (`layer-N` down to `layer-0`), escapes colons for overlay lowerdir syntax, and calls `mount.All`. `Image.Umount` tolerates missing rootfs, otherwise calls containerd `mount.Unmount` and removes the rootfs tree.

State and persistence: creates and deletes rootfs directories; performs kernel mount operations. Layer data is assumed to already exist under `LayerBaseDir`.

Dependencies and integration: uses containerd mount package, OCI descriptors, and parser types. It is part of checker comparisons where OCI rootfs must be mounted while Nydus rootfs is mounted by `nydusd`.

Risks and test signals: requires mount privileges at runtime. Overlay lowerdir escaping only handles colon replacement; other unusual paths rely on kernel behavior. Unmount failure prevents cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image_test.go

Purpose: tests pure helper behavior and error paths in the image mount wrapper.

Important APIs and flow: `TestMkMounts` asserts nil, bind, and overlay mount structures. `TestCheckImageType` verifies priority of `NydusImage` over `OCIImage`. `TestImageMountErrors` forces `MkdirAll` failure by setting `Rootfs` to an existing file. `TestImageUmount` covers missing rootfs, stat failure through a file-as-parent path, and unmount failure for an ordinary temporary directory.

State and persistence: uses temporary files and directories only; no successful privileged mount is attempted.

Dependencies and integration: validates the shape expected by containerd mount APIs. It does not require OCI descriptors with real layer metadata.

Risks and test signals: good coverage for branch behavior and error wrapping. It intentionally avoids positive mount tests, so actual overlay/bind mount compatibility is left to integration testing on Linux with privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector.go

Purpose: wraps `nydus-image inspect` for extracting metadata from a Nydus bootstrap, currently blob information.

Important APIs and flow: `InspectOption` contains `Operation` and `Bootstrap`. `BlobInfo` maps JSON fields for blob ID, compressed/decompressed size, and readahead data; `String` methods marshal objects/lists as JSON. `NewInspector` stores the binary path. `(*Inspector).Inspect` builds `nydus-image inspect <bootstrap> --request blobs` for `GetBlobs`, runs `CombinedOutput`, wraps command failures with output text, unmarshals the JSON into `BlobInfoList`, and rejects unsupported operations with `not support method`.

State and persistence: no persistent state. Reads bootstrap via external command and returns decoded in-memory metadata.

Dependencies and integration: used by checker/tooling that needs blob layout from a bootstrap. Depends on external `nydus-image` output schema.

Risks and test signals: command output must be pure JSON on success. Unsupported operations use integer constants, so adding operations requires updating both dispatch and callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector_test.go

Purpose: tests inspector JSON formatting, construction, success parsing, command failure propagation, and invalid JSON handling.

Important APIs and flow: `TestBlobInfoString` and `TestBlobInfoListString` assert JSON serialization. `TestNewInspector` validates binary path assignment. `TestInspectorInspect` uses temporary shell scripts to emit valid blob JSON, emit an error with nonzero exit, and emit invalid JSON. It also tests unsupported operation dispatch.

State and persistence: writes temporary executable scripts only. No real bootstrap or `nydus-image` dependency is used.

Dependencies and integration: confirms the wrapper can decode the expected `nydus-image inspect --request blobs` schema and exposes failures to callers.

Risks and test signals: strong unit signal around parsing and errors. It does not check exact CLI arguments, so a command order regression could pass if fake scripts ignore arguments.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd.go

Purpose: creates configuration for and controls a `nydusd` process mounted by the checker.

Important APIs and flow: `NydusdConfig` carries backend, cache, socket, mount, bootstrap, mode, prefetch, and digest validation settings. `makeConfig` renders a JSON template, defaulting empty backend to localfs `{"dir": "/fake"}` and requiring explicit config for nonempty backend type. `checkReady` creates an HTTP client over a Unix socket and polls `/api/v1/daemon` until JSON state is `RUNNING` or context cancellation. `NewNydusd` writes config and returns a wrapper. `Mount` first calls silent `Umount`, starts `nydusd` with config, mountpoint, bootstrap, apisock, and warn logging, then races process exit, readiness, and a 30 second timeout. `Umount` shells out to `umount <mountpath>` if the mount path exists.

State and persistence: writes config files, starts long-lived external process, uses Unix socket HTTP, and changes kernel mount state.

Dependencies and integration: integrates checker rootfs validation with real `nydusd`. Uses `text/template`, `net/http`, Unix socket dialing, `exec`, and logrus.

Risks and test signals: readiness goroutine spins without sleep on connection failure, which can consume CPU during startup. `defer resp.Body.Close()` inside a loop delays closes until goroutine return. Runtime depends on `umount` and `nydusd` availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd_test.go

Purpose: tests config generation, Unix-socket readiness polling, mount command behavior, and unmount paths for `Nydusd`.

Important APIs and flow: `TestMakeConfig` asserts default localfs config and missing backend config errors. Readiness tests create Unix listeners/HTTP handlers that return `RUNNING` or invalid/non-running responses. Mount tests use fake `nydusd` scripts and PATH-injected `umount` scripts to validate successful readiness and binary failure. `TestUmount` covers missing mount path, successful command invocation, command failure, and non-silent output path.

State and persistence: uses temp config files, Unix sockets, temporary executable scripts, and environment PATH overrides.

Dependencies and integration: exercises real HTTP-over-Unix behavior without real `nydusd`. It verifies integration contracts around daemon state JSON and command invocation.

Risks and test signals: good coverage for wrapper mechanics. It does not verify actual FUSE mount behavior, cache behavior, or timeout duration except through controlled fake process/socket timing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator.go

Purpose: implements chunk dictionary generation from one or more source Nydus images and pushes a target image containing the generated dictionary bootstrap and required blob layers.

Important APIs and flow: `Opt` holds source/target refs, insecure flags, backend settings, workdir, `nydus-image` path, arch, and platform selection. `Generator` owns parsers for each source. `New` creates remotes and parsers. `Generate` pulls bootstraps with HTTP retry, runs `generate`, then `push`. `pull` parses each source, creates a sanitized workdir, and delegates `Output`. `generate` invokes `build.Builder.Generate` with bootstrap paths, sqlite database URI, output bootstrap, and output JSON. `push` creates a converter provider, optionally a backend, pulls source images, enumerates manifests, calls `pushBlobFromBackend`, and pushes target descriptors. `pushBlobFromBackend` reads the original manifest and output JSON blob IDs, deduplicates blob IDs, pushes blobs from backend or content store, repacks the generated bootstrap into a gzip layer, rewrites manifest layers/config diff IDs, and writes updated JSON to the content store. `getPushWriter` opens a registry pusher and treats already-existing blobs as skipped. `store.Info` overlays descriptor sizes for remote blobs not present in the base store.

State and persistence: writes per-source bootstrap directories, a sqlite database, output JSON, generated bootstrap, and content-store objects; pushes blobs/manifests to registries. It mutates provider content store when remote blob descriptors are needed.

Dependencies and integration: integrates `parser`, original provider remotes, Harbor acceleration service provider, containerd content store, Nydus build wrapper, backend abstraction, OCI descriptors, platform filtering, and retry-with-HTTP behavior.

Risks and test signals: manifest rewrite assumes output JSON accurately lists blob IDs and that bootstrap gzip digest/size are committed correctly. `sem.Acquire` errors are ignored. Concurrency is limited to one manifest in `push` but blob push uses provider layer limit. External registry/backend failures dominate runtime risk.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator_test.go

Purpose: tests chunkdict generator construction and helper paths with mocked parser/provider/backend behavior.

Important APIs and flow: tests use `gomonkey` to patch external-heavy functions such as remote/parser creation, parser parsing, bootstrap pulling, provider pulls/pushes, and content store operations. They validate `New`, source output for Nydus images, errors for non-Nydus inputs, output JSON/blob handling, `getPushWriter` already-exists behavior, and the `store.Info` descriptor fallback.

State and persistence: uses temporary directories, local content stores, tar/gzip helpers, and mocked readers. It avoids real registries and real `nydus-image`.

Dependencies and integration: covers interfaces to parser, provider, content store, backend, and OCI JSON helpers, giving regression signal for generator orchestration without full network execution.

Risks and test signals: extensive monkey patching isolates units but can hide integration breakage in actual containerd/registry paths. Tests emphasize success/error plumbing over validating generated chunk dictionary semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/generator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/output.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/output.go

Purpose: writes parsed Nydus image metadata and extracts its bootstrap to disk as generator input.

Important APIs and flow: `prettyDump` writes indented JSON to a path. `(*Generator).Output` optionally dumps image index, dumps Nydus manifest and config, calls the source parser's `PullNydusBootstrap`, and unpacks `utils.BootstrapFileNameInLayer` from the bootstrap layer into `nydus_bootstrap`. If the parsed source lacks `NydusImage`, it returns an error naming the source ref.

State and persistence: creates JSON files and a raw bootstrap file under the per-source output directory. It consumes a streamed bootstrap layer and closes it after unpacking.

Dependencies and integration: depends on parser output shape and `utils.UnpackFile`. It is called by `Generator.pull` before `nydus-image chunkdict generate`.

Risks and test signals: assumes output directory exists. Failure to close the bootstrap reader after unpack is deferred but close errors are not surfaced. Non-Nydus sources are rejected early.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter.go

Purpose: implements committing a running container's changes into a new Nydus image.

Important APIs and flow: `Opt` carries workdir, containerd address/namespace, container ID, image refs, max commit count, fs/compressor options, and selected include/exclude paths. `NewCommitter` prepares a temp workdir and container manager. `Commit` resolves short container IDs, inspects containerd state, pulls the base Nydus bootstrap, enforces maximum committed layers, discovers fs version/compressor via `nydus-image check`, pushes lower blobs, syncs filesystems, pauses the container, commits upperdir diff and requested mount paths as Nydus blobs, commits appended mount paths discovered during diff, merges bootstraps, and pushes config/bootstrap/manifest. Helper functions cover bootstrap pulling, upper diff packing, blob pushing from local files or remote source layers, pausing/unpausing, namespace sync, descriptor generation, mount copying with `nsenter tar`, bootstrap merging, retry, target ref validation, bootstrap info extraction, and short ID resolution.

State and persistence: creates temp workdir files for base bootstrap, upper/mount blobs, merged bootstrap tar/gz, and output JSON. It pauses/resumes containers, runs host and namespace `sync`, reads remote images, and pushes blobs/manifests. It mutates the target image manifest/config diff IDs and Nydus commit annotations.

Dependencies and integration: ties together containerd manager, parser/provider remotes, snapshotter-converter pack/merge, overlay diff package, nsenter, local content readers, OCI descriptors, distribution source labels, and Nydus annotation constants.

Risks and test signals: high operational risk due to container pause windows, mount namespace access, overlay diff correctness, remote push retry with reused readers, and external command dependence. Lower blob detection by `blob-mount-` name overlaps explicit mount blob names, so call context matters. Close errors in `pushBlob` are captured in a deferred variable but checked before deferred close runs, making close failures effectively lost.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter_helpers_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter_helpers_test.go

Purpose: unit tests helper functions in `commiter.go`.

Important APIs and flow: `TestWithRetry` and `TestWithRetryImmediate` validate retry counts and final error behavior. `TestValidateRef` and `TestValidateRefAddsTag` assert Docker reference normalization and digested reference rejection. `TestGetDistributionSourceLabel` and invalid cases verify containerd distribution-source label construction. `TestMountList` checks thread-safe append behavior at the API level. `TestMakeDesc` and marshal-error cases validate JSON descriptor generation.

State and persistence: pure in-memory except for no-op descriptor data. No containerd or registry operations are invoked.

Dependencies and integration: validates behavior critical to manifest push and retry control. Uses OCI descriptors and distribution/reference parsing.

Risks and test signals: good coverage of deterministic helpers. It does not test concurrent `MountList.Add`, real retry side effects, or descriptor media type preservation beyond simple inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker.go

Purpose: resolves container ID prefixes by walking containerd containers, ported from nerdctl.

Important APIs and flow: `Found` describes each match with raw request, index, and total match count. `NewContainerWalker` stores a containerd client and callback. `Walk` rejects `k8s://` form, builds a regex ID filter `id~=^<quoted req>.*$`, lists containers, and calls `OnFound` for each result with match metadata.

State and persistence: no persistence. Reads containerd metadata through the client.

Dependencies and integration: used by `Committer.resolveContainerID` to expand short IDs and detect ambiguity before inspecting/committing containers.

Risks and test signals: only ID prefix matching is supported; names are mentioned in comments but not implemented. Callback errors abort the walk. A nil `OnFound` would panic if matches exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker_test.go

Purpose: tests `ContainerWalker` using a mock container store plugged into a containerd client.

Important APIs and flow: `mockContainerStore` implements container store methods around a configurable list/error. `TestWalkK8sPrefixRejection` checks unsupported request form. `TestWalkContainersQueryFails` covers list errors. `TestWalkOnFoundCallbackFails` ensures callback errors abort. `TestWalkSuccessfulPath` verifies match count, request propagation, and match indexes for two containers.

State and persistence: pure in-memory containerd service mock; no daemon needed.

Dependencies and integration: validates the walker contract consumed by commit short-ID resolution.

Risks and test signals: strong for walker branching. It does not assert the exact filter string sent to the store, because the mock ignores filters, and does not test zero-match success directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar.go

Purpose: writes OCI layer tar streams from filesystem change events, ported from containerd with Nydus-specific error context.

Important APIs and flow: `ChangeWriter` wraps `tar.Writer`, source root, inode hardlink tracking, parent-directory tracking, and timestamp options. `NewChangeWriter` initializes it. `HandleChange` converts delete events to OCI whiteout files, skips sockets, handles symlinks, creates PAX headers, normalizes paths to slash form, sets special device headers via Unix helper, tracks hardlinks, skips unmodified entries, records `security.capability` xattrs, includes parent directories, writes file headers and regular file contents, and emits additional hardlink entries. `Close` closes the tar writer. `includeParents` recursively ensures parent directory entries exist. `copyBuffered` copies with pooled buffers and context cancellation checks.

State and persistence: streams tar output only; reads source filesystem metadata, file contents, symlinks, and xattrs.

Dependencies and integration: consumed by overlay diff `writeUpperdir` to produce the tar stream that snapshotter-converter packs into a Nydus blob. Relies on containerd continuity change kinds and Unix-specific helpers.

Risks and test signals: correctness is security-sensitive because ownership, devices, hardlinks, xattrs, and whiteouts define image layer behavior. Parent inclusion uses `os.Stat`, so missing parents fail the diff. Context in file copy uses `context.TODO` from `HandleChange`, so caller cancellation only reaches the outer writer path, not copy internals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_test.go

Purpose: tests tar change writer behavior for copying, whiteouts, parent directories, skipped unmodified files, directories, and archive entry names.

Important APIs and flow: helper `tarEntryNames` reads generated tar bytes and sorts names. Tests cover `copyBuffered` success and canceled context, delete-to-whiteout output, added regular files with parent directory entries, unmodified file omission, and directory handling. Additional tests in the file exercise symlinks, hardlinks, special cases, and close behavior where available.

State and persistence: uses temporary source directories and in-memory tar buffers.

Dependencies and integration: validates output consumed by the Nydus commit diff path and OCI layer semantics.

Risks and test signals: good signal for common tar entry behavior. Full device/xattr behavior depends on platform privileges and is partly delegated to Unix-specific tests/helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix.go

Purpose: provides Unix-specific filesystem helpers for tar archive generation.

Important APIs and flow: the file supplies helpers used by `tar.go` such as opening paths without following unsafe semantics where appropriate, reading xattrs, setting tar header fields for character/block devices and FIFOs, and normalizing permission bits through `chmodTarEntry`.

State and persistence: reads Unix file metadata and extended attributes; no writes except through tar headers created by callers.

Dependencies and integration: required by `ChangeWriter.HandleChange` for preserving Linux/Unix layer semantics in committed images. It integrates with `archive/tar`, `os.FileInfo`, and syscall metadata.

Risks and test signals: behavior is platform-specific and affects correctness for devices, capabilities, and mode bits. Runtime depends on filesystem/xattr support and caller privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix_test.go

Purpose: tests Unix-specific tar helper behavior.

Important APIs and flow: tests validate mode normalization and special header handling for Unix file modes where feasible in a unit-test environment. They complement `tar_test.go` by covering helper branches that are compiled only on Unix.

State and persistence: uses temporary filesystem entries and in-memory headers/buffers. Device node coverage may be constrained by permissions.

Dependencies and integration: verifies the tar writer's platform layer, which is critical for container image fidelity.

Risks and test signals: useful for permission/mode regressions, but privileged device and xattr scenarios may not be fully covered on all CI systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/diff.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/diff.go

Purpose: builds a tar diff stream from overlay snapshot lower/upper directories for container commit.

Important APIs and flow: `overlaySupportIndex` detects kernel overlay index support. `writeUpperdir` creates an empty lower dir, overlays upperdir over it, mounts the real lower snapshot, constructs `archive.ChangeWriter`, and calls `Changes` to emit change records. `Diff` appends an empty lower to the lowerdir list, creates lower and upper overlay mount definitions, finds the real upperdir with BuildKit overlay logic, then calls `writeUpperdir` with a cancellable writer.

State and persistence: creates temporary empty lower directories and temporary overlay mounts through containerd mount helpers; writes diff data to caller's writer.

Dependencies and integration: called by `Committer.commitUpperByDiff`. Depends on containerd mount, BuildKit overlay helpers, and local archive writer.

Risks and test signals: requires Linux overlay mount support and privileges. Incorrect lowerdir ordering or unsupported overlay options can produce wrong diffs or fail. It appends an empty lower to avoid overlay constraints.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_linux.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_linux.go

Purpose: implements overlayfs-specific change detection, adapted from BuildKit/containerd continuity.

Important APIs and flow: `GetUpperdir` compares lower and upper mount descriptions to identify the top diff directory. `GetOverlayLayers` parses `lowerdir`, `upperdir`, and known overlay options, returning bottom-to-top layers. `cancellableWriter` stops writes when context is canceled. `Changes` walks the upperdir, rebases paths, filters `withoutPaths`, detects unsupported redirect directories and appends them for separate mount commits, classifies whiteout deletes, modifies, and adds by comparing against the base, skips unchanged directory entries with `sameDirent`, handles opaque directories through a nested continuity diff, and finally emits delete records for `withPaths` so those lower files are replaced by separately committed mount blobs. Helper functions detect whiteouts, opaque xattrs, redirect xattrs, compare stat/capability/symlink/content, and use pooled buffers for file comparison.

State and persistence: reads overlay upper/base/view trees and xattrs; no direct writes except via supplied change callback.

Dependencies and integration: central to committer correctness. Integrates selected mount path handling with `MountList.Add`, `archive.ChangeWriter`, and snapshotter-converter pack.

Risks and test signals: redirect_dir is not supported and is surfaced as append-mount work rather than diffed. Xattr access may require privileges. Unknown overlay options intentionally fail. Path filtering is prefix-based and should use normalized absolute paths to avoid surprises.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_test.go

Purpose: tests overlay layer parsing, upperdir selection, stat comparison, and file comparison helpers.

Important APIs and flow: `TestGetOverlayLayers` covers lower/upper ordering, lower-only mounts, known option skipping, and unknown option errors. `TestGetUpperdir` covers bind bottom layers, overlay-over-bind and overlay-over-overlay cases, unsupported mount types, multiple mount configs, layer mismatch, and too many upper layers. Additional tests validate `compareSysStat`, symlink/content comparison, and related helper outcomes.

State and persistence: mostly in-memory mount structs, plus temporary files for content comparison tests.

Dependencies and integration: validates the assumptions used before the committer packs diffs from containerd nydus snapshots.

Risks and test signals: strong branch coverage for parser logic. It does not perform real overlay mounts or full `Changes` traversal with kernel whiteout/opaque xattrs in all cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager.go

Purpose: provides containerd operations needed by the committer: pause, resume, and inspect.

Important APIs and flow: `InspectResult` contains lowerdirs, upperdir, source image name, OCI mounts, and task PID. `NewManager` stores the containerd address. `Pause` and `UnPause` create a containerd client, load a container, get its task, and call `Pause`/`Resume`. `Inspect` loads the container, reads image name and task PID, unmarshals OCI spec mounts, queries the `nydus` snapshot service for snapshot mounts, requires at least one mount, and parses `lowerdir`/`upperdir` from mount options. `parseMountOptions` accepts arbitrary option order but requires both fields.

State and persistence: reads containerd metadata and controls task state. It creates new clients per call and does not close them explicitly.

Dependencies and integration: used by `Committer.Commit`, `syncFilesystem`, and pause handling. Assumes the snapshotter name is `nydus`.

Risks and test signals: missing client close can leak resources in long-running processes. Snapshotter name is hard-coded. It only uses the first returned mount. Mount option parsing is simple and does not unescape commas/colons.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager_test.go

Purpose: tests manager behavior with monkey-patched containerd clients, mock containers/tasks/images, and snapshotter responses.

Important APIs and flow: mock types implement required containerd interfaces. Tests cover pause/resume client/load/task failures and success, inspect failures at image/task/info/spec/snapshot stages, empty snapshot mounts, and parsing mount options into lower/upper dirs. `TestParseMountOptions` covers standard, volatile, reversed, multi-lower, `index=off`, and missing field cases.

State and persistence: pure mocks, no containerd daemon. Uses gomonkey to replace client methods.

Dependencies and integration: verifies the exact inspect data consumed by committer orchestration.

Risks and test signals: good branch coverage for error wrapping and parsing. Monkey-patched tests can be brittle across containerd API changes and do not catch real service lifecycle issues such as unclosed clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter.go

Purpose: builds and executes `nsenter` commands for running programs inside a target process namespace.

Important APIs and flow: `Config` contains booleans and optional namespace file paths for cgroup, IPC, mount, net, PID, user, and UTS namespaces, plus UID/GID, root, working directory, no-fork, credential preservation, SELinux context, and target PID. `Execute` uses a background context. `ExecuteContext` builds the base command, opens stdout pipe, appends program and args, captures stderr, starts the process, copies stdout to the supplied writer, and waits. `buildCommand` validates `Target`, appends `nsenter` flags for enabled fields, and returns `exec.CommandContext(ctx, "nsenter", args...)`.

State and persistence: runs external processes and streams their output. No persistent files are created by this wrapper.

Dependencies and integration: used by committer to run `sync` and `tar` in container mount/PID namespaces.

Risks and test signals: stdout pipe close is polled by a goroutine checking `ProcessState`, which may lag until `Wait`. Typo-compatible flag `--ip=<file>` is used for IPC file mode, matching current code but worth validating against util-linux `nsenter`. Requires host privileges and `nsenter` binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter_test.go

Purpose: tests `Config.buildCommand` flag construction.

Important APIs and flow: tests cover missing target, minimal target, namespace booleans without file paths, namespace booleans with explicit file paths, and credential/directory flags such as follow-context, setgid, no-fork, preserve-credentials, root, setuid, and working directory.

State and persistence: no process execution; only command argument construction is inspected.

Dependencies and integration: protects the `nsenter` command contract used by `copyFromContainer` and `syncFilesystem`.

Risks and test signals: strong for argument assembly. It does not run `ExecuteContext`, so stdout/stderr streaming, cancellation, and process wait behavior are not validated here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util.go

Purpose: provides a small atomic byte counter implementing `io.Writer`.

Important APIs and flow: `Counter.Write` atomically adds `len(p)` to an int64 and reports the full write length. `Counter.Size` atomically reads the accumulated count.

State and persistence: in-memory atomic counter only.

Dependencies and integration: used while packing upper and mount blobs to log generated blob sizes without wrapping the output stream in a separate counting writer.

Risks and test signals: simple and thread-safe for concurrent writes. It never returns partial writes or errors, which is appropriate for a side-channel counter.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util_test.go

Purpose: verifies `Counter` write accounting.

Important APIs and flow: `TestCounterWriteAndSize` checks initial zero size, writes two byte slices, verifies returned lengths, nil errors, and cumulative size.

State and persistence: pure in-memory.

Dependencies and integration: protects blob-size logging used by committer pack paths.

Risks and test signals: covers sequential writes. It does not stress concurrent writes, though the implementation uses atomics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor.go

Purpose: wraps `nydus-image compact` to compact Nydus blobs/bootstrap using configurable thresholds.

Important APIs and flow: `CompactConfig` stores min used ratio, compact blob size, max compact size, layers to compact, and blobs directory. `Dumps` writes JSON config; `loadCompactConfig` reads it. `NewCompactor` loads a config or uses defaults, sets `BlobsDir` to the workdir, and creates a build `Builder`. `Compact` removes stale `<bootstrap>.compact` and `compact-result.json`, calls `builder.Compact` with chunk dictionary, backend, output paths, and config thresholds, then returns the target bootstrap path.

State and persistence: reads/writes config files, removes old output files, writes compact output through the external builder command.

Dependencies and integration: integrates with `pkg/build.Builder` and Nydus compact CLI options. Intended to be used in conversion/optimization flows after bootstrap creation.

Risks and test signals: all numeric config values are strings and are not validated before command execution. `BlobsDir` from config is always overwritten by workdir. Output JSON is removed and regenerated but not parsed here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor_test.go

Purpose: tests compactor configuration and command wrapper behavior.

Important APIs and flow: `TestCompactConfigRoundTrip` writes and reloads JSON config. `TestNewCompactor` validates defaults, workdir-assigned `BlobsDir`, and missing config errors. `TestCompactorCompact` uses fake `nydus-image` scripts to assert compact arguments are issued and stale outputs are removed, and checks builder failure wrapping.

State and persistence: uses temporary directories, fake executable scripts, bootstrap files, and stale output files.

Dependencies and integration: verifies CLI wrapper plumbing without requiring real compaction.

Risks and test signals: strong for config and command invocation. It does not inspect the complete argument vector in order or validate compact output bootstrap contents.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict.go

Purpose: parses chunk dictionary command arguments used by converter options.

Important APIs and flow: valid formats currently contain only `bootstrap`; valid sources are `registry` and `local`. `ParseChunkDictArgs` splits the string on colon, requires at least three parts, validates format and source, and rejoins all remaining parts as the ref so registry tags and local paths containing colons are preserved. `ChunkDictOpt` stores raw args and an insecure flag.

State and persistence: none.

Dependencies and integration: feeds converter/chunk dictionary setup by separating format, source type, and reference/path.

Risks and test signals: simple split syntax cannot escape colons in the first two fields, but preserves them in refs. Error messages include accepted values.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict_test.go

Purpose: tests chunk dictionary argument parsing.

Important APIs and flow: success cases cover registry refs with tags and local absolute paths. Failure cases cover too few fields, invalid format, and invalid source, asserting specific error text.

State and persistence: pure in-memory.

Dependencies and integration: protects converter CLI/config parsing for chunk dictionary references.

Risks and test signals: adequate for current grammar. It does not cover Windows-style paths or future formats/sources.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/chunk_dict_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config.go

Purpose: converts `converter.Opt` into string driver configuration for the Harbor acceleration-service converter.

Important APIs and flow: `getConfig` returns a map with workdir, builder path, backend type/config/force-push, chunk dictionary ref, Docker/OCI/manifest/referrer booleans, prefetch patterns, compressor, fs version/alignment/chunk size, batch size, and cache ref/version/max records. Boolean and unsigned values are formatted as strings.

State and persistence: none.

Dependencies and integration: consumed by `converter.New(converter.WithDriver("nydus", getConfig(opt)))` in `Convert`.

Risks and test signals: stringly typed config means misspelled keys or invalid values are only caught by the downstream driver. Adding fields to `Opt` requires updating this mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config_metric_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config_metric_test.go

Purpose: tests converter driver config mapping and metric dumping.

Important APIs and flow: `TestGetConfig` populates an `Opt` with representative values and asserts every generated config key. `TestDumpMetric` writes an acceleration-service `Metric` to JSON, checks expected fields, and verifies path creation failure is wrapped.

State and persistence: writes metric JSON to a temporary file.

Dependencies and integration: protects `getConfig` compatibility with the `nydus` driver and `dumpMetric` output used by `Convert` when `OutputJSON` is set.

Risks and test signals: comprehensive for current config keys. It does not validate downstream driver interpretation or metric schema evolution beyond field presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config_metric_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter.go

Purpose: is the main image/model conversion entry point for `nydusify`.

Important APIs and flow: `Opt` captures workdir, containerd path, source/target refs or archives, backend/chunkdict/cache/security settings, Nydus filesystem parameters, platform filtering, metrics, and push retry settings. `Convert` dispatches model-file and model-artifact sources to specialized flows; otherwise it creates a namespace, platform matcher, work/temp dirs, converter provider, retry settings, local archive modes, optional plain HTTP, and runs Harbor acceleration-service converter with the `nydus` driver config. `convertModelFile` and `convertModelArtifact` process model data through `modctl` and snapshotter external handlers, pack Nydus blobs with attributes, build a final bootstrap tar including backend config, build model config/layers, and push an OCI artifact manifest. `packWithAttributes` writes blob and external blob files named by digest. `packFinalBootstrap` reads backend config, extracts bootstrap from an external blob, and packs backend plus bootstrap entries into a final tar. `buildNydusImage`, `buildModelConfig`, `pushManifest`, `getSourceManifestSubject`, and `makeDesc` construct and push model artifact config/bootstrap/manifest descriptors.

State and persistence: creates/removes workdirs and temp dirs, writes blob files, final bootstrap tar/gz, backend metadata/config/attributes, optional metric JSON, and pushes config/layer/manifest to remote registries or archives through providers.

Dependencies and integration: integrates Harbor acceleration-service converter, local provider wrapper, snapshotter-converter pack/unpack, CloudNativeAI model-spec, modctl handlers, parser image structs, remote provider, platformutil, and OCI descriptors.

Risks and test signals: workdir cleanup only occurs when the workdir did not exist initially. Push retry delay parsing requires a valid duration even for standard conversion. `packFinalBootstrap` has duplicated `defer bootstrap.Close()` and does not close `bootstrapTar` explicitly. Model artifact path depends on source subject resolution and correct Nydus artifact annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter_test.go

Purpose: tests standard conversion input validation and model conversion helper flows using monkey patching.

Important APIs and flow: `TestConvert` covers model dispatch errors, invalid platform, and invalid push retry delay. `TestConvertModelFile` and `TestConvertModelArtifact` patch modctl/external/pack/push helpers to verify success and each failure stage. `TestPackWithAttributes`, `TestPackFinalBootstrap`, `TestBuildNydusImage`, `TestMakeDesc`, `TestBuildModelConfig`, `TestPushManifest`, and `TestGetSourceManifestSubject` exercise helper behavior, remote fallback, gzip/bootstrap handling, and descriptor creation with mocks.

State and persistence: uses `/tmp/nydusify` and temp files, with cleanup in tests; monkey patches external functions and remote pushes.

Dependencies and integration: provides regression signal for orchestration and error wrapping across modctl, snapshotter-converter, remote provider, parser image descriptors, and model-spec.

Risks and test signals: broad but heavily mocked, so it validates call sequencing more than real conversion correctness. Some tests use fixed `/tmp/nydusify`, which can be sensitive to parallel runs or leftover files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts.go

Purpose: builds a Harbor acceleration-service `remote.HostFunc` for converter endpoints.

Important APIs and flow: `hosts(opt)` maps source, target, chunk dictionary, and cache refs to their corresponding insecure flags. The returned function always supplies Docker config credentials and returns the insecure flag for the requested ref.

State and persistence: no persistence; reads Docker credentials later through the returned credential function.

Dependencies and integration: used by `provider.New` in `Convert` so registry resolver setup can honor per-reference TLS settings.

Risks and test signals: map lookup defaults unknown refs to `false`, so unregistered refs are treated as secure. Empty string refs can collide in the map when optional fields are unset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts_test.go

Purpose: tests host function insecure flag mapping and credential function creation.

Important APIs and flow: tests construct an `Opt` with source, target, chunk dictionary, and cache refs/insecure flags, call `hosts`, and verify each ref returns the expected boolean and non-nil Docker credential function. Unknown refs are expected to return secure false.

State and persistence: pure in-memory; Docker config credential function is not invoked.

Dependencies and integration: protects resolver configuration used by converter provider creation.

Risks and test signals: adequate for map behavior. It does not verify actual credential lookup from Docker config files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/metric.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/metric.go

Purpose: writes conversion metrics to JSON.

Important APIs and flow: `dumpMetric` creates/truncates the target file, JSON-encodes a `converter.Metric`, wraps create and encode errors, and closes the file on return.

State and persistence: writes one JSON metrics file.

Dependencies and integration: called by `Convert` when `Opt.OutputJSON` is nonempty. Uses Harbor acceleration-service metric type.

Risks and test signals: caller ignores `dumpMetric` errors in `Convert`, so metric write failures do not fail conversion. Parent directories must already exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/metric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported.go

Purpose: ports selected containerd pull/push/import helpers so the custom provider can fetch, push, and load images against its content store.

Important APIs and flow: `importOpts` mirrors containerd archive import settings. `fetch` resolves a ref, creates a fetcher, rejects Docker schema1 manifests, builds handler chains for fetching children, platform filtering, legacy config conversion detection, distribution source labels, optional wrappers, concurrency limiting, and stream-store default refs; it dispatches descriptors and converts legacy manifests when needed. `push` normalizes platform matcher, annotates refs with digest, creates a pusher, wraps handlers, applies upload concurrency, and calls `remotes.PushContent`. `load` imports an OCI/docker archive index, walks descriptors with platform filtering and optional layer discard/missing skip, and produces image records from annotations or digest refs. `imageName` prefers containerd image-name annotation then OCI ref-name with optional cleanup.

State and persistence: reads/writes the supplied content store, pulls from remote fetchers, pushes to remote pushers, and imports archive streams.

Dependencies and integration: used by `Provider.remotePull`, `remotePush`, and `Import`. It bridges containerd v2 APIs with acceleration-service content and Nydus streaming content.

Risks and test signals: ported code must track containerd API semantics. Label handling assumes stream content can support Info/Update. Schema1 is explicitly unsupported. Platform filtering can drop manifests if matcher is wrong.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported_test.go

Purpose: tests `imageName` annotation precedence and cleanup behavior.

Important APIs and flow: cases assert `images.AnnotationImageName` is returned as-is, OCI `AnnotationRefName` is passed through a cleanup function, and nil annotations produce an empty string.

State and persistence: pure in-memory.

Dependencies and integration: protects archive import naming behavior used by `load`.

Risks and test signals: narrow coverage. The larger ported fetch/push/load flows are not unit-tested here and depend on containerd integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider.go

Purpose: implements the acceleration-service provider interface for Nydus conversion, supporting remote registries and local archive import/export.

Important APIs and flow: `Provider` stores mutex-protected image descriptors, content store, host resolver function, platform matcher, cache settings, chunk size, push retry config, local source/target paths, and plain HTTP flag. `New` creates a content directory and either uses an override store or acceleration-service content. `newDefaultClient` and `newResolver` build Docker resolvers with credentials, TLS skip, plain HTTP, and chunk size. `Pull` imports from local tar or remote-pulls and records the target descriptor. `remotePull` calls ported `fetch`. `SetPushRetryConfig` updates retry settings. `Push` exports to local tar or remote-pushes with retry. `Import` loads an archive and requires exactly one image. `Export`, `Image`, `ContentStore`, `SetContentStore`, `NewRemoteCache`, `WithLocalSource`, and `WithLocalTarget` expose provider operations for converter and chunkdict paths.

State and persistence: creates `<root>/content`, stores blobs/manifests in content store, records image descriptor map, imports/exports tar archives, pushes/pulls remote registry content, and toggles plain HTTP.

Dependencies and integration: central bridge between Harbor acceleration-service converter, containerd remotes/content, cache, Docker auth, local archive modes, and Nydus stream content.

Risks and test signals: `SetContentStore` is not mutex-protected while other methods use the store concurrently. `localPush` opens output without `O_TRUNC`, so overwriting a longer tar can leave trailing bytes. `newDefaultClient` sets `InsecureSkipVerify`; callers must ensure insecure flags are correct. Push retry reuses descriptors but underlying content readers are reopened by `PushContent`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider.go -->
