<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go

Purpose: shared e2e helpers for pod log archival, mount leak checks, pod discovery, permission validation, pool-id selection, and PVC creation without framework assertions.
Important APIs/functions: `VerifyDirectoryModeUidGidInPod`, `VerifyNoOrphanedMounts`, `ArchiveServiceLogs`, `AppendBytesToFile`, `GetRunningControllerPod`, `GetRunningNodePods`, `GetUnusedPoolId`, `ContainsString`, and `CreatePVCFromStorageClass`.
Control flow/state: many helpers fail tests directly through e2e framework assertions. Log archival appends pod logs to report files; orphan checks SSH to ready schedulable nodes and fails if BeeGFS mounts under kubelet remain; PVC creation returns errors so negative tests can inspect provisioning failure.
Dependencies/integration: Kubernetes e2e node/pod/PV/volume/SSH packages, client-go, labels `app=csi-beegfs-controller` and `app=csi-beegfs-node`, and report directory state.
Risks/test signals: `VerifyDirectoryModeUidGidInPod` assumes `ls -ld` field order; orphan checks require SSH provider and more than one ready node; appending logs can accumulate repeated entries. Test signals are explicit framework failures and report log files.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go -->
