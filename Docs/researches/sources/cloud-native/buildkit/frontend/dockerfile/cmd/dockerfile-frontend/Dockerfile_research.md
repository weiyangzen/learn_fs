# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/Dockerfile

Purpose: defines the container build for the external Dockerfile frontend binary.

Important stages: `xx` supplies cross-compilation helper tools; `base` installs Go, git, bash, and vendored module mode; `version` validates release tags and writes ldflags/build tags; `build` compiles a static `dockerfile-frontend`; `release` packages the binary in scratch with capability labels and network-none label.

Control flow: version stage reads release channel tag file, compares exact Dockerfile tag against built-in frontend version, records git revision including dirty suffix, and writes `/tmp/.ldflags` and `/tmp/.buildtags`. Build stage uses `xx-go build` with static/netgo/osusergo tags and verifies the binary. Release stage copies binary and sets entrypoint.

State and persistence: only image layers and temporary build artifacts inside stages. Build labels persist in the final frontend image and influence BuildKit capability negotiation.

Dependencies and integration: integrates Dockerfile frontend release metadata, tonistiigi/xx, Go toolchain, and BuildKit frontend labels.

Risks and test signals: risks include release tag/version mismatch, channel tag file drift, cross-compilation failures, static verification failures, and capability label drift with `caps.go`.
