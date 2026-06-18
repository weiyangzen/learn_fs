# subset-b-000079 research

This grouped report covers the requested containers/storage graphdriver files. Each file section is wrapped with the required source-path markers so reconciliation can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/aufs.go -->
# sources/cloud-native/containers-storage/drivers/aufs/aufs.go

## Purpose
`aufs.go` implements the Linux AUFS graphdriver. It registers `aufs`, validates kernel and backing-filesystem support, creates the `mnt/`, `diff/`, and `layers/` layout, mounts layered filesystems, performs layer lifecycle operations, and implements AUFS-specific diff/archive behavior where possible.

## Important APIs, Types, And Functions
`Driver` owns the graph root, `RefCounter`, path cache, per-layer locker, optional mount options, and a `NaiveDiffDriver` fallback. `Init` performs support checks, option parsing, directory creation, mount-private setup, and stale `*-removing` cleanup. Core methods include `Create`, `Remove`, `Get`, `Put`, `Diff`, `DiffGetter`, `ApplyDiff`, `Changes`, `DiffSize`, `Cleanup`, `aufsMount`, `useDirperm`, `SupportsShifting`, `DeferredRemove`, and `GetTempDirRootDirs`.

## Control Flow
Initialization rejects rootless/user-namespace use, checks `/proc/filesystems`, rejects AUFS-on-AUFS/Btrfs/eCryptfs, parses only `aufs.mountopt`, creates driver directories, and builds a naive diff fallback. `Create` prepares `mnt/<id>` and `diff/<id>`, then writes `layers/<id>` with the direct parent and transitive parents. `Get` locks the layer, reads parents, returns `diff/<id>` for base layers, or mounts an AUFS union at `mnt/<id>` for child layers, using `RefCounter` to avoid duplicate mounts. `Put` decrements and unmounts only when the count reaches zero. `Remove` retries busy unmounts, removes the layer metadata file, then atomically renames/removes `diff` and `mnt` directories.

## State And Persistence
Persistent state is filesystem-based: layer contents in `diff/<id>`, mountpoints in `mnt/<id>`, and parent ordering in newline-delimited `layers/<id>`. Runtime state includes path cache entries and mount reference counts, both rebuilt or invalidated by filesystem checks. Stale `diff/*-removing` and `mnt/*-removing` directories are cleaned on initialization.

## Dependencies And Integration Points
The driver integrates with `graphdriver.Driver`, `RefCounter`, `locker`, `archive`, `chrootarchive`, `directory`, `fileutils`, `idtools`, `mount`, SELinux labels, `tar-split` file getters, and `x/sys/unix`. AUFS mounting is delegated to package-local `mount` and `Unmount` helpers. Non-parent diff requests delegate to `NaiveDiffDriver`.

## Risks
AUFS support depends on kernel module availability and init user namespace. Mount option strings are page-size-limited; `aufsMount` splits excess readonly branches into remount append operations. Incorrect parent metadata breaks union ordering and diff behavior. `Remove` has to handle `EBUSY`, stale temporary directories, and path-cache consistency. ID-map shifting is unsupported, so callers needing shifted layers must not expect native behavior.

## Test Signals
`aufs_test.go` covers initialization, directory layout, create/remove, mounts with and without parents, stale cleanup, diff/apply/changes/size, status, existence, deep layer mount option splitting, and concurrent get/put/remove behavior. Shared `graphtest` tests verify create, snapshot, template, echo, and layer listing semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/aufs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/aufs_test.go -->
# sources/cloud-native/containers-storage/drivers/aufs/aufs_test.go

## Purpose
`aufs_test.go` is the AUFS driver test suite. It validates AUFS-specific lifecycle, mount, diff, cleanup, and concurrency behavior, while also invoking the shared graphdriver contract tests.

## Important APIs, Types, And Functions
Helpers include `testInit`, `newDriver`, `driverGet`, `hash`, and `testMountMoreThan42Layers`. Tests cover `TestNewDriver`, `TestCreateDirStructure`, `TestRemoveImage`, `TestGetWithoutParent`, `TestMountedTrueResponse`, `TestMountWithParent`, `TestChanges`, `TestDiffSize`, `TestApplyDiff`, `TestMountMoreThan42Layers`, `BenchmarkConcurrentAccess`, and `TestInitStaleCleanup`, followed by `graphtest` wrappers.

## Control Flow
Tests create a temporary AUFS root, skip when unsupported, create base and child layers, call `Get`/`Put`/`Remove`, and inspect actual directories or mount state. Diff tests mutate layer contents, export tar streams, apply them to another layer, and verify resulting files. Deep-layer tests create up to 126 layers and verify AUFS mount option splitting across page-size boundaries.

## State And Persistence
Test state lives under `/tmp/aufs-tests` and `/tmp/aufs-tests/aufs`. Tests assert the expected `mnt`, `diff`, and `layers` directories and confirm `*-removing` directories disappear after removal or initialization.

## Dependencies And Integration Points
The suite depends on `graphdriver`, `graphtest`, `archive`, `reexec`, `stringid`, `testify`, and real AUFS kernel mount support. It exercises package-private AUFS helpers because tests are in package `aufs`.

## Risks
Tests are environment-sensitive and skip without AUFS support. They rely on real mounts and permissions, so failures may reflect kernel, namespace, or cleanup issues rather than pure Go logic. Deep layer and concurrent tests are important regressions for mount-data length and locking/refcount correctness.

## Test Signals
The file is itself the main test signal for AUFS. The strongest behavioral signals are coverage of parent mount behavior, direct-parent diff fast paths, fallback graphdriver contracts, stale deletion cleanup, and high-concurrency `Get`/`Put` races.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/aufs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/dirs.go -->
# sources/cloud-native/containers-storage/drivers/aufs/dirs.go

## Purpose
`dirs.go` centralizes AUFS directory and parent metadata helpers. It reads known layer IDs, parses parent chains, and constructs driver paths for mount and diff directories.

## Important APIs, Types, And Functions
`loadIds(root)` returns non-directory entries from the metadata directory, matching AUFS `layers/<id>` files. `getParentIDs(root, id)` reads non-empty lines from `layers/<id>`. `getMountpoint`, `mntPath`, `getDiffPath`, and `diffPath` build canonical paths from `Driver.rootPath`.

## Control Flow
Status calls `loadIds` to count layer metadata. Create/Get/Changes call `getParentIDs` to recover parent order. Path helpers are used by create, remove, mount, diff, and disk-usage methods.

## State And Persistence
The file reads persistent `layers/<id>` files but does not mutate state. Parent ordering is significant: the first line is the direct parent and following lines are older ancestors.

