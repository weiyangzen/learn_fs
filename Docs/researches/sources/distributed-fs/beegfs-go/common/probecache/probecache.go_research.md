# sources/distributed-fs/beegfs-go/common/probecache/probecache.go

Purpose: caches negative capability or feature probe results for a bounded window so tight loops avoid repeatedly invoking known-failing newer operations while still allowing later recovery after upgrades.

Important API is `Availability` with `New(recheckAfter)`, `ShouldAttempt`, and `MarkUnavailable`. The type stores `unavailableUntil`, `recheckAfter`, and a mutex.

Control flow: `ShouldAttempt` returns true when current time is after the deadline. `MarkUnavailable` sets the deadline to now plus `recheckAfter` only if the previous deadline has expired. That non-extending behavior is central: repeated failures during the same window do not postpone the next re-probe.

State is in-memory only and protected by `sync.Mutex`. There is no persistence across process restarts. Dependencies are only `sync` and `time`.

Integration points are callers that optimistically try newer ioctls/RPCs, call `MarkUnavailable` on unsupported responses, and fall back until `ShouldAttempt` becomes true again.

Risks: use of `time.Now` directly makes tests sleep-based and can be affected by clock changes. A zero or negative `recheckAfter` effectively disables negative caching. It caches only one availability state per instance, so callers need distinct instances per probe target.

Test signals: `probecache_test.go` covers cold state, unavailable state, expiry, non-extension, and re-arming.
