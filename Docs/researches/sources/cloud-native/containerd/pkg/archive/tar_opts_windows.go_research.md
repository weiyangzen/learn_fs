<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go

Purpose: Windows container layer apply/diff option support using hcsshim/ociwclayer.

Important APIs and functions: `applyWindowsLayer`, `AsWindowsContainerLayer`, `writeDiffWindowsLayers`, `AsWindowsContainerLayerPair`, and `WithParentLayers`.

Control flow and state: applying a Windows layer wraps `ociwclayer.ImportLayerFromTar` in `winio.RunWithPrivileges` for `SeSecurityPrivilege`; diffing delegates to `ociwclayer.ExportLayerToTar` with configured parent layers. The option functions install these platform-specific implementations into `ApplyOptions` or `WriteDiffOptions`.

Dependencies and integration: integrates Microsoft `go-winio` and `hcsshim/pkg/ociwclayer`. It is the Windows counterpart to generic Unix directory diff/apply.

Risks and test signals: callers must hold backup/restore privileges as documented, and path/layer semantics are delegated to hcsshim. Failures often depend on Windows privilege state and storage location, so CI needs Windows coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go -->
