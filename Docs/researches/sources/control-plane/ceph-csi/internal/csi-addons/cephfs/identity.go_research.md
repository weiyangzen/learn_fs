# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/identity.go

Purpose: CSI-addons identity service implementation for the CephFS driver.

Important APIs/types/functions: `IdentityServer` embeds `identity.UnimplementedIdentityServer` and stores `*util.Config`. `NewIdentityServer()`, `RegisterService()`, `GetIdentity()`, `GetCapabilities()`, and `Probe()` implement the service.

Control flow: registration binds the server to a gRPC registrar. `GetIdentity()` returns configured driver name and `util.DriverVersion`. `GetCapabilities()` builds capabilities based on process role: controller mode advertises controller service and network fence; node mode advertises network fence get-clients. `Probe()` always returns ready true.

State and persistence: stateless apart from the immutable config pointer. No backend calls are made.

Dependencies and integration points: integrates CSI-addons identity protobufs, gRPC registration, and Ceph-CSI runtime config. Capabilities gate what CSI-addons sidecars/operators expect from CephFS endpoints.

Risks: capability accuracy depends on `IsControllerServer` and `IsNodeServer` config. There is no nil-config guard, so construction must pass a valid config. Probe is optimistic and does not check backend readiness.

Test signals: no direct tests here. Useful tests would validate exact capability sets for controller-only, node-only, combined, and neither-role configurations.
