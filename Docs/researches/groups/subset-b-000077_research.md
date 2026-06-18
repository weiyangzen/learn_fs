# subset-b-000077 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go

## Purpose
Linux-only integration and unit tests for the EROFS snapshotter, its writable sizing, fsverity, dm-verity, tar-index differ integration, and fsmeta mount construction. The file is the main behavioral safety net for EROFS-specific storage paths.

## Important APIs, Types, And Functions
Key helpers are `newSnapshotter`, `testMount`, `createTestTarContent`, `createDmverityMetadata`, and `createTestLayerBlob`. Test entry points include `TestErofs`, `TestErofsWithQuota`, `TestWritableSize`, `TestErofsFsverity`, `TestErofsDifferWithTarIndexMode`, `TestCreateErofsMount`, `TestDmverityEndToEnd`, `TestDmverityModeValidation`, `TestApplyDmverityPolicy`, and `TestMountFsMeta`.

## Control Flow
The generic snapshotter suite is run against EROFS only when root, `mkfs.erofs`, and kernel EROFS support are available. The tar-index and dm-verity tests build tar content, write it into a local content store, apply it with the EROFS differ, commit the snapshotter layer, then mount a view and verify files. dm-verity end-to-end routes view mounts through the mount manager and EROFS mount handler because the snapshotter only emits metadata-bearing mount options.

## State And Persistence
Tests create temporary snapshot roots, content stores, bbolt mount-manager DBs, snapshot metadata stores, layer blobs, `.dmverity` metadata files, and fsmeta files. Cleanup is handled with `t.Cleanup`, deferred `Close`, and explicit `Remove` calls in end-to-end paths.

## Dependencies And Integration Points
Depends on containerd content, mount, mount manager, snapshots storage/testsuite, local content store, EROFS differ, EROFS mount handler, `dmverity`, `erofsutils`, `fsverity`, tartest, namespaces, bbolt, and root/kernel/external-tool availability.

## Risks And Edge Cases
Most tests are environment-sensitive and skip when kernel support, mkfs features, fsverity, dm-verity, or root privileges are absent. The dm-verity policy tests protect the strict `"on"` mode from silently accepting old layers without metadata. `TestMountFsMeta` verifies that merged fsmeta device ordering follows reverse parent order, which is easy to regress.

## Test Signals
This file itself signals EROFS correctness: generic snapshotter behavior, configured/default writable size labels, fsverity immutability, differ-created layer existence, dm-verity activation through the mount manager, mode validation, and fsmeta mount options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go

## Purpose
Provides non-Linux stubs for EROFS platform operations so the package can compile while making Linux-only functionality explicitly unavailable.

## Important APIs, Types, And Functions
Defines `defaultWritableSize` as 64 MiB on non-Linux and stubs `checkCompatibility`, `setImmutable`, `cleanupUpper`, `convertDirToErofs`, and `getParentOwnership`.

## Control Flow
No real EROFS work is performed. Compatibility and cleanup are no-ops; immutable flag setting and directory-to-EROFS conversion return `errdefs.ErrNotImplemented`; ownership probing returns `-1, -1`.

## State And Persistence
No persistent state is created. The file intentionally avoids touching filesystem attributes or layer blobs on unsupported platforms.

## Dependencies And Integration Points
Compiled under `!linux`. It integrates with the common EROFS snapshotter code by satisfying platform-specific helper symbols and depends only on `context` and `errdefs`.

## Risks And Edge Cases
If common code invokes conversion or immutable operations on non-Linux, callers must surface `ErrNotImplemented` cleanly. The 64 MiB default writable size differs from Linux's zero default and can affect block-mode expectations in cross-platform configuration.

## Test Signals
No file-local tests. Coverage is compile-time plus any non-Linux package builds that exercise option parsing without invoking unsupported paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go

## Purpose
Registers the `erofs` snapshotter plugin and translates daemon TOML configuration into EROFS snapshotter options and plugin metadata.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `ovl_mount_options`, `enable_fsverity`, `set_immutable`, `default_size`, and `dmverity_mode`. `init` registers a `plugins.SnapshotPlugin` with ID `erofs`. Capability constants are `remap-ids` and `only-remap-ids`.

## Control Flow
At initialization, the plugin sets the default platform, validates `Config`, chooses `RootPath` or the plugin root property, appends EROFS options for overlay mount options, fsverity, immutable files, parsed default writable size, and dm-verity mode, then probes ID-mapped mount support. It always advertises `only-remap-ids` and `rebase`, and advertises `remap-ids` only when supported.

## State And Persistence
The plugin exports the snapshotter root via `plugins.SnapshotterRootDir`; persistent metadata and layer state are created by `erofs.NewSnapshotter`, not in this file.

## Dependencies And Integration Points
Integrates with `github.com/containerd/plugin/registry`, containerd plugin type constants, `platforms.DefaultSpec`, EROFS snapshotter options, and `docker/go-units` for size parsing. Platform probing is delegated to `supportsIDMappedMounts`.

## Risks And Edge Cases
Invalid `default_size` aborts plugin initialization. `dmverity_mode` parsing is deferred to the snapshotter. The plugin intentionally does not support overlay's slow recursive chown fallback, so callers relying on remapping need ID-mapped mount support.

## Test Signals
Indirectly covered through EROFS snapshotter tests and transfer default tests that expect optional EROFS differ/snapshotter configuration to skip when unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go

## Purpose
Provides the Linux implementation of EROFS plugin ID-mapped mount capability probing.

## Important APIs, Types, And Functions
`supportsIDMappedMounts` delegates to `overlayutils.SupportsIDMappedMounts`.

## Control Flow
During plugin initialization, `plugin.go` calls this helper; a true result adds `erofs.WithRemapIDs` and advertises the `remap-ids` capability.

## State And Persistence
No persistent state. The helper may trigger overlayutils' temporary mount/probe work.

## Dependencies And Integration Points
Depends on `plugins/snapshots/overlay/overlayutils`, reusing the same kernel feature probe as overlayfs.

## Risks And Edge Cases
EROFS remap support is inferred through overlay utility logic, so false negatives or probe permission failures cause the EROFS plugin to omit remap capability even if parts of the stack might support it.

## Test Signals
Indirectly covered by plugin initialization and EROFS/overlay ID-mapped mount behavior on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go

## Purpose
Provides the non-Linux EROFS plugin capability shim.

## Important APIs, Types, And Functions
`supportsIDMappedMounts` returns `false, nil`.

## Control Flow
When the common plugin initializer runs on non-Linux builds, remap support is never enabled and the snapshotter receives no `WithRemapIDs` option.

## State And Persistence
No state or filesystem effects.

