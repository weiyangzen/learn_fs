# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_test.go

## Purpose
Tests for capabilities defaults and validation.

## Important APIs, Types, and Functions
Ginkgo specs assert default list and Validate success/failure for known/unknown capabilities.

## Control Flow
Calls package functions directly.

## State and Persistence
No state.

## Dependencies
Depends on Ginkgo/Gomega and host/common capabilities validator.

## Integration Points
Validates capabilities_linux.go.

## Risks and Edge Cases
Unknown capabilities should fail consistently; host capability set may vary in edge cases.

## Test Signals
go test suite is signal.
