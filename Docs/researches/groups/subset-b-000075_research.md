# subset-b-000075 research

This grouped report covers the requested containerd CRI, diff, GC, mount, server, and service plugin files. Each source file has its own marked section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/images/plugin.go -->
# sources/cloud-native/containerd/plugins/cri/images/plugin.go

## Purpose
Registers the CRI image service plugin (`io.containerd.cri.v1.images`) and migrates image-related settings from the legacy monolithic CRI gRPC plugin. It wires the CRI image server to metadata content/images, snapshotters, transfer, leases, sandbox store, warnings, and an in-memory containerd client.

## Important APIs, Types, And Functions
`init` registers the plugin with `criconfig.DefaultImageConfig`. `configMigration` and `migrateConfig` copy legacy `sandbox_image`, registry, image pull, image decryption, snapshotter, and runtime snapshot settings into the new image config. The init function builds `images.CRIImageServiceOptions`, resolves snapshotter roots, parses runtime platforms, and calls `images.NewService`.

## Control Flow
Startup loads metadata DB, fills the default Linux registry config path only when no registry mirrors/config path are configured, validates image config, emits warnings through the warning plugin, warns about local image pull conflicts, creates an in-memory client in the Kubernetes namespace, selects the default snapshotter, computes image filesystem paths, maps runtime names to snapshotter/platform pairs, then returns the CRI image service.

## State And Persistence
The plugin itself is not persistent. It uses metadata DB content/image services and snapshotter state. `ImageFSPaths` are derived from plugin exports or root-directory conventions. Migration mutates the daemon config map before plugin initialization.

## Dependencies And Integration Points
Depends on metadata, lease, sandbox store, service, snapshot, transfer, and warning plugins. Integrates with `internal/cri/server/images`, CRI config validation, `platforms`, containerd client in-memory services, and snapshotter plugin metadata exports.

## Risks
Migration uses unchecked type assertions on config maps, so malformed legacy config can panic during daemon config migration. Runtime platform parsing is startup-fatal. Missing default snapshotter prevents CRI image service startup. Registry defaults are Linux-specific and can conflict with explicitly configured mirrors if validation is bypassed.

## Test Signals
`plugin_test.go` verifies sandbox image and registry config migration. Broader behavior is covered indirectly by CRI image service and daemon integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/images/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/images/plugin_test.go -->
# sources/cloud-native/containerd/plugins/cri/images/plugin_test.go

## Purpose
Tests legacy CRI image configuration migration into the split CRI image plugin.

## Important APIs, Types, And Functions
`TestSandboxImageConfigMigration` calls `configMigration` with a legacy `sandbox_image` and asserts it appears under `pinned_images.sandbox`. `TestRegistryConfigMigration` verifies `registry.config_path` is preserved under the image service plugin key.

## Control Flow
Each test builds a synthetic `pluginConfigs` map containing `io.containerd.grpc.v1.cri`, invokes migration with config version `2`, and inspects the generated `io.containerd.cri.v1.images` map.

## State And Persistence
All state is in-memory test data. The tests validate mutation of the config map, not on-disk TOML serialization.

## Dependencies And Integration Points
Uses `plugins` names and `testify` assertions. It directly covers migration helpers in `plugin.go`.

## Risks
Coverage is narrow: it does not test runtime platform migration, pinned image merge behavior, existing destination config preservation, or invalid map types.

## Test Signals
Positive migration tests provide regression signals for the two most visible legacy image settings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/images/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/load_test.go -->
# sources/cloud-native/containerd/plugins/cri/runtime/load_test.go

## Purpose
Validates preloading of base OCI runtime specs referenced from CRI runtime configuration.

## Important APIs, Types, And Functions
`TestLoadBaseOCISpec` writes a JSON `oci.Spec`, configures a runtime with `BaseRuntimeSpec`, calls `loadBaseOCISpecs`, and asserts the spec map contains the loaded version and hostname.

## Control Flow
The test creates a temporary file, JSON-encodes a minimal spec, builds `criconfig.Config.Runtimes`, loads specs, then checks the returned map by filename.

## State And Persistence
Uses a temporary file only. It verifies file-backed config input becomes an in-memory cache for `runtime.LoadOCISpec`.

## Dependencies And Integration Points
Depends on `criconfig`, `pkg/oci`, JSON encoding, and `testify`. It directly exercises helpers from `runtime/plugin.go`.

## Risks
It does not cover duplicate spec paths, malformed JSON, missing files, or `runtime.LoadOCISpec` not-found behavior.

## Test Signals
Provides a focused startup-cache regression for the base OCI spec loading path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/plugin.go -->
# sources/cloud-native/containerd/plugins/cri/runtime/plugin.go

## Purpose
Registers the base CRI runtime plugin and owns runtime-side CRI config validation, state/root directory compatibility, base OCI spec preloading, klog level setup, and migration from legacy CRI config.

## Important APIs, Types, And Functions
`init` registers the `runtime` CRI service plugin. `initCRIRuntime` validates config and returns a `runtime` object. `runtime.Config` and `runtime.LoadOCISpec` expose cached runtime state. `loadBaseOCISpecs`, `loadOCISpec`, `setGLogLevel`, `configMigration`, and `migrateConfig` are the main helpers.

## Control Flow
Initialization sets plugin platform/export metadata, validates runtime config and emits warnings, computes backward-compatible CRI root/state directories, creates/chmods state dir, logs the marshaled config, initializes klog flags from containerd log level, loads unique `BaseRuntimeSpec` files, and returns the runtime service object.

## State And Persistence
Persistent state is the CRI state directory under the containerd state parent and any referenced base OCI spec files. The plugin caches loaded specs in memory. Migration mutates config maps before startup and preserves unknown runtime keys unless they moved to other split plugins.

## Dependencies And Integration Points
Integrates with the warning plugin, CRI config validation, Kubernetes klog, `platforms`, `errdefs`, `pkg/oci`, and versioned config migration. Other CRI services depend on this base plugin for config and OCI spec lookup.

## Risks
Config migration relies on concrete `map[string]any` shapes and type assertions. `setGLogLevel` mutates global klog flags. Base OCI spec loading is startup-fatal when a referenced file is missing or invalid. Directory permissions are forced to `0700`, which matters for upgrades.

## Test Signals
`load_test.go` covers spec loading. `plugin_test.go` covers migration of selected runtime, CNI, and moved keys. Full startup validation is covered by broader CRI integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/plugin_test.go -->
# sources/cloud-native/containerd/plugins/cri/runtime/plugin_test.go

## Purpose
Tests migration from the old CRI plugin config into the split CRI runtime plugin config.

## Important APIs, Types, And Functions
`TestCRIRuntimePluginConfigMigration` exercises `configMigration` and checks migrated general runtime keys, moved image/server keys, CNI `bin_dir` to `bin_dirs`, and runtime `sandbox_mode` to `sandboxer`.

## Control Flow
The test constructs a legacy CRI config map with runtime, CNI, image, and server fields, runs migration for config version `2`, then inspects the destination runtime plugin map.

## State And Persistence
All state is in-memory. It verifies config shape migration rather than TOML persistence.

## Dependencies And Integration Points
Uses the `plugins` package for plugin keys and `testify` for assertions. It covers the migration helper in `runtime/plugin.go`.

## Risks
It does not check preservation of existing destination values, invalid CNI type shapes, or multiple runtimes, but it covers the most important split-config behavior.

## Test Signals
Provides regression coverage for avoiding image/server config leakage into the runtime plugin and for compatibility renames.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/runtime/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/compare_linux.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/compare_linux.go

## Purpose
Implements Linux-only EROFS differ comparison by generating a standard OCI layer tar diff from EROFS snapshot mounts and storing it in the content store.

## Important APIs, Types, And Functions
`writeDiff` mounts the lower mount set and streams overlay-style directory changes from the upper root. `erofsDiff.Compare` handles diff options, media-type compression selection, content writer lifecycle, uncompressed digest labels, commits, and descriptor construction. `uniqueRef` creates upload references.

## Control Flow
Compare converts the upper mount to an EROFS layer path, applies diff options and source-date epoch, defaults media type to gzip, opens or truncates a content writer, writes a tar diff from `layer/fs`, optionally compresses while hashing the uncompressed stream, commits by writer digest, fetches content info, patches missing uncompressed labels, and returns an OCI descriptor.

## State And Persistence
Persists diff blobs and labels in the content store. Temporary state is the content ingest reference and mounted lower filesystem. Failed new-reference writes abort the ingest.

## Dependencies And Integration Points
Uses `continuity/fs`, `archive.NewChangeWriter`, compression helpers, `epoch`, content store APIs, EROFS mount-to-layer utilities, and OCI media types. It is selected by the EROFS diff plugin on Linux.

## Risks
The path assumption `layer/fs` must match EROFS snapshot layout. Label repair assumes `config.Labels` has an uncompressed digest, which is only guaranteed for compressed writes. Writer cleanup and existing-content label update are important for interrupted or deduplicated diffs.

## Test Signals
No direct tests in this subset. Behavior is exercised by containerd diff/apply integration tests and EROFS snapshot/differ workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/compare_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/compare_other.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/compare_other.go

## Purpose
Provides the non-Linux implementation of EROFS `Compare`, returning not implemented.

## Important APIs, Types, And Functions
`erofsDiff.Compare` matches the Linux method signature but returns `emptyDesc` and `errdefs.ErrNotImplemented`.

