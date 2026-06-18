# Research Report: subset-b-000274

This grouped report covers the requested SOCI snapshotter service, snapshot, SOCI artifact/index, Docker shell, IO utility, and LRU cache files. Each section is source-tree-aligned and bounded for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/registry.go -->
# sources/cloud-native/soci-snapshotter/service/resolver/registry.go

Purpose: this file builds registry host resolution for remote image access. It adapts SOCI snapshotter resolver configuration, retryable HTTP behavior, registry mirrors, and credential providers into containerd `docker.RegistryHost` values used by source label resolution and filesystem pulls.

Important APIs and types: `Credential` resolves username/secret for an image reference and host; `RegistryHosts` returns containerd registry hosts for an image reference; `RegistryManager` owns the retry client, global headers, resolver config, credential providers, and a `sync.Map` cache keyed by `reference.Spec.String()`. `NewRegistryManager` wires retry and header defaults. `AsRegistryHosts` returns the closure consumed by containerd remote resolver code. `multiCredsFuncs` chains credential providers in order and stops at the first non-empty credential. `DefaultScheme` forces HTTP for localhost and HTTPS elsewhere.

Control flow: `AsRegistryHosts` first checks the per-image cache. On a miss, it creates a per-image auth client with `multiCredsFuncs`, expands any configured mirrors for `imgRefSpec.Hostname()`, then appends the canonical upstream host. Mirror URLs are parsed, normalized through `docker.DefaultHost`, and default to `/v2` if no path is provided. Mirror `Insecure` changes scheme to HTTP. Per-mirror request timeouts clone the retryable client and auth client while reusing the global transport.

State and persistence: state is in-memory only. The cache can retain registry host configurations for the life of the process. Because credentials can be image/repository scoped, the auth client is intentionally created per image reference, not globally per host.

Dependencies and integration points: depends on `config.ResolverConfig`, HashiCorp retryablehttp, containerd `remotes/docker`, and local auth helpers in the resolver package. It is used by `service.NewSociSnapshotterService` through `source.RegistryHosts`.

Risks: `int64(retryClient.HTTPClient.Timeout)` compares a nanosecond duration to a configured seconds value, so timeout equality detection is suspicious and may clone more often than intended. Cached `RegistryHost` slices may also freeze credential-provider behavior for an image reference if provider semantics or resolver config are changed at runtime. Mirror URL parsing trusts `url.Host`; malformed mirror strings without a scheme may produce empty hosts.

Test signals: this file has no direct test in the requested set, but resolver behavior is likely covered by neighboring resolver tests. Important test gaps are mirror timeout handling, per-image credential scoping, and invalid mirror URL forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/service.go -->
# sources/cloud-native/soci-snapshotter/service/service.go

Purpose: this file is the service-level constructor for the SOCI snapshotter. It converts `config.ServiceConfig` and optional dependency injection into a configured filesystem plus snapshotter implementation.

Important APIs and types: `Option` mutates private `options`. `WithCredsFuncs` adds registry credential providers. `WithCustomRegistryHosts` allows a caller to override registry resolution entirely. `WithFilesystemOptions` passes lower-level filesystem options through to `fs.NewFilesystem`. `NewSociSnapshotterService` is the main constructor. `Supported` delegates host capability checks to overlay snapshotter support. `snapshotterRoot` and `fsRoot` define the root subdirectories.

Control flow: constructor options are applied first. If registry hosts are not supplied, it constructs a `resolver.RegistryManager` from retry and resolver config. It detects whether overlay should use `userxattr`, then maps that to SOCI layer opaque-marker handling. It builds source resolution from default labels plus registry hosts and appends filesystem options for source lookup, overlay opaque type, pull modes, and optional max concurrency. After `socifs.NewFilesystem`, it builds snapshotter options: asynchronous remove by default, optional min layer size, restart invalid-mount tolerance, parallel pull, and experimental parallel-pull-as-fallback. Finally it calls `snapshot.NewSnapshotter`.

State and persistence: service state is delegated to filesystem root `<root>/soci` and snapshotter root `<root>/snapshotter`. The service itself persists no additional data.

Dependencies and integration points: integrates config, resolver, `fs`, `fs/layer`, `fs/source`, `snapshot`, and containerd overlay utilities. The resulting value implements containerd `snapshots.Snapshotter` and is intended to be registered by the daemon plugin.

Risks: constructor errors from filesystem or snapshotter creation are logged with `Fatalf`, which exits the process rather than returning an error in those cases. The warning for experimental parallel fallback correctly surfaces GC edge cases when lazy-load and parallel-pull share a content store. User xattr detection failures continue with the default boolean value, so mount behavior depends on overlayutils defaults.

Test signals: no direct test in this subset. Behavior is indirectly exercised by snapshot and filesystem tests. Constructor-level tests would be useful for option propagation, fatal paths, and root path derivation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/snapshot/snapshot.go -->
# sources/cloud-native/soci-snapshotter/snapshot/snapshot.go

Purpose: this is the core containerd snapshotter implementation. It extends overlayfs snapshot behavior with remote SOCI lazy mounts, local and parallel pull fallbacks, restart restoration, idmapped mounts, and cleanup of snapshot directories.

Important APIs and types: exported errors distinguish `ErrNoIndex`, `ErrNoZtoc`, `ErrDeferToContainerRuntime`, and `ErrNoNamespace`. `FileSystem` is the backing abstraction with remote `Mount`/`Check`/`Unmount`, local `MountLocal`, parallel `MountParallel`, idmap mount creation, and image cleanup. `SnapshotterConfig` and options configure async remove, min layer size, invalid restart mounts, parallel pull/unpack, and fallback mode. `NewSnapshotter` creates metadata DB, validates d_type support, detects `userxattr`, and restores remote mounts.

Control flow: standard snapshotter methods use containerd `storage.MetaStore` transactions. `Prepare` creates an active snapshot. Without the target snapshot label, it behaves like overlayfs and may set up idmapped parent mounts. With the target label, it records namespace labels, attempts remote mount unless skipped by parallel pull or min layer size, commits successful remote snapshots internally, and returns `ErrAlreadyExists` to signal that the target snapshot is already committed. On `ErrNoIndex`, it either defers to container runtime or uses parallel-pull fallback. On `ErrNoZtoc`, it falls back to local layer materialization. Local or parallel success is committed as a non-remote target. `Mounts` and `View` return bind mounts for single-layer/no-parent cases and overlay mounts for layered cases.

