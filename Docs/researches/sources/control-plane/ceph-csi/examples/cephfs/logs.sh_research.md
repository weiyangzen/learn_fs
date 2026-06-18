# sources/control-plane/ceph-csi/examples/cephfs/logs.sh

Purpose: convenience script for following logs from the first CephFS nodeplugin pod.

Important APIs and flow: selects `app=csi-cephfsplugin`, waits until the pod phase is `Running`, and executes `kubectl logs -f` for container `csi-cephfsplugin`.

State, dependencies, and integration: reads pod status/logs only. It depends on deployment labels and the current kubectl namespace/context.

Risks and test signals: no timeout and no explicit namespace can make it hang or target the wrong context. It provides operational debug signal but is not an automated test.