## Dependencies And Integration Points
Compiled under `!linux` and used only by the common EROFS plugin registration code.

## Risks And Edge Cases
The common plugin may still register EROFS and advertise `rebase`/`only-remap-ids` on platforms where the actual snapshotter helpers are stubs; unsupported runtime paths must fail with `ErrNotImplemented`.

## Test Signals
Compile-time coverage for non-Linux builds; no file-local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/plugin/plugin_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go -->
# sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go

## Purpose
Implements and registers the Windows LCOW snapshotter, which exposes Linux container layers on Windows through `lcow-layer` mounts and manages per-container or shared scratch VHDX files.

## Important APIs, Types, And Functions
Registration ID is `windows-lcow`. Labels include rootfs size/location and scratch reuse owner labels. Main APIs implement `snapshots.Snapshotter`: `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, and `Close`. LCOW-specific helpers are `mounts`, `createSnapshot`, `handleSharing`, `openOrCreateScratch`, and `parentIDsToParentPaths`.

## Control Flow
Initialization requires the root to be on NTFS, creates `metadata.db` and `snapshots/`, and registers Linux platform support for the host architecture. Active snapshot creation creates metadata, a snapshot directory, then skips scratch creation for unpack keys. For container scratch snapshots it either symlinks to an owner snapshot's `sandbox.vhdx` when reuse labels are set, or creates/caches a scratch VHDX with runhcs and copies it into the snapshot directory.

## State And Persistence
Persistent state includes `metadata.db`, per-ID snapshot directories, cached `scratch.vhdx` or size-specific `scratch_<N>.vhdx` files, copied `sandbox.vhdx` files, optional symlinks, and `runhcs-scratch.log`. Removal renames snapshot directories to `rm-<id>` inside the metadata transaction and deletes them afterward.

## Dependencies And Integration Points
Uses `go-winio` filesystem detection, `hcsshim/pkg/go-runhcs` scratch creation, containerd snapshot storage, mount `ParentLayerPathsFlag`, plugin registry, `ocispec.Platform`, and continuity disk usage.

## Risks And Edge Cases
Correctness depends on NTFS semantics, scratch cache locking, key-name detection of unpack operations, and owner-key substring lookup for shared scratch. Size parsing ignores parse errors and treats bad values as zero. Rename rollback failures can leave inconsistent on-disk state.

## Test Signals
No file-local tests in this subset. Generic Windows snapshotter tests do not cover LCOW directly; practical coverage is mostly integration/runtime behavior on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native.go

## Purpose
Implements the portable native snapshotter, which materializes each active snapshot as a full copied directory on the backing filesystem rather than using overlay composition.

## Important APIs, Types, And Functions
`snapshotter` stores `root` and `*storage.MetaStore`. Public snapshotter methods are `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, and `Close`. Helpers are `createSnapshot`, `getSnapshotDir`, and `mounts`.

## Control Flow
`NewSnapshotter` creates the root, `metadata.db`, and `snapshots/`. `Prepare` and `View` call `createSnapshot`; active snapshots and parentless views get a temporary directory, active snapshots copy the first parent directory into it, metadata is created in a write transaction, and the temp dir is renamed to the snapshot ID. `Commit` computes disk usage and commits active metadata. `Remove` removes metadata, renames the directory to `rm-<id>`, then deletes it after the transaction.

## State And Persistence
Persistent state is `metadata.db` plus one directory under `snapshots/<id>` per snapshot. Active usage is scanned with `fs.DiskUsage`; committed usage is stored in metadata. Temporary `new-*` directories and `rm-*` directories represent in-flight creation/removal.

## Dependencies And Integration Points
Uses containerd mount and snapshot storage APIs, `continuity/fs` copy/disk usage helpers, platform-specific `mountType`/`defaultMountOptions`, and containerd logging.

## Risks And Edge Cases
Copying parents is expensive and copies only the first parent, matching snapshot chain semantics. Security xattrs are ignored during copy because they often cannot be copied. Failed rollback after directory rename can leave orphaned or inconsistent directories.

## Test Signals
`native_test.go` runs the containerd snapshotter suite as root on non-Windows systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_default.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_default.go

## Purpose
Supplies default native snapshotter mount settings for all non-FreeBSD platforms.

## Important APIs, Types, And Functions
Defines `mountType = "bind"` and `defaultMountOptions = []string{"rbind"}`.

## Control Flow
No functions. `native.go` appends `ro` or `rw` to these defaults when returning mounts.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged `!freebsd`; consumed by `snapshotter.mounts`.

## Risks And Edge Cases
Assumes recursive bind mounts are the correct native representation on non-FreeBSD Unix-like systems. Windows is skipped by tests and does not implement native snapshotter behavior.

## Test Signals
Covered indirectly by `TestNative` and the snapshotter suite on Linux and other non-FreeBSD platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go

## Purpose
Supplies FreeBSD-specific native snapshotter mount settings.

## Important APIs, Types, And Functions
Defines `mountType = "nullfs"` and an empty `defaultMountOptions`.

## Control Flow
No functions. The shared native snapshotter appends `ro` or `rw` to create FreeBSD nullfs mounts.

## State And Persistence
No state.

## Dependencies And Integration Points
Builds on FreeBSD and is consumed by `native.go`.

## Risks And Edge Cases
FreeBSD nullfs option semantics differ from Linux bind mounts, so behavior relies on the generic snapshotter suite catching mount/read/write regressions on FreeBSD.

## Test Signals
Covered indirectly by `TestNative` on FreeBSD.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_test.go

