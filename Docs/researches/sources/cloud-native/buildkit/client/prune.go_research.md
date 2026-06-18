# sources/cloud-native/buildkit/client/prune.go

## Purpose
This client API wraps the BuildKit control service `Prune` RPC and streams deleted or pruned cache records back to callers as client-level `UsageInfo` values.

## Important APIs, Types, and Functions
- `Client.Prune(ctx, ch, opts...)` is the public entry point.
- `PruneOption` and `pruneOptionFunc` provide the option pattern.
- `PruneInfo` stores request fields: `All`, filter strings, keep duration, reserved/max-used/min-free space.
- `PruneAll` enables complete pruning.
- `WithKeepOpt(duration, reserved, max, free)` fills keep and space policy fields.

## Control Flow
`Prune` creates a `PruneInfo`, applies all options, maps it into `controlapi.PruneRequest`, calls `ControlClient().Prune`, and loops over streamed responses until EOF. Each response is converted into `UsageInfo` and sent to `ch` when a channel is provided. Non-EOF stream errors abort the call.

## State and Persistence Behavior
The function does not store state locally. It triggers daemon-side garbage collection and reports daemon-side records. `LastUsedAt` is converted only when the protobuf timestamp is present, preserving nil when the daemon does not know a last-used time.

## Dependencies and Integration Points
This file depends on the control API protobuf service, `UsageInfo`/`UsageRecordType` types defined elsewhere in the client package, and standard time conversion. It is the client-facing bridge for BuildKit cache cleanup tooling.

## Risks and Edge Cases
If `ch` is unbuffered or the receiver stops reading, `Prune` blocks while streaming. The code does not close `ch`, leaving channel ownership to the caller. Duration is sent as raw `int64(info.KeepDuration)`, so both client and daemon must agree on nanosecond `time.Duration` semantics.

## Test Signals
No direct tests are in this file. Indirect signals come from integration tests and cache cleanup flows that exercise `Client.Prune` and validate returned `UsageInfo` fields.
