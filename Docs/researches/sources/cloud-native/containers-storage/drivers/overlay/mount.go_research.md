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