## Purpose
Runs the generic containerd snapshotter compliance suite against the native snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` constructs `native.NewSnapshotter` and returns a close function. `TestNative` gates the suite by OS and root privileges.

## Control Flow
Windows is skipped because the native snapshotter is not implemented there. On other systems the test requires root and invokes `testsuite.SnapshotterSuite(t, "Native", newSnapshotter)`.

## State And Persistence
Uses temporary roots provided by the suite and closes the snapshotter after each test case.

## Dependencies And Integration Points
Depends on `snapshots/testsuite` and `pkg/testutil.RequiresRoot`, making this a conformance bridge rather than bespoke assertions.

## Risks And Edge Cases
The suite may not stress native-specific full-copy performance or xattr-copy behavior. Root and mount availability determine whether tests run.

## Test Signals
Signals broad snapshotter API compatibility: prepare/view/commit/remove/walk/mounts/usage behavior through the shared suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go

## Purpose
Registers the native snapshotter plugin and maps optional root-path configuration to `native.NewSnapshotter`.

## Important APIs, Types, And Functions
`Config` has `RootPath`. `init` registers snapshot plugin ID `native`.

## Control Flow
The initializer appends the default platform, validates `Config`, chooses configured root or `plugins.PropertyRootDir`, exports the root directory metadata, and constructs the native snapshotter.

## State And Persistence
The plugin itself stores no state. The snapshotter creates `metadata.db` and snapshot directories under the selected root.

## Dependencies And Integration Points
Integrates with containerd plugin registry, `plugins.SnapshotPlugin`, `plugins.SnapshotterRootDir`, `platforms.DefaultSpec`, and the native snapshotter package.

## Risks And Edge Cases
Mis-typed config returns an initialization error. Root path override can place snapshotter state outside the daemon plugin root, which is intentional but operationally significant.

## Test Signals
Indirectly covered through daemon plugin initialization and native snapshotter tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go

## Purpose
Implements the Linux overlayfs snapshotter, storing per-snapshot upper/work directories and returning bind or overlay mounts that compose parent snapshots.

## Important APIs, Types, And Functions
Configuration includes `SnapshotterConfig`, `Opt`, `AsynchronousRemove`, `WithUpperdirLabel`, `WithMountOptions`, `WithMetaStore`, `WithRemapIDs`, and `WithSlowChown`. The `snapshotter` implements `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Cleanup`, and `Close`. Helpers include `createSnapshot`, `prepareDirectory`, `mounts`, `upperPath`, `workPath`, `supportsIndex`, and cleanup directory scanners.

## Control Flow
Initialization validates backing filesystem `d_type`, opens or accepts a metastore, creates `snapshots/`, auto-adds `userxattr` if needed in user namespaces, and adds `index=off` when supported. Snapshot creation creates a `new-*` directory with `fs` and optional `work`, writes snapshot metadata, applies user namespace ownership or parent ownership, then renames to the snapshot ID. Mount construction returns bind mounts for no-parent and single-parent views, and overlay mounts with `workdir`, `upperdir`, `lowerdir`, ID-map options, and configured options for active or multi-parent views.

## State And Persistence
Persistent state is `metadata.db` and `snapshots/<id>/fs` plus `work` for active snapshots. Removed metadata is decoupled from disk cleanup when `asyncRemove` is enabled; `Cleanup` removes directories not present in `storage.IDMap`.

## Dependencies And Integration Points
Uses containerd mount/snapshot storage APIs, `overlayutils`, `internal/userns`, continuity `fs`, Linux `syscall.Stat_t`, and plugin-provided metadata store injection for tests or embedding.

## Risks And Edge Cases
Overlayfs requires `d_type`, correct `userxattr` behavior in user namespaces, and support for multiple lowerdirs. ID mapping depends on valid snapshot labels and root mapping extraction. Async removal can leave disk usage until cleanup. Mount option ordering is tested and can break callers that compare options.

## Test Signals
`overlay_test.go` runs the generic suite and checks mount forms, commit parent rebasing, real overlay reads, view behavior, ID-mapped ownership and mount options, and invalid mapping rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go

## Purpose
Validates the Linux overlay snapshotter through the generic snapshotter suite and targeted tests for mount option construction, rebase semantics, real overlay reads, views, and ID-mapped mounts.

## Important APIs, Types, And Functions
`newSnapshotterWithOpts` constructs configured snapshotters. Main tests are `TestOverlay` plus helpers `testOverlayMounts`, `testOverlayCommit`, `testOverlayOverlayMount`, `testOverlayRemappedBind`, `testOverlayRemappedActive`, `testOverlayRemappedInvalidMapping`, `testOverlayOverlayRead`, and `testOverlayView`.

## Control Flow
`TestOverlay` runs three option sets: no option, async remove, and remap IDs. It invokes `testsuite.SnapshotterSuite` and then runs targeted subtests. Tests create snapshots, inspect returned mounts, write files into bind or overlay sources, commit, create children/views, and in one case mount the overlay to verify file reads.

## State And Persistence
Each case uses a temporary root and snapshot metadata. Helper functions open read transactions to map keys to internal snapshot IDs and parent directories.

## Dependencies And Integration Points
Depends on root privileges, containerd client remapper label helpers, snapshot testsuite, mount package, overlayutils, internal user namespace IDMap, and Linux stat ownership data.

## Risks And Edge Cases
Root and kernel mount support gate coverage. Tests depend on exact mount option ordering and feature probes such as `supportsIndex` and `NeedsUserXAttr`. Invalid mapping tests protect the snapshotter from accepting malformed UID/GID labels.

## Test Signals
Strong coverage for API compliance, bind-vs-overlay mount selection, rebase validation via `snapshots.WithParent`, user namespace remap labels, and read-only view lowerdir composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go

## Purpose
Provides Linux overlayfs capability probes for backing filesystem support, multiple lowerdirs, tmpfs detection, userxattr needs, and ID-mapped overlay mounts.

## Important APIs, Types, And Functions
Exports `SupportsMultipleLowerDir`, `Supported`, `IsPathOnTmpfs`, `NeedsUserXAttr`, and `SupportsIDMappedMounts`. Constant `tmpfsMagic` identifies tmpfs via statfs.

## Control Flow
`Supported` creates the root, checks `d_type`, then attempts a real multiple-lowerdir overlay mount. `NeedsUserXAttr` returns false outside user namespaces and on tmpfs, returns true quickly on kernels >= 5.11, otherwise attempts a temporary overlay mount with `userxattr`. `SupportsIDMappedMounts` fast-paths kernels >= 5.19, otherwise creates temp dirs, obtains a user namespace fd, ID-maps a lowerdir, mounts overlay, and verifies merged directory ownership.

## State And Persistence
All probes create temporary directories and mounts, then unmount and remove them. Failed cleanup is logged, not persisted intentionally.

## Dependencies And Integration Points
Uses containerd mount helpers, kernel version utilities, continuity `fs.SupportsDType`, moby userns detection, Linux `unix` syscalls, and logging. Called by overlay and EROFS plugin initialization and by embedders through `Supported`.

## Risks And Edge Cases
Probes require privileges and can fail because of policy rather than kernel capability. Vendor backports make version checks insufficient, which is why slow paths exist. Mount cleanup failures can leave temporary mounts/directories.

## Test Signals
Benchmarks in `check_test.go` exercise `Supported` on loopback filesystems with ext4, XFS ftype variants, and FAT when tooling is available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go

## Purpose
Benchmarks and validates overlay backing-filesystem support detection against temporary loopback filesystems.

## Important APIs, Types, And Functions
`testOverlaySupported` creates a loopback device, formats it, mounts it, and runs `Supported`. Benchmarks cover ext4, XFS with `ftype=0`, XFS with `ftype=1`, and FAT.

## Control Flow
The helper requires root, allocates a 100 MiB loopback device, runs the selected `mkfs`, mounts it, invokes `Supported`, and checks whether success matches the expected result. When called as a benchmark, it repeats only the support check inside the timer.

## State And Persistence
Temporary mount points and loopback devices are cleaned up with deferred unmount and close. Formatting/mount failures skip rather than fail.

## Dependencies And Integration Points
Depends on external mkfs tools, mount command availability, root privileges, continuity loopback helpers, and `pkg/testutil`.

## Risks And Edge Cases
These are benchmarks, not normal `Test*` tests, so routine CI may not run them. Environment tool availability controls coverage.

## Test Signals
Provides focused evidence that `Supported` accepts ext4 and XFS ftype=1 and rejects XFS ftype=0 and FAT.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go

## Purpose
Registers the Linux `overlayfs` snapshotter plugin and maps daemon config into overlay snapshotter options and advertised capabilities.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `upperdir_label`, `sync_remove`, `slow_chown`, and `mount_options`. Capability constants are `remap-ids`, `only-remap-ids`, and `rebase`.

## Control Flow
The initializer sets the default platform, validates config, chooses root, enables upperdir labels if requested, enables async removal unless `sync_remove` is true, passes configured mount options, probes ID-mapped mount support, and handles slow-chown capability signaling. It advertises `rebase` only outside user namespaces because whiteout conversion needs `mknod`.

## State And Persistence
Exports the snapshotter root and delegates persistent metadata/directory creation to `overlay.NewSnapshotter`.

## Dependencies And Integration Points
Integrates with the plugin registry, containerd plugin constants, `platforms.DefaultSpec`, moby userns detection, overlayutils capability probing, and the overlay snapshotter package.

## Risks And Edge Cases
Capability metadata affects higher-level unpack/rebase behavior. If ID-mapped mount probing fails and `slow_chown` is false, the plugin signals `only-remap-ids` without `remap-ids`, restricting user namespace workflows.

## Test Signals
Indirectly covered by overlay tests and daemon plugin initialization; capability combinations are not exhaustively unit tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go

## Purpose
Implements the Windows `blockcim` snapshotter, storing image layers as block CIMs and creating scratch VHDs for writable container layers.

## Important APIs, Types, And Functions
`BlockCIMSnapshotterConfig` controls layer integrity, VHD footer appending, and unformatted scratch behavior. Main methods implement `snapshots.Snapshotter`: `NewBlockCIMSnapshotter`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`. Helpers include `snapshotInfoFromID`, `getSnapshotBlockCIM`, `createSnapshot`, `createScratchLayer`, `mounts`, `prepareMergedCIM`, and `isScratchSnapshot`.

