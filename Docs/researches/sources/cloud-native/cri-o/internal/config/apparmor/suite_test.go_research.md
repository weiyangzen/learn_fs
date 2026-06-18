# sources/cloud-native/cri-o/internal/config/apparmor/suite_test.go

## Purpose
Ginkgo suite bootstrap for AppArmor config tests.

## Important APIs, Types, and Functions
TestLibConfig registers fail handler and RunFrameworkSpecs; BeforeSuite creates TestFramework; AfterSuite tears down.

## Control Flow
Standard suite lifecycle.

## State and Persistence
Temporary test framework state.

## Dependencies
Depends on test/framework, Ginkgo, Gomega.

## Integration Points
Supports apparmor_test.go.

## Risks and Edge Cases
Failures in setup affect all specs.

## Test Signals
go test invokes suite.
