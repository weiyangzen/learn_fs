## sources/control-plane/csi-driver-smb/.github/workflows/static.yaml

Purpose: runs Go static analysis on push and pull request. It uses `golangci-lint-action` v7 with golangci-lint v2.10.

Important flow: setup Go `^1.19`, checkout, and run golangci-lint with explicit enabled linters: errcheck, govet, unused, ineffassign, staticcheck, revive, misspell, asciicheck, bodyclose, dogsled, durationcheck, errname, and forbidigo, with a 30 minute timeout.

State is analysis-only. Dependencies are `.golangci.yml`, the action, and Go module resolution. Risks include mismatch between inline `-E` linter list and config default, long runtime on large vendor trees if exclusions drift, and Go version lag. Test signal is lint failure before runtime tests.