## Dependencies And Integration Points
It uses `os.ReadDir`, `os.Open`, `bufio.Scanner`, and `path.Join`. It is tightly coupled to the storage layout described in `aufs.go`.

## Risks
Malformed or missing `layers/<id>` files propagate errors or produce incorrect parent stacks. `loadIds` intentionally returns file names, not directories; changing that would break status counts.

## Test Signals
AUFS tests indirectly exercise these helpers via status counts, parent-aware mounts, invalid-parent create failures, and deep-layer construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/dirs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/mount.go -->
# sources/cloud-native/containers-storage/drivers/aufs/mount.go

## Purpose
`mount.go` provides AUFS unmount cleanup. It flushes AUFS state with `auplink` before invoking the kernel unmount syscall.

## Important APIs, Types, And Functions
`Unmount(target string) error` runs `auplink <target> flush`, logs a warning if that command fails, then calls `unix.Unmount(target, 0)`.

## Control Flow
`Driver.unmount`, `Remove`, `Cleanup`, and error cleanup in `aufsMount` all funnel through this helper. `auplink` failure is non-fatal because the actual unmount remains authoritative.

## State And Persistence
It does not persist Go state. It affects kernel mount state and may flush AUFS branch metadata before unmounting.

## Dependencies And Integration Points
It depends on `os/exec`, `logrus`, and `x/sys/unix`. It assumes `auplink` may be available on AUFS systems.

## Risks
If `auplink` is missing or fails, stale AUFS state may be harder to diagnose, though unmount can still succeed. Busy mountpoints surface as syscall errors to callers that implement retry or logging.

## Test Signals
AUFS mount/unmount tests and cleanup tests exercise this helper indirectly. Real coverage requires a kernel with AUFS and mount privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/mount_linux.go -->
# sources/cloud-native/containers-storage/drivers/aufs/mount_linux.go

## Purpose
`mount_linux.go` is the Linux syscall shim used by the AUFS driver to create and remount AUFS unions.

## Important APIs, Types, And Functions
`mount(source, target, fstype string, flags uintptr, data string) error` calls `unix.Mount` with the same arguments.

## Control Flow
`aufsMount` uses this helper for the initial AUFS mount and any remount append operations when readonly branches exceed the page-sized mount option buffer.

## State And Persistence
It mutates kernel mount state only. No persistent files or package state are created here.

## Dependencies And Integration Points
The helper depends solely on `golang.org/x/sys/unix` and is package-private for AUFS code.

## Risks
The thin wrapper carries syscall semantics directly to callers. Error interpretation, option construction, and cleanup all occur in `aufs.go`.

## Test Signals
Indirectly covered by AUFS mount tests, including deep layer mount-data splitting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/aufs/mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/btrfs.go -->
# sources/cloud-native/containers-storage/drivers/btrfs/btrfs.go

## Purpose
`btrfs.go` implements the Linux cgo Btrfs graphdriver. It registers `btrfs`, validates that the graph root is on Btrfs, manages layers as Btrfs subvolumes/snapshots, supports optional qgroup quota limits, and returns a `NaiveDiffDriver` wrapper for diff behavior.

## Important APIs, Types, And Functions
`btrfsOptions` tracks `minSpace` and per-layer `size`; `Driver` stores `home`, options, quota status, and a `sync.Once`. `Init`, `parseOptions`, `Create`, `CreateReadWrite`, `CreateFromTemplate`, `Remove`, `Get`, `Put`, `ReadWriteDiskUsage`, `Exists`, `ListLayers`, and `Cleanup` implement the graphdriver lifecycle. Low-level helpers wrap Btrfs ioctls: `subvolCreate`, `subvolSnapshot`, `subvolDelete`, `subvolLimitQgroup`, `qgroupStatus`, `subvolLookupQgroup`, and quota rescan/enabling methods.

## Control Flow
Initialization checks `GetFSMagic(home) == FsMagicBtrfs`, creates `subvolumes`, makes the graph root private, parses driver options, and enables quotas when requested. `Create` creates a new subvolume for base layers or snapshots the parent subvolume, then applies optional `size` storage options and SELinux relabeling. `Get` validates the subvolume and re-applies stored quota files when present. `Remove` deletes a quota sidecar, recursively destroys nested subvolumes, falls back to filesystem cleanup when quotas are disabled, and rescans quotas.

## State And Persistence
Layer data persists as Btrfs subvolumes under `subvolumes/<id>`. Per-layer quota values are stored in text files under `quotas/<id>`. The quota-enabled flag is cached after first status check, but persisted quota state lives in the filesystem qgroup tree. No runtime mounts are created per layer, so `Put` is a no-op.

## Dependencies And Integration Points
The file depends on cgo headers from btrfs-progs, Btrfs ioctl constants, `x/sys/unix`, graphdriver interfaces, `directory`, `fileutils`, `idtools`, `mount`, `parsers`, `system`, Docker units parsing, SELinux labels, and `NaiveLayerIDMapUpdater`.

## Risks
Btrfs behavior is kernel, filesystem, qgroup, and cgo-header dependent. Recursive subvolume deletion must correctly handle children disappearing during walks. Quota deletion logs errors but proceeds in some cases; quota rescan and qgroup lookup failures can affect cleanup. Unsupported mount options and invalid storage options fail early. `CreateFromTemplate` delegates to `Create(id, template, opts)`, so template semantics depend on snapshotting the template layer.

## Test Signals
`btrfs_test.go` runs shared graphdriver contract tests and validates nested subvolume removal. Version tests validate btrfs library version exposure. Full coverage requires Linux, cgo, btrfs headers, Btrfs backing filesystem, and sufficient privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/btrfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/btrfs_test.go -->
# sources/cloud-native/containers-storage/drivers/btrfs/btrfs_test.go

## Purpose
`btrfs_test.go` validates Btrfs graphdriver integration through the shared `graphtest` suite and one Btrfs-specific nested subvolume deletion test.

## Important APIs, Types, And Functions
Tests include `TestBtrfsSetup`, `TestBtrfsCreateEmpty`, `TestBtrfsCreateBase`, `TestBtrfsCreateSnap`, `TestBtrfsCreateFromTemplate`, `TestBtrfsSubvolDelete`, `TestBtrfsEcho`, `TestBtrfsListLayers`, and `TestBtrfsTeardown`.

## Control Flow
The setup test creates a shared Btrfs driver with no cleanup so later tests can reuse it. Shared tests exercise create, snapshot, template, echo/diff, and list behavior. `TestBtrfsSubvolDelete` creates a layer, creates a nested Btrfs subvolume inside it, removes the layer, and asserts the nested subvolume path is gone.

## State And Persistence
Temporary graph roots are managed by `graphtest`. The nested subvolume test creates real Btrfs subvolume state inside a layer and expects `Remove` to recursively destroy it.

