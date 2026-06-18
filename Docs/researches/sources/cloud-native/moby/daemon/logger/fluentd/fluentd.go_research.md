## sources/cloud-native/moby/daemon/logger/fluentd/fluentd.go

Purpose: Implements the `fluentd` logging driver, sending container logs to Fluentd over TCP, TLS, or Unix socket with configurable buffering, retries, acknowledgements, async behavior, precision, and read/write timeouts.

Important APIs and types: `fluentd` stores tag, container ID/name, `*fluent.Fluent` writer, and extra attributes. `location` represents parsed address. Public functions are `New`, `Log`, `Close`, `Name`, `ValidateLogOpt`, with internal `parseConfig` and `parseAddress`.

Control flow and state: `New` parses options into `fluent.Config`, parses the log tag, extracts extra attributes, creates a Fluent writer, and stores container metadata. `Log` builds a map with container ID/name, source, log line, extra attributes, and optional partial-log metadata, then posts it with the message timestamp. Messages are returned to the pool only after successful post. `parseConfig` handles address, buffer size, retry wait, max retries, async and async reconnect interval bounds, sub-second precision, request ack, and non-negative read/write timeouts. `parseAddress` defaults empty/host-only addresses to TCP `127.0.0.1:24224`, supports `tcp`, `tls`, and `unix`, validates port range and path rules.

Dependencies and integration points: Uses `fluent-logger-golang`, Docker units parser, logger tag and extra attribute helpers, errdefs invalid-parameter wrapping, and containerd logging.

Risks: Fluentd writer can buffer and retry, so delivery semantics depend on its library. Timeouts are important to avoid indefinite blocking on unhealthy connections. Address parsing must handle IPv6, Unix paths, invalid schemes, and port bounds. Partial metadata fields are stringified and must remain compatible with downstream consumers.

Test signals: `fluentd_test.go` validates reconnect interval bounds, extensive address parsing, write timeout validation, and integration-style read/write timeout effectiveness against Unix socket test servers.
