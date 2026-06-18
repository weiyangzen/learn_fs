# sources/control-plane/beegfs-csi-driver/pkg/beegfs/identityserver.go

Purpose: Implements the CSI Identity service for the BeeGFS driver. It returns plugin metadata, basic liveness probe response, and plugin capability declarations.

Important APIs/types/functions: `identityServer` stores driver `name` and `version` and embeds `csi.UnimplementedIdentityServer`. `newIdentityServer` constructs it. `GetPluginInfo` validates that name and version are configured before returning them. `Probe` returns an empty healthy response. `GetPluginCapabilities` advertises `CONTROLLER_SERVICE` and online volume expansion.

Control flow: Calls are simple request-response handlers. `GetPluginInfo` logs at debug level, returns `Unavailable` if either field is empty, and otherwise returns a `GetPluginInfoResponse`. Capabilities are assembled inline as CSI protobuf structures.

State and persistence: No persistence. State is immutable server metadata set at construction.

Dependencies and integration points: Registered by `server.go` into the gRPC server. Consumed by CSI sidecars and orchestrators during driver discovery. Uses gRPC status codes and the shared logging helpers.

Risks: Capability declarations must stay aligned with controller behavior; online volume expansion is advertised because `ControllerExpandVolume` returns a metadata-only success and `NodeExpandVolume` is unimplemented. Empty string validation makes misconfigured builds fail discovery clearly.

Test signals: Covered indirectly by CSI sanity tests. There is no dedicated identity unit test in this subset.
