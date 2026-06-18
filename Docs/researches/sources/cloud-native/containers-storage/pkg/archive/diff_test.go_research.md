<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/diff_test.go

Purpose: security and whiteout tests for applying layer tar streams.

Important APIs/types/functions: `TestApplyLayerInvalidFilenames`, `TestApplyLayerInvalidHardlink`, `TestApplyLayerInvalidSymlink`, `TestApplyLayerWhiteouts`, `makeTestLayer`, and `readDirContents`.

Control flow: breakout tests build malicious tar headers and pass them to shared `testBreakout` with `applylayer`, expecting either a `breakoutError` or no mutation/leak outside the destination. Whiteout tests apply a sequence of synthetic layers and verify final directory contents after regular entries, `.wh.<name>` removals, escaped dot names, and `.wh..wh..opq` opaque directory behavior.

State/persistence: temporary test trees and generated layer streams only.

Dependencies/integration: exercises `UnpackLayer`, `ApplyLayer`, `Tar`, whiteout constants, path breakout detection, hardlink/symlink extraction checks, and directory walking.

Risks/test signal: protects against archive breakout vulnerabilities and whiteout regressions. Windows skips indicate platform gaps in link and whiteout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff_test.go -->
