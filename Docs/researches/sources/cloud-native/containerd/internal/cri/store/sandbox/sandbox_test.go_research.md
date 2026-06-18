# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox_test.go

This test file validates sandbox store behavior. `TestSandboxStore` constructs several sandboxes in ready and not-ready states plus one unknown-state sandbox, adds them to a store, retrieves normal sandboxes by truncated IDs, retrieves the unknown sandbox by full ID, lists all sandboxes, updates cached stats, checks duplicate add errors, deletes sandboxes by truncated IDs, and verifies deleted IDs return `errdefs.ErrNotFound`.

The test confirms that `NewSandbox` objects with different states can coexist in the store and that unknown state does not prevent retrieval. It also verifies `UpdateContainerStats` persists new cached stats into stored sandbox values visible through `List`.

The test signal covers basic map/index behavior, truncated-ID lookup, duplicate detection, stats cache mutation, and deletion. It does not exercise SELinux label reservation callbacks, stats collector add/remove callbacks, endpoint validity, network namespace cleanup, concurrent access, or stop-channel behavior directly. The stop-channel behavior for not-ready sandboxes is covered indirectly by `sandbox_stop_test.go`.
