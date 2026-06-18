# sources/cloud-native/containerd/.devcontainer/devcontainer.json

## Purpose
This file configures the VS Code/devcontainer environment for containerd development.

## Important APIs, Types, And Functions
It builds from `.devcontainer/Dockerfile`, binds the repository into `/go/src/github.com/containerd/containerd`, enables Docker-in-Docker and Go `1.26.4` features, runs `.devcontainer/setup.sh` on create, and defines post-attach tasks for `make test` and `sudo make root-test`.

## Control Flow
Devcontainer tooling builds the image, mounts the workspace, provisions features, executes `onCreateCommand`, and runs named `postAttachCommand` tasks. The container runs as `root` and passes privileged host-related run args.

## State And Persistence
State is the mounted workspace plus installed tools and binaries from setup. Privileged mounts expose `/dev` and `/run/udev`.

## Dependencies And Integration Points
It depends on devcontainers feature registry entries for Docker-in-Docker and Go, and integrates with containerd Makefile targets and setup scripts.

## Risks
The environment is privileged and rootful, appropriate for runtime tests but broad in capability. Go version drift must remain aligned with CI and `.github/actions/install-go`.

## Test Signals
Opening the devcontainer should complete setup, and the post-attach `make test` and `sudo make root-test` commands should run.
