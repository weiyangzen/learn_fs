# sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers.go

Purpose: wraps AWS SDK v2 S3 client creation and common bucket/object operations for Ceph RGW.

Important APIs/types: `rookLogger`, `CephRegion`, `S3Agent`, `NewS3Agent`, `CreateBucket`, `createBucket`, `PutObjectInBucket`, `GetObjectInBucket`, `DeleteObjectInBucket`, and `BuildTransportTLS`.

Control flow: `NewS3Agent` configures static credentials, region `us-east-1`, retry settings, optional signing debug logging, path-style addressing, endpoint parsing with inferred `http`/`https` scheme based on TLS inputs, and an HTTP client with optional TLS transport. Bucket create treats already-exists/already-owned errors as success. Object put/get/delete call AWS SDK methods with `context.TODO`; delete treats missing bucket/key as success. TLS transport builds a system cert pool, appends provided PEM bytes if present, and honors insecure skip verify.

State and persistence: S3 operations persist buckets and objects in RGW. The agent itself stores only the SDK client.

Dependencies and integration points: used by notification provisioning, bucket policy helpers, bucket provisioning logic, and object-store HTTP client generation. Depends on AWS SDK v2, static credential provider, Go TLS/x509, and Rook's package logger.

Risks: uses `context.TODO` for all operations; `GetObjectInBucket` does not close `result.Body`; invalid PEM append result is ignored; custom `http.Client` bypasses TLS transport setup even when TLS args are provided; endpoint parsing treats parse errors or missing schemes by prepending inferred scheme. Returning `"ERROR_ OBJECT NOT FOUND"` with an error is a legacy oddity.

Test signals: `s3-handlers_test.go` covers endpoint scheme inference, debug log mode, insecure/secure TLS transport configuration, custom HTTP client preservation, and host:port/full URL handling.
