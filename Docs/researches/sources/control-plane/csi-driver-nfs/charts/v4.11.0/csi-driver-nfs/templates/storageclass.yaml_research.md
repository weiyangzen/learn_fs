# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/storageclass.yaml

Purpose: 4.11.0 optional single StorageClass.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; values for create, name, annotations, parameters, reclaim policy, binding mode, mount options, and driver name.

Control flow: Renders on `storageClass.create`; includes labels, an annotations section, optional parameters/mountOptions, and fixed `allowVolumeExpansion: true`.

State and persistence: Cluster storage provisioning policy.

Dependencies and integration points: External provisioner/resizer and NFS driver parameters/secrets.

Risks: Bad parameters or default annotations can affect PVC provisioning cluster-wide. Test signals: render with realistic NFS parameters and perform PVC create/resize/delete.
