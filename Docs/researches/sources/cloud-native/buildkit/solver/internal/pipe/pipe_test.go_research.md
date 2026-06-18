<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go -->
## sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go

Purpose: validates function-backed pipe completion and cancellation.

Important APIs and types: `TestPipe` and `TestPipeCancel` exercise `NewWithFunction`, receiver polling, callbacks, status fields, and cancellation.

Control flow: both tests use a blocking function that either returns `res0` after a channel is closed or returns `context.Cause(ctx)` after cancellation. They assert no status is available before completion, then verify `Completed`, `Canceled`, `Err`, and `Value`.

State and dependencies: test-only channels coordinate execution. Dependencies are `context`, `testing`, and testify `require`.

Integration points: protects scheduler pipe assumptions that no status appears before send completion, completion callbacks fire, and cancellation is represented both as an error and as `Status.Canceled`.

Risks and test signals: tests cover two core paths but not multiple updates, duplicate cancel, or concurrent receiver polling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe_test.go -->
