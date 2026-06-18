# sources/distributed-fs/juicefs/pkg/object/response_attrs_test.go

Purpose: verifies the optional response-attribute callback pattern.

Important APIs and types: `apiCall` simulates a backend by applying getters, setting `"STANDARD"` storage class, and setting a fixed request ID. `Test_api_call` uses testify assertions to check caller-visible mutation.

Control flow and state: the test passes pointers for request ID and storage class, then checks they were populated. It then applies only `WithStorageClass`, calls `SetStorageClass("")`, and verifies the previous `"STANDARD"` value remains unchanged because empty storage-class values are ignored.

Persistence and integration: no storage is touched; this is a pure unit test for the generic attribute helper.

Risks and test signals: the test establishes the contract that setters are no-ops unless the attribute was requested and that empty storage class values do not clear existing state. It does not test `WithRequestSize` or concurrency.
