<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/get_ci_vm.sh -->
# sources/cloud-native/containers-storage/hack/get_ci_vm.sh

## Purpose
This developer helper creates or configures a Google Cloud VM for debugging Cirrus-CI tasks for containers/storage.

## Important APIs, Types, And Functions
`in_get_ci_vm` gates container-entrypoint-only modes. `--config` prints repository-specific VM/container settings. `--setup` runs `contrib/cirrus/setup.sh`. The default path runs `podman run` with gcloud config and repository bind mounts against `quay.io/libpod/get_ci_vm:latest`.

## Control Flow
The script resolves its own path and repo root, branches on the first argument, validates `GET_CI_VM` for internal modes, then either emits config, performs setup, or launches the helper container.

## State And Persistence
It may create `$HOME/.config/gcloud/ssh` and the helper container can create cloud VMs or modify gcloud-related config. It does not directly edit repository files except through setup mode.

## Dependencies And Integration Points
Dependencies include podman, gcloud credentials, the get_ci_vm container image, Cirrus-CI conventions, and repository setup scripts.

## Risks And Test Signals
This is operational tooling with external side effects and access prerequisites. Volume SELinux flags and overlay `:O` bind behavior are environment-sensitive.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/get_ci_vm.sh -->
