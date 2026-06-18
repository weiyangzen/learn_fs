# sources/cloud-native/cri-o/test/mocks/config/cgmgr/cgmgr.go

## Purpose
Generated GoMock implementation of CRI-O `CgroupManager`.

## Important APIs, Types, And Functions
`MockCgroupManager` and recorder methods cover container/sandbox cgroup path resolution, cgroup manager creation, stats retrieval, create/remove, conmon movement, systemd detection, and manager naming.

## Control Flow
All methods delegate to GoMock call recording and typed return extraction.

## State And Persistence
Mock expectations are in memory only. It does not touch cgroup filesystems.

## Dependencies And Integration Points
Supports tests for resource updates, stats, sandbox/container lifecycle, and conmon cgroup placement. Imports CRI-O stats, opencontainers cgroups, and OCI specs.

## Risks And Test Signals
Because it bypasses real cgroup behavior, it verifies call contracts but not kernel/systemd semantics. Regenerate when the interface changes.
