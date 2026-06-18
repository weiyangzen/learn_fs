# sources/cloud-native/containerd/plugins/services/version/service.go

## Purpose
`version/service.go` registers the gRPC version service.

## Important APIs, Types, And Functions
The plugin ID is `version`. `service` implements `api.VersionServer`; `Version` returns `ctrdversion.Version` and `ctrdversion.Revision`.

## Control Flow
Plugin initialization returns an empty service. `Register` installs the server on a gRPC server. The `Version` RPC ignores the empty request and reads package-level version variables.

## State And Persistence
No mutable state or persistence exists. Values are build-time/version package state.

## Dependencies And Integration Points
It integrates the version API, plugin registry, gRPC, and `containerd/v2/version`.

## Risks
If version variables are not populated at build time, the service returns those defaults. No validation is performed.

## Test Signals
No direct tests are in this subset. Basic daemon API tests normally cover this endpoint.
