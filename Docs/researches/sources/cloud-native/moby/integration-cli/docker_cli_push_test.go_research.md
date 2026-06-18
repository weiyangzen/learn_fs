# sources/cloud-native/moby/integration-cli/docker_cli_push_test.go

Purpose: registry push coverage for normal pushes, tag handling, empty layers, concurrent pushes, cross-repository blob mounts, unauthorized behavior, and token service error handling.

Important APIs and functions: `DockerCLIPushSuite`, registry auth suites, `cli.BuildCmd`, `tar.NewWriter`, `icmd.RunCmd`, `errgroup.Group`, `reference.DigestRegexp`, `httptest.Server`, `getTestTokenService`, and token-registry setup helpers.

Control flow: tests tag busybox and push to a private registry, reject unprefixed/untagged/bad-tag pushes, push all tags and compare subsequent "Image already exists" lines, import an empty tarball and push it, push multiple tags concurrently then repull/run them, verify cross-repo layer mount output and digest stability, ensure unauthenticated pushes do not retry, and exercise token service responses for unauthorized, malformed, rate-limit, unparsable, and no-token bodies with snapshotter-specific expectations.

State and persistence: creates registry repositories/tags, local images, imported empty-layer images, token-service-backed registry configuration, and temporary HTTP servers.

Dependencies and integration points: private registry, central registry unauthorized path, distribution token auth behavior, containerd snapshotter differences, tar import, goroutine concurrency, and digest parsing.

Risks: external registry responses and token semantics can vary; concurrent push checks must avoid goroutine-unsafe assertions; output messages differ between snapshotter and classic graphdriver paths.

Test signals: pushes must upload correct manifests/layers, reject invalid refs and auth states, safely handle concurrent uploads, reuse blobs across repositories, preserve digest identity, and report token service errors without inappropriate retries.
