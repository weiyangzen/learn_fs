# sources/control-plane/rook/deploy/examples/monitoring/prometheus-service.yaml

Purpose: exposes the example Prometheus instance as a Kubernetes `Service` named `rook-prometheus` in `rook-ceph`.

Important APIs/types/functions: `v1/Service` with `type: NodePort`, selector `prometheus: rook-prometheus`, and port `9090` exposed on node port `30900` targeting named container port `web`.

Control flow: Kubernetes routes traffic from node port 30900 to pods created by the Prometheus Operator for the `rook-prometheus` CR.

State and persistence: no durable state; it is a service routing object whose endpoints are derived from matching Prometheus pods.

Dependencies/integration: requires the Prometheus CR in `prometheus.yaml` to create pods with the matching label and a named `web` port.

Risks: fixed NodePort can conflict with cluster policy or another service, and NodePort exposes Prometheus broadly on every node unless network policy constrains it.

Test signals: service creation dry-run, endpoint population, and HTTP reachability to `/graph` or `/-/ready` through node port 30900.
