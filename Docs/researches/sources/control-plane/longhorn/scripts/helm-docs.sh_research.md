# sources/control-plane/longhorn/scripts/helm-docs.sh

## Purpose
Runs the `jnorwood/helm-docs:v1.9.1` Docker image against the Longhorn `chart` directory to regenerate Helm chart documentation.

## Important APIs and Variables
Derives `PRJ_DIR` and `CHART_DIR`, prints the chart path, then invokes `sudo docker run -v "$CHART_DIR:/helm-docs" -u $(id -u) jnorwood/helm-docs:v1.9.1`.

## Control Flow
`errexit` and `xtrace` stop on failures and echo commands. There is no argument parsing. Docker runs as the current UID inside the container to reduce root-owned output.

## State and Persistence
Mutates files under `chart`, typically README-style generated docs, through the bind mount. Docker image layers/cache live outside the repository.

## Dependencies and Integration Points
Requires sudo, Docker, network access or cached image, and the Helm chart tree. Integrates with chart release maintenance and documentation checks.

## Risks
Pinning to an old helm-docs image can diverge from chart features. `sudo docker` may fail in noninteractive CI or create files with unexpected group/permissions. The script does not verify Docker is installed before running.

## Test Signals
Run and inspect `git diff chart`. A clean regeneration should produce expected README changes only. CI can validate by rerunning and requiring no diff.
