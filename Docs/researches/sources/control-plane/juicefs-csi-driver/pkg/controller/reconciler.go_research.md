# sources/control-plane/juicefs-csi-driver/pkg/controller/reconciler.go

## Purpose
This file starts and runs the node-side mount-pod reconciler that periodically inspects kubelet pod state and repairs JuiceFS mount pods on the node.

## Important APIs, Types, And Functions
It defines retry constants, `PodReconciler`, `StartReconciler`, `PodStatus`, and `doReconcile`. `StartReconciler` builds a kubelet client and Kubernetes client; `doReconcile` owns the infinite reconciliation loop.

## Control Flow
`StartReconciler` parses `config.KubeletPort`, creates a kubelet client for `config.HostIp`, verifies access, creates a Kubernetes client, and starts `doReconcile` in a goroutine. `doReconcile` loops forever: it creates a timeout context, fetches node-running pods from kubelet, creates a `PodDriver`, installs current mountinfo, filters mount pods in the CSI namespace by JuiceFS pod-type label, skips unchanged pod statuses until their `nextSyncAt`, honors the immediate-reconcile annotation, applies a shared backoff for API rate-limit errors, and runs `podDriver.Run` concurrently through an errgroup.

## State And Persistence
Runtime state is `lastPodStatus`, guarded by a mutex, plus a `flowcontrol.BackOff` keyed as `"mountpod"` for all pods. Persistence is limited to Kubernetes pod annotation mutation: the immediate reconciler annotation is removed after a reconcile attempt. The mountinfo table is rebuilt each loop.

## Dependencies And Integration Points
It depends on `k8sclient.KubeletClient`, `PodDriver`, `newMountInfoTable`, controller config values, `common.ImmediateReconcilerKey`, and `resource.DelPodAnnotation`. It is the scheduler around the handler behavior tested in `pod_driver_test.go`.

## Risks
The loop has no stop channel other than process exit, and it intentionally ignores `errgroup.Wait` errors after logging inside workers. The shared backoff ID can throttle all mount pods after one rate-limit error. The goroutine closes over the loop variable `pod`; because `pod` is declared with `:=` inside the loop body in modern Go this is usually safe, but it remains a sensitive pattern to review with compiler version assumptions.

## Test Signals
The direct reconciler loop is not tested here. Indirect confidence comes from `pod_driver_test.go`; additional tests would need fake kubelet clients and controllable time/backoff to validate skip, immediate-reconcile, and rate-limit behavior.
