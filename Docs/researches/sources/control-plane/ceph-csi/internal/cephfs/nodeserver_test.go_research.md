## sources/control-plane/ceph-csi/internal/cephfs/nodeserver_test.go

Purpose: Unit tests for CephFS node mount option resolution.

Important flow: `Test_setMountOptions` writes a temporary JSON CSI config containing cluster-specific kernel/fuse mount options, constructs test cases for config vs CLI precedence across kernel and FUSE mounters, initializes a default node server, calls `setMountOptions`, and checks expected options are present.

State and dependencies: Uses a temp config file and in-memory `VolumeOptions`; no real mounts or Ceph connections. Depends on Kubernetes deploy API types, mounter constructors, csi-common server defaults, and JSON config parsing helpers.

Risks and signal: Confirms cluster config overrides CLI options and CLI options are used when config is empty. It does not test read-affinity options, read-only access mode injection, invalid config, or full stage/publish behavior. One test name appears mismatched to cluster setup, but the assertions check resulting option content.
