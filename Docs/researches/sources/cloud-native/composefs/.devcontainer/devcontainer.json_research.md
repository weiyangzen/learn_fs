# sources/cloud-native/composefs/.devcontainer/devcontainer.json

Purpose: default devcontainer definition, currently matching the Debian variant.

Important APIs/types/functions: bootc Debian devenv image, rust/go extensions, nested container customization, privileged fallback, devenv init, and cargo PATH.

Control flow: used when no distro subfolder is selected.

State/persistence: development-only configuration.

Dependencies/integration: VS Code/devcontainer CLI, devaipod, and bootc-dev image.

Risks/test signals: duplicated config can diverge from Debian file; privileged default may be undesirable outside controlled dev environments.