## Control Flow
Initialization skips when block CIMs are unsupported, creates base snapshotter state, and prepares either formatted differencing scratch VHDs or an unformatted template VHD. Active scratch creation rejects parentless scratch snapshots, handles optional UVM scratch first, creates a scratch VHD, then for multi-parent scratch snapshots serializes merged-CIM preparation with a keyed lock. Mount construction emits `BlockCIM` mounts with parent CIM paths, block type, integrity/footer flags, optional merged CIM path, and source selected by scratch-vs-layer status.

## State And Persistence
Stores metadata in `metadata.db`, snapshot directories under `snapshots/<id>`, `layer.vhd/layer.cim` single-file block CIM data, optional `merged.vhd/merged.cim`, `sandbox.vhdx`, and root-level scratch templates. Removal renames metadata/directory through `preRemove` and deletes the renamed snapshot directory.

## Dependencies And Integration Points
Uses hcsshim CIMFS APIs, OCI WC layer CIM merge package, keyed mutex, containerd mount flags for BlockCIM, Windows base snapshotter helpers, plugin registry, and continuity disk usage.

## Risks And Edge Cases
Only unpack snapshots can be committed as read-only CIM layers; scratch commit is unsupported. Unformatted scratch requires at least 40 GiB when custom-sized. Merge correctness depends on snapshot parent order and committed parent metadata. Merge and mount options must stay aligned with downstream Windows mount handlers.

## Test Signals
No file-local tests in this subset. Coverage is mostly compile/integration on Windows and shared tests for mount flag parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/block_cimfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go

## Purpose
Implements the Windows `cimfs` snapshotter, storing committed read-only image layers as CimFS `.cim` files and using VHDX scratch layers for writable containers.

## Important APIs, Types, And Functions
Scratch helpers include `scratchCreationOpt`, `WithNTFSFormat`, `WithSize`, `defaultScratchCreationOptions`, `createDifferencingScratchVHDs`, and `createScratchVHD`. Snapshotter APIs include `NewCimFSSnapshotter`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `createSnapshot`, `createScratchLayer`, and `mounts`.

## Control Flow
Initialization skips unsupported hosts, creates base metadata state, prepares base/differencing scratch VHDs, and creates a shared `cim-layers` directory. Unpack snapshots do not create scratch VHDs and later commit as read-only CIM layers. Non-unpack active snapshots require parents, may create a UVM scratch layer, then copy/expand the scratch template. Mounts include layer CIM path plus parent layer and parent CIM path JSON options.

## State And Persistence
Persistent state includes `metadata.db`, `snapshots/<id>` directories, root-level `blank-base.vhdx` and `blank.vhdx`, shared `snapshots/cim-layers/<id>.cim`, and per-snapshot `sandbox.vhdx`. Usage for committed snapshots adds CimFS usage to base directory usage.

## Dependencies And Integration Points
Uses hcsshim, hcsshim CimFS, compute storage formatting, VHD APIs, VM group ACL helpers, containerd mount flags, and common Windows base snapshotter code.

## Risks And Edge Cases
Committing scratch snapshots to CIM is explicitly unsupported. Parentless scratch snapshots fail. Scratch VHD creation must handle partially existing base/diff files and clean them on failure. Host support and Windows privileges strongly affect behavior.

## Test Signals
`cimfs_test.go` covers mount option parsing through containerd mount helpers; full snapshotter behavior requires Windows integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go

## Purpose
Tests parsing of CimFS-related mount options used by Windows CimFS snapshotters and mount handlers.

## Important APIs, Types, And Functions
`TestGetOptionByPrefix` constructs a `mount.Mount` with `LayerCimPathFlag` and `ParentLayerCimPathsFlag`, then calls `mount.GetCimPath` and `mount.GetParentCimPaths`.

## Control Flow
The test marshals two parent CIM paths to JSON, appends both options to a CimFS mount, parses them back, and asserts exact values and order.

## State And Persistence
No filesystem state; all data is in-memory strings.

