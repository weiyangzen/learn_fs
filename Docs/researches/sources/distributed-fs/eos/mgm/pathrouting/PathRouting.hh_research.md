<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh -->
# sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh

Source read size: 135 lines, 5803 bytes.

## Purpose

Declares the `PathRouting` class and its public contract for path-prefix based MGM redirection.

## Important APIs, Types, and Functions

The header defines `PathRouting::Status`, constructor with update interval, destructor, `Reroute`, `Add`, `Remove`, `Clear`, `GetListing`, and private `UpdateEndpointsStatus`. Main fields are `mPathRoute`, `mPathRouteMutex`, `mThread`, and `mTimeout`.

## Control Flow

The constructor stores the update timeout and starts the assisted status-update thread if the timeout is nonzero. Public methods are implemented in the `.cc`: route-table mutation takes write locks, routing/listing take read locks, and the private thread method polls endpoint status until termination is requested.

## State and Persistence Behavior

The route table is process-local memory. There is no serialization in this header; persistence, if any, is handled by higher-level configuration code that calls `Add` and `Remove`.

## Dependencies and Integration Points

Includes MGM namespace/logging, `Mapping`, `AssistedThread`, and `RouteEndpoint`. Consumers include MGM redirect decisions and admin route listing/configuration commands.

## Risks and Edge Cases

Callers must normalize route keys consistently with `Reroute`'s trailing-slash logic. Thread lifetime is tied to the object. `RouteEndpoint` equality determines duplicate detection semantics.

## Test Signals

Compile tests for route consumers, construction with zero and nonzero timeout, route-table concurrent add/list/reroute coverage, and endpoint status update tests using controlled `RouteEndpoint` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh -->
