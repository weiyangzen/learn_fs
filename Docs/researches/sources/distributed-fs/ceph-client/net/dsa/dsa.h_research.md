# sources/distributed-fs/ceph-client/net/dsa/dsa.h

## Purpose
This private header exposes DSA core helpers shared across `dsa.c`, conduit, port, switch, tag, and user handling.

## Important APIs, Types, And Functions
It declares the global `dsa_tree_list`, database comparison, ordered work scheduling, LAG map/unmap/find helpers, first conduit lookup, runtime tag-protocol change, conduit admin/oper state notification helpers, bridge number get/put/find helpers, and bridge lookup.

## Control Flow
The header has no executable logic. Its functions are implemented mainly in `dsa.c` and called by the rest of DSA core.

## State And Persistence
The only declared state is `dsa_tree_list`, the global list of switch trees. Other declarations manipulate tree, bridge, and LAG runtime state owned elsewhere.

## Dependencies And Integration Points
It forward-declares DSA and netdev types to keep local includes lightweight. It is the glue for DSA internal modules that need topology state but not full public API exposure.

## Risks And Edge Cases
Because many declarations manipulate global topology, callers must obey locking expectations from implementations, especially `dsa2_mutex` and RTNL contexts.

## Test Signals
Compile coverage plus DSA probe, LAG, bridge, conduit state, and tagger-change tests exercise these declarations.
