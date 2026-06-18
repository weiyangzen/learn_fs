# sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_bitmap.h

## Purpose
This header provides bitmap ipset kernel constants layered on the uapi bitmap definitions.

## Important APIs, Types, and Functions
It defines `IPSET_BITMAP_MAX_RANGE` as `0x0000FFFF` and add-result sentinel values: `IPSET_ADD_STORE_PLAIN_TIMEOUT`, `IPSET_ADD_FAILED`, and `IPSET_ADD_START_STORED_TIMEOUT`.

## Control Flow
Bitmap set implementations use these values to constrain accepted ranges and distinguish add failure from add paths that need to store timeout data. There are no functions in this header.

## State and Persistence
No state is declared. Constants affect in-memory bitmap set behavior in implementation files.

## Dependencies and Integration Points
It includes `uapi/linux/netfilter/ipset/ip_set_bitmap.h` and is consumed by bitmap ipset type implementations.

## Risks
Range-boundary mistakes can cause off-by-one bitmap allocation or element addressing bugs. The negative timeout sentinel must not be confused with normal positive add results.

## Test Signals
Boundary tests around range 0, 1, `0xffff`, and overflow; add tests with timeout-enabled and timeout-disabled bitmap sets; and user/kernel ABI compatibility tests for uapi bitmap attributes.
