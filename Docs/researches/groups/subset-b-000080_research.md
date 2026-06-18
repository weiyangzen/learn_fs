# subset-b-000080 research

This grouped report covers the requested containers/storage driver, store, helper, and test files. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay.go

## Purpose
`overlay.go` is the Linux implementation of the overlay and overlay2 graph driver. It owns driver initialization, feature probing, overlay directory layout, layer creation/removal, mounting/unmounting, native and naive diff selection, ID-mapped mounts, composefs integration, additional read-only layer stores, project quota wiring, and deduplication over overlay layer `diff` directories.

## Important APIs, Types, And Functions
`overlayOptions` carries parsed driver settings: image stores, additional layer stores, project quota limits, mount program, mount options, force mask, chown behavior, and composefs. `Driver` stores `home`, `runhome`, optional `imageStore`, ref counter, quota controller, cached feature booleans, staging locks, and naive diff wrapper. `Init`, `parseOptions`, `SupportsNativeOverlay`, `supportsOverlay`, `Create`, `CreateReadWrite`, `Get`, `Put`, `Remove`, `Diff`, `ApplyDiff`, `Changes`, `UpdateLayerIDMap`, `LookupAdditionalLayer`, and `Dedup` form the main API surface. Helpers such as `cachedFeatureCheck`, `recreateSymlinks`, `redirectDiffIfAdditionalLayer`, and `getMergedDir` protect operational edge cases.

## Control Flow
`Init` parses options, identifies backing filesystem, creates `home/l`, optional image-store link directories, and `runhome`, then chooses native overlay or a `mount_program` such as `fuse-overlayfs`. Native mode probes d_type, multiple lower support, metacopy, volatile, data-only layers, and ID-mapped lower support; many probe results are cached under `runhome` as feature marker files. Layer creation builds the overlay layout: per-layer `diff`, `work`, `merged`, `empty`, `link`, and optional `lower` files, plus `home/l/<random>` symlinks pointing to `../<id>/diff`. `Get` resolves lower symlinks across primary/image/additional stores, optionally mounts composefs blobs, applies ID-mapped bind mounts, assembles mount data, falls back to relative `mountOverlayFrom` when mount data exceeds a page, and increments a ref counter. `Put` decrements the counter, unmounts via FUSE helpers or `unix.Unmount`, cleans leaked mapped mounts, and atomically refreshes `merged`.

## State And Persistence
Persistent state lives in the driver home: layer directories, the `l` symlink farm, per-layer `lower` and `link` files, `additionallayer` pointer files, optional `composefs-data`, staging directories, temp deletion roots, and XFS project-quota metadata. Runtime state lives in `runhome`, including feature cache files and private mountpoints for additional stores. The driver can repair missing `l` symlinks or `link` files via `recreateSymlinks`; staging locks are tracked in memory and on disk with `staging.lock`.

## Dependencies And Integration Points
The file integrates with the graphdriver registry, `graphdriver.RefCounter`, quota package, internal dedup, staging lockfiles, tempdir deletion, idtools/idmap, mount helpers, SELinux labels, archive/chrootarchive, overlay feature checks from sibling files, composefs helpers, and additional image/layer store contracts. It exposes additional image stores to higher storage layers and wraps itself with naive diff and naive ID-map update helpers when native overlay semantics are unsuitable.

## Risks And Edge Cases
Mount data length, lower depth (`maxDepth`), stale symlink farms, missing feature-cache consistency, rootless/network filesystem constraints, metacopy compatibility, FUSE force-mask behavior, additional-store lock expectations, and ID-mapped mount cleanup are high-risk areas. `useNaiveDiff` is guarded by package-level `sync.Once`, so global native-diff choice is process-wide. `getMergedDir` explicitly documents a locking risk around `DiffSize`. Composefs data-only lower separator support and extra composefs mounts add failure paths that must be unwound carefully.

## Test Signals
`overlay_test.go` exercises general graphdriver create/snapshot/diff/list behavior, deep lower reads, force-mask xattr preservation, shifting support differences for native versus mount-program overlay, and benchmarks. The broader codebase likely covers feature probes and additional store behavior indirectly, but the most complex mount assembly and composefs paths need environment-specific integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go

## Purpose
This Linux+cgo quota-enabled overlay companion implements writable-layer disk usage reporting when project quota support is available.

## Important APIs, Types, And Functions
`(*Driver).ReadWriteDiskUsage(id string)` returns `*directory.DiskUsage`. It uses `d.quotaCtl.GetDiskUsage(d.dir(id), usage)` when `quotaCtl` exists and otherwise falls back to `directory.Usage(<layer>/diff)`.

## Control Flow
The function creates an empty usage object, checks whether the driver initialized a quota controller, and either queries XFS project quota accounting or scans the `diff` directory.

## State And Persistence
No new state is written here. It reads quota state already assigned by `overlay.go`/`quota.Control`, or reads filesystem metadata under the layer `diff` directory.

## Dependencies And Integration Points
This file depends on `pkg/directory` and the quota controller field on `Driver`. It is selected only for `linux && cgo && !exclude_disk_quota`, complementing the unsupported build.

## Risks And Test Signals
Quota accounting can fail if backing block device nodes or project IDs are missing; in that case the error from `GetDiskUsage` is returned. Fallback scanning is slower and may differ from quota usage for sparse/reflinked files. Coverage is primarily through graphdriver disk-usage tests on quota-capable XFS systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go

## Purpose
This alternate build implements overlay writable-layer usage reporting when cgo or disk quota support is unavailable.

## Important APIs, Types, And Functions
`(*Driver).ReadWriteDiskUsage(id string)` always returns `directory.Usage(path.Join(d.dir(id), "diff"))`.

## Control Flow
There is no branching except normal directory scanning error propagation.

## State And Persistence
It reads filesystem state only; it does not interact with project quota metadata.

## Dependencies And Integration Points
The build tag `linux && (!cgo || exclude_disk_quota)` prevents duplicate definitions with the quota-enabled file.

## Risks And Test Signals
Usage reflects recursive directory accounting rather than quota counters. It can be expensive on large writable layers and may not represent deduplicated/reflinked storage the same way as quota accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go

## Purpose
`overlay_test.go` defines Linux graphdriver conformance tests and performance benchmarks for the overlay driver.

## Important APIs, Types, And Functions
`init` swaps archive helpers to non-chroot implementations for easier debugging and initializes reexec. `skipIfNaive` skips native-diff-only tests when the host cannot support native diff. Tests include `TestContainersOverlayXattr`, `TestSupportsShifting`, the standard `graphtest` lifecycle tests, and benchmarks for exists/get/diff/apply/deep-layer scenarios.

