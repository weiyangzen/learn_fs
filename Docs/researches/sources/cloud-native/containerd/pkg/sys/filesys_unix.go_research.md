<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_unix.go -->
# sources/cloud-native/containerd/pkg/sys/filesys_unix.go

## Purpose
Unix filesystem helper wrapper for ACL-aware mkdir API compatibility.

## Important APIs, Types, And Functions
MkdirAllWithACL delegates to os.MkdirAll.

## Control Flow
Single pass-through call.

## State And Persistence
Creates directories according to os.MkdirAll semantics.

## Dependencies And Integration Points
Keeps API parity with Windows ACL implementation.

## Risks And Edge Cases
Does not apply ACLs on Unix; callers must not assume Windows-style ACL behavior cross-platform.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_unix.go -->