## Dependencies And Integration Points
The file depends on `graphdriver`, `graphtest`, Btrfs driver internals, and Linux+cgo build tags.

## Risks
Tests skip or fail depending on Btrfs support, cgo headers, filesystem type, and privileges. The shared driver pattern means setup/teardown ordering matters.

## Test Signals
Strong signal for recursive subvolume cleanup and baseline graphdriver contract behavior. Quota-specific paths are not directly covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/btrfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/dummy_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/btrfs/dummy_unsupported.go

## Purpose
`dummy_unsupported.go` keeps the `btrfs` package buildable on non-Linux or non-cgo targets where the real Btrfs driver is excluded.

## Important APIs, Types, And Functions
The file contains only the package declaration under the `!linux || !cgo` build constraint.

## Control Flow
There is no runtime control flow. Build tags select this file when `btrfs.go` and version files are unavailable.

## State And Persistence
No state is defined or persisted.

## Dependencies And Integration Points
It integrates at the package/build level only, allowing imports of `drivers/btrfs` to compile on unsupported platforms.

## Risks
No driver registration occurs on unsupported platforms, so callers must handle driver unavailability through graphdriver selection errors.

## Test Signals
Build-only signal on unsupported platforms; no unit tests are attached.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/dummy_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/version.go -->
# sources/cloud-native/containers-storage/drivers/btrfs/version.go

## Purpose
`version.go` exposes Btrfs build and library version information from btrfs-progs headers for driver status output.

## Important APIs, Types, And Functions
The cgo preamble includes `btrfs/version.h` and defines fallback `BTRFS_LIB_VERSION` and `BTRFS_BUILD_VERSION` values when headers omit them. `btrfsBuildVersion()` returns the build version string; `btrfsLibVersion()` returns the integer library version.

## Control Flow
`Driver.Status` calls these helpers and includes non-placeholder values in the diagnostic status list.

## State And Persistence
The values are compile-time constants from headers. No persistent or mutable runtime state exists.

## Dependencies And Integration Points
The file requires Linux+cgo and Btrfs development headers. It feeds the graphdriver status API.

## Risks
Header compatibility varies by btrfs-progs version, hence the fallback macros. Incorrect header values would affect diagnostics but not layer data directly.

## Test Signals
`version_test.go` asserts the library version is positive on supported builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/version_test.go -->
# sources/cloud-native/containers-storage/drivers/btrfs/version_test.go

## Purpose
`version_test.go` checks that the Btrfs library version binding returns a meaningful positive value.

## Important APIs, Types, And Functions
`TestLibVersion` calls `btrfsLibVersion()` and reports an error when it is less than or equal to zero.

## Control Flow
The test runs only on Linux+cgo builds and validates the cgo header path at test time.

## State And Persistence
No persistent state is touched.

## Dependencies And Integration Points
It depends on the version helper in `version.go` and Btrfs headers.

## Risks
Older or unusual btrfs-progs headers that define no library version may make this test fail through the fallback `-1`.

## Test Signals
This is a narrow build-environment signal rather than a graphdriver behavior test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/btrfs/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown.go -->
# sources/cloud-native/containers-storage/drivers/chown.go

## Purpose
`chown.go` implements ID-map based ownership rewriting for layer trees. It registers a reexec helper that chroots/chdirs into a layer and walks it, translating UIDs/GIDs from an old mapping to a new one.

## Important APIs, Types, And Functions
`chownByMapsCmd` names the reexec command. `chownByMapsMain` decodes four ID-map slices from stdin, enters the target root, builds `IDMappings`, and parallel-walks the tree with a platform `LChown` implementation. `ChownPathByMaps` marshals mapping data and invokes the reexec command. `naiveLayerIDMapUpdater` implements `LayerIDMapUpdater` with `UpdateLayerIDMap` and `SupportsShifting`.

## Control Flow
Callers invoke `UpdateLayerIDMap`, which mounts/gets the layer, defers `Put`, and calls `ChownPathByMaps`. The child process reads JSON config, enters the layer root, skips `"."`, and calls platform-specific `LChown` on each entry. Errors propagate through combined process output.

## State And Persistence
The persistent effect is changed file ownership, restored mode bits, and restored security capability xattrs inside the target layer tree. No metadata sidecar is written.

## Dependencies And Integration Points
It depends on `idtools`, `reexec`, `pwalkdir`, package-local `json`, `chrootOrChdir`, and platform `newLChowner`. `NaiveDiffDriver` and drivers without native shifting use `NewNaiveLayerIDMapUpdater`.

## Risks
Running in a reexec/chroot path protects against path traversal but depends on platform chroot behavior. Mapping failures are tolerated only for zero IDs in the old map. Hardlink preservation is delegated to platform code. Combined output error wrapping can expose stderr text as part of errors.

## Test Signals
No direct test in this subset. Indirect coverage comes from drivers using naïve ID-map updating and any tests that exercise user namespace or mapping transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_darwin.go -->
# sources/cloud-native/containers-storage/drivers/chown_darwin.go

## Purpose
`chown_darwin.go` provides the Darwin implementation of platform-specific `LChown` for ID-map rewriting.

## Important APIs, Types, And Functions
It defines `inode`, `platformChowner`, `newLChowner`, and `(*platformChowner).LChown`. The chowner tracks visited device/inode pairs to avoid processing hardlinked files repeatedly.

## Control Flow
`LChown` extracts `syscall.Stat_t`, skips already-seen inodes, maps UID/GID from host to container and back to host, reads `security.capability` when present, calls `system.Lchown`, restores setuid/setgid mode bits, and restores the capability xattr.

## State And Persistence
The in-memory `inodes` map deduplicates processing during one walk. Persistent changes are file ownership, mode restoration, and xattr restoration.

## Dependencies And Integration Points
It integrates with `chown.go` through `newLChowner`. Dependencies include `idtools`, `system`, `os`, `syscall`, and `sync`.

## Risks
Darwin has no Linux-style hardlink copy-up issue here, so repeated hardlinks are skipped rather than relinked. Capability xattr handling is best-effort for unsupported platforms. Mapping failures for nonzero IDs abort the walk.

## Test Signals
No direct Darwin test in this subset; behavior is exercised only when ID-map updates run on Darwin builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_unix.go -->
# sources/cloud-native/containers-storage/drivers/chown_unix.go

## Purpose
`chown_unix.go` provides the non-Windows, non-Darwin `LChown` implementation for ID-map rewriting, with special hardlink preservation for filesystems that break inodes during copy-up.

## Important APIs, Types, And Functions
It defines `inode`, `platformChowner`, `newLChowner`, and `(*platformChowner).LChown`. The chowner maps a device/inode pair to the first path seen, not just a boolean.

