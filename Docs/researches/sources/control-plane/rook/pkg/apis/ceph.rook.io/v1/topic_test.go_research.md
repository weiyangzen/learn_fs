# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic_test.go

Purpose: tests bucket topic endpoint validation for HTTP, AMQP, Kafka, multiple endpoints, and missing endpoint specs.

Important APIs/types/functions: exercises `CephBucketTopic.ValidateTopicSpec` and, through it, `ValidateHTTPSpec`, `ValidateAMQPSpec`, `ValidateKafkaSpec`, and `validateURI`. Fixtures use `CephBucketTopic`, `BucketTopicSpec`, `TopicEndpointSpec`, `HTTPEndpointSpec`, `AMQPEndpointSpec`, and `KafkaEndpointSpec`.

Control flow: HTTP tests start with a valid `http://` URI, then mutate to an invalid host with a space, a valid `https://` URI, and an invalid `kaboom://` scheme. AMQP tests cover valid `amqp://`, valid `amqps://`, and invalid `http://`. Kafka tests cover valid `kafka://` and invalid `http://`. The invalid-topic test starts with both Kafka and AMQP endpoints, expects a multiple-endpoint error, removes AMQP and expects success, then removes Kafka and expects a missing-endpoint error.

State and persistence: local topic structs only; no persistence.

Dependencies/integration: depends on testify and Kubernetes `metav1`. These tests protect CRD validation behavior before bucket notification topics are reconciled to RGW.

Risks: tests mutate the same topic object across subtests, making order significant within each parent test. They do not validate empty hosts for otherwise valid schemes, Kafka SSL option consistency, AMQP exchange/ack fields, or exact error messages.

Test signals: focused coverage for endpoint cardinality and URI scheme matching.
