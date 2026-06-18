# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/register.go

Purpose: registers manually written Rook Ceph v1 API types with a Kubernetes runtime scheme and provides the group/version/resource helpers for this API package.

Important APIs/types/functions: `CustomResourceGroup`, `Version`, `SchemeGroupVersion`, `Resource`, `SchemeBuilder`, `localSchemeBuilder`, `AddToScheme`, `init`, and `addKnownTypes`.

Control flow: package initialization registers `addKnownTypes` with the local scheme builder. `addKnownTypes` calls `scheme.AddKnownTypes` for the Ceph group/version and includes core Rook Ceph CRDs such as cluster, client, block pool, filesystem, NFS, NVMe-oF gateway, object store/user/account/realm/zone group/zone, bucket topic/notification, mirrors, subvolume groups, pool namespaces, and COSI driver types. It then adds the group version to the scheme. The same function also registers lib-bucket-provisioner `ObjectBucketClaim` and `ObjectBucket` types under their own scheme group version.

State and persistence: no durable persistence. It mutates the provided in-memory `runtime.Scheme` and sets up package-level scheme-builder registration.

Dependencies/integration: depends on Kubernetes `metav1`, `runtime`, and `schema`, the parent `ceph.rook.io` API package for the group name, and `github.com/kube-object-storage/lib-bucket-provisioner` v1alpha1 types. This is a core integration point for Kubernetes clients, controllers, informers, serializers, and tests that need typed scheme registration.

Risks: new CRD types must be added here or clients using only manual registration may fail to encode/decode them. The comment notes generated registration happens elsewhere, so builds without generated files rely on this file. `CustomResourceGroup` duplicates the string while `SchemeGroupVersion` uses the parent package constant; drift would be confusing even though current values match.

Test signals: no direct tests in this subset. Runtime scheme smoke tests should verify `AddToScheme` registers every expected CRD and the bucket-provisioner types.
