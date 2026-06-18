# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-config-map.yaml

Purpose: empty Ceph-CSI cluster config ConfigMap for NVMe-oF deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config` with `config.json: []`.

Control flow: NVMe-oF pods mount it and require real cluster/gateway configuration before use.

State and persistence behavior: Kubernetes ConfigMap state.

Dependencies and integration points: mounted by NVMe-oF node and provisioner manifests.

Risks: empty default is nonfunctional. Unlike generated files with comments, this file has no "do not modify" header, so ownership may be less obvious.

Test signals: NVMe-oF driver config loading and provisioning/mount tests.
