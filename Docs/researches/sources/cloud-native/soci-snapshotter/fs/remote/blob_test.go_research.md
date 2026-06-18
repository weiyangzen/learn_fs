# sources/cloud-native/soci-snapshotter/fs/remote/blob_test.go

Purpose: tests remote blob range reading, failure paths, check interval behavior, and helper round trippers for single and multipart HTTP responses.

Important APIs and flow: `TestReadAt` enumerates chunk sizes, offsets, blob sizes, and multi-range support, then validates returned bytes. `TestFailReadAt` covers HTTP failure responses, truncated bodies, and missing/broken headers. `TestParallelDownloadingBehavior` starts three concurrent `fetchRange` calls and checks round-trip counts/content with a counting transport. `TestCheckInterval` ensures `Check` skips network calls before interval expiry and updates `lastCheck` after an expired successful check. Helper transports validate Range headers and synthesize full, single-part partial, multipart partial, broken body, and broken header responses.

State and persistence: all in-memory bytes and fake `http.RoundTripper` implementations. No real registry or cache.

Dependencies and integration: exercises `blob`, `httpFetcher.fetch`, multipart parsing, range parsing, and `bytesWriter` together. It gives strong signal around HTTP response shape handling.

Risks and test signals: the comment in `TestParallelDownloadingBehavior` mentions expecting one round trip, but test data expects three, matching the current implementation without singleflight coalescing. Tests do not cover 401/403 URL refresh, force single-range mode from config, or `Blob.Refresh`.
