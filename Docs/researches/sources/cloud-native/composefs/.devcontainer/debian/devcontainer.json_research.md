# sources/cloud-native/composefs/.devcontainer/debian/devcontainer.json

Purpose: Debian devcontainer definition for the C composefs repository.

Important APIs/types/functions: image `ghcr.io/bootc-dev/devenv-debian`, VS Code extensions `rust-lang.rust-analyzer` and `golang.Go`, `devaipod.nestedContainers=true`, `privileged=true`, post-create `sudo /usr/local/bin/devenv-init.sh`, and PATH extension for cargo.

Control flow: devcontainer tooling pulls the image, starts a privileged/nested-container-capable environment, runs init, and sets remote environment.

State/persistence: development environment config; no project runtime state.

Dependencies/integration: integrates with VS Code Dev Containers/Codespaces and bootc devenv image.

Risks/test signals: privileged mode is broad; image tags are external. Same content as root devcontainer, so drift should be avoided.
