<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml

- Purpose: Kerberos-enabled StorageClass example for dynamically provisioning SMB volumes with `sec=krb5`, sealed SMB traffic, and Kerberos credential secrets.
- Important APIs/types/functions: Kubernetes APIs `storage.k8s.io/v1`; kinds `StorageClass`; notable images `none`; names include `smb-krb5`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Kerberos options require node keytab/cache setup and correct secret material; `nosuid`/`noexec` are security hardening choices but may break workloads; wrong `cruid` or cache path causes mount failures.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml -->
