<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml

## Purpose
`services.yaml` deploys simple Redis and MinIO dependencies into the default namespace for JuiceFS CSI Driver e2e tests.

## Important APIs, Types, and Functions
It defines two headless Services, `redis` on port 6379 selecting `app: redis-server` and `minio` on port 9000 selecting `app: minio-server`. It also defines one-replica StatefulSets `redis-server` and `minio-server`. Redis uses image `redis` with `/data` mounted from hostPath `/data/redis`; MinIO uses image `minio/minio`, args `server /data`, and hostPath `/data/minio`.

## Control Flow, State, and Persistence
Applying the YAML creates services and stateful pods. Persistence is hostPath-backed on the MicroK8s node under `/data/redis` and `/data/minio`, so data may survive pod recreation on the same runner unless the host path is cleaned.

## Dependencies and Integration Points
It depends on Kubernetes apps/v1 and core/v1 APIs, image pulls from Docker registries, writable host paths, and MicroK8s scheduling. `k8s-deps.sh` applies this file and then waits for pod IPs and TCP ports before e2e tests continue.

## Risks and Test Signals
Risks include unpinned images, no resource limits, no readiness probes, no MinIO credentials in this manifest, and hostPath state leakage between CI runs. Signals are StatefulSet pod IP assignment, TCP availability on 6379 and 9000, and service DNS resolution through the MicroK8s DNS setup.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml -->
