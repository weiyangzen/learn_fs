<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-dev-tools -->
# sources/cloud-native/containerd/script/setup/install-dev-tools

- Purpose: Installs pinned developer tooling used by containerd generation, docs, lint, and protocol workflows.
- Important commands: `go install` for `go-fix-acronym`, `go-md2man`, `golangci-lint/v2`, `protoc-gen-go-ttrpc`, and `buf`.
- Control flow and state: Sequential Go installs place binaries into `$GOBIN` or `$GOPATH/bin`.
- Dependencies and integration: Requires module-aware Go and network access to module proxies/source. Integrates with make targets for lint, docs, protobuf, and validation.
- Risks: Global tool installation can shadow user versions; no checksum pinning beyond module versions; failures leave partial tool sets.
- Test signals: Make validation/lint/doc targets finding the expected binaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-dev-tools -->
