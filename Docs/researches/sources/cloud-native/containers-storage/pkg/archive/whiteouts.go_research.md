<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/whiteouts.go -->
# sources/cloud-native/containers-storage/pkg/archive/whiteouts.go

Purpose: central constants describing Docker/AUFS whiteout filenames used in layer archives.

Important APIs/types/functions: `WhiteoutPrefix`, `WhiteoutMetaPrefix`, `WhiteoutLinkDir`, and `WhiteoutOpaqueDir`.

Control flow: no functions; constants are consumed by tar creation/extraction and diff logic.

State/persistence: these names become on-disk tar entries and drive deletion/opaque-directory semantics during layer application.

Dependencies/integration: used by `diff.go`, change export, overlay conversion, and tests. `.wh.<file>` denotes deletion; `.wh..wh..opq` makes a directory opaque; `.wh..wh.plnk` carries AUFS hardlink targets.

Risks/test signal: changing constants breaks layer compatibility. Whiteout handling is covered by `diff_test.go`, `changes_test.go`, and overlay archive tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/whiteouts.go -->
