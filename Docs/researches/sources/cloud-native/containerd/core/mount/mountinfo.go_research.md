<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mountinfo.go -->
# sources/cloud-native/containerd/core/mount/mountinfo.go

Purpose: exposes mountinfo lookup through the mount package.

Important APIs/types/functions: this file aliases or wraps `moby/sys/mountinfo` types/functions so callers can query mount table entries without importing the lower-level package directly.

Control flow: lookup functions read current mountinfo and filter by target/path according to the underlying mountinfo implementation.

State and persistence: read-only view of kernel mount table state.

Dependencies and integration points: used by platform mount implementations and tests to compare mount IDs before/after helper invocations and to detect successful mounts.

Risks: behavior depends on `/proc/self/mountinfo` availability and namespace context on Unix-like systems. Stale or namespace-mismatched lookup results can affect ECHILD cleanup decisions.

Test signals: indirectly exercised by FUSE/FreeBSD-style helper retry logic and Linux tests using `Lookup`/unmount flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mountinfo.go -->
