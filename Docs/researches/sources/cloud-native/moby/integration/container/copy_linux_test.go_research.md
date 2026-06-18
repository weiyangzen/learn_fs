# sources/cloud-native/moby/integration/container/copy_linux_test.go

Purpose: Linux-only regression coverage for `docker cp` when the destination path traverses an absolute in-container symlink that is also part of a bind mount target, matching the `/var/run -> /run` class of layouts.

Important APIs and flow: `TestCopyWithAbsoluteSymlinkedMountTarget` builds a busybox image with `/sockets -> /root`, creates a host file using `testutil.TempDir`, bind-mounts it to `/sockets/docker.sock`, then calls `apiClient.CopyToContainer` with destination `/sockets/` and empty content. It uses `build.Do`, `fakecontext`, `container.Create`, `container.WithMount`, and `mounttypes.Mount`.

State and dependencies: The test creates an image, host temp file, and container metadata; cleanup is handled by test helpers. It depends on Linux behavior, bind mounts, symlink resolution, and daemon archive copy internals.

Risks and signals: It guards the security fix using `os.Root` from regressing into rejecting common absolute symlink paths. Passing signal is no error from `CopyToContainer`; failures indicate broken mount-target resolution for distro-style symlinks.