## Dependencies And Integration Points
Depends on containerd `core/mount` CimFS flag helpers and Windows build tags.

## Risks And Edge Cases
This only validates option parsing, not actual CimFS mounting, layer creation, or parent path existence.

## Test Signals
Protects the string contract between snapshotters that emit CimFS mount options and consumers that parse them.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/common.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/common.go

## Purpose
Provides shared Windows snapshotter infrastructure for metadata, common snapshot APIs, removal preparation, UVM scratch creation, scratch disk copying, and scratch size label parsing.

## Important APIs, Types, And Functions
`windowsBaseSnapshotter` holds root, metastore, and hcsshim driver info. Common methods are `newBaseSnapshotter`, `getSnapshotDir`, `parentIDsToParentPaths`, `Stat`, `Update`, `Usage`, `Walk`, `preRemove`, and `Close`. Helpers are `createUVMScratchLayer`, `copyScratchDisk`, and `getRequestedScratchSize`.

## Control Flow
Base initialization creates root, `metadata.db`, and `snapshots/`. `preRemove` removes metadata in a transaction, renames the snapshot directory to `rm-<id>`, and if permission is denied attempts HCS layer deactivation before retrying. UVM scratch creation locates the base layer `UtilityVM/SystemTemplate.vhdx`, creates a `vm` subdir, and copies it to `vm/sandbox.vhdx`.

## State And Persistence
Shared state is `metadata.db`, `snapshots/<id>` directories, renamed `rm-<id>` directories, and copied scratch VHDX files. Active usage scans snapshot directories; committed usage comes from metadata unless specialized snapshotters add layer-specific usage.

## Dependencies And Integration Points
Uses hcsshim driver info and layer deactivation, containerd snapshot storage, continuity disk usage, and labels defined in Windows snapshotter files.

## Risks And Edge Cases
Rename rollback failure can leave inconsistent state. Permission-denied removal recovery is best-effort. Scratch size labels support both deprecated GB and newer byte labels, preferring bytes; invalid values fail snapshot creation.

## Test Signals
Exercised indirectly by WCOW, CimFS, and block-CIM snapshotters plus Windows snapshotter suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/windows.go

## Purpose
Implements and registers the legacy WCOW Windows snapshotter for `windows-layer` mounts, base layer conversion, sandbox VHDX creation, and writable-to-read-only layer commit conversion.

## Important APIs, Types, And Functions
Registration ID is `windows`. Labels include `uvmScratchLabel`, deprecated GB rootfs size, and byte rootfs size. Main APIs are `NewWindowsSnapshotter`, `Prepare`, `View`, `Commit`, `Remove`, `Mounts`, `createSnapshot`, `createScratchLayer`, `convertScratchToReadOnlyLayer`, and `mounts`.

## Control Flow
Initialization requires NTFS and creates a base snapshotter. Parentless active snapshots create a `Files` directory for a future base layer. Child scratch snapshots gather parent layer paths, parse scratch size labels, optionally create UVM scratch, and copy/expand `blank.vhdx` into `sandbox.vhdx`. Commit converts parentless layers to base layers or reimports scratch layers as read-only layers unless the key is an unpack key.

## State And Persistence
Stores metadata in `metadata.db`, snapshot directories under `snapshots/<id>`, `Files` for base layers, `sandbox.vhdx`, optional `vm/sandbox.vhdx`, and converted on-disk Windows layer data. Removal delegates directory rename to `preRemove` and destroys the renamed layer with hcsshim.

## Dependencies And Integration Points
Uses go-winio privileges, hcsshim, OCI Windows layer import/export, containerd mount flags, platform registration, and common Windows base snapshotter helpers.

## Risks And Edge Cases
Commit conversion duplicates data because `sandbox.vhdx` is retained for later export. Privilege enabling is required for import/export. Key-name detection of unpack snapshots controls whether scratch creation or conversion is skipped.

## Test Signals
`windows_test.go` runs the generic snapshotter suite on Windows as root/admin. Specific conversion and scratch-size paths need broader Windows integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go

