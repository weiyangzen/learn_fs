<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_freebsd.go -->
# sources/cloud-native/containerd/pkg/archive/link_freebsd.go

Purpose: FreeBSD-specific hard-link implementation that avoids unsupported cross-device or special-case behavior by delegating through containerd sys helpers and Unix flags.

Important APIs and functions: `link(oldname, newname string) error` calls `sys.Link(oldname, newname, unix.AT_SYMLINK_FOLLOW)`.

Control flow and state: stateless wrapper. The important behavior is that symlink-following semantics are explicit through `AT_SYMLINK_FOLLOW`.

Dependencies and integration: integrates `github.com/containerd/containerd/v2/pkg/sys` and `golang.org/x/sys/unix` into the archive apply flow for tar hardlinks.

Risks and test signals: hardlink security is sensitive because tar linknames may attempt to escape extraction roots. Root bounding is handled in `tar.go` before this function is called; platform-specific link following should be validated with FreeBSD CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_freebsd.go -->
