<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go -->
# sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go

Purpose: shared fixture for object integration tests that creates one reusable `CephObjectStore` and matching Service, reducing per-package setup cost. It explicitly allows object-store users from the test namespaces used by bucket-owner, Kafka topic, caps, keys, and opmask tests.

Important APIs and control flow: `Setup` constructs a single-replica object store named `test-shared` in `object-ns`, with metadata/data pools size 1 and gateway port 80. It creates the CR, polls until `Status.Phase == ConditionReady`, then creates a NodePort Service whose selector matches RGW labels and whose name matches the object store for `util/s3.GetS3Endpoint`. It returns the object store and a teardown closure.

State, persistence, and integration: creates durable Kubernetes CR and Service state, then deletes both during teardown. Dependencies include Rook Ceph APIs, Kubernetes Services, `intstr`, and `utils.Retry`. Risks include namespace preconditions, fixed names, single replica/no safe replica sizing, service target port 8080 assumption, and teardown that logs but does not fail if deletion fails. Test signals are readiness polling and immediate Service create success; downstream object tests validate RGW behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sharedstore/sharedstore.go -->
