# sources/cloud-native/moby/integration-cli/docker_cli_pull_local_test.go

Purpose: private-registry pull tests for alias isolation, concurrent pulls, failing pulls, ID stability, zero-layer images, manifest lists, external auth helpers, and implicit pull behavior.

Important APIs and functions: registry suite methods, `cli.BuildCmd`, `build.WithDockerfile`, `icmd.RunCommand`, `digest.FromBytes`, OCI `Index` and descriptors, filesystem writes into the registry v2 storage layout, credential helper fixture setup, and temp Docker config files.

Control flow: tests tag/push multiple aliases and ensure pulling one tag does not fetch others; run concurrent `pull -a`, failed pulls, and multi-tag pulls; compare image IDs before and after push/pull cycles; pull scratch-derived images with no layers; manually inject an OCI manifest list into the registry store; and use external credential helpers for login/push/pull with bare and scheme-qualified registry hosts. The implicit run test confirms only `latest` is pulled.

State and persistence: mutates private registry contents, local image store, temp Docker config with `credsStore`, credential helper storage, and on-disk registry blobs/revisions/tag links.

Dependencies and integration points: private registry fixture, busybox builds, OCI image-spec structs, opencontainers digest, Docker credential helper protocol, filesystem layout of distribution registry, and platform/snapshotter skips.

Risks: direct registry store mutation is tightly coupled to distribution layout; concurrent pulls expose race sensitivity; external auth tests can be affected by helper PATH/config leakage.

Test signals: pulls should be tag-scoped, concurrency-safe, failure-safe, ID-stable, capable of selecting correct manifest-list platform, compatible with external credential storage, and limited to `latest` for implicit pulls without a tag.
