<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/setup-multus.sh -->
# sources/control-plane/rook/tests/scripts/multus/setup-multus.sh

Purpose: installs Multus, CNI plugins, and whereabouts into a test Kubernetes cluster.

Important APIs and control flow: waits for CoreDNS, uses a retry wrapper around `kubectl create` for the Multus daemonset URL, waits for Multus pods, creates CNI install manifests, waits for CNI plugin pods, then applies whereabouts daemonset and CRDs and waits for whereabouts pods. Timeouts and retry counts are configurable through variables at the top.

State, persistence, and integration: creates cluster networking components under kube-system plus whereabouts CRDs. Dependencies include remote raw GitHub manifests, kubectl, CoreDNS availability, and `timeout`. Risks include using `master` branch remote manifests, command-string retry quoting, and create failures on re-runs due to existing resources. Test signals are ready pods for Multus, CNI plugins, and whereabouts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/setup-multus.sh -->
