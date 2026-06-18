# sources/control-plane/csi-driver-nfs/pkg/nfs/nfs.go

Purpose: defines the main NFS CSI driver configuration, runtime state, default capabilities, startup sequence, corruption helper, and metadata replacement helper.

Important APIs and types: `DriverOptions`, `Driver`, constants for parameter names and metadata placeholders, `NewDriver`, `NewNodeServer`, `Run`, `AddControllerServiceCapabilities`, `AddNodeServiceCapabilities`, `IsCorruptedDir`, and `replaceWithMap`.

Control flow: `NewDriver` copies deployment options into a `Driver`, registers default controller capabilities for create/delete, single-node multi-writer, clone, snapshot, and expansion, registers node stats and multi-writer capabilities, initializes volume locks, and creates timed caches for volume stats and deletion idempotency. `Run` logs version metadata, creates a Kubernetes mounter, wraps it with force-unmount support on Linux, constructs the node server, registers identity/controller/node services in a non-blocking gRPC server, and waits.

State and persistence behavior: maintains in-memory driver metadata, CSI capabilities, locks, and timed caches. It does not persist volumes; persistent storage state is represented by NFS directories created by controller/node operations.

Dependencies and integration points: depends on CSI protobufs, `k8s.io/mount-utils`, klog, runtime metadata, and the local timed cache implementation. It is the entry point connecting identity, controller, node, and gRPC server files.

Risks: `Run` fatals on version YAML or server startup failures. Default cache expiry is mutated in local options after some fields have already been copied, while cache construction uses the corrected value. `replaceWithMap` iterates map keys in random order, so overlapping placeholders would be order-dependent.

Test signals: `nfs_test.go` covers fake driver construction, `Run` in test mode, capability constructors, corrupted-dir helper basics, and metadata replacement behavior.
