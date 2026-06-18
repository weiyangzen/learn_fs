# sources/control-plane/ceph-csi/e2e/log.go

Purpose: collects CSI and gateway pod logs for e2e failure diagnostics, including fallback to previous container logs when current logs are unavailable.

Important APIs/types/functions: `logsCSIPods(label, c)` lists pods in `cephCSINamespace` by label and logs each. `kubectlLogPod(c, pod)` iterates all containers in a pod, fetches current logs or previous logs, and writes formatted output to the framework log. `getPreviousPodLogs(c, namespace, podName, containerName)` calls the pod log subresource with `previous=true` and rejects responses containing `Internal Error`.

Control flow: failure hooks call `logsCSIPods()` for provisioner/nodeplugin labels. For each pod/container, the helper first calls Kubernetes e2e `GetPodLogs`; if that fails, it tries the previous log endpoint. It logs any retrieval failure but continues through remaining containers.

State and persistence: read-only against Kubernetes logs; writes diagnostic text to the test log stream.

Dependencies and integration points: uses Kubernetes CoreV1 pod list/log REST APIs, e2e framework logging, and pod framework log retrieval. CephFS, NFS, and NVMe-oF failure hooks rely on it before dumping namespace info.

Risks: large logs can make failing job output heavy. Previous-log fallback can mask current-log retrieval failure but still omit logs if the pod never restarted. The `Internal Error` string check is heuristic.

Test signals: visible `STARTLOG`/`ENDLOG` sections in failed e2e runs, including container name and node name, are the main signal. There are no direct unit tests.
