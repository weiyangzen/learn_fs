<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks_test.go -->
# sources/cloud-native/containerd/plugins/content/local/locks_test.go

## Purpose
Unit test for local store ref locks.

## Important APIs, Types, And Functions
TestTryLock calls tryLock twice on the same ref and checks second error contains lock duration text.

## Control Flow
Creates minimal store with locks map, locks/unlocks a ref.

## State And Persistence
Pure in-memory state.

## Dependencies And Integration Points
Exercises locks.go duplicate protection.

## Risks And Edge Cases
Does not test concurrent goroutines or unlock of absent refs.

## Test Signals
Direct coverage for duplicate lock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks_test.go -->
