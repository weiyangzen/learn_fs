## sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs_test.go

Purpose: Comprehensive unit and benchmark coverage for the `awslogs` CloudWatch log driver.

Important fixtures and tests: Defines constants, `logGenerator`, `testEventBatch`, mock CloudWatch client usage, and many focused tests. Config tests cover defaults, invalid booleans/intervals/buffer sizes, multiline regex parsing, datetime format conversion, log format conflicts, create-stream validation, and custom log tag generation. Client tests verify Docker user-agent header, EMF header, custom endpoint routing, IMDS region fallback, and credential endpoint signing. Creation tests cover stream creation, skipped stream creation, group creation after not-found, generic errors, and already-exists success.

Control flow and state: Queue tests assert blocking and closed behavior. Publish tests assert sequence-token use, invalid-token retry, data-already-accepted handling, and preserving token on generic errors. Batch tests replace `newTicker` with a channel to deterministically trigger flushes and validate simple, ticker, multiline, close, max event count, max total bytes, duplicate timestamps, long line, emoji, and invalid-binary scenarios.

Dependencies and integration points: Uses AWS SDK types, httptest servers for SDK middleware, loggerutils queues, and test mocks from `cwlogsiface_mock_test.go`.

Risks covered: Strongly protects CloudWatch limits, ordering, UTF-8-safe splitting, nonblocking queue mechanics, API sequence handling, option validation, and AWS client customization. Some tests mutate package globals such as `newTicker`, `newRegionFinder`, and `newSDKEndpoint`, so isolation is important when adding parallel tests.

Test signals: This is one of the strongest test files in the subset and includes benchmarks for batch collection and event unwrapping.
