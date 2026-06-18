<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_default.go -->
# sources/cloud-native/containerd/pkg/archive/link_default.go

Purpose: default hard-link implementation for all non-FreeBSD builds.

Important APIs and functions: `link(oldname, newname string) error` is a thin wrapper around `os.Link`.

Control flow and state: no persistent state; it delegates directly to the host filesystem and returns the syscall error unchanged.

Dependencies and integration: used by `createTarFile` in `tar.go` when applying tar `TypeLink` entries after resolving the link target with `hardlinkRootPath`.

Risks and test signals: behavior inherits platform `os.Link` semantics. FreeBSD has a separate implementation because containerd needs different link handling there; common hardlink and breakout behavior is covered by `tar_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_default.go -->
