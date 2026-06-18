<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_linux_test.go -->
# sources/cloud-native/containerd/pkg/archive/tar_linux_test.go

Purpose: Linux-only integration tests for applying generated diffs as overlay lower layers and converting OCI whiteouts to overlayfs semantics.

Important APIs and types: `TestOverlayApply`, `TestOverlayApplyNoParents`, `overlayDiffApplier`, `overlayContext`, and its `TestContext`/`Apply` methods. The tests exercise `WriteDiff`, `NewChangeWriter`, `Apply`, `WithConvertWhiteout(OverlayConvertWhiteout)`, and `WithParents`.

Control flow and state: tests require root and overlayfs support. Each FSSuite change is applied to a copy, diffed against the current lower/merged state, applied into a new lower directory, and then optionally mounted as an overlay stack. `oc.lowers` grows with each applied diff, and mounted state is unmounted between iterations.

Dependencies and integration: integrates containerd `core/mount`, overlay snapshotter support checks, continuity `fs/fstest`, and archive overlay whiteout conversion.

Risks and test signals: validates parent directory attribute inheritance with and without explicit parent inclusion. It also covers real overlay mount behavior, so it catches issues not visible in plain directory comparison, but it is gated by root and kernel overlay support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_linux_test.go -->
