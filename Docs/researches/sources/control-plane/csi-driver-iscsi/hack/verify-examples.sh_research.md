## sources/control-plane/csi-driver-iscsi/hack/verify-examples.sh

Purpose: applies and waits for example Kubernetes workloads, but the paths indicate it was copied from an NFS driver workflow.

Control flow defines `rollout_and_wait`, which applies a manifest, parses the created resource kind/name, then waits for rollout or ready condition. It applies `deploy/example/storageclass-nfs.yaml`, then NFS deployment/statefulset examples, and optionally an ephemeral NFS daemonset.

State is Kubernetes cluster resources. Dependencies are kubectl and example paths that are not part of the listed iSCSI examples. Risks are high mismatch with this repo, fragile parsing of `kubectl apply` output, unquoted variables, and trap typo using lowercase `err`. Test signal is manual only; it is not called by `verify-all.sh`.
