<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go

Purpose: registers the BeeGFS operator API group/version for Kubernetes runtime schemes.

Important APIs and flow: declares kubebuilder package annotations, `GroupVersion = schema.GroupVersion{Group: "beegfs.csi.netapp.com", Version: "v1"}`, `SchemeBuilder`, and `AddToScheme`.

State and persistence: no runtime state beyond scheme registration data compiled into the manager binary.

Dependencies and integration points: imports `k8s.io/apimachinery/pkg/runtime/schema` and controller-runtime `scheme`. Used by managers, clients, tests, and generated code to recognize `BeegfsDriver` objects.

Risks and test signals: changing group or version is a breaking API/storage change and must match CRDs, CSVs, RBAC, and manifests. Test by compiling, running envtest, and verifying CRD group/version alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go -->
