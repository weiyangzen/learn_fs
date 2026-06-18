## sources/control-plane/ceph-csi/internal/cephfs/identityserver.go

Purpose: CephFS CSI identity server implementation for plugin capability discovery.

Important API: `IdentityServer` embeds `DefaultIdentityServer`; `GetPluginCapabilities` returns controller service, online volume expansion, and group controller service plugin capabilities.

Control flow and state: The method is a pure response builder with no external calls or persistent state. Kubernetes sidecars use these advertised capabilities to decide which controller and expansion operations are available.

Dependencies and risks: Depends on CSI protobuf types and csi-common default identity behavior. Capability mismatch with actual controller registration would confuse sidecars; here it aligns with `driver.go` adding controller/group capabilities. Tests are not present for this file specifically.
