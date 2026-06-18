# sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver_test.go

Purpose: validates CSI Identity service responses and error handling.

Important APIs and helpers: `TestGetPluginInfo`, `TestProbe`, and `TestGetPluginCapabilities` use `NewEmptyDriver` to create normal, empty-name, and empty-version driver states.

Control flow: plugin info cases call `GetPluginInfo` and compare expected gRPC errors for unavailable name or version. Probe asserts a non-nil response with ready=true. Capabilities asserts the single controller-service plugin capability.

State and persistence behavior: entirely in-memory. The tests mutate only the driver metadata used by identity responses.

Dependencies and integration points: depends on CSI types, gRPC status codes, testify assertions, and `nfs_test.go` helpers. It validates what clients see when `server.go` registers the identity service.

Risks: exact equality for capability structs can be sensitive to additional capabilities. It does not exercise server registration or gRPC transport.

Test signals: solid unit signal for the identity server's public CSI contract.
