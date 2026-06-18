# sources/control-plane/longhorn/chart/templates/serviceaccount.yaml

Purpose: creates service accounts for Longhorn core workloads, UI, and support bundle operations.

Important APIs/types/functions: Kubernetes `ServiceAccount`, names `longhorn-service-account`, `longhorn-ui-service-account`, and `longhorn-support-bundle`, shared `.Values.serviceAccount.annotations`, OpenShift OAuth redirect annotation, and release namespace helper.

Control flow: the template always emits three ServiceAccounts. For the UI service account, if OpenShift and route mode are enabled, it adds `serviceaccounts.openshift.io/oauth-redirectreference.primary`, creating an annotations map if one was not already supplied.

State and persistence: persistent service account identity in the release namespace. Tokens and projected credentials are managed by Kubernetes. Annotations affect OpenShift OAuth integration.

Dependencies/integration: `longhorn-service-account` is bound by `rolebinding.yaml` and used by driver deployer and hook jobs. `longhorn-ui-service-account` is used by the UI Deployment and OpenShift oauth proxy. `longhorn-support-bundle` is used by support bundle components elsewhere in the chart.

Risks: shared annotations apply to all three service accounts, which can be too broad for IAM or workload-identity integrations. OpenShift route annotation assumes the route name `longhorn-ui`, while the route value is configurable, creating a mismatch if `.Values.openshift.ui.route` is changed.

Test signals: render with and without annotations, OpenShift disabled, and OpenShift route renamed. Verify RoleBinding targets only the core service account and UI OAuth redirects match the actual Route name.
