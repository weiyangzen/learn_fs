# sources/cloud-native/stargz-snapshotter/script/k3s/create-pod.sh

Purpose: Creates a k3s pod from a private image and verifies all parent layers are remote stargz snapshots.
Important APIs/types/functions: same structure as kind create-pod but uses `ctr` inside k3s node.
Control flow: applies pod/secret usage, waits for running, locates container by Kubernetes label, walks snapshot parents with `ctr --namespace=k8s.io`, and checks `containerd.io/snapshot/remote` labels.
State and persistence: creates a pod in namespace `ns1`; reads node snapshot metadata.
Dependencies and integration points: used by `k3s/test.sh`; depends on k3d node container, kubectl, ctr, jq, and imagePullSecret.
Risks: status parsing and snapshot traversal assumptions match the kind script; max layer count is fixed at 100.
Test signals: success demonstrates k3s private-image lazy pulling.
