# sources/control-plane/longhorn/chart/templates/network-policies/manager-network-policy.yaml

Purpose: optionally restricts ingress to Longhorn Manager pods labeled `app: longhorn-manager`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, manager `podSelector`, ingress-only policy, and allowed sources including manager peers, UI, CSI plugin, Longhorn recurring job pods, Longhorn job-task pods, and driver deployer pods.

Control flow: when network policies are enabled, the template emits one policy selecting manager pods. The allowed `from` list uses pod label selectors and match expressions to admit the main actors that call the manager API.

State and persistence: persistent state is the NetworkPolicy. It protects the manager API surface but can affect Longhorn control loops and system jobs if selectors do not match running pods.

Dependencies/integration: depends on labels from manager DaemonSet, UI Deployment, CSI plugin, recurring job objects, job-task pods, and driver deployer Deployment. It integrates with services that expose manager pods, including the backend service used by UI and driver deployer.

Risks: any label change in Longhorn-managed jobs or CSI pods can block manager API access. There are no port constraints, so allowed sources can reach any manager pod port. External monitoring or support tools are not admitted unless they run under matching labels or separate policies are added.

Test signals: with policies enabled, verify UI, CSI provisioning/attach, driver deployment, recurring jobs, and Longhorn job tasks can all call the manager API. Run a negative test from an unlabeled pod and observe denial.
