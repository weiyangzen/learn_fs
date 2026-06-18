# sources/control-plane/rook/pkg/operator/ceph/object/bucket/util.go

## Purpose
`util.go` contains bucket-provisioner helpers for Rook Ceph object buckets. It starts the lib-bucket-provisioner controller, extracts storage-class/ObjectBucket metadata, validates the target CephObjectStore, parses OBC quota/policy/lifecycle options, and resolves the owning object store for existing ObjectBuckets.

## Important APIs, Types, and Functions
`NewBucketController()` computes the provisioner name from `object.GetObjectBucketProvisioner()` and creates a `provisioner.Provisioner` that watches all namespaces. Simple accessors read storage class parameters, ObjectBucket bucket names, Ceph users, endpoints, and static bucket names. `(*Provisioner).getObjectStore()` verifies the CephObjectStore CR in the cluster namespace. `additionalConfigSpecFromMap()` accepts only controller-allowed keys and converts Kubernetes quantities through `quanityToInt64()`. `GetObjectStoreNameFromBucket()` prefers `AdditionalState` keys `objectStoreName` and `objectStoreNamespace`, then falls back to parsing the legacy RGW service DNS name.

## Control Flow, State, and Persistence
The file does not persist state directly. It transforms OBC/OB/StorageClass state into provisioner inputs and errors early for missing object store CRs, disallowed extra config, invalid quantities, or malformed legacy bucket hosts. Object store ownership is persisted indirectly in ObjectBucket `Spec.AdditionalState`; legacy fallback is retained for older buckets.

## Dependencies and Integration Points
It integrates kube-object-storage `ObjectBucket`, Kubernetes `StorageClass`, Rook CephObjectStore clients, object-store DNS parsing, OBC additional-config allow-listing, Kubernetes quantity parsing, and the lib-bucket-provisioner runtime.

## Risks and Test Signals
Risks include relying on untyped string map keys, the misspelled helper name `quanityToInt64`, fallback behavior that cannot support all external-store endpoints, and invalid config being controlled by the global OBC allow-list. Tests should cover allowed/disallowed additional config, quantity parsing, AdditionalState resolution, legacy endpoint parsing, and missing CephObjectStore errors.
