<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test-compatibility-releases -->
# sources/cloud-native/buildkit/hack/test-compatibility-releases

Purpose: runs compatibility integration tests against published BuildKit release images.

Important APIs, types, and functions: shell script defaults `TEST_IMAGE_NAME`, `TESTPKGS`, `TESTFLAGS`, and `TEST_IMAGE_BUILD`, defines a default `COMPATIBILITY_RELEASES` matrix from `v0.13.0` through `v0.29.0` with expected compatibility versions, pulls each `moby/buildkit:<release>` image, copies `/usr/bin/buildkitd` into `.tmp/compat-bin/<release>`, then invokes `./hack/test integration` with `TEST_BUILDKITD_BINARY`, report suffix, and expected version.

Control flow and state: downloads or references release artifacts, then runs tests comparing current behavior with release expectations. State is mostly temporary caches and Docker resources.

Dependencies and integration: depends on Docker, Go test tooling, release artifact availability, and the repository's test harness.

Risks and test signals: network/release availability, image architecture, and Docker daemon state can cause non-code failures. The script accumulates failures and exits non-zero after all releases, so logs must be checked per grouped release.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test-compatibility-releases -->
