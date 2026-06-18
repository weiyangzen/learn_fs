# sources/cloud-native/moby/integration/service/inspect_test.go

## Purpose
Validates that `ServiceInspect` returns a rich Swarm service object equivalent to the service spec submitted through the API, including annotations, container spec, DNS config, restart policy, update and rollback config, service mode, IDs, and timestamps.

## Important APIs, Types, And Functions
- `TestInspect` creates a two-replica service from `fullSwarmServiceSpec`, waits for tasks, inspects the service, and compares against an expected `swarmtypes.Service`.
- `cmpServiceOpts` builds `cmp` options that compare `CreatedAt` and `UpdatedAt` within a 20 second threshold and equate `netip` comparable values.
- `fullSwarmServiceSpec` constructs the canonical expected service specification used here and by list tests.

## Control Flow
The test skips remote daemons and Windows, starts a Swarm daemon, records `time.Now`, creates the service with `QueryRegistry: false`, waits for both tasks to run, inspects by ID, and performs a deep comparison with relaxed timestamp handling.

## State And Persistence
Persistent state is the Swarm service object and its tasks inside the temporary test daemon. No explicit service removal is needed because package cleanup and daemon shutdown own teardown. Time state is intentionally approximate because service creation timestamps are daemon-generated.

## Dependencies And Integration Points
Uses the API client `ServiceCreate` and `ServiceInspect`, Swarm polling helpers, `google/go-cmp`, and Moby Swarm API types. It touches serialization/deserialization of service specs and SwarmKit's storage metadata.

## Risks And Edge Cases
The expected version index is hard-coded to `11`, which can be brittle if SwarmKit object creation sequencing changes. The timestamp comparator tolerates clock and scheduling delay but only within 20 seconds. The fixture assumes `busybox:latest` is available through frozen images.

## Test Signals
Passing means the inspected service preserves the full submitted spec, includes the expected ID and metadata, and exposes timestamps close to creation time.