## Control Flow
The suite initializes a shared driver between `TestOverlaySetup` and `TestOverlayTeardown`, then runs create, base/snapshot, template, deep read, diff/apply, changes, echo, and layer list checks. `TestContainersOverlayXattr` intentionally runs before setup because it uses a distinct `force_mask=700` configuration. `TestSupportsShifting` compares contiguous and non-contiguous mappings with and without `mount_program`.

## State And Persistence
Tests create temporary graphdriver storage through `graphtest` and rely on real overlay support where available. They may mount filesystems and write layer directories, xattrs, and diff contents under test roots.

## Dependencies And Integration Points
The tests depend on `drivers/graphtest`, archive package hooks, reexec, idtools, and testify. They are integration-like and require Linux overlay capabilities; native diff tests skip when unsupported.

## Risks And Test Signals
The file provides good broad behavioral coverage but limited direct coverage for composefs, additional layer stores, feature cache files, stale symlink repair, quota enforcement, and mount-data page-size fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go

## Purpose
This non-Linux fallback exposes the `SupportsNativeOverlay` symbol for platforms where the overlay driver implementation is not built.

## Important APIs, Types, And Functions
`SupportsNativeOverlay(graphroot, rundir string) (bool, error)` always returns `false, nil`.

## Control Flow
There is no probing on unsupported platforms.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The `!linux` build tag keeps callers portable when they compile shared code that asks whether native overlay is available.

## Risks And Test Signals
The behavior is intentionally conservative. Any caller requiring an explanatory error must not rely on this function for unsupported-platform diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/randomid.go -->
# sources/cloud-native/containers-storage/drivers/overlay/randomid.go

## Purpose
`randomid.go` generates compact random link identifiers for overlay layer symlinks under `home/l`.

## Important APIs, Types, And Functions
`generateID(l int)` reads enough random bytes from `crypto/rand`, base32-encodes them, and returns the requested prefix length. `retryOnError` unwraps `*os.PathError` and treats `unix.EPERM` as retryable entropy exhaustion.

## Control Flow
The generator computes byte count as `(l*5+7)/8`, repeatedly reads from `rand.Reader`, sleeps with a 10 ms incremental backoff on retryable errors, and panics on non-retryable or exhausted retry failures. Successful bytes are base32 encoded.

## State And Persistence
The function has no durable state. Its output becomes persistent when `overlay.go` writes it to each layer `link` file and creates a symlink in `home/l`.

## Dependencies And Integration Points
Overlay layer creation uses `generateID(idLength)` to keep lowerdir mount arguments short while avoiding collisions. Dependencies are standard crypto/base32/time/os/syscall plus logrus and unix constants.

## Risks And Test Signals
The function panics instead of returning an error if randomness fails, making it a process-level failure path. It does not check collision itself; callers depend on symlink creation failure to catch collisions. There is no file-local test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/randomid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go -->
# sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go

## Purpose
This utility file centralizes the error message for backing filesystems without d_type support.

## Important APIs, Types, And Functions
`ErrDTypeNotSupported(driver, backingFs string) error` builds a detailed message, adds XFS `ftype=1` guidance when relevant, and wraps `graphdriver.ErrNotSupported`.

## Control Flow
The function formats the message and returns a wrapped error in one path.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
`overlay.go` calls this from `supportsOverlay` after `fsutils.SupportsDType` fails. Wrapping `graphdriver.ErrNotSupported` lets higher layers classify the failure.

## Risks And Test Signals
The function is simple but user-facing; message changes can affect tests or documentation that match errors. No direct tests are present here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota.go

## Purpose
This shared quota file defines the backing block device link name used by project quota support.

## Important APIs, Types, And Functions
`BackingFsBlockDeviceLink` is the filename `backingFsBlockDev`.

## Control Flow
There is no runtime control flow.

## State And Persistence
Quota-enabled builds create a block device node with this name under the driver home so `quotactl` can address the backing filesystem. Overlay `ListLayers` skips it as non-layer state.

## Dependencies And Integration Points
The constant is consumed by the quota implementation and overlay driver layer listing.

## Risks And Test Signals
Renaming the constant would break compatibility with existing driver home layouts and cleanup/listing logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go

## Purpose
This Linux+cgo implementation provides XFS project quota control for graph drivers, mainly overlay on XFS with project quotas enabled.

## Important APIs, Types, And Functions
`Quota` stores byte and inode limits. `Control` tracks the backing block device, next project ID, `targetPath -> projectID` map, and base path. `NewControl`, `SetQuota`, `ClearQuota`, `GetQuota`, and `GetDiskUsage` are the public operations. Internal functions manage project IDs via `FS_IOC_FSGETXATTR`/`FS_IOC_FSSETXATTR`, set quota limits via `quotactl`, create the backing block device node, and scan existing directories for used project IDs.

## Control Flow
`NewControl` reads or generates a base project ID, creates/recreates `backingFsBlockDev`, verifies quota support by setting a zero quota, clears project inheritance from the top-level directory, and scans existing children to seed the map and next ID. `SetQuota` reuses an existing project ID for a target or assigns `nextProjectID` to an empty directory, sets `FS_XFLAG_PROJINHERIT`, records the mapping, increments the counter, and applies block/inode limits. Reads resolve the stored project ID and call `Q_XGETPQUOTA`.

## State And Persistence
Persistent state includes XFS project IDs and inherit flags on directories plus the block-device node under the quota home. In-memory state is `sync.Map` quota assignments and `nextProjectID`. On startup, `findNextProjectID` reconstructs much of the in-memory state from existing directories.

## Dependencies And Integration Points
The file uses cgo Linux quota and fs ioctls, `unix.Syscall6`, `directory.DiskUsage`, logrus, and filesystem stat data. Overlay initializes `Control` only on XFS and calls `SetQuota`, `GetDiskUsage`, and `ClearQuota`.

## Risks And Edge Cases
Project ID generation is inode-derived and reserves ranges of 10,000 IDs per quota home, reducing but not eliminating administrative conflicts. `SetQuota` requires empty target directories because project ID inheritance does not apply retroactively. Missing `backingFsBlockDev` is recreated on quota set, but device changes and copied stores remain operational hazards. Concurrency relies on `sync.Map` but `nextProjectID` increments are not protected by an explicit mutex in this file.

## Test Signals
Coverage depends on quota-capable XFS integration tests. ZFS has quota tests separately; this package has no direct unit test in the listed files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go

## Purpose
This fallback quota implementation preserves the quota API on non-Linux, non-cgo, or quota-excluded builds.

