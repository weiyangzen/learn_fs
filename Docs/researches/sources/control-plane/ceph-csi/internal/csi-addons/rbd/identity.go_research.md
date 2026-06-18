# sources/control-plane/ceph-csi/internal/csi-addons/rbd/identity.go

Purpose: CSI-addons identity service implementation for the RBD driver, advertising RBD-specific addon capabilities.

Important APIs/types/functions: `IdentityServer` stores `*util.Config` and implements `NewIdentityServer()`, `RegisterService()`, `GetIdentity()`, `GetCapabilities()`, and `Probe()`.

Control flow: `GetIdentity()` returns driver name and `util.DriverVersion`. `GetCapabilities()` appends controller capabilities when `IsControllerServer` is true: controller service, offline reclaim space, network fence, volume replication, volume group, do-not-delete-volume-group-volumes, one-group limit, modify volume group, and get volume group. When `IsNodeServer` is true it appends node service, online reclaim space, encryption key rotation, and get-clients-to-fence. Probe always reports ready.

State and persistence: stateless except config. No Ceph connection is attempted.

Dependencies and integration points: integrates CSI-addons identity API and controls what external CSI-addons operators attempt against the RBD controller/node sockets.

Risks: advertised capability drift is high impact because operators may call unsupported RPCs or miss supported ones. Probe is not a backend health check. Nil config is not guarded.

Test signals: no direct tests here. Useful tests should snapshot controller/node capability lists and ensure future changes are intentional.
