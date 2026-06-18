# sources/distributed-fs/lizardfs/src/master/topology.h

## Purpose

`topology.h` declares the public topology API: distance lookup between two IP addresses and module initialization. The source was read as a complete 26-line header.

## Important APIs, Types, and Functions

The header declares `uint8_t topology_distance(uint32_t ip1, uint32_t ip2)` and `int topology_init(void)`.

## Control Flow

No implementation flow is present. Callers initialize the module and later query distances.

## State and Persistence Behavior

The header owns no state. The implementation loads topology config into runtime interval-tree state.

## Dependencies and Integration Points

It depends on `common/platform.h` and integer types. It is used by placement logic that wants rack/locality awareness.

## Risks and Edge Cases

Callers should treat return values as coarse classes, not physical distances beyond the implementation's 0/1/2 semantics.

## Test Signals

Compile coverage and placement tests that mock or load topology and observe distance effects.
