# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_oci_worker.go

Purpose: registers and implements the Linux OCI/runc worker initializer. It selects snapshotters, applies worker flags, handles rootless and process sandbox modes, and constructs a worker backed by runc.

Important APIs and flow: init registers OCI flags and priority 0. `applyOCIFlags` applies enable/auto, labels, snapshotter, rootless, no-process-sandbox, platforms, GC thresholds, network/CNI paths, worker binary, proxy snapshotter, apparmor/SELinux, and parallelism. `ociWorkerInitializer` skips auto mode when no runc/buildkit-runc exists, parses user remapping, builds resolver/session-aware snapshotter factory, validates unsafe no-process-sandbox requires rootless, builds DNS/CDI/network/parallelism options, calls `runc.NewWorkerOpt`, attaches GC policy/version/registry hosts/platforms, and creates a base worker.

State and persistence: worker state lives under daemon root with chosen snapshotter (`native`, `overlayfs`, `fuse-overlayfs`, `stargz`, or proxy). Stargz setup persists filesystem/snapshotter state and uses session-aware resolver labels. User remap can alter state compatibility.

Dependencies and risks: depends on Linux-only containerd snapshotters, fuse-overlayfs, stargz, network providers, semaphores, userns, resolver/session manager, and runc worker. Risks include snapshotter auto-detection, unsafe process sandbox mode, rootless requirements, typo-prone CNI flag application, and proxy snapshotter socket validation. Direct tests are absent in this group.
