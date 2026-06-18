# Research: sources/cloud-native/moby/daemon/command/config_unix.go

## sources/cloud-native/moby/daemon/command/config_unix.go

Purpose: installs Unix-specific dockerd configuration flags after common flags.

Important API: `installConfigFlags`. It adds runtime registration, socket group, storage driver, SELinux, default ulimits, bridge networking and firewall flags, default gateways, publishing host IP, userland proxy settings, cgroup parent, userns remap, live restore, init path, CPU real-time period/runtime, seccomp profile, default shm size, no-new-privileges, default IPC mode, default address pools, firewall backend, rootless mode, and default cgroup namespace.

State is mutation of the config object and flag set. Dependencies include daemon config, platform opts, `net`, and pflag. Risks include many flags feeding later validation and platform setup, especially userns remap, cgroup v2 CPU RT support, rootless behavior, and bridge/network defaults. `config_unix_test.go` confirms default shm size parsing.
