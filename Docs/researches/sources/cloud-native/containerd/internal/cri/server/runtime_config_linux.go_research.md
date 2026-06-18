# sources/cloud-native/containerd/internal/cri/server/runtime_config_linux.go

## Purpose

This Linux file reports the effective cgroup driver to CRI clients.

## Important APIs, Types, and Functions

`getLinuxRuntimeConfig` returns `LinuxRuntimeConfiguration` with `CgroupDriver`. `getCgroupDriver` inspects configured runtimes in deterministic order, preferring the default runtime, then sorted names. `getCgroupDriverFromRuntimeHandlerOpts` recognizes runc options and maps `SystemdCgroup` to CRI cgroup driver enum.

## Control Flow

The service tries to generate runtime options per handler. The first handler that exposes runc cgroup settings wins. If none do, it auto-detects systemd and returns systemd or cgroupfs accordingly.

## State and Persistence Behavior

No state is persisted. It reads runtime configuration and host systemd state.

## Dependencies and Integration Points

It integrates with CRI runtime config, containerd runtime option generation, runc options, and systemd detection.

## Risks and Test Signals

Risks include returning default systemd for unrecognized option types and picking a non-obvious runtime when the default is absent. Tests cover no runtime, non-runc, alphabetical fallback, and default runtime preference.