## Control Flow
The method performs no inspection and immediately delegates fallback selection to callers that understand `ErrNotImplemented`.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Compiled under `!linux`. It integrates with the diff service fallback chain, allowing other differs such as walking to handle comparisons on unsupported platforms.

## Risks
Callers must check `errdefs.IsNotImplemented`; treating the error as fatal can disable otherwise valid fallback differs.

## Test Signals
No direct tests. Platform build coverage ensures signature compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/compare_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/differ.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/differ.go

## Purpose
Implements EROFS diff application and construction options. It can apply native EROFS blobs directly, convert tar layers to EROFS, generate tar-index EROFS layers, and optionally append dm-verity metadata.

## Important APIs, Types, And Functions
`erofsDiff` stores the content store and options. `WithMkfsOptions`, `WithTarIndexMode`, and `WithDmverity` configure behavior. `NewErofsDiffer` constructs a combined `diff.Applier`/`diff.Comparer`. `Apply` streams content through processors and writes `layer.erofs`. `readCounter` tracks uncompressed byte count.

## Control Flow
Apply determines whether the descriptor is native EROFS or a supported OCI layer, normalizes native media types for processor selection, parses apply options, resolves the snapshot layer path, opens content, fast-copies uncompressed native EROFS blobs, otherwise obtains an uncompressed layer stream, hashes and counts bytes, writes either native EROFS, tar-index EROFS, or converted EROFS, drains trailing data, optionally formats dm-verity, and returns the descriptor representing applied content.

## State And Persistence
Writes `layer.erofs` inside the snapshot layer directory. Optional dm-verity formatting extends that file and writes adjacent metadata. Content blobs remain in the content store and are only read.

## Dependencies And Integration Points
Integrates with `core/diff`, content store readers, OCI media types, `images.DiffCompression`, `internal/erofsutils`, Google UUID generation, and platform-specific `formatDmverityLayer`.

## Risks
Native media suffix handling only accepts `+zstd`. Fast-copy returns the original descriptor without rehashing. Tar-index mode has block-size implications for dm-verity. Any mismatch between EROFS snapshot layout and `MountsToLayer` breaks apply.

## Test Signals
Dm-verity helpers have unit tests. EROFS apply behavior is mainly covered by integration tests requiring mkfs.erofs and EROFS snapshotter support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/differ.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux.go

## Purpose
Adds Linux dm-verity formatting support for EROFS layers produced by the EROFS differ.

## Important APIs, Types, And Functions
`getDmverityOptions` selects dm-verity data/hash block sizes based on tar-index mode. `formatDmverityLayer` calculates aligned hash offsets, truncates the EROFS blob to include superblock/hash tree, calls `dmverity.Format`, and writes `DmverityMetadata`.

## Control Flow
Formatting skips when metadata already exists, stats the layer file, computes data blocks and hash offset, asks the verity library for hash-tree size, accounts for optional superblock size, preallocates the combined file, ensures a UUID, formats in place, marshals root hash and original hash offset to JSON metadata, and logs success.

## State And Persistence
Mutates the EROFS layer file by extending it with dm-verity structures and persists a sidecar metadata file used by the mount handler to open the verified block device.

## Dependencies And Integration Points
Depends on `containerd/go-dmverity`, `internal/dmverity`, UUIDs, JSON, and OS file operations. It pairs with the EROFS mount handler, which reads this metadata and opens `/dev/mapper` devices.

## Risks
Hash offset correctness is critical: metadata stores the superblock location, not the hash-tree start. File truncation is destructive if options are wrong. Tar-index layers require 512-byte blocks; using default 4096-byte blocks would make EROFS mounts fail.

## Test Signals
`dmverity_linux_test.go` verifies option selection, idempotency, missing-file errors, and block-aligned hash offsets when dm-verity is available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux_test.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux_test.go

## Purpose
Tests Linux dm-verity configuration and formatting behavior for EROFS differ layers.

## Important APIs, Types, And Functions
`TestGetDmverityOptions` checks 512-byte blocks for tar-index mode and 4096-byte blocks for regular mode. `TestFormatDmverityLayer` covers metadata creation, idempotency, regular/tar-index offsets, missing files, and non-aligned file-size rounding.

## Control Flow
The formatting test skips when dm-verity is unsupported, writes temporary layer files, calls `formatDmverityLayer`, reads sidecar metadata via `dmverity.ReadMetadata`, and asserts root hash and hash offset expectations.

## State And Persistence
Uses temporary files and real dm-verity formatting support. The tests create sidecar metadata and mutate layer files in temp directories.

## Dependencies And Integration Points
Depends on `internal/dmverity`, `logtest`, `testify`, Linux dm-verity availability, and `formatDmverityLayer`.

## Risks
The tests are environment-sensitive and skip without kernel/module support, so CI can miss formatting regressions on unsupported hosts.

## Test Signals
Strong targeted coverage for block-size selection, idempotency, metadata sidecar creation, and hash-offset alignment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_other.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_other.go

## Purpose
Provides the non-Linux dm-verity formatting stub for the EROFS differ.

## Important APIs, Types, And Functions
`formatDmverityLayer` returns an explicit unsupported-platform error.

## Control Flow
The method immediately fails when called.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Compiled under `!linux`. It preserves the common `erofsDiff.Apply` call shape while preventing silent dm-verity no-ops on unsupported platforms.

## Risks
If dm-verity is enabled through config on non-Linux builds, apply fails at runtime rather than formatting. Plugin-level checks should prevent most unsupported configurations.

## Test Signals
No direct tests. Build tags validate compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/dmverity_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/diff/erofs/plugin/plugin.go

## Purpose
Registers the EROFS diff plugin and validates host/tooling support before exposing an EROFS comparer/applier.

## Important APIs, Types, And Functions
`Config` exposes `MkfsOptions`, `EnableTarIndex`, and `EnableDmverity`. `init` registers the `erofs` diff plugin and builds `erofs.NewErofsDiffer` with configured options.

## Control Flow
Startup verifies `mkfs.erofs` tar support, loads metadata DB, advertises Linux platform support plus an `erofs` OS feature variant, gets the content store, maps config fields to differ options, checks dm-verity support when requested, and returns the configured differ or skips the plugin when prerequisites are unavailable.

## State And Persistence
No direct persistence. It reads metadata DB only to obtain the content store. Plugin metadata advertises supported platforms/features.

## Dependencies And Integration Points
Depends on metadata, `internal/erofsutils`, `internal/dmverity`, platforms, plugin registry, and the EROFS differ package. The diff service uses this plugin according to platform-specific differ order.

## Risks
Host tool availability directly controls plugin loading. Enabling dm-verity can skip the plugin entirely if kernel support is missing. Platform metadata is manually adjusted to prefer EROFS-native images.

## Test Signals
No direct tests in this file. Dm-verity helper tests and integration tests with mkfs.erofs provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/erofs/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/lcow/lcow.go -->
# sources/cloud-native/containerd/plugins/diff/lcow/lcow.go

## Purpose
Implements the Windows LCOW diff applier that converts Linux tar layers into ext4 VHD files for Linux containers on Windows.

## Important APIs, Types, And Functions
Registers the `windows-lcow` diff plugin under Windows builds. `CompareApplier` combines `diff.Applier` and `diff.Comparer`. `windowsLcowDiff.Apply` converts content to `layer.vhd`; `Compare` returns not implemented. `mountsToLayerAndParents` validates `lcow-layer` mounts. `readCounter` tracks stream size.

## Control Flow
Apply reads the content blob, walks stream processors to an OCI layer tar stream, hashes/counts bytes via `readCounter`, creates `layer.vhd`, converts tar to ext4 with whiteout handling and VHD footer, syncs the output, drains trailing data, grants VM group access, and returns an uncompressed OCI descriptor.

## State And Persistence
Writes a `layer.vhd` file into the snapshot layer directory and updates file ACLs for VM access. Content store blobs are read-only inputs.

## Dependencies And Integration Points
Uses hcsshim `tar2ext4`, Windows security helpers, content store, diff processors, plugin metadata, and Windows-specific mount type conventions. It is a fallback partner for the Windows diff service.

## Risks
Windows-only privileges and ACL setup are required. Partial VHD files are removed only on the error path before successful close. Compare is intentionally unsupported, so callers must fall back or avoid LCOW diff generation.

## Test Signals
No direct tests in this subset. Coverage is Windows integration dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/lcow/lcow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/walking/differ.go -->
# sources/cloud-native/containerd/plugins/diff/walking/differ.go

## Purpose
Implements the generic walking filesystem differ that compares mounted lower and upper filesystems and writes OCI layer tar diffs to the content store.

## Important APIs, Types, And Functions
`walkingDiff` holds a content store. `NewWalkingDiff` returns a `diff.Comparer`. `Compare` mounts lower and upper sets, writes `archive.WriteDiff`, handles compression/custom compressors, commits content, and returns descriptors. `uniqueRef` generates upload references.

## Control Flow
Compare applies diff options and source-date epoch, chooses compression from media type or custom compressor, mounts lower and read-only upper temp mounts, opens/truncates a content writer, streams a tar diff with optional source-date normalization, records the uncompressed digest label for compressed media, commits by writer digest, repairs missing labels on existing blobs, and returns content info.

## State And Persistence
Persists diff blobs and labels in the content store. Temporary mounts and ingest refs are cleaned up on errors; new references are aborted when open writes fail.

