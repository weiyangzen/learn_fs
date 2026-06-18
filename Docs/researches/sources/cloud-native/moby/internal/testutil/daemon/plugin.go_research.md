# sources/cloud-native/moby/internal/testutil/daemon/plugin.go

## Purpose
Provides polling predicates for plugin state on a test daemon.

## Important APIs, Types, And Functions
- `PluginIsRunning`, `PluginIsNotRunning`, `PluginIsNotPresent`, and `PluginReferenceIs` return `poll.Check` functions.
- `withPluginInspect` wraps plugin inspection and delegates to a predicate.
- `withClient` creates/closes a daemon client for each poll.

## Control Flow
Poll predicates inspect a plugin by name through a new client. They translate not-found and state/reference mismatches into `poll.Continue`, success into `poll.Success`, and unexpected errors into `poll.Error`.

## State And Persistence
Read-only observation of daemon plugin state. Polling creates short-lived clients repeatedly.

## Dependencies And Integration Points
Uses plugin API types, client plugin inspect, containerd errdefs, daemon client helpers, and gotest poll.

## Risks And Edge Cases
Name/reference ambiguity matters because plugin service tests may use explicit names or remote references. Creating a new client on every poll is simple but can add overhead.

## Test Signals
Signals are successful plugin running state, disabled/not-running state, not-found state, or matching plugin remote reference.