State and persistence: metadata lives in `<root>/metadata.db`; snapshot directories live under `<root>/snapshots/<id>/fs` and optional `work`. Remote snapshots are marked with `containerd.io/snapshot/remote`; SOCI-backed snapshots get source labels including namespace and index presence. `idmapped` is process-local and affects generated parent paths. Async removal leaves directories for later `Cleanup`.

Dependencies and integration points: integrates containerd mount/snapshots/storage/namespaces/snapshotters labels, overlayutils, continuity disk usage, mountinfo, idtools, SOCI `fs/source` labels, and common metrics.

Risks: `Remove` calls `fs.CleanImage` with the manifest digest label after committing metadata removal; if that cleanup fails, the snapshot is already gone. `restoreRemoteSnapshot` force-unmounts any mount under the snapshot root at startup, so incorrect root configuration has high blast radius. Concurrent zTOC or filesystem failures are surfaced through fallback semantics that depend on exact sentinel errors. The `idmapped` map is not persisted, so restart behavior for idmapped derived paths needs care. `allowInvalidMountsOnRestart` can leave unusable committed snapshots that require manual cleanup.

Test signals: `snapshot_test.go` covers remote prepare/commit/overlay behavior, availability checks across remote layer chains, and overlay compatibility. The containerd snapshotter suite is reused for baseline overlay semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/snapshot/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/snapshot/snapshot_test.go -->
# sources/cloud-native/soci-snapshotter/snapshot/snapshot_test.go

Purpose: this file verifies the snapshotter's remote-layer behavior and its compatibility with overlayfs snapshotter expectations.

Important APIs and helpers: `prepareWithTarget` simulates containerd prepare requests carrying `containerd.io/snapshot.ref`; it expects the snapshotter to internally commit and return an already-exists error. `bindFs` is a test `FileSystem` that bind-mounts a temporary directory into snapshot mountpoints and can mark mountpoints as broken. `dummyFs` makes normal overlay tests independent of remote filesystem behavior. `getBasePath` and `getParents` inspect snapshot metadata to build expected paths.

Control flow: remote tests require root because they perform real mount operations. `TestRemotePrepare` confirms a target-labeled prepare creates a committed remote snapshot with the right labels. `TestRemoteOverlay` checks active overlay mounts built on a remote parent include workdir, upperdir, and lowerdir pointing into the snapshot tree. `TestRemoteCommit` writes through an overlay mount and verifies commit/readback. `TestFailureDetection` builds chains of remote layers and optional overlay layers, toggles the fake filesystem's check failures, and validates `Prepare`/`Mounts` return unavailable errors for broken remote ancestors.

State and persistence behavior tested: tests create real metadata DBs and snapshot directories in `t.TempDir()`. Remote bind mounts are unmounted during cleanup. `bindFs.broken` tracks per-mountpoint failure state in memory.

Dependencies and integration points: uses containerd snapshot testsuite, namespaces, mount helpers, overlayutils, and errdefs. The tests exercise the public `snapshots.Snapshotter` interface rather than private methods where possible.

Risks and gaps: the root-required tests are likely skipped or unavailable in unprivileged CI. There are no tests in this file for parallel pull fallback, min-layer-size skip, `ErrNoIndex` deferral, restart restoration, invalid restart mount tolerance, or idmapped mount behavior. `TestOverlayView` mutates a lower path directly instead of mounting the active top layer, which checks mount composition but not full copy-up behavior.

Test signal quality: strong for basic remote and overlay compatibility paths; weaker for newer fallback modes and restart recovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/snapshot/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci-snapshotter.service -->
# sources/cloud-native/soci-snapshotter/soci-snapshotter.service

Purpose: this systemd unit starts the SOCI snapshotter gRPC daemon as a containerd-adjacent service.

Important fields: `[Unit]` describes the service, links documentation, starts after `network.target`, and orders before `containerd.service` so containerd can connect to the snapshotter. `[Service]` uses `Type=notify`, executes `/usr/local/bin/soci-snapshotter-grpc --address fd://`, and restarts on failure with a five-second delay. `[Install]` enables it for `multi-user.target`.

Control flow and integration: the `fd://` address implies socket activation from the paired `soci-snapshotter.socket`. With socket activation, systemd owns the Unix socket and passes the file descriptor to the daemon. The ordering before containerd matters because containerd snapshotter plugin configuration expects the socket to be available early.

State and persistence: no direct persistent state is configured here. Runtime state is owned by the daemon's configured root and systemd restart state.

Dependencies: depends on systemd notify support in the daemon and the matching socket unit. It indirectly depends on `/usr/local/bin/soci-snapshotter-grpc` existing and having required privileges for mounts and content operations.

Risks: the service file has no explicit `Requires=` or `Also=` relationship to the socket, so packaging/install configuration must ensure both units are installed and enabled as intended. It also has no hardening settings, environment file, or explicit user, which may be deliberate because snapshotter mount operations need privileges but should be reviewed by packagers.

Test signals: no tests in this subset validate unit installation or socket activation. Manual or integration tests should verify `systemctl enable --now soci-snapshotter.socket` and containerd startup ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci-snapshotter.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci-snapshotter.socket -->
# sources/cloud-native/soci-snapshotter/soci-snapshotter.socket

Purpose: this systemd socket unit defines the Unix socket used to activate and connect to the SOCI snapshotter gRPC daemon.

Important fields: `[Socket]` listens on `/run/soci-snapshotter-grpc/soci-snapshotter-grpc.sock` and sets `SocketMode=0660`. `[Install]` enables it under `sockets.target`.

Control flow and integration: when a client connects to the socket, systemd can activate the matching service, which uses `--address fd://` to receive the socket descriptor. Containerd configuration must point to the same path for the proxy snapshotter.

State and persistence: the socket path is under `/run`, so it is runtime-only. Permissions allow owner/group read-write access; group ownership is not specified here and will be determined by systemd defaults or packaging overrides.

Dependencies: paired with `soci-snapshotter.service` by systemd naming conventions. Requires systemd socket activation support in the daemon.

Risks: lack of explicit `SocketUser`/`SocketGroup` means access control depends on unit manager defaults. Containerd must have permission to connect to the socket. The unit itself does not create persistent directories; systemd normally manages runtime socket parent creation, but packaging should verify the path.

Test signals: no direct tests in this subset. Operational validation should check socket creation, mode, daemon activation, and containerd access.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci-snapshotter.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/artifacts.go -->
# sources/cloud-native/soci-snapshotter/soci/artifacts.go

