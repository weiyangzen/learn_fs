# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_unsupported.go

## Purpose
Unsupported-platform cgroup manager stub.

## Important APIs, Types, and Functions
Defines CgroupManager interface subset, NullCgroupManager, Set/New, MoveProcessToContainerCgroup, VerifyMemoryIsEnough and no-op methods for unsupported builds.

## Control Flow
Unsupported builds return null manager behavior or unsupported errors.

## State and Persistence
No real cgroup state.

## Dependencies
Build tags select this file outside Linux.

## Integration Points
Allows non-Linux compilation of packages that reference cgmgr.

## Risks and Edge Cases
Runtime cgroup functionality unavailable; method signatures must match Linux interface expectations.

## Test Signals
Compile tests on unsupported platforms are signal.
