# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence_test.go

Purpose: minimal smoke tests for CephFS CSI-addons network fence RPC validation.

Important APIs/types/functions: `TestFenceClusterNetwork()` and `TestUnfenceClusterNetwork()` instantiate `NewFenceControllerServer(true)` and call RPCs with empty parameters, nil secrets, and nil CIDRs.

Control flow: both tests expect an error before any Ceph backend work is attempted, relying on `validateNetworkFenceReq()` to reject empty CIDRs/missing cluster ID.

State and persistence: no Ceph state, no filesystem state, and no socket state. Tests run fully in memory.

Dependencies and integration points: verifies the CephFS wrapper rejects malformed CSI-addons fence requests without needing a cluster.

Risks: tests do not validate successful request construction, admin credential handling, shared network fence calls, auto-unfence get-client behavior, or exact gRPC status codes.

Test signals: useful as a low-cost guard against accidentally accepting empty fence/unfence requests. It is not a behavioral test for fencing.
