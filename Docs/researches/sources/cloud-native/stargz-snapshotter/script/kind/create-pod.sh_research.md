# sources/cloud-native/stargz-snapshotter/script/kind/create-pod.sh

Purpose: Creates a kind pod from a private image, verifies remote snapshot labels, and checks standalone snapshotter restart when applicable.
Important APIs/types/functions: random names, `REMOTE_SNAPSHOT_LABEL`, kubectl wait loop, ctr-remote snapshot traversal, optional systemd restart.
Control flow: applies pod, waits for running, finds container in kind node, walks stargz snapshot parents and requires remote labels, then for standalone snapshotter deletes the pod and restarts `stargz-snapshotter.service`.
State and persistence: creates/deletes Kubernetes pod and reads node snapshot state; may restart snapshotter service.
Dependencies and integration points: used by `kind/test.sh`; depends on kubectl, docker exec, ctr-remote, jq, systemd inside node.
Risks: same status parsing/layer traversal fragility as related scripts; service restart check only applies to standalone mode.
Test signals: validates both lazy pull and restart health in kind.
