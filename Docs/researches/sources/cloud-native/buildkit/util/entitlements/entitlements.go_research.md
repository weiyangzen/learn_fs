# sources/cloud-native/buildkit/util/entitlements/entitlements.go

## Purpose
Entitlement parsing and allow-list enforcement for privileged BuildKit features. It covers security.insecure, network.host, and device with optional device config/aliases.

## Important APIs, Types, And Functions
Package: `entitlements`. Build tags: `none`. Key declarations observed in the file: `Entitlement, String, all, EntitlementsConfig, DevicesConfig, _, ParseDevicesConfig, Merge, Parse, WhiteList, Set, Allowed, ...`.

## Control Flow, State, And Persistence
Parse handles device=<csv fields>, WhiteList validates allowed values against optional daemon-supported list and merges device configs, Set.Check validates requested Values for network/security.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, github.com/tonistiigi/go-csvvalue`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are config parsing errors, unsupported daemon entitlements, and device entitlement not checked by Values.Check here. No local tests.
