# sources/distributed-fs/beegfs-go/common/strfmt/time_test.go

Purpose: verifies expiration string formatting across hour/day boundaries and expired/not-expired cases.

Important test is `TestExpirationString`, which calls `ExpirationString` with durations from minutes to a year.

Control flow is direct assertions. Positive cases cover 365 days, 364 days, exactly 24 hours, just under 24 hours, 119/90/89/60/59 minutes. Expired cases cover zero, just under an hour ago, exactly and just over an hour ago, 90 minutes, just under a day, and exactly a day.

State and persistence: none. Dependencies are `testing`, `time`, and `testify/assert`.

Integration point is the public formatting contract in `time.go`.

Risks: tests do not call `RoundToHoursOrDays` directly, but cover it through `ExpirationString`. They do not exercise durations that round from 36 hours to 2 days, very large durations, or negative input to `RoundToHoursOrDays`.

Test signals: good threshold coverage for the user-facing messages most likely to regress.