## Dependencies And Integration Points
Uses containerd mount helpers, archive diff generation, compression, epoch, content store, labels, OCI media types, and errdefs. It is the default generic differ on most Unix platforms and part of Windows fallback ordering.

## Risks
Custom compressor requires explicit media type. Existing-blob label repair assumes a computed uncompressed digest. Mount lifecycle and writer cleanup are critical for failures. This generic implementation may be slower than snapshotter-specific differs.

## Test Signals
No direct tests in this subset. It is heavily exercised by rootfs diff and content integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/walking/differ.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/walking/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/diff/walking/plugin/plugin.go

## Purpose
Registers the generic walking diff plugin, combining the walking comparer with a filesystem applier.

## Important APIs, Types, And Functions
`init` registers the `walking` diff plugin. `diffPlugin` embeds `diff.Comparer` and `diff.Applier`.

## Control Flow
Startup gets metadata DB, optionally gets the mount manager, advertises the default platform, obtains the content store, builds `walking.NewWalkingDiff`, builds `apply.NewFileSystemApplierWithMountManager`, and returns the combined plugin.

## State And Persistence
No direct persistence. It uses the content store from metadata and optionally the mount manager for apply operations.

## Dependencies And Integration Points
Depends on metadata, optional mount manager, core diff apply, plugin registry, and platforms. The diff service selects it according to platform-specific default ordering.

## Risks
Mount manager errors other than plugin-not-found are startup-fatal. Apply behavior changes depending on whether a mount manager is available.

## Test Signals
No direct tests. Walking differ and filesystem applier are exercised by diff/apply integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/walking/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/windows/cimfs.go -->
# sources/cloud-native/containerd/plugins/diff/windows/cimfs.go

## Purpose
Registers and implements Windows CimFS and block CIM diff appliers, importing OCI layer tar streams into CimFS-backed layer formats.

## Important APIs, Types, And Functions
Registers `cimfs` and `blockcim` diff plugins. `cimApplyFunc` abstracts import functions. `cimDiff.Apply` imports standard CimFS layers. `blockCIMDiff.Apply` imports block CIMs. `parseBlockCIMMount` decodes mount options. `applyCIMLayerCommon` handles content reading, processor chain, hashing, and descriptor return.

## Control Flow
Plugin init checks OS feature support, loads metadata content store, and returns the appropriate differ. Apply validates mount type, extracts source/parent/CIM paths and mount flags, builds an import function, then common code reads the blob, unwraps processors to an OCI layer, tees through a digest, invokes the import function, drains trailing data, and returns an OCI layer descriptor.

## State And Persistence
Writes CimFS or block CIM layer artifacts through hcsshim import APIs. Reads content blobs but does not write the content store. Parent layer paths come from mount options.

## Dependencies And Integration Points
Windows-only. Integrates with hcsshim CimFS APIs, containerd mount option helpers, content store, diff processors, and platform/plugin registration.

## Risks
Only single-file block CIM extraction is supported. Compare is not implemented. Mount option JSON parsing and parent path interpretation are critical. Host OS feature checks determine plugin availability.

## Test Signals
No direct tests in this subset. Coverage depends on Windows CimFS integration environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/windows/cimfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/windows/windows.go -->
# sources/cloud-native/containerd/plugins/diff/windows/windows.go

## Purpose
Implements the standard Windows container layer diff plugin for applying and comparing WCOW layers.

## Important APIs, Types, And Functions
Registers the `windows` diff plugin. `windowsDiff.Apply` applies a tar layer to a Windows layer. `windowsDiff.Compare` writes layer diffs to the content store. `mountsToLayerAndParents` and `mountPairToLayerStack` validate Windows layer relationships. `readCounter` and `uniqueRef` support streaming and ingest.

## Control Flow
Apply validates a single `windows-layer` mount, enables backup/restore privileges, unwraps content processors to OCI tar, hashes/counts data, applies with Windows layer archive options and parent layers, drains trailing data, and returns a descriptor. Compare validates lower/upper stack relationship, enables backup privilege, writes a compressed or uncompressed Windows layer diff to a content writer, commits it, repairs missing uncompressed labels, and logs timing.

## State And Persistence
Apply mutates the target Windows layer directory. Compare persists content blobs and labels. It may alter process privileges for the daemon process.

## Dependencies And Integration Points
Windows-only. Uses go-winio privileges, archive Windows layer options, content store, mount parent metadata, compression, labels, and errdefs. The diff service tries this before LCOW on Windows.

## Risks
Process privilege changes are global and not ref-counted. Layer-stack validation must be strict to avoid invalid parent diffs. Non-Windows mount types intentionally return `ErrNotImplemented` to allow LCOW fallback.

## Test Signals
No direct tests in this subset. Windows integration tests are required for meaningful coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/diff/windows/windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/events/plugin.go -->
# sources/cloud-native/containerd/plugins/events/plugin.go

## Purpose
Registers the core containerd event exchange plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.EventPlugin` with ID `exchange`; its init function returns `exchange.NewExchange()`.

## Control Flow
Plugin initialization simply constructs an in-memory event exchange without external prerequisites.

## State And Persistence
Event state is in-memory pub/sub only. No event persistence is handled here.

## Dependencies And Integration Points
Services and plugins use the exchange as `events.Publisher` and subscriber hub. Event gRPC/TTRPC services depend on this plugin.

## Risks
Because events are in-memory, subscribers only see events after subscription and daemon restart loses in-flight subscriptions.

## Test Signals
No direct tests here; event service tests and daemon integration cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/events/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/metrics.go -->
# sources/cloud-native/containerd/plugins/gc/metrics.go

## Purpose
Defines Prometheus-style metrics for the garbage collection scheduler.

## Important APIs, Types, And Functions
Package globals `collectionCounter` and `gcTimeHist` track collection counts by status and collection duration. `init` creates and registers the `containerd_gc` metrics namespace.

## Control Flow
At package init, metrics are created and registered. The scheduler updates them after successful or failed collection attempts.

## State And Persistence
Metrics are in-memory process counters/timers exported through the configured metrics server.

## Dependencies And Integration Points
Uses `docker/go-metrics`; consumed by `scheduler.go`. Exposed by the metrics HTTP server if configured.

## Risks
Metrics registration happens globally and can conflict if package init is repeated in unusual test setups.

## Test Signals
No direct tests. Scheduler tests exercise paths that update metrics, but do not assert metric values.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/scheduler.go -->
# sources/cloud-native/containerd/plugins/gc/scheduler.go

## Purpose
Registers and implements the metadata garbage collection scheduler. It turns metadata mutations, deletion counts, startup delay, manual triggers, and pause-threshold heuristics into calls to the metadata collector.

## Important APIs, Types, And Functions
`config` exposes pause, deletion, mutation, schedule, and startup delays. `collector` abstracts metadata GC. `gcScheduler` owns event channel, waiter list, thresholds, and run loop. `ScheduleAndWait`, `wait`, `mutationCallback`, `schedule`, and `run` are the core methods.

## Control Flow
Startup validates/clamps config, registers a mutation callback, exports effective config, and starts `run`. The run loop optionally schedules startup GC, accepts mutation/manual events, counts dirty deletions and mutations, schedules collections when thresholds are met, skips unneeded scheduled runs, runs `GarbageCollect`, notifies waiters, updates metrics, and recalculates the next interval from average GC duration and pause threshold.

## State And Persistence
Scheduler state is in-memory: counters, average GC timing, waiters, and next collection time. Actual persistence cleanup is delegated to metadata DB garbage collection.

## Dependencies And Integration Points
Requires metadata plugin implementing `collector`, uses `pkg/gc.Stats`, `tomlext.Duration`, plugin exports, logging, and metrics from `metrics.go`. Lease and image services use `ScheduleAndWait` for synchronous deletes.

## Risks
Events are sent from goroutines into an unbuffered channel; if the run loop is blocked in GC, senders can accumulate. GC failure closes all waiters and reschedules. Pause threshold is clamped to avoid overscheduling, but very small GC durations are floored to 5ms.

## Test Signals
`scheduler_test.go` covers pause threshold limiting, deletion threshold triggering, manual trigger wait, and startup delay behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/scheduler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/scheduler_test.go -->
# sources/cloud-native/containerd/plugins/gc/scheduler_test.go

## Purpose
Unit tests the GC scheduler timing and trigger policy.

## Important APIs, Types, And Functions
Tests include `TestPauseThreshold`, `TestDeletionThreshold`, `TestTrigger`, and `TestStartupDelay`. `testCollector` implements mutation callbacks and `GarbageCollect`. `gcStats` supplies elapsed duration.

## Control Flow
Tests instantiate schedulers with controlled configs and collectors, run them in a goroutine using test contexts, trigger mutations or waits, sleep/select for expected scheduling, and assert run counts or elapsed stats.

## State And Persistence
All state is in-memory. The collector only increments counters and returns synthetic elapsed times.

## Dependencies And Integration Points
Uses `testing`, `sync`, `time`, `tomlext`, `pkg/gc`, and `testify/assert`. Directly targets `newScheduler`, `run`, `wait`, and callback behavior.

## Risks
Timing-sensitive sleeps can be flaky under very slow CI. Tests do not cover GC failure, mutation threshold behavior, context cancellation while waiting, or waiter notification ordering.

## Test Signals
Provides targeted confidence for core scheduling heuristics and manual synchronous GC.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/gc/scheduler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/path_unix.go -->
# sources/cloud-native/containerd/plugins/imageverifier/path_unix.go

## Purpose
Defines the default image verifier binary directory for non-Windows platforms.

## Important APIs, Types, And Functions
Package variable `defaultPath` is `/opt/containerd/image-verifier/bin`.

## Control Flow
No runtime control flow beyond package initialization.

## State And Persistence
No persistence. The path is consumed by default image verifier configuration.

## Dependencies And Integration Points
Compiled under `!windows` and used by `plugin.go` default config.

## Risks
Hard-coded absolute path may not exist; verifier discovery/runtime behavior must handle missing binaries.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/path_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/path_windows.go -->
# sources/cloud-native/containerd/plugins/imageverifier/path_windows.go

## Purpose
Defines the default image verifier binary directory for Windows.

## Important APIs, Types, And Functions
Package variable `defaultPath` joins `defaults.DefaultRootDir`, `opt`, `image-verifier`, and `bin`.

## Control Flow
No runtime control flow beyond package initialization.

## State And Persistence
No persistence. It derives a path from containerd defaults.

## Dependencies And Integration Points
Compiled on Windows and consumed by image verifier plugin defaults.

## Risks
Path semantics depend on `defaults.DefaultRootDir`; missing verifier binaries are handled downstream.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/plugin.go -->
# sources/cloud-native/containerd/plugins/imageverifier/plugin.go

## Purpose
Registers the default `bindir` image verifier plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.ImageVerifierPlugin` with ID `bindir`. `defaultConfig` returns `bindir.Config` with binary directory, maximum concurrent verifiers, and per-verifier timeout.

