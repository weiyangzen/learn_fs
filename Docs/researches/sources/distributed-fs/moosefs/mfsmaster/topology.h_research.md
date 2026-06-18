# sources/distributed-fs/moosefs/mfsmaster/topology.h

## Purpose
`topology.h` declares the master network-topology lookup API and public distance constants.

## Important APIs, Types, And Functions
It defines `TOPOLOGY_DIST_SAME_IP`, `TOPOLOGY_DIST_SAME_RACKID`, and `TOPOLOGY_DIST_MAX`, and declares `topology_get_rackid()`, `topology_distance()`, and `topology_init()`.

## Control Flow
Callers initialize the module through `topology_init()`, then query rack ids and pairwise distances for IP addresses. Reload/destruction are registered internally and are not exposed here.

## State, Persistence, And Dependencies
The header includes only `<inttypes.h>`. All topology state and file parsing live in `topology.c`.

## Integration Points
Chunk placement and read selection consume the lookup functions. Startup code uses `topology_init()`.

## Risks
`TOPOLOGY_DIST_MAX` is defined as 2, but `topology_distance()` can return values greater than 2 for hierarchical rack paths. Callers should not treat it as a hard maximum for all possible return values; it is better read as the base "different rack" distance.

## Test Signals
Caller tests should accept distances above 2 and only rely on 0 for same IP and 1 for same rack id.
