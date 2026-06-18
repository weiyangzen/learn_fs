# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI cluster config ConfigMap for CephFS static deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config` with `data.config.json: []`.

Control flow: operators replace or patch this list with cluster monitor information before driver use.

State and persistence behavior: Kubernetes ConfigMap; stores cluster connection metadata, not credentials.

Dependencies and integration points: mounted by CephFS nodeplugin/provisioner pods and generated from `api/deploy`.

Risks: empty default makes the deployment nonfunctional until configured. Direct edits may be overwritten by yamlgen.

Test signals: driver config loading and provisioning failures/successes.
