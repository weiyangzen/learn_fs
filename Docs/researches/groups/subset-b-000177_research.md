# subset-b-000177 Research

Grouped research report for the subset B work item. Each section preserves its source path in the title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_opts.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_opts.go

## Purpose
Defines `executorOpts`, the shared option bag used by platform-specific `newExecutor` implementations in Moby's embedded BuildKit builder. It is intentionally unexported and spans common, Linux-only, and Windows-only fields.

## APIs, Control Flow, and Integration
The struct carries the builder root, libnetwork controller, OCI DNS config, CDI manager, proxy provider, Linux cgroup/AppArmor/rootless/userns settings, and Windows containerd namespace/address/Hyper-V settings. There is no executable flow here; the file is an integration contract consumed by `executor_*.go` and builder setup code.

## State, Dependencies, and Risks
State is in-memory configuration only. Dependencies are BuildKit OCI/network/CDI APIs, Moby libnetwork, and `moby/sys/user`. Risk is field drift: platform files must ignore unsupported fields while builder setup must populate the platform-specific subset correctly. Tests are indirect through executor construction and build execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_others.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_others.go

## Purpose
Provides the non-Linux, non-Windows executor fallback under `//go:build !linux && !windows`.

## APIs, Control Flow, and Integration
`newExecutor(executorOpts)` returns a `stubExecutor`, no proxy provider, and no error. This lets the package compile on unsupported OS targets while avoiding real process execution support. It satisfies the same signature as Linux and Windows executor constructors.

## State, Dependencies, and Risks
There is no persisted state. Dependencies are only BuildKit `executor` and `network` interfaces. Runtime risk is that builds requiring execution will fail later through stub behavior; this file is primarily a compile-time portability shim. Test coverage is indirect by build tags and package compilation on non-Linux/non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_windows.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_windows.go

## Purpose
Constructs the Windows BuildKit executor and applies libnetwork endpoint data to OCI runtime specs.

## APIs, Control Flow, and Integration
`newExecutor` builds network providers for default/NAT and none modes, opens a containerd client using `containerdAddr` and namespace, then creates a `containerdexecutor.Executor` with DNS, CDI, proxy, root, network, and Hyper-V isolation options. `lnInterface.Set` waits for network readiness, extracts HNS endpoint IDs and unqualified DNS flags from libnetwork endpoints, and writes them into `specs.Windows.Network`.

## State, Dependencies, and Risks
State is external: containerd connectivity, libnetwork sandbox endpoint data, and runtime spec mutation. Risks include blocking on `iface.ready`, type assertions for driver info values, and missing endpoint metadata causing incomplete network specs. Test signals are indirect through Windows build/run behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/exporter.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/exporter.go

## Purpose
Defines shared constants and metadata types for Moby-specific BuildKit exporters.

## APIs, Control Flow, and Integration
`Moby` names the custom exporter type. `BuildRefLabel` prefixes content labels that track build references. `BuildRefLabelValue` stores optional `createdAt` timestamp metadata as JSON. The wrapper and moby exporter use these symbols when labeling exported image config descriptors and dispatching callbacks.

## State, Dependencies, and Risks
The file has no control flow or persistence by itself; it defines the label schema persisted in containerd content metadata by `wrapper.go`. Main risk is label key compatibility: consumers must treat the timestamp as optional and avoid assuming label presence. Test coverage is indirect through exporter wrapper behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/export.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/export.go

## Purpose
Implements the Moby image-store exporter for BuildKit results. It converts BuildKit refs into Moby image layers/configs, tags images, writes a temporary OCI descriptor reference, and returns BuildKit exporter metadata.

## APIs, Control Flow, and Integration
Key interfaces are `Differ` for turning snapshot refs into Moby layer diffIDs and `ImageTagger` for tag updates. `Opt` wires image store, differ, content store, lease manager, tagger, and callbacks. `Resolve` parses `name` exporter attributes into normalized references and stores all other attrs as metadata. `Export` rejects multiple refs, resolves the single ref/config, finalizes/extracts the ref, calls `EnsureLayer`, normalizes history, patches image config, creates the Moby image, tags target names, writes response keys, and creates a descriptor reference via `newTempReference`.

## State, Dependencies, and Risks
Persistence touches Moby image store, ref/tag store through callbacks, containerd content store, and temporary leases. Risks include only single-platform/single-ref support, nil-ref scratch handling, stale temporary leases if write/unlease fails, and history/rootfs mismatch bugs. Test coverage is mostly helper-level (`writer_test.go`), so full exporter behavior relies on integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer.go

## Purpose
Builds and patches OCI image configuration JSON for images exported into Moby's image store.

## APIs, Control Flow, and Integration
`emptyImageConfig` creates a minimal default-platform config with `WorkingDir`, default PATH, and `rootfs.type=layers`. `parseHistoryFromConfig` extracts history. `patchImageConfig` unmarshals config into raw JSON fields, replaces `rootfs` and `history`, fills `created` from the latest history timestamp when absent, and embeds inline cache under `moby.buildkit.cache.v0`. `normalizeLayersAndHistory` reconciles diffIDs, history entries, and BuildKit ref layer metadata, marking excess history layers empty and filling missing `Created` values. `getRefMetadata` reads description and created time from `cache.ImmutableRef.LayerChain`.

## State, Dependencies, and Risks
State is JSON-only, but it defines persisted image config semantics. Risks include silently rewriting invalid configs into usable-but-surprising history, nil ref metadata defaulting to empty entries, and embedded inline cache increasing config size. Tests assert patching accepts empty/history/rootfs configs and rejects `null`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer_test.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer_test.go

