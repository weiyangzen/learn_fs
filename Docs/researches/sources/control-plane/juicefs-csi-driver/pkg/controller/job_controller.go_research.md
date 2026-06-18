# sources/control-plane/juicefs-csi-driver/pkg/controller/job_controller.go

Purpose: recycles JuiceFS-related Kubernetes Jobs, especially completed jobs and node-bound jobs whose CSI node pod has disappeared.

Important APIs: `JobController.Reconcile` fetches a job, ignores missing/deleting jobs, checks node binding, lists CSI node pods by label and node, and deletes jobs that should be recycled. `SetupWithManager` registers Job watches.

Control flow/state: unbound jobs are deleted only when `resource.IsJobShouldBeRecycled` says so. Node-bound jobs are also deleted when no CSI node pod exists in `config.Namespace` on the target node. Persistent state change is Job deletion.

Dependencies/integration: Kubernetes batch API, controller-runtime, common CSI node label constants, `config.Namespace`, `k8sclient`, and resource job predicates. Fuse abort jobs created by `pod_driver.go` are likely consumers.

Risks: CSI node label/namespace mismatch can cause deletion of useful jobs. Delete events can still enqueue missing objects. No direct tests are in this subset.

Test signals: none directly for this file.
