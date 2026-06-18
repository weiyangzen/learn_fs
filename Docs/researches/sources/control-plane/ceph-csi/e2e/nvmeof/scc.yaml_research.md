# sources/control-plane/ceph-csi/e2e/nvmeof/scc.yaml

Purpose: grants OpenShift SecurityContextConstraints needed by the temporary NVMe-oF gateway service account.

Important APIs/types/functions: defines a `security.openshift.io/v1 SecurityContextConstraints` named `ceph-nvmeof` allowing privileged containers, host networking, host ports, `SYS_ADMIN`, `RunAsAny`, `seLinuxContext RunAsAny`, broad volume types, and user `system:serviceaccount:rook-ceph:ceph-nvmeof-gateway`.

Control flow: `createORDeleteGateway()` applies this resource only when `isOpenShift` is true and rewrites the service-account namespace marker if `rookNamespace` differs.

State and persistence: persists a cluster-scoped SCC granting elevated privileges to the gateway SA until gateway teardown deletes it.

Dependencies and integration points: tied to `serviceaccount.yaml` and `deployment.yaml`; OpenShift clusters require it for privileged SPDK/NVMe-oF gateway operation.

Risks: it grants powerful privileges and host networking/ports. The comment says "ssc" but resource is SCC. Namespace/user replacement must stay aligned with the service account namespace.

Test signals: on OpenShift, gateway pod admission succeeds instead of failing SCC validation, and teardown removes the SCC.
