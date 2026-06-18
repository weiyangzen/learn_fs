# sources/cloud-native/moby/daemon/logger/syslog/syslog_test.go

## Purpose
This file tests syslog driver parsing and validation behavior.

## Important APIs, Types, And Functions
Tests target `parseLogFormat`, `ValidateLogOpt`, and `parseAddress`; `functionMatches` compares function pointers to verify selected formatter and framer implementations.

## Control Flow
`TestParseLogFormat` checks RFC5424, RFC5424 microsecond, RFC3164, default, TLS framing, and invalid format cases. `TestValidateSyslogAddress` creates a temporary socket path, substitutes it into unix URLs, and verifies unsupported schemes, missing sockets, tcp/udp defaults, and platform skips. Other tests assert empty config validity, default port 514, invalid facility/format errors, accepted full option sets, and rejection of unsupported options.

## State, Persistence, And Dependencies
The only filesystem state is a temporary file used as a stand-in unix socket path. Dependencies include `testing`, `runtime`, `reflect`, `net`, `os`, `filepath`, `strings`, `log`, RackSec `srslog`, and logger constants.

## Integration Points
The tests encode user-facing `--log-opt` behavior and protect syslog's compatibility with TLS framing and Docker's shared logger attributes.

## Risks And Edge Cases
The unix socket validation is skipped or has different messages on Windows. The function-pointer comparison is exact and can fail if wrapper functions are introduced. Address tests validate syntax and stat behavior, not actual network dialing.

## Test Signals
The test suite gives focused coverage for validation paths but does not instantiate a real syslog server or assert `Log` write behavior.