## Control Flow
For each entry, the code records the first path for an inode. If a later hardlink to the same inode is found, it removes the new path and links it to the first path instead of chowning again. For first occurrences, it maps UID/GID through `toContainer` and `toHost`, preserves `security.capability`, applies `Lchown`, restores setuid/setgid bits, and restores capabilities.

## State And Persistence
In-memory state tracks inode-to-path mappings during a walk. Persistent effects include ownership changes, hardlink topology preservation, mode restoration, and capability xattr restoration.

## Dependencies And Integration Points
It depends on `idtools`, `system`, `os`, `syscall`, and `sync`. It is selected for Linux, FreeBSD, Solaris-like non-Darwin Unix builds and is used by the reexec chown walker.

## Risks
The locking around hardlinks avoids races while relinking/chowning, but path removal and relink can fail if files change concurrently. Capability xattr errors other than unsupported/overflow are fatal. Zero-ID fallback behavior can mask parent layers that were not mapped as expected.

## Test Signals
No direct test in this subset. The hardlink preservation logic is a critical indirect dependency for overlay and other copy-up filesystems during ID-map updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_windows.go -->
# sources/cloud-native/containers-storage/drivers/chown_windows.go

## Purpose
`chown_windows.go` provides a Windows stub for platform `LChown`.

## Important APIs, Types, And Functions
It defines empty `platformChowner`, `newLChowner`, and `LChown`, which returns an `os.PathError` wrapping `syscall.EWINDOWS`.

## Control Flow
Any attempted ID-map chown on Windows fails immediately for the path being processed.

## State And Persistence
No state is mutated and no filesystem ownership changes occur.

## Dependencies And Integration Points
It satisfies the shared chown API on Windows builds.

## Risks
Callers must not assume ID-map shifting works on Windows. The error is explicit and should propagate to higher-level storage operations.

## Test Signals
Build coverage only in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chown_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chroot_unix.go -->
# sources/cloud-native/containers-storage/drivers/chroot_unix.go

## Purpose
`chroot_unix.go` enters a filesystem root for reexec helper operations on non-Windows platforms.

## Important APIs, Types, And Functions
`chrootOrChdir(path string) error` calls `syscall.Chroot(path)` and then `syscall.Chdir("/")`.

## Control Flow
`chownByMapsMain` calls this before walking the layer so all subsequent paths are relative to the target root.

## State And Persistence
It changes process-local root and current working directory in the reexec child. It does not persist files.

## Dependencies And Integration Points
It depends on `os`, `syscall`, and `fmt`, and is part of the chown reexec flow.

## Risks
The function requires privileges/capabilities for `chroot`. Failure aborts the reexec helper. Once chrooted, error paths should avoid assuming access to the original filesystem.

## Test Signals
Indirectly covered by any ID-map chown tests on Unix platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chroot_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chroot_windows.go -->
# sources/cloud-native/containers-storage/drivers/chroot_windows.go

## Purpose
`chroot_windows.go` provides the Windows implementation of `chrootOrChdir`, where true chroot is unavailable.

## Important APIs, Types, And Functions
`chrootOrChdir(path string) error` calls `syscall.Chdir(path)` and wraps errors with context.

## Control Flow
Windows reexec helpers can only change the working directory, not the process root.

## State And Persistence
It changes only process-local current working directory.

## Dependencies And Integration Points
It satisfies the shared chown helper API for Windows builds.

## Risks
Because it cannot isolate paths with chroot semantics, callers must avoid treating this as a security boundary. In practice Windows chown support is also stubbed.

## Test Signals
Build coverage only in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/chroot_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_linux.go -->
# sources/cloud-native/containers-storage/drivers/copy/copy_linux.go

## Purpose
`copy_linux.go` implements Linux/cgo directory and regular-file copy helpers for storage drivers. It preserves metadata, hardlinks, selected xattrs, special files, and directory mtimes, while trying accelerated data copy paths first.

## Important APIs, Types, And Functions
`Mode` selects `Content` or `Hardlink`. `CopyRegularToFile` tries `FICLONE`, then `copy_file_range`, then buffered copy. `CopyRegular` opens a destination exclusively and delegates. `DirCopy` walks a source tree and recreates entries. Helpers include `doCopyWithFileRange`, `legacyCopy`, `copyXattr`, `doCopyXattrs`, `fileID`, and `dirMtimeInfo`.

## Control Flow
`DirCopy` walks source paths, rebases each path to the destination, handles regular files, directories, symlinks, FIFOs, sockets, and devices, then applies ownership, xattrs, mode, and times. It records already-copied regular-file inode IDs so content-copy mode still preserves hardlink relationships. Directory mtimes are delayed until after children are copied.

## State And Persistence
The destination tree is fully materialized on disk. Runtime state tracks copied inode IDs and delayed directory timestamp updates. The `copyWithFileRange` and `copyWithFileClone` booleans are mutated to disable unsupported acceleration after errors.

## Dependencies And Integration Points
It depends on Linux syscalls, cgo `FICLONE`, `idtools`, `system`, `unshare`, and storage buffer pools. Overlay and other drivers can use it for layer copying.

## Risks
Accelerated copy fallback is subtle: `EXDEV`, `ENOSYS`, and ioctl failures adjust future behavior. Rootless mode silently skips device creation. Xattr copying is selective and rootless cannot copy `trusted.overlay.opaque`. `copy_file_range` loops until file size bytes are copied and assumes progress from the syscall.

## Test Signals
`copy_test.go` covers regular copies with and without acceleration flags, recursive metadata-preserving directory copy, and hardlink preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_test.go -->
# sources/cloud-native/containers-storage/drivers/copy/copy_test.go

## Purpose
`copy_test.go` validates Linux copy helper behavior for regular-file content, recursive directory metadata, and hardlink preservation.

## Important APIs, Types, And Functions
Tests include `TestCopy`, `TestCopyWithoutRange`, `TestCopyDir`, and `TestCopyHardlink`. Helpers include `randomMode`, `populateSrcDir`, and `doCopyTest`.

## Control Flow
Regular-file tests create deterministic random data and compare destination bytes. Directory tests generate a nested tree with random modes, mtimes, files, directories, and a socket, then walk source and destination to compare mode, ownership, and mtime metadata. Hardlink tests create two source names for the same inode and assert the copied destination names also share an inode.

## State And Persistence
All state is test temporary filesystem content. Tests intentionally create Unix sockets and hardlinks to validate special handling.

## Dependencies And Integration Points
The suite depends on `system.Chtimes`, `x/sys/unix`, `gotest.tools` assertions, and Linux build tags.

## Risks
Tests are filesystem-sensitive: inode equality, ctime comments, ownership, and special files can vary by platform or permissions. They do not directly verify xattr copying.

