# sources/cloud-native/moby/daemon/container_operations_windows.go

## Purpose
Provides Windows-specific container operation helpers for secrets/configs, network namespace sharing metadata, and feature flags that differ from Unix implementations.

## Important APIs, Types, And Functions
- `setupLinkedContainers`, `addLegacyLinks`, `setupIpcDirs`, `mountVolumes`, and `killProcessDirectly` are Windows no-op or placeholder implementations.
- `setupConfigDir` and `setupSecretDir` create ACL-protected local directories and write config/secret file payloads.
- `enableIPOnPredefinedNetwork` and `serviceDiscoveryOnDefaultNetwork` return `true` for Windows default network behavior.
- `buildSandboxPlatformOptions` returns no extra sandbox options.
- `initializeNetworkingPaths` rejects Hyper-V donor sharing and records shared HNS endpoint IDs.

## Control Flow
Secrets/config setup checks for references, creates local directories with administrators/local-system ACLs, validates dependency store availability, skips non-file runtime configs, then writes file contents with configured modes. Network namespace sharing records the donor container ID and walks donor networks/endpoints, extracting HNS IDs from endpoint driver data into `SharedEndpointList`.

## State And Persistence
Writes config and secret payloads into container-specific local filesystem directories and removes them if setup fails. It mutates `NetworkSharedContainerID` and `SharedEndpointList` for Windows network namespace sharing.

## Dependencies And Integration Points
Depends on Windows ACL helpers, daemon dependency stores, libnetwork endpoint driver metadata, and Windows isolation mode checks. It is used by Windows container start/configuration flows and by `--network container:` sharing support.

## Risks And Edge Cases
Several Unix behaviors are no-ops on Windows, so shared code must not assume IPC setup, direct kill, or sandbox path options did work. Hyper-V network sharing is explicitly unsupported. Type assertions on endpoint driver data assume HNS metadata shapes and could panic if driver info changes unexpectedly.

## Test Signals
No direct tests in this subset. Expected coverage comes from Windows CI for config/secret injection, network sharing, default network service discovery, and HNS endpoint metadata.
