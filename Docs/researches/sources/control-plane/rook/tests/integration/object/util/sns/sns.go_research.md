<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sns/sns.go -->
# sources/control-plane/rook/tests/integration/object/util/sns/sns.go

Purpose: shared helper for creating an AWS SDK v2 SNS client pointed at Ceph RGW's SNS-compatible endpoint. It is used by bucket-topic integration tests.

Important APIs and control flow: `snsResolverV2.ResolveEndpoint` converts a stored endpoint string into a Smithy endpoint. `NewClient` retrieves RGW credentials, loads AWS default config with static credentials and region `us-east-1`, gets the object-store endpoint, installs the custom endpoint resolver in `sns.NewFromConfig`, and sanity checks with `ListTopics`.

State, persistence, and integration: no state is written; it reads credentials and Kubernetes service data through S3 utilities and sends SNS API requests to RGW. Dependencies include AWS SDK v2 config/credentials/SNS, Smithy endpoints, Rook installer/K8s helpers, and CephObjectStore metadata. Risks include no TLS insecure transport override here despite endpoint scheme support, reliance on static dashboard-admin credentials, and region hard-coding. Test signal is the `ListTopics` sanity check before returning the client.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/sns/sns.go -->
