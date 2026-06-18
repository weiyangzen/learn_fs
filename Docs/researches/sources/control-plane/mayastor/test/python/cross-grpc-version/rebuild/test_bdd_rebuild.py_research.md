# sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/test_bdd_rebuild.py

## Purpose
BDD tests for v1 rebuild operations on a nexus created through the legacy API.

## Important APIs, Types, And Functions
Defines state conversion helpers, `lookup_nexus`, `lookup_nexus_child`, `wait_child_state`, `mayastor_nexus`, `rebuild_state`, and steps for add child, start/stop/pause/resume rebuild, child online/offline, stats retrieval, and assertions over nexus/child/rebuild counters.

## Control Flow
Module fixtures create source and target aio files. A legacy nexus is created with the source child, v1 nexus RPCs add the target child and control rebuild state, and then legacy/v1 state reads verify transitions and counters.

## State And Persistence
State includes `/tmp/disk-rebuild-source.img`, `/tmp/disk-rebuild-target.img`, the legacy nexus, target child, and rebuild task. Cleanup destroys the nexus and removes files.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `nexus_pb2`, gRPC status handling, `retrying.retry`, and both common/v1 Mayastor fixtures.

## Risks
Polling expects state to settle within retry defaults. Conversion maps must stay in sync with v1 enum names. Rebuild stats assertions depend on task progress being nonzero at the right moment.

## Test Signals
Passing scenarios validate cross-version rebuild command compatibility, child action mapping, stopped-state handling, and rebuild statistics visibility.
