# sources/cloud-native/soci-snapshotter/Dockerfile

Purpose: multi-stage Dockerfile for SOCI Snapshotter integration/runtime test image with registry, containerd, runc, nerdctl, crictl, igzip, rapidgzip, and built SOCI binaries.

Important APIs/types/functions: build args for containerd/runc/nerdctl/crictl/igzip/rapidgzip versions; stages `registry`, `igzip-builder`, `rapidgzip-builder`, and `containerd-snapshotter-base`; copies `soci` and `soci-snapshotter-grpc` from `out/`; installs configs and systemd units.

Control flow: builder stages compile ISA-L static libraries and rapidgzip, with ARM-specific ISA-L/fcf-protection disables. Final Amazon Linux stage installs utilities, copies built binaries/configs/services, downloads containerd/runc/nerdctl/crictl release artifacts for target architecture, and prepares integration entrypoint/config paths.

State and persistence: image layers contain built dependencies, SOCI binaries, containerd tooling, systemd units, and config files.

Dependencies/integration: used by integration tests and Makefile/CI Docker build flows; depends on external GitHub releases and Amazon ECR public images.

Risks: network downloads are not checksum-verified. `dnf update && dnf upgrade` can reduce reproducibility. Static rapidgzip build has architecture-specific workarounds.

Test signals: Docker build success and integration tests using the image.
