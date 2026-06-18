# sources/control-plane/rook/pkg/operator/ceph/object/notification/s3ext.go

Purpose: implements Ceph RGW's non-standard S3 DELETE notification endpoint using AWS SDK v2 credentials, endpoint configuration, and SigV4 signing.

Important APIs/types: `DeleteBucketNotificationRequestInput`, its `validate` method, `emptyPayloadSHA256`, and `DeleteBucketNotification`.

Control flow: the delete helper defaults nil input, validates that `Bucket` is non-empty, derives the base endpoint from `client.Options().BaseEndpoint`, builds `DELETE /<bucket>?notification` or `DELETE /<bucket>?notification=<id>`, adds the empty payload hash and optional expected-owner header, retrieves credentials from the S3 client's credential provider, signs the HTTP request with SigV4 for service `s3`, sends it through the SDK-configured HTTP client, and treats any HTTP status >=300 as an error with response body included.

State and persistence: no local state. It deletes RGW bucket notification configuration server-side.

Dependencies and integration points: depends on the AWS SDK v2 S3 client options for endpoint, region, credentials, and HTTP client. It is called by `deleteNotification` in `provisioner.go`.

Risks: notification IDs are interpolated into the query string without URL escaping; empty or nil `BaseEndpoint` can produce malformed URLs; response body is read into memory for error paths; signing time uses `time.Now()` directly; expected bucket owner is supported but caller currently does not pass it. Because this is outside the AWS modeled API, SDK behavior changes around `BaseEndpoint` or signing options can break it.

Test signals: no dedicated tests in the listed subset. Coverage is indirect through mocked delete paths in controller tests, so real request construction, signing, escaping, and HTTP status handling are not locked down here.
