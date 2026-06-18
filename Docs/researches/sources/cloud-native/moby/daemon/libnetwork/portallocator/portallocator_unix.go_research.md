<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go

Purpose: non-Windows default dynamic port range constants.

Important APIs/types/functions: defines `defaultPortRangeStart = 49153` and `defaultPortRangeEnd = 65535`.

Control flow: no functions. The shared allocator uses these constants when platform range discovery fails.

State and persistence: no state.

Dependencies and integration points: selected by `//go:build !windows`. Used by `dynamicPortRange` fallback in `portallocator.go` for Linux, FreeBSD, and other Unix-like builds.

Risks and test signals: fallback differs from Windows defaults and should remain aligned with expected Unix/Linux ephemeral ranges. Coverage is indirect through allocator tests and platform build coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go -->