Purpose: this file manages the BoltDB metadata index for local SOCI artifacts. It records SOCI index manifests, zTOC layer artifacts, and prefetch artifacts so CLI and daemon flows can discover, push, clean, and relate artifacts to images and layers.

Important APIs and types: `ArtifactsDb` wraps `*bolt.DB`. `ArtifactEntry` stores size, digest, original content digest, image digest, platform, location, entry type, media type, artifact type, creation time, and span size. `ArtifactsDbPath` resolves the default DB path. `NewDB` initializes a package-level singleton. Public methods include `Walk`, `SyncWithLocalStore`, `RemoveOldArtifacts`, `GetArtifactEntry`, `GetArtifactType`, `RemoveArtifactEntryByIndexDigest`, `GetArtifactEntriesByImageDigest`, and `WriteArtifactEntry`.

Control flow: `SyncWithLocalStore` removes DB entries whose descriptors no longer exist in the blob store, then scans the local content store path for new SOCI index blobs. `addNewArtifacts` walks files, ignores tiny/config-like content, decodes candidate indexes, verifies media/artifact/subject fields, derives platform from the containerd content store, writes an index entry, and writes zTOC entries from the index blobs. `WriteArtifactEntry` creates per-digest buckets under `soci_artifacts`; `loadArtifact` reverses that encoding.

State and persistence: BoltDB schema is bucket-oriented: root `soci_artifacts`, child bucket per artifact digest, scalar keys for encoded size/span size, digests, platform, location, type, media type, artifact type, and creation time. Integer fields use varint encoding from `util/dbutil`.

Dependencies and integration points: integrates config defaults, SOCI `store.Store`, containerd content/images/platforms, OCI descriptors, bbolt, errdefs, and `soci_index.go` serialization.

Risks: `NewDB` is a package-level `sync.Once` singleton, so tests and multi-root callers must reset or cannot open different DBs in one process. `Walk` suppresses missing root bucket errors by returning nil, which makes an absent DB look empty. `addNewArtifacts` guesses digest algorithm by filename length, assumes `images.Platforms` returns at least one platform, and silently ignores decode failures. `RemoveOldArtifacts` queues bucket deletion to avoid Bolt iteration mutation hazards.

Test signals: `artifacts_test.go` covers path derivation, singleton failure behavior, read/write round trips, atomic bucket helper operations, and index-entry filtering by original digest.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/artifacts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/artifacts_test.go -->
# sources/cloud-native/soci-snapshotter/soci/artifacts_test.go

Purpose: this file tests the BoltDB artifact metadata helpers used by SOCI index and zTOC management.

Important APIs and helpers: `newTestableDb` creates a temporary bbolt DB with the `soci_artifacts` bucket and returns an `ArtifactsDb` wrapper. `resetArtifactDBInit` resets package-level `once` and `db` to make singleton initialization testable. Tests use realistic sha256 digest strings and `ArtifactEntry` structs.

Control flow: `TestGetIndexArtifactEntries` writes multiple index and layer entries and verifies filtering by `OriginalDigest` returns only index entries for the requested digest. `TestArtifactDbPath` checks default and custom root path behavior. `TestArtifactDB_DoesNotExist` forces singleton initialization failure and confirms `NewDB` reports unavailable DB. `TestArtifactEntry_ReadWrite_Using_ArtifactsDb` writes through the public API and reads back through `GetArtifactEntry`. `TestArtifactEntry_ReadWrite_AtomicDbOperations` exercises lower-level transaction helpers directly.

State and persistence behavior tested: tests create real temporary bbolt files, initialize the root bucket, and verify varint-encoded fields and string fields round-trip through bucket storage. They also demonstrate the global singleton must be reset to isolate tests.

Dependencies and integration points: tests use bbolt directly and validate helpers consumed by `soci_index.go` and `artifacts.go`.

Risks and gaps: no tests cover `SyncWithLocalStore`, `RemoveOldArtifacts`, `addNewArtifacts`, prefetch entries, `CreatedAt` binary encoding with non-zero times, image-digest reverse lookup, or removal by index digest. Ordering in `getIndexArtifactEntries` depends on Bolt bucket iteration order; current fixture order matches lexicographic digest order.

Test signal quality: good for core read/write and filtering helpers, limited for content-store synchronization and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/artifacts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/fs.go -->
# sources/cloud-native/soci-snapshotter/soci/fs.go

Purpose: this small helper ensures the SOCI snapshotter root directory exists with restricted permissions before ORAS/local content-store code can create it with broader defaults.

Important API: `EnsureSnapshotterRootPath(root string) error` substitutes `config.DefaultSociSnapshotterRootPath` when root is empty, stats the path, creates it with mode `0700` if missing, and returns any stat or mkdir errors.

Control flow: the function distinguishes non-existence via `os.IsNotExist`, creates only the final root component, and treats an existing path as success. It does not call `MkdirAll`, so parent directories must exist.

State and persistence: it creates a filesystem directory and does not otherwise persist metadata. The comment says restricted permissions `0711`, but the actual mode is `0700`; the implementation is the source of truth.

Dependencies and integration points: depends on `config.DefaultSociSnapshotterRootPath`. It is relevant before initializing SOCI content stores or artifact DBs under the snapshotter root.

Risks: parent directory absence returns an error. Existing directories with broad permissions are accepted and not tightened. The comment-mode mismatch may confuse hardening reviews.

Test signals: `fs_test.go` covers missing and existing custom roots but not default root substitution, parent-missing failure, or permission assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/fs_test.go -->
# sources/cloud-native/soci-snapshotter/soci/fs_test.go

Purpose: this file tests root-directory creation behavior for SOCI filesystem setup.

Important tests: `TestEnsureSnapshotterRootPath` has two subtests. The first creates a parent `var/lib`, calls `EnsureSnapshotterRootPath` for a missing `soci-snapshotter-grpc` child, and verifies the child exists. The second pre-creates the root and verifies the function returns success and leaves it present.

Control flow and state: tests use `t.TempDir()` for isolation and real filesystem operations through `os.MkdirAll` and `os.Stat`. They validate existence only.

Dependencies and integration points: exercises `soci/fs.go` and indirectly documents that callers need parent directories to exist when passing a nested custom root.

Risks and gaps: no assertion checks the intended mode, so the comment claiming `0711` versus implementation `0700` is not caught. There is no test for empty root/default path, inaccessible parent, existing file instead of directory, or permission preservation on existing directories.

