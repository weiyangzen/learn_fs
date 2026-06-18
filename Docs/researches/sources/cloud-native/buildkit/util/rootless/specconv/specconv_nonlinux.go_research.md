<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go -->
# sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go

Purpose: non-Linux stub for rootless OCI spec conversion.

Important APIs and types: `ToRootless`.

Control flow: always returns an error stating rootless conversion is not implemented on the current GOOS.

State and persistence: none.

Dependencies and integration: uses runtime GOOS and `pkg/errors`; preserves API compatibility for cross-platform builds.

Risks: callers must handle the error on non-Linux platforms.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/specconv/specconv_nonlinux.go -->
