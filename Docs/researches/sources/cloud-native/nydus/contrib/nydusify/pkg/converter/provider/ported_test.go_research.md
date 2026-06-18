# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported_test.go

Purpose: tests `imageName` annotation precedence and cleanup behavior.

Important APIs and flow: cases assert `images.AnnotationImageName` is returned as-is, OCI `AnnotationRefName` is passed through a cleanup function, and nil annotations produce an empty string.

State and persistence: pure in-memory.

Dependencies and integration: protects archive import naming behavior used by `load`.

Risks and test signals: narrow coverage. The larger ported fetch/push/load flows are not unit-tested here and depend on containerd integration tests elsewhere.
