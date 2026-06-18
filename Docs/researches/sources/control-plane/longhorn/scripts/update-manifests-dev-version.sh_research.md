# sources/control-plane/longhorn/scripts/update-manifests-dev-version.sh

## Purpose
Bumps Longhorn manifests from a current version to a `-dev` chart/app version and replaces matching image tags with `master-head`, then regenerates deploy manifests.

## Important APIs and Variables
Inputs are `CURRENT_VERSION` and `NEW_VERSION` from environment or positional args. `NEW_VERSION` is formed as `$2-dev`. It finds all `*.yaml` and `longhorn-images.txt` files under the repo.

## Control Flow
With `errexit` and `nounset`, the script builds a manifest file list. For `Chart.yaml`, it replaces `version: <current>` and `appVersion: v<current>` with the dev version. For all other files, it replaces occurrences of `: v<CURRENT_VERSION>` with `master-head`. It prints each updated file, then sources `scripts/generate-longhorn-yaml.sh`.

## State and Persistence
Mutates many YAML files and image-list files in the repo, then overwrites generated deploy manifests.

## Dependencies and Integration Points
Depends on GNU sed behavior, find, and Helm through the sourced generation script. Integrates with Longhorn development manifest preparation.

## Risks
The echo says `$NEW_VERSION-dev` even though `NEW_VERSION` already includes `-dev`. Sourcing another script means its shell options/variables affect the current process. The broad find/sed operation can change unintended YAML files. It assumes tags are formatted exactly with a leading `v` after a colon.

## Test Signals
Run on a disposable branch and inspect diffs. Validate chart version/appVersion, image-list tags, generated deploy YAML, and `helm template` output. A no-op or wrong-current-version run should be detected by diff review.
