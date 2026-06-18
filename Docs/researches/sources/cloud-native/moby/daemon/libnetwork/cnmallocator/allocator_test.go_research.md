<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go

## Purpose
Delegates generic SwarmKit allocator conformance tests to the CNM network allocator provider.

## Important APIs, Types, And Functions
`TestAllocator` calls `allocator.RunAllocatorTests(t, NewProvider(nil))` and skips on Windows because the generic test suite uses Linux driver names.

## Control Flow
The test is a single wrapper: skip condition first, then SwarmKit-provided allocator tests exercise provider/allocator behavior.

## State And Persistence
No persistent state; allocator instances are created inside the test suite.

## Dependencies And Integration Points
Integrates `cnmallocator.Provider` with SwarmKit manager allocator tests.

## Risks And Edge Cases
Coverage depends on SwarmKit's external test suite and is skipped on Windows, leaving Windows-specific predefined network names to separate tests.

## Test Signals
Passing this test shows CNM provider behavior remains compatible with SwarmKit allocator expectations on non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go -->
