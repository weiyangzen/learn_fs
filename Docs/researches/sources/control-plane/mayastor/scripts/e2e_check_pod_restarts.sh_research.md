# sources/control-plane/mayastor/scripts/e2e_check_pod_restarts.sh

Purpose: simple Kubernetes e2e guard that fails when Mayastor or MOAC pods restarted.

Important APIs/types/functions: runs `kubectl get pods -n mayastor`, filters names containing `mayastor` or `moac`, extracts column 4 restart counts, and exits `255` after dumping pods if any count is nonzero.

Control flow: linear shell loop over restart counts.

State/persistence: read-only Kubernetes API access.

Dependencies/integration: used after e2e tests to catch restarts/crashes in the Mayastor namespace.

Risks: parses human table output and assumes the restart column remains fourth. Grep may match unrelated pod names containing those strings.

Test signals: exit `0` means no matching pod reported restarts.