Test signal quality: narrow but useful for the basic create/no-op cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/prefetch.go -->
# sources/cloud-native/soci-snapshotter/soci/prefetch.go

Purpose: this file defines the JSON artifact format used to describe compressed spans that should be prefetched for a layer.

Important APIs and types: constants define media type `application/vnd.amazon.soci.prefetch.v1+json` and version `1.0`. `ErrEmptyPrefetchArtifact` rejects nil or empty artifacts. `PrefetchArtifact` contains version and a slice of `PrefetchSpan`. `PrefetchSpan` stores start/end `compression.SpanID` and optional future priority. `NewPrefetchArtifact`, `AddPrefetchSpan`, and `IsEmpty` manage the in-memory value. `MarshalPrefetchArtifact` returns an `io.Reader` plus OCI descriptor with digest and size. `UnmarshalPrefetchArtifact` validates JSON, version, and non-empty content.

Control flow: marshal rejects nil/empty artifacts, JSON encodes, computes digest from bytes, and returns a descriptor with the prefetch media type. Unmarshal reads all data, JSON decodes, verifies exact version, rejects empty span lists, and returns the artifact.

State and persistence: persisted form is a small JSON blob stored in a content store. Descriptor digest is content-addressed from the JSON representation. No internal mutable global state exists.

Dependencies and integration points: used by `soci_index.go` to create prefetch descriptors and artifact DB entries. It depends on zTOC compression span IDs and OCI descriptors.

Risks: no semantic validation ensures start span is less than or equal to end span or that priorities are non-negative. JSON ordering is stable for structs but any future map fields could affect digest expectations. Unmarshal reads the full reader into memory, acceptable for small artifacts.

Test signals: `prefetch_test.go` covers constructor, add/is-empty, marshal nil/empty rejection, successful marshal, successful unmarshal, invalid JSON, and unsupported version.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/prefetch_test.go -->
# sources/cloud-native/soci-snapshotter/soci/prefetch_test.go

Purpose: this file validates the prefetch JSON artifact format and simple in-memory helpers.

Important tests: `TestNewPrefetchArtifact` verifies version initialization and empty state. `TestPrefetchArtifactAddPrefetchSpanAndIsEmpty` verifies span append behavior. `TestMarshalPrefetchArtifact_EmptyError` checks nil and empty artifacts are rejected. `TestMarshalPrefetchArtifact_Success` confirms descriptor media type, positive size, readable JSON, and round-trip field preservation. `TestUnmarshalPrefetchArtifact_Success` includes priority. Error tests cover invalid JSON and unsupported version.

Control flow and state: tests use in-memory JSON readers/writers only. They inspect decoded struct values rather than relying on digest constants.

Dependencies and integration points: imports `ztoc/compression` for `SpanID`, matching the production artifact type.

Risks and gaps: tests do not verify the descriptor digest equals the marshaled bytes, empty unmarshal rejection, malformed span ranges, priority omission, or unknown extra JSON fields. There is no interoperability fixture for a frozen JSON artifact schema.

Test signal quality: good for basic schema acceptance/rejection; limited for descriptor integrity and semantic validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/prefetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_convert.go -->
# sources/cloud-native/soci-snapshotter/soci/soci_convert.go

Purpose: this file converts a normal image into a SOCI-enabled OCI index. It builds SOCI v2 indexes, annotates image manifests with SOCI index digests, appends/replaces SOCI index descriptors in the top-level OCI index, writes new content, updates artifact DB references, and adds GC labels.

Important APIs and types: `ConvertOption` mutates `convertConfig`. `ConvertWithPlatforms` selects platform builds. `ConvertWithNoGarbageCollectionLabels` disables root GC labels on the converted image. Main methods are `IndexBuilder.Convert`, `buildSociIndexesv2ForPlatforms`, `newOciIndex`, `annotateImages`, `addSociIndexes`, `pushOCIObject`, and `updateSociV2ArtifactReferences`.

Control flow: `Convert` discovers supported platforms and adapts single-manifest inputs by setting target/default platform. It builds or loads an OCI index, builds SOCI v2 indexes per selected platform, rewrites relevant image manifests with `com.amazon.soci.index-digest`, adds SOCI descriptors to the OCI index, pushes the new index, updates artifact DB records to point at the rewritten manifest and new image digest, then labels all referenced manifests and optionally the root index for GC. `annotateImages` tolerates missing manifests when no SOCI index was built for that platform, enabling reduced-platform pushes.

State and persistence: converted manifests and indexes are pushed to `blobStore`; artifact DB records are mutated through `updateSociV2ArtifactReference`; containerd GC labels are written through `store.LabelGCRefContent` and `LabelGCRoot`.

Dependencies and integration points: heavily integrates containerd `images`, platforms, OCI media types, local `ociutil`, SOCI index builder, and content-store abstraction.

Risks: converting manifests changes digests and creates a new image identity. `pushOCIObject` returns descriptors without media type until callers set it. `ConvertWithNoGarbageCollectionLabels` leaves lifecycle responsibility to the caller. Missing manifests are skipped only in a specific branch; unexpected store errors abort. Artifact DB updates assume SOCI v2 descriptors carry `IndexAnnotationImageManifestDigest`.

Test signals: `soci_convert_test.go` only covers `addSociIndexes` append/no-op/replace behavior; full conversion, annotation, push, GC labels, and artifact DB updates are not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_convert_test.go -->
# sources/cloud-native/soci-snapshotter/soci/soci_convert_test.go

Purpose: this file tests the descriptor-list mutation logic for adding SOCI v2 indexes into an OCI index.

Important fixtures: package-level descriptors define a Linux amd64 image manifest, two SOCI index descriptors, and copies with platform pointers assigned in `init`. `TestAddSociIndexes` runs table cases against `IndexBuilder.addSociIndexes`.

Control flow: cases cover appending a new SOCI index, preserving an identical existing SOCI index for the platform, and replacing an existing SOCI index for the same platform with a new digest. Assertions compare manifest count, digest, media type, artifact type, architecture, and OS in order.

State and persistence: purely in-memory descriptor mutation; no content store or artifact DB is involved.

Dependencies and integration points: validates part of `soci_convert.go` that is used after SOCI indexes are built and before the converted OCI index is pushed.

