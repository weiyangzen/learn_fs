# sources/cloud-native/cri-o/internal/ociartifact/store_test.go

Purpose: Ginkgo/Gomega tests for `ociartifact.Store` behavior around rejecting real container images from artifact paths and applying pinned-image metadata to artifact list/status results.

Important APIs/types/functions: test helpers build OCI manifests, Docker schema 2 manifests, schema 1 manifests, and OCI indexes. The suite exercises `Store.EnsureNotContainerImage`, `Store.List`, `Store.Status`, `SetPinnedImageRegexps`, `ErrIsAnImage`, mocked `Impl`, and mocked `LibartifactStore`.

Control flow: `EnsureNotContainerImage` tests first mock top-level manifest lookup, then cover direct manifest parsing, manifest-list parsing, platform instance selection, second manifest fetch, and error wrapping. Pinning tests mock libartifact list/inspect responses and verify CRI image `Pinned` flags from configured regexps.

State and persistence behavior: tests use temporary artifact roots and mock stores, so no durable artifact data is required. They validate in-memory regex state on `Store` and fake-store injection.

Dependencies and integration points: depends on `gomock`, CRI-O ociartifact mocks, `libartifact`, containers/image manifest constants, OCI image-spec media types, digest parsing, and the CRI image conversion path.

Risks: manifest classification is security-sensitive because image pulls must not be accepted as artifacts. Multi-arch handling can regress if instance digest lookup or manifest media-type parsing changes. Pinning by canonical name depends on how artifact names and digests are exposed.

Test signals: covers image rejection for OCI image config, empty config media type, Docker v2s2, Docker v2s1, bad manifest bytes, bad index bytes, instance-selection failures, and successful artifact cases with `artifactType` or custom config media types. Pinning coverage includes constructor regexps, runtime regexp updates, list/status results, name matching, and digest/canonical matching.
