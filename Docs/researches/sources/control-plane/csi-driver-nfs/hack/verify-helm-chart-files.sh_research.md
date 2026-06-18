<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh

## Purpose
Verifies packaged Helm chart `.tgz` files match the chart source and checks the published Helm repo index path.

## Important APIs, Types, and Functions
The script disables git filemode tracking, checks initial `git diff`, expands any `charts/*/*.tgz` archives into their chart directories, checks `git diff` again, installs Helm from the upstream script, adds the `csi-driver-nfs` chart repository, and runs `helm search repo -l`.

## Control Flow, State, and Persistence
It fails if the working tree is already dirty or if unpacking chart packages produces diffs. It can install Helm and adds a Helm repo entry to the user's Helm config/cache.

## Dependencies and Integration Points
It depends on tar, git, curl, Helm installation, network access to Helm scripts and the upstream chart repo, and packaged chart archives. `verify-all.sh` includes it before chart lint/index checks.

## Risks and Test Signals
Risks include mutating Helm user config, network dependency, unpacking tarballs over source directories, dirty-tree false failures, and glob behavior with no `.tgz`. Signals are no git diff after extraction and successful `helm search repo`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh -->