## Purpose
Runs the generic snapshotter compliance suite against the Windows WCOW snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` constructs `NewWindowsSnapshotter` and returns a close function. `TestWindows` invokes `testsuite.SnapshotterSuite`.

## Control Flow
The test requires root/admin privileges, creates snapshotters under suite-provided roots, and lets the shared suite exercise snapshot lifecycle operations.

## State And Persistence
Uses temporary suite roots and closes each snapshotter after use.

## Dependencies And Integration Points
Depends on Windows build tags, `pkg/testutil.RequiresRoot`, and the shared snapshotter testsuite.

## Risks And Edge Cases
The generic suite does not necessarily cover all WCOW-specific hcsshim conversion, UVM scratch, or custom scratch size behavior.

## Test Signals
Provides baseline snapshotter API compatibility for the Windows implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/streaming/manager.go -->
# sources/cloud-native/containerd/plugins/streaming/manager.go

## Purpose
Registers and implements containerd's in-memory streaming manager, including metadata GC integration for active and leased stream resources.

## Important APIs, Types, And Functions
Plugin ID is `manager` under `plugins.StreamingPlugin`. Main types are `streamManager`, `managedStream`, and `collectionContext`. APIs include `Register`, `Get`, `StartCollection`, `ReferenceLabel`, `managedStream.Close`, and collection methods `All`, `Active`, `Leased`, `Remove`, `Cancel`, and `Finish`.

## Control Flow
Initialization requires the metadata plugin, creates namespace/name and namespace/lease indexes, and registers the manager as a collectible metadata resource. `Register` records a stream under the current namespace and optional lease. `Get` looks up by namespace/name. GC collection locks the manager until canceled or finished; `Finish` removes marked streams from both indexes, unlocks, and then closes removed streams.

## State And Persistence
State is in-memory maps protected by an RW mutex. Stream liveness is not persisted across daemon restarts. Lease associations are tracked in `byLease` so metadata GC can keep leased streams.

## Dependencies And Integration Points
Integrates with metadata DB resource collection, leases context, namespaces, streaming core interface, GC nodes, errdefs, and plugin registry.

## Risks And Edge Cases
Collection holds the write lock for its full duration, blocking register/get/close. `managedStream.Close` removes indexes before closing the underlying stream; underlying close errors do not roll back map removal. Non-leased stream expiry is left as a TODO.

## Test Signals
No file-local tests in this subset. Expected coverage is via metadata GC and streaming service integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/streaming/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin.go

## Purpose
Registers the local transfer service plugin and builds its configuration from leases, metadata, image verifiers, snapshotters, differs, registry config, and unpack platform rules.

## Important APIs, Types, And Functions
Plugin ID is `local` under `plugins.TransferPlugin`. Key functions are `configureUnpackPlatforms`, `getApplier`, and `defaultConfig`. Config types are `transferConfig` and `unpackConfiguration`.

## Control Flow
Initialization obtains metadata and lease plugins, collects optional image verifier plugins, applies concurrency settings, configures unpack platforms, sets registry config path and duplication suppressor, then constructs `local.NewTransferService`. `configureUnpackPlatforms` defaults unpack config when nil, parses platforms, resolves snapshotters, obtains snapshotter exports/capabilities, chooses an applier, and appends `unpack.Platform` entries. `getApplier` uses explicit differ selection when configured or scans diff plugins by supported platform, preferring the default differ when multiple match.

## State And Persistence
The plugin itself persists no state. It passes the metadata DB content/image stores and snapshotter references into the local transfer service. The duplication suppressor is an in-memory keyed mutex.

## Dependencies And Integration Points
Requires lease, metadata, diff, image verifier, and snapshot plugins. Imports transfer archive/image/registry packages for type registration. Integrates with platform matching, errdefs, defaults, unpack, and local transfer APIs.

## Risks And Edge Cases
Optional unpack entries are skipped when snapshotters or differs are missing; required entries fail initialization. Auto differ selection can be ambiguous, with warnings and default preference. `CheckPlatformSupported=false` broadens matching to OS-only, which can unpack for architectures not explicitly supported by a snapshotter.

## Test Signals
`plugin_test.go` covers optional/required differ skip and missing behavior plus auto differ skip. `plugin_linux_test.go` confirms default Linux config skips unavailable EROFS differ rather than failing all transfer initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go

## Purpose
Defines Darwin's default unpack configuration for the transfer plugin.

## Important APIs, Types, And Functions
`defaultUnpackConfig` returns one `unpackConfiguration`.

## Control Flow
It starts from `platforms.DefaultSpec`, rewrites the OS to `linux`, and selects the default snapshotter and default differ.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `containerd/defaults` and `platforms`. Consumed by `plugin.go` when no explicit unpack configuration is provided.

## Risks And Edge Cases
Darwin images are not defined for default unpack, so Linux is assumed. This is convenient for Linux image workflows on Darwin clients but not a general Darwin runtime statement.

## Test Signals
Indirectly covered by transfer configuration tests where platform-specific defaults are compiled.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go

## Purpose
Defines Linux default transfer unpack platforms, including an optional EROFS-native image path.

## Important APIs, Types, And Functions
`erofsPlatformSpec` adds OS feature `erofs` to the default platform. `defaultUnpackConfig` returns default and EROFS configurations.

## Control Flow
The first entry uses the default platform, default snapshotter, and default differ. The second entry uses the full platform including `os.features=erofs`, snapshotter `erofs`, differ `erofs`, and `Optional: true`.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by transfer plugin initialization on Linux. It ties EROFS snapshotter/differ discovery to unpack platform configuration without making EROFS mandatory.

## Risks And Edge Cases
If EROFS differ or snapshotter is registered but skipped or unavailable, optional handling must skip cleanly; this is tested. Platform formatting uses `FormatAll` so OS features remain part of matching.

## Test Signals
`plugin_linux_test.go` verifies unavailable EROFS differ does not prevent default unpack platform configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_other.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_other.go

## Purpose
Defines default transfer unpack configuration for platforms other than Windows, Darwin, and Linux.

## Important APIs, Types, And Functions
`defaultUnpackConfig` returns one entry using the default platform, snapshotter, and differ.

## Control Flow
No probing or optional entries are added; `plugin.go` consumes this when config is nil.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged `!windows && !darwin && !linux`, depending on containerd defaults and platforms.

## Risks And Edge Cases
Assumes the default platform/snapshotter/differ combination is valid for less common OS targets; initialization will fail later if required plugins are absent.

## Test Signals
Compile-time coverage on matching platforms; no file-local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go

## Purpose
Defines Windows default transfer unpack configuration.

## Important APIs, Types, And Functions
`defaultUnpackConfig` returns one entry using the default platform, snapshotter, and differ.

## Control Flow
The transfer plugin uses this entry when no TOML unpack config is provided on Windows.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrates with defaults/platforms and the Windows build of the transfer plugin.

## Risks And Edge Cases
No optional CimFS/block-CIM defaults are added here, so advanced Windows snapshotters require explicit config or separate registration behavior.

## Test Signals
No file-local tests; covered by platform builds and transfer plugin initialization tests where run on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_defaults_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go

## Purpose
Tests Linux-specific transfer defaults, especially the optional EROFS unpack entry.

## Important APIs, Types, And Functions
`TestConfigureUnpackPlatformsDefaultConfigSkipsUnavailableErofsDiffer` uses `defaultConfig`, `newTestInitContext`, and `newTestDiffPlugin`.

## Control Flow
The test registers default and EROFS snapshotters, a usable default differ, and an EROFS differ that returns `plugin.ErrSkipPlugin`. It calls `configureUnpackPlatforms` with default config and asserts only the default unpack platform remains.

## State And Persistence
Uses temporary content and metadata stores created by shared test helpers.

## Dependencies And Integration Points
Depends on Linux build tags, transfer local config, snapshotter stubs, platform specs with `OSFeatures`, and plugin skip semantics.

## Risks And Edge Cases
Only covers unavailable EROFS differ, not unavailable EROFS snapshotter or successful EROFS configuration.

## Test Signals
Protects startup resilience when optional EROFS support is compiled into defaults but runtime dependencies are not available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_test.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_test.go

## Purpose
Unit tests for transfer unpack platform configuration and diff applier selection.

## Important APIs, Types, And Functions
`TestConfigureUnpackPlatforms`, `newTestInitContext`, `newTestDiffPlugin`, `testApplier`, and `testSnapshotter`.

## Control Flow
Table cases cover optional explicit differ skip, required explicit differ skip, optional explicit differ missing, and auto differ selection that skips unavailable candidates and uses a later usable candidate. Helpers create a local content store, bbolt metadata DB, plugin set with snapshotter registrations, and diff plugin registrations.

## State And Persistence
Creates temporary content stores and bbolt metadata DBs, closing the DB through `t.Cleanup`.

## Dependencies And Integration Points
Uses containerd metadata DB, local transfer config, plugin set/context APIs, diff and snapshotter interfaces, errdefs, and platform matching.

## Risks And Edge Cases
Tests use minimal stubs and do not instantiate the full transfer service. Ambiguous multi-differ default preference is not explicitly asserted here.

## Test Signals
Provides focused coverage for optional vs required unpack configuration failures and auto applier selection with skipped plugins.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/types.go -->
# sources/cloud-native/containerd/plugins/types.go

## Purpose
Defines containerd's internal plugin type strings, common plugin IDs, property keys, and export keys.

## Important APIs, Types, And Functions
Constants include plugin types for internal, runtime v1/v2, service, GRPC, TTRPC, snapshotter, diff, metadata, content, GC, events, leases, streaming, tracing, metrics, NRI, transfer, sandbox, image verifier, warning, CRI, shim, HTTP, server, mount manager, and mount handler. Also defines `RuntimeRuncV2`, `RuntimeRunhcsV1`, `DeprecationsPlugin`, root/state/GRPC/TTRPC property keys, and `SnapshotterRootDir`.

## Control Flow
No runtime logic; constants are imported by plugin registrations throughout containerd.

## State And Persistence
No state. String values become part of plugin identity, configuration, metadata, and compatibility contracts.

## Dependencies And Integration Points
Depends only on `github.com/containerd/plugin`. Used by snapshotter, streaming, transfer, and many other plugin packages.

## Risks And Edge Cases
Changing any string breaks plugin registration, config lookup, exported metadata, or external assumptions. The package comment warns external plugins to copy these types rather than import this internal package.

## Test Signals
No file-local tests. Stability is enforced by widespread compile-time use and runtime plugin registration behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.0.0.toml -->
# sources/cloud-native/containerd/releases/v1.0.0.toml

## Purpose
Release metadata and long-form notes for containerd v1.0.0.

## Important APIs, Types, And Functions
Top-level TOML keys set `commit = "HEAD"`, `project_name`, `github_repo`, `previous = "v1.0.0-rc.0"`, `pre_release = false`, and a `preface`. Empty `[notes]` and `[breaking]` tables are placeholders for release tooling.

## Control Flow
Consumed by release-note tooling to compare from the previous release, tag the configured commit, and render the preface with generated notes.

## State And Persistence
No runtime state. It preserves release intent: 1.0 graduation after alphas/betas/RC, 0.2 EOL, support horizon, and governance model changes.

## Dependencies And Integration Points
References README, API docs, cri-containerd, release support policy, GitHub issues, and Moby TSC governance.

## Risks And Edge Cases
Historical text includes links and support dates that must remain stable for reproducibility. The repeated phrase "designed for use designed for use" appears in source and should not be silently changed by tooling.

## Test Signals
Validation is by TOML parse/release generation rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.0.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.1.0.toml -->
# sources/cloud-native/containerd/releases/v1.1.0.toml

## Purpose
Release metadata and notes for containerd v1.1.0, centered on the integrated CRI plugin and Kubernetes v1.10 support.

## Important APIs, Types, And Functions
Defines `previous = "v1.0.0"`, `pre_release = true`, project/repo metadata, and a large `preface`. Empty `[notes]` and `[breaking]` tables remain for generated content.

## Control Flow
Release tooling reads the previous release boundary, pre-release flag, and preface to generate the GitHub release.

## State And Persistence
Captures historical release state: CRI built into containerd, cri-containerd end-of-life, CRI v1alpha2 support, registry mirrors, e2e/performance claims, and support horizon tied to Kubernetes 1.10.

## Dependencies And Integration Points
References Kubernetes CRI, containerd/cri docs, Kata/Clear Containers, runc, Prow results, node performance dashboards, LinuxKit, ansible, kubeadm, and Kubernetes the Hard Way.

## Risks And Edge Cases
`pre_release = true` for a major release manifest is unusual and affects release automation. Links point to historical branches and should not be modernized casually.

## Test Signals
TOML parse and release-tool rendering are the relevant checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.1.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.2.0.toml -->
# sources/cloud-native/containerd/releases/v1.2.0.toml

## Purpose
Release metadata and notes for containerd v1.2.0, covering runtime v2, CRI updates, proxy plugins, managed `/opt`, GC, importer, and API additions.

## Important APIs, Types, And Functions
Adds `match_deps = "^github.com/(containerd/[a-zA-Z0-9-]+)$"`, `previous = "v1.1.0"`, `pre_release = false`, `preface`, empty `[notes]`/`[breaking]`, and `[rename_deps.ttrpc]` mapping old `github.com/stevvooe/ttrpc` to `github.com/containerd/ttrpc`.

## Control Flow
Release tooling uses dependency matching and rename metadata when building changelogs and dependency deltas.

## State And Persistence
Preserves the v1.2 narrative: stable runtime v2 shim API, Kubernetes v1.10-v1.12 CRI behavior, RuntimeClass migration, proxy plugins, managed host binaries, GC cleanup for leases/content ingests, docker-save import support, and API additions.

## Dependencies And Integration Points
References runtime v2 docs, CRI config/registry docs, Kubernetes RuntimeClass/ProcMount, PLUGINS.md, managed-opt docs, and ttrpc module rename handling.

## Risks And Edge Cases
The rename-deps table is important for release-note accuracy across module renames. Some CRI options are marked deprecated but retained.

## Test Signals
Validation is release tooling parsing the manifest and rendering renamed dependency sections correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.2.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.3.0.toml -->
# sources/cloud-native/containerd/releases/v1.3.0.toml

## Purpose
Release metadata and notes for containerd v1.3.0, emphasizing Windows v2 runtime, devmapper snapshotter, plugin/client/API improvements, and CRI feature expansion.

## Important APIs, Types, And Functions
Defines standard project metadata, dependency matching, `previous = "v1.2.0"`, `pre_release = false`, `preface`, and empty notes/breaking sections.

## Control Flow
Release automation uses the manifest to generate release notes from v1.2.0 to v1.3.0 with the supplied preface.

## State And Persistence
Captures historical compatibility and feature state: new Windows shim runtime, devmapper snapshotter, stream processor plugin, namespace defaults, resolver mirror support, lease resource management, and Kubernetes v1.16-validated CRI support.

## Dependencies And Integration Points
References hcsshim runhcs shim, CRI issue/PR links, registry config snippets, Kubernetes dual-stack docs, and containerd PRs.

## Risks And Edge Cases
Long CRI deprecation and config examples are part of release history and can become misleading if edited outside release tooling context.

## Test Signals
TOML parse and generated release-note output are the relevant checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.3.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.4.0.toml -->
# sources/cloud-native/containerd/releases/v1.4.0.toml

## Purpose
Release metadata and notes for containerd v1.4.0, highlighting cgroups v2, SELinux, Windows on Kubernetes through CRI, and remote/shared snapshotter support.

## Important APIs, Types, And Functions
Defines project/repo metadata, dependency matching, `previous = "v1.3.0"`, `pre_release = false`, `preface`, and empty notes/breaking tables.

## Control Flow
Release tooling renders this manifest as the v1.4.0 release note base and computes changes from v1.3.0.

## State And Persistence
Records snapshotter API additions like target snapshot option, walk filters, FUSE mounts, backend options, lazy-pull support, and proxy snapshotter cleanup, plus runtime/client/API/daemon/Windows/CRI changes.

## Dependencies And Integration Points
References stargz snapshotter, CRI PRs, Kubernetes network policy/dual-stack docs, and many containerd PRs.

## Risks And Edge Cases
This release notes that significant fixes are also available on prior supported releases; generated notes should not imply all fixes are exclusive to v1.4.0.

## Test Signals
Release manifest parsing and generated changelog rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.4.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.5.0.toml -->
# sources/cloud-native/containerd/releases/v1.5.0.toml

## Purpose
Release metadata and notes for containerd v1.5.0, documenting project reorganization, Go modules, CRI merge, snapshotter plugin separation, registry host config, and FreeBSD runtime support.

## Important APIs, Types, And Functions
Defines standard release keys with `previous = "v1.4.0"` and a large `preface`. No notes/breaking tables are present after the preface in this file.

## Control Flow
Release tooling reads the manifest to generate v1.5.0 notes and dependency deltas from v1.4.0.

## State And Persistence
Captures important migration state: containerd/cri moved into main repo, Go modules adoption, snapshotter implementation/plugin split, new registry `config_path`, deprecation of registry mirrors/configs and config version 1, and experimental FreeBSD runtime support.

## Dependencies And Integration Points
References Go modules, CRI import path migration, OCI spec option changes, registry hosts.toml layout, NRI, CNI, ocicrypt, and runj.

## Risks And Edge Cases
This is a client-impacting release; import paths and config deprecations need accurate historical preservation. Registry examples include security-sensitive mirror capability semantics.

## Test Signals
Release tooling TOML parsing plus generated docs; no code tests apply.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.5.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.6.0.toml -->
# sources/cloud-native/containerd/releases/v1.6.0.toml

## Purpose
Release metadata and notes for containerd v1.6.0, documenting runtime, Windows, CRI, client, and packaging updates.

## Important APIs, Types, And Functions
Defines `previous = "v1.5.0"`, dependency matching, `pre_release = false`, and a `preface` with highlights and release update notes.

## Control Flow
Release tooling generates v1.6.0 release notes from this preface and the v1.5.0 comparison boundary.

## State And Persistence
Records shim/runtime changes, Windows HostProcess/resource support, CRI v1 and v1alpha parallel support, cgroups v2 resource support, sandbox/container metrics, TLS auth, devmapper improvements, and deprecation of `cri-containerd-*.tar.gz` bundles.

## Dependencies And Integration Points
References runc v1.1.0, CNI/runc/critools tar bundles, libseccomp compatibility, and containerd PRs.

## Risks And Edge Cases
Packaging notes are operationally important: dynamically linked runc from cri-containerd bundles may not work on older distributions, and bundle deprecation affects downstream installers.

## Test Signals
TOML parse and release artifact generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.6.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.7.0.toml -->
# sources/cloud-native/containerd/releases/v1.7.0.toml

## Purpose
Release metadata and notes for containerd v1.7.0, the last 1.x major release before 2.0, introducing experimental sandbox API, transfer service, expanded NRI, gRPC shim support, and 2.0 migration guidance.

## Important APIs, Types, And Functions
Defines `previous = "v1.6.0"`, dependency matching, `pre_release = false`, `preface`, and `postface` with artifact download guidance.

## Control Flow
Release tooling renders both preface and postface around generated changelog content and uses v1.6.0 as the previous boundary.

## State And Persistence
Preserves historical status for experimental sandbox API, transfer service, NRI v0.3.0, Linux containers on FreeBSD, CDI, blockio, restart policy, gRPC shim protocol, protobuf/ttrpc refactors, CRI v1alpha2 deprecation, and build baseline changes.

## Dependencies And Integration Points
References transfer docs, NRI docs, containerd 2.0 roadmap, Kubernetes user namespaces KEP, runc/CNI external downloads, and release tarball naming.

## Risks And Edge Cases
The postface includes artifact recommendations and deprecations that should match actual release assets. Several features are explicitly experimental and should not be documented as stable for this release.

## Test Signals
Release manifest parsing and rendered release text.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v1.7.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.0.0.toml -->
# sources/cloud-native/containerd/releases/v2.0.0.toml

## Purpose
Release metadata and notes for containerd v2.0.0, the first 2.x major release focused on stability, 1.x upgrade path, and removal/stabilization of deprecated 1.x features.

## Important APIs, Types, And Functions
Defines `previous = "v1.7.0"`, `ignore_deps = ["github.com/containerd/containerd"]`, dependency matching, `pre_release = false`, concise `preface`, artifact `postface`, and `override_deps` previous commits for `containerd/log`, `plugin`, `platforms`, and `errdefs`.

## Control Flow
Release tooling uses override dependency baselines because several containerd submodules have previous points not captured by a normal tag comparison. The postface drops deprecated CRI bundle recommendations.

## State And Persistence
Captures the 2.0 release framing and documentation pointer to `containerd-2.0.md`. It also records the Ubuntu 20.04/glibc 2.31 binary baseline for dynamic artifacts.

## Dependencies And Integration Points
References runc, CNI plugins, getting-started docs, and specific containerd submodule repositories through override dependencies.

## Risks And Edge Cases
Incorrect override dependency commits would skew generated dependency changelogs. This manifest intentionally ignores the main containerd module dependency to avoid self-referential noise.

## Test Signals
Release tooling must parse override tables and render artifacts/download guidance correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.0.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.1.0.toml -->
# sources/cloud-native/containerd/releases/v2.1.0.toml

## Purpose
Release metadata and notes for containerd v2.1.0, the first time-based 2.x minor release.

## Important APIs, Types, And Functions
Defines `previous = "v2.0.0"`, `ignore_deps = ["github.com/containerd/containerd"]`, dependency matching, `pre_release = false`, a concise `preface`, and a `postface` with artifact guidance.

## Control Flow
Release tooling compares against v2.0.0, ignores the main module dependency, and appends the postface to generated release notes.

## State And Persistence
Captures the project's shift to time-based releases and updates binary guidance to Ubuntu 22.04/glibc 2.35 for dynamic builds.

## Dependencies And Integration Points
References external runc and CNI plugin downloads plus getting-started docs.

## Risks And Edge Cases
The postface changes minimum glibc expectations for dynamic artifacts; downstream installation docs need to align with this release-specific guidance.

## Test Signals
TOML parsing and release-note generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.1.0.toml -->
