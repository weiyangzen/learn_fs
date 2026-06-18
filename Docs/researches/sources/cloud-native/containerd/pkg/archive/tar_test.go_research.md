<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_test.go -->
# sources/cloud-native/containerd/pkg/archive/tar_test.go

Purpose: main non-Windows archive test suite for diff/apply correctness, security-sensitive path handling, whiteout semantics, hardlinks, xattrs, directory creation, source-date reproducibility, and integration with system `tar`.

Important APIs and functions: top-level tests include `TestUnpack`, `TestBaseDiff`, `TestRelativeSymlinks`, `TestSymlinks`, `TestTarWithXattr`, `TestBreakouts`, `TestDiffApply`, `TestApplyTar`, `TestDiffTar`, and `TestSourceDateEpoch`. Helpers include `testApply`, `testBaseDiff`, `testDiffApply`, `makeWriterToTarTest`, `makeDiffTarTest`, validators for tar entries, `diffApplier`, and `requireTar`.

Control flow and state: tests build synthetic filesystems with `continuity/fs/fstest`, produce tar streams either through system `tar`, `Diff`, or `tartest`, apply them into temp dirs, and compare with expected filesystem state or tar-entry validators. Security cases intentionally create symlinks/hardlinks with absolute, relative, parent, empty, and replacement paths to check root bounding.

Dependencies and integration: integrates archive code with continuity test fixtures, system `tar`, `go-digest`, root-only xattr checks, and the tartest tar-stream builder.

Risks and test signals: the suite is the strongest signal for archive regressions. It validates invalid whiteout names return `errInvalidArchive`, sockets are ignored, hardlink parent inclusion is deterministic, source-date mtimes are capped while whiteouts remain Unix epoch, and repeated diff generation has stable digests outside short mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_test.go -->
