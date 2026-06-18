<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go

### Purpose
`pvc_test.go` validates the metadata parsing and PVC/PV cleanup-safety contracts from `pvc.go`. It acts as the behavior reference for template substitution, subPath deletion gating, secret template expansion, and secret finalizer sharing decisions.

### Important APIs, Types, And Functions
The file tests `ObjectMeta.StringParser`, `CheckForSubPath`, `ObjectMeta.ResolveSecret`, and `CheckForSecretFinalizer`. It uses fake Kubernetes clientsets and `k8s.K8sClient` wrappers to simulate existing PVs.

### Control Flow
`TestObjectMetadata_StringParser` builds `ObjectMeta` by hand and verifies replacements for PVC names/namespaces, labels, annotations, node names, node pod CIDR, and node annotations with dotted/slashed keys. `TestCheckForSubPath` creates fake PVs, calls the helper with a target PV and path pattern, and checks the boolean/error result. `TestResolveSecret` validates `os.Expand`-style variable substitution. The finalizer test constructs target and peer PVs with storage classes and secret attributes to determine whether finalizer removal should be allowed.

### State, Persistence, And Dependencies
State is confined to fake Kubernetes API objects. Dependencies include Kubernetes fake clientsets, corev1 PV/PVC structs, metav1 metadata, and the project k8s client wrapper. No real cluster or filesystem is touched.

### Integration Points
The tests protect controller cleanup behavior where deleting a PV could delete a backing JuiceFS subPath or generated secret. They also protect StorageClass parameter and secret templating logic that users rely on for PVC- and node-derived configuration.

### Risks
The tests do not cover nil CSI sources, nil volume attributes, or client list errors, even though the production helpers dereference CSI fields. The placeholder tests accept empty-string replacement for missing keys, so they lock in permissive behavior. Fake clientsets do not model resource-version conflicts for JSON Patch finalizer updates.

### Test Signals
Strong signals include correct handling of uppercase/lowercase PVC placeholder names, annotations with dotted domains, root subPath refusal, shared-subPath refusal, no-peer deletion approval, `${pv.name}` substitution, and secret finalizer retention when another live PV references the same provisioner secret.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go -->
