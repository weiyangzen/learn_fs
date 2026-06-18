# sources/cloud-native/moby/client/version.go

## Purpose
Implements daemon version retrieval and typed decoding of version, API, platform, component, and runtime metadata.

## APIs, Types, And Functions
`ServerVersionOptions` is empty; `ServerVersionResult` embeds `system.Version`; `PlatformInfo` describes platform names; `Client.ServerVersion` performs `GET /version` and decodes the result.

## Control Flow, State, And Integration
The method sends a simple GET request, decodes JSON into `system.Version`, and returns it. It reads daemon build/runtime state and does not modify client fields itself.

## Risks And Test Signals
Risks include schema drift for components/runtimes, invalid JSON, and callers using server version for feature gates. Integration is central to API negotiation, diagnostics, and CLI version output.