## Purpose
Validates basic image config patching behavior for the Moby exporter writer helpers.

## APIs, Control Flow, and Integration
`TestPatchImageConfig` table-drives `patchImageConfig` with `{}`, `{"history":[]}`, `{"rootfs":{}}`, and `null`. It expects all object configs to succeed and a null config to return `null image config`. The test uses `gotest.tools/v3/assert`.

## State, Dependencies, and Risks
No external state is touched. The test confirms parsing and top-level object validation but does not verify actual generated `rootfs`, `history`, `created`, or inline cache fields. It is a smoke test rather than comprehensive config compatibility coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/overrides/overrides.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/overrides/overrides.go

## Purpose
Sanitizes BuildKit exporter image names before passing them into Moby/containerd image export.

## APIs, Control Flow, and Integration
`SanitizeRepoAndTags` skips empty names, parses normalized references, rejects references containing a digest, applies `reference.TagNameOnly`, and deduplicates while preserving first occurrence order. It returns normalized repo:tag strings for `exporter/wrapper.go`.

## State, Dependencies, and Risks
No persistence. Dependency is `distribution/reference`. The primary risk is user-visible normalization: untagged names become `:latest`, duplicate aliases are removed, and digest-tag combinations are forbidden with a generic error. Test coverage is indirect; wrapper behavior depends on this function to prevent BuildKit from naming immutable digest refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/overrides/overrides.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/wrapper.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/exporter/wrapper.go

## Purpose
Wraps BuildKit's image exporter to apply Moby defaults, label exported content with build-reference metadata, and invoke daemon callbacks for exported/named images.

## APIs, Control Flow, and Integration
`BuildkitCallbacks` exposes `Exported` and `Named`. `NewWrapper` stores the wrapped exporter and content store. `Resolve` sanitizes `name`, defaults `unpack=true`, sets dangling image prefix, forces dangling-empty-only, and wraps the resolved instance. `Export` delegates to the inner exporter, reads the descriptor and image digest, writes a `moby/build.ref.<ref>` content label containing `createdAt`, invokes `Exported`, then parses output `image.name` and calls `Named` for valid tagged refs.

## State, Dependencies, and Risks
Persistence is containerd content label updates. Risks include mutating the caller's attr map, relying on legacy `image.name` until newer BuildKit constants are vendored, and export failure if label update fails after the inner exporter already wrote content. Integration is with containerd image store and Moby callbacks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/exporter/wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/imagerefchecker/checker.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/imagerefchecker/checker.go

## Purpose
Provides a BuildKit external reference checker that prevents cache garbage collection from deleting refs still used by Moby images.

## APIs, Control Flow, and Integration
`LayerGetter` abstracts lookup of a layer by snapshot/cache key. `Opt` wires `LayerGetter` and `image.Store`. `New` returns a `cache.ExternalRefCheckerFunc`. The checker lazily initializes once by walking all images and inserting each image rootfs diffID chain into an `lchain` trie. `Exists` caches answers by key, resolves the layer, reconstructs its parent diffID chain via `diffIDs`, and checks if that chain exists in the trie.

## State, Dependencies, and Risks
State is in-memory and per checker: `sync.Once`, trie, and key result cache. It reads the current image map only once, so newly created images after initialization are not reflected. Risks include recursion depth on long layer chains and false negatives if `LayerGetter` cannot resolve a key. Tests are indirect through cache GC behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/imagerefchecker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/reqbodyhandler.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/reqbodyhandler.go

## Purpose
Implements an HTTP round tripper that serves build context request bodies through synthetic one-shot URLs.

## APIs, Control Flow, and Integration
`newReqBodyHandler` wraps a fallback `RoundTripper`. `newRequest` stores an `io.ReadCloser` under a generated ID and returns `http://build-context-<id>` plus a cleanup function. `RoundTrip` intercepts hosts with `build-context-`, requires GET, atomically removes the stored reader, and returns a 200 response with that body. Other requests delegate to the wrapped transport.

## State, Dependencies, and Risks
State is a mutex-protected map of pending bodies. Readers are single-use; retrying the synthetic URL returns `context not found`. Cleanup closes the body and removes the entry. Risks include leaks if cleanup is not called for unused URLs and no response headers/content length metadata. Integration is BuildKit HTTP source transport.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/reqbodyhandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/containerdworker.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/worker/containerdworker.go

## Purpose
Adapts BuildKit's base containerd worker for Docker's containerd image store mode.

## APIs, Control Flow, and Integration
`ContainerdWorker` embeds `*base.Worker` and stores export callbacks. `NewContainerdWorker` creates the base worker, registers an HTTP source using the daemon transport, and returns the wrapper. `Exporter` intercepts the Moby exporter name by resolving BuildKit's normal image exporter and wrapping it with Moby-specific callbacks and content labeling; all other exporters delegate to the base worker.

## State, Dependencies, and Risks
State is owned by the embedded BuildKit worker and content store. Risks include HTTP source registration failure only logging a warning, so HTTP source support can be absent at runtime. The Moby exporter path depends on wrapper correctness and content store label support. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/containerdworker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/gc.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/worker/gc.go

## Purpose
Defines default BuildKit cache garbage-collection policy for the Moby worker.

## APIs, Control Flow, and Integration
`DefaultGCPolicy` fills reserved/max/min free-space defaults from disk stats when caller values are zero, falls back to 2GB reserved when disk stats fail, computes a small temporary cache cap, and returns four ordered `client.PruneInfo` rules: prune reproducible local/cache/git entries after 48h over temp cap, prune old unused entries after 60 days, keep unshared cache under the cap, then allow pruning all internal data if needed. `diskPercentage` rounds disk percentage to GB-ish decimal bytes.