## Control Flow
Plugin init casts config to `*bindir.Config` and returns `bindir.NewImageVerifier`.

## State And Persistence
No persistent state is owned here. Runtime verifier behavior depends on executable files in the configured directory.

## Dependencies And Integration Points
Integrates with `pkg/imageverifier/bindir`, platform-specific `defaultPath`, and `tomlext.Duration`.

## Risks
Misconfigured or missing verifier binaries affect image verification. Timeout and concurrency defaults gate verifier process behavior.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/imageverifier/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/leases/local.go -->
# sources/cloud-native/containerd/plugins/leases/local.go

## Purpose
Registers the local lease manager plugin and adds synchronous-delete GC behavior.

## Important APIs, Types, And Functions
`gcScheduler` abstracts `ScheduleAndWait`. `local` embeds `leases.Manager` and overrides `Delete`. `init` constructs a metadata lease manager and stores the GC scheduler dependency.

## Control Flow
Startup gets metadata DB and GC scheduler, returns a `local` manager. Delete applies delete options, deletes the lease through the embedded manager, then triggers and waits for GC when `leases.SynchronousDelete` is requested.

## State And Persistence
Lease data is persisted in metadata DB. GC may remove unreferenced content/snapshots after lease deletion.

## Dependencies And Integration Points
Requires metadata and GC plugins. The gRPC leases service depends on this plugin and exposes synchronous delete through request flags.

## Risks
If GC fails after lease deletion, the delete call returns an error even though the lease is already removed. Synchronous delete latency depends on full metadata GC duration.

## Test Signals
No direct tests here; lease service and GC scheduler tests cover adjacent behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/leases/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/metadata/plugin.go -->
# sources/cloud-native/containerd/plugins/metadata/plugin.go

## Purpose
Registers the Bolt-backed metadata DB plugin that centralizes containerd metadata, content labels/policy, snapshotter references, and event publishing.

## Important APIs, Types, And Functions
`BoltConfig` controls content sharing policy and unsafe async bbolt mode. `Validate` accepts `shared` or `isolated`. The plugin init opens `meta.db`, configures bbolt options, gathers content store, snapshotters, and event publisher, creates `metadata.DB`, and initializes it.

## Control Flow
Startup creates the root directory, loads dependencies, sets bbolt options including no freelist sync and configurable open timeout, validates sharing policy, records plugin exports (`policy`, `path`), logs slow opens after 10 seconds, opens `meta.db`, builds DB options with event publisher and optional isolated policy, initializes metadata buckets, and returns the DB.

## State And Persistence
Persists all metadata in `meta.db` under the plugin root. Content sharing policy and no-sync settings affect persistence semantics. Snapshotter map and content store are attached to the metadata DB.

## Dependencies And Integration Points
Requires content, event, and snapshot plugins. Integrates with bbolt, timeout registry, metadata stores, content store policy, event publisher, and downstream services such as images, containers, leases, diff, and CRI.

## Risks
`NoSync`/`NoGrowSync` improve performance at data-loss risk. Bolt open can wait indefinitely by default. Invalid sharing policy prevents startup. Directory mode and DB file permissions are security-sensitive.

## Test Signals
No direct tests in this subset; nearly all containerd integration tests depend on this plugin.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/metadata/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux.go -->
# sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux.go

## Purpose
Registers a Linux EROFS mount handler supporting raw file-backed mounts, loop-device fallback, multi-device options, fsmount fallback, and optional dm-verity device setup/cleanup.

## Important APIs, Types, And Functions
`erofsMountHandler` implements `mount.Handler`. `Mount` handles EROFS mount activation. `setupDmVerityDevice`, `waitForDevice`, `doMount`, and `Unmount` manage dm-verity and mount syscalls. `Config` is empty plugin config.

## Control Flow
Mount rejects non-EROFS types, parses `X-containerd.dmverity=`, reads metadata and opens/reuses a dm-verity device when present, filters internal options, creates the mount point, tries file-backed fsmount unless loop fallback is forced, on `ENOTBLK` sets up loop devices for source and `device=` options, mounts, and returns `ActiveMount`. Unmount looks up the source, unmounts, and closes matching `/dev/mapper/containerd-erofs-*` devices.

## State And Persistence
Mount state is kernel state plus loop/dm-verity devices. It creates mount-point directories and may create device-mapper devices. `forceloop` is process-global after raw file mount fails.

## Dependencies And Integration Points
Uses core mount APIs, `internal/dmverity`, `internal/fsmount`, Unix errors, plugin registry, and EROFS differ sidecar metadata.

## Risks
Device-mapper cleanup is best-effort and tied to source naming. `forceloop` globally changes future behavior. Loop device setup for `device=` options must match multi-device EROFS images. Mount requires Linux kernel support and privileges.

## Test Signals
`plugin_linux_test.go` covers fsmount loop-device mounting and fsmount behavior with long option lists under privileged Linux environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux_test.go -->
# sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux_test.go

## Purpose
Integration-style tests for Linux EROFS mounting through loop devices and fsmount behavior.

## Important APIs, Types, And Functions
`TestFsmountLoopDevice` creates an EROFS image, attaches a loop device, mounts it with `fsmount`, and reads a file. `TestMountOptionsPageSizeLimit` demonstrates traditional mount option length failure and fsmount success.

## Control Flow
Tests require root, `mkfs.erofs`, kernel EROFS support, and fsmount support. They build temporary EROFS images from a directory, attach loop devices, mount under temp mount points, inspect file contents, and unmount/detach.

## State And Persistence
Uses temporary directories, loop devices, kernel mounts, and generated EROFS images. Cleanup closes loop files and unmounts where needed.

## Dependencies And Integration Points
Depends on `testutil.RequiresRoot`, `internal/fsmount`, core mount helpers, `plugins/snapshots/erofs.FindErofs`, `mkfs.erofs`, and Linux syscalls.

## Risks
Environment-sensitive skips mean CI without privileges/tooling misses coverage. Tests can leave mounts/loop devices if cleanup paths fail.

## Test Signals
Strong signal for privileged Linux fsmount and EROFS image readability, plus regression coverage for PAGE_SIZE option limit handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/fsview/erofs/erofs.go -->
# sources/cloud-native/containerd/plugins/mount/fsview/erofs/erofs.go

## Purpose
Registers an fsview handler that can inspect EROFS images without mounting them through the kernel.

## Important APIs, Types, And Functions
`handleMount` opens the EROFS source and extra `device=` readers, calls `erofs.Open`, and returns an `erofsView`. `erofsView.Close` closes all files. `getxattr` reads EROFS xattrs from `erofs.Stat`. `isWhiteout` identifies char-device whiteouts with rdev zero.

## Control Flow
The init function registers `handleMount`, `getxattr`, and `isWhiteout`. `handleMount` rejects non-EROFS mounts, opens source and extra devices, cleans up on error, requires `fs.ReadLinkFS`, and returns a closable read-link filesystem view.

## State And Persistence
No persistence. It opens file descriptors for EROFS images and closes them through the view.

## Dependencies And Integration Points
Integrates with `internal/fsview`, core mount types, `github.com/erofs/go-erofs`, xattr handling, and whiteout detection used by archive/diff logic.

## Risks
All opened readers must be closed on every error path. Only `device=` options are interpreted. If go-erofs does not expose expected `erofs.Stat`, xattr and whiteout detection return false.

## Test Signals
No direct tests in this subset. Covered indirectly by EROFS diff/view integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/fsview/erofs/erofs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/manager.go -->
# sources/cloud-native/containerd/plugins/mount/manager.go

## Purpose
Registers the Bolt-backed mount manager plugin that tracks activated mounts and delegates type-specific mount handling.

