# sources/cloud-native/stargz-snapshotter/script/generated-files/generate.sh

Purpose: BuildKit-based generator/validator for protobuf-generated Go files.
Important APIs/types/functions: commands `update` and `validate`; generated Dockerfile stages `golang-base`, `generate`, `update`, `validate`.
Control flow: derives Go base version, builds a tool image with protoc and protoc-gen-gogo, runs `go generate ./...`, then either exports changed `*.pb.go` files back to the repo or fails if validation sees diffs.
State and persistence: creates temporary build context/output dirs and may copy generated files into the repository on `update`.
Dependencies and integration points: depends on Docker BuildKit, Go, protoc, gogo protobuf, and `utils.sh` version parsing.
Risks: network-dependent tool downloads; only tracks `*.pb.go`; update copies generated output over existing files.
Test signals: CI can run `validate`; developers use `update` when generated files are stale.
