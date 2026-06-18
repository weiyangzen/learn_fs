
# sources/control-plane/rook/deploy/examples/bucket-notification-endpoint.yaml

Purpose: provides a simple HTTP endpoint for testing Ceph RGW bucket notifications. It deploys two nginx replicas and exposes them through a NodePort service.

Important APIs/types/functions: Kubernetes `apps/v1` `Deployment`, `v1` `Service`, label selector `run: my-notification-endpoint`, container image `nginx`, container port 80, service port 8080, targetPort 80, protocol TCP, and service type `NodePort`.

Control flow: the Deployment creates nginx pods with matching labels. The Service selects those pods and forwards port 8080 to container port 80 so a `CephBucketTopic` HTTP endpoint can target `http://my-notification-endpoint:8080`.

State and persistence: deployment replica state and service state persist in Kubernetes. The endpoint has no durable application state and is suitable only as a sample notification sink.

Dependencies/integration: integrates with `bucket-topic.yaml`, which references this service URI, and with Kubernetes service discovery in the namespace where both manifests are applied.

Risks: NodePort exposes the endpoint beyond the cluster depending on environment. The generic nginx image does not record or validate notification payloads, so it is weak as an assertion target. Namespace mismatch breaks DNS lookup from RGW.

Test signals: apply the manifest and verify two ready pods, service endpoints, and HTTP 200 from `my-notification-endpoint:8080`. Trigger an RGW notification and confirm delivery attempts reach the service.
