# Research: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/cephrbdmirror.go

Purpose: generated typed client for namespaced `CephRBDMirror` resources.

Important APIs/types/functions: `CephRBDMirrorsGetter`, `CephRBDMirrorInterface`, private `cephRBDMirrors`, and `newCephRBDMirrors`. It exposes CRUD, delete collection, get/list/watch, patch, and `CephRBDMirrorExpansion`.

Control flow: `newCephRBDMirrors` creates a generic client bound to resource plural `cephrbdmirrors` and the RBD mirror object/list types.

State and persistence behavior: no local persistence. API server stores mirror CRs; mirror daemon behavior is reconciled elsewhere.

Dependencies and integration points: accessed through `CephV1Client.CephRBDMirrors(namespace)`.

Risks: generated code cannot enforce peer token or mirroring health semantics. Plural/type drift breaks mirror management.

Test signals: GVR/path checks for `cephrbdmirrors`, fake CRUD/list/watch tests, and controller integration tests for mirror flows.
