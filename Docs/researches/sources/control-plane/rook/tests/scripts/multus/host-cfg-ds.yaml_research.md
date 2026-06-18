<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml -->
# sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml

Purpose: test-only DaemonSet that configures each KinD/minikube node to route traffic to the Multus public network.

Important structure and control flow: runs privileged `jonlabelle/network-tools` pods on host networking, including control-plane toleration. The shell command derives the host `eth0` IP, creates a macvlan shim named `public-shim` using the last octet under `192.168.29.0/24`, and routes `192.168.20.0/24` through that shim before sleeping forever.

State, persistence, and integration: modifies host network interfaces/routes inside each node namespace while the DaemonSet is running. Dependencies include privileged pods, `NET_ADMIN`, macvlan support, and fixed network ranges matching NADs. Risks include non-production privileged networking, route conflicts, and hard-coded `eth0`. Test signals are pod readiness and successful connectivity from validation clients.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/host-cfg-ds.yaml -->
