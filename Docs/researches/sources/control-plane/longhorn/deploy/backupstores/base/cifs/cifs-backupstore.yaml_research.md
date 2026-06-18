# sources/control-plane/longhorn/deploy/backupstores/base/cifs/cifs-backupstore.yaml

Purpose: provides a Kustomize base for a test CIFS/Samba backupstore and placeholder credentials in both Longhorn and workload namespaces.

Important APIs/types/functions: two `Secret` objects named `cifs-secret` in `longhorn-system` and `default`, `Deployment` `longhorn-test-cifs`, image `chanow/samba:latest`, ports 139/445, env vars `EXPORT_PATH`, `CIFS_DISK_IMAGE_SIZE_MB`, `CIFS_USERNAME`, `CIFS_PASSWORD`, privileged security context with `SYS_ADMIN` and `DAC_READ_SEARCH`, `emptyDir` volume mounted at `/opt/backupstore`, Samba args, and headless `Service` `longhorn-test-cifs-svc`.

Control flow: applying the manifest creates empty secrets, starts one privileged Samba container, reads username/password from the default-namespace secret, exports `/opt/backupstore` as share `backupstore`, and exposes SMB ports through a headless service.

State and persistence: backup data is stored on `emptyDir`, so it is ephemeral per pod lifecycle. Secrets persist but start empty and must be populated with base64 credentials.

Dependencies/integration: depends on the Samba image behavior and secret keys `CIFS_USERNAME` and `CIFS_PASSWORD`. Longhorn must be configured to use the CIFS endpoint and the `longhorn-system` credential secret. The default namespace secret is needed by the Samba server pod itself.

Risks: `chanow/samba:latest` and `imagePullPolicy: Always` make test behavior non-reproducible. The container is privileged with elevated capabilities. Empty credentials block startup or login. Headless service and SMB ports may behave differently across clusters and network policies.

Test signals: populate both secrets, apply the kustomization, confirm Samba listens on 139/445, configure Longhorn CIFS backup target, create/restore a backup, and verify data loss after pod recreation due to `emptyDir`.
