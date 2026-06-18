# sources/control-plane/rook/pkg/daemon/ceph/util/util.go

## Purpose
`util.go` contains small Ceph daemon utility helpers for parsing endpoint strings into host and port components. It is a shared support file for code that needs to split monitor or daemon endpoint addresses.

## Important APIs, Types, and Functions
`GetIPFromEndpoint(endpoint string) string` returns the host portion from `net.SplitHostPort()`. `GetPortFromEndpoint(endpoint string) int32` returns the parsed port as a 32-bit integer. A package logger records parse failures.

## Control Flow
Both helpers call `net.SplitHostPort(endpoint)`. `GetIPFromEndpoint()` logs an error and returns the zero-value host string when splitting fails. `GetPortFromEndpoint()` logs a split failure, otherwise parses the port string with `strconv.ParseInt(..., 10, 32)`, logs parse failures, and returns the resulting `int32` value, which is zero on failure.

## State and Persistence
There is no persisted state. The only side effect is logging. Failed parsing returns zero values rather than errors.

## Dependencies and Integration Points
The helpers depend on Go's `net` and `strconv` packages and Rook's capnslog logger. Callers must provide endpoints in `host:port` form accepted by `net.SplitHostPort`, including bracketed IPv6 addresses when applicable.

## Risks
Returning zero values on parse failure can hide invalid endpoints if callers do not separately validate input. `GetPortFromEndpoint()` logs a split failure with `portString`, which is empty in that branch. The API cannot distinguish an actual port `0` from an invalid endpoint. No tests are included in this work item.

## Test Signals
Useful tests would cover IPv4 `1.2.3.4:6789`, DNS names, bracketed IPv6, missing port, non-numeric port, and out-of-range port values. Callers should also have validation tests if port zero is not acceptable.