## Important APIs, Types, And Functions
It defines the same `Quota` struct and a stub `Control`. `NewControl`, `SetQuota`, and `GetQuota` return errors saying quotas are unsupported; `ClearQuota` is a no-op.

## Control Flow
All modifying/query operations fail immediately except cleanup.

## State And Persistence
No quota state is read or written.

## Dependencies And Integration Points
Build tags select this file for unsupported configurations. Overlay initialization uses the error from `NewControl` to decide whether storage options requiring quota should fail.

## Risks And Test Signals
Callers must gate quota-required behavior on `NewControl` success. This file intentionally does not implement `GetDiskUsage`, because quota-aware usage is only compiled into the overlay disk quota file for supported builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_aufs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_aufs.go

## Purpose
This file conditionally registers the aufs graphdriver by blank-importing its package.

## Important APIs, Types, And Functions
There are no exported symbols; the blank import triggers the aufs package `init`.

## Control Flow
Registration occurs at package initialization when built with `linux` and without `exclude_graphdriver_aufs`.

## State And Persistence
No state is persisted here, though the imported driver registers into the global graphdriver registry.

## Dependencies And Integration Points
The package is used by consumers that want all available drivers linked by importing `drivers/register`.

## Risks And Test Signals
Build tags are the main behavior. Incorrect tags could unexpectedly include a driver with unavailable prerequisites.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_aufs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_btrfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_btrfs.go

## Purpose
This file conditionally registers the btrfs graphdriver.

## Important APIs, Types, And Functions
It has only a blank import of `github.com/containers/storage/drivers/btrfs`.

## Control Flow
The btrfs driver's `init` runs when this file is included by `linux && !exclude_graphdriver_btrfs`.

## State And Persistence
Only global driver-registry state changes.

## Dependencies And Integration Points
The build tag pairs with `hack/btrfs_tag.sh`, which can emit the exclusion tag when btrfs headers are unavailable.

## Risks And Test Signals
Registration availability depends on build environment and tags, not runtime probing in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_btrfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_overlay.go -->
# sources/cloud-native/containers-storage/drivers/register/register_overlay.go

## Purpose
This file conditionally registers the overlay graphdriver.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/overlay`.

## Control Flow
The overlay driver's `init` registers both `overlay` and `overlay2` when built with `linux && !exclude_graphdriver_overlay`.

## State And Persistence
Only in-process graphdriver registry state is affected.

## Dependencies And Integration Points
Consumers import `drivers/register` to make overlay discoverable without explicitly importing the driver package.

## Risks And Test Signals
If the build excludes this file, overlay names will not resolve through the registry even if overlay source exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_vfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_vfs.go

## Purpose
This file always links the VFS graphdriver into the driver registry.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/vfs`.

## Control Flow
Package initialization of VFS registers the `vfs` driver.

## State And Persistence
No persistent state; the global driver registry is populated.

## Dependencies And Integration Points
VFS is the portable fallback driver and is available regardless of Linux-specific graphdrivers.

## Risks And Test Signals
The file is intentionally minimal. Regressions would present as missing `vfs` registration in driver discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_zfs.go -->
# sources/cloud-native/containers-storage/drivers/register/register_zfs.go

## Purpose
This file conditionally registers the ZFS graphdriver.

## Important APIs, Types, And Functions
It blank-imports `github.com/containers/storage/drivers/zfs`.

## Control Flow
ZFS registration runs on Linux, FreeBSD, or Solaris unless `exclude_graphdriver_zfs` is set for Linux/FreeBSD.

## State And Persistence
Only graphdriver registry state changes.

## Dependencies And Integration Points
The registration makes ZFS available to storage configuration that selects it by name.

## Risks And Test Signals
Runtime ZFS prerequisites are checked in `zfs.Init`; this file only controls link-time availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/register/register_zfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/template.go -->
# sources/cloud-native/containers-storage/drivers/template.go

## Purpose
`template.go` provides a naive implementation of create-from-template for graphdrivers that can create, remove, diff, and apply layers but lack a specialized clone/template path.

## Important APIs, Types, And Functions
`TemplateDriver` combines `DiffDriver`, `CreateReadWrite`, `Create`, and `Remove`. `NaiveCreateFromTemplate` creates the destination layer, diffs the template against the requested parent, and applies that diff to the new layer.

## Control Flow
The function chooses read-write or read-only creation, removes the new layer if creation of the diff or apply fails, defers closing the diff reader, then calls `ApplyDiff` with template mappings and mount label from `CreateOpts`.

## State And Persistence
It creates a new layer through the supplied driver and may delete it on errors. The actual persistent layout is driver-specific.

## Dependencies And Integration Points
It is a graphdriver-level helper for drivers without native template support. It depends on idtools mappings and logrus for cleanup errors.

## Risks And Test Signals
The implementation assumes `opts` is non-nil when reading `opts.MountLabel` and `opts.ignoreChownErrors`; callers must satisfy that contract. It can be expensive because it streams a full diff instead of using filesystem-native cloning.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go -->
# sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go

## Purpose
This Linux-specific VFS helper copies a parent layer directory into a child layer using the optimized driver copy package.

## Important APIs, Types, And Functions
`dirCopy(srcDir, dstDir string) error` calls `copy.DirCopy(srcDir, dstDir, copy.Content, true)`.

## Control Flow
The helper delegates all traversal and copy behavior to the copy package.

## State And Persistence
It materializes a full copy of parent contents in the destination VFS layer directory.

## Dependencies And Integration Points
`driver.go` calls `dirCopy` during `Create` when a parent exists. Linux builds use this implementation instead of tar-based copying.

## Risks And Test Signals
Copy semantics are determined by `drivers/copy`; permissions, xattrs, hardlinks, and special files must remain consistent with graphdriver expectations. VFS graphdriver tests exercise parent snapshot creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go

## Purpose
This non-Linux VFS helper provides directory copy behavior via tar archive streaming.

## Important APIs, Types, And Functions
`dirCopy(srcDir, dstDir string) error` calls `chrootarchive.NewArchiver(nil).CopyWithTar`.

## Control Flow
All copy logic is delegated to the archive package.

## State And Persistence
It writes a complete destination directory copy for VFS child layers.

## Dependencies And Integration Points
The `!linux` build tag selects this fallback for platforms without the Linux copy implementation.

## Risks And Test Signals
Tar copy behavior may differ from Linux copy behavior for platform-specific metadata. Cross-platform VFS tests are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/driver.go -->
# sources/cloud-native/containers-storage/drivers/vfs/driver.go

## Purpose
`driver.go` implements the VFS graphdriver, a simple portable driver that stores each layer as a full directory copy instead of using copy-on-write filesystem features.

