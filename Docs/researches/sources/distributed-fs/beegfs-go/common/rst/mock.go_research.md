# sources/distributed-fs/beegfs-go/common/rst/mock.go

Purpose: provides a `Provider` implementation for tests and higher-level packages that need an RST without real remote storage.

Important API is `MockClient`, embedding `testify/mock.Mock`, with implementations of all `Provider` methods. It has special built-in behavior for `flex.MockJob` requests and mock-driven behavior for other request types.

Control flow: `GenerateWorkRequests` returns generated segments for mock jobs or configured mock expectations. `ExecuteWorkRequestPart` marks parts completed unless a mock job asks to fail. `CompleteWorkRequests` succeeds or fails for mock jobs, otherwise delegates to mock expectations. Unsupported methods such as builder execution and remote info return RST sentinels.

State is test expectation state inside `mock.Mock` plus direct mutations of `flex.Work_Part.Completed`. There is no persistence.

Dependencies include `testify/mock`, filesystem stream result types, protobuf job/work messages, and RST segment recreation helpers.

Integration points are worker-manager tests, `ClientStore.SetMockClientForTesting`, and any package that initializes a mock RST through `rst.New`.

Risks: some mock methods call `args.Get(0).(*flex.RemoteStorageTarget)` or `args.Get(1).(time.Duration)`, so missing expectations panic. `GetJobRequest` returns nil, which is fine for current mock use but unsafe if used as a normal provider.

Test signals: this file is itself test support. RST tests use mock-job behavior indirectly through `RecreateWorkRequests`.
