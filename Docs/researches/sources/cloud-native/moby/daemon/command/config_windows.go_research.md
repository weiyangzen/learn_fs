# Research: sources/cloud-native/moby/daemon/command/config_windows.go

## sources/cloud-native/moby/daemon/command/config_windows.go

Purpose: installs Windows-specific dockerd configuration flags and defines Windows certificate-directory behavior.

Important APIs: `installConfigFlags` and `configureCertsDir`. It installs common flags, then Windows bridge fixed CIDR, virtual switch bridge name, and named-pipe access group. `configureCertsDir` is a no-op on Windows.

State is config and flag-set mutation only. Dependencies are daemon config and pflag. Risks include smaller Windows flag surface than Unix, compatibility of long-standing but platform-specific bridge/group flags, and no-op cert directory behavior differing from Unix implementations outside this subset. Tests are indirect.