## Test Signals
Strong signal for content correctness, metadata preservation, and hardlink topology, but limited signal for reflink/copy_file_range paths because fallback behavior depends on kernel/filesystem support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/copy/copy_unsupported.go

## Purpose
`copy_unsupported.go` provides fallback copy helpers for non-Linux or non-cgo builds.

## Important APIs, Types, And Functions
It defines `Mode` with only `Content`, `DirCopy`, `CopyRegularToFile`, and `CopyRegular`. `DirCopy` and `CopyRegular` use `chrootarchive.NewArchiver(nil).CopyWithTar`; `CopyRegularToFile` uses `io.Copy`.

## Control Flow
Fallback paths avoid Linux-specific syscalls and metadata logic by relying on tar-based copy where possible.

## State And Persistence
The destination tree/file is created by tar extraction or stream copy. No acceleration flags are used despite parameters being present for API compatibility.

## Dependencies And Integration Points
It preserves the public package API for unsupported platforms and depends on `chrootarchive`, `io`, and `os`.

## Risks
Behavior differs from Linux: no `Hardlink` mode constant, no explicit xattr selection logic, and `CopyRegular` uses tar copy semantics. Callers with Linux-specific metadata expectations must be build-tag aware.

## Test Signals
Build-only in this subset; Linux tests do not run against this implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/copy/copy_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/counter.go -->
# sources/cloud-native/containers-storage/drivers/counter.go

## Purpose
`counter.go` implements `RefCounter`, a concurrency-safe mount reference counter for graphdriver `Get`/`Put` flows.

## Important APIs, Types, And Functions
`minfo` stores whether a path has been checked and the current count. `RefCounter` stores counts, a mutex, and a `Checker`. `NewRefCounter`, `Increment`, `Decrement`, and `incdec` provide the public behavior.

## Control Flow
On first use of a path, `incdec` asks the checker whether it is already mounted and seeds the count accordingly. On later operations, if the checker reports the path is no longer mounted, the count is reset to zero before applying the increment/decrement. Entries are deleted when count drops to zero or below.

## State And Persistence
State is in-memory only and keyed by mount path. It is intentionally reconciled with external mount state because another process can unmount a path.

## Dependencies And Integration Points
AUFS and similar mount-backed drivers use it to prevent duplicate mounts and premature unmounts. It depends on the `Checker` abstraction implemented by platform driver files.

## Risks
Correctness depends on the checker accurately reporting mounted state. A decrement for an unknown path can produce a negative intermediate count before entry deletion. External unmounts reset the count, which is defensive but can surprise callers that still hold references.

## Test Signals
AUFS concurrent benchmark and mount tests indirectly exercise refcount behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver.go -->
# sources/cloud-native/containers-storage/drivers/driver.go

## Purpose
`driver.go` defines the graphdriver interfaces, option types, registration and selection logic, errors, and shared helper contracts used by all storage drivers.

## Important APIs, Types, And Functions
Key types include `FsMagic`, `CreateOpts`, `MountOpts`, `ApplyDiffOpts`, `ApplyDiffWithDifferOpts`, `DedupArgs`, `DedupResult`, `InitFunc`, `ProtoDriver`, `DiffDriver`, `LayerIDMapUpdater`, `Driver`, `DriverWithDifferOutput`, `Differ`, `DriverWithDiffer`, `Capabilities`, `AdditionalLayer`, `AdditionalLayerStoreDriver`, `DiffGetterDriver`, `FileGetCloser`, `Checker`, and `Options`. Key functions include `MustRegister`, `Register`, `GetDriver`, `New`, `ScanPriorDrivers`, `isDriverNotSupported`, and `driverPut`.

## Control Flow
Drivers register in package init functions. `New` uses an explicit driver name when provided, otherwise scans prior driver directories, applies priority ordering, refuses ambiguous prior state, then probes priority and registered drivers until one succeeds or all are unsupported. `driverPut` is a defer helper that merges `Put` errors into an existing return error or logs secondary failures.

## State And Persistence
The global `drivers` map is in-memory registration state. Persistent detection is directory-based through `ScanPriorDrivers(config.Root)`. Options carry root/runroot/image store paths, driver priorities, and driver options into initialization.

## Dependencies And Integration Points
Every driver package depends on these contracts. The file integrates with dedup options, tempdir cleanup, archive diffs, directory usage, idtools, digest metadata, tar-split file getters, fileutils, and logrus.

## Risks
Driver selection protects existing storage by erroring when prior driver state exists but no longer initializes; changing this can make images appear missing. Interface changes have broad blast radius. `DriverWithDiffer` and additional layer APIs are experimental but still used by overlay/composefs flows.

## Test Signals
Concrete driver tests and `graphtest` exercise the contracts. There is no direct registration/selection unit test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_darwin.go -->
# sources/cloud-native/containers-storage/drivers/driver_darwin.go

## Purpose
`driver_darwin.go` provides Darwin-specific driver priority and filesystem magic behavior.

## Important APIs, Types, And Functions
`Priority` contains only `vfs`. `GetFSMagic` returns `FsMagicUnsupported` with no error.

## Control Flow
On Darwin, automatic graphdriver selection will prefer VFS and filesystem-specific drivers cannot rely on actual statfs magic from this file.

## State And Persistence
No mutable state is maintained.

## Dependencies And Integration Points
It satisfies platform symbols required by `driver.go`.

## Risks
Filesystem compatibility checks are effectively disabled except by individual drivers. Darwin storage behavior is therefore expected to use VFS.

## Test Signals
Build-only in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_freebsd.go -->
# sources/cloud-native/containers-storage/drivers/driver_freebsd.go

## Purpose
`driver_freebsd.go` provides FreeBSD graphdriver priority and mount/filesystem checking helpers.

## Important APIs, Types, And Functions
It defines `FsMagicZfs`, `Priority` as `zfs` then `vfs`, `FsNames`, `NewDefaultChecker`, `defaultChecker.IsMounted`, and `Mounted`.

## Control Flow
FreeBSD selection prefers ZFS. `Mounted` calls `unix.Statfs` on a path and compares the reported filesystem type with the requested `FsMagic`.

## State And Persistence
No persistent or mutable package state beyond static maps/slices.

## Dependencies And Integration Points
It integrates with `RefCounter` through `Checker`, with mount parsing through `pkg/mount`, and with platform graphdriver selection.

## Risks
Unlike Linux, `Mounted` does not separately verify mountpoint boundary by parent device; it only compares filesystem type. This can be less precise for nested paths.

## Test Signals
FreeBSD-specific build and driver tests would exercise it; none are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_linux.go -->
# sources/cloud-native/containers-storage/drivers/driver_linux.go