## Important APIs, Types, And Functions
Plugin init gathers mount handlers, configures `manager.WithMountHandler` and allowed roots, opens `mounts.db`, creates `manager.NewManager`, optionally runs `Sync`, and registers metadata collectible resources.

## Control Flow
Startup loads metadata, optional mount handlers, creates a target directory under plugin state, permits the parent of the containerd root as an allowed root, opens a bbolt DB, constructs the manager, starts a readiness-gated background sync transaction when supported, registers mount resources for GC if the manager implements `metadata.Collector`, and returns it.

## State And Persistence
Persists mount activation metadata in `mounts.db` and creates target mount directories under `state/t`. Kernel mount state is reconciled by optional sync.

## Dependencies And Integration Points
Requires metadata and mount-handler plugins. Uses bbolt, metadata bolt transaction context, mount manager package, and metadata GC resource registration. The mounts service and walking applier can depend on it.

## Risks
Sync runs in a goroutine but daemon readiness waits through the registered callback. DB open/create failures prevent startup. Allowed-root policy is broad enough to include the containerd root parent.

## Test Signals
No direct tests in this subset; mount service and integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/mount/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/nri/plugin.go -->
# sources/cloud-native/containerd/plugins/nri/plugin.go

## Purpose
Registers the Node Resource Interface API plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.NRIApiPlugin` with ID `nri`, default NRI config, and `initFunc`. `initFunc` calls `nri.New`.

## Control Flow
Startup requires the internal plugin type, casts config to `*nri.Config`, constructs the NRI listener/service, and returns it.

## State And Persistence
No direct persistence in this wrapper. Runtime state is managed by the internal NRI package.

## Dependencies And Integration Points
Integrates with `internal/nri` and plugin registry. Other CRI/runtime paths can use the NRI API plugin.

## Risks
All validation and side effects are delegated to `nri.New`; this wrapper has little defensive logic beyond dependency registration.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/nri/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/restart/change.go -->
# sources/cloud-native/containerd/plugins/restart/change.go

## Purpose
Defines restart monitor actions for stopping and starting containers to reconcile desired restart state.

## Important APIs, Types, And Functions
`stopChange.apply` kills/deletes an existing task. `startChange.apply` updates restart count labels, creates a new task with configured logging, and starts it. `killTask` kills and deletes an existing task if present.

## Control Flow
Start change loads the OCI spec to determine TTY logging, parses log URI when configured, updates restart count label, kills any existing task, creates a new task with selected `cio` logging, and starts it. `killTask` waits on the task, sends SIGKILL with kill-all, waits for exit, and deletes the task, tolerating some delete-after-error cases.

## State And Persistence
Updates container labels for restart counts and mutates task runtime state by killing/deleting/creating tasks. It does not change restart policy labels.

## Dependencies And Integration Points
Uses containerd client container/task APIs, restart labels, `cio` logging helpers, URL parsing, and syscall signals. Called from `monitor.go`.

## Risks
Force-killing tasks is disruptive but intentional for reconciliation. If task status/wait/delete behavior differs by runtime, errors may leave tasks partially cleaned. Unsupported legacy logpath is handled in monitor, not here.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/restart/change.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/restart/monitor.go -->
# sources/cloud-native/containerd/plugins/restart/monitor.go

## Purpose
Registers and runs the container restart monitor plugin, reconciling container restart labels against actual task status across namespaces.

## Important APIs, Types, And Functions
`Config` controls reconcile interval. `monitor.run`, `reconcile`, and `monitor` implement the polling loop. The config migration moves legacy `internal.restart` config to `container-monitor.restart`.

## Control Flow
Startup advertises restart capabilities, builds an in-memory containerd client, starts the monitor loop, and returns the monitor. Each loop lists namespaces, concurrently scans containers with restart status labels per namespace, computes start/stop changes based on desired status, task status, and `restart.Reconcile`, then concurrently applies changes.

## State And Persistence
Desired state and restart counters live in container labels. Actual task state lives in runtime/shims. The monitor itself holds only a client.

## Dependencies And Integration Points
Requires event and service plugins, uses containerd client APIs, namespaces, restart policy helpers, plugin config migration, and logging.

## Risks
Polling interval controls responsiveness. Namespace and change loops run concurrently and may race with user operations. A known issue is empty task status after failed/deleted tasks affecting `on-failure` reconciliation.

## Test Signals
No direct tests in this subset. Restart behavior requires integration tests with task lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/restart/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/sandbox/controller.go -->
# sources/cloud-native/containerd/plugins/sandbox/controller.go

## Purpose
Registers the shim-backed sandbox controller plugin that creates, starts, stops, waits, queries, and shuts down runtime v2 sandbox shims.

## Important APIs, Types, And Functions
`controllerLocal` implements `sandbox.Controller`. Key methods are `Create`, `Start`, `Platform`, `Stop`, `Shutdown`, `Wait`, `Status`, `Metrics`, `Update`, and `getSandbox`. `cleanupShim` handles failed creation/start cleanup.

## Control Flow
Startup loads shim manager and event exchange, creates/chmods root and state directories, loads existing shims, and returns a controller. Create ensures no existing shim, creates a bundle, starts a shim, builds a sandbox TTRPC client, and calls `CreateSandbox`. Start calls `StartSandbox` and returns instance metadata. Stop/Shutdown/Wait/Status/Metrics forward to shim sandbox services with error translation and cleanup behavior.

## State And Persistence
Bundles, shim state, and root/state directories are persisted under plugin paths. Active shim processes and TTRPC endpoints represent runtime state. Existing shims are loaded on daemon startup.

## Dependencies And Integration Points
Requires shim and event exchange plugins. Integrates with runtime v2 shim manager, sandbox API, mount proto conversion, typeurl options, errgrpc translation, and containerd sandbox core interfaces.

## Risks
Cleanup paths must shut down shim services and delete shim state to avoid leaks. Status returns an exited status when the shim is not found. `Update` is currently a no-op. Directory permission changes matter for upgrades and security.

## Test Signals
No direct tests in this subset; runtime sandbox service integration tests are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/sandbox/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/debug/plugin.go -->
# sources/cloud-native/containerd/plugins/server/debug/plugin.go

## Purpose
Registers the optional debug HTTP server exposing the internal pprof handler.

## Important APIs, Types, And Functions
`config` stores address/UID/GID. `server.Start` opens a Unix/local or TCP listener and serves the configured HTTP server. `Close` closes the HTTP server.

## Control Flow
Startup skips if no address is configured, looks up the `pprof` HTTP handler, returns a server wrapper, and logs/skips if pprof is not found. Start chooses local listener for local addresses or TCP for others and delegates serving to `internal.Serve`.

## State And Persistence
No persistence. It owns a listener and HTTP server lifecycle.

## Dependencies And Integration Points
Depends on HTTP handler plugins, internal pprof registration, `pkg/sys.GetLocalListener`, and shared server `internal.Serve`.

## Risks
Debug endpoints can expose sensitive process information; configuration must bind appropriately. Missing pprof handler skips the server.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/debug/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/metrics.go -->
# sources/cloud-native/containerd/plugins/server/grpc/metrics.go

## Purpose
Registers gRPC metrics plugins for Prometheus and OpenTelemetry instrumentation.

## Important APIs, Types, And Functions
`metricsConfig` controls Prometheus handling-time histograms. The `grpc-prometheus` plugin returns `*grpc_prometheus.ServerMetrics`; the `grpc-otel` plugin returns an `otelgrpc` stats handler.

## Control Flow
Prometheus init creates optional histogram settings, registers metrics with the default Prometheus registry, and returns the metrics object. OTEL init returns a new server handler.

## State And Persistence
Metrics/tracing state is process-local and exported through configured telemetry pipelines.

## Dependencies And Integration Points
Requires gRPC plugin type, integrates with `server/grpc/plugin.go` to install interceptors and stats handlers.

## Risks
Prometheus global registration can fail/panic on duplicate registrations in unusual test processes. Histogram enablement increases metric cardinality/cost.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/namespace.go -->
# sources/cloud-native/containerd/plugins/server/grpc/namespace.go

## Purpose
Provides gRPC interceptors that preserve namespace context from incoming metadata into outgoing context values.

## Important APIs, Types, And Functions
`unaryNamespaceInterceptor` wraps unary calls. `streamNamespaceInterceptor` wraps stream calls with `wrappedSSWithContext`. `wrappedSSWithContext.Context` returns the replacement context.

## Control Flow
Each interceptor checks `namespaces.Namespace(ctx)`, and when present, re-applies it with `namespaces.WithNamespace` before invoking the handler.

## State And Persistence
No persistence. It only modifies request context.

## Dependencies And Integration Points
Used by gRPC server construction for all registered services. Depends on containerd namespace metadata helpers and gRPC interceptors.

## Risks
If namespace metadata parsing changes, all services can receive incorrect namespace context. Streams require wrapper correctness to avoid losing other stream behavior.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/plugin.go -->
# sources/cloud-native/containerd/plugins/server/grpc/plugin.go

## Purpose
Registers the main local gRPC server and optional TCP gRPC server, wiring registered service plugins, namespace interceptors, telemetry, message size limits, and TLS.

## Important APIs, Types, And Functions
`config` controls local endpoint settings. `tcpConfig` controls TCP/TLS settings. `grpcServer` and `tcpServer` implement server lifecycle. Init registers `grpc` and `grpc-tcp` server plugins.

## Control Flow
Local server init validates address, builds interceptor and stats options from metrics plugins, configures message size limits, creates a gRPC server, iterates all initialized gRPC plugins and calls `Register`, initializes Prometheus metrics, and returns `grpcServer`. TCP init skips without address, builds similar options, configures file-based TLS or Windows cert-store TLS, registers only services supporting `RegisterTCP`, requires at least one, and returns `tcpServer`.

## State And Persistence
No persistent state. It owns gRPC server instances, local/TCP listeners, and optional cached Windows TLS resources.

## Dependencies And Integration Points
Requires gRPC and metrics plugins. Integrates with `pkg/sys.GetLocalListener`, `internal.Serve`, TLS credentials, Windows TLS helper, Prometheus/OTEL plugins, and all service plugins implementing registration interfaces.

## Risks
Iterating all plugins intentionally ignores failed service plugin instances. TLS configuration must be correct for TCP exposure. `TLSCName` path uses Windows cert-store resources that need cleanup. Empty local address is invalid while empty TCP address skips.

## Test Signals
No direct tests in this subset; daemon startup and service integration tests cover registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/tls_other.go -->
# sources/cloud-native/containerd/plugins/server/grpc/tls_other.go

## Purpose
Provides non-Windows no-op TLS resource cleanup hooks for the gRPC TCP server.

## Important APIs, Types, And Functions
`setTLSResource` and `cleanupTLSResources` accept/handle `wintls.CertResource` but do nothing.

## Control Flow
No-op functions are called from shared gRPC server code when Windows cert-store TLS is not active.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Compiled under `!windows`; preserves shared code compatibility with Windows TLS helper types.

## Risks
None beyond ensuring no non-Windows resource cleanup is needed.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/tls_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/tls_windows.go -->
# sources/cloud-native/containerd/plugins/server/grpc/tls_windows.go

## Purpose
Stores and releases Windows certificate-store TLS resources used by the TCP gRPC server.

## Important APIs, Types, And Functions
Package variable `tlsResource` holds a `wintls.CertResource`. `setTLSResource` caches it. `cleanupTLSResources` closes it and logs failures.

## Control Flow
When TCP gRPC config uses a Windows certificate common name, setup stores the returned resource. Server close calls cleanup, which closes and clears the resource if present.

## State And Persistence
State is a process-global cached certificate resource handle. No file persistence.

## Dependencies And Integration Points
Windows-only; integrates with `internal/wintls` and `grpc-tcp` server shutdown.

## Risks
Global single-resource storage assumes one TCP server instance. Cleanup failures are logged but not returned from server close.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/grpc/tls_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/listen_unix.go -->
# sources/cloud-native/containerd/plugins/server/internal/listen_unix.go

## Purpose
Classifies local listener addresses on non-Windows platforms.

## Important APIs, Types, And Functions
`IsLocalAddress` returns `filepath.IsAbs(path)`.

## Control Flow
Server plugins call this helper to decide between local socket listener creation and TCP listening.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by debug server and shared local endpoint logic on Unix-like systems.

## Risks
Treating all absolute paths as local addresses is appropriate for Unix sockets but relies on callers not passing absolute TCP-like strings.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/listen_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/listen_windows.go -->
# sources/cloud-native/containerd/plugins/server/internal/listen_windows.go

## Purpose
Classifies local listener addresses on Windows.

## Important APIs, Types, And Functions
`IsLocalAddress` checks for the named-pipe prefix `\\.\pipe\`.

## Control Flow
Server plugins use this helper to choose local named-pipe listener handling versus TCP listening.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by debug and server listener setup on Windows.

## Risks
Only named-pipe addresses are considered local; other Windows path forms are treated as non-local.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/listen_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/serve.go -->
# sources/cloud-native/containerd/plugins/server/internal/serve.go

## Purpose
Provides shared asynchronous serving behavior for HTTP, gRPC, and TTRPC listeners.

## Important APIs, Types, And Functions
`Serve` logs the address, starts `serveFunc` in a goroutine, closes the listener on exit, and treats expected closed-server errors as non-fatal.

## Control Flow
The function captures listener address, logs, launches a goroutine, defers listener close, invokes the supplied serve function, and logs fatal only for unexpected errors not matching net/http/ttrpc closed conditions.

## State And Persistence
No persistence. Owns listener lifecycle after called.

## Dependencies And Integration Points
Used by debug, metrics, gRPC, and TTRPC server plugins. Depends on `net`, `http`, `ttrpc`, and logging.

## Risks
Unexpected serve errors call `Fatal`, terminating the daemon. Server start functions return after goroutine launch, so later bind/serve failures are asynchronous.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/internal/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/metrics/plugin.go -->
# sources/cloud-native/containerd/plugins/server/metrics/plugin.go

## Purpose
Registers the optional HTTP metrics endpoint server.

## Important APIs, Types, And Functions
`config` stores the address. `server.Start` listens on TCP and serves `/v1/metrics`. `Close` closes the HTTP server.

## Control Flow
Startup skips without an address, builds an HTTP mux with `metrics.Handler`, and returns a server. Start opens a TCP listener, constructs `http.Server` with a long read-header timeout, and delegates serving to `internal.Serve`.

## State And Persistence
No persistence. Owns an HTTP server and TCP listener.

## Dependencies And Integration Points
Uses `docker/go-metrics` handler and shared server internal serving logic. Exposes metrics registered by GC, gRPC, and other packages.

## Risks
Metrics endpoint exposure depends on configured address. Read header timeout is intentionally long, so deployments should bind to trusted interfaces.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/metrics/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/plugin.go -->
# sources/cloud-native/containerd/plugins/server/ttrpc/plugin.go

## Purpose
Registers the local TTRPC server endpoint and wires TTRPC-capable services.

## Important APIs, Types, And Functions
`config` stores endpoint address/UID/GID and implements getter/setter. `server.Start` opens a local listener and serves TTRPC. Init creates `newTTRPCServer`, registers services implementing `RegisterTTRPC`, and returns a server.

## Control Flow
Startup skips on empty address, creates platform-specific TTRPC server options, iterates all initialized TTRPC and gRPC plugin instances, calls `RegisterTTRPC` on supported services, requires at least one service, and returns the server wrapper. Start opens a local listener and serves with `context.WithoutCancel(ctx)`.

## State And Persistence
No persistence. Owns the TTRPC server and listener.

## Dependencies And Integration Points
Requires TTRPC and gRPC plugin types. Uses `pkg/sys.GetLocalListener`, `internal.Serve`, and platform-specific server constructors. Events service registers TTRPC forwarding here.

## Risks
Only services that implement `RegisterTTRPC` are exposed. Failed service plugins are skipped. The server uses a context without cancellation for serving, relying on server close/listener close for shutdown.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_linux.go -->
# sources/cloud-native/containerd/plugins/server/ttrpc/server_linux.go

## Purpose
Builds the Linux TTRPC server with same-user Unix socket handshaking and OpenTelemetry interception.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer` with `UnixSocketRequireSameUser` and `otelttrpc.UnaryServerInterceptor`.

