# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap_test.go

This test file provides detailed coverage for bootstrap readiness and validation. Helpers `writeFakeV5Bootstrap` and `writeFakeV6Bootstrap` create synthetic RAFS headers using layout constants. The tests simulate changing file size, delayed blob-meta creation, stable invalid v6 alignment, valid v5 bootstraps, too-small files, unknown v6 block bits, sorted blob-meta state, empty blob-meta rejection, combined state generation, and `bootstrapState.Equal`.

The test signals are strong for local file validation because they exercise both the retry-stability behavior and individual validation helpers. They verify that readiness waits through a first valid-but-changing observation and that `.blob.meta` state is included in stability decisions. The tests use short retry intervals and temporary files only; no real nydusd, daemon manager, or snapshotter state is required.

Coverage gaps are around real RAFS headers beyond the minimal magic/block-bit fields, concurrent file replacement/rename behavior, non-regular file cases for bootstrap, and permission errors. Still, this file materially reduces risk in the mount path because `Filesystem.Mount` calls `waitForReadyBootstrap` before daemon configuration and start.
