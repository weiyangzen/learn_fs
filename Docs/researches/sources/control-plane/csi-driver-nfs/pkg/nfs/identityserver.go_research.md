# sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver.go

Purpose: implements the CSI Identity service for the NFS driver.

Important APIs and types: `IdentityServer` embeds `csi.UnimplementedIdentityServer` and exposes `GetPluginInfo`, `Probe`, and `GetPluginCapabilities`.

Control flow: `GetPluginInfo` rejects empty driver name or version with `codes.Unavailable`, otherwise returns the configured driver name and vendor version. `Probe` always reports ready with a protobuf bool wrapper. `GetPluginCapabilities` advertises `PluginCapability_Service_CONTROLLER_SERVICE`.

State and persistence behavior: identity responses are derived from the in-memory `Driver` fields only. No persistent state, filesystem state, or network state is touched.

Dependencies and integration points: depends on CSI protobuf types, gRPC status codes, and `wrapperspb`. Registered by `server.go` when `Driver.Run` starts the gRPC server.

Risks: readiness is unconditional, so it does not prove mount dependencies, endpoint health, or controller/node initialization. Capability advertisement assumes a controller service is always registered.

Test signals: `identityserver_test.go` covers success and missing driver metadata paths, readiness response, and advertised plugin capability.