## Purpose
`driver_linux.go` defines Linux filesystem magic constants, filesystem names, default driver priority, and mount checking helpers.

## Important APIs, Types, And Functions
It defines many `FsMagic*` constants, `Priority` (`overlay`, `aufs`, `btrfs`, `zfs`, `vfs`), `FsNames`, `GetFSMagic`, `NewFsChecker`, `fsChecker.IsMounted`, `NewDefaultChecker`, `defaultChecker.IsMounted`, `isMountPoint`, and `Mounted`.

## Control Flow
`GetFSMagic` performs `unix.Statfs` on the parent directory of the requested root path and logs unknown types. `Mounted` checks statfs type at the mount path and then confirms mountpoint status by comparing device IDs against the parent directory. The checker wrappers make this usable by `RefCounter`.

## State And Persistence
Static constants/maps define platform behavior. No mutable state is persisted.

## Dependencies And Integration Points
AUFS, Btrfs, overlay, and driver selection use these constants and helpers. It depends on `pkg/mount`, `x/sys/unix`, `filepath`, and logrus.

## Risks
`GetFSMagic` uses `filepath.Dir(rootpath)`, so callers must pass roots whose parent exists. `isMountPoint` returns true alongside stat errors, leaving the error for callers to interpret. Accurate mount detection is critical for refcounting and cleanup.

## Test Signals
Concrete driver initialization and mount tests indirectly validate these helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_solaris.go -->
# sources/cloud-native/containers-storage/drivers/driver_solaris.go

## Purpose
`driver_solaris.go` supplies Solaris+cgo graphdriver priority and ZFS mount detection.

## Important APIs, Types, And Functions
It defines `FsMagicZfs`, `Priority` as `zfs`, `FsNames`, `GetFSMagic`, `NewFsChecker`, `NewDefaultChecker`, `Mounted`, and checker structs. The cgo helper calls `statvfs`.

## Control Flow
`Mounted` calls `statvfs` on the mount path's directory and inspects `f_basetype` bytes for `"zfs"`. Non-ZFS results return `ErrPrerequisites`; ZFS returns mounted success.

## State And Persistence
Only static priority/name data exists.

## Dependencies And Integration Points
It supports graphdriver selection and refcount checking on Solaris. Dependencies include cgo, `pkg/mount`, `filepath`, `unsafe`, and logrus.

## Risks
`GetFSMagic` currently returns zero/nil, so filesystem detection is minimal. The cgo allocation helper ignores statvfs error detail and relies on `f_basetype` inspection.

## Test Signals
Solaris build/runtime tests would be needed; none are present in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/driver_unsupported.go

## Purpose
`driver_unsupported.go` provides fallback driver priority and filesystem magic behavior for platforms not covered by Linux, FreeBSD, Solaris, or Darwin.

## Important APIs, Types, And Functions
`Priority` contains `unsupported`. `GetFSMagic` returns `FsMagicUnsupported`.

## Control Flow
Automatic selection will try the unsupported driver name, and platform-specific filesystem checks are unavailable.

## State And Persistence
No mutable state is kept.

## Dependencies And Integration Points
It satisfies symbols needed by `driver.go` on miscellaneous platforms.

## Risks
Only drivers registered for such platforms can work; most storage backends will report unsupported.

## Test Signals
Build-only signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/driver_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/fsdiff.go -->
# sources/cloud-native/containers-storage/drivers/fsdiff.go

## Purpose
`fsdiff.go` implements `NaiveDiffDriver`, a generic diff/apply/changes wrapper for `ProtoDriver` implementations that do not provide native diffing.

## Important APIs, Types, And Functions
`ApplyUncompressedLayer` is the injectable unpack function. `NaiveDiffDriver` embeds `ProtoDriver` and `LayerIDMapUpdater`. `NewNaiveDiffDriver` returns a complete `Driver`. Methods implement `Diff`, `Changes`, `ApplyDiff`, and `DiffSize`.

## Control Flow
`Diff` mounts the layer read-only, and for non-base layers also mounts the parent read-only, computes changes with `archive.ChangesDirs`, and exports changes. Base layers are tarred directly. Close wrappers call `driverPut`, and `Diff` sleeps until the next second to avoid mtime precision races. `ApplyDiff` gets the target layer, builds tar options with user namespace and mapping behavior, and calls `ApplyUncompressedLayer`. `DiffSize` computes changes and sums their sizes.

## State And Persistence
The wrapper does not persist its own state. It mounts/releases underlying driver layers and applies tar data into the target layer filesystem.

## Dependencies And Integration Points
It integrates with every driver that wraps a `ProtoDriver`, including Btrfs. Dependencies include `archive`, `chrootarchive`, `idtools`, `ioutils`, `unshare`, runtime OS checks, and logrus.

## Risks
Naïve diffing is slower and depends on mounted filesystem views. Mtime granularity is explicitly handled with a sleep. Forgetting to close returned diff readers can leak `Get` references. Parent mapping defaults must be correct for ID-mapped layer comparisons.

## Test Signals
`graphtest` diff/apply/changes tests exercise this path for drivers that use the wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/fsdiff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphbench_unix.go -->
# sources/cloud-native/containers-storage/drivers/graphtest/graphbench_unix.go

## Purpose
`graphbench_unix.go` provides reusable benchmark helpers for graphdriver implementations on Unix-like systems.

## Important APIs, Types, And Functions
Benchmarks include `DriverBenchExists`, `DriverBenchGetEmpty`, `DriverBenchDiffBase`, `DriverBenchDiffN`, `DriverBenchDiffApplyN`, `DriverBenchDeepLayerDiff`, and `DriverBenchDeepLayerRead`.

## Control Flow
Each benchmark obtains a driver, creates base/upper/deep layers, populates files through testutil helpers, resets the timer, and loops on the operation being measured. Some benchmarks stop the timer for setup/validation inside each iteration.

## State And Persistence
Temporary layer state is created under `graphtest` driver roots. Benchmarks read, write, diff, and apply actual layer filesystem content.

## Dependencies And Integration Points
It depends on `graphdriver`, `stringid`, `testing`, and graphtest helpers such as `addManyFiles`, `checkManyFiles`, and `addManyLayers`.

## Risks
`DriverBenchDiffApplyN` must feed the produced diff reader into `ApplyDiff`; missing or incorrect diff wiring would make benchmark validation fail. Results are highly dependent on backing filesystem and driver behavior.

## Test Signals
Benchmarks serve as performance signals for existence checks, mount/get cost, diff cost, diff/apply cost, and deep-layer read/diff behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphbench_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphtest_unix.go -->
# sources/cloud-native/containers-storage/drivers/graphtest/graphtest_unix.go

