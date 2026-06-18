# sources/cloud-native/moby/daemon/logger/splunk/splunk_test.go

## Purpose
This file is the behavioral test suite for the Splunk HEC log driver. It validates configuration parsing, construction defaults, proxy handling, message formatting variants, compression, batching, retry buffering, connection verification, shutdown, and deadlock resistance.

## Important APIs, Types, And Functions
The tests exercise `ValidateLogOpt`, `New`, `logger.Logger.Log`, and `logger.Logger.Close` through concrete driver implementations such as `splunkLoggerInline`, `splunkLoggerJSON`, and `splunkLoggerRaw`. The test data uses `logger.Info` fields for container identity, labels, environment, and tag templates, and checks the resulting `splunkMessage` payloads recorded by the local HEC mock.

## Control Flow
Most tests start a `NewHTTPEventCollectorMock`, build `logger.Info`, call `New`, submit one or more `logger.Message` values, close the logger, and inspect mock HTTP state. The suite covers defaults, inline/json/raw formats, raw mode with labels and empty tags, batching by frequency and batch size, one-message-per-request compatibility, failed verification, skipped verification with later recovery, bounded buffers, permanently failing servers, log-after-close rejection, and blocked endpoint close completion.

## State, Persistence, And Dependencies
The state under test is in-memory driver state: URL path normalization, auth header, null/default Splunk message fields, gzip flags, stream channel capacity, batch settings from environment variables, retry buffers, and close markers. Dependencies include `net/http`, `compress/gzip`, `runtime`, `time`, `github.com/moby/moby/v2/daemon/logger`, and the package-local HEC mock.

## Integration Points
These tests define the contract between Docker's logger subsystem and Splunk HEC. They verify HEC endpoint path `/services/collector/event/1.0`, `Authorization: Splunk <token>`, optional proxy use through `HTTP_PROXY`, gzip request handling, log tag templating, Docker labels/env attribute inclusion, and fallback behavior when a HEC endpoint is unhealthy.

## Risks And Edge Cases
High-risk areas are asynchronous send loops, bounded buffers dropping old messages under sustained outage, flush-on-close behavior, and blocked HTTP requests causing `Close` to hang. Raw format explicitly drops whitespace-only events because HEC rejects empty events. Timing-sensitive frequency tests are relaxed on Windows due to slower scheduling.

## Test Signals
The suite is itself the primary signal. It asserts exact message counts, request counts, per-message timestamps, field values, event map/string content, gzip consistency, connection verification behavior, retry success, buffer eviction order, and a 60-second watchdog with stack dump for blocked close deadlocks.
