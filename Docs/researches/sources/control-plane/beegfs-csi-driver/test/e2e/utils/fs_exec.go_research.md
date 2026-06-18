<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go

Purpose: encapsulates creating a dynamic BeeGFS volume and pod so tests can execute commands on the host node where that volume is mounted.
Important APIs/types/functions: `FSExec`, `FSMountData`, `FindmntData`, `NewFSExec`, `GetVolumeSHA256Checksum`, `GetVolumeHostMountInfo`, `IssueCtlCommandWithBeegfsPathArgs`, `IssueCommandWithBeegfsPaths`, `IssueCommandWithResult`, and `Cleanup`.
Control flow/state: creates a volume resource, launches a pod consuming it, determines host mount paths by parsing `findmnt -J -t beegfs`, supports both SHA256 CSI staging paths and older PV-name paths, then routes commands through Kubernetes `HostExec`. Cleanup deletes pod, volume resource, and host exec artifacts.
Dependencies/integration: depends on Kubernetes storage e2e helpers, BeeGFS command-line utilities on the node PATH or plugin client path, JSON parsing of findmnt output, and kubelet CSI mount layout.
Risks/test signals: command format strings interpolate paths and should not receive untrusted input; failure during `CreateVolumeResource` can leak non-namespaced objects; mount detection assumes `source == beegfs_nodev` filters bind mounts. Tests using it signal via command stdout/stderr and cleanup aggregate errors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go -->