Risks and gaps: no test covers missing platform error, multi-platform replacement isolation, duplicate SOCI descriptors, non-SOCI artifact descriptors, nil platform on existing descriptors, full `Convert`, image annotation, new OCI index creation, GC labels, or artifact DB reference updates. The fixture uses digest strings like `sha256:1234` that are not valid full OCI digests, but the tested function only compares strings.

Test signal quality: focused and useful for the simple append/replace contract, but it does not validate the end-to-end conversion path.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_convert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_index.go -->
# sources/cloud-native/soci-snapshotter/soci/soci_index.go

Purpose: this is the SOCI index builder and serializer. It creates zTOCs for eligible image layers, stores zTOC and prefetch artifacts, writes SOCI index manifests in OCI-manifest form, and records artifacts in the Bolt metadata DB.

Important APIs and types: constants define SOCI artifact types, media types, annotations, defaults, and xattr optimization markers. `IndexVersion` models v1/v2 differences. `Index`, `IndexWithMetadata`, and `IndexDescriptorInfo` represent SOCI manifests and metadata. Serialization functions are `DecodeIndex`, `UnmarshalIndex`, `MarshalIndex`, and `NewIndexFromReader`. Builder options configure span size, min layer size, artifact DB, build tool identifier, force recreate, optimizations, and prefetch paths. Build options configure platform, GC labels, and index version. `IndexBuilder` is constructed by `NewIndexBuilder` and builds through `Build`.

Control flow: `Build` opens a blob-store batch/lease, calls internal `build`, then writes the SOCI index. `build` resolves the platform-specific image manifest, loads manifest layers, concurrently calls `buildSociLayer` per layer, optionally builds prefetch descriptors, filters nil descriptors, and constructs an `Index`. `buildSociLayer` skips SOCI prefetch entries, non-layer media, layers below min size, and unsupported compression. It reuses existing zTOCs from artifacts DB when present and fetchable; otherwise it copies layer content to a temp file, builds a zTOC, pushes it, writes an artifact entry, and annotates the descriptor. Prefetch generation maps requested file paths to topmost matching layer zTOC metadata and span IDs, normalizes overlapping/adjacent spans, stores JSON prefetch artifacts, and adds them to the index. `writeSociIndex` pushes default config content, pushes the manifest, applies GC labels to config and blobs, validates v1 subject, and writes an index artifact entry.

State and persistence: blob content is stored in the configured `store.Store`; artifact metadata is stored in `ArtifactsDb`; temporary layer files are removed after zTOC build. GC labels keep config/zTOC/index content reachable in containerd stores.

Dependencies and integration points: integrates containerd content/images/platforms, zTOC builder and compression metadata, OCI descriptors, SOCI store abstraction, artifact DB, and xattr/whiteout knowledge shared with layer handling.

Risks: concurrent `build` appends to `builtZtocs` from multiple goroutines without synchronization, a data race when prefetch is enabled. `errors.Join(allErr, err)` in `writeSociIndex` does not assign the result, so GC label errors for blobs may be dropped. `NewIndexFromReader` decodes JSON directly into `Index` and bypasses manifest-to-index conversion, unlike `DecodeIndex`. Existing zTOC lookup exits `Walk` via intentional error and ignores that error. Building zTOCs copies entire layer contents to temp files, which can be expensive. `GetImageManifestDescriptor` returns nil,nil for unsupported target media types, so callers must avoid nil dereferences.

Test signals: `soci_index_test.go` covers existing zTOC reuse, min-size skip, layer type filtering, xattr disable decisions, index marshal/unmarshal, prefetch store/normalize behavior, and v1/v2 round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_index_test.go -->
# sources/cloud-native/soci-snapshotter/soci/soci_index_test.go

Purpose: this file tests important SOCI index builder helper contracts without requiring a real containerd content store.

Important tests: `TestGetExistingZtocForLayer` verifies artifacts DB lookup respects original layer digest, span size, and force-recreate. `TestSkipBuildingZtoc` verifies min-layer-size behavior. `TestBuildSociIndexNotLayer` distinguishes non-layer media from supported layer media types. `TestBuildSociIndexWithLimits` checks layer size thresholds. `TestDisableXattrs` validates the xattr optimization rejects xattrs and opaque directory whiteouts. `TestNewIndex`, `TestDecodeIndex`, and `TestMarshalIndex` validate index construction and OCI-manifest serialization for v1/v2. Prefetch tests cover empty path behavior, storing artifacts, descriptor annotations, and span normalization.

Control flow and state: tests use `newFakeContentStore`, `NewOrasMemoryStore`, and temporary artifact DBs. They call some private builder helpers directly, giving targeted coverage of edge conditions.

Dependencies and integration points: tests depend on fake content-store implementations from `util_test.go`, ORAS memory store, OCI descriptors, zTOC metadata structs, and cmp diffing.

Risks and gaps: the tests do not exercise full `Build` over real tar/gzip layer content, concurrent layer builds, actual zTOC correctness, `writeSociIndex` GC label error aggregation, `GetImageManifestDescriptor`, or the prefetch path search against real zTOC file metadata. Some layer media tests only assert not `errNotLayerType`; they may still fail later for fake content/compression reasons. The prefetch layer builder test expects zero descriptors because no zTOCs/layers are supplied, so it does not validate path matching.

Test signal quality: broad helper coverage with low setup cost, but end-to-end build and concurrency behavior need integration or race tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/soci_index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/store/store.go -->
# sources/cloud-native/soci-snapshotter/soci/store/store.go

Purpose: this file abstracts SOCI artifact blob storage over either an ORAS OCI layout store under the SOCI root or containerd's content store.

Important APIs and types: `BasicStore` defines `Exists`, `Fetch`, and `Push`. `Store` adds `Label`, `Delete`, and `BatchOpen`. `ContentStoreType` aliases config types. `ContainerdClient` lazily creates a containerd client under a mutex. `ContentStoreConfig` and `Option` configure store type, containerd address, snapshotter root, and client. `NewContentStore` selects `SociStore` or `ContainerdStore`. Helper functions include `CanonicalizeContentStoreType`, `GetContentStorePath`, `IsErrAlreadyExists`, `LabelGCRoot`, and `LabelGCRefContent`.

Control flow: ORAS-backed `SociStore` wraps `oci.Store` and stubs labels, delete, and batching. Containerd-backed `ContainerdStore` creates a client on demand, checks existence with content info, fetches through `ReaderAt` plus `io.SectionReader`, pushes with `content.OpenWriter`, copies in chunks below gRPC receive limit, validates size, commits by digest, labels content by updating label fields, deletes content, and opens leases for batch protection.

