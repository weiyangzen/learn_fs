# sources/cloud-native/containers-storage/pkg/system/rm.go

Purpose: robust recursive removal helper that tries harder than `os.RemoveAll` for storage directories, especially when mounts, races, or immutable flags are involved.

Important APIs/types/functions: `EnsureRemoveAll(dir string) error`.

Control flow: first tries `os.RemoveAll`. On failure it runs `mount.RecursiveUnmount`, then loops up to per-path retry limits. It retries benign missing-child races, treats missing top-level dir as success, resets file flags on `EPERM`, unmounts `EBUSY` paths, sleeps briefly, and eventually returns unrecoverable errors.

State/persistence: removes filesystem trees and may unmount mounts under the target. Tracks transient retry maps in memory.

Dependencies/integration: depends on `pkg/mount`, `logrus`, `syscall`, and platform `resetFileFlags`/`IsEBUSY`. Used by store deletion and garbage cleanup for container/userdata directories.

Risks: aggressive unmount/removal is intentionally destructive for the target tree. Non-`PathError` failures are returned immediately. Race handling for repeated missing paths returns the error after seeing the same child twice. It can loop for about 10 seconds per busy path at the max retry setting.

Test signals: `rm_test.go` covers missing paths, files, directories, and bind mounts. FreeBSD immutable-flag behavior depends on `rm_freebsd.go`.