## Purpose
`graphtest_unix.go` is the shared graphdriver behavioral test suite for Unix-like platforms. It standardizes setup, cleanup, and tests that concrete drivers call from their own test files.

## Important APIs, Types, And Functions
`Driver` wraps `graphdriver.Driver` with root/runRoot/refCount. Setup helpers include `newGraphDriver`, `newDriver`, `GetDriverNoCleanup`, `GetDriver`, `ReconfigureDriver`, and `PutDriver`. Contract tests include create-empty/base/snapshot/template, deep layer read, diff/apply, changes, quota, echo, and list layers.

## Control Flow
Driver setup creates temporary roots and skips unsupported/prerequisite/permission failures. Tests create layers, mutate files, call driver methods, compare archive changes, validate file metadata, and register cleanup removals. `GetDriverNoCleanup` allows suites to reuse an expensive driver across multiple tests until `PutDriver` decrements the refcount to zero.

## State And Persistence
State lives in temporary root and runRoot directories. A package-global `drv` caches a shared driver and its refcount. Layer contents and driver metadata are real filesystem artifacts removed during cleanup.

## Dependencies And Integration Points
Concrete driver tests for AUFS, Btrfs, overlay, and others import these helpers. Dependencies include `graphdriver`, `archive`, `stringid`, `go-units`, `testify`, and Unix syscalls.

## Risks
The global driver makes test ordering/refcount discipline important. Tests are integration-heavy and can skip due to environment. Quota tests expect write failures with `EDQUOT`, which depends on backend quota enforcement.

## Test Signals
This file is the main cross-driver signal for graphdriver correctness: create/snapshot inheritance, template identity, diff/apply round trips, deletion whiteouts, metadata preservation, deep layer visibility, quota behavior, echo edge cases, and exact layer listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphtest_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphtest_windows.go -->
# sources/cloud-native/containers-storage/drivers/graphtest/graphtest_windows.go

## Purpose
`graphtest_windows.go` is an empty Windows package stub for `graphtest`.

## Important APIs, Types, And Functions
It declares package `graphtest` and no APIs.

## Control Flow
No runtime behavior exists.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
It keeps the package buildable on Windows when Unix test helpers are excluded.

## Risks
Windows builds receive none of the shared graphtest helpers from Unix files.

## Test Signals
Build-only signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/graphtest_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/testutil.go -->
# sources/cloud-native/containers-storage/drivers/graphtest/testutil.go

## Purpose
`testutil.go` contains reusable filesystem mutation and verification helpers for graphdriver tests and benchmarks.

## Important APIs, Types, And Functions
Helpers include `randomContent`, `addFiles`, `checkFile`, `addFile`, `addDirectory`, `removeAll`, `checkFileRemoved`, `addManyFiles`, `changeManyFiles`, `checkManyFiles`, `addLayerFiles`, `addManyLayers`, `checkManyLayers`, `readDir`, and `removeLayer`.

## Control Flow
Helpers obtain a layer root with `driver.Get`, defer `Put`, then write/read/remove filesystem entries. Multi-file helpers batch files into directories of up to 100 entries. Change helpers produce expected `archive.Change` records alongside actual filesystem mutations.

## State And Persistence
All state is temporary layer content created under active graphdriver roots. `randomContent` is deterministic by seed, allowing later verification.

## Dependencies And Integration Points
The file is used by `graphtest_unix.go` and `graphbench_unix.go`. It depends on `graphdriver`, `archive`, `stringid`, and logrus.

## Risks
Failures in cleanup `Put` calls are logged rather than returned in many helpers, so primary operation errors may hide release failures. `readDir` filters `lost+found`, which is useful for ext filesystems but could hide a real test artifact with that name.

## Test Signals
These helpers generate the file trees used to validate diffs, changes, deep layer reads, and list behavior across drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/testutil_unix.go -->
# sources/cloud-native/containers-storage/drivers/graphtest/testutil_unix.go

## Purpose
`testutil_unix.go` provides Unix-specific metadata helpers for graphdriver tests.

## Important APIs, Types, And Functions
`verifyFile` checks file type, permissions, sticky/setuid/setgid bits, UID, and GID. `createBase` creates a base layer with a subdirectory and file using specific permissions and ownership. `verifyBase` validates that structure.

## Control Flow
`createBase` temporarily sets umask to zero, creates a writable layer, gets its root, creates test entries, applies chown, and puts the layer. `verifyBase` gets the layer and asserts root, subdir, file, and directory listing properties.

## State And Persistence
It writes deterministic base-layer content and metadata used by shared graphdriver tests.

## Dependencies And Integration Points
It depends on Unix stat data, `graphdriver`, `testify`, and `x/sys/unix`. `graphtest_unix.go` relies on these helpers for create/snapshot/template tests.

## Risks
Tests require permission to chown to UID/GID 1/2 or suitable test environment behavior. Umask restoration is important for process-wide test isolation.

## Test Signals
Strong signal for metadata preservation across driver create and snapshot operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/graphtest/testutil_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/jsoniter.go -->
# sources/cloud-native/containers-storage/drivers/jsoniter.go

## Purpose
`jsoniter.go` defines the package-level JSON codec used by graphdriver helpers.

## Important APIs, Types, And Functions
`var json = jsoniter.ConfigCompatibleWithStandardLibrary` exposes a standard-library-compatible JSON API.

## Control Flow
`chown.go` uses this variable to marshal and unmarshal ID-map configuration for the reexec chown helper.

## State And Persistence
No persistent state. The variable is an in-memory codec configuration.

## Dependencies And Integration Points
It depends on `github.com/json-iterator/go` and avoids repeated imports or naming conflicts across graphdriver files.

## Risks
Compatibility with standard library JSON is expected; changing config could affect reexec protocol encoding.

## Test Signals
Indirectly tested by chown reexec flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/jsoniter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/check.go -->
# sources/cloud-native/containers-storage/drivers/overlay/check.go

## Purpose
`overlay/check.go` implements active Linux overlayfs feature probes for native diff safety, metacopy, volatile mounts, idmapped lower layers, and data-only layers.

## Important APIs, Types, And Functions
Functions include `doesSupportNativeDiff`, `doesMetacopy`, `doesVolatile`, `supportsIdmappedLowerLayers`, and `supportsDataOnlyLayers`.

## Control Flow
Each probe creates temporary lower/upper/work/merged directories under the driver home, performs an overlay mount with relevant options, mutates or inspects files, reads overlay xattrs, then unmounts and removes the temporary tree. Native diff detection checks opaque xattr copy-up and redirect-dir behavior. Metacopy detection chmods a lower file and checks for the metacopy xattr. Idmapped support creates a user namespace process and an ID-mapped lower mount before overlay mounting it.

