## sources/cloud-native/buildkit/util/network/netpool/pool_test.go

Purpose: validates basic netpool lifecycle semantics.

Important tests: `TestPoolReusesReturnedValue` ensures `Put` then `Get` returns the same item and `New` is called once. `TestPoolCloseReleasesAvailableAndReturnedValues` closes while an item is checked out, then verifies returning it releases it and future `Get` errors.

State/control flow: uses integer resources and slices to record releases.

Risks covered: resource reuse, close behavior, checked-out item release after close. Gaps: no delayed shrink/grace-period test, no new/release error propagation under race.
