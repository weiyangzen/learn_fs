# sources/control-plane/ceph-csi/deploy/ceph-conf.yaml

Purpose: static sample ConfigMap for Ceph client configuration consumed by CSI pods.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-config`; `data.ceph.conf` contains cephx auth requirements and commented debug logging options; `data.keyring` is intentionally empty but present.

Control flow: static deploy manifests mount this ConfigMap under `/etc/ceph/` for nodeplugin and provisioner pods.

State and persistence behavior: Kubernetes ConfigMap persists client configuration; no secrets are stored here.

Dependencies and integration points: consumed by RBD, CephFS, and provisioner deployments; pairs with `ceph-csi-config` and Secrets for full connectivity.

Risks: debug logging comments can be enabled and produce high-volume logs. Missing `keyring` can break clients even if empty content is expected.

Test signals: driver pod startup and Ceph client connection attempts validate the file.
