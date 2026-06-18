# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remote_test.go

This test file validates `Remote.RetryWithPlainHTTP`. It constructs an image reference, simulated HTTPS-to-HTTP and connection-refused errors containing the registry host, and an unrelated error. Table tests verify insecure remotes allow fallback for the two expected errors, secure remotes block fallback, unrelated errors do not fallback, and nil error returns false.

The test gives useful coverage for the security-sensitive fallback gate: HTTP downgrade only happens when explicitly insecure and when the error looks like a registry protocol mismatch for the current host. It does not exercise resolver creation, actual registry requests, TLS configuration, host mismatch behavior, malformed references, or persistence of `withPlainHTTP` across calls.

There is no filesystem or network state. The test directly constructs `Remote{insecure: ...}` rather than using `New`, so it isolates fallback logic but does not validate the resolver factory created by `New`.
