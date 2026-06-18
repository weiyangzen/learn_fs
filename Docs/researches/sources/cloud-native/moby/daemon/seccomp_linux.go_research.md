# sources/cloud-native/moby/daemon/seccomp_linux.go

## Purpose
Applies seccomp configuration to OCI specs for Linux containers, respecting container-specific profiles, daemon defaults, privileged mode, and kernels without seccomp support.

## Important APIs, Types, And Functions
`supportsSeccomp` is true on Linux. `WithSeccomp(daemon, c)` returns a containerd OCI `SpecOpts` closure. It uses `daemon.RawSysInfo`, `seccomp.GetDefaultProfile`, `seccomp.LoadProfile`, container `SeccompProfile`, and daemon profile fields.

## Control Flow
The option returns immediately for unconfined containers. Privileged containers run unconfined unless a custom container profile is provided. Non-privileged containers require kernel seccomp support for custom/default profiles; if unsupported, custom profiles error and default behavior becomes unconfined with a warning. Otherwise the code ensures `s.Linux` exists and chooses profile priority: explicit default, container custom, daemon custom profile bytes, daemon unconfined setting, or built-in default profile.

## State And Persistence
The OCI spec is mutated in memory by setting `s.Linux.Seccomp`. The container's `SeccompProfile` may be changed to `unconfined` when kernel support is absent or daemon profile path is unconfined.

## Dependencies And Integration Points
Integrates with containerd OCI spec generation, Moby container security options, daemon sysinfo, Moby profiles/seccomp, and runtime start.

## Risks And Edge Cases
Privileged containers with custom profiles are allowed to load that profile, while privileged default/daemon profiles are ignored. Missing kernel support changes container state to unconfined for default profiles. Invalid JSON/profile content returns errors during spec construction.

## Test Signals
`seccomp_linux_test.go` covers unconfined, privileged custom/default/daemon, disabled-kernel custom error, empty default loading, container custom, daemon custom, and profile priority.
