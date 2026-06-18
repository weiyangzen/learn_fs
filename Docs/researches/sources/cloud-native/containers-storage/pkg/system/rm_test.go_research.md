# sources/cloud-native/containers-storage/pkg/system/rm_test.go

Purpose: unit/integration tests for `EnsureRemoveAll`.

Important APIs/types/functions: tests cover non-existent paths, temporary directories, temporary files, and bind-mounted subdirectories.

Control flow: the mount test creates two temp dirs, bind-mounts one into the other, runs `EnsureRemoveAll` in a goroutine, and fails if it does not complete within five seconds.

State/persistence: creates and removes temporary filesystem objects; the mount test performs a real bind mount on non-Windows systems.

Dependencies/integration: depends on `pkg/mount`, `runtime`, and host mount permissions.

Risks: mount test requires privileges/capabilities and skips only Windows; unprivileged Unix test environments may fail during `mount.Mount`. Timeout detects hangs in busy-unmount retry logic.

Test signals: good regression signal for `EBUSY` unmount cleanup and no-error behavior for missing paths.
