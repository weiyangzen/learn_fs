# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_postpolicy.go

Purpose: this file implements browser-style S3 POST Object policy uploads. It parses multipart forms, validates policy signatures and conditions, normalizes the target key, forwards allowed form fields to the underlying write path, stores the uploaded file with `putToFiler`, and emits the S3 success response or redirect behavior.

Important APIs/types/functions: `PostPolicyBucketHandler` is the main handler. Helpers are `postPolicyReservedFormFields`, `applyPostPolicyFormHeaders`, `extractPostPolicyFormValues`, `validateFormFieldSize`, `getRedirectPostRawQuery`, and `IdentityAccessManagement.doesPolicySignatureMatch`.

Control flow: the handler obtains the bucket from mux vars, reads the multipart form with a 5 MiB field-memory limit, extracts exactly the canonical form headers and file part, substitutes `${filename}` in the key, validates and normalizes the key, validates table bucket restrictions, parses optional redirect URL, verifies V2 or V4 policy signature, decodes and checks policy conditions, enforces content-length range against the actual file part size, resolves content type, forwards selected form fields as request headers, computes lifecycle TTL using file size rather than multipart wire length, and calls `putToFiler`. On success it either redirects with bucket/key/etag query parameters or returns 201 XML, 200, or 204 depending on `success_action_status`.

State and persistence behavior: persistence is delegated to `putToFiler`, so POST uploads share chunk storage, ETag, SSE, ACL-derived file mode, tags, metadata, owner, and lifecycle TTL behavior with PUT. `extractPostPolicyFormValues` canonicalizes form fields into `http.Header`, validates individual field size, supports a text `file` form value when no file part exists, and uses `io.Seeker` to compute file size before rewinding the file part.

Dependencies and integration points: integrates with Gorilla mux, policy parsing/checking, IAM signature verification, `s3_constants.NormalizeObjectKey`, `validateTableBucketObjectPath`, lifecycle TTL resolver, and the shared PUT pipeline. Header forwarding maps `acl` to `x-amz-acl`, forwards cache/content metadata and all `x-amz-*` fields, and skips auth, target, and success-action fields.

Risks: only the first matching file part is used; unusual multipart implementations need compatible seekable file parts. Forwarding arbitrary `x-amz-*` fields is necessary for S3 compatibility but makes policy validation and reserved-field filtering security-sensitive. The handler validates policy before upload, which prevents redirect masking of access failures.

Test signals: the paired test file covers key normalization, filename substitution, form extraction, path construction, allowed/reserved header forwarding, traversal rejection, and a signed policy-violation path returning 403 without redirect.
