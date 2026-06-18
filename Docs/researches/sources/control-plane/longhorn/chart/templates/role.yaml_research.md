# sources/control-plane/longhorn/chart/templates/role.yaml

Purpose: grants Longhorn Manager broad namespace-scoped permissions over core, apps, batch, policy, coordination, RBAC, and discovery resources.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `Role`, resource groups `""`, `apps`, `batch`, `policy`, `coordination.k8s.io`, `rbac.authorization.k8s.io`, and `discovery.k8s.io`, all with wildcard verbs.

Control flow: the template always renders one Role named by `include "longhorn.name"` in the release namespace. Rules are static and not value-gated.

State and persistence: the Role persists namespace-scoped authorization policy. It does not bind itself until `rolebinding.yaml` links it to `longhorn-service-account`.

Dependencies/integration: required by Longhorn Manager, driver deployer, upgrade hooks, and uninstall job to create and mutate pods, services, configmaps, PVCs, workloads, jobs, leases, local RBAC, and endpoint slices.

Risks: wildcard verbs across many namespace resources are powerful; compromise of the bound service account gives extensive namespace control. The role is namespace-scoped, so any cluster-scoped permissions Longhorn needs must come from other templates not in this work item.

Test signals: use `kubectl auth can-i --as system:serviceaccount:<ns>:longhorn-service-account` for core Longhorn operations. Run install, upgrade, CSI deployment, recurring jobs, and uninstall to catch missing resource verbs.