## Important APIs, Types, And Functions
`Init` registers and constructs `Driver`. `Driver` holds driver name, home, additional homes, ignore-chown flag, naive diff driver, ID-map updater, and optional image store. Public methods implement graphdriver behavior: `Create`, `CreateReadWrite`, `CreateFromTemplate`, `Get`, `Put`, `Remove`, `DeferredRemove`, `ListLayers`, `Diff`, `ApplyDiff`, `Changes`, `DiffSize`, `UpdateLayerIDMap`, `ReadWriteDiskUsage`, and `Dedup`.

## Control Flow
Initialization creates `<home>/dir`, parses limited VFS options, and wraps the driver in naive diff/update helpers. Layer creation resolves ID mappings, creates `<home>/dir/<id>` or image-store paths, copies parent contents if present, and applies SELinux labels best-effort. `Get` validates the directory and rejects mount options except `ro`; `Put` is a no-op. Diff, changes, and apply delegate to the naive diff driver. Removal deletes the directory directly or stages it through `tempdir` for deferred cleanup.

## State And Persistence
Persistent state is just directories under `<home>/dir/<id>` plus optional image-store/additional-home copies. There is no mount table or driver metadata file. Temporary deletion roots live under `<home>/tempdirs` and optional image-store tempdirs.

## Dependencies And Integration Points
The driver integrates with graphdriver registration, naive diff, naive layer ID-map updater, copy helpers, archive/directory utilities, idtools, SELinux label setup, tempdir staged deletion, and internal dedup. Additional image stores are read-only search paths for existing layers.

## Risks And Edge Cases
VFS is space-heavy because every child starts as a full copy. `dir2` uses `filepath.Base(id)`, so callers must not rely on hierarchical IDs. Mount options are mostly unsupported. `UpdateLayerIDMap` delegates chowning then explicitly chowns the root directory, which can fail if mappings are incomplete. Additional homes are searched for reads but writable layers are only primary/image-store.

## Test Signals
`vfs_test.go` runs graphtest create/base/snapshot/template/diff/apply/changes/echo/list lifecycle tests. Dedup and option parsing have separate support tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/vfs_test.go -->
# sources/cloud-native/containers-storage/drivers/vfs/vfs_test.go

## Purpose
This Linux test file verifies VFS graphdriver behavior through shared graphtest scenarios.

## Important APIs, Types, And Functions
`init` calls `reexec.Init`. Tests cover setup, empty/base/snapshot/template creation, diff/apply with 100 files, changes, echo, list layers, and teardown.

## Control Flow
The suite reuses a driver between setup and teardown, running standard graphdriver checks in between.

## State And Persistence
Tests create temporary VFS layer directories and copied contents through the driver.

## Dependencies And Integration Points
The file relies on `drivers/graphtest` and package reexec support.

## Risks And Test Signals
The tests provide broad conformance coverage but do not directly test additional image stores, deferred remove, dedup, or ID-map update edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/vfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs.go

## Purpose
`zfs.go` implements the Linux/FreeBSD ZFS graphdriver using ZFS datasets, snapshots, clones, and legacy mounts.

## Important APIs, Types, And Functions
`zfsOptions` stores dataset name, mount path, and mount options. `Driver` holds the root dataset, options, a mutex-protected filesystem cache, and mount ref counter. Important functions include `Init`, `parseOptions`, `lookupZfsDataset`, `cloneFilesystem`, `Create`, `Get`, `Put`, `Remove`, `Status`, `Metadata`, `parseStorageOpt`, and `setQuota`.

## Control Flow
`Init` checks for the `zfs` command and `/dev/zfs`, parses options, derives the backing dataset from rootdir if not configured, enumerates child filesystems, creates the base directory, and returns a naive diff wrapper. Creating a base layer creates a ZFS filesystem with `mountpoint=legacy`, optionally sets quota, mounts it temporarily to adjust permissions/ownership/label behavior, and unmounts. Creating a child layer snapshots the parent dataset, clones the snapshot, marks the clone in cache, and destroys the snapshot with deferred deletion. `Get` mounts the dataset at `<base>/graph/<id>`, supports `ro` through remount, and ref-counts mounts. `Put` decrements, detach-unmounts, and removes the mountpoint. `Remove` destroys datasets recursively and updates the cache.

## State And Persistence
Persistent state is stored in ZFS datasets, snapshots/clones during creation, dataset quota properties, and mountpoint directories under `<base>/graph`. In-memory state is the dataset cache and ref counter. `ListLayers` is intentionally unsupported because arbitrary datasets can resemble layers.

## Dependencies And Integration Points
The driver uses `github.com/mistifyio/go-zfs/v3`, graphdriver naive diff/updater wrappers, mount helpers, idtools, SELinux labels, tempdir type compatibility, directory usage, and platform helpers in `zfs_linux.go`/`zfs_freebsd.go`.

## Risks And Edge Cases
The driver depends on external `zfs` tooling, `/dev/zfs`, correct dataset discovery, and legacy mount behavior. Snapshot names use `time.Now().Nanosecond()`, which may collide under rapid operations. Destroy retry logic handles aborted builds when datasets already exist. Read-only mounts first mount read-write to set state, then remount, which can surprise strict callers. Dedup and ListLayers are effectively unsupported.

## Test Signals
`zfs_test.go` runs graphtest lifecycle tests and quota tests, but requires a real ZFS environment and Linux build for the listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go

## Purpose
This FreeBSD companion supplies platform-specific ZFS root checks, mountpoint naming, and unmount behavior.

## Important APIs, Types, And Functions
`checkRootdirFs` verifies `unix.Statfs_t.Fstypename` starts with `zfs`. `getMountpoint` returns the ID unchanged. `detachUnmount` uses `unix.MNT_FORCE`.

## Control Flow
The filesystem check stats the rootdir and returns `graphdriver.ErrPrerequisites` when it is not ZFS.

## State And Persistence
No state is persisted here; functions inspect filesystem type and unmount existing ZFS mountpoints.

## Dependencies And Integration Points
`zfs.go` calls these helpers during initialization and mount cleanup.

## Risks And Test Signals
The Fstypename byte comparison is platform-specific and intentionally low-level. FreeBSD test coverage must validate the expected statfs layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go

## Purpose
This Linux companion supplies root filesystem validation and detach unmount behavior for the ZFS driver.

## Important APIs, Types, And Functions
`checkRootdirFs` uses `graphdriver.GetFSMagic` and requires `FsMagicZfs`. `getMountpoint` returns the ID unchanged. `detachUnmount` calls `unix.Unmount(..., unix.MNT_DETACH)`.

