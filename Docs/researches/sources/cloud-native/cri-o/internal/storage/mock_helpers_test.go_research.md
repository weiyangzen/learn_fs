# sources/cloud-native/cri-o/internal/storage/mock_helpers_test.go

Purpose: shared gomock sequence helpers for storage image service tests.

Important APIs/types/functions: `mockStorageReferenceStringWithinTransport`, `mockResolveReference`, `mockResolveImage`, `mockStorageImageSourceGetSize`, and `mockNewImage`.

Control flow: helpers construct expected containers-storage references, return ordered mock sequences for successful or missing image resolution, simulate storage reference string formatting calls, simulate size lookup, and compose new-image setup.

State and persistence behavior: no persistent state; only gomock expectations.

Dependencies and integration points: depends on CRI-O mockutils, containers/image storage transport, containers/storage mocks, CRI-O storage transport mocks, and package test constants such as `testManifest`.

Risks: helpers encode expected call order and some containers/image internal behavior, making tests sensitive to dependency changes. Missing-image behavior assumes digestless lookup paths.

Test signals: enables concise status/list/untag tests while preserving exact mocked interactions.
