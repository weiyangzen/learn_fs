# sources/cloud-native/moby/daemon/internal/timestamp/timestamp.go

## Purpose
Parses Docker timestamp inputs for log and event filters, accepting durations, partial RFC3339 forms, date forms, and Unix timestamps with optional fractional seconds.

## Important APIs, Types, And Functions
`Parse(value, reference)` returns UTC time, treating durations as `reference - duration`. It chooses layouts based on zones, `T`, fractional seconds, and date-only input. `ParseUnixTimestamp` wraps `parseTimestamp` and permits empty input as zero time. `parseTimestamp` parses seconds and fractional nanoseconds, pads/truncates to nine digits, and rejects fractional parts over 20 digits or containing non-digits.

## Control Flow
`Parse` rejects blank strings, tries `time.ParseDuration` except literal `"0"`, then selects either `time.ParseInLocation` using the reference zone or absolute `time.Parse`. Failed non-date parsing falls back to Unix timestamp parsing.

## State And Persistence
No persistent state. Returned times are normalized to UTC.

## Dependencies And Integration Points
Used by daemon API query parameters such as `docker logs --since/--until` and `docker events`. Behavior is client-facing and compatibility-sensitive.

## Risks And Test Signals
Heuristics around `-`, `+`, and `Z` determine local versus absolute parsing. Whitespace is rejected except for the initial empty check. Tests cover partial RFC3339, zones, Unix timestamps, fractional bounds, durations, invalid values, and empty Unix timestamp behavior.
