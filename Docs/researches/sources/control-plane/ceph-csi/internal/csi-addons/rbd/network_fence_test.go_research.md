# sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence_test.go

Purpose: minimal smoke tests for RBD CSI-addons fence and unfence request validation.

Important APIs/types/functions: `TestFenceClusterNetwork()` and `TestUnfenceClusterNetwork()` instantiate `NewFenceControllerServer(true)` and send empty requests.

Control flow: both tests expect errors from validation before credentials or Ceph calls are reached.

State and persistence: none; all objects are in-memory protobufs.

Dependencies and integration points: protects the RBD fence wrapper from accepting empty CIDR/parameter requests.

Risks: does not inspect gRPC status codes or successful paths. It does not cover `GetFenceClients()`, credential handling, or shared networkfence behavior.

Test signals: basic invalid-input guard only.
