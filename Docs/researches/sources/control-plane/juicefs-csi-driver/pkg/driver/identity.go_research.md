# sources/control-plane/juicefs-csi-driver/pkg/driver/identity.go

Purpose: implements the CSI Identity service for the JuiceFS CSI driver.

Important APIs and functions: `GetPluginInfo` returns `config.DriverName` and the build-time `driverVersion`. `GetPluginCapabilities` advertises `CONTROLLER_SERVICE`. `Probe` returns an empty successful response.

Control flow: all methods are simple request logging plus deterministic response construction. No validation, health check, or external dependency is involved.

State and persistence behavior: no mutable state is changed. The only data read is package/global configuration and build metadata.

Dependencies and integration points: uses CSI protobuf types, klog, and `config.DriverName`. These methods are registered by `Driver.Run` and are called by the container orchestrator during CSI discovery.

Risks and test signals: `Probe` does not verify node/controller readiness or backend health, so it only signals that the gRPC process can answer. Tests assert exact responses for plugin info, capabilities, and probe.
