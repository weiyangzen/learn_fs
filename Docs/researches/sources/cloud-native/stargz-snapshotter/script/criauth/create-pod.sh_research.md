# sources/cloud-native/stargz-snapshotter/script/criauth/create-pod.sh

Purpose: Creates a Kubernetes pod that pulls a private image and verifies every committed layer is a remote stargz snapshot.
Important APIs/types/functions: random pod/container names, `REMOTE_SNAPSHOT_LABEL`, kubectl apply/wait loop, ctr-remote snapshot traversal.
Control flow: applies a pod in namespace `ns1` using `testsecret`, waits for container running state, finds the container in the kind node, walks snapshot parents from the active snapshot, and requires every parent layer to have the remote snapshot label.
State and persistence: creates a pod and leaves it running unless caller cleans cluster; reads snapshot metadata from the node.
Dependencies and integration points: used by CRI auth kind tests; depends on kubectl, docker exec, ctr-remote, jq, and Kubernetes secrets.
Risks: status parsing is odd (`cut -d '$'`) because jsonpath output has no delimiter; snapshot traversal assumes stargz snapshotter naming and a max of 100 layers.
Test signals: test fails if private image pull does not use lazy remote snapshots.
