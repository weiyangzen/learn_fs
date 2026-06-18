## sources/cloud-native/buildkit/util/flightcontrol/flightcontrol_test.go

Purpose: stress-tests `Group` semantics around deduplication and cancellation.

Important tests: `TestNoCancel` expects two callers on one key to invoke `fn` once. `TestCancelOne` cancels one caller while another completes. `TestCancelRace` exercises retry after a cancellation race. `TestCancelBoth` verifies all callers cancel, then later calls can run fresh for both same and different keys. `TestContention` creates 100,000 calls. `TestMassiveParallel` sends 1000 failing waiters and checks retry timeout is not surfaced spuriously.

State/control flow: uses `errgroup`, atomic counters, context cancellation causes, and timed sleeps to expose synchronization behavior.

Dependencies/integration: `testify`, `x/sync/errgroup`, `pkg/errors`. Risks covered: duplicate execution, leaked failed calls, cancellation propagation, and contention. Gaps: progress replay behavior is not directly tested here.
