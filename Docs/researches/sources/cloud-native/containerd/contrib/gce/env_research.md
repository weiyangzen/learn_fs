# sources/cloud-native/containerd/contrib/gce/env

Purpose: shell environment fragment used by Kubernetes GCE cluster setup to inject containerd-specific cloud-init and runtime metadata.

Important exports: `KUBE_MASTER_EXTRA_METADATA` and `KUBE_NODE_EXTRA_METADATA` point cloud-init user-data and `containerd-configure-sh` to local GCE files, while `containerd-env` points to `../version`. Runtime exports set Kubernetes to remote CRI mode with endpoint `unix:///run/containerd/containerd.sock`, runtime name `containerd`, and image import command using `ctr -n=k8s.io images import`. It also sets network provider fields and kubelet runtime cgroup args.

Control flow and state: resolves `GCE_DIR` relative to the script, verifies a sibling `version` file, then exports variables for a parent kube-up or test harness process. It does not write persistent files itself.

Dependencies and integration: assumes Kubernetes GCE scripts consume `KUBE_*` variables and instance metadata strings. Depends on `cloud-init/master.yaml`, `cloud-init/node.yaml`, `configure.sh`, and `../version`.

Risks: aborts if version file is absent. Some feature gates are legacy and may be ignored or rejected by newer Kubernetes. The empty `NETWORK_PROVIDER` and broad `NON_MASQUERADE_CIDR` are bootstrap-specific and should not leak into unrelated cluster configs.

Test signals: no direct tests; validate by sourcing from kube-up flow and confirming metadata values appear on master/node instances.