## State, Dependencies, and Risks
It reads filesystem disk stats but persists nothing. Risks include surprising `tempCachePercent` value and decimal/gibibyte rounding. The policy directly affects build cache retention and disk pressure behavior; coverage is indirect through daemon/build cache tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/label/label.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/worker/label/label.go

## Purpose
Defines Moby BuildKit worker label keys.

## APIs, Control Flow, and Integration
The package exposes `HostGatewayIP`, under prefix `org.mobyproject.buildkit.worker.moby.`, mirroring BuildKit-style worker labels. It has no functions; callers use the constant to advertise host-gateway IP capability/configuration.

## State, Dependencies, and Risks
No state or dependencies beyond package constants. Compatibility risk is label-key stability, since labels may be consumed by frontends or diagnostics. Tests are not present; correctness is by convention and integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/label/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/worker.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/worker/worker.go

## Purpose
Implements Docker's local BuildKit worker over Moby layer storage, snapshot/content/cache managers, daemon image source, registry metadata, and Moby exporters.

## APIs, Control Flow, and Integration
`Opt` wires executor, snapshotter, cache/content/lease managers, image source, download manager, v2 metadata service, registry transport, exporter, layer access, platforms, CDI, and proxy provider. `NewWorker` registers image, git, HTTP, and local sources. The worker implements identity/labels/platforms/GC/version/close, source metadata resolution for image/git/http, LLB op resolution, exporters, disk usage/prune, remotes conversion, cache-mount pruning, and remote import.

## State, Dependencies, and Risks
State spans BuildKit cache refs, Moby layers, containerd content, leases, v2 distribution metadata, and source managers. `GetRemotes` can finalize/extract refs and ensure Moby layers; `FromRemote` downloads descriptors into the layer store, deletes content blobs after import, and reconstructs cache refs with creation/description annotations. Risks include source registration only warning on failure, no source-policy support, attestation-chain rejection without containerd image store, mutable platform cache in `Platforms(noCache)`, and metadata Add errors ignored in `layerDescriptor.Registered`. `worker_test.go` covers platform merging only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/worker_test.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/worker/worker_test.go

## Purpose
Tests platform list merging for the Moby BuildKit worker.

## APIs, Control Flow, and Integration
`TestMergePlatforms` defines default, Windows, and Darwin/arm64 platforms and covers unique, overlapping, empty-supported, empty-defined, and both-empty cases. It asserts result length and that expected platforms are present using `gotest.tools`.

## State, Dependencies, and Risks
No external state. The test confirms `mergePlatforms` deduplicates using platform matchers while preserving desired membership. It does not assert order or the mutating behavior of `Worker.Platforms(noCache)`, and it does not cover source registration, executor, export, remote import, or cache operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/worker/worker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/capabilities/caps.go -->
# sources/cloud-native/moby/daemon/internal/capabilities/caps.go

## Purpose
Provides a tiny generic capability matching helper.

## APIs, Control Flow, and Integration
`Set` is `map[string]struct{}`. `Match(caps [][]string)` treats the input as OR-of-AND capability requirements, scanning in order and returning the first AND-list fully contained in the set. A nil set returns nil. If no list matches, it returns nil; an empty inner list matches immediately.

## State, Dependencies, and Risks
No persistence and no imports. Risks are semantic: nil also means no match, while an empty returned slice means a deliberately empty requirement matched. Callers must distinguish nil from empty when needed. Tests cover matching, ordering, empty lists, and non-matches.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/capabilities/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/capabilities/caps_test.go -->
# sources/cloud-native/moby/daemon/internal/capabilities/caps_test.go

## Purpose
Validates OR-of-AND capability matching semantics.

## APIs, Control Flow, and Integration
`TestMatch` builds a set containing `foo` and `bar`, then table-tests empty AND-list match, single capability matches, first-match ordering, multi-capability AND matches, fallback to later OR entries, and several non-match cases. It compares returned slice length and values in order.

## State, Dependencies, and Risks
No external state. The tests document the important nil-versus-empty distinction and ordered selection behavior. They do not exercise nil `Set`; production code explicitly returns nil for that.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/capabilities/caps_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/cleanups/composite.go -->
# sources/cloud-native/moby/daemon/internal/cleanups/composite.go

## Purpose
Implements a simple LIFO cleanup stack with aggregate error reporting.

## APIs, Control Flow, and Integration
`Composite.Add` appends cleanup functions. `Call` executes all registered cleanups in reverse order via `call`, joins all returned errors using `multierror.Join`, and clears the stack. `Release` clears the stack but returns a function that can later execute the previously registered cleanups, also in reverse order.

## State, Dependencies, and Risks
State is an in-memory slice; there is no synchronization, so callers must not mutate from multiple goroutines. Cleanup functions are always called even after earlier errors. Risks include nil cleanup functions panicking and callers forgetting to invoke a released function. Tests confirm reverse order and nested/joined error preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/cleanups/composite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/cleanups/composite_test.go -->
# sources/cloud-native/moby/daemon/internal/cleanups/composite_test.go

## Purpose
Tests cleanup aggregation and reverse execution order.

## APIs, Control Flow, and Integration
`TestCall` registers four cleanups: one direct error, one nil, one wrapped error, and one `errors.Join` group. It calls `Composite.Call`, unwraps the multi-error, checks all component messages/errors are present, and asserts reverse-order placement for the non-nil cleanup errors.

## State, Dependencies, and Risks
No external state. The test documents that nil cleanup results are omitted from the joined error and that wrapped/joined errors remain discoverable with `errors.Is`. It does not cover `Release` behavior or concurrent mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/cleanups/composite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/compat/compat.go -->
# sources/cloud-native/moby/daemon/internal/compat/compat.go

