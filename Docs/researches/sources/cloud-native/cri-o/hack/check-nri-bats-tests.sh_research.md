# sources/cloud-native/cri-o/hack/check-nri-bats-tests.sh

## Purpose
Consistency check ensuring every Go NRI test case is represented in the NRI BATS wrapper.

## Important APIs, Types, and Functions
Runs test/nri/nri.test -test.list Test and greps test/nri.bats for matching -test.run invocations.

## Control Flow
Iterates listed tests, reports missing cases, accumulates status, exits non-zero if any are absent.

## State and Persistence
No state.

## Dependencies
Depends on built nri.test binary, grep, realpath, and NRI BATS file naming.

## Integration Points
Used by validation/CI to keep Go and BATS NRI coverage synchronized.

## Risks and Edge Cases
Pattern matching can miss renamed or parameterized invocations; requires binary built before running.

## Test Signals
Non-zero exit and missing-test messages are the signal.
