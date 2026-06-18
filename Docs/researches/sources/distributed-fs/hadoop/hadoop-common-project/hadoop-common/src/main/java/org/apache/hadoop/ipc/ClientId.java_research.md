# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ClientId.java

## Purpose

`ClientId` provides UUID-based 16-byte identifiers for IPC clients and conversion helpers between byte arrays and canonical UUID strings.

## Important APIs, control flow, and state

`getClientId()` generates a random UUID and writes its most and least significant bits into a 16-byte array. `toString(byte[])` returns empty string for null/empty arrays, validates length 16 otherwise, reconstructs MSB/LSB with big-endian byte shifting, and returns `UUID.toString()`. `toBytes(String)` returns empty bytes for null/empty strings or parses the UUID string into a 16-byte array. `getMsb()` and `getLsb()` expose the big-endian halves for retry cache integration.

The class is stateless.

## Dependencies and integration points

`Client` uses it to generate client IDs. `RetryCache` uses the 16-byte constraint and MSB/LSB helpers. Server response headers echo client IDs for validation.

## Risks and test signals

Only null or zero-length IDs are treated as empty; any non-empty non-16-byte array fails precondition checks. `toBytes()` relies on `UUID.fromString()` and will throw for invalid strings. Tests should check round trips, empty handling, byte-order stability, and retry-cache key compatibility.
