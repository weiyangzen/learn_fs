# sources/control-plane/juicefs-csi-driver/pkg/driver/node_test.go

Purpose: tests the `nodeService` CSI node implementation using Ginkgo/Gomega and ordinary `testing` cases.

Important APIs and functions: the Ginkgo `Describe("nodeService")` block covers `NodePublishVolume` normal operation, readonly mounts, mount options from volume attributes and capabilities, `JfsMount` errors, `CreateVol` errors, bind errors, target creation errors, missing target, missing capability, invalid capability, and `NodeUnpublishVolume` success/failure/missing target. Later table tests cover `NodeGetCapabilities`, `NodeGetInfo`, `newNodeService`, `NodeExpandVolume`, `NodeGetVolumeStats` invalid input, `NodeStageVolume`, and `NodeUnstageVolume`.

Control flow: tests build a fresh `nodeService` with fake Kubernetes client, metrics, safe mounter, sync map, and volume locks. They use GoMock JuiceFS/Jfs objects to assert exact calls and gomonkey patches for filesystem and exec functions.

State and persistence behavior: uses in-memory fake clients, patched filesystem calls, fake metrics, and local lock state. It does not perform real mounts or disk usage queries in successful stats paths.

Dependencies and integration points: depends on CSI protobufs, GoMock JuiceFS mocks, gomonkey, Ginkgo/Gomega, fake Kubernetes clients, klog context helpers, and resource locks. It validates the node-to-JuiceFS provider boundary and basic CSI response shapes.

Risks and test signals: strong signal for publish/unpublish branching and mount option composition. The tests do not exercise successful `NodeGetVolumeStats`, recently-unmounted suppression, corrupted mount recovery, quota dispatch behavior, or lock contention. Several `It("should succeed")` names actually expect errors, so test names are less precise than assertions.
