## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod_test.go

### Purpose
`pod_test.go` is the main specification test suite for mount pod generation. It asserts exact Kubernetes pod specs and important helper behavior for cache volumes, generated commands, metrics ports, fuse-pass support, template expansion, and hostPath volume creation.

### Important APIs, Types, And Functions
The tests define `podDefaultTest` as the canonical expected mount pod. `deepcopyPodFromDefault` builds independent expected objects. Test cases cover `PodBuilder.genCacheDirVolumes`, `PodBuilder.NewMountPod`, cache-dir expansion from `MountPodPatch`, hostPath template expansion, `BaseBuilder.genMountCommand`, `BaseBuilder.genMetricsPort`, and `PodBuilder.genHostPathVolumes`.

### Control Flow
Tests build `config.JfsSetting` values through `config.ParseSetting` or literals, then call builder helpers and compare generated Kubernetes objects. The exact-pod tests marshal to YAML before comparison, making field ordering less brittle than raw struct formatting. Fuse-pass tests initialize test passfd state and switch images to one that supports smooth upgrade behavior.

### State, Persistence, And Dependencies
The test mutates global `config.NodeName`, `config.Namespace`, and `config.GlobalConfig.MountPodPatch` in places, with some defers for cleanup. It uses local filesystem cleanup for `tmp` passfd artifacts. Dependencies include Kubernetes core types, `sigs.k8s.io/yaml`, `stretchr/testify/assert`, `passfd`, and configuration parsing.

### Integration Points
The tests encode the expected contract consumed by `PodMount`, `JobBuilder`, and sidecar builders. They indirectly protect secret key references, mount path constants, metrics ports, cache volume naming, FUSE communication environment variables, and host mount propagation fields.

### Risks
Snapshot-style YAML comparisons are useful but can be brittle when Kubernetes defaults or struct fields change. Some tests append to reused slices while checking lengths, so they primarily validate aggregate count behavior rather than isolated helper output. Global config mutation can leak if future tests miss cleanup.

### Test Signals
Strong signals are failure of exact pod YAML comparisons, missing selected-node annotations for generic ephemeral cache volumes, wrong cache/hostPath template expansion, wrong metrics port defaults/fallbacks, and missing `JFS_SUPER_COMM` for fuse-pass-capable images.
