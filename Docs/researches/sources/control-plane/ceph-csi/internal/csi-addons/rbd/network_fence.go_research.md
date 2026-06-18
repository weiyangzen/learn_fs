# sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence.go

Purpose: RBD CSI-addons fence controller facade. It validates network fence requests and delegates blocklist/get-client behavior to the shared networkfence package.

Important APIs/types/functions: `FenceControllerServer` with `enableFencing`, `NewFenceControllerServer()`, `RegisterService()`, `FenceClusterNetwork()`, `UnfenceClusterNetwork()`, `GetFenceClients()`, and local `validateNetworkFenceReq()`.

Control flow: fence/unfence validate non-empty CIDR list and `clusterID`, create user credentials, construct `networkfence.NetworkFence`, and call `AddNetworkFence()` or `RemoveNetworkFence()`. `GetFenceClients()` delegates to shared code with the auto-fencing flag.

State and persistence: no local state beyond the enable flag. Backend state changes are Ceph OSD blocklist entries. Credentials create temporary files and are deleted after RPC execution.

Dependencies and integration points: integrates CSI-addons fence protobufs, shared networkfence, common credentials, and gRPC status codes. Unlike CephFS, RBD fencing does not evict MDS clients and uses user credentials for explicit fence calls.

Risks: same validation limitations as CephFS wrapper; CIDR syntax is not checked until shared code. `NewUserCredentials()` errors in fence map to `Internal`, while unfence maps credential errors to `InvalidArgument`, an inconsistency that callers may observe. Large CIDR fallback risks live in the shared package.

Test signals: wrapper tests assert invalid requests return errors. More coverage should verify credential error code consistency and shared package invocation.
