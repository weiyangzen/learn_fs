# sources/control-plane/longhorn/scripts/longhorn_rancher_chart_migration.sh

## Purpose
Migrates a Longhorn installation managed by Rancher's legacy catalog app model to Helm/App Marketplace ownership. It has two modes: `migrate` patches downstream resources with Helm labels/annotations, and `cleanup` marks/deletes the old Rancher project app after manual chart install.

## Important APIs and Variables
Requires `kubectl get-all` from `ketall`. Inputs are upstream Rancher kubeconfig, downstream cluster kubeconfig, `--type migrate|cleanup`, and optional `--dry-run`. Constants are `RELEASE_NAMESPACE=longhorn-system` and `RELEASE_NAME=longhorn-system`.

The script reads the downstream cluster ID from kubeconfig server URL, searches upstream `apps.project.cattle.io`, extracts catalog/template/version from `.spec.externalId`, and obtains old values from `.spec.valuesYaml` or `.spec.answers`.

## Control Flow
After parsing and validation, it locates the Rancher Project App. In cleanup mode it verifies downstream `longhorn-manager` DaemonSet is Helm-managed, patches the upstream app with skip-uninstall/migration annotations, then deletes it. In migrate mode it verifies Longhorn setting `concurrent-automatic-engine-upgrade-per-node-limit` is `0`, lists all resources labeled `io.cattle.field/appId=<release>`, annotates CRDs as release `longhorn-crd` with keep policy, and annotates/labels all other resources as Helm release `longhorn`.

## State and Persistence
In migrate mode it mutates Kubernetes labels and annotations on many downstream resources. In cleanup mode it mutates and deletes the upstream Rancher app object. `--dry-run=client` can prevent server writes for most kubectl operations.

## Dependencies and Integration Points
Integrates with Rancher `apps.project.cattle.io`, Longhorn settings CRs, Kubernetes resources returned by `kubectl get-all`, Helm ownership metadata, and the manual Rancher UI chart installation step.

## Risks
Broad resource patching can affect every object with the legacy app label. Kubeconfig parsing via grep/awk is brittle. Several variable expansions are unquoted, so paths or unexpected values can break execution. Cleanup deletes the Rancher app and relies on prior manual install success. It does not verify Helm release readiness after migration.

## Test Signals
Use `--dry-run` on a staging Rancher install and inspect planned resources. Pre/post checks should include Longhorn setting value, resource labels/annotations, Helm release ownership, and successful old app cleanup only after new chart health is confirmed.
