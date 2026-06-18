## sources/control-plane/csi-driver-nfs/test/utils/check_driver_pods_restart.sh

Purpose: checks kube-system NFS driver pods for restart counts before e2e tests. It prints restart status and warns if any pod matching `nfs` has a nonzero restart count.

Important flow: `kubectl get pods -n kube-system | grep nfs | awk '{print $4}'` extracts restart counts and loops over them. The former failure path is commented out, so the script currently logs restart detection but always prints success.

State is only live Kubernetes pod status. Dependencies are kubectl, grep, awk, and pod table column layout. Risks include matching unrelated NFS pods, no failure despite restarts, brittle parsing when kubectl output changes, and `set -e` causing no-match grep to fail the script. Test signal is weak because it is informational unless shell pipeline failure occurs.
