# sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller_test.go

Purpose: tests app-sidecar eligibility and unmount helper behavior.

Important tests: `Test_shouldRequeue` covers missing injection label, restart policy Always, no fuse container, app still running, fuse exited, single/multiple app containers terminated while fuse runs, and Pending pods. `TestAppController_umountFuseSidecars_normal` patches `ExecuteInContainer` to succeed. `TestAppController_umountFuseSidecars_error` patches exec failure and expects errors for PreStop sidecars.

State/dependencies: no cluster is used. Uses inline pod fixtures, `gomonkey`, `k8sclient`, Kubernetes pod statuses, and common constants.

Risks/gaps: does not cover ignored stderr messages, exit code 137/143 handling, missing PreStop path, `killFuseProcess`, or complete `Reconcile` timing behavior.

Test signal: good for filter predicates and basic exec propagation; limited for real reconcile behavior.
