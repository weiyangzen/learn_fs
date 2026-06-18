# sources/control-plane/juicefs-csi-driver/pkg/controller/pod_controller.go

Purpose: node-local controller that reconciles JuiceFS mount pods assigned to `config.NodeName` and delegates lifecycle work to `PodDriver`.

Important APIs: `PodController.Reconcile` fetches the mount pod from cache, filters by node, removes immediate-reconciler annotations, parses mountinfo, lists app/mount pods on the node, constructs `PodDriver`, and converts driver results into requeue behavior. `SetupWithManager` watches mount pod create/update/delete events.

Control flow/state: reconciliation uses `config.ReconcileTimeout`. It reads app pods with `common.UniqueId` and mount pods with `PodTypeValue`, passes a combined snapshot plus mountinfo to `PodDriver`, and honors `DeleteDelayAtKey` by requeueing until the target time.

Dependencies/integration: controller-runtime cached reader/watch APIs, Kubernetes label/field selectors, `config`, `common`, `k8sclient`, util/resource helpers, mount utilities, `mountinfo.go`, and `pod_driver.go`.

Risks: controller name `"mount"` overlaps with `MountController`. Update predicate does not recheck node before enqueue, though Reconcile skips off-node pods. Cached reads can be stale, but `PodDriver.Run` refetches current pod.

Test signals: no direct tests in this subset; delegated helpers have partial coverage.
