# sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser_test.go

Purpose: deterministic unit tests for parser classification, platform matching, bootstrap detection, and parse error paths.

Important fixtures/APIs: `testResolver`, `newTestParser`, `New`, `FindNydusBootstrapDesc`, `matchImagePlatform`, `parseImage`, `PullNydusBootstrap`, and `Parse`.

Control flow and state: tests build mocked remotes whose resolver/fetcher return JSON by descriptor digest. They validate unsupported arch rejection, bootstrap layer annotation detection, platform matching, ignored arch mismatch for single manifests, bootstrap pulling, certificate resolve errors, single-manifest OCI mode, index classification via artifact type, no matching arch, manifest pull failure, and config missing architecture errors.

Dependencies and integration points: containerd remotes, OCI image/index/manifest JSON, digest helpers, nydus utility constants, and the remote package.

Risks and test signals: tests cover classification well without registry dependency. They do not cover descriptor platform feature-based Nydus detection directly or multiple matching descriptor precedence.
