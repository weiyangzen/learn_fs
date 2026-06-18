# sources/control-plane/rook/tests/framework/utils/k8s_helper.go

Purpose: `K8sHelper` is the central Kubernetes utility layer for Rook integration tests. It combines typed clients, kubectl/oc execution, pod/resource waits, log collection, storage checks, RGW service helpers, hostname mutation, and cleanup diagnostics.

Important APIs/types/functions: `K8sHelper` holds command executors, Kubernetes/Rook/bucket clientsets, in-cluster flag, testing callback, and remote pod executor. Key methods include `CreateK8sHelper`, `Kubectl`, `KubectlWithTimeout`, `KubectlWithStdin`, `ResourceOperation`, delete/get wrappers, pod/deployment/PVC/PV wait and status checks, `ExecToolboxWithRetry`, RGW URL/service helpers, namespace creation/deletion waits, log/event/describe collection, hostname change/restore, and anonymous cluster binding creation.

Control flow: helper creation builds REST config and clientsets. Most waits poll typed clients for up to `RetryLoop` iterations with `RetryInterval` sleeps. Kubectl paths run shell commands through `CommandExecutor` or `ExecuteCommand`. Resource application uses stdin. Diagnostics create files under `_output/tests/` and collect logs via typed pod log APIs with kubectl fallback.

State and persistence behavior: mutates Kubernetes resources, node hostname labels, cluster role bindings, external RGW services, files in `_output/tests`, and remote pod filesystem contents. It also observes persistent storage resources and cluster state.

Dependencies and integration points: used by nearly every client and installer file. Depends on controller-runtime config, Kubernetes client-go, Rook and object bucket clientsets, Rook command/remote executors, env-derived retry/platform settings, and kubectl/oc binaries.

Risks: broad API surface mixes typed and shell behavior, leading to inconsistent error semantics. `KubectlWithTimeout` always invokes `kubectl` instead of platform `cmd`, while stdin path uses `cmd`. Some helpers assume labels, first service port, first pod, or specific output strings. `CreateAnonSystemClusterBinding` grants cluster-admin to `system:anonymous` for kubeadm test environments and is high privilege. Log files are timestamped and can grow across repeated failures.

Test signals: successful clientset construction, pod/deployment readiness waits, PVC/PV lifecycle checks, resource apply/delete idempotence, toolbox exec, log/event capture on failure, RGW endpoint reachability, and hostname restoration are the principal signals.
