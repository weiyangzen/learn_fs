# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI config ConfigMap for RBD deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config`, `config.json: []`.

Control flow: RBD pods mount it and require real cluster monitor/config entries before use.

State and persistence behavior: Kubernetes ConfigMap state.

Dependencies and integration points: mounted by RBD nodeplugin and provisioner manifests.

Risks: empty default is nonfunctional; generated file should be changed through `api/deploy` sources.

Test signals: RBD driver config loading and provisioning/mount tests.