## State And Persistence
Temporary directories and kernel mounts are created and cleaned up. Results are returned to caller; caching is handled elsewhere in overlay driver code.

## Dependencies And Integration Points
The probes feed overlay driver initialization and capability decisions. Dependencies include `archive` overlay xattr helpers, `idmap`, `idtools`, `ioutils`, `mount.ParseOptions`, `system`, `unshare`, `unix`, and logrus.

## Risks
Probes require mount privileges and kernel support; failures may mean unsupported feature or hard error depending on context. Cleanup runs in defers and logs unmount/remove failures. Native diff safety is sensitive to overlay kernel behavior around opaque and redirect xattrs.

## Test Signals
Overlay driver tests indirectly cover cached use of these probes. Direct unit tests are difficult because behavior is kernel-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/check_116.go -->
# sources/cloud-native/containers-storage/drivers/overlay/check_116.go

## Purpose
`check_116.go` scans an overlay storage home for artifacts that indicate prior use of a mount program such as fuse-overlayfs.

## Important APIs, Types, And Functions
`scanForMountProgramIndicators(home string) (detected bool, err error)` walks the tree looking for whiteout-prefixed names or directory xattrs with `user.fuseoverlayfs.` or `user.containers.` prefixes.

## Control Flow
The walk stops early with `fs.SkipDir` once an indicator is detected. Directory xattrs are listed with `system.Llistxattr`; unsupported xattrs are ignored.

## State And Persistence
The function is read-only. It inspects existing file names and xattrs.

## Dependencies And Integration Points
It depends on `archive.WhiteoutPrefix`, `system.Llistxattr`, `filepath.WalkDir`, and build-time Linux support. Overlay initialization can use it for compatibility decisions.

## Risks
Large storage trees can make scans expensive if no indicator is found. Read errors abort the scan. Detection is heuristic and may miss future mount-program markers.

## Test Signals
No direct tests in this subset; behavior is inferred through overlay initialization paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/check_116.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/composefs.go -->
# sources/cloud-native/containers-storage/drivers/overlay/composefs.go

## Purpose
`composefs.go` supports overlay's composefs/EROFS additional-layer path. It generates composefs blobs with `mkcomposefs`, enables fs-verity when possible, opens EROFS filesystem mounts using the new mount API, and moves those mounts to target mountpoints.

## Important APIs, Types, And Functions
State includes cached `mkcomposefs` lookup fields and `skipMountViaFile`. Functions include `getComposeFsHelper`, `getComposefsBlob`, `generateComposeFsBlob`, `hasACL`, `openBlobFile`, `openComposefsMount`, and `mountComposefsBlob`.

## Control Flow
`generateComposeFsBlob` creates a composefs data directory, generates JSON dump data from TOC and verity digests, runs `mkcomposefs --from-file - -`, writes `composefs.blob`, reopens it read-only, and attempts fs-verity enablement. `openComposefsMount` reads ACL flags, tries mounting EROFS directly from the file, falls back to a readonly loop device on `ENOTBLK`, and caches that fallback. `mountComposefsBlob` moves the detached mount FD to the target path.

## State And Persistence
Persistent state is `composefs.blob` under the data directory. Runtime state caches helper lookup and whether direct file-backed EROFS mounting should be skipped. Loop devices and mount file descriptors are temporary resources.

## Dependencies And Integration Points
It integrates with overlay additional layer support and chunked composefs artifacts. Dependencies include `dump.GenerateDump`, `fsverity`, `loopback`, `unix` fsopen/fsconfig/fsmount/move_mount APIs, `mkcomposefs`, and logrus.

## Risks
Requires external `mkcomposefs`, kernel EROFS support, and newer mount APIs. Direct file mounting works only on newer kernels, so fallback logic must remain correct. Blob header flag parsing assumes the composefs/EROFS header layout. Failed fs-verity enablement is warning-only for unsupported ioctls.

## Test Signals
No direct tests in this subset. Overlay additional layer and composefs integration tests elsewhere would validate blob generation and mount behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/composefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/jsoniter.go -->
# sources/cloud-native/containers-storage/drivers/overlay/jsoniter.go

## Purpose
`overlay/jsoniter.go` defines the overlay package's standard-compatible JSON codec.

## Important APIs, Types, And Functions
`var json = jsoniter.ConfigCompatibleWithStandardLibrary` is used by overlay reexec and metadata flows.

## Control Flow
`mount.go` uses this codec to encode/decode `mountOptions` across a reexec stdin pipe.

## State And Persistence
No persistent state. The codec configuration is package-level runtime state.

## Dependencies And Integration Points
It depends on `github.com/json-iterator/go` and avoids repeating codec setup across overlay files.

## Risks
The reexec protocol expects standard JSON compatibility. Changing codec behavior could break option transport.

## Test Signals
Indirectly tested by overlay mount reexec paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/jsoniter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/mount.go -->
# sources/cloud-native/containers-storage/drivers/overlay/mount.go

## Purpose
`overlay/mount.go` implements a reexec helper for mounting overlay filesystems from a specific directory, including a workaround for page-size-limited mount option strings.

## Important APIs, Types, And Functions
`mountOptions` carries device, target, type, label/data, and flags. `mountOverlayFrom` starts the `storage-mountfrom` reexec command and sends options as JSON. `mountOverlayFromMain` is the reexec entrypoint. `fatal` writes an error and exits.

## Control Flow
The parent process encodes mount options to the child. The child locks its OS thread, parses flags, decodes options, `chdir`s to the home directory, and tries a direct `unix.Mount` if the mount data fits in one page. If too large, it parses `upperdir`, `workdir`, `lowerdir`, `label`, and other options, converts relative upper/work/target paths to absolute paths, opens each lower directory, replaces lower paths with shorter `/proc/self/fd` descriptors, reconstructs the data string, changes to `/proc/self/fd`, and retries the mount.

## State And Persistence
The reexec child mutates process working directory and creates a kernel overlay mount at the target. Open lower directory file descriptors live only for the child process during mount setup.

## Dependencies And Integration Points
Overlay driver mount code calls `mountOverlayFrom` when long lowerdir lists or relative paths need controlled mounting. It depends on `reexec`, package `json`, `x/sys/unix`, and runtime thread locking.

## Risks
Mount data parsing is string-based and must preserve options while shortening lower paths. Data-only lower layers are represented by empty lowerdir components and need special colon handling. If the reconstructed label still exceeds page size, mounting fails with a detailed error. File descriptors are intentionally leaked until process exit to keep `/proc/self/fd` paths valid for the mount syscall.

## Test Signals
Overlay deep-layer and mount tests indirectly validate this path, especially when lowerdir option strings exceed the kernel page-size limit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/mount.go -->
