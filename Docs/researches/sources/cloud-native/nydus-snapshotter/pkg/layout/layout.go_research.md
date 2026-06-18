# Research: sources/cloud-native/nydus-snapshotter/pkg/layout/layout.go

This file defines RAFS layout constants and filesystem-version detection. Constants describe maximum superblock read size, RAFS v5/v6 names, v5 magic/version, v6 magic, v6 superblock offsets, bootstrap file paths, and a dummy mountpoint. `ImageMode` distinguishes on-demand and preload modes.

At init time, the file detects native byte order using `unsafe`. `DetectFsVersion` first checks the first eight bytes for RAFS v5 magic and version using little endian. If not v5, it checks that the buffer is large enough for v6 and that the v6 magic appears at `RafsV6SuperBlockOffset` using native endian. Unknown or too-small headers return errors.

State is limited to package-level `nativeEndian`. Integration points include bootstrap readiness validation, fake bootstrap tests, image conversion code, and mount preparation paths that locate bootstraps. Risks include native-endian v6 detection on non-little-endian systems, limited magic checks noted by the FIXME, and no direct tests for `DetectFsVersion` in this subset beyond bootstrap tests. The constants are contract-level and changing them affects filesystem validation and generated metadata paths.
