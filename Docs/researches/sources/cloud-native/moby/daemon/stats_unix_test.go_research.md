# sources/cloud-native/moby/daemon/stats_unix_test.go

## Purpose
This test validates parsing of Linux `/proc/stat` CPU usage data.

## Important APIs, Types, And Functions
`TestGetSystemCPUUsageParsing` embeds `testdata/stat`, passes it to `readSystemCPUUsage`, and checks expected total CPU nanoseconds and CPU count.

## Control Flow
The test avoids reading the real host by using an embedded fixture.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects host CPU values used by `GetContainerStats` for Docker stats CPU percentage calculations.

## Risks
Only one fixture is covered; malformed or partial `/proc/stat` cases rely on function error paths.

## Test Signals
Directly verifies the parser's tick-to-nanosecond conversion and CPU line counting.
