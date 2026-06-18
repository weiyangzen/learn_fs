<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh -->
# sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh

## Purpose
Declares the `eos::mgm::RouteEndpoint` class used to describe MGM path-routing redirect targets. The class stores endpoint identity, XRootD/HTTP ports, and online/master status flags while exposing parsing, serialization, equality, and status-refresh operations.

## Important APIs and Types
- `RouteEndpoint()`: default endpoint with offline/non-master status and zero ports.
- `RouteEndpoint(const std::string&, uint32_t, uint32_t)`: constructs an endpoint from FQDN and ports, initially offline and non-master.
- Move constructor and move assignment: enable insertion into containers and transfer into routing tables.
- `ParseFromString`, `ToString`, `UpdateStatus`: implemented in the `.cc` file.
- `GetHostname()`, `GetXrdPort()`, `GetHttpPort()`: inline accessors.
- `operator==` / `operator!=`: compare only endpoint identity fields, not online/master status.
- Public `std::atomic<bool> mIsOnline` and `mIsMaster`: runtime routing status exposed for direct manipulation by routing code/tests.

## Control Flow and Usage Contract
The header establishes a two-phase endpoint lifecycle: construct or parse identity first, then update or externally set status. `PathRouting` can then use the endpoint to pick redirect destinations. Equality ignores status, so duplicate detection is based on host and ports rather than health.

## State and Persistence
State is entirely in-memory. Persistent route definitions are likely stored/managed by surrounding MGM routing configuration code, while this type carries the parsed endpoint. Atomic booleans allow status updates and reads from multiple threads, but hostname and ports are not atomic and should be considered immutable after publishing unless protected externally.

## Dependencies and Integration Points
Includes `mgm/Namespace.hh` for the MGM namespace, `common/Logging.hh` for `eos::common::LogId`, and C++ string/integer headers. The class is referenced by `mgm/pathrouting/PathRouting.hh`, user route commands, and `unit_tests/mgm/RoutingTests.cc`.

## Risks
- Public mutable atomic flags make status manipulation easy but bypass invariants.
- The type has move support but no explicit copy constructor/assignment, largely because atomics are not copyable; callers need move semantics.
- Accessors return ports as `int` even though storage is `uint32_t`; values above `INT_MAX` would be lossy if admitted by parsing.
- Equality ignoring status is useful for route identity but can surprise callers expecting full object equality.

## Test Signals
`RoutingTests.cc` validates construction/parsing failures, equality/inequality, duplicate prevention in `PathRouting`, and routing decisions when status flags are manually set. Header-only API risks around port range and copy/move constraints are not directly covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/routeendpoint/RouteEndpoint.hh -->
