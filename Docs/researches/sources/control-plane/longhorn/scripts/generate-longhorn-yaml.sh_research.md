# sources/control-plane/longhorn/scripts/generate-longhorn-yaml.sh

## Purpose
Generates static Longhorn install manifests from the Helm chart into `deploy/longhorn.yaml` and `deploy/longhorn-okd.yaml`.

## Important APIs and Variables
Variables derive `PRJ_DIR`, `CHART_DIR`, the two deploy output paths, temp output path, and `NAMESPACE` defaulting to `longhorn-system`. It requires `helm` version 3 or 4.

## Control Flow
With `errexit` and `xtrace`, the script checks Helm availability/version. For each deploy YAML, it writes an explicit Namespace object because `helm template` does not honor `--create-namespace`. For the OKD manifest it sets `OKD_ENABLED_FLAG="--set openshift.enabled=true"`, then runs `helm template longhorn "$CHART_DIR" --namespace "$NAMESPACE" ... --no-hooks`. It filters Helm ownership/chart metadata lines and atomically replaces the output from a temp file.

## State and Persistence
Persists generated manifests in the repo's `deploy` directory, overwriting existing files. It does not touch cluster state. `OKD_ENABLED_FLAG` is not reset inside the loop, but because the OKD file is last in the current array order this does not affect the normal two-output run.

## Dependencies and Integration Points
Depends on Helm v3/v4, chart templates under `chart`, and standard shell tools. Integrates with release/update scripts and static manifest consumers.

## Risks
The metadata filtering is grep-based and may remove unintended lines containing `helm.sh` or `app.kubernetes.io/managed-by: Helm`. If output order changes, `OKD_ENABLED_FLAG` could leak into later manifests. The error message references `$DEPLOY_YAML` before loop assignment under failure conditions.

## Test Signals
Run the script and compare generated manifest diffs, validate YAML parse, and perform a server-side or dry-run Kubernetes validation for both standard and OKD manifests. Confirm namespace override behavior with `NAMESPACE=...`.
