# sources/control-plane/ceph-csi/e2e/nvmeof-gateway.go

Purpose: deploys the temporary NVMe-oF gateway used by the NVMe-oF e2e suite and exposes the gateway pod identity/IP for StorageClass configuration.

Important APIs/types/functions: constants point to gateway YAML files under `e2e/nvmeof/`. `createORDeleteGateway(action)` applies optional OpenShift SCC plus ServiceAccount, ConfigMap, and Deployment in `rookNamespace`. `deployGateway(f, deployTimeout)` creates the backing pool, applies resources, waits for the gateway Deployment and pod, and dumps container logs if startup fails. `deleteGateway(f)` removes resources and deletes the pool. `getNVMeofGateway(c)` returns the single gateway pod name and pod IP.

Control flow: deployment first creates the `nvmeofPool`, applies templates, waits for Deployment availability, finds the pod by `app=ceph-nvmeof-gateway`, and waits for Running. On pod wait failure, it fetches logs from `generate-minimal-ceph-conf` and `nvmeof-gateway` before asserting failure. Deletion removes YAML resources then deletes the pool.

State and persistence: creates a Ceph pool, Kubernetes ServiceAccount, ConfigMap, Deployment, optional SCC, and gateway pod in the Rook namespace. The gateway registers itself with Ceph through its init container.

Dependencies and integration points: uses generic resource deployers, pool helpers, pod/deployment wait helpers, Kubernetes pod logs, global `rookNamespace`, `isOpenShift`, and `nvmeofPool`. `createNVMeoFStorageClass()` consumes the gateway pod IP returned here.

Risks: the helper expects exactly one gateway pod. There is no Kubernetes Service abstraction here, so tests depend on the pod IP staying valid. Pool deletion after gateway removal can fail if backend objects remain. SCC namespace replacement assumes the YAML contains `:rook-ceph:`.

Test signals: pool creation, gateway Deployment availability, pod Running, usable gateway IP in StorageClass, and successful pool deletion during teardown.
