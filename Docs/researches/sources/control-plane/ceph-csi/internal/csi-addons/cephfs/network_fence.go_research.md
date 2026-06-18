# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence.go

Purpose: CephFS CSI-addons fence controller facade. It validates requests, constructs credentials and shared network fence objects, and exposes fence/unfence/get-clients RPCs for CephFS.

Important APIs/types/functions: `FenceControllerServer` stores `enableFencing`. Public functions are `NewFenceControllerServer()`, `RegisterService()`, `FenceClusterNetwork()`, `UnfenceClusterNetwork()`, and `GetFenceClients()`. Local `validateNetworkFenceReq()` checks CIDRs and `clusterID`.

Control flow: fence/unfence reject empty CIDRs or missing cluster ID, create admin credentials from request secrets, construct `networkfence.NetworkFence`, and call either `AddClientEviction()` for fencing or `RemoveNetworkFence()` for unfencing. Get-clients delegates to shared `networkfence.GetFenceClients()` with the server's auto-fencing flag.

State and persistence: no local persistence. Backend effects are CephFS client eviction and OSD blocklist changes performed by the shared networkfence package. Credentials create temporary key files and are deleted with `defer`.

Dependencies and integration points: depends on CSI-addons fence protobufs, gRPC, common credentials, gRPC status codes, and shared `internal/csi-addons/networkfence`. CephFS differs from RBD by using admin credentials and evicting active MDS clients before adding the blocklist.

Risks: validation only checks CIDR presence, not CIDR syntax; syntax errors surface later. Admin credentials are required. `enableFencing` only affects get-clients auto-unfence behavior, not explicit fence/unfence RPCs. Error mapping is mostly `Internal` after validation.

Test signals: tests only verify invalid empty requests return errors. Additional coverage should mock shared fence construction and check credential/error code behavior.