## Control Flow
Called during TTRPC plugin init to construct the server before service registration.

## State And Persistence
No persistence; configures runtime server behavior.

## Dependencies And Integration Points
Linux-only. Integrates with containerd TTRPC server plugin and OpenTelemetry TTRPC instrumentation.

## Risks
Same-user enforcement affects client compatibility and security posture.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_otel.go -->
# sources/cloud-native/containerd/plugins/server/ttrpc/server_otel.go

## Purpose
Builds TTRPC servers with OpenTelemetry interception for Windows and Solaris.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer` with `otelttrpc.UnaryServerInterceptor`.

## Control Flow
Called by the shared TTRPC server plugin at initialization.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Compiled under `windows || solaris`; integrates with TTRPC plugin and OpenTelemetry.

## Risks
Unlike Linux, this constructor does not install Unix same-user handshaking, matching platform capabilities.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_otel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_other.go -->
# sources/cloud-native/containerd/plugins/server/ttrpc/server_other.go

## Purpose
Builds a default TTRPC server on platforms that are not Linux, Windows, or Solaris.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer()` with no extra options.

## Control Flow
Called by shared TTRPC plugin initialization.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Compiled under `!linux && !windows && !solaris`.

## Risks
No OTEL interceptor or same-user handshaker is installed on these platforms.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/server/ttrpc/server_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/helpers.go -->
# sources/cloud-native/containerd/plugins/services/containers/helpers.go

## Purpose
Converts containerd core container records to and from gRPC API protobuf structures.

## Important APIs, Types, And Functions
`containersToProto`, `containerToProto`, and `containerFromProto` map IDs, labels, image, runtime info, specs, snapshot metadata, extensions, timestamps, and sandbox IDs.

## Control Flow
Conversion to proto marshals runtime options and extensions through typeurl and timestamps through protobuf helpers. Conversion from proto reconstructs runtime info and extension map without timestamp fields.

## State And Persistence
No persistence. These functions define the service boundary representation used when storing or returning container metadata.

## Dependencies And Integration Points
Used by local and gRPC containers services. Depends on API types, core containers, protobuf timestamp helpers, and typeurl.

## Risks
`containerFromProto` does not populate created/updated timestamps, leaving store logic to manage them. Typeurl marshaling assumes extension values are compatible.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/local.go -->
# sources/cloud-native/containerd/plugins/services/containers/local.go

## Purpose
Registers and implements the local containers service client backed by metadata DB and event publishing.

