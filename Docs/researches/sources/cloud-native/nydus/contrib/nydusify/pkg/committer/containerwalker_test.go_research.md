# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker_test.go

Purpose: tests `ContainerWalker` using a mock container store plugged into a containerd client.

Important APIs and flow: `mockContainerStore` implements container store methods around a configurable list/error. `TestWalkK8sPrefixRejection` checks unsupported request form. `TestWalkContainersQueryFails` covers list errors. `TestWalkOnFoundCallbackFails` ensures callback errors abort. `TestWalkSuccessfulPath` verifies match count, request propagation, and match indexes for two containers.

State and persistence: pure in-memory containerd service mock; no daemon needed.

Dependencies and integration: validates the walker contract consumed by commit short-ID resolution.

Risks and test signals: strong for walker branching. It does not assert the exact filter string sent to the store, because the mock ignores filters, and does not test zero-match success directly.
