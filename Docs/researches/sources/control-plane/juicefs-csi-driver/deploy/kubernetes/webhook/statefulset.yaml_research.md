<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `webhook` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--webhook=true` and `--validating-webhook=true` with verbosity 5.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml -->
