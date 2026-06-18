# sources/cloud-native/moby/daemon/oci_windows.go

## Purpose
This file assembles Windows OCI runtime specs and handles Windows-specific container directories, Hyper-V isolation, HNS endpoint lists, credential specs, resource limits, backing device paths, and device assignments.

## Important APIs, Types, And Functions
Key methods/functions include `setupContainerDirs`, `isHyperV`, `createSpec`, `createSpecWindowsFields`, `escapeArgs`, `getBackingDeviceForContainerdMount`, `setWindowsCredentialSpec`, `setResourcesInSpec`, `readCredentialSpecRegistry`, `readCredentialSpecFile`, `setupWindowsDevices`, and no-op Windows `getUser`/`mergeUlimits`.

## Control Flow
`setupContainerDirs` prepares secret/config dirs, mounts Hyper-V rootfs only when needed for first-start symlink creation, and returns secret/config mounts. `createSpec` validates image OS, starts from default Windows spec, applies annotations and mounts, sets process env/CWD/TTY/user, computes layer folders, gathers HNS endpoint IDs and gateway endpoint IDs from libnetwork driver info, handles shared network containers, sets DNS search, then delegates Windows fields. `createSpecWindowsFields` sets hostname, default CWD, command line vs args, root path/backing device for process-isolated snapshotter containers, boot optimization, resources, credential spec, and Windows devices.

## State, Persistence, And Dependencies
The file mutates only the spec and prepares container filesystem symlinks for secrets/configs. It reads daemon root, image service, dependency store configs, Windows registry, credential spec files under daemon root, alternate data streams from containerd mounts, hcsshim layer paths, runtime CPU count, and HNS driver metadata.

## Integration Points
This is the Windows counterpart to Linux OCI creation, integrating Docker container config with containerd/HCS, image layers, libnetwork/HNS, Swarm config-backed credential specs, registry/file/raw credential specs, Windows resource controls, and Windows device syntax.

## Risks And Edge Cases
Credential spec parsing silently lets the last valid `credentialspec` option win but rejects unknown malformed options. `file://` credential specs must be relative and remain under the daemon credential spec directory. `config://` is accepted only for swarm-managed containers with a dependency store. Backing device extraction depends on containerd's Windows alternate data stream implementation. Endpoint gathering skips networks/endpoints/driver info that cannot be found. Windows rootfs cannot be read-only.

## Test Signals
`oci_windows_test.go` covers credential spec no-op cases, file/registry/config/raw success, path traversal/absolute path rejection, missing file/registry errors, case-insensitive option names, unsupported option/scheme rejection, empty values, registry mocking, and Windows device mapping validation.
