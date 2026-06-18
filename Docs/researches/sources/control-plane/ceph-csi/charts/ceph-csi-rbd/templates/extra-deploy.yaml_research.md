# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/extra-deploy.yaml

Purpose: injects arbitrary extra Kubernetes objects into an RBD Helm release.

Important APIs/types/functions: ranges over `.Values.extraDeploy`, emits `---`, and renders each object through `tpl (. | toYaml) $`.

Control flow: any value-provided object becomes part of the rendered chart, with full chart context available during templating.

State and persistence behavior: depends entirely on the extra objects supplied by the operator.

Dependencies and integration points: supports local extensions such as Secrets, ServiceMonitors, additional RBAC, or policy objects without modifying the chart.

Risks: this is a powerful escape hatch. Bad objects can fail the whole release, conflict with chart-owned objects, or grant unexpected permissions. `tpl` evaluates user-provided templates.

Test signals: Helm template/lint and cluster admission are the main validation; chart tests rarely cover operator-specific extras.
