## sources/control-plane/csi-driver-iscsi/pkg/iscsi/identityserver.go

Purpose: implements CSI identity service for plugin discovery, probe, and plugin capabilities.

Control flow in `GetPluginInfo` validates driver name and version and returns them; `Probe` returns an empty success response; `GetPluginCapabilities` returns `CONTROLLER_SERVICE`. State is read-only driver metadata.

Dependencies are CSI types, gRPC status codes, and klog. Risks include advertising controller service even though controller RPCs are unimplemented, and no health details in `Probe`. Test signal comes from csi-sanity/registration behavior; no unit tests are listed.