## Purpose
Provides JSON response compatibility wrappers that can add legacy fields or omit newer fields without mutating source structs.

## APIs, Control Flow, and Integration
`Wrapper.MarshalJSON` marshals `Base` with HTML escaping disabled, optionally unmarshals into a map, deletes omitted fields, recursively merges extra fields, and marshals again. `WithExtraFields` accumulates additive-only fields; existing output values win except nil values may be replaced. `WithOmittedFields` records top-level fields to delete. `Wrap` constructs the wrapper.

## State, Dependencies, and Risks
State is per-wrapper maps/slices. Risks include map-based JSON reordering, top-level-only omit semantics, type erasure through `map[string]any`, and marshal failure for non-object base JSON when options are present. Tests cover add/omit, nil field replacement, nested wrapped values, and no HTML escaping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/compat/compat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/compat/compat_test.go -->
# sources/cloud-native/moby/daemon/internal/compat/compat_test.go

## Purpose
Documents and verifies compatibility JSON wrapper behavior.

## APIs, Control Flow, and Integration
Tests cover no-options passthrough, extra fields, omitted fields, combined add/omit, replacing nil pointer fields with extra values, nested wrapped structs as extra fields, and disabled HTML escaping for `&` and `<...>`. Assertions compare exact JSON strings.

## State, Dependencies, and Risks
No external state. Exact string comparisons intentionally lock output ordering produced by map marshaling in the tested cases, which can make tests sensitive to future implementation changes. The suite does not cover invalid base JSON shapes, conflicting non-nil fields, or repeated option conflict ordering beyond comments.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/compat/compat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm.go -->
# sources/cloud-native/moby/daemon/internal/containerfs/rm.go

## Purpose
Provides a robust Unix/non-Darwin container filesystem removal helper that handles mounts and common removal races.

## APIs, Control Flow, and Integration
`EnsureRemoveAll` first recursively unmounts beneath the target, then loops around `os.RemoveAll`. It ignores/reruns certain `ENOENT` races for child paths, retries once on `ENOTEMPTY`, handles `EBUSY` by unmounting the reported path, and retries busy paths up to 50 times with 100ms sleeps.

## State, Dependencies, and Risks
State is local retry maps. External effects are destructive filesystem deletion and mount unmounting. Risks include broad recursive unmount scope, up to five seconds waiting per busy path, and returning wrapped unmount errors instead of original removal errors. Tests cover absent paths, files, dirs, and root-only bind mount removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_nodarwin_test.go -->
# sources/cloud-native/moby/daemon/internal/containerfs/rm_nodarwin_test.go

## Purpose
Tests platform-independent non-Darwin removal behavior.

## APIs, Control Flow, and Integration
Tests assert `EnsureRemoveAll` does not error for a nonexistent path, a temporary directory, or a temporary file. The file is excluded on Darwin by build tag and covers both Unix and Windows implementations where applicable.

## State, Dependencies, and Risks
Tests operate on temp files/directories plus one fixed nonexistent path. They confirm the helper's contract not to return `os.ErrNotExist` for missing targets. They do not cover race retries, busy mount unmounting, or permission failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_nodarwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_test.go -->
# sources/cloud-native/moby/daemon/internal/containerfs/rm_test.go

## Purpose
Tests Linux/non-Windows/non-Darwin mount cleanup behavior for `EnsureRemoveAll`.

## APIs, Control Flow, and Integration
`TestEnsureRemoveAllWithMount` requires root, creates two temp dirs, bind-mounts one inside the other, calls `EnsureRemoveAll` asynchronously, fails on a 5-second timeout, and verifies the outer directory is gone.

## State, Dependencies, and Risks
The test mutates real mounts and skips when not root. It directly validates recursive unmount/busy-path handling, but depends on host mount permissions and can be skipped in most CI environments. It does not assert the secondary source directory remains intact beyond deferred cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_windows.go -->
# sources/cloud-native/moby/daemon/internal/containerfs/rm_windows.go

## Purpose
Provides the Windows implementation of container filesystem removal.

## APIs, Control Flow, and Integration
`EnsureRemoveAll(path string)` is a direct alias to `os.RemoveAll`. Unlike the Unix implementation, it performs no mount recursion, busy retry, or race-specific handling.

## State, Dependencies, and Risks
State and effects are exactly `os.RemoveAll`. The risk is behavioral divergence from Unix: missing-path handling and transient filesystem races depend entirely on Go's Windows removal behavior. Shared non-Darwin tests cover missing path/file/dir removal, but Windows-specific busy or locked-file behavior is not tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/containerfs/rm_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory.go -->
# sources/cloud-native/moby/daemon/internal/directory/directory.go

## Purpose
Exposes a platform-neutral directory size API.

## APIs, Control Flow, and Integration
`Size(ctx, dir)` delegates to platform-specific `calcSize`. The public contract is to walk a tree and return total file bytes while honoring cancellation and platform-specific filesystem semantics.

## State, Dependencies, and Risks
No state is kept. The behavior is entirely determined by `directory_unix.go` or `directory_windows.go`. Callers must pass a context and handle errors for nonexistent roots. Tests in `directory_test.go` exercise the exported function rather than platform implementations directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_test.go -->
# sources/cloud-native/moby/daemon/internal/directory/directory_test.go

## Purpose
Tests exported directory size behavior.

## APIs, Control Flow, and Integration
The suite creates temp dirs/files and verifies empty dirs, empty files, 5-byte files, empty nested dirs, file plus empty nested dir, file plus nonempty nested file, and nonexistent root errors. It calls `Size(context.Background(), ...)` in all cases.

