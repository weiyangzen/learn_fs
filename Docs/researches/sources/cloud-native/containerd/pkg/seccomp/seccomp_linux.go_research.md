<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go

## Purpose
Linux seccomp support detection based on prctl error behavior.

## Important APIs, Types, And Functions
isEnabled uses sync.Once and unix.Prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, nil) and treats EINVAL as unsupported and any other error as supported.

## Control Flow
The first call performs the kernel probe, stores enabled, and all later calls return the cached value.

## State And Persistence
Process-global cached boolean guarded by sync.Once; no filesystem persistence.

## Dependencies And Integration Points
Depends on x/sys/unix. Mirrors runc-style capability detection.

## Risks And Edge Cases
Relies on Linux prctl error semantics: EACCES/EFAULT imply configured support. A future kernel semantic change could misclassify.

## Test Signals
No direct tests; behavior is kernel-specific.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go -->
