# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic.go

Purpose: validates Ceph bucket notification topic endpoint specs for HTTP, AMQP, and Kafka.

Important APIs/types/functions: `validateURI`, `ValidateHTTPSpec`, `ValidateAMQPSpec`, `ValidateKafkaSpec`, and `CephBucketTopic.ValidateTopicSpec`.

Control flow: `validateURI` parses a URI with `net/url`, lowercases the parsed scheme, and checks it against an allowed scheme list. HTTP allows `http` and `https`; AMQP allows `amqp` and `amqps`; Kafka allows `kafka`. `ValidateTopicSpec` walks the optional endpoint pointers in order. It validates the present endpoint and enforces exactly one endpoint spec by tracking whether one has already been seen. Multiple endpoints and missing endpoints produce errors.

State and persistence: no persistence or mutation. The function validates in-memory CRD fields before reconciliation.

Dependencies/integration: depends on `net/url`, `strings`, and `github.com/pkg/errors`. Integrates with RGW bucket notification configuration where endpoint type and URI scheme must match.

Risks: `url.Parse` may accept some inputs with empty host or unusual URI shapes; the helper validates only scheme membership. Error text says `"schema"` rather than `"scheme"`. Kafka TLS or SASL options are not validated here beyond URI scheme. Nil endpoint pointer checks happen in `ValidateTopicSpec`, but the individual `Validate*Spec` helpers assume non-nil arguments.

Test signals: `topic_test.go` covers valid and invalid schemes for all endpoint types, one invalid HTTP host case, multiple endpoint rejection, and missing endpoint rejection.
