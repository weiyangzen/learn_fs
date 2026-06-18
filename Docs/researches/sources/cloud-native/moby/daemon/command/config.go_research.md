# Research: sources/cloud-native/moby/daemon/command/config.go

## sources/cloud-native/moby/daemon/command/config.go

Purpose: installs daemon-wide, cross-platform configuration flags on a pflag set and provides a generic string flag adapter.

Important APIs: `installCommonConfigFlags` and `stringVar[T]`. The flag installer wires registry mirrors, insecure registries, storage opts, authorization plugins, exec opts, pid/data/exec roots, containerd options, feature flags, network defaults, DNS, host-gateway IPs, labels, log driver/options, transfer concurrency, shutdown timeout, swarm default advertise address, experimental mode, metrics, generic resources, containerd namespaces, default runtime, proxy settings, CDI dirs, NRI options, and deprecated `--restart`.

State is mutation of the passed `config.Config` and `pflag.FlagSet`. Dependencies include daemon config, opts validators, registry validators, internal named option helpers, containerd log output format, and runtime GOOS for hiding Windows MTU. Risks include flag/config merge conflicts later in `loadDaemonCliConfig`, hidden/deprecated flag compatibility, map/list option aliasing, and permissive `stringVar` accepting any string until config validation. Tests in this subset cover Unix `--default-shm-size` through platform-specific flag installation.
