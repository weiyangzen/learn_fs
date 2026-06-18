## sources/cloud-native/buildkit/util/imageutil/config_test.go

Purpose: tests `Config` platform selection and cache-first behavior for multi-platform images.

Important test: `TestConfigMultiplatform` builds fake amd64/386/arm64 manifests and an OCI index. Only amd64 manifest/config are in cache; resolver/fetcher reads from the same test cache and errors if missing. It verifies amd64 config is returned without remote fetch and arm/v7 reports containerd not found. The test shuffles manifests to avoid order assumptions.

Support types: `testCache` implements minimal content manager/provider/ingester pieces; `testResolver` implements resolver/fetcher; `makeDesc` and `Add` create digest-addressed descriptors.

Risks covered: wrong platform selection from index and accidental fetch of unavailable manifests. Gaps: schema1 rejection, lease behavior, digest source-label validation, media type ambiguity, and resolver errors are not tested here.
