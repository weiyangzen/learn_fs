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
