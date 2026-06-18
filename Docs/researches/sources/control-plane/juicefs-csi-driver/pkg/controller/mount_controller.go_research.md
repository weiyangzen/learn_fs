# sources/control-plane/juicefs-csi-driver/pkg/controller/mount_controller.go

Purpose: control-plane mount pod controller that manages finalizer removal for deleting mount pods and cleans pending unscheduled mount pods whose app references are gone.

Important APIs: `Reconcile`, `handlePendingMountPod`, `GetPodByUidAndNode`, `shouldInQueue`, and `SetupWithManager`.

Control flow/state: pending unscheduled pods are scanned for reference annotations; if no referenced app pods exist, the mount pod is deleted. Deleting mount pods with the JuiceFS finalizer list CSI node pods on the same node; if a CSI pod exists, reconciliation requeues, otherwise the finalizer is removed.

Dependencies/integration: controller-runtime pod watches, Kubernetes field/label selectors, `k8sclient`, common labels/finalizer, config namespace, util reference-key parsing, and resource finalizer helpers.

Risks: malformed target annotations are skipped and can contribute to orphan deletion. `GetPodByUidAndNode` depends on app pods carrying `common.UniqueId`. Finalizer removal depends on CSI node presence, not a full mount cleanup proof.

Test signals: no direct tests in this subset.