## Important APIs, Types, And Functions
`local` embeds `containers.Store` and implements `api.ContainersClient`. Methods include `Get`, `List`, `ListStream`, `Create`, `Update`, `Delete`, and transaction helpers. `localStream` implements the client streaming interface for in-memory listing.

## Control Flow
Startup obtains metadata DB and event publisher, creates a metadata container store, and returns `local`. Read methods run in DB view transactions; create/update/delete run in update transactions, convert proto/core types, then publish container events after successful mutation. `ListStream` materializes all results into an in-memory stream.

## State And Persistence
Container metadata is persisted in metadata DB. Events are published through the in-memory event exchange after mutations.

## Dependencies And Integration Points
Requires event and metadata plugins. Integrates with metadata transactions, containers store, protobuf helpers, errgrpc conversion, and event types.

## Risks
Events are emitted after DB commit; event publish failures return errors even after metadata changes. `ListStream` buffers all containers rather than streaming from the DB cursor. Update requires non-empty container ID.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/service.go -->
# sources/cloud-native/containerd/plugins/services/containers/service.go

## Purpose
Registers the gRPC containers service as a thin adapter over the local containers client.

## Important APIs, Types, And Functions
`service` embeds `UnimplementedContainersServer` and implements `Register`, `Get`, `List`, `ListStream`, `Create`, `Update`, and `Delete`.

## Control Flow
Startup gets the local containers service by ID and wraps it. gRPC methods forward to the local client. `ListStream` receives from the local stream until EOF or context cancellation and sends each item to the gRPC stream.

## State And Persistence
No direct state. Persistence is handled by the local containers service.

## Dependencies And Integration Points
Requires service plugin, registers with the main gRPC server, and bridges API server/client interfaces.

## Risks
Context cancellation in `ListStream` returns nil, which can hide client-side cancellation details. All validation is delegated to local service.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/containers/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/contentserver/contentserver.go -->
# sources/cloud-native/containerd/plugins/services/content/contentserver/contentserver.go

## Purpose
Implements the gRPC content service over a containerd content store, including info/update/list/delete/read/write/status/abort operations.

## Important APIs, Types, And Functions
`service` holds a `content.Store`. `New` returns an API server. Methods include `Info`, `Update`, `List`, `Delete`, `Read`, `Status`, `ListStatuses`, `Write`, and `Abort`. `readResponseWriter`, `infoToGRPC`, and `infoFromGRPC` handle streaming and conversion. `bufPool` reuses 1 MiB buffers.

## Control Flow
Read validates digest, bounds offset/size, opens a reader, and streams chunks through `readResponseWriter`. Write receives an initial ref message, opens a content writer, loops over stat/write/commit actions, validates offsets, truncates when restarting at zero, detects existing expected digests, writes data, commits with labels on commit, and sends status responses. List batches content info in groups of 100.

## State And Persistence
Persists content blobs, ingest status, and labels through the content store. Write may abort ingests on duplicate expected digest. Read/list/status are read-only.

## Dependencies And Integration Points
Used by the content gRPC plugin. Depends on content store APIs, OCI descriptors, digest parsing, errgrpc, protobuf timestamps, and gRPC streaming.

## Risks
Streaming write protocol is stateful and sensitive to offset mismatches. Duplicate expected digest aborts the current ref. Final defer attempts to send the last message only on success. Buffer reuse must not retain mutable response data beyond send semantics.

## Test Signals
No direct tests in this subset; content service integration tests cover protocol behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/contentserver/contentserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/service.go -->
# sources/cloud-native/containerd/plugins/services/content/service.go

## Purpose
Registers the gRPC content service plugin.

## Important APIs, Types, And Functions
`init` registers gRPC plugin ID `content`; init loads the content service plugin and wraps it with `contentserver.New`.

## Control Flow
During startup, the plugin retrieves `services.ContentService`, asserts it is a content store, constructs the gRPC server, and returns it for registration by the main gRPC server.

## State And Persistence
No state here; persistence is in the underlying content store.

## Dependencies And Integration Points
Requires service plugin and integrates with `contentserver` and gRPC server registration.

## Risks
Type assertion assumes the service plugin returns `content.Store`.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/store.go -->
# sources/cloud-native/containerd/plugins/services/content/store.go

## Purpose
Registers the local content service backed by metadata DB.

## Important APIs, Types, And Functions
`init` registers `services.ContentService` and returns `metadata.DB.ContentStore()`.

## Control Flow
Startup retrieves the metadata plugin and exposes its content store as a service plugin.

## State And Persistence
Content blob metadata and labels are managed by metadata DB; blob storage is through the underlying content store attached to metadata.

## Dependencies And Integration Points
Requires metadata plugin. Used by content gRPC service and other in-memory clients.

## Risks
The plugin is a thin type assertion wrapper; metadata plugin availability and correctness are prerequisites.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/content/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/local.go -->
# sources/cloud-native/containerd/plugins/services/diff/local.go

## Purpose
Registers and implements the local diff service client that selects an ordered chain of differs for apply and diff operations.

## Important APIs, Types, And Functions
`config` controls differ order and global `sync_fs`. `differ` combines comparer and applier. `local.Apply` and `local.Diff` implement the API client by translating protobuf mounts/descriptors/options and trying differs in order.

## Control Flow
Startup loads all diff plugins, validates configured order names and interfaces, and returns `local`. Apply converts the descriptor and mounts, decodes payloads, enforces global syncfs if configured, calls each differ until an error other than `ErrNotImplemented`, and returns the applied descriptor. Diff converts mounts, maps media/ref/labels/source-date options, tries compares in order, and returns the diff descriptor.

## State And Persistence
No direct persistence. Underlying differs write content store blobs or snapshot layer files depending on operation.

## Dependencies And Integration Points
Depends on diff plugins, mount/proto conversion, OCI descriptor conversion, typeurl payloads, errgrpc, and platform-specific default config files.

## Risks
If configured differ order references a missing plugin, startup fails. Fallback only works for errors recognized as `ErrNotImplemented`. Global syncfs overrides request behavior.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service.go -->
# sources/cloud-native/containerd/plugins/services/diff/service.go

## Purpose
Registers the gRPC diff service adapter.

## Important APIs, Types, And Functions
`service` wraps a `diffapi.DiffClient` and implements `Register`, `Apply`, and `Diff`.

## Control Flow
Startup gets the local diff service by ID, wraps it, and the main gRPC server later calls `Register`. RPC methods forward directly to the local client.

## State And Persistence
No direct state; underlying diff service and differ implementations perform state changes.

## Dependencies And Integration Points
Requires service plugin and registers with gRPC. Bridges remote API calls to local differ chain.

## Risks
All validation and fallback logic are delegated to the local client.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_darwin.go -->
# sources/cloud-native/containerd/plugins/services/diff/service_darwin.go

## Purpose
Defines Darwin default differ ordering.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["erofs", "walking"]` and `SyncFs` false.

## Control Flow
Loaded as package-level default config for the diff service on Darwin.

## State And Persistence
No state beyond default configuration.

## Dependencies And Integration Points
Used by `local.go` service registration.

## Risks
If EROFS plugin is unavailable and still listed as required, diff service startup can fail unless plugin loading/config generation accounts for support.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_unix.go -->
# sources/cloud-native/containerd/plugins/services/diff/service_unix.go

## Purpose
Defines default differ ordering for Unix platforms other than Windows and Darwin.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["walking"]` and `SyncFs` false.

## Control Flow
Loaded as package-level config for diff service registration.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Used by `local.go` to select diff plugins.

## Risks
Only walking differ is tried by default, so specialized differs must be configured or platform-specific defaults must change to use them.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_windows.go -->
# sources/cloud-native/containerd/plugins/services/diff/service_windows.go

