<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh -->
# sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh

## Purpose
End-to-end Kubernetes checkpoint/restore test using kubectl, crictl, ctr, and local checkpoint image.

## Important APIs, Types, And Functions
Shell `cleanup` plus linear test workflow.

## Control Flow
Validates CRIU/tools, applies a sleeper pod, observes counter output, checkpoints/restores through Kubernetes/containerd paths, imports/restores image, and validates continued behavior.

## State And Persistence
Mutates Kubernetes cluster pods, local images, temp files, and checkpoint artifacts.

## Dependencies And Integration Points
kubectl, crictl, ctr, CRIU, Kubernetes admin kubeconfig, testdata pod YAML.

## Risks And Test Signals
Requires a live cluster and root/runtime privileges; can delete pod `sleeper`. Strong but environment-heavy test signal. Source size reviewed: 231 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/checkpoint/checkpoint-restore-kubernetes-test.sh -->
