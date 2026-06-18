# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space_test.go

## Purpose
Tests the lower-level address-space allocator, especially predefined dynamic pool selection and release/reuse behavior.

## Important APIs, Types, And Functions
- `TestNewAddrSpaceDedup` verifies overlapping predefined entries are sorted and deduplicated.
- `TestDynamicPoolAllocation` is a large table of allocation/reservation overlap scenarios and prefix-size requests.
- `TestStaticAllocation` checks sorted insertion of static pools.
- `TestPoolAllocateAndRelease` regresses release/reallocate behavior from Moby issue 48069.

## Control Flow
The dynamic allocation table constructs an `addrSpace`, injects existing allocations, calls `allocatePredefinedPool`, and compares returned prefix or expected error. Release tests use closures to simulate network name to subnet ownership, checking no duplicate or reserved allocation occurs.

## State And Persistence
All state is in-memory test allocator state. Tests deliberately manipulate `as.allocated` to exercise allocator internals.

## Dependencies And Integration Points
Uses `netip`, `ipamutils.NetworkToSplit`, `ipamapi` errors, and `cmpopts` for prefix-comparable assertions.

## Risks
The tests document many compatibility cases but also reveal the allocator's complexity. If reserved prefixes are not sorted in real callers despite the API contract, behavior may diverge from the tested cases.

## Test Signals
Strong coverage of full overlap, partial overlap, duplicate allocations, reserved exclusions, invalid requested sizes, specified subnet sizes larger/smaller than predefined defaults, and reusing released subnets.
