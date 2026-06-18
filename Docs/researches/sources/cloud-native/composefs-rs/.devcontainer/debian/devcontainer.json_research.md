# sources/cloud-native/composefs-rs/.devcontainer/debian/devcontainer.json

## Purpose
configuration or script file supporting the adjacent project workflow.

## Important APIs, Types, Functions, Or Configuration
JSON top-level keys: name, image, customizations, features, privileged, postCreateCommand, remoteEnv.

## Control Flow And Integration Points
This .json file is 31 lines and belongs to this workflow area: composefs-rs repository configuration, CI, container build, devcontainer, packaging, and Cargo manifest material. Integration points include GitHub Actions, cargo/nextest/just, bootc VM tooling, Podman/skopeo, distro package managers, devcontainer tooling, crates.io trusted publishing, and workspace lint/dependency policy. Risks include privileged/KVM/fs-verity assumptions, external image/action availability, distro differences, and publication workflow scope.

## State, Persistence, Dependencies, Risks, And Test Signals
State is held in the consuming tool: GitHub Actions runner state, Cargo workspace resolution, container image layers, package-manager databases, devcontainer runtime settings, or automation review settings depending on file type. Risks include drift between CI/devcontainer/container images and source requirements, privileged or networked runtime assumptions, external action/image/package availability, and release/publish blast radius for workflow files.
