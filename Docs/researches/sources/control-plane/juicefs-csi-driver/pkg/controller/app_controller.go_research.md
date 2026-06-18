# sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller.go

Purpose: controller for app pods injected with JuiceFS sidecar containers. It unmounts or kills lingering FUSE sidecars after non-restarting app containers terminate.

Important APIs: `AppController.Reconcile`, `umountFuseSidecars`, `umountFuseSidecar`, `killFuseProcesss`, `killFuseProcess`, `SetupWithManager`, and `ShouldInQueue`.

Control flow/state: eligibility requires injection done, not disabled, restart policy not Always, no mount init container, at least one mount sidecar, Running phase, app containers terminated, and mount sidecar running. Reconcile kills the mount process if app containers exited more than five minutes ago; otherwise it executes sidecar PreStop commands and requeues. State changes are container exec side effects only.

Dependencies/integration: controller-runtime pod watches, `K8sClient.ExecuteInContainer`, common labels/container names, and util label checks.

Risks: sidecar matching uses substring containment. Non-mount container exit code is not checked. Cleanup relies on exec availability and PreStop correctness. Some known unmounted/exit-code errors are intentionally ignored.

Test signals: `app_controller_test.go` covers queue filtering and unmount helper success/error; not the full time-based kill branch.
