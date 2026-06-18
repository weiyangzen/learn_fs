# sources/cloud-native/cri-o/internal/storage/image_test.go

Purpose: tests core image service behavior using mocked containers/storage and CRI-O storage transport.

Important APIs/types/functions: specs for `GetImageService`, `GetStore`, `HeuristicallyTryResolvingStringAsIDPrefix`, `CandidatesForPotentiallyShortImageName`, `UntagImage`, `ImageStatusByName`, `ListImages`, `PullImage`, and `CompileRegexpsForPinnedImages`.

Control flow: setup constructs mocks, temp registries config paths, and an `ImageServer`. Tests configure gomock sequences for storage resolution, image metadata reads, big data, layers, and deletion. Pull tests call real copy paths with invalid policy/context inputs to assert failures.

State and persistence behavior: uses temporary config files and mock state only; no real image store is required.

Dependencies and integration points: Ginkgo/Gomega, gomock, CRI-O mockutils, containers/image references/storage transport, containers/storage mock store, and CRI-O config/reference helpers.

Risks: mocked storage sequences mirror containers/image internals, so upstream behavior changes may require helper updates. Pull tests validate failure behavior, not successful remote pulls.

Test signals: covers short-name aliases/search registries, tag+digest normalization, missing registry config, untag delete vs remove-name paths, corrupt/missing image status, list cache-building failures, cancellation/deadline propagation, and pinned regexp exact/keyword/glob cases.
