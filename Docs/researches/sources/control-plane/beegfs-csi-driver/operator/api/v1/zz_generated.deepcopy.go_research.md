<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go

Purpose: controller-gen generated deep-copy implementations required for Kubernetes API machinery.

Important APIs and flow: implements `DeepCopyInto`, `DeepCopy`, and `DeepCopyObject` for CR root/list types, plus deep copies for nested config, image override, resource override, connAuth, and TLS structs. It allocates fresh slices/maps for connection filters, `beegfsClientConf`, node lists, file-system config arrays, conditions, and plugin config arrays, and delegates to Kubernetes deep-copy methods for `ObjectMeta`, `ResourceRequirements`, `NodeAffinity`, and `metav1.Condition`.

State and persistence: prevents shared mutable state when cached objects are copied by controllers or clients; does not persist data itself.

Dependencies and integration points: depends on controller-gen output and Kubernetes runtime interfaces.

Risks and test signals: manual edits will be overwritten and can introduce cache mutation bugs. Test with `make generate` producing no diff and `go test` controller/API paths.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go -->