## State, Dependencies, and Risks
State is temporary filesystem content. Tests validate file byte summation and error propagation, but not context cancellation, hard-link de-duplication on Unix, disappearing child paths during walk, or Windows-specific hard-link double counting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_unix.go -->
# sources/cloud-native/moby/daemon/internal/directory/directory_unix.go

## Purpose
Implements Unix directory size calculation for Linux, FreeBSD, and Darwin.

## APIs, Control Flow, and Integration
`calcSize` walks the path with `filepath.Walk`, ignores vanished non-root entries, checks context cancellation on each visited file, ignores directories and zero-byte files, and sums file sizes. It tracks inode numbers from `syscall.Stat_t` to avoid counting hard-linked content multiple times.

## State, Dependencies, and Risks
State is a map of visited inode numbers. Risks include assuming `Sys()` is `*syscall.Stat_t`, inode-only de-duplication without device ID, and `filepath.Walk` behavior on permission errors. Tests cover basic size cases through `Size`; hard links and cancellation are untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_windows.go -->
# sources/cloud-native/moby/daemon/internal/directory/directory_windows.go

## Purpose
Implements Windows directory size calculation.

## APIs, Control Flow, and Integration
`calcSize` uses `filepath.Walk`, ignores disappeared non-root entries, honors context cancellation, skips nil infos, directories, and zero-byte files, and sums sizes of all visited files.

## State, Dependencies, and Risks
No de-duplication state is maintained, so hard links/reparse semantics may count differently than Unix. The implementation depends on Go walk behavior and Windows filesystem errors. Shared tests validate basic totals and nonexistent root errors but not cancellation, symlinks, or locked files.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/directory/directory_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/config.go -->
# sources/cloud-native/moby/daemon/internal/distribution/config.go

## Purpose
Defines distribution pull/push configuration and adapters from Moby image/layer stores to registry-oriented interfaces.

## APIs, Control Flow, and Integration
`Config` holds auth, progress, registry resolver, event logger, metadata, image, and reference stores. `ImagePullConfig` adds download manager, accepted schema2 config types, and platform. `ImagePushConfig` adds config media type, layer provider, and upload manager. `ImageConfigStore` wraps image config put/get; `PushLayerProvider` and `PushLayer` abstract layer access. `rootFSFromConfig` and `platformFromConfig` parse image JSON, validate OS, and default empty OS to host. Store-layer adapters expose tar stream, size, media type, parent chain, release, and optional distribution descriptor.

## State, Dependencies, and Risks
State lives in image store, layer store, refstore, and metadata store. Risks include platform defaulting to host for missing OS, only uncompressed tar support from layer store, and release ownership across parent adapters. This file is central to pull/push integration but tested indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/errors.go -->
# sources/cloud-native/moby/daemon/internal/distribution/errors.go

## Purpose
Normalizes registry/pull/push errors into daemon error classes and controls retry/fallback behavior.

## APIs, Control Flow, and Integration
`fallbackError` marks endpoint fallback eligibility and TLS transport success. `notFoundError`, `unsupportedMediaTypeError`, AI model, invalid manifest class/format, reserved name, and invalid argument types implement daemon error interfaces. `translatePullError` maps registry errcodes to not-found/unauthorized/unknown. `continueOnError` decides endpoint fallback, especially for mirrors and transport errors. `retryOnError` wraps non-retryable transfer failures in `xfer.DoNotRetry`. `DeprecatedSchema1ImageError` emits the removal message.

## State, Dependencies, and Risks
No persistence. Risks include string matching `ESRCH`/`ENOSPC`, taking first error from `errcode.Errors`, and nuanced differences between retry and endpoint fallback. Tests focus on `continueOnError`; most translation behavior is integration-tested through pull/push.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/errors_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/errors_test.go

## Purpose
Tests endpoint fallback decisions for distribution errors.

## APIs, Control Flow, and Integration
The tests define errors that should always continue, only continue from mirror endpoints, and never continue. They run `continueOnError` with mirror and non-mirror settings to verify unauthorized/name-unknown behavior, unexpected HTTP response fallback, image config pull fallback, unsupported media type blocking, cancellation/deadline blocking, and unexpected error fallback.

## State, Dependencies, and Risks
No external state. Coverage is intentionally narrow to fallback control. It does not verify `translatePullError`, `retryOnError`, or daemon error interface markers beyond their effect on fallback decisions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/manifest.go -->
# sources/cloud-native/moby/daemon/internal/distribution/manifest.go

## Purpose
Caches registry manifests in a containerd content store and validates/detects manifest media types for pull-by-digest and local reuse.

## APIs, Control Flow, and Integration
`ContentStore` narrows containerd ingest/provider/update APIs. `manifestStore.Get` detects missing descriptor media type, opens a writer to retain/write content, returns cached local manifests when possible, otherwise fetches remote and persists via `Put`. `getLocal` verifies distribution-source labels for canonical refs, optionally checks remote existence, updates source labels, reads content, and unmarshals the manifest. Helpers manage sorted deduplicated `containerd.io/distribution.source.<domain>` labels. `detectManifestBlobMediaType` infers or validates Docker/OCI schema2/list/index/schema1 shapes.

## State, Dependencies, and Risks
State persists in containerd content blobs, active ingests, and content labels. Risks include serving cached digest content only after source verification, best-effort label update failures, ingest abort complexity, and strict media-type structural validation. Tests cover cache/no-cache, unknown media type, persistence failures, and detection invalid cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/manifest_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/manifest_test.go

