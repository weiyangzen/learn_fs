# sources/control-plane/rook/pkg/operator/ceph/object/s3-handlers_test.go

Purpose: tests S3 client construction behavior in `NewS3Agent`.

Important APIs/tests: `TestNewS3Agent` with subtests for no TLS/debug, debug logging, insecure TLS without cert, secure TLS with cert, insecure TLS with cert, custom HTTP client, host:port endpoint with TLS, host:port endpoint without TLS, and full URL endpoint.

Control flow: each subtest constructs an agent with different flags and asserts the SDK client's `BaseEndpoint`, `ClientLogMode`, and HTTP transport/TLS settings. The custom client case verifies transport tuning survives construction.

State and persistence: no external state; no real S3 calls are made.

Dependencies and integration points: depends on AWS config values exposed through SDK client options, Go `http.Transport`, and `testify/assert`.

Risks: tests use arbitrary `tlsCert` bytes, so they verify transport wiring but not PEM parsing success. They do not cover bucket/object method behavior, retries, credentials, or path-style setting.

Test signals: strong signal for endpoint normalization and TLS mode selection, which are critical for RGW internal clients and notification provisioning.
