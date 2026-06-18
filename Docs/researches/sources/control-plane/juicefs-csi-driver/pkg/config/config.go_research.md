# sources/control-plane/juicefs-csi-driver/pkg/config/config.go

Purpose: central process-wide configuration for the CSI driver, including feature flags, path/image defaults, pod locks, mount pod patching, config loading, and live reload.

Important APIs/types: globals such as `ByProcess`, `MountManager`, share-mount flags, `ReconcileTimeout`, CLI paths, mount bases, and default images shape runtime behavior. `PVCSelector`, `MountPatchCacheDir`, and `MountPodPatch` describe configurable mount pod customization. `Config.GenMountPodPatch` filters and merges patches. `LoadConfig`, `LoadFromConfigMap`, `StartConfigReloader`, `GetPodLock`, and `GetGlobalConfigName` are core helpers.

Control flow/state: `GlobalConfig` is mutable package-global state replaced by file/ConfigMap loads. Patch matching requires PVC and node selectors to match when present. Merge order is sequential; later matching patches can override scalars/maps/slices. Volumes with internal names or duplicates are ignored, and mounts/devices are only accepted when their volume was added.

Dependencies/integration: uses fsnotify, Kubernetes API selectors/resources, YAML parsing, klog, `pkg/common`, `pkg/k8sclient`, and `pkg/util`. `setting.go` and controllers depend on these globals and patch semantics.

Risks: config reload swaps global pointers without explicit synchronization. Map/slice merge semantics are mostly replacement, not deep merge. `deepCopy` ignores marshal errors. VolumeMount validation may surprise users who expect mounts for pre-existing volumes.

Test signals: `config_test.go` covers loading, patch generation, selectors, template replacement, volume safety, DNS settings, and `SupportFusePass`; not reload goroutines or ConfigMap loading.
