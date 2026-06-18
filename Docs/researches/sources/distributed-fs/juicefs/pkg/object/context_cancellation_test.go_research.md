# sources/distributed-fs/juicefs/pkg/object/context_cancellation_test.go


Purpose: asserts that core object interfaces and selected network helpers honor `context.Context` cancellation.

Important APIs and flow: `TestObjectStorageInterfaceMethodsUseContext` reflects over `ObjectStorage` and checks every listed method has `context.Context` as its first input. `TestDialParallel_ContextCanceled` cancels a context before calling `dialParallel` and expects `context.Canceled`. `TestRestfulStorageGet_ContextCanceled` and `TestRestfulStoragePut_ContextCanceled` use a loopback endpoint and pre-canceled context to ensure REST calls report cancellation or deadline errors.

State and persistence: no persistent state. Tests use local contexts, dummy HTTP endpoint configuration, and no real storage writes.

Dependencies and integration: depends on `RestfulStorage`, `dialParallel`, and the public `ObjectStorage` interface. The test acts as a guard for future API changes by requiring context propagation at the interface level.

Risks and gaps: provider implementations may still ignore context internally despite the interface accepting it; this file only directly exercises REST and dial helper behavior. It does not cover cloud SDK, filesystem, or Ceph implementations.

Test signal: important API-contract coverage for cancellation-aware method signatures and selected HTTP/dial paths.
