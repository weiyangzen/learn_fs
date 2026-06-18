# sources/cloud-native/moby/integration/container/overlayfs_linux_test.go

Purpose: Linux overlayfs regression test ensuring container diff/export/copy operations do not produce kernel warnings about undefined overlay behavior.

Important APIs and flow: A container continuously appends to `/file`. For each operation (`ContainerDiff`, `ContainerExport`, `CopyToContainer`, `CopyFromContainer`), the test reads recent kernel logs before and after using `unix.Klogctl`, computes new lines with `diffDmesg`, and fails if overlayfs warning text mentions lowerdir, upperdir, or workdir in-use with undefined behavior.

State and dependencies: Requires local non-rootless Linux daemon and kernel log read permission. It uses a live mutating container and archive generation through `go-archive`.

Risks and signals: It detects daemon operations that mount overlay internals unsafely while a container is active. Failures indicate potential storage-driver correctness or data-integrity risks beyond ordinary API output.
