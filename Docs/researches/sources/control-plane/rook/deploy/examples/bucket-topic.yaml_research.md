
# sources/control-plane/rook/deploy/examples/bucket-topic.yaml

Purpose: defines a sample `CephBucketTopic` named `my-topic` that routes RGW bucket notifications to an HTTP endpoint, with commented examples for AMQP and Kafka.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephBucketTopic`, `spec.objectStoreName`, `objectStoreNamespace`, `opaqueData`, `persistent`, and `endpoint.http.uri`, `disableVerifySSL`, `sendCloudEvents`. Commented fields document AMQP/Kafka `uri`, `ackLevel`, `exchange`, `useSSL`, and `mechanism`.

Control flow: Rook reconciles the topic CR in the application namespace and programs RGW notification topic configuration for object store `my-store` in namespace `rook-ceph`. Notifications referencing `my-topic` then publish to the configured endpoint.

State and persistence: the CR persists desired topic state. `persistent: false` indicates transient topic behavior in RGW rather than a durable queue managed by this manifest.

Dependencies/integration: integrates with `bucket-notification.yaml`, the nginx endpoint example, the target CephObjectStore, and RGW notification compatibility.

Risks: `disableVerifySSL: true` is unsafe for HTTPS production endpoints. Object store name/namespace must match an existing RGW. Non-persistent topics may lose events if the endpoint is unavailable.

Test signals: verify CR status after apply, confirm RGW topic creation, curl the HTTP endpoint from the RGW network path, and run object create/copy tests that trigger the paired notification.
