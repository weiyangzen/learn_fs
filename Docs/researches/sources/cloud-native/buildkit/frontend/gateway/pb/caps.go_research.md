# sources/cloud-native/buildkit/frontend/gateway/pb/caps.go

## Purpose

This file defines the gateway frontend API capability IDs and registers them in a global `apicaps.CapList`. Capabilities document and gate wire/API features for compatibility between frontend clients and BuildKit daemons.

## Important APIs, Types, And Functions

- `Caps` is the global gateway capability list.
- Capability constants include solve, inline return, image resolution, file read, explicit return, result maps, read dir, stat file, cache imports, proto ref arrays, reference output, frontend inputs, gateway metadata, exec, exec extra hosts, secret env, signals, exec filesystem, frontend caps, evaluate, warnings, attestations, and source metadata resolver feature levels.
- `init` registers each capability with ID, optional name, enabled state, status, and deprecation flag.

## Control Flow

During package initialization, every capability is added to `Caps`. Most are enabled experimental capabilities. `CapSolveInlineReturn` is marked deprecated. The comments establish the compatibility policy: non-compatible changes need new capability rows, experimental by default, immutable after merge, and stable capabilities should not be disabled.

## State And Persistence Behavior

`Caps` is global package state initialized once. It is exported through gateway ping responses and converted into capability sets by clients and forwarders. It is not persisted to disk.

## Dependencies And Integration Points

It depends on `util/apicaps`. Server-side `Ping` returns `pb.Caps.All()`, the grpc client checks support before optional API calls, and gateway image frontend label checks compare requested frontend capabilities with labels.

## Risks And Edge Cases

Capability IDs are wire contracts and must not be renamed. Some comments are copy-paste inaccurate for secret env and signals, but the IDs and names are distinct. Adding a feature without gating it here can break old clients or servers. Marking capabilities enabled by default means unsupported implementations must not advertise them.

## Test Signals

No direct tests are in this subset. Compatibility is exercised indirectly by grpc client and server integration. Snapshot-style tests over the cap list could catch accidental ID changes.
