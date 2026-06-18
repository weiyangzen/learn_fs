# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_test.go

## Purpose
Ginkgo/Gomega tests for Linux AppArmor config behavior.

## Important APIs, Types, and Functions
Specs exercise New, LoadProfile, IsEnabled, and Apply behavior for default, localhost, runtime/default, unconfined, and invalid profiles.

## Control Flow
Test framework creates temp fixtures and asserts returned profile/errors.

## State and Persistence
Uses temporary files and host AppArmor availability assumptions through package behavior.

## Dependencies
Depends on Ginkgo/Gomega and CRI-O test framework.

## Integration Points
Validates apparmor_linux.go behavior.

## Risks and Edge Cases
Tests may be host-feature-sensitive if AppArmor is absent.

## Test Signals
RunFrameworkSpecs suite is the signal.
