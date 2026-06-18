# sources/control-plane/ceph-csi/examples/cephfs/exec-bash.sh

Purpose: operator convenience script for opening an interactive shell in the first CephFS nodeplugin pod.

Important APIs and flow: selects a pod with label `app=csi-cephfsplugin`, polls its phase until `Running`, then runs `kubectl exec -it <pod> -c csi-cephfsplugin bash`.

State, dependencies, and integration: reads pod status and opens an exec session; it does not create cluster resources. It integrates with the example/development deployment labels.

Risks and test signals: assumes label uniqueness, namespace from current kubectl context, and bash availability in the container. It has no timeout and can wait forever if the pod never runs.
