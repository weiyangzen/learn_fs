## sources/control-plane/csi-driver-smb/.github/workflows/linux.yaml

Purpose: runs the main Linux unit, container build, sanity, and coverage workflow for SMB CSI on push and pull request.

Important flow: it installs `cifs-utils` and `procps`, runs `go test -race -covermode=atomic -coverprofile=profile.cov ./pkg/...`, builds the container with Docker CLI experimental enabled, runs `make` and `make sanity-test` with `GITHUB_ACTIONS=true`, installs `goveralls`, and uploads coverage using the GitHub token.

State includes local packages, coverage profile, built image, sanity test resources, and coverage upload. Dependencies include cifs tools, Docker, Makefile targets, Go `^1.16`, and secrets. Risks include old Go version, privileged/container assumptions in sanity tests, coverage upload flakiness, and external package install drift. Test signal is the broadest Linux CI pass.
