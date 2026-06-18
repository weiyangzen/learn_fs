<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go

Purpose: validates XML marshaling shape for `GetCallerIdentity` responses.

Important APIs/functions: `TestGetCallerIdentityResponse_XMLMarshal` builds `GetCallerIdentityResponse` with `GetCallerIdentityResult`, marshals with `encoding/xml`, and checks namespace, ARN, user ID, account, and request ID.

Control flow: no HTTP handler is invoked; this isolates the response struct tags and field names.

State and persistence behavior: no state. It uses default account ID constants and an in-memory response value.

Dependencies and integration: depends on STS response types in `s3api_sts.go`, XML marshaling, and testify. It protects AWS SDK/client compatibility for the response envelope.

Risks: it does not validate SigV4 auth or runtime handler behavior. String containment assertions catch gross XML drift but not full schema conformance.

Test signals: passing test means response XML includes the expected AWS STS namespace and core identity fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_get_caller_identity_test.go -->
