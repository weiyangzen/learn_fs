# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator_test.go

## Purpose
Provides broad behavioral and regression coverage for the default IPAM driver.

## Important APIs, Types, And Functions
- Tests cover `PoolID` round-tripping, pool add/release, predefined dynamic pools, preferred subnet sizes, overlap checks, subpool allocation, address allocation/release, serial mode, syntax validation, unusual subnets, random deallocate/reallocate, and parallel scenarios.
- Benchmarks measure request exhaustion and pool ID conversion overhead.

## Control Flow
Tests build fresh allocators from default pools, issue IPAM API requests, and assert returned pool IDs, IPNet masks, address sequences, and error identities. Some tests intentionally request historical edge cases such as overlapping subpools and child subnet compatibility.

## State And Persistence
All allocator state is in-memory. Parallel tests use package-level synchronization for `t.Parallel` cases and errgroups for racing request/release operations.

## Dependencies And Integration Points
Uses `ipamapi`, `ipamutils`, `addrset`, `netiputil`, `types`, and `errgroup`. These tests are the main safety net for default IPAM behavior consumed by libnetwork network creation.

## Risks
Some random tests use current time as seed; failures log the seed but are not deterministic by default. Several tests are skipped or constrained by Go test parallelism flags. Heavy allocation loops can be expensive for large subnets, so some exhaustive cases are commented out.

## Test Signals
Strong signals include duplicate address prevention under concurrent release/request, `ErrNoAvailableIPs` on exhaustion, `ErrIPOutOfRange` on invalid preferred addresses, reusing released addresses, preserving /31 usable endpoints, and maintaining compatibility with documented validation inconsistencies.
