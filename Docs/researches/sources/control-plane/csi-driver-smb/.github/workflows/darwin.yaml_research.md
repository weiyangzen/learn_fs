## sources/control-plane/csi-driver-smb/.github/workflows/darwin.yaml

Purpose: validates macOS build and package-level unit tests. It runs on push and pull request using `macos-latest`.

Important flow: setup Go `^1.16`, checkout, run `make smb-darwin` to cross/build the driver binary for Darwin, then run `go test -v -race ./pkg/...`.

State is only build artifacts under `_output` and Go test cache. Dependencies include macOS runner support, Makefile target `smb-darwin`, vendored modules, and package tests that are portable to Darwin. Risks include old Go version, package tests accidentally depending on Linux/Windows SMB utilities, and macOS runner image drift. Test signal is cross-platform compile and unit test success.
