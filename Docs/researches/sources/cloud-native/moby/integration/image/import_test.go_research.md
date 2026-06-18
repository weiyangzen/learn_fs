# sources/cloud-native/moby/integration/image/import_test.go

Purpose: integration tests for image import robustness, platform handling, validation, and bad source errors.

Important APIs and helpers: `TestImportExtremelyLargeImageWorks`, `TestImportWithCustomPlatform`, `TestImportWithCustomPlatformReject`, and `TestImageImportBadSrc`. They use tar writers, `ImageImport`, platform options, a sub-daemon, and an HTTP test server.

Control flow: the large-image regression constructs an empty tar followed by 8GB of zero padding via `io.LimitReader` and imports it. Platform test imports empty tar streams with no platform, OS-only platform, and custom architecture, then inspects OS/arch. Reject test, in graphdriver mode, imports invalid or unsupported platforms and expects invalid-argument errors. Bad-source test checks missing full/trimmed URLs, encoded URL paths, and encoded absolute local paths.

State and persistence: import creates image records with specified references and platform metadata. The large test uses a separate daemon so it can run in parallel and avoid polluting the shared daemon.

Dependencies and integration: depends on tar import logic, platform normalization, snapshotter vs graphdriver behavior, daemon harness, HTTP source handling, and containerd error definitions.

Risks: large import is skipped on arm64 and remote/Windows contexts due to runtime cost. Reusing a single `imageRdr` across subtests is safe here only because it is an empty tar/zero reader path with no expected data reuse beyond construction assumptions.

Test signals: protects CVE-related large padding handling, custom platform import, unsupported platform rejection, and source path/URL error classification.