State and persistence: ORAS store persists blobs under the selected OCI layout path. Containerd store persists through containerd's content service and labels. `ContainerdClient` caches the client pointer for process lifetime.

Dependencies and integration points: integrates repo config defaults, containerd client/content/defaults, OCI descriptors, ORAS OCI store, ORAS/containerd already-exists errors, and SOCI index/artifact builders.

Risks: `DefaultSociContentStorePath` concatenates `config.DefaultSociSnapshotterRootPath + "content"` without `filepath.Join`; correctness depends on the default ending with a slash or intentionally forming that path. ORAS `Delete` is a no-op, so cleanup semantics differ by store type. Containerd `Push` uses the digest string as writer ref, which can conflict with stale incomplete writers. Size validation only triggers when expected size is positive. Lazy client creation hides containerd availability until first operation.

Test signals: `store_test.go` covers store-type canonicalization, path derivation, and GC label helper naming/value behavior through a fake memory store.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/store/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/store/store_test.go -->
# sources/cloud-native/soci-snapshotter/soci/store/store_test.go

Purpose: this file tests content-store configuration helpers and GC label helper functions.

Important tests and helpers: `TestStoreCanonicalizeContentStoreType` checks empty/default, `soci`, `containerd`, and invalid types. `TestStoreGetContentStorePath` verifies default paths, custom SOCI root path, containerd ignoring custom root, and invalid type errors. `fakeStore` embeds ORAS memory store and records labels/deletes while satisfying the `Store` interface. `TestStoreLabelGCRoot` and `TestStoreLabelGCRefContent` assert label names, target digest, and referenced digest.

Control flow and state: tests are in-memory except for `filepath.Join` path expectations. Label helper tests record calls in slices on `fakeStore`.

Dependencies and integration points: validates behavior consumed by `soci_index.go` and `soci_convert.go` when keeping content reachable under containerd GC.

Risks and gaps: no tests instantiate `NewContentStore`, `NewSociStore`, or `ContainerdStore`; no tests cover `Push`, `Fetch`, `Exists`, `Delete`, batch leases, containerd client lazy initialization, address trimming, or already-exists normalization. The fake store does not emulate label update errors.

Test signal quality: solid for pure configuration and label formatting; absent for real storage behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/store/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/util_test.go -->
# sources/cloud-native/soci-snapshotter/soci/util_test.go

Purpose: this file provides test doubles and helpers for SOCI index tests.

Important APIs and types: `parseDigest` parses digest strings while ignoring errors for concise test fixtures. `OrasMemoryStore` adapts `oras-go` memory store to the SOCI `store.Store` interface by adding no-op `BatchOpen`, `Label`, and `Delete`. `fakeContentStore` implements containerd `content.Store` enough for selected tests. `fakeReaderAt` returns a configured size and synthetic read count. `fakeWriter` implements `content.Writer` with no-op writes and optional commit function.

Control flow: tests call `newFakeContentStore` to satisfy builder dependencies without containerd. `ReaderAt` returns a fake reader sized from descriptor size; `Writer` returns a fake writer; unsupported methods panic to reveal accidental use. `NewOrasMemoryStore` wraps a fresh memory store for blob operations.

State and persistence: all state is in memory. The fake content store does not persist bytes; fake reader content is zeros/implicit and only size-aware.

Dependencies and integration points: these helpers support `soci_index_test.go` and potentially conversion tests by satisfying `content.Store` and `store.Store`.

Risks: ignored digest parse errors can hide invalid fixture digests. `fakeReaderAt.ReadAt` returns `int(r.size)` regardless of buffer length, which is not a faithful `ReaderAt` implementation and can mask read semantics. Several `content.Store` methods panic, so helpers are only safe for narrow unit paths. No-op labels mean GC-label code cannot be validated with these helpers.

Test signals: as a support file, its quality determines how much confidence SOCI builder tests provide; it is useful for isolated helper tests but not a substitute for integration content-store tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/soci/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dbutil/encoders.go -->
# sources/cloud-native/soci-snapshotter/util/dbutil/encoders.go

Purpose: this file provides varint encoding/decoding helpers for integer values stored in BoltDB buckets.

Important APIs: `EncodeInt(i int64) ([]byte, error)` encodes an int64 with `binary.PutVarint` and returns the used slice. `DecodeInt(data []byte) (int64, error)` decodes with `binary.Varint` and reports insufficient data or overflow when the decoded value is zero and the byte count indicates an error.

Control flow: encoding uses a fixed stack buffer of `binary.MaxVarintLen64`. Decoding relies on `binary.Varint`'s byte-count result: `n == 0` means too little data, `n < 0` means overflow.

State and persistence: no internal state. The encoded bytes are used by artifact DB fields such as size and span size.

Dependencies and integration points: used by `soci/artifacts.go` to persist `ArtifactEntry.Size` and `SpanSize`.

Risks: error detection is conditional on `i == 0`; this matches `binary.Varint` behavior for invalid inputs that return zero, but readers should understand that valid encoded zero also returns `n > 0` and no error. There are no tests in this subset specifically for negative values, zero, overflow, or truncated buffers.

Test signals: indirect coverage through artifact entry round trips; no direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dbutil/encoders.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/compose/compose.go -->
# sources/cloud-native/soci-snapshotter/util/dockershell/compose/compose.go

Purpose: this file provides Docker Compose-based test environments and returns per-service container exec handles.

Important APIs and types: `Supported` checks Docker and `docker compose`. `Compose` holds service-name to `*exec.Exec` map plus cleanup functions. Options support build args and stdio redirection. `Build` only builds images. `Up` starts services from YAML without an explicit build step. `New` builds then starts services. `Get`, `List`, and `Cleanup` manage the resulting environment.

Control flow: functions write provided Compose YAML to a temporary context, call Docker Compose commands with that file, parse `docker compose ps --services`, resolve each service's container ID with `ps -q`, and wrap it with `dexec.New`. Cleanups tear down compose projects and remove temporary contexts. `Build` registers repeated `down --rmi all` cleanup functions before removing the context.

State and persistence: creates temporary directories under the system temp path and Docker containers/images/volumes/networks managed by Compose. Cleanup errors are joined and returned.

Dependencies and integration points: integrates `os/exec`, Docker Compose CLI, local `dockershell/exec`, and xid-generated unique temp names. Used by integration tests that need multi-container fixtures.

