<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go

## Purpose
Non-Linux seccomp support stub.

## Important APIs, Types, And Functions
isEnabled always returns false.

## Control Flow
No control flow beyond return.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Preserves seccomp package API on unsupported platforms.

## Risks And Edge Cases
Silent false may need higher-level user-facing diagnostics for seccomp-required configs.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go -->
