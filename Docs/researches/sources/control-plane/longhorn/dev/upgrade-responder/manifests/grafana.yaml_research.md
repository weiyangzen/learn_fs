<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml -->
# sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml

Purpose: development Grafana deployment backed by Longhorn storage for visualizing upgrade responder data.

Important APIs/types/functions: creates a 2Gi `grafana-pvc`, an `apps/v1` Deployment using `grafana/grafana:7.1.0`, `GF_INSTALL_PLUGINS=grafana-worldmap-panel`, readiness/liveness probes, and a LoadBalancer Service on port 3000.

Control flow: Kubernetes binds the PVC through Longhorn, starts Grafana with persistent `/var/lib/grafana`, probes HTTP `/robots.txt` and TCP 3000, and exposes it through the LoadBalancer.

State and persistence: dashboard/configuration data persists in the Longhorn PVC. Pod runtime state is otherwise disposable.

Dependencies/integration points: depends on Longhorn StorageClass, Grafana image/plugin installation, LoadBalancer support, and the install script for rollout waiting.

Risks/test signals: old Grafana image and plugin install may have security or availability issues; LoadBalancer is environment-specific. Test signals are PVC binding, deployment readiness, service external address, plugin installation logs, and dashboard access.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/upgrade-responder/manifests/grafana.yaml -->