## Control Flow
If filesystem magic is not ZFS, the helper logs backing filesystem information and returns an error wrapping `graphdriver.ErrPrerequisites`.

## State And Persistence
No persistent state is modified; unmount affects kernel mount state.

## Dependencies And Integration Points
`zfs.Init`, `zfs.Get`, and `zfs.Put` depend on these helpers for platform behavior.

## Risks And Test Signals
The root directory must already reside on ZFS unless `zfs.fsname` is supplied. Tests require Linux with ZFS available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_test.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_test.go

## Purpose
This Linux test file applies shared graphdriver conformance tests to the ZFS driver.

## Important APIs, Types, And Functions
Tests cover setup, empty/base/snapshot/template creation, quota setting, echo behavior, and teardown via `graphtest`.

## Control Flow
The suite creates a driver in `TestZfsSetup`, runs standard tests, then releases it in `TestZfsTeardown`.

## State And Persistence
Tests require and manipulate real ZFS datasets/mountpoints through the driver.

## Dependencies And Integration Points
The file depends on `drivers/graphtest` and a suitable ZFS host environment.

## Risks And Test Signals
These tests are high-value integration signals but are likely skipped or fail in environments lacking ZFS prerequisites. They do not cover ListLayers unsupported behavior or all mount option permutations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go

## Purpose
This file provides an empty `zfs` package on platforms where the ZFS implementation is not built.

## Important APIs, Types, And Functions
There are no declarations beyond the package statement.

## Control Flow
No runtime behavior exists.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The build tag `!linux && !freebsd` lets imports of the package compile without registering a usable driver.

## Risks And Test Signals
Consumers must rely on build tags/registration and driver lookup results rather than expecting a runtime unsupported error from this package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/errors.go -->
# sources/cloud-native/containers-storage/errors.go

## Purpose
`errors.go` re-exports canonical storage errors from `types` and defines one internal image-name operation error.

## Important APIs, Types, And Functions
Exported variables include container, image, layer, digest, duplicate, read-only, unsupported, load, mapping, and size errors such as `ErrContainerUnknown`, `ErrImageUnknown`, `ErrDuplicateName`, `ErrStoreIsReadOnly`, and `ErrInvalidMappings`. `errInvalidUpdateNameOperation` is package-internal.

## Control Flow
There is no dynamic control flow. Variables are aliases to `types` errors so callers can use the storage package API.

## State And Persistence
No state is stored beyond package-level error values.

## Dependencies And Integration Points
The file preserves public API compatibility while centralizing error definitions in `types`. Store, image, layer, container, and mapping code wrap these sentinels with contextual errors.

## Risks And Test Signals
Changing aliases would break `errors.Is` behavior and public compatibility. The internal update-name error is used by name mutation code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/btrfs_tag.sh -->
# sources/cloud-native/containers-storage/hack/btrfs_tag.sh

## Purpose
This build helper emits a Go build exclusion tag when Linux btrfs headers are unavailable.

## Important APIs, Types, And Functions
It uses `${GO:-go} env GOOS`, the system C preprocessor, and `#include <btrfs/ioctl.h>`.

## Control Flow
Non-Linux exits successfully with no output. On Linux, it preprocesses a small C snippet; if preprocessing fails, it prints `exclude_graphdriver_btrfs`.

## State And Persistence
No files are modified.

## Dependencies And Integration Points
Build scripts can use the output as a build tag, pairing with `register_btrfs.go`.

## Risks And Test Signals
It assumes `cc` is available. Header detection is compile-time and may not reflect runtime btrfs capability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/btrfs_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh -->
# sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh

## Purpose
This wrapper works around gccgo include path behavior for vendored dependencies.

## Important APIs, Types, And Functions
It scans command arguments for directories containing `github.com/containers/storage/vendor` and appends `-I <vendor>` flags before execing `gccgo`.

## Control Flow
For each argument that is a directory with the vendor path, it accumulates include flags, then replaces the shell with `gccgo $addflags "$@"`.

## State And Persistence
No persistent state is written.

## Dependencies And Integration Points
The script integrates with gccgo build flows and references a Go issue in comments.

## Risks And Test Signals
Arguments with spaces are handled for original arguments but `addflags` is expanded as a string, so unusual paths could be fragile. It assumes gccgo is on `PATH`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/gccgo-wrapper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/generate-authors.sh -->
# sources/cloud-native/containers-storage/hack/generate-authors.sh

## Purpose
This helper regenerates the repository `AUTHORS` file from git history.

## Important APIs, Types, And Functions
It changes to the repository root, writes a fixed header, then appends unique author names/emails from `git log --format='%aN <%aE>'` sorted with `LC_ALL=C.UTF-8 sort -uf`.

## Control Flow
`set -e` aborts on failure. Output is redirected atomically only at shell-redirection granularity to `AUTHORS`.

## State And Persistence
It overwrites `AUTHORS` in the repository root.

## Dependencies And Integration Points
It depends on git history and `.mailmap` behavior for deduplication.

## Risks And Test Signals
Running outside a git checkout or without expected locale support can fail. The write is not temp-file atomic, so interruption could leave a partial `AUTHORS`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/generate-authors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/get_ci_vm.sh -->
# sources/cloud-native/containers-storage/hack/get_ci_vm.sh

## Purpose
This developer helper creates or configures a Google Cloud VM for debugging Cirrus-CI tasks for containers/storage.

## Important APIs, Types, And Functions
`in_get_ci_vm` gates container-entrypoint-only modes. `--config` prints repository-specific VM/container settings. `--setup` runs `contrib/cirrus/setup.sh`. The default path runs `podman run` with gcloud config and repository bind mounts against `quay.io/libpod/get_ci_vm:latest`.

## Control Flow
The script resolves its own path and repo root, branches on the first argument, validates `GET_CI_VM` for internal modes, then either emits config, performs setup, or launches the helper container.

## State And Persistence
It may create `$HOME/.config/gcloud/ssh` and the helper container can create cloud VMs or modify gcloud-related config. It does not directly edit repository files except through setup mode.

## Dependencies And Integration Points
Dependencies include podman, gcloud credentials, the get_ci_vm container image, Cirrus-CI conventions, and repository setup scripts.

## Risks And Test Signals
This is operational tooling with external side effects and access prerequisites. Volume SELinux flags and overlay `:O` bind behavior are environment-sensitive.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/get_ci_vm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/git-validation.sh -->
# sources/cloud-native/containers-storage/hack/git-validation.sh

## Purpose
This helper runs DCO and short-subject validation over commits in the current branch.

