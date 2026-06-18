# sources/control-plane/longhorn/chart/templates/rolebinding.yaml

Purpose: binds the chart's namespace Role to `longhorn-service-account`.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `RoleBinding`, `roleRef` to the Role named by `include "longhorn.name"`, and a ServiceAccount subject in the release namespace.

Control flow: the template always renders one RoleBinding. Kubernetes then grants the service account all permissions defined by `role.yaml`.

State and persistence: persistent namespace RBAC binding state. It is the connection point that makes the broad Role effective for Longhorn Manager and related jobs.

Dependencies/integration: depends on `serviceaccount.yaml` creating `longhorn-service-account` and `role.yaml` creating the referenced Role. Workloads using this service account include driver deployer and upgrade/uninstall jobs.

Risks: if the namespace helper changes or a subchart uses namespaceOverride unexpectedly, subject and role namespaces must remain aligned. Any over-permission in the Role is inherited here.

Test signals: template namespace override cases and verify RoleBinding subject namespace. Use `kubectl auth can-i` as the service account after install.
