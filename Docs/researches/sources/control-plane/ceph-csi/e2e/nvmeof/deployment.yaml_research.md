# sources/control-plane/ceph-csi/e2e/nvmeof/deployment.yaml

Purpose: deploys the temporary `ceph-nvmeof-gateway` workload used by e2e tests to expose RBD images over NVMe-oF.

Important APIs/types/functions: defines an `apps/v1 Deployment` with one replica, label `app=ceph-nvmeof-gateway`, main container `nvmeof-gateway` using `quay.io/ceph/nvmeof:1.5`, and init container `generate-minimal-ceph-conf` using `quay.io/ceph/ceph:v19`. It exposes TCP ports 4420, 5500, 5499, and 8009 and uses service account `ceph-nvmeof-gateway`.

Control flow: the init container reads monitor host from `rook-ceph-config`, writes `/etc/ceph/ceph.conf`, copies the admin keyring, renders `/etc/ceph/nvmeof.conf` from the ConfigMap template, and registers the gateway with `ceph nvme-gw create ${POD_NAME} nvmeofpool ${ANA_GROUP}` followed by `show`. The main container starts the gateway with the rendered config.

State and persistence: uses an `emptyDir` for generated `/etc/ceph`, a Secret volume for `rook-ceph-admin-keyring`, and a projected ConfigMap volume for gateway config. It registers gateway state in Ceph for `nvmeofpool`.

Dependencies and integration points: depends on Rook Secrets/ConfigMap, the `ceph-nvmeof-config` ConfigMap, the `ceph-nvmeof-gateway` ServiceAccount, and privileged container permissions. The e2e gateway helper waits on this Deployment and uses the resulting pod IP.

Risks: both init and main containers run privileged; admin keyring is mounted into the pod. Image tags are fixed and can drift from cluster Ceph version. There is no Service, so pod IP volatility matters. The init container hard-codes `nvmeofpool` and depends on `ceph nvme-gw` CLI availability.

Test signals: Deployment available, pod running, init logs showing rendered config and successful `ceph nvme-gw show`, open listener ports, and successful CSI provisioning through the gateway.
