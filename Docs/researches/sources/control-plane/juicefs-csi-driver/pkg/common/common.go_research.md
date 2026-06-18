# sources/control-plane/juicefs-csi-driver/pkg/common/common.go

Purpose: central constant registry for Kubernetes labels, annotations, secret keys, volume context keys, defaults, and smooth-upgrade paths used across config, controller, builder, and utility packages.

Important API surface: pod identity constants include `PodTypeKey`, `PodTypeValue`, `PodUniqueIdLabelKey`, `PodJuiceHashLabelKey`, and `PodUpgradeUUIDLabelKey`. Lifecycle keys include `Finalizer`, delete-delay annotations, `ImmediateReconcilerKey`, and `CleanCache`. CSI secret reference keys, mount pod resource/config annotations, cache mode keys, and FUSE fd upgrade constants are all defined here.

Control flow and state: no functions or mutable state. Behavior comes from other packages comparing or writing these exact strings on Kubernetes objects.

Dependencies and integration: imported by config parsing, controllers, resource utilities, mount pod builders, and sidecar/webhook paths. These constants form an external API contract with PV attributes, PVC annotations, Secrets, ConfigMaps, Pods, and Jobs.

Risks: changing values is breaking. Broad labels such as `app` and `volume-id` can collide if used outside expected JuiceFS objects. Many tests depend indirectly on these exact constants.

Test signals: no direct unit tests; failures surface as selector, annotation, and metadata mismatches in config/controller tests.
