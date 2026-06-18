# sources/cloud-native/nydus-snapshotter/integration/Dockerfile

Purpose: privileged integration test image containing Go, containerd, runc, Nydus tools, nerdctl, configs, and test entrypoint.

Flow: starts from Go Debian image, installs system deps and delve, downloads containerd/runc/Nydus/nerdctl by ARG versions and mirror, copies containerd and snapshotter configs, marks repo as safe for git, and sets entrypoint to `make install && /entrypoint.sh`.

State/dependencies: downloads external release artifacts and installs binaries under `/usr/local/bin`; exposes `/var/lib` volume.

Integration points: driven by Makefile `integration` and GitHub E2E workflow.

Risks/tests: default `GO_VER=1.24.0-bookworm` may diverge from go.mod/CI setup. Network/download availability and privileged host kernel features determine test reliability.