## Purpose
Validates manifest content-store caching, fallback to remote, ingest cleanup, and media-type detection.

## APIs, Control Flow, and Integration
`TestManifestStore` uses a local labeled content store and mock remote manifest getter. It covers no local/remote, remote fetch and cache, cached reuse without remote calls, digested refs, unknown media type with and without cache, writer/commit errors that should not block remote result, and no active ingest left behind. Detection tests cover mediaType precedence, OCI manifest/index inference, schema1 deprecation, and invalid field combinations.

## State, Dependencies, and Risks
State is temporary content store data and labels. Tests strongly document content-cache semantics, but they do not cover concurrent pulls or remote existence failures for canonical refs without matching source labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/metadata.go -->
# sources/cloud-native/moby/daemon/internal/distribution/metadata/metadata.go

## Purpose
Provides a filesystem-backed key/value store for distribution metadata.

## APIs, Control Flow, and Integration
`Store` exposes `Get`, `Set`, and `Delete` by namespace/key. `FSMetadataStore` creates the base path, protects operations with an RW mutex, maps namespace/key to nested paths, reads files, atomically writes values after creating parent directories, and removes files.

## State, Dependencies, and Risks
Persistence is under the configured base path with namespace directories and key paths, using 0700 base, 0755 namespace dirs, and 0644 files. Risks include unsanitized keys creating nested paths, delete errors for missing files, and process-local locking only. It is used by v2 metadata service for layer digest/diffID mappings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service.go -->
# sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service.go

## Purpose
Maintains Docker Registry v2 layer metadata mapping uncompressed DiffIDs to compressed blob digests/source repositories, including credential-scoped HMAC tags.

## APIs, Control Flow, and Integration
`V2MetadataService` supports metadata lookup by DiffID, DiffID lookup by digest, add, HMAC tag-and-add, and remove. `V2Metadata` stores digest, source repo, and HMAC. HMAC helpers derive a key from selected auth fields and hash digest+source repository. `Add` deduplicates entries, appends newest, caps per DiffID to 50, stores JSON under `v2metadata-by-diffid`, and stores reverse digest mapping. `Remove` uses reverse mapping, removes matching metadata, and deletes the DiffID record if empty.

## State, Dependencies, and Risks
Persistence uses the metadata store. A nil store makes add/remove no-ops but read operations error. Risks include reverse digest mapping pointing to only the latest DiffID, remove failing if reverse mapping is missing, HMAC compatibility with auth-field changes, and stale metadata influencing push mount/existence behavior. Tests cover add/get/capping/reverse overwrite.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service_test.go

## Purpose
Tests filesystem-backed v2 distribution metadata mapping behavior.

## APIs, Control Flow, and Integration
`TestV2MetadataService` creates an `FSMetadataStore`, adds metadata entries for several DiffIDs including 100 entries for capping, verifies returned metadata equals the newest 50 where applicable, expects errors for nonexistent DiffID/digest lookups, then overwrites a digest mapping and confirms `GetDiffID` returns the latest DiffID.

## State, Dependencies, and Risks
State is temporary on-disk metadata. Tests cover the main persistence contract but not HMAC computation/checking, remove semantics, nil-store behavior, malformed JSON, or concurrent access. `randomDigest` uses pseudo-random bytes for test data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/metadata/v2_metadata_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull.go -->
# sources/cloud-native/moby/daemon/internal/distribution/pull.go

## Purpose
Provides top-level pull and tag listing orchestration across registry endpoints.

## APIs, Control Flow, and Integration
`Pull` resolves endpoints through `pullEndpoints`, constructs a v2 puller for each candidate, and logs a pull event on success. `Tags` reuses endpoint fallback to list remote tags. `validateRepoName` rejects `scratch`. `addDigestReference` adds immutable digest references without updating changed digest IDs. `pullEndpoints` trims refs, looks up pull endpoints, skips plaintext endpoints after confirmed TLS, invokes the callback, unwraps fallback errors, records last error, and translates final failures.

