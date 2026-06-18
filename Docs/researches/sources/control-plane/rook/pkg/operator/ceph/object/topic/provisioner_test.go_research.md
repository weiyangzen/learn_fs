# sources/control-plane/rook/pkg/operator/ceph/object/topic/provisioner_test.go

Purpose: this test file validates `createTopicAttributes` for the three supported Ceph bucket topic endpoint families: HTTP, AMQP, and Kafka.

Important test cases: `TestTopicAttributesCreation` defines common string constants and runs subtests for HTTP, AMQP, and Kafka. Each subtest creates a `CephBucketTopic` with endpoint-specific spec fields, calls `createTopicAttributes(provisioner{}, topic)`, and asserts the exact SNS attribute map.

Control flow and state behavior: no Kubernetes client or Secrets are used in these tests. The function is called with an empty provisioner because the covered cases do not require `getSecretValue`. The output map is checked for baseline `OpaqueData` and `persistent` plus endpoint-specific fields such as `push-endpoint`, `verify-ssl`, `cloudevents`, `amqp-exchange`, `amqp-ack-level`, `kafka-ack-level`, `use-ssl`, and `mechanism`.

Dependencies and integration points: the tests use `cephv1.CephBucketTopic`, endpoint spec structs, Kubernetes metadata, `capnslog` log configuration, `testify/assert`, and `testify/require`.

Risks and gaps: this file does not test Kafka `UserSecretRef` or `PasswordSecretRef`, URI credential replacement, referenced Secret return values, invalid Kafka URIs, opaque data non-empty values, persistent true, disable-verify-SSL variants, SNS client creation, topic creation/deletion, or `GetProvisioned`. Because `createTopicAttributes` returns a Secret map pointer, status dependency tracking remains mostly untested here.

Test signals: failures indicate a changed RGW/SNS attribute contract for endpoint provisioning. The tests are intentionally small and deterministic, making them useful for detecting accidental key renames or boolean formatting changes.
