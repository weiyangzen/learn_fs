# sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace.go

Purpose: CSI-addons reclaim space implementation for RBD, supporting offline controller-side sparsify and online node-side filesystem trim.

Important APIs/types/functions: `ReclaimSpaceControllerServer` exposes `ControllerReclaimSpace()` with driver instance and volume locks. `ReclaimSpaceNodeServer` exposes `NodeReclaimSpace()` with volume locks. Constructors and `RegisterService()` functions bind both services.

Control flow: controller reclaim validates volume ID, locks by ID, resolves the RBD volume through a manager, calls `Sparsify()`, treats `ErrImageInUse` as a no-op success, and maps other failures to gRPC errors. Node reclaim validates ID, locks, selects staging target path plus `/<volumeID>` or volume path, rejects multi-node capabilities and all block mode, then executes `fstrim <path>`.

State and persistence: controller-side effects are RBD image sparsification. Node-side effects are filesystem discard/TRIM on a mounted path. No local state is persisted. Locks prevent concurrent reclaim for the same volume in-process.

Dependencies and integration points: depends on CSI-addons reclaimspace protobufs, common CSI capability helpers, RBD manager/volume APIs, common command execution, and error sentinels. Identity advertises offline reclaim on controller and online reclaim on node.

Risks: `ErrImageInUse` is intentionally swallowed due to CSI-addons behavior, so offline reclaim may report success without space recovery. Node path construction assumes the driver's staging layout. Multi-node and block-mode rejection prevents corruption but may surprise users. `fstrim` availability and permissions are host-dependent.

Test signals: minimal tests cover invalid empty requests. Additional tests should cover path selection, multi-node/block rejection, lock contention, in-use no-op behavior, and command execution failures.