## State, Dependencies, and Risks
State updates reference store digest refs and emits events. Risks include endpoint fallback subtlety, `scratch` reservation, unchanged digest refs not updated if image ID differs, and TLS/plaintext skip behavior. Pull-specific error translation lives in `errors.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2.go -->
# sources/cloud-native/moby/daemon/internal/distribution/pull_v2.go

## Purpose
Implements Docker Registry v2 image pull: manifest resolution, platform selection, config/layer download, verification, metadata recording, image-store insertion, and refstore updates.

## APIs, Control Flow, and Integration
`newPuller` wires endpoint, repo name, config, metadata service, and manifest store. `pull` creates an authenticated repository and manifest service. `pullRepository` pulls a specific ref or all tags. `pullTag` resolves tag/digest to manifest, validates config media type, dispatches schema2/OCI/manifest-list handling, writes digest status, and updates tag/digest references. `pullSchema2Layers` skips existing images, validates media types, builds `layerDescriptor`s, concurrently pulls image config and layers, checks Windows compatibility early, verifies downloaded DiffIDs match config rootfs, and stores image config. `layerDescriptor.Download` supports temp-file resume, byte-range retry, digest verification, and metadata registration.

## State, Dependencies, and Risks
State spans temp files, layer store via download manager, image store configs, refstore tags/digests, content-store manifest cache, and v2 metadata. Risks include concurrent config/layer race handling, rootfs mismatch security, AI/unsupported media type blocking, digest verification, temp-file cleanup, and manifest-list recursion/no-match handling. Tests cover no-match messages and config retry/auth behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_test.go

## Purpose
Tests selected Registry v2 pull helpers.

## APIs, Control Flow, and Integration
`TestNoMatchesErr` validates platform formatting for default host platform and explicit Windows/arm64/v8 platform. `TestPullSchema2Config` starts an HTTP registry-like test server and verifies config blob fetch retry behavior: immediate success, one 500 then success, EOF/panic then success, and unauthorized responses that should not retry. `testNewPuller` builds a token-authenticated puller against the test server.

## State, Dependencies, and Risks
State is an in-process HTTP server and atomic request counter. Tests validate digest-verifying config fetch and retry classification, but not layer downloads, manifest list platform matching, refstore updates, rootfs mismatch, or temp-file resume.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_unix.go -->
# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_unix.go

## Purpose
Provides non-Windows pull helpers for blob opening, manifest-list platform filtering, and compatibility checks.

## APIs, Control Flow, and Integration
`layerDescriptor.open` reads blobs from the registry blob store. `filterManifests` defaults the requested platform, normalizes it, includes descriptors with nil platform or matching platforms, logs matches, and stable-sorts matches by platform preference. `checkImageCompatibility` is a no-op. `withDefault` fills missing OS/architecture/variant from `maximumSpec`.

## State, Dependencies, and Risks
No persistence. Risks include accepting nil-platform descriptors broadly and platform defaulting choosing host maximum compatibility. This file's behavior controls which manifest-list entry is pulled on Linux/Unix. Coverage is indirect; no dedicated tests in this subset validate sorting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_windows.go -->
# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_windows.go

## Purpose
Implements Windows-specific v2 pull behavior for foreign layers and Windows image compatibility.

## APIs, Control Flow, and Integration
`Descriptor` exposes foreign layer descriptors when URL-backed. `open` tries registry blob access first, then foreign URLs via HTTP read seeker. `filterManifests` filters by architecture, requested/host OS validity, Windows compatibility, logs skipped/matched entries, and sorts compatible Windows versions before others. `versionMatch` matches version prefix up to build. `checkImageCompatibility` rejects Windows images with build numbers newer than the host.

## State, Dependencies, and Risks
State is host OS version and network access to foreign URLs. Risks include foreign URL trust/availability, version parsing leniency, only architecture matching host GOARCH, and sorting that prefers compatible versions without full numeric ordering. Tests are indirect; Windows behavior is hard to cover cross-platform.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/pull_v2_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push.go -->
# sources/cloud-native/moby/daemon/internal/distribution/push.go

## Purpose
Provides top-level image push orchestration and gzip compression helper.

## APIs, Control Flow, and Integration
`Push` trims the reference, looks up push endpoints, emits progress, verifies local references exist, iterates endpoints with TLS/plaintext fallback rules, invokes a v2 pusher, logs push events on success, and returns the last endpoint error when all fail. `compress` streams gzip-compressed data through a pipe with buffered writes and returns a completion channel so callers can wait before releasing the input.

## State, Dependencies, and Risks
State updates are delegated to pusher/refstore and event logger. Risks include requiring `ReferenceStore`, no digest-reference push, endpoint fallback complexity, and goroutine/pipe error propagation in compression. Tests for top-level push are indirect; push_v2 tests cover lower-level metadata behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push_v2.go -->
# sources/cloud-native/moby/daemon/internal/distribution/push_v2.go

## Purpose
Implements Registry v2 image push: layer upload/mount/existence checks, manifest creation, metadata updates, and refstore digest recording.

## APIs, Control Flow, and Integration
`newPusher` wires metadata, refs, endpoint, and config. `push` creates a push/pull-capable repository and records whether auth info exists. `pushRepository` pushes one tag or all tags. `pushTag` loads image config/rootfs, resolves top layer, computes auth HMAC key, creates reverse-order `pushDescriptor`s, uploads layers via upload manager, builds schema2 manifest, pushes it with tag, emits digest progress/aux, and records digest ref. `pushDescriptor.Upload` checks shared remote layer state, consults v2 metadata, attempts cross-repo mounts, performs existence checks by layer size policy, uploads/compresses as needed, and records HMAC-tagged metadata.

## State, Dependencies, and Risks
State spans remote registry blobs/manifests, Moby layer store, image store, refstore, upload manager, and v2 metadata. Risks include stale metadata removal heuristics, auth-sensitive mount candidate cleanup, dedupe map locking, upload cancellation, unsupported layer media types, and schema2-only manifest creation. Tests heavily cover mount candidate sorting, existence checks, metadata add/remove, and auth-info cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push_v2_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/push_v2_test.go

## Purpose
Tests v2 push layer metadata selection, existence checks, and auth-sensitive cleanup behavior.

## APIs, Control Flow, and Integration
`TestGetRepositoryMountCandidates` verifies same-registry filtering, target repo exclusion, Docker Hub normalization, HMAC preference, path-component likeness sorting, recency ordering, and max-candidate truncation. `TestLayerAlreadyExists` table-tests metadata filtering, remote stat order, unknown blob cleanup, access-denied tolerance, existing descriptor normalization, duplicate digest checks, and max attempts. `TestWhenEmptyAuthConfig` verifies `hasAuthInfo`. `TestPushRegistryWhenAuthInfoEmpty` ensures unauthorized mount create does not remove metadata when unauthenticated.

## State, Dependencies, and Risks
Tests use mock repos/blob stores/metadata services and progress sink. They exercise the trickiest metadata logic but do not perform real uploads, manifest pushes, compression, or endpoint fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/push_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/registry.go -->
# sources/cloud-native/moby/daemon/internal/distribution/registry.go

## Purpose
Creates authenticated Docker distribution repository clients and defines supported media/config types.

## APIs, Control Flow, and Integration
Package vars list acceptable media-type prefixes, default image config types, plugin config types, and `mediaTypeClasses`. `newRepository` constructs an HTTP transport with proxy/TLS/timeouts, adds Docker headers and OpenTelemetry wrapping, pings `/v2/`, builds token/basic or pass-through bearer auth, creates the distribution repository with path-only remote name, and wraps setup failures in `fallbackError` with transport status. `passThruTokenHandler` injects `Authorization: Bearer`.

## State, Dependencies, and Risks
State is network transport/auth configuration. Risks include relying on ping challenge flow, token scopes matching requested actions, fallback classification on ping errors, and media-type allowlists needing updates for new artifact classes. Tests cover pass-through token host scoping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/registry_unit_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/registry_unit_test.go

## Purpose
Tests registry bearer token pass-through behavior.

## APIs, Control Flow, and Integration
The test server handler validates `Authorization` against `Bearer mysecrettoken`. `testTokenPassThru` constructs a repository endpoint using `RegistryToken` and performs a blob stat for a dummy digest. `TestTokenPassThru` expects success against the token-checking server. `TestTokenPassThruDifferentHost` changes endpoint host to another registry and expects an error.

## State, Dependencies, and Risks
State is an HTTP test server. The tests validate that registry tokens are passed to the intended registry flow and not blindly reused for a mismatched host. They do not cover username/password token exchange or TLS fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/registry_unit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/repository.go -->
# sources/cloud-native/moby/daemon/internal/distribution/repository.go

## Purpose
Returns all reachable pull repositories for a reference, including mirrors where configured.

## APIs, Control Flow, and Integration
`GetRepositories` trims and validates the name, resolves pull endpoints, creates a repository for each endpoint with pull scope, logs per-endpoint failures, collects successful repositories, and returns the last error if none were reachable. It wraps reserved-name validation as invalid parameter.

## State, Dependencies, and Risks
No persistence; it performs network pings/auth setup through `newRepository`. Risks include returning partial success silently when some endpoints fail and `lastError` being nil only if endpoint list is empty/unusual. Used by callers that need repository handles rather than full pull orchestration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/transport.go -->
# sources/cloud-native/moby/daemon/internal/distribution/transport.go

## Purpose
Builds registry HTTP transports with request modifiers and OpenTelemetry instrumentation.

## APIs, Control Flow, and Integration
`newTransport` wraps the base round tripper with Docker distribution `transport.NewTransport` to apply headers/auth modifiers, then wraps that with `otelhttp.NewTransport` so trace context is propagated.

## State, Dependencies, and Risks
No state. Risks include modifier ordering being determined by caller-provided order and observability wrapping changing transport type/behavior. This helper is used by `newRepository` for both unauthenticated ping and authenticated repository operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/transport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/utils/progress.go -->
# sources/cloud-native/moby/daemon/internal/distribution/utils/progress.go

## Purpose
Streams distribution progress messages to a JSON progress output and cancels the operation if the client writer fails.

## APIs, Control Flow, and Integration
`WriteDistributionProgress(cancelFunc, outStream, progressChan)` creates a JSON progress output, drains `progressChan`, writes each progress item, logs EPIPE as client cancellation, logs other write errors, calls `cancelFunc` once, and keeps draining until the channel closes to avoid producer deadlock.

## State, Dependencies, and Risks
State is the local `operationCancelled` guard. Risks include cancellation after first write failure while still consuming progress, and no return error to caller. Integration is API streaming for pull/push progress.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/utils/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/download.go -->
# sources/cloud-native/moby/daemon/internal/distribution/xfer/download.go

## Purpose
Manages concurrent, deduplicated layer downloads and ordered registration into the Moby layer store.

## APIs, Control Flow, and Integration
`LayerDownloadManager` owns a layer store, transfer manager, retry wait, and max attempts. `Download` walks descriptors bottom-up, skips already-present layers when DiffID is known, deduplicates repeated descriptor keys, schedules downloads with dependency-aware transfer functions, waits for the top layer, reconstructs rootfs DiffIDs, and returns a release function. `makeDownloadFunc` downloads with retry/backoff progress, waits for parent registration, decompresses content, registers with descriptor when supported, updates progress, calls `Registered`, and releases layers after watchers release. `makeDownloadFuncFromDownload` re-registers duplicate layer data atop a different parent.

## State, Dependencies, and Risks
State includes transfer manager slots/watchers, layer store references, descriptor cleanup, and rootfs chain reconstruction. Risks include complex release ownership, cancellation during retry/registration, duplicate-key re-registration semantics, and unexported `DoNotRetry` behavior from transfer package. Tests cover success, cancellation, concurrency, dedupe, and max attempts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/download.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/download_test.go -->
# sources/cloud-native/moby/daemon/internal/distribution/xfer/download_test.go

## Purpose
Tests the layer download manager's success path, cancellation, concurrency guard, deduplication, and retry limits.

## APIs, Control Flow, and Integration
Mocks implement `layer.Layer`, `layer.Store`, and `DownloadDescriptor`. `TestSuccessfulDownload` pre-registers the first layer, downloads a descriptor set with a duplicate key and one retrying descriptor, verifies progress states, rootfs DiffIDs, and `Registered` callbacks. `TestCancelledDownload` cancels context shortly after start and expects `context.Canceled`. `TestMaxDownloadAttempts` table-tests success/failure based on simulated retry count and configured max attempts.

## State, Dependencies, and Risks
State is an in-memory mock layer store and progress channel. The success test skips on Windows. Tests do not cover descriptor `Close` ordering, `DoNotRetry`, describable layer registration, or parent failure propagation in every branch.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/distribution/xfer/download_test.go -->