## Purpose
Defines Windows default differ ordering.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["windows", "windows-lcow"]` and `SyncFs` false.

## Control Flow
Loaded as package-level config for Windows diff service registration.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Pairs the WCOW differ with LCOW fallback in `local.go`.

## Risks
Startup requires both configured differ plugins to load. Fallback depends on WCOW differ returning `ErrNotImplemented` for LCOW mounts.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/diff/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/events/service.go -->
# sources/cloud-native/containerd/plugins/services/events/service.go

## Purpose
Registers the gRPC events service and exposes event publish, forward, subscribe, and TTRPC forwarding.

## Important APIs, Types, And Functions
`NewService` returns an `api.EventsServer`. `service.Register`, `RegisterTTRPC`, `Publish`, `Forward`, `Subscribe`, `toProto`, and `fromProto` implement event service behavior.

## Control Flow
Startup gets the event exchange plugin and returns the service. Publish sends raw topic/event to exchange. Forward converts an envelope and forwards it. Subscribe creates an exchange subscription with filters, loops sending protobuf envelopes until an error or completion.

## State And Persistence
Events are in-memory exchange messages. No persistence is handled by this service.

## Dependencies And Integration Points
Requires event exchange. Registers with both gRPC and TTRPC server plugins. Uses typeurl and protobuf timestamp conversion.

## Risks
Subscribe blocks per stream and returns send/subscription errors. Event payloads depend on typeurl marshaling compatibility.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/events/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/events/ttrpc.go -->
# sources/cloud-native/containerd/plugins/services/events/ttrpc.go

## Purpose
Implements the TTRPC subset of the events service, currently forwarding event envelopes.

## Important APIs, Types, And Functions
`ttrpcService` holds the exchange. `Forward` converts TTRPC request envelope and forwards it. `fromTProto` converts API envelope to core event envelope.

## Control Flow
TTRPC server invokes `Forward`, which delegates to exchange forwarding and returns an empty response or gRPC-compatible error.

## State And Persistence
No persistence; event exchange is in-memory.

## Dependencies And Integration Points
Registered from `events/service.go` via `RegisterTTRPC`. Uses TTRPC events API, core events, protobuf timestamps, and errgrpc conversion.

## Risks
Only forwarding is exposed over TTRPC, not subscribe/publish. Payload type compatibility is delegated to event consumers.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/events/ttrpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/healthcheck/service.go -->
# sources/cloud-native/containerd/plugins/services/healthcheck/service.go

## Purpose
Registers the standard gRPC health checking service.

## Important APIs, Types, And Functions
`service` wraps `*health.Server`. `newService` constructs it. `Register` registers `grpc_health_v1.HealthServer`.

## Control Flow
Plugin init returns a new health service without dependencies. The gRPC server later registers it.

## State And Persistence
Health status state is in-memory inside `health.Server`.

## Dependencies And Integration Points
Depends on gRPC health package and plugin registry. Exposed by the main gRPC server.

## Risks
No service statuses are configured here; default behavior depends on `health.Server`.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/healthcheck/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/helpers.go -->
# sources/cloud-native/containerd/plugins/services/images/helpers.go

## Purpose
Converts core image records to and from image service protobuf structures.

## Important APIs, Types, And Functions
`imagesToProto`, `imageToProto`, and `imageFromProto` map names, labels, target descriptors, and timestamps.

## Control Flow
Conversion to proto maps OCI descriptors through `oci.DescriptorToProto` and timestamps through protobuf helpers. Conversion from proto reconstructs core image fields.

## State And Persistence
No direct persistence. These mappings define service API representation.

## Dependencies And Integration Points
Used by local and gRPC image services. Depends on API image types, core images, OCI conversion, and protobuf timestamps.

## Risks
Descriptor conversion must preserve media type, digest, size, platform, and annotations correctly through helper APIs.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/local.go -->
# sources/cloud-native/containerd/plugins/services/images/local.go

## Purpose
Registers and implements the local images service client backed by metadata image store and optional synchronous GC.

## Important APIs, Types, And Functions
`local` stores an `images.Store`, `gcScheduler`, and warning service. It implements `Get`, `List`, `Create`, `Update`, and `Delete` for `imagesapi.ImagesClient`.

## Control Flow
Startup loads metadata, GC, and warning plugins, builds a metadata image store, and returns the local client. Create/update validate image name, optionally inject source-date epoch into context, write to the store, and return proto images. Delete optionally constrains target descriptor, deletes by name, and runs GC synchronously when requested.

## State And Persistence
Image records persist in metadata DB. Delete can trigger metadata GC to clean unreferenced resources. Source-date epoch context can affect timestamps created by lower layers.

## Dependencies And Integration Points
Requires metadata, GC, and warning plugins. Uses image store APIs, errgrpc, epoch context, OCI descriptor conversion, and protobuf helpers.

## Risks
Event publishing is not present here, unlike containers. Synchronous delete returns GC errors after image deletion. Warning service is stored but unused in this file.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/service.go -->
# sources/cloud-native/containerd/plugins/services/images/service.go

## Purpose
Registers the gRPC images service adapter.

## Important APIs, Types, And Functions
`service` wraps `imagesapi.ImagesClient` and implements `Register`, `Get`, `List`, `Create`, `Update`, and `Delete`.

## Control Flow
Startup retrieves the local images service and returns a gRPC server wrapper. RPC methods forward directly to the local client.

## State And Persistence
No direct state; metadata persistence is handled by the local image service.

## Dependencies And Integration Points
Requires service plugin and registers with the gRPC server.

## Risks
All validation, GC, and storage behavior is delegated to the local client.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/images/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/local.go -->
# sources/cloud-native/containerd/plugins/services/introspection/local.go

## Purpose
Registers and implements the local introspection service for plugin inventory, server identity, deprecation warnings, and plugin-specific extra info.

## Important APIs, Types, And Functions
`Local` stores plugin set, root, plugin cache, and warning client. Methods include `UpdateLocal`, `Plugins`, `Server`, `PluginInfo`, `getUUID`, `generateUUID`, `pluginToPB`, `pluginsToPB`, `warningsPB`, and `adaptPlugin`.

## Control Flow
Startup gets the deprecations warning service and captures the plugin set/root. `Plugins` parses filters and returns matching cached plugin protos. `Server` returns persisted daemon UUID, process ID, Linux PID namespace inode when available, and warning list. `PluginInfo` looks up a plugin, returns base metadata, optionally instantiates the plugin and calls its `PluginInfo` provider, then marshals extra data.

## State And Persistence
Persists a daemon UUID at `<root>/uuid`, generating it if missing or empty. Caches plugin protobufs in memory until plugin count changes. Warning state comes from the warning service.

## Dependencies And Integration Points
Requires warning/deprecation service. Integrates with plugin registry, filters, errgrpc/status conversion, typeurl, protobuf timestamps, OS process info, and platform-specific `statPIDNS`.

## Risks
Plugin cache invalidation only checks count, not metadata mutations. UUID file is written with mode `0666` subject to umask. Extra plugin info is unavailable for failed plugins and depends on optional provider interface.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/pidns_linux.go -->
# sources/cloud-native/containerd/plugins/services/introspection/pidns_linux.go

## Purpose
Reports the Linux PID namespace inode for the containerd process.

## Important APIs, Types, And Functions
`statPIDNS` stats `/proc/<pid>/ns/pid`, asserts `*syscall.Stat_t`, and returns inode number.

## Control Flow
Called by `Local.Server` on Linux. It reads procfs metadata and returns the namespace inode or an error.

## State And Persistence
No persistence; reads procfs.

## Dependencies And Integration Points
Linux-only; used by introspection server information.

## Risks
Fails if procfs is unavailable or stat sys type is unexpected. Errors propagate through the server info RPC.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/pidns_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/pidns_others.go -->
# sources/cloud-native/containerd/plugins/services/introspection/pidns_others.go

## Purpose
Provides a non-Linux stub for PID namespace reporting.

## Important APIs, Types, And Functions
`statPIDNS` returns zero and nil.

## Control Flow
No inspection occurs; non-Linux `Local.Server` receives a zero PID namespace value.

## State And Persistence
No state.

## Dependencies And Integration Points
Compiled under `!linux` to preserve shared introspection code.

## Risks
Clients must treat zero PID namespace as unsupported rather than a real namespace inode.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/pidns_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/service.go -->
# sources/cloud-native/containerd/plugins/services/introspection/service.go

## Purpose
Registers the gRPC introspection service adapter.

## Important APIs, Types, And Functions
`server` wraps `introspection.Service` and implements `Register`, `Plugins`, `Server`, and `PluginInfo`.

## Control Flow
Startup loads the local introspection service, updates its root from the current plugin context, and returns the gRPC wrapper. RPC methods forward to local service and convert errors. `PluginInfo` unmarshals optional typeurl options before forwarding.

## State And Persistence
No direct state beyond updating the local service root. UUID persistence is handled by `local.go`.

## Dependencies And Integration Points
Requires service plugin, gRPC, typeurl, errgrpc, and introspection API types.

## Risks
Startup requires the service implementation to be `*Local`; alternative implementations fail. Malformed options cause request failure before plugin lookup.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/introspection/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/leases/service.go -->
# sources/cloud-native/containerd/plugins/services/leases/service.go

## Purpose
Registers the gRPC leases service over the local lease manager.

## Important APIs, Types, And Functions
`service` wraps `leases.Manager` and implements `Register`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, `ListResources`, and `leaseToGRPC`.

## Control Flow
Startup loads the lease manager plugin. Create applies labels and either random or requested ID. Delete maps sync flag to `leases.SynchronousDelete`. Resource methods convert proto resource IDs/types and delegate. List converts all leases to proto.

## State And Persistence
Lease records and resources persist in metadata DB through the lease manager. Synchronous delete can trigger GC through the local manager wrapper.

## Dependencies And Integration Points
Requires lease plugin ID `manager`, gRPC server registration, errgrpc, protobuf timestamp conversion, and core leases APIs.

## Risks
Delete with sync can return GC errors after lease deletion. Resource requests assume non-nil resource fields.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/leases/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/mounts/service.go -->
# sources/cloud-native/containerd/plugins/services/mounts/service.go

## Purpose
Registers the gRPC mount manager service for activating, deactivating, inspecting, updating, and listing managed mounts.

## Important APIs, Types, And Functions
`service` wraps `mount.Manager` and implements `Register`, `Activate`, `Deactivate`, `Info`, `Update`, and `List`.

## Control Flow
Startup gets the mount manager plugin. Activate maps temporary and label options, converts proto mounts, delegates to `mm.Activate`, and returns activation info. Deactivate, Info, and Update forward to the manager. List streams converted activation info records to the client.

## State And Persistence
Mount activation state is managed by the mount manager and persisted in its DB. The service itself is stateless.

## Dependencies And Integration Points
Requires mount manager plugin, core mount/proxy conversion helpers, errgrpc, logging, and gRPC registration.

## Risks
Streaming list stops on first send error. Activation can create kernel mounts and persistent manager records, so errors must be interpreted through manager semantics.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/mounts/service.go -->
