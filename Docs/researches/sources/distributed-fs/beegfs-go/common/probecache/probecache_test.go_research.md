# sources/distributed-fs/beegfs-go/common/probecache/probecache_test.go

Purpose: verifies the intended negative-probe cache semantics for `Availability`.

Important tests are `TestAvailabilityColdState`, `TestAvailabilityAfterMarkUnavailable`, `TestAvailability_AfterWindowExpires`, `TestAvailabilityRepeatedMarkUnavailableDoesNotExtendWindow`, and `TestAvailabilityMarkUnavailableAfterWindowResetsDeadline`.

Control flow uses short TTLs and sleeps to move through the unavailability window. The repeated-mark test inspects the package-private `unavailableUntil` deadline to ensure a second mark inside the window is a no-op. The reset test waits past expiry, confirms probing is allowed, then re-arms the window.

State behavior under test is the in-memory deadline protected by the mutex. There is no persistence or external dependency.

Dependencies are `testing`, `time`, `fmt`, and `testify/assert`. Integration signal is pure unit-level; no caller-specific feature probe is exercised.

Risks: sleep-based timing can be flaky under extreme scheduling delays, though durations are small and assertions are simple. Tests do not exercise concurrent callers, zero TTL, negative TTL, or clock jumps.

Test signals: good coverage of the core API contract, especially the important non-extending deadline behavior.
