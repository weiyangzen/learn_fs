# sources/cloud-native/moby/daemon/logger/syslog/register.go

## Purpose
This file registers the syslog log driver with the daemon logging subsystem at package initialization time.

## Important APIs, Types, And Functions
The `init` function calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`. The registered constructor and validator are defined in `syslog.go`.

## Control Flow
Registration happens during package import. After registration, the daemon logger factory can instantiate the syslog driver by name and validate syslog-specific `log-opts`.

## State, Persistence, And Dependencies
The only state mutation is global registration inside the logger package. There is no persistence or runtime data structure in this file.

## Integration Points
The file connects package-local syslog implementation to Docker daemon log-driver discovery. Without it, daemon config using `--log-driver=syslog` would not resolve.

## Risks And Edge Cases
The registration relies on the shared `name` constant matching user-facing driver names and validator/constructor signatures. Duplicate registration would be detected by the logger package rather than here.

## Test Signals
No direct test file targets registration; indirect coverage comes from syslog option tests and daemon log config validation paths.