Risks: if a command fails before returning a `Compose`, accumulated cleanups are not automatically run, so callers may leak temp directories or compose resources on setup failure. `Build` appends three identical image-removal cleanups, likely to handle dependency ordering but unusual. Compose project naming is implicit from temp directory, and stdio handling differs between full stdio and stderr-only commands.

Test signals: no direct tests in this subset. Validation requires Docker-enabled integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/compose/compose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/exec/cmd.go -->
# sources/cloud-native/soci-snapshotter/util/dockershell/exec/cmd.go

Purpose: this file wraps `docker exec` in an `exec.Cmd`-like API for running commands inside a target container.

Important APIs and types: `Supported` runs `docker version`. `Exec` identifies a container by name and creates commands. `New` validates container availability through `docker inspect`. `Exec.Command` constructs a `Cmd`. `Exec.Kill` runs `docker kill`. `Cmd` exposes familiar fields: path, args, env, dir, stdin/stdout/stderr. Methods mirror `exec.Cmd`: `CombinedOutput`, `Output`, `Run`, `Start`, `Wait`, pipes, and `String`.

Control flow: `Command` resolves the `docker` binary once and stores any lookup error. `toDocker` translates `Cmd` into a host command `docker exec` with `-i`, `-w`, and `-e` options as needed, followed by container name and command args. Execution methods check `lookPathErr` for synchronous methods; pipe/start methods call `toDocker` directly.

State and persistence: command state is held in the embedded `*exec.Cmd`; repeated calls mutate the same `dockerExec.Args` and stdio fields. No persistent state is created except effects of commands inside containers.

Dependencies and integration points: used by `dockershell.Shell` and Compose wrapper to execute commands in integration containers.

Risks: `Start`, pipe methods, and `String` do not check `lookPathErr`, so missing Docker may surface inconsistently. Reusing the same `Cmd` after execution is not safe, matching `exec.Cmd` semantics but not enforced. Args include a literal `"docker"` element even though `Path` is set to the docker binary, which is normal for `exec.Cmd` display/argv0.

Test signals: no direct tests in this subset; behavior is likely integration-tested through Docker shell utilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/exec/cmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/exec/util.go -->
# sources/cloud-native/soci-snapshotter/util/dockershell/exec/util.go

Purpose: this file provides Docker utility helpers for temporary networks and temporary images used by integration tests.

Important APIs and types: `NewTempNetwork` creates a Docker network and returns a cleanup function. `Connect` attaches an `Exec` container to a network. Image options configure patch Dockerfile content, patch build context, build args, and build stdio. `NewTempImage` builds an image from a context and optional target stage, optionally then builds a derived patch image. `newTempImage` performs the actual Docker build and returns image tag plus cleanup.

Control flow: `NewTempImage` requires an absolute context dir. If a patch context is specified, a patch Dockerfile must also be specified. It first builds the base image; without patch content, it returns that image and cleanup. With patch content, it defers cleanup of the base image, creates or uses a patch context, writes a Dockerfile `FROM <base>` plus patch content, and builds a second image. `newTempImage` generates a unique tag, assembles `docker build -q -t`, optional Dockerfile, target, build args, and context, then returns cleanup that removes the image.

State and persistence: creates Docker networks/images and temporary Dockerfile/context directories. Cleanup removes created network/image and temporary directories created by the helper.

Dependencies and integration points: uses Docker CLI, xid, filesystem temp dirs, and `Exec` for container identity in `Connect`.

Risks: cleanup is caller-managed and setup failures can leak resources. Patch Dockerfile is written with mode `0666`, subject to umask, broader than needed. Temporary image names are not namespaced beyond `tmpimage<id>`. Build args are passed directly to Docker CLI.

Test signals: no direct tests in this subset; requires Docker integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/exec/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/shell.go -->
# sources/cloud-native/soci-snapshotter/util/dockershell/shell.go

Purpose: this file provides a chainable shell-like interface for executing commands inside a Docker container via `dockershell/exec`.

Important APIs and types: `Supported` delegates Docker support check. `Reporter` abstracts error/log/stdout/stderr sinks. `DefaultReporter` writes to stdout/stderr. `Shell` embeds `*dexec.Exec`, tracks the last error and an invalid flag. Core methods include `Fatal`, `Err`, `IsInvalid`, `Refresh`, `X`, `XLog`, `Gox`, `Pipe`, `Retry`, `O`, `OLog`, `CombinedOLog`, `R`, and `ForEach`. `C` is a command slice helper for `Pipe`.

Control flow: most methods no-op if the shell is invalid. `X`, `O`, `Pipe`, and exhausted `Retry` mark the shell invalid on failure. `XLog`, `OLog`, `CombinedOLog`, and `Gox` log errors but allow later commands. `Pipe` starts each command with the previous command's stdout as stdin, then waits in reverse order to avoid truncating stdout pipes. `R` returns pipe readers and runs the command in a goroutine, closing pipes with errors on failure. `ForEach` streams stdout lines to a callback and stderr to the reporter.

State and persistence: shell invalid/error state is in memory, protected by a mutex for the invalid flag. Commands can mutate container state but the shell has no persistent storage.

Dependencies and integration points: integrates the Docker exec wrapper and is used by integration tests for command orchestration inside containers.

Risks: `Gox` launches background goroutines without cancellation or wait handles, so callers cannot reliably synchronize. `ForEach` does not return scanner errors. `Retry` logs attempts starting at `0/num`, which is mildly misleading. Reporter comments contain copy-paste wording mistakes but behavior is clear.

Test signals: no direct tests in this subset. The most important behaviors to integration-test are invalid-state short-circuiting, pipe lifecycle, and background command handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/dockershell/shell.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/multireadcloser.go -->
# sources/cloud-native/soci-snapshotter/util/ioutils/multireadcloser.go

Purpose: this file combines multiple `io.ReadCloser` values into one sequential reader that closes all underlying resources.

Important API: `MultiReadCloser` stores the underlying closers and embeds an `io.Reader`. `NewMultiReadCloser` converts the closers to readers and wraps them with `io.MultiReader`. `Close` iterates all closers and returns `errors.Join` of any close failures.

Control flow: reads proceed in order through `io.MultiReader`; close is independent of read position and attempts every closer even if earlier closes fail.

State and persistence: in-memory wrapper only. Closing affects the underlying resources.

Dependencies and integration points: useful when content is assembled from multiple streams but callers need a single closeable reader.

