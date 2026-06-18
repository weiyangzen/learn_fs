# sources/distributed-fs/beegfs-go/common/strfmt/time.go

Purpose: formats durations around expiration deadlines into concise human-readable strings.

Important APIs are `ExpirationString(remaining time.Duration)` and `RoundToHoursOrDays(d time.Duration)`.

Control flow: `ExpirationString` treats positive durations under an hour as "expires in less than an hour", positive longer durations as rounded hours/days, zero or negative durations within the last hour as "expired less than an hour ago", and older expirations as rounded elapsed hours/days. `RoundToHoursOrDays` switches to days at `>=24h`, rounds to the nearest day or hour, and pluralizes units.

State and persistence: none. Dependencies are `fmt` and `time`.

Integration points are license, certificate, or status messages that need consistent expiry text.

Risks: rounding can produce "24 hours" for just under a day and "1 day" at exactly a day, which is intentional but can surprise consumers expecting floor behavior. Negative durations should be passed to `ExpirationString`, not `RoundToHoursOrDays` directly.

Test signals: `time_test.go` covers positive and negative thresholds, pluralization, and hour/day rounding boundaries.
