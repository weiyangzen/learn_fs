# sources/cloud-native/composefs/.devcontainer/ubuntu/devcontainer.json

Purpose: Ubuntu devcontainer definition for the C composefs repository.

Important APIs/types/functions: image `ghcr.io/bootc-dev/devenv-ubuntu`, same VS Code/devaipod/privileged/init/PATH settings as Debian variants.

Control flow: starts an Ubuntu-based development container and runs the standard init script.

State/persistence: development-only configuration.

Dependencies/integration: VS Code/devcontainer tooling and bootc Ubuntu devenv image.

Risks/test signals: distro image differences can hide dependency assumptions; config has no direct CI test in this subset.
