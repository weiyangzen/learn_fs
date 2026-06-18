# sources/cloud-native/cri-o/internal/resourcestore/resourcestore_test.go

Purpose: validates `ResourceStore` lifecycle, watcher, timeout cleanup, and stage behavior.

Important APIs/types/functions: local `entry` implements `IdentifiableCreatable`; specs call `New`, `NewWithTimeout`, `Put`, `Get`, `WatcherForResource`, `SetStageForResource`, and `Close`.

Control flow: no-timeout tests perform immediate put/get and watcher flows. Timeout tests create a short timeout store, add cleanup callbacks, and wait for channels. Stage tests create or update stage values and read them through watchers.

State and persistence behavior: all state is in-memory; timeout tests rely on goroutines and channel synchronization.

Dependencies and integration points: uses Ginkgo/Gomega, context, time, and resourcecleaner.

Risks: timeout-based tests can be slow or flaky under load. Some stores created in `BeforeEach` are replaced in tests, so cleanup via `Close` must cover the active instance.

Test signals: verifies stale resources are cleaned and become unavailable, placeholders are not cleaned before `Put`, watchers receive notifications, and stage defaults to `unknown`.
