## sources/control-plane/csi-driver-smb/.github/workflows/windows.yaml

Purpose: validates Windows build and package tests for SMB CSI on push and pull request.

Important flow: matrix uses Go 1.16.x and `windows-latest`, runs `make smb-windows`, starts CSI Proxy v1.1.1 as a background PowerShell job with kubelet path set to the workspace, waits 30 seconds, lists named pipes, and runs `go test -v -race ./pkg/...`.

State includes a background CSI Proxy process, extracted proxy binaries, Windows named pipes, and `_output/amd64/smbplugin.exe`. Dependencies are Windows runner Docker/PowerShell environment, Azure Edge download, Makefile target, and package tests. Risks include fixed sleep for proxy readiness, unpinned runner OS behavior, external binary download, and old Go version. Test signal covers Windows-specific package code and CSI proxy integration.
