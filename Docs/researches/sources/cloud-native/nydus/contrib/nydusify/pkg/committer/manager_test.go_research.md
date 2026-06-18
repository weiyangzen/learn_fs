# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/manager_test.go

Purpose: tests manager behavior with monkey-patched containerd clients, mock containers/tasks/images, and snapshotter responses.

Important APIs and flow: mock types implement required containerd interfaces. Tests cover pause/resume client/load/task failures and success, inspect failures at image/task/info/spec/snapshot stages, empty snapshot mounts, and parsing mount options into lower/upper dirs. `TestParseMountOptions` covers standard, volatile, reversed, multi-lower, `index=off`, and missing field cases.

State and persistence: pure mocks, no containerd daemon. Uses gomonkey to replace client methods.

Dependencies and integration: verifies the exact inspect data consumed by committer orchestration.

Risks and test signals: good branch coverage for error wrapping and parsing. Monkey-patched tests can be brittle across containerd API changes and do not catch real service lifecycle issues such as unclosed clients.
