# sources/cloud-native/moby/daemon/container_linux.go

## Purpose
Provides the non-Windows implementation of AppArmor profile derivation for container creation/start configuration.

## Important APIs, Types, And Functions
- `saveAppArmorConfig(container *container.Container) error` resets `AppArmorProfile`, reads daemon system info, parses security options, and assigns default or unconfined AppArmor profiles.
- Uses `daemon.RawSysInfo`, `parseSecurityOpt`, `unconfinedAppArmorProfile`, and `defaultAppArmorProfile`.

## Control Flow
The function first clears the existing profile so it can be derived from current `HostConfig.SecurityOpt`. If AppArmor is disabled according to daemon system info, it exits without setting a profile. Otherwise it parses security options as invalid-parameter errors, then defaults privileged containers to unconfined and non-privileged containers to the default profile when no explicit profile was set.

## State And Persistence
It mutates the in-memory `container.Container` security fields before those settings are persisted with the rest of the container metadata. It does not write profile files.

## Dependencies And Integration Points
Integrated by daemon container setup and validation paths that prepare Linux/FreeBSD security configuration. It depends on daemon system capability detection and the shared security option parser.

## Risks And Edge Cases
Resetting the profile is intentional, but callers must invoke it before checkpointing final container state. `RawSysInfo` failures are treated as system errors. If security option parsing changes, this file controls whether errors surface as invalid parameters.

## Test Signals
No direct test in this subset. Indirect coverage should come from container-create security option tests and platform integration tests that assert AppArmor defaults.
