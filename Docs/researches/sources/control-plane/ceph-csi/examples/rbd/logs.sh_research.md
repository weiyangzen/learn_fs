## sources/control-plane/ceph-csi/examples/rbd/logs.sh

Purpose: Helper script to stream logs from the first running RBD node plugin Pod.

Important functions and flow: Uses the same `CONTAINER_NAME` and Pod label lookup as `exec-bash.sh`, defines `get_pod_status`, waits for `Running`, then executes `kubectl logs -f "$POD_NAME" -c "$CONTAINER_NAME"`.

State and integration: It reads Kubernetes Pod state and streams container logs; it persists nothing. It integrates with example deployments using the `app=csi-rbdplugin` label and the default `kubectl` namespace/context.

Risks and tests: Empty Pod matches, non-default namespaces, multiple daemonset Pods, or Pods stuck outside `Running` can make the script hang or target the wrong Pod. Test by deploying the plugin and confirming logs follow the intended node plugin container.
