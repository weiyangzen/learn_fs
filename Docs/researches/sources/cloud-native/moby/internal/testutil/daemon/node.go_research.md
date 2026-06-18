# sources/cloud-native/moby/internal/testutil/daemon/node.go

## Purpose
Provides Swarm node helper methods on `Daemon` for inspect, remove, update, and list operations in integration tests.

## Important APIs, Types, And Functions
- `NodeConstructor` mutates a `swarm.Node`.
- `GetNode` inspects a node and optionally tolerates errors through supplied predicates.
- `RemoveNode` removes a node with optional force.
- `UpdateNode` retries node updates on `update out of sequence` errors.
- `ListNodes` returns all Swarm nodes.

## Control Flow
Each helper creates a daemon client and defers close. `UpdateNode` loops up to 11 attempts: inspect latest node, apply constructors, submit update with current version, retry short sleeps for sequence errors, otherwise assert success.

## State And Persistence
Mutates Swarm node objects for updates/removals. Node state persists in Swarm raft state until changed or cleaned.

## Dependencies And Integration Points
Uses Moby Swarm node APIs, daemon client helpers, gotest assertions, and string matching for sequence errors.

## Risks And Edge Cases
Retry detection depends on error text. `GetNode` returns nil if an allowed error predicate matches, so callers must handle nil. Update constructors mutate the inspected object in place.

## Test Signals
Expected signals are successful node inspect/list, node removal without API error, and robust update despite transient version conflicts.
