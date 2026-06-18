# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI config ConfigMap for NFS deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config`, `config.json: []`.

Control flow: NFS driver pods mount this and expect operators to populate cluster entries including NFS network namespace config when needed.

State and persistence behavior: Kubernetes ConfigMap state only.

Dependencies and integration points: mounted by NFS provisioner and nodeplugin manifests.

Risks: empty default prevents functional provisioning/mounts. Generated file should be changed at source rather than edited here.

Test signals: NFS CSI driver startup and provisioning tests.
