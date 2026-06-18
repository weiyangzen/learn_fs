# sources/cloud-native/moby/daemon/logger/syslog/syslog.go

## Purpose
This file implements Docker's syslog log driver, including option validation, address parsing, facility parsing, TLS config construction, message formatting/framing selection, and log writes.

## Important APIs, Types, And Functions
`New(info logger.Info)` constructs a `syslogger` around a `srslog.Writer`. `syslogger.Log`, `Close`, and `Name` satisfy the logger interface. Helper functions include `parseAddress`, `ValidateLogOpt`, `parseFacility`, `parseTLSConfig`, `parseLogFormat`, and RFC5424 formatter variants that set the app-name/tag field for rsyslog compatibility.

## Control Flow
`New` parses the Docker log tag template, validates/deduces protocol and address, parses facility, selects formatter and framer, dials syslog with optional TLS, configures the writer, and returns the logger. `Log` drops empty lines, sends stderr through `writer.Err`, sends other streams through `writer.Info`, and returns pooled logger messages only on successful writes.

## State, Persistence, And Dependencies
Runtime state is just the `*syslog.Writer`. No daemon state is persisted here. Dependencies include RackSec `srslog`, Docker TLS config helpers, logger utilities, standard `net/url`, `net`, `os`, `tls`, `time`, and configured TLS cert/key/CA paths.

## Integration Points
The file integrates Docker logger configuration keys (`syslog-address`, `syslog-facility`, `syslog-format`, TLS options, common tag/env/label attrs) with local or remote syslog endpoints. For `tcp+tls`, RFC5424 formats use RFC5425 length framing; for UDP/TCP they use default framing.

## Risks And Edge Cases
Unix socket addresses are validated by `os.Stat`, so missing sockets fail during validation. TCP/UDP addresses without ports default to 514. TLS skip verification is enabled by the presence of `syslog-tls-skip-verify`, regardless of its string value. `parseFacility` accepts named facilities and numeric 0-23 values shifted into syslog priority space. Empty log lines are silently ignored.

## Test Signals
`syslog_test.go` covers formatter/framer mapping, empty configs, malformed/unsupported addresses, default port behavior, invalid facilities, invalid formats, accepted common attributes, and unknown option rejection.
