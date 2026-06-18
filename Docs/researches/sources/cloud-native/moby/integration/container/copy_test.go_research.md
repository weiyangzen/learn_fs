# sources/cloud-native/moby/integration/container/copy_test.go

Purpose: Exercises container archive copy APIs for missing paths, non-directory paths, empty archives, UID/GID ownership mapping, symlink copy semantics, and a security regression around xz decompression.

Important APIs and flow: Tests call `CopyFromContainer`, `CopyToContainer`, `ContainerCreate`, `ImageBuild`, and `container.Exec`. `makeTestImage` builds a busybox image with `testuser:testgroup`; `makeEmptyArchive` uses `go-archive` `CopyInfoSourcePath`, `TarResource`, and `PrepareArchiveCopy`. `TestCopyFromContainer` builds a tree with files and symlinks, copies many path forms, and reads the returned tar stream with `archive/tar`. `TestCopyToContainerXZBinaryNotExecutedOnDaemon` launches a separate daemon with a secret env var, injects a fake `/usr/bin/xz` into the container image, uploads invalid xz-magic data, and asserts the container binary was not executed by dockerd.

State and dependencies: Builds temporary images and archives, creates containers, reads tar streams, and can start a child daemon for the security case. Uses platform skips for Windows and snapshotter limitations.

Risks and signals: It covers client/server path validation, archive preparation, root/user ownership propagation, symlink traversal rules, and daemon/container process boundary security. Failures may indicate API error-type drift, archive extraction regressions, or a critical decompressor execution bug.
