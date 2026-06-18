# sources/distributed-fs/eos/unit_tests/mgm/TrafficShapingTests.cc

## Purpose
Tests the MGM traffic shaping engine and manager. Coverage spans config propagation, detail-level stats, report aggregation, policy persistence boundaries, garbage collection, reservation-controller decisions, delay calculation, ephemeral controller limits, and delay publication gates.

## Important APIs, types, and functions
The tests exercise `TrafficShapingEngine` methods for detail, limits, reservations, GC idle seconds, and active-node-rate threshold; `TrafficShapingManager` methods for report processing, estimator updates, policy loading/serialization, policy accessors, garbage collection, controller-limit expiration, reserved-app pressure, default reservation controller, delay calculation, and `ShouldEmitDelayForPolicy`. They also use `eos::traffic_shaping::FstIoReport` and `AppState`.

## Control flow
Engine tests apply config under FsView write lock and verify values propagate to the manager. Manager tests synthesize FST IO reports, update estimators, inspect global/disk/detailed/projection cardinality, load JSON policies, apply controller-only updates without persistence, and expire ephemeral limits after five minutes. Delay tests call pure calculation helpers across idle, above-limit, near-target, global-vs-node, and reference-rate cases. Reservation-controller tests mutate `AppState` vectors and assert when competitor limits are set or cleared.

## State and persistence
State includes in-memory policy maps, cumulative stats, EMA rates, controller-limit timestamps, reservation flags, and detail toggles. Persistent policy JSON is distinguished from ephemeral controller-only limits; serialization is expected to omit ephemeral-only updates.

## Dependencies and integration points
Depends on Google Test, traffic shaping internals under `IN_TEST_HARNESS`, FsView lock, common constants, and protobuf FST IO reports. It integrates MGM control-plane policy with FST rate/delay publication.

## Risks and test signals
This is a broad regression suite for new shaping behavior. Risks include floating-point tolerance, clock/timestamp expiry boundaries, JSON policy compatibility, stale controller limits, map cardinality leaks, and incorrect throttling under reservation pressure. Missing signals include multi-threaded report ingestion and full engine-to-FST publication integration.