Risks: no nil checks for input closers. `Close` can be called multiple times and will call underlying closers multiple times. There are no direct tests in this subset. The constructor uses `for i := range len(rcs)`, requiring a Go version that supports ranging over integers.

Test signals: absent here; should be tested for read order, close-all semantics, and joined errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/multireadcloser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader.go -->
# sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader.go

Purpose: this file wraps an `io.Reader` and tracks how many bytes have been returned to callers.

Important API: `PositionTrackerReader` contains the underlying reader and current `pos`. `NewPositionTrackerReader` initializes position to zero. `Read` delegates to the underlying reader and increments `pos` by `n` even when an error is also returned. `CurrentPos` returns the accumulated byte count.

Control flow: the wrapper follows normal Go reader semantics: bytes read before an error still count. It does not inspect or transform data.

State and persistence: position is process-local mutable state. There is no locking, so concurrent reads are not safe unless the caller serializes access.

Dependencies and integration points: used wherever streamed reads need offset tracking, such as compression or archive processing code.

Risks: not concurrency-safe; no reset or seek support; position can diverge if the underlying reader has side-channel seeking. It increments on any positive `n`, including custom readers that return data with non-EOF errors.

Test signals: `positiontrackerreader_test.go` covers full read, short read, and read with `io.ErrUnexpectedEOF`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader_test.go -->
# sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader_test.go

Purpose: this file verifies byte-position tracking for `PositionTrackerReader`.

Important helpers and tests: `bs` is a fixed byte slice. The helper `copy` fills buffers from `bs` and errors if the buffer is too short. `testReader` returns a configured byte count and error. `TestPositionTrackingReader` covers a full read from `bytes.Reader`, a short successful read, and a short read with `io.ErrUnexpectedEOF`.

Control flow and state: each case creates a new tracker, reads into a 10-byte buffer once, then checks `CurrentPos` and expected error matching with `errors.Is`.

Dependencies and integration points: tests only the local ioutils wrapper.

Risks and gaps: tests do not cover multiple reads accumulating position, zero-byte reads, EOF after all data, concurrent reads, or underlying readers that return `n=0` with an error. The package-level helper named `copy` shadows the builtin, but only within this test file.

Test signal quality: good for the key contract that bytes returned before an error still advance position; limited for repeated-read behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/sectionreadcloser.go -->
# sources/cloud-native/soci-snapshotter/util/ioutils/sectionreadcloser.go

Purpose: this file adapts an `io.SectionReader` plus separate closer into a closeable section reader.

Important API: `SectionReadCloser` embeds `*io.SectionReader` and stores an `io.Closer`. `NewSectionReadCloser` constructs the pair. `Close` delegates to the stored closer.

Control flow: all read/seek/read-at behavior comes from the embedded `SectionReader`; close only affects the external closer, usually the underlying file or content reader.

State and persistence: no own persistence. Closing releases the resource represented by `c`.

Dependencies and integration points: useful for APIs that need an `io.ReadCloser` over a bounded section while retaining section-reader capabilities.

Risks: nil reader or closer will panic on use/close. Closing does not prevent further reads at this wrapper level if the underlying section reader still works. There are no direct tests in this subset.

Test signals: absent; recommended tests would cover read bounds and close delegation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ioutils/sectionreadcloser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/lrucache/lrucache.go -->
# sources/cloud-native/soci-snapshotter/util/lrucache/lrucache.go

Purpose: this package provides a reference-count-aware LRU cache. It delays final eviction callbacks until an entry has been removed from the LRU and all borrowers have released their references.

Important APIs and types: `Cache` wraps `groupcache/lru.Cache`, a mutex, and optional `OnEvicted`. `New` configures the inner LRU callback to finalize the cache-owned reference. `Get` returns value, a `done` release function, and ok flag. `Add` inserts new values or returns the existing value for duplicate keys; both paths increment a borrower reference and return a one-shot `done`. `Remove` removes from LRU. `refCounter` stores key, value, callback, reference count, and once guards for initialization/finalization.

Control flow: adding a new entry creates a refCounter, increments once for cache ownership, increments once for the caller, and inserts it. LRU eviction or explicit remove calls `finalize`, dropping the cache-owned ref. Borrowers call `done`, which is protected by `sync.Once` and decrements under the cache mutex. When ref count reaches zero, `OnEvicted` runs.

State and persistence: all state is in memory. The cache does not persist values and does not close resources by itself; `OnEvicted` is the finalization hook.

Dependencies and integration points: depends on `github.com/golang/groupcache/lru`. Useful for cached remote/layer resources where active users must keep objects alive past LRU eviction.

Risks: `OnEvicted` runs while locks are held through `dec`, so callbacks that re-enter the cache can deadlock. `refCounts` is signed and can go non-positive; one-shot `done` prevents common double-decrement, but misuse of internals could underflow. Changing `Cache.OnEvicted` after entries are added only affects future entries because the callback is copied into each `refCounter`.

Test signals: `lrucache_test.go` covers add/get duplicate behavior, explicit remove delayed until references are released, LRU overflow delayed eviction, and one-shot `done`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/lrucache/lrucache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/lrucache/lrucache_test.go -->
# sources/cloud-native/soci-snapshotter/util/lrucache/lrucache_test.go

Purpose: this file tests the reference-count-aware LRU cache behavior.

Important tests: `TestAdd` confirms a first add stores the value and a duplicate add returns the original cached value with `added=false`. `TestGet` verifies retrieving an existing value succeeds. `TestRemove` checks explicit removal does not trigger eviction while borrowed references remain, then triggers after all `done` callbacks are called. `TestEviction` fills a size-two cache, overflows it, confirms callbacks are delayed until references are released, and verifies duplicate calls to the same `done` are ignored.

Control flow and state: tests capture evicted keys in a slice via `OnEvicted`. They intentionally hold references returned by `Add` and `Get` to validate delayed finalization.

Dependencies and integration points: tests the local wrapper over groupcache LRU without external resources.

Risks and gaps: no tests cover cache capacity zero, callback reentrancy/deadlock, concurrent access, changing `OnEvicted` after insertion, or `Remove` of missing keys. Tests do not call all returned `done` functions for overflow-added entries, which is acceptable for the targeted assertions but leaves some reference-count paths unobserved.

Test signal quality: strong for the package's central delayed-eviction contract; missing for concurrency and callback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/lrucache/lrucache_test.go -->
