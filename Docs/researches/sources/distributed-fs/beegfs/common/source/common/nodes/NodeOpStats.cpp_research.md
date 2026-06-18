# sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.cpp

## Purpose
Serializes per-client or per-user operation counters into the `uint128_t` vector layout consumed by `fhgfs-ctl`, with cookie-based pagination.

## Important APIs, Types, And Functions
`mapToUInt128Vec()` is the core API. `getMaxIPsPerVector()` calculates how many map entries fit in a response buffer, and `reserveVector()` preallocates output capacity.

## Control Flow
The method selects either `userCounterMap` or `clientCounterMap`, positions after a cookie unless the cookie is all-bits-one, reserves header plus per-IP data, writes metadata fields (`num ops`, `more data`, layout version), appends each key and its `OpCounter` values until the buffer-derived limit is reached, and sets the more-data flag if entries remain.

## State, Persistence, And Dependencies
The function reads in-memory maps under `SafeRWLock`. It depends on `OpCounter`, `Common.h` integer helpers, and constants from `NodeOpStats.h`. There is no disk persistence.

## Integration Points
Derived metadata and storage op-stat classes populate the maps; management/ctl message handlers call `mapToUInt128Vec()` to stream stats to users.

## Risks
If `bufLen` is too small, `maxNumIPs` can be zero and the method may return an empty data vector with `more data` semantics that callers must handle. Layout changes require bumping `OPCOUNTER_VEC_LAYOUT_VERS`. Cookie ordering follows map key ordering, so clients must use the last returned key.

## Test Signals
Validate empty maps, all-bits-one cookie, mid-map cookie, zero/very small buffer, exact-fit buffer, multi-page responses, user versus client maps, and layout version compatibility.
