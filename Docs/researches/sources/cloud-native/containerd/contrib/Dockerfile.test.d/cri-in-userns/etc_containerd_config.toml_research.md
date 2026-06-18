<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml -->
# sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml

## Purpose
Containerd config fixture for CRI-in-userns test container.

## Important APIs, Types, And Functions
TOML config enabling containerd/CRI settings for that environment.

## Control Flow
Read by containerd on startup from the entrypoint.

## State And Persistence
Controls daemon runtime behavior; no execution by itself.

## Dependencies And Integration Points
containerd config schema and CRI plugin.

## Risks And Test Signals
Schema drift can break tests; validated only when the test container starts. Source size reviewed: 10 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/Dockerfile.test.d/cri-in-userns/etc_containerd_config.toml -->
