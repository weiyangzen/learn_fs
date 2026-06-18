# sources/control-plane/ceph-csi/internal/csi-common/identityserver-default.go

Purpose: default CSI identity server implementation shared by Ceph-CSI drivers.

Important APIs/types/functions: `DefaultIdentityServer` embeds `csi.UnimplementedIdentityServer` and stores `*CSIDriver`. Methods are `GetPluginInfo()`, `Probe()`, and `GetPluginCapabilities()`.

Control flow: `GetPluginInfo()` logs and returns driver name/version, rejecting empty values with `Unavailable`. `Probe()` returns an empty response. `GetPluginCapabilities()` always advertises controller service capability.

State and persistence: reads in-memory driver metadata only.

Dependencies and integration points: registered on CSI gRPC servers for all drivers using common identity behavior. The plugin capability influences CO expectations for controller service availability.

Risks: no nil-driver guard before dereferencing `ids.Driver`. Probe does not verify backend readiness. Always advertising controller service may be inappropriate if a node-only deployment uses this default without override.

Test signals: no direct tests. Useful tests would cover missing name/version, nil driver behavior, and plugin capability assumptions.
