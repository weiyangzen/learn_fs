<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_opts.go -->
# sources/cloud-native/moby/client/container_diff_opts.go

Purpose: declares public option and result types for container filesystem diff.

Important APIs/types: empty extensibility struct `ContainerDiffOptions` and `ContainerDiffResult{Changes []container.FilesystemChange}`.

Control flow and dependencies: no runtime flow; depends on the container API type package.

State and risks: no persistence. Compatibility risk is low but public type shape matters for callers and interface signatures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_opts.go -->
