# sources/control-plane/longhorn/chart/templates/services.yaml

Purpose: creates ClusterIP services for Longhorn admission webhook and recovery backend components.

Important APIs/types/functions: Kubernetes `Service`, names `longhorn-admission-webhook` and `longhorn-recovery-backend`, selectors `longhorn.io/admission-webhook` and `longhorn.io/recovery-backend`, service ports 9502/9503, and targetPort names `admission-wh` and `recov-backend`.

Control flow: the template always emits two services separated by a YAML document boundary. Each service selects pods by Longhorn-managed labels and exposes one named port.

State and persistence: persistent service objects provide stable DNS and virtual IPs for webhook and recovery backend traffic. No endpoint state is stored here beyond Kubernetes-managed endpoint slices.

Dependencies/integration: depends on workloads outside this subset that create pods with matching labels and named container ports. Network policy templates for webhook and recovery backend use the same labels and ports.

Risks: label or targetPort-name drift yields services with no ready endpoints or broken port mapping. These services are always rendered even if corresponding pods are disabled elsewhere, which can confuse health checks unless endpoints are validated.

Test signals: after install, check service endpoints/endpointslices for both services, validate port names match containers, and exercise webhook admission and recovery backend calls through service DNS.
