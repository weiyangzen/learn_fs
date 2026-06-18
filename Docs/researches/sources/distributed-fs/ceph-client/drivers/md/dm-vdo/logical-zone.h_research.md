# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.h

## Purpose
`logical-zone.h` defines logical-zone state and declares zone lifecycle, flush-generation, allocation-zone, and dump APIs.

## Important APIs, Types, and Functions
`struct logical_zone` contains a completion for flush notification, owner pointer, zone/thread IDs, active LBN operation map, block-map zone, flush generation counters, notification state, active write list, admin state, current physical allocation zone, allocation counter, and next-zone link. `struct logical_zones` owns the VDO pointer, action manager, zone count, and flexible array of zones. The header declares construction, freeing, drain/resume, generation increment, lock acquire/release, allocation-zone selection, and dump functions.

## Control Flow
The header defines no executable flow, but it establishes that data VIO write paths call acquire/release around flush generations, admin code drains/resumes all zones through the action manager, and allocation code asks the logical zone for the next physical zone.

## State and Persistence Behavior
All fields are runtime state. The active-generation fields provide ordering for flush completion but are not stored on disk.

## Dependencies and Integration Points
It includes Linux lists, admin-state, int-map, and VDO types, and forward-declares physical zones. It is consumed by data VIO, flush, block-map, and VDO setup paths.

## Risks and Edge Cases
The exposed struct makes direct field access possible; correctness depends on callers honoring zone-thread ownership. `oldest_active_generation` is read from another thread, so updates must remain disciplined.

## Test Signals
Compile coverage, data VIO flush-generation lifecycle tests, drain/resume administrative tests, and allocation-zone rotation tests validate the header contract.