## Important APIs, Types, And Functions
It expects `tests/tools/build/git-validation` to be executable, determines `EPOCH_TEST_COMMIT` from `CIRRUS_BASE_SHA` or `git merge-base ${DEST_BRANCH:-main} HEAD`, and execs the validator with `-q -run DCO,short-subject`.

## Control Flow
Missing validator prints install guidance and exits 1. Otherwise it computes the range and replaces the shell with the validation tool.

## State And Persistence
No repository state is modified.

## Dependencies And Integration Points
It integrates with CI variables and local tool installation via `make install.tools`.

## Risks And Test Signals
Unquoted branch variable expansion is typical shell risk for unusual values. The correctness of the range depends on CI base SHA or local `DEST_BRANCH`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/git-validation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/govet.sh -->
# sources/cloud-native/containers-storage/hack/govet.sh

## Purpose
This helper runs `go vet` for all non-vendor packages.

## Important APIs, Types, And Functions
It uses `go list ./... | grep -v /vendor/` and runs `go vet` for each package.

## Control Flow
The script exits immediately with an error message if any package fails vet; otherwise exits 0.

## State And Persistence
No files are modified.

## Dependencies And Integration Points
It depends on the Go toolchain and package list resolution.

## Risks And Test Signals
Package names with whitespace are not handled, though Go import paths normally avoid that. It runs packages sequentially and may be slower than `go vet ./...`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/govet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/libsubid_tag.sh -->
# sources/cloud-native/containers-storage/hack/libsubid_tag.sh

## Purpose
This build helper detects whether the system can compile and link against libsubid.

## Important APIs, Types, And Functions
It checks `${GO:-go} env GOOS`, creates a temporary directory, compiles a C program including `<shadow/subid.h>` and linking `-l subid`, handles ABI differences around `SUBID_ABI_MAJOR`, and prints `libsubid` on success.

## Control Flow
Non-Linux exits with no output. On Linux it builds the probe program and removes the temporary directory through a trap.

## State And Persistence
It writes only a temporary probe binary under `$PWD/tmp.$RANDOM`, then deletes it.

## Dependencies And Integration Points
Build systems can consume its output as a build tag to enable libsubid-backed code.

## Risks And Test Signals
The temporary path is predictable enough for local build tooling but not hardened. The probe assumes `cc`, headers, and libraries are installed and linkable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/libsubid_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/tree_status.sh -->
# sources/cloud-native/containers-storage/hack/tree_status.sh

## Purpose
This helper verifies that the git worktree is clean.

## Important APIs, Types, And Functions
It captures `git status --porcelain`.

## Control Flow
With empty status, it prints `tree is clean`. Otherwise it prints a dirty-tree message, the porcelain status, and exits 1.

## State And Persistence
No state is modified.

## Dependencies And Integration Points
It is suitable for CI or release checks that require no uncommitted changes.

## Risks And Test Signals
It reports all untracked files as dirty and assumes it is run inside a git worktree.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/tree_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/idset.go -->
# sources/cloud-native/containers-storage/idset.go

## Purpose
`idset.go` implements interval-set operations for UID/GID mapping management and conflict detection.

## Important APIs, Types, And Functions
`idSet` wraps `intervalset.ImmutableSet`. `newIDSet`, `getHostIDs`, `getContainerIDs`, `subtract`, `union`, `iterator`, `size`, `findAvailable`, and `zip` compose and consume ID intervals. `interval` implements `intervalset.Interval` through `Intersect`, `Before`, `IsZero`, `Bisect`, `Adjoin`, and `Encompass`. `hasOverlappingRanges` detects overlapping host or container ID mappings.

## Control Flow
Input ID maps are converted to half-open intervals. Set operations delegate to `github.com/google/go-intervals/intervalset`. Iteration launches a goroutine that streams intervals over a channel until exhausted or canceled. `findAvailable` walks intervals and truncates the final interval to allocate exactly the requested size. `zip` walks host and container sets in parallel to produce contiguous `idtools.IDMap` entries.

## State And Persistence
All state is in-memory and immutable once an `idSet` is constructed. No disk state is written.

## Dependencies And Integration Points
The code integrates with storage ID-map allocation logic, idtools mappings, and public storage errors. It uses `types.ErrNoAvailableIDs` and wraps `ErrInvalidMappings` for conflicts.

## Risks And Edge Cases
The iterator requires callers to call cancel unless it returns nil; the implementation uses `defer cancel` in local methods. Negative or zero-length intervals collapse to empty sets. `hasOverlappingRanges` reports the incoming mapping that conflicts, but it accumulates conflicts after mutating interval sets.

## Test Signals
`idset_test.go` is extensive: it covers construction, host/container extraction, set operators, sizing, allocation, zipping, interval interface behavior, and overlapping mapping detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/idset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/idset_test.go -->
# sources/cloud-native/containers-storage/idset_test.go

## Purpose
This test file validates interval and ID-map set logic used by storage mapping allocation.

## Important APIs, Types, And Functions
Helpers `allIntervals`, `idSetsEqual`, and `assertIntervalSame` normalize comparisons. Test groups cover `newIDSet`, `getHostIDs`, `getContainerIDs`, `subtract`, `union`, `size`, `findAvailable`, `zip`, interval methods, and `hasOverlappingRanges`.

## Control Flow
Large table-driven cases exercise nil, empty, invalid, overlapping, adjacent, unordered, and multi-interval inputs. Operator tests also verify that original sets are unchanged after operations. Reflective interval tests check behavior in both operand orders.

## State And Persistence
Tests are pure in-memory and write no durable state.

## Dependencies And Integration Points
The tests depend on `idtools.IDMap`, `intervalset`, and Go's testing/reflect packages.

## Risks And Test Signals
The suite is strong for mathematical behavior and edge cases. It does not directly test goroutine leaks from missed iterator cancellation, but production methods consistently defer cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/idset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/images.go -->
# sources/cloud-native/containers-storage/images.go

## Purpose
`images.go` implements the persistent image metadata store: image records, names, name history, top layers, mapped top layers, metadata, big-data blobs, digest indexes, locking, reload, save, garbage collection, and read-only/read-write views.

## Important APIs, Types, And Functions
`Image` is the stored record. `roImageStore` and `rwImageStore` define internal store capabilities. `imageStore` owns the lockfile, directory, in-process lock, `images` slice, truncation index, and lookup maps. Key functions include `newImageStore`, `newROImageStore`, `startReading`, `startWriting`, `reloadIfChanged`, `load`, `Save`, `create`, `updateNames`, `Delete`, `Get`, `Images`, `ByDigest`, `SetBigData`, `BigData*`, flag setters, mapped-layer setters, `GarbageCollect`, and `Wipe`.

