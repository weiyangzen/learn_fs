## sources/control-plane/rook/deploy/charts/rook-ceph/templates/aggregate-roles.yaml

Purpose: optionally renders Kubernetes aggregate ClusterRoles that add ObjectBucketClaim permissions to default `view` and `edit` roles.

Important template behavior: gated by `.Values.rbacAggregate.enableOBCs`. It creates `rook-ceph-obc-view` labeled `aggregate-to-view` with get/list/watch on `objectbucketclaims`, and `rook-ceph-obc-edit` labeled `aggregate-to-edit` with create/delete/deletecollection/patch/update on `objectbucketclaims`. Both use shared chart labels from the library helper.

Control flow: all output is conditional.

State and persistence: creates cluster-scoped RBAC aggregation roles that affect users bound to Kubernetes built-in aggregate roles.

Dependencies and integration points: requires Kubernetes RBAC aggregation controller and objectbucket.io CRDs. Risks: enabling this broadens default role capabilities cluster-wide; edit role lacks get/list/watch here, relying on aggregation with view or separate permissions. Test signals should render enabled and disabled paths.
