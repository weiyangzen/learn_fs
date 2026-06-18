# sources/control-plane/longhorn/chart/templates/extra-objects.yaml

Purpose: provides an escape hatch for chart consumers to append arbitrary Kubernetes manifests through `.Values.extraObjects`.

Important APIs/types/functions: Helm `range`, document separator `---`, `toYaml`, and `tpl` evaluated against the root chart context. The rendered objects can be any Kubernetes resource shape supplied by the user.

Control flow: for each entry in `extraObjects`, the template starts a new YAML document, serializes the object to YAML, and evaluates it as a template with access to chart values, release metadata, and helper functions.

State and persistence: this template itself holds no fixed state, but any supplied object can create persistent cluster resources, secrets, roles, workloads, or storage. Helm will track rendered objects as part of the release output.

Dependencies/integration: depends entirely on user-provided values and Helm's `tpl` behavior. It can integrate with any chart object by referencing names such as the release namespace, service accounts, services, labels, or secrets.

Risks: `tpl` gives user values full templating power, so malformed or unsafe extra objects can break rendering, bypass chart conventions, or introduce privileged resources. There is no schema-level guard here for namespace, labels, RBAC scope, or resource collisions.

Test signals: render with an empty list, a simple ConfigMap, a templated object referencing `release_namespace`, and an intentionally invalid object to confirm failure mode. Check that extra objects appear as separate documents and do not corrupt adjacent manifests.
