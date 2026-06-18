# sources/control-plane/rook/tests/framework/utils/storage.go

Purpose: this file copies Kubernetes storage helper logic to detect default StorageClasses by annotation.

Important APIs/types/functions: constants `isDefaultStorageClassAnnotation` and `betaIsDefaultStorageClassAnnotation`; function `isDefaultAnnotation`.

Control flow: `isDefaultAnnotation` checks the GA annotation first, then the beta annotation, returning true only when either value is exactly `"true"`.

State and persistence behavior: read-only. It inspects `metav1.ObjectMeta` annotations supplied by callers.

Dependencies and integration points: used by `K8sHelper.IsDefaultStorageClassPresent` after listing storage classes. Depends only on Kubernetes metav1 types.

Risks: nil annotation maps are safe for reads in Go. The helper does not parse truthy values other than lowercase `"true"`, matching Kubernetes behavior. It is copied from Kubernetes v1.21.1, so future upstream semantic changes would need manual sync.

Test signals: storage classes annotated with GA or beta default annotations should return true; absent/false annotations should return false.