## Control Flow
Callers acquire read or write locks before using store methods. Reads first use the on-disk lockfile `LastWrite` state to decide whether to reload. If a read reload detects duplicate image names that a writable save could repair, it upgrades through a write lock path and retries. `load` reads `images.json`, rebuilds indexes, recomputes digests from explicit image digest and manifest-like big data names, removes duplicate names from older records when writable, and saves repaired state. `create` validates ID/name uniqueness, appends a record, saves metadata, then writes requested big-data items. `updateNames` applies set/add/remove operations, transfers names away from conflicting images, appends name history, and saves. `Delete` updates every index, saves, and removes the image data directory.

## State And Persistence
Persistent state is `images.json`, `images.lock`, and per-image data directories containing big-data files named through the big-data basename helper. In-memory state mirrors the JSON plus indexes by full/truncated ID, name, and digest. The store uses atomic writes for JSON and big data. `GarbageCollect` removes unreferenced ID-looking directories after crashes.

## Dependencies And Integration Points
The file depends on lockfile, ioutils atomic writes, string IDs, string utilities, truncindex, digest validation, and package-level helpers such as `dedupeStrings`, `applyNameOperation`, `makeBigDataBaseName`, and map/slice copy helpers from neighboring files. Higher-level storage operations use these interfaces for image lifecycle and lookup.

## Risks And Edge Cases
Lock ordering is subtle: the filesystem lock must be held before the in-process lock, and reload upgrades must avoid stale `LastWrite` assumptions. Read-only stores cannot repair duplicate names and return `ErrDuplicateImageNames`. Big data writes happen after the image JSON record is saved, so partial creation cleanup must use `Delete`. Digest indexes depend on valid digest strings and manifest key naming. Methods often require the caller to have already locked correctly; misuse can race or panic.

## Test Signals
`images_test.go` covers name history and conflict transfer semantics. Other image store behaviors are likely covered elsewhere; this subset does not directly test reload upgrade, duplicate-name repair, big data persistence, garbage collection, or read-only errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/images.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/images_test.go -->
# sources/cloud-native/containers-storage/images_test.go

## Purpose
This test file validates image name history behavior and name ownership transfer between images.

## Important APIs, Types, And Functions
`newTestImageStore` creates a temporary read-write image store. `addTestImage` creates an image and assigns names. `TestAddNameToHistorySuccess` checks de-duplication of history entries. `TestHistoryNames` checks set/add/remove name operations and conflict handling.

## Control Flow
The main test creates two images with overlapping requested names, verifies the later image takes conflicting names, then reassigns many names to the first image and verifies the second loses them. It also tests add and remove operations preserving history.

## State And Persistence
Tests use a temporary store directory, writing real `images.json`, lockfiles, and image metadata through store APIs.

## Dependencies And Integration Points
The file depends on digest defaults, testify require, and image store internal methods.

## Risks And Test Signals
Coverage is focused on name history only. It is a useful regression signal for `updateNames` conflict transfer, but does not cover big data, reload, garbage collection, or read-only store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup.go

## Purpose
`dedup.go` implements platform-independent orchestration for file deduplication by grouping candidate files by checksum and asking platform-specific reflink/dedupe code to share storage.

## Important APIs, Types, And Functions
`DedupHashMethod` supports invalid, CRC64, file size, and SHA256 strategies. `DedupOptions` selects the hash method. `DedupResult` reports total deduped bytes. `getFileChecksum` hashes a file using `readAllFile`. `DedupDirs` walks directories, groups paths by checksum, skips zero-byte and already-visited inodes, and calls `dedupFiles.dedup`.

## Control Flow
`DedupDirs` initializes platform `dedupFiles`, then parallel-walks each directory using `pwalkdir.Walk`. For each regular non-empty file, it checks inode visitation, computes a checksum, locks the checksum bucket, tries deduping against known source paths, and appends as a future source if no dedupe succeeded. `errNotSupported` short-circuits as a non-fatal result.

## State And Persistence
In-memory maps track checksum groups and visited inodes. Persistent effects are filesystem reflink/dedupe operations that can cause duplicate file extents to share storage.

## Dependencies And Integration Points
Overlay and VFS drivers call `DedupDirs` for selected layer directories. The platform-specific files provide inode tracking, checksum reading, and Linux `FIDEDUPERANGE` ioctl behavior.

## Risks And Edge Cases
`DedupHashFileSize` is unsafe as a true content hash and should be used only when callers accept possible false positives guarded by kernel dedupe verification. Hash bucket locking and global result locking are concurrency-sensitive. Some filesystems can return unsupported per-file after walking has begun; this returns current savings with nil error.

## Test Signals
`dedup_linux_test.go` tests inode visit tracking. Full dedupe behavior depends on filesystem support and is not directly covered in the listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go

## Purpose
This Linux implementation provides inode tracking, file reading, and `FIDEDUPERANGE` ioctl support for deduplication.

## Important APIs, Types, And Functions
`deviceInodePair` keys visited files by device and inode. `dedupFiles` stores a mutex-protected visited set. `newDedupFiles`, `recordInode`, `isFirstVisitOf`, `dedup`, and `readAllFile` implement platform operations.

## Control Flow
`isFirstVisitOf` extracts `syscall.Stat_t` and records the inode. `dedup` opens source read-only and destination write-only, rejects hardlinks by comparing device/inode, builds `unix.FileDedupeRange`, and calls `unix.IoctlFileDedupeRange`; `ENOTSUP` is normalized to `errNotSupported`. `readAllFile` reads small files into memory and mmaps larger files with sequential madvise before hashing.

## State And Persistence
Visited inode state is in-memory. Successful ioctl calls modify filesystem extent sharing for destination files.

## Dependencies And Integration Points
`dedup.go` calls these methods while walking driver layer directories. The code depends on Linux file dedupe ioctl support and `golang.org/x/sys/unix`.

## Risks And Edge Cases
Mmap of large files can fail; small-file reads assume stable file size from `fs.FileInfo`. Destination files are opened write-only because the ioctl targets their fd. The function reports unsupported reflinks as benign to the caller, but other ioctl errors abort dedup.

## Test Signals
`dedup_linux_test.go` verifies inode recording and repeat detection, including separate device/inode pairs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go

## Purpose
This Linux unit test validates the in-memory inode visitation logic used to avoid redundant dedupe work.

## Important APIs, Types, And Functions
`wasVisited` inspects `dedupFiles.visitedInodes` under lock. `TestRecordAndCheckInode` exercises `newDedupFiles` and `recordInode`.

## Control Flow
The test creates a dedup state, verifies an inode is initially unvisited, records it, verifies repeat detection, and checks different inode/device pairs remain unvisited.

