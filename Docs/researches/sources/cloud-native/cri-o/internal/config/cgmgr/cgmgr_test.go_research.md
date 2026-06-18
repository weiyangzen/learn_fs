# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_test.go

## Purpose
Tests for cgroup manager selection, naming, paths, memory validation, and manager behavior.

## Important APIs, Types, and Functions
Ginkgo specs create default/systemd/cgroupfs managers and assert SetCgroupManager, Name, cgroup paths, sandbox path validation, memory minimum checks, and unsupported inputs.

## Control Flow
Direct unit-style calls into cgmgr package.

## State and Persistence
May touch temp paths or rely on host cgroup mode for selected branches.

## Dependencies
Depends on Ginkgo/Gomega and cgmgr package.

## Integration Points
Validates cgmgr_linux.go plus manager implementations.

## Risks and Edge Cases
Host cgroup version can affect expectations; tests focus on deterministic helper behavior where possible.

## Test Signals
go test suite is signal.
