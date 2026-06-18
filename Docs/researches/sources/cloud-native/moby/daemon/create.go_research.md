# sources/cloud-native/moby/daemon/create.go

## Purpose
Implements the generic container-create path for the daemon. It validates API create input, merges image defaults, allocates daemon metadata, creates the writable image layer, configures security and networking state, creates volumes, registers the container, records metrics, and emits the create event.

## Important APIs, Types, And Functions
- `createOpts` carries `ContainerCreateConfig`, service-managed state, and builder-specific `ignoreImagesArgsEscaped`.
- `CreateManagedContainer`, `ContainerCreate`, and `ContainerCreateIgnoreImagesArgsEscaped` are thin public entrypoints into `containerCreate`.
- `containerCreate` handles OpenTelemetry span setup, default restart policy normalization, settings/network validation, platform mismatch warnings, and warning response shaping.
- `create` performs the irreversible create sequence: image lookup, config merge, `newContainer`, security options, link registration, OS-specific setup, NRI notification, mount registration, layer creation, directory creation, OS volume setup, daemon registration, metrics, and event emission.
- `generateSecurityOpt`, `mergeAndVerifyConfig`, `validateNetworkingConfig`, and `maximumSpec` are key helpers.

## Control Flow
The create path first rejects nil container config, normalizes empty restart policy to `no`, validates host/container settings, optionally warns if the image platform does not match the host, validates endpoint settings, creates an empty host config if absent, and adapts platform defaults. The lower-level `create` resolves image/platform data, preserves Windows `ArgsEscaped` when needed, merges image config, validates logging, constructs the `container.Container`, and installs a deferred cleanup that force-removes the partially created container on later failure. The successful path sets security, registers links, initializes OS-specific defaults, normalizes network mode, informs NRI, registers mounts, creates the RW layer, creates root/checkpoint directories, creates/populates volumes, registers the container, and logs the create event.

## State And Persistence
State created here includes the in-memory `container.Container`, the container root and checkpoint directories, the writable layer from `imageService.CreateLayer`, mount point metadata, volume references, SELinux labels, NRI container state, container store/index registration, metrics, and event history. Failures after `newContainer` attempt cleanup through `cleanupContainer` with `ForceRemove` and `RemoveVolume` to avoid orphaned partial state.

## Dependencies And Integration Points
Integrates with image service lookup/layer creation, container metadata constructors, host-config validators, libnetwork validation, NRI, volume services, SELinux, user namespace identity mapping, metrics, OpenTelemetry, and event logging. The OS-specific hooks are implemented in `create_unix.go` and `create_windows.go`.

## Risks And Edge Cases
Create has many side effects before final registration, so cleanup quality is critical. Image-platform warning logic only runs when no explicit platform is requested. `labelsAsOTelAttributes` is governed by an experimental environment variable and caches the filter once. SELinux label sharing across `--ipc=container` and `--pid=container` requires labels to match. `mergeAndVerifyConfig` rejects containers with no effective command after image/user config merge.

## Test Signals
This file is indirectly covered by daemon create, config merge, networking, delete cleanup, and platform validation tests. Strong regressions show up as invalid warning/error typing, incomplete cleanup on failed create, missing RW layers, bad network endpoint validation, or create events/metrics not being emitted.