## State And Persistence
No filesystem dedupe is performed; state is in-memory.

## Dependencies And Integration Points
The test uses testify assertions and the Linux dedup implementation.

## Risks And Test Signals
It does not test `IoctlFileDedupeRange`, checksum hashing, mmap reads, or walking behavior, but it covers the concurrency-protected visited map basics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go

## Purpose
This non-Linux fallback marks deduplication primitives as unsupported.

## Important APIs, Types, And Functions
`newDedupFiles`, `isFirstVisitOf`, `dedup`, and `readAllFile` all return `errNotSupported`.

## Control Flow
All operations fail immediately with the shared unsupported sentinel.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
`DedupDirs` treats `errNotSupported` as a benign result, so drivers can expose `Dedup` portably.

## Risks And Test Signals
Callers receive zero savings without an error at the orchestration level. Platform-specific tests should ensure unsupported behavior remains non-fatal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts.go -->
# sources/cloud-native/containers-storage/internal/opts/opts.go

## Purpose
`opts.go` implements reusable command/config option value types and validators.

## Important APIs, Types, And Functions
`ListOpts`, `NamedListOpts`, `MapOpts`, `NamedMapOpts`, `FilterOpt`, `ValidatorFctType`, and `ValidatorFctListType` are the main types. Methods support `Set`, `Delete`, `Get`, `GetAll`, `GetAllOrEmpty`, `GetMap`, `Len`, `Type`, `Name`, `String`, and filter `Value`. Validators include `ValidateIPAddress`, `ValidateLabel`, and `ValidateSysctl`.

## Control Flow
List and map setters optionally normalize input through a validator, then append or split key/value data. `ValidateIPAddress` trims and parses with `net.ParseIP`. `ValidateLabel` requires at least one `=`. `ValidateSysctl` allows a fixed set of kernel keys plus `net.` and `fs.mqueue.` prefixes. `FilterOpt.Set` parses `key=value` filter strings into `Args`.

## State And Persistence
All state is in-memory. List options can wrap caller-owned slices by pointer; map options can wrap caller-owned maps.

## Dependencies And Integration Points
These types are typically used as flag values or configuration parsing helpers. `FilterOpt` delegates to `parse.go`'s `Args`.

## Risks And Edge Cases
`MapOpts.Set` accepts strings without `=` and stores an empty value. `ListOpts.GetAll` returns the underlying slice, not a defensive copy. `ValidateSysctl` uses `strings.Split` rather than `Cut`, so values containing `=` are still accepted as long as the key is allowed.

## Test Signals
`opts_test.go` covers IP validation, map/list option behavior, label validation, and named option wrappers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts_test.go -->
# sources/cloud-native/containers-storage/internal/opts/opts_test.go

## Purpose
This test file verifies option containers and validators in `internal/opts`.

## Important APIs, Types, And Functions
Tests cover `ValidateIPAddress`, `MapOpts`, `ListOpts` with and without validators, `ValidateLabel`, `NamedListOpts`, and `NamedMapOpts`. `logOptsValidator` is a test validator accepting `max-size` and `max-file`.

## Control Flow
The tests set values, assert string forms and lengths, verify validator rejection, delete values, inspect duplicate handling through `GetMap`, and ensure named wrappers update referenced storage.

## State And Persistence
Tests use in-memory maps and slices only.

## Dependencies And Integration Points
The tests use testify and the public opts package API from an external test package.

## Risks And Test Signals
Coverage does not include `ValidateSysctl`, `FilterOpt`, or the richer `Args` matching behavior in `parse.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/parse.go -->
# sources/cloud-native/containers-storage/internal/opts/parse.go

## Purpose
`parse.go` implements Docker-derived filter argument parsing and matching.

## Important APIs, Types, And Functions
`Args` stores `map[key]map[value]bool`. `KeyValuePair`, `Arg`, `NewArgs`, `ParseFlag`, `ToParam`, `ToJSON`, `MarshalJSON`, `Get`, `Add`, `Del`, `Len`, `MatchKVList`, `Match`, `ExactMatch`, `UniqueExactMatch`, `FuzzyMatch`, `Include`, `Contains`, `Validate`, and `WalkValues` are the main API. `ErrBadFormat` and `invalidFilterError` model errors.

## Control Flow
`ParseFlag` accepts `name=value`, trims/lowercases names, trims values, and adds them to a value set. Matching helpers interpret absent filters as match-all, exact matches before regex matching, and prefix matching for fuzzy checks. `Validate` rejects keys absent from an accepted map. `WalkValues` calls a callback for each value under a field.

## State And Persistence
All filter state is in-memory. JSON encoding returns an empty byte slice or string for no filters.

## Dependencies And Integration Points
`FilterOpt` wraps this type for flag parsing. Higher-level commands can use it to filter images, containers, or metadata maps.

## Risks And Edge Cases
Map iteration order is intentionally unstable, so `Get`, JSON object key ordering, and `WalkValues` should not be treated as ordered. Regex errors in `Match` are ignored. Empty filters match everything in exact, unique, and key/value list paths.

## Test Signals
The listed `opts_test.go` does not cover this file beyond `FilterOpt` indirectly not being tested. Dedicated tests should cover bad format, JSON output, matching modes, validation, and callback errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go -->
# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go

## Purpose
`rawfilelock.go` exposes the low-level file lock wrapper used by higher-level storage locking packages.

## Important APIs, Types, And Functions
`LockType` has `ReadLock` and `WriteLock`. `FileHandle` aliases the platform-specific `fileHandle`. Public functions are `OpenLock`, `TryLockFile`, `LockFile`, `UnlockAndCloseHandle`, and `CloseHandle`.

## Control Flow
`OpenLock` opens or creates a lock file with read-only or read-write flags and wraps open errors as `os.PathError`. `TryLockFile` calls the platform lock function in non-blocking mode; `LockFile` blocks. Close helpers delegate to platform-specific unlock/close primitives.

## State And Persistence
The lock file path is created if needed. Actual lock state is kernel/OS file-lock state tied to the file handle lifecycle.

## Dependencies And Integration Points
Higher-level `internal/staging_lockfile` and `pkg/lockfile` should be preferred by most callers. Platform-specific files implement `openHandle`, `lockHandle`, `unlockAndCloseHandle`, and `closeHandle`.

## Risks And Edge Cases
The comments emphasize that closing a file handle can release locks, making this primitive unsafe for multiple goroutines sharing the same path. `CloseHandle` is explicitly for corrupted/error paths because Unix cannot close without unlocking.

## Test Signals
Tests for this package are outside the requested file list, but the API is small and high-risk because lock misuse can corrupt storage state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock.go -->
