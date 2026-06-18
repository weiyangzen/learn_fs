# sources/cloud-native/buildkit/util/appdefaults/appdefaults.go

## Purpose
Shared default network constants for BuildKit. It defines BridgeName buildkit0 and BridgeSubnet 10.10.0.0/16.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow or state. Platform-specific appdefaults files add socket/root/config defaults.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is collisions with local network configuration. No tests.
