# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy_test.go

Purpose: this file tests the POST policy upload path, especially object-key normalization, multipart form extraction, safe path construction, forwarding of policy-approved form fields into PUT headers, traversal rejection, and correct error response ordering for policy failures.

Important APIs/types/functions: tests call `s3_constants.NormalizeObjectKey`, `extractPostPolicyFormValues`, `applyPostPolicyFormHeaders`, and `PostPolicyBucketHandler`. `canonicalFormValues` mirrors handler canonicalization with `http.CanonicalHeaderKey`. The end-to-end policy test initializes `IdentityAccessManagement`, signs a V4 POST policy using `getSigningKey`/`getSignature`, and drives the handler through `httptest`.

Control flow: early tests verify that keys with leading slash, duplicate slash, backslash, Windows-style separators, and `${filename}` substitution normalize to source-relative object keys. Form extraction tests build multipart bodies, parse them with `multipart.NewReader`, then confirm file name/content type/size and canonical `Key`. Header tests show `acl` becomes `X-Amz-Acl`, content metadata survives, arbitrary `x-amz-*` fields are forwarded, reserved signature/target/success fields are skipped, and resolved `Content-Type` is not overwritten by the helper. Handler tests build mux-vars requests for key extraction, traversal rejection, and signed policy mismatch.

State and persistence behavior: most tests do not write to filer; they exercise pre-persistence transformations. The policy-violation test pre-populates `BucketRegistry.metadataCache` to avoid live filer access and ensures failure occurs before upload. That test verifies no `Location` header is set on access denial.

Dependencies and integration points: depends on multipart form handling, `httptest`, Gorilla mux vars, IAM protobuf configuration, S3 signature helpers, bucket registry metadata, and S3 constants. It integrates directly with the POST handler and indirectly with PUT semantics by validating the request headers that will be seen by `putToFiler`.

Risks: many tests validate reconstructed path logic instead of instrumenting `putToFiler`, so they do not prove bytes are persisted at the expected filer path. Header forwarding tests are strong for canonicalized keys but should be maintained when new POST policy fields are added. Time-dependent signing uses current UTC with one-hour expiration, which is stable but still tied to clock correctness.

Test signals: strong signals cover issue-class path bugs, traversal defense returning `InvalidRequest`, reserved field leakage prevention, preservation of cache/content metadata, object-lock/SSE/tag forwarding through `x-amz-*`, and policy condition failure producing `403 AccessDenied` instead of a redirect.
