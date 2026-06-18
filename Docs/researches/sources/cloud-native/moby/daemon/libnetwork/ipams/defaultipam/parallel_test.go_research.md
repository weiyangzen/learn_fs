# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/parallel_test.go

## Purpose
Stress-tests default IPAM under concurrent pool, address allocation, and address release workloads.

## Important APIs, Types, And Functions
- `testContext` stores allocator, options, allocated IPs, pool ID, and expected capacity.
- `TestRequestPoolParallel` allocates every /24 from a /10 predefined range concurrently.
- `TestFullAllocateRelease`, `TestOddAllocateRelease`, and serial-release variants run address allocation and release with varying parallelism.
- `allocate` and `release` are helper routines using semaphores, goroutines, and errgroups.

## Control Flow
Tests allocate more goroutines than available IPs, collect successful allocations, assert no duplicates and exact capacity, then release all/odd/even subsets in parallel. Pool parallel test builds the expected complete subnet list and ensures all were allocated exactly once.

## State And Persistence
State is in-memory within the allocator and test context. The helpers coordinate with channels, wait groups, semaphores, and errgroups.

## Dependencies And Integration Points
Uses `errgroup`, `semaphore`, `ipamapi.AllocSerialPrefix`, and `ipamutils`. It validates `addrSpace` mutex behavior under real driver calls.

## Risks
Concurrency tests can be timing-sensitive. Some helper code ignores errors from `RequestAddress` during over-capacity goroutine runs and filters nils, which is intentional for exhaustion but could mask unexpected error types.

## Test Signals
Key signal is no duplicate IPs and no release failures across masks /29, /25, /24, /23, and /21 with parallelism up to 8.
