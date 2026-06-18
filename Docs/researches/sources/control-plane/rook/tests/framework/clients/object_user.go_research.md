# sources/control-plane/rook/tests/framework/clients/object_user.go

Purpose: `ObjectUserOperation` manages `CephObjectStoreUser` resources and verifies RGW user state/secret creation.

Important APIs/types/functions: constructor `CreateObjectUserOperation`; `GetUser`, `UserSecretExists`, `Create`, and `Delete`.

Control flow: `Create` applies a rendered object store user CR with quotas/caps. `GetUser` reads the object store CR, creates an RGW multisite context using admin cluster info, and calls `rgw.GetUser`. `UserSecretExists` runs `kubectl get secrets` with labels for object store and user and interprets output text. `Delete` deletes the CR through kubectl.

State and persistence behavior: persistent state includes the Kubernetes user CR, generated secret, and RGW user account/quota/cap metadata.

Dependencies and integration points: depends on Rook object operator APIs, Ceph admin context, typed Rook clientset, installer manifests, and kubectl output conventions.

Risks: `UserSecretExists` treats successful command output containing `No resources found` as absence, which is sensitive to kubectl localization/output format. `GetUser` assumes the object store is available and RGW admin operations are reachable. Deletion does not wait for user or secret cleanup.

Test signals: user CR creation, generated secret labels/data, RGW `GetUser` details, quota/cap propagation, and post-delete absence of CR/secret/RGW user are useful signals.
