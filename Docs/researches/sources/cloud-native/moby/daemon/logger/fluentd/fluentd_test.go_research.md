## sources/cloud-native/moby/daemon/logger/fluentd/fluentd_test.go

Purpose: Tests Fluentd driver option validation, address parsing, and read/write timeout behavior.

Important tests: `TestValidateLogOptReconnectInterval` rejects negative, unitless, below-minimum, and above-maximum async reconnect intervals and accepts `100ms` and `10s`. `TestValidateLogOptAddress` table-tests defaults, IPv4, IPv6, hostnames, TCP/TLS schemes, unsupported schemes, invalid ports, forbidden paths, and Unix socket paths. `TestValidateWriteTimeoutDuration` validates non-negative duration parsing. `TestReadWriteTimeoutsAreEffective` starts a Unix socket server and verifies write timeout against a blackhole connection and read timeout when request-ack is enabled but no ack is returned.

Control flow and state: Timeout tests skip Windows, use a context with 10 second deadline, create temporary Unix sockets, disable async behavior, limit retries/buffer size, and close loggers through `closeLoggerWithContext` to avoid hanging on library mutexes.

Dependencies and integration points: Uses real Fluentd client behavior over Unix sockets, logger `Info`, and helper connection handlers.

Risks covered: Protects against invalid address acceptance and indefinite blocking on broken downstream Fluentd endpoints. Timing and socket tests can be platform-sensitive, hence the Windows skip.
