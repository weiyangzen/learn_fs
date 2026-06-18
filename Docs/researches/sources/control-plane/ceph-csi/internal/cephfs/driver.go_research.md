## sources/control-plane/ceph-csi/internal/cephfs/driver.go

Purpose: Initializes and runs the CephFS CSI driver, including identity, controller, node, group controller, journals, mounters, topology, read affinity, and CSI-Addons server.

Important types/functions: `cephfsDriver`, `NewDriver`, `NewIdentityServer`, `NewControllerServer`, `NewNodeServer`, `Run`, and `setupCSIAddonsServer`.

Control flow: `Run` loads available mounters, sets the CephFS RADOS namespace, reads node labels/topology/read-affinity inputs, initializes volume/snapshot/group journals, constructs the CSI driver and capabilities, creates requested servers based on config, starts CSI-Addons, then starts the nonblocking gRPC server. Controller capabilities include create/delete volume/snapshot, expand, clone, single-node multi-writer, publish/unpublish, and group snapshots.

State and persistence: Initializes global journal configs in `store` and process-local server state/locks. Persistent cluster state is created later by request handlers.

Dependencies and risks: Depends on mounter probing, Kubernetes helpers, CSI common server, health checker, journal package, CSI-Addons CephFS services, and config feature gates. Fatal logging is used for startup failures. Test coverage verifies CSI-Addons socket creation but not full driver startup. Risks include mounter availability, topology config errors, and global journal state coupling.
