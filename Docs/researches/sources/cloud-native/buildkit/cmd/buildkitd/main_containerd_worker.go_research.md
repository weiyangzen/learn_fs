# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker.go

Purpose: registers and implements the containerd worker initializer for buildkitd. It translates config/CLI flags into containerd worker options and constructs a BuildKit worker when a usable containerd daemon is available.

Important APIs and flow: init computes defaults for containerd address, namespace, runtime, rootless, GC flags, network flags, snapshotter, labels, apparmor/SELinux, and parallelism, then registers priority 1. `applyContainerdFlags` applies CLI overrides and validates rootless requirements. `containerdWorkerInitializer` skips disabled/unavailable sockets in auto mode, adjusts rootless network default to host, builds DNS/CDI/network/parallelism/runtime options, calls `containerd.NewWorkerOpt`, sets GC policy, BuildKit version, registry hosts, optional platforms, and wraps the result in `base.NewWorker`. `validContainerdSocket` checks socket existence, client connection, and containerd introspection.

State and dependencies: persists through worker root and containerd namespace/snapshotter state. Depends on containerd client/defaults/runtime options, TOML conversion for runtime options, network providers, CDI manager, disk/GC helpers, semaphore parallelism, and BuildKit worker/base packages.

Risks and test signals: auto mode can silently skip containerd if the socket is absent or unhealthy; explicit enable turns errors into startup failures. Runtime option unmarshaling is type-dependent via platform files. No direct tests in this group cover flag interactions or socket probing.
