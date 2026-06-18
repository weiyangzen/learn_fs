# Research: sources/cloud-native/moby/daemon/command/daemon_linux.go

## sources/cloud-native/moby/daemon/command/daemon_linux.go

Purpose: implements Linux-specific daemon platform setup, systemd notifications, and CPU real-time option validation.

Important APIs: `setPlatformOptions`, `preNotifyReady`, `notifyReady`, `notifyStopping`, `notifyReloading`, and `validateCPURealtimeOptions`. `setPlatformOptions` handles user namespace remapping by deriving remapped containerd namespaces, rejecting explicitly enabled containerd snapshotter, and otherwise disabling the snapshotter feature with a warning. Notifications use systemd `SdNotify` for ready, stopping, and reloading states. CPU real-time options are rejected on cgroup v2 and on kernels without CPU RT support.

State is mutation of daemon config features and containerd namespaces, plus systemd notification side effects. Dependencies include containerd cgroups, systemd daemon package, daemon remap helpers, sysinfo, and config. Risks include compatibility of userns remap with snapshotter, cgroup mode detection, and readiness/reload signaling correctness. `daemon_linux_test.go` covers snapshotter/userns behavior; listener tests also exercise Linux-specific socket activation through common `loadListeners`.
