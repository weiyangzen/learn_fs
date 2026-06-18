# sources/cloud-native/cri-o/internal/oci/container_unsupported.go

## Purpose
Fallback implementation for platforms that are neither Linux nor FreeBSD.

## Behavior, Integration, and Risks
`getPidStartTime` always returns `"0", nil`, allowing code to compile and PID initialization to proceed but disabling meaningful PID reuse protection. Because `Container.verifyPid` depends on start-time equality, this fallback is intentionally weak and should not be treated as equivalent to Linux/FreeBSD support. No direct tests cover this unsupported path.
