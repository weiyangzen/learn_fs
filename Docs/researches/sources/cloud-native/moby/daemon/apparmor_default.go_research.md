# sources/cloud-native/moby/daemon/apparmor_default.go

## Purpose
Implements Linux default AppArmor profile naming, support checks, and installation for the daemon.

## APIs, Types, And Functions
The file defines `unconfinedAppArmorProfile`, `defaultAppArmorProfile`, `DefaultApparmorProfile`, `loadDefaultAppArmorProfileIfMissing`, `installDefaultAppArmorProfile`, and `defaultAppArmorProfileSupported`. It uses `github.com/moby/profiles/apparmor` and rootless detached-netns detection.

## Control Flow, State, And Integration
`DefaultApparmorProfile` returns `docker-default` only when AppArmor is supported. Loading checks whether the default profile is already present, installs it if missing, and skips support in rootless detached-netns mode because AppArmor sysfs is inaccessible. Persistent state is the loaded kernel AppArmor profile.

## Risks And Test Signals
Risks include false support detection, failure to load profiles on AppArmor-enabled hosts, and rootless detached namespace permission errors. Integration is with container default security profiles and host LSM state.
