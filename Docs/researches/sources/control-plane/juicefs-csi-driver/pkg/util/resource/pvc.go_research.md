<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go

### Purpose
`pvc.go` provides metadata substitution and reclaim-safety helpers for JuiceFS CSI PVC/PV resources. It resolves PVC/node placeholders in strings, resolves secret template variables, decides whether a subPath or provisioner secret is still shared by other PVs, and patches secret finalizers.

### Important APIs, Types, And Functions
`objectMetadata` stores simple data, labels, and annotations. `ObjectMeta` joins PVC and node metadata. `NewObjectMeta` builds that structure from a PVC and optional node. `StringParser` and `objectMetadata.stringParser` replace `${.PVC.name}`, `${.pvc.namespace}`, `${.node.labels.key}`, and similar placeholders. `ResolveSecret` expands `${pvc.name}`, `${pvc.namespace}`, `${pv.name}`, and `${pvc.annotations['key']}`. `CheckForSubPath` protects shared subPath deletion. `CheckForSecretFinalizer`, `AddSecretFinalizer`, `RemoveSecretFinalizer`, and `patchSecretFinalizer` manage finalizers on Kubernetes Secrets.

### Control Flow
`StringParser` applies a package regex to find placeholders, dispatches on `PVC`/`pvc`/`node`, and replaces each placeholder with the matching metadata map entry or an empty string for missing map keys. `CheckForSubPath` returns immediately for empty path patterns, rejects root subPaths, lists all PVs in the same StorageClass, and blocks deletion if another live PV has the same CSI `subPath`. `CheckForSecretFinalizer` similarly lists PVs in the same StorageClass and blocks finalizer removal if any other live PV references the same provisioner secret namespace/name. Finalizer updates mutate the local object, JSON-patch `/metadata/finalizers`, and call the k8s client.

### State, Persistence, And Dependencies
Persistent state is in Kubernetes PVs and Secrets. The file depends on corev1 resources, JSON Patch, controller-runtime finalizer helpers, the local k8s client wrapper, and JuiceFS `common.ProvisionerSecret*` volume-attribute keys. Local state is only transient metadata maps and patch payloads.

### Integration Points
Provisioning and cleanup paths can use these helpers to expand user-provided path/secret templates and avoid deleting shared JuiceFS subdirectories or secrets while another PV still references them. The finalizer helpers integrate with controller cleanup ownership around generated or user-supplied secrets.

### Risks
The placeholder regex and direct map lookups silently replace unknown keys with empty strings, which can hide misconfigured templates. `CheckForSubPath` and `CheckForSecretFinalizer` assume `volume.Spec.PersistentVolumeSource.CSI` and its attributes exist; callers must only pass JuiceFS CSI PVs. Both list all PVs and filter in memory, so very large clusters make deletion checks more expensive and race-prone. JSON Patch uses `replace` on `/metadata/finalizers`; a Secret without that path or with stale resource version behavior may require client retry at a higher layer.

### Test Signals
Useful signals are placeholder replacement for PVC/node data, labels, annotations, lowercase `pvc`, missing keys, subPath root rejection, shared subPath prevention, empty path-pattern allowance, shared secret blocking, no StorageClass/secret bypass, and finalizer patch behavior under already-present/already-absent finalizers.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go -->
