# sources/cloud-native/containerd/api/services/introspection/v1/introspection.proto

## Purpose

This proto file defines containerd's Introspection service, which lets clients discover daemon plugins, server identity, deprecations, and plugin-provided dynamic details. It is capability discovery and diagnostics infrastructure rather than a mutating metadata API.

## Important APIs, Types, and Functions

The service has unary RPCs `Plugins`, `Server`, and `PluginInfo`. `Plugin` describes plugin type, id, dependency requirements, supported platforms, export key/value data, capabilities, and initialization error status. `PluginsRequest` filters plugin lists. `ServerResponse` contains daemon UUID, PID, PID namespace, and repeated `DeprecationWarning`. `PluginInfoRequest` includes plugin type, id, and optional `Any` options; `PluginInfoResponse` returns the `Plugin` plus optional `Any` extra data.

## Control Flow

Clients list plugins to detect daemon features, call `Server` for daemon process identity and deprecation state, and call `PluginInfo` when a specific plugin supports richer dynamic information. PluginInfo options and extra payloads are plugin-defined, so the server may return not-implemented or invalid-argument errors for unsupported option types or values.

## State and Persistence Behavior

The schema reports runtime state. It does not define persistent storage. Plugin exports and capabilities are dynamic feature/configuration signals. `InitErr` records initialization failure state. Deprecation warnings carry the last occurrence timestamp to help clients understand whether deprecated behavior has been observed recently.

## Dependencies and Integration Points

Imports are `google.protobuf.Any`, `Empty`, `Timestamp`, `google.rpc.Status`, `types/introspection.proto`, and `types/platform.proto`. `go_package` maps to `github.com/containerd/containerd/api/services/introspection/v1;introspection`. Generated gRPC and ttrpc files expose the same service over both transports.

## Risks and Test Signals

Risks include loose contracts around plugin-defined `Any` payloads, feature-detection clients relying on export strings that may change, platform-list interpretation mistakes, and leaking internal plugin state through exports or extra data. Tests should cover filter syntax, plugins with and without platform restrictions, plugins with initialization errors, server response identity fields, deprecation warning timestamp handling, and PluginInfo error behavior for unsupported options.
