# sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/nodeserver.go

Purpose: Implements the NVMe-oF CSI Node service: connects NVMe-oF subsystems, stages filesystem/block devices, publishes bind mounts, unstages and disconnects controllers when safe, and performs filesystem resize.

Important APIs/types/functions: `NodeServer` holds default node server, per-volume locks, `NVMeInitiator`, DH-CHAP kernel support status, security manager, node ID, `MountCache`, and `GroupLock`. CSI methods include `NodeGetCapabilities`, `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, and `NodeExpandVolume`. Helpers include `getNvmeConnection`, `connectToSubsystem`, `stageTransaction`, rollback, mount path creation, staging mount, mount-cache initialization, and path/device lookup.

Control flow: Construction loads `nvme_tcp`, verifies `/dev/nvme-fabrics`, records DH-CHAP kernel support, and initializes mounted-device cache from `findmnt`. Stage validates and locks, prevents stage/unstage interleaving with GroupLock group A, skips already mounted paths, parses controller-provided contexts, connects to listeners, creates staging path, mounts/formats the device, and caches the mounted device. Publish validates service-account restrictions, creates target file/dir, and bind mounts from staging path. Unstage locks GroupLock group B, resolves device from cache or `findmnt`, unmounts/removes staging path, updates cache, and calls `DisconnectIfLastMount`. Expand finds the device backing staging path and runs filesystem resize for filesystem volumes only.

State and persistence behavior: Persistent state is external: kernel NVMe connections, mount table, filesystem formatting, and CSI staging/target paths. In-memory state is lock maps and mount cache reconstructed at startup. CSI volume/publish context from controller is required for stage.

Dependencies and integration points: Depends on csi-common validation/mount option helpers, `internal/nvmeof` initiator and listener data, NVMe-oF utility mount discovery, Kubernetes service account restriction helpers, kernel-version utilities, mount-utils resize/format logic, and node security setup.

Risks: Mount cache is 1:1 by device and staging path; multipath or unusual device aliases could challenge disconnect decisions. GroupLock allows parallel staging operations and parallel unstaging operations, so shared initiator command behavior must be safe. `getNvmeConnection` requires HostNQN in publish context, coupling stage to successful ControllerPublish. DH-CHAP with older kernels fails staging as InvalidArgument. `os.Remove` expects staging path to be empty after unmount.

Test signals: This file lacks direct node-server unit tests in the subset. Related utility tests cover mount source parsing and mount cache behavior; integration coverage is needed for real mount and NVMe operations.
