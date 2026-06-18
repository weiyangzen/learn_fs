# sources/control-plane/longhorn/deploy/backupstores/base/nfs/nfs-backupstore.yaml

Purpose: provides a Kustomize base for a test NFS backupstore using the Longhorn NFS backupstore image.

Important APIs/types/functions: `Deployment` `longhorn-test-nfs` in `default`, image `longhornio/nfs-backupstore:latest`, env vars `EXPORT_ID`, `EXPORT_PATH`, `PSEUDO_PATH`, `NFS_DISK_IMAGE_SIZE_MB`, command that chmods `/opt/backupstore` and starts NFS while teeing `/var/log/ganesha.log`, privileged security context with `SYS_ADMIN` and `DAC_READ_SEARCH`, `emptyDir` volumes for backup data and ganesha data, liveness probe checking the log, and headless `Service` `longhorn-test-nfs-svc`.

Control flow: applying the manifest starts one privileged NFS/Ganesha pod, initializes the export path, runs `/opt/start_nfs.sh`, and exposes a headless service. The liveness probe fails if the log reports no export entries.

State and persistence: backup data lives on an `emptyDir` and is lost when the pod is deleted or rescheduled. Ganesha runtime data is also ephemeral. No credential secret is created for NFS.

Dependencies/integration: depends on the `longhornio/nfs-backupstore:latest` image and its startup script. Longhorn must be configured with an NFS backup target pointing to the headless service/export path.

Risks: `latest` with `Always` image pulls is non-reproducible. Privileged NFS server pods may be blocked by cluster policy. The service exposes only a placeholder port 1234, while NFS may rely on pod networking and image-specific behavior, so consumers need the documented endpoint pattern. Ephemeral storage makes it unsuitable for durable backups.

Test signals: apply the base, inspect pod logs for exported path, verify liveness remains healthy, configure Longhorn NFS backup target, run backup/restore, and confirm backup loss after pod recreation.
