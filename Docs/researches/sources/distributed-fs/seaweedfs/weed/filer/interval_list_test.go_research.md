# sources/distributed-fs/seaweedfs/weed/filer/interval_list_test.go

## Purpose

`interval_list_test.go` validates the interval overlay and timestamp-aware insertion algorithms with many boundary combinations. It documents expected segment counts for overwrites and timestamp precedence.

## Important APIs, Types, and Functions

The file defines `IntervalInt` and `IntervalStruct` as test payloads satisfying `IntervalValue`. Test functions cover `Overlay` cases 1 through 11, `InsertInterval` cases 1 through 11, and struct payload insertion.

## Control Flow

Each test builds a new list, applies ordered operations, prints the resulting ranges for human debugging, and asserts final list length. Overlay tests cover full cover, left and right partial cover, same start/end, adjacent writes, and ignored zero-length overlay. Insert tests cover older/newer interval interactions, gaps, and splitting around existing intervals.

## State and Persistence Behavior

All state is in-memory and local to each test. The tests do not validate persistent side effects. `IntervalStruct.SetStartStop` has a value receiver, so it does not mutate the struct in the test; this limits coverage for payload boundary mutation.

## Dependencies and Integration Points

The tests use `stretchr/testify/assert` and the interval list APIs in the filer package. They indirectly cover reader/chunk-view behavior that depends on interval ordering.

## Risks and Edge Cases

The tests assert mostly counts rather than exact interval boundaries, and many tests print to stdout instead of using structured assertions. This can miss value aliasing, incorrect timestamp assignment, or wrong start/stop values if the number of intervals is unchanged.

## Test Signals

Useful added signals would assert exact interval sequences, payload start/stop mutation, clone identity, zero-length insert behavior, and race detection under representative read/write locking.
