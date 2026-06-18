# sources/control-plane/ceph-csi/internal/nvmeof/identity/identityserver.go

Purpose: Implements the NVMe-oF CSI Identity service by wrapping the default identity server and overriding plugin capability reporting.

Important APIs/types/functions: `Server` embeds `*csicommon.DefaultIdentityServer`; `NewIdentityServer` constructs it; `GetPluginCapabilities` reports controller service and online volume expansion support.

Control flow: Capability response is static and independent of request content. Other identity methods are inherited from `DefaultIdentityServer`.

State and persistence behavior: No persistent state beyond the embedded driver metadata.

Dependencies and integration points: Used by the NVMe-oF driver startup. Depends on CSI protobufs and common identity server implementation.

Risks: Capability reporting must stay aligned with controller/node advertised capabilities. If online expansion behavior changes, this static response must be updated.

Test signals: No direct tests in this subset.
