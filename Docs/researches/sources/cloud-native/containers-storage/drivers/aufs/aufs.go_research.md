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
